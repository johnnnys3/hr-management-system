"""The payroll calculation engine (HRMS-FR-039 to HRMS-FR-042) and bank
transfer file generation (HRMS-FR-046).

Both are placeholders, owner-confirmed 2026-07-19, because TBD-005
(statutory rates) and TBD-006 (bank transfer file format) are open
external inputs this project cannot resolve. `docs/02-project-plan.md`
§7.5: this module completes as "calculation engine built, statutory
correctness unverified," not "Payroll done." Swapping in real rates is
a `StatutoryRateTable` data migration; swapping the file format is a
change to `generate_bank_transfer_file` alone — neither requires
touching the calculation shape or the calling code in `tasks.py`.
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from compensation.models import CompensationRecord, EmployeeAllowance
from employees.models import Employee

from .models import BankTransferFile, PayrollRun, Payslip, PayslipLine, StatutoryRateTable
from .storage import generate_bank_transfer_object_key, generate_payslip_object_key, save_file

DEDUCTION_RATE_TYPES = [
    (StatutoryRateTable.RATE_TYPE_PAYE, PayslipLine.LINE_DEDUCTION_PAYE),
    (StatutoryRateTable.RATE_TYPE_SSNIT_TIER1, PayslipLine.LINE_DEDUCTION_SSNIT_TIER1),
    (StatutoryRateTable.RATE_TYPE_SSNIT_TIER2, PayslipLine.LINE_DEDUCTION_SSNIT_TIER2),
    (StatutoryRateTable.RATE_TYPE_SSNIT_TIER3, PayslipLine.LINE_DEDUCTION_SSNIT_TIER3),
]


def _current_rate(rate_type, as_of):
    return (
        StatutoryRateTable.objects
        .filter(rate_type=rate_type, effective_from__lte=as_of)
        .order_by('-effective_from')
        .first()
    )


def _apply_brackets(base, brackets):
    """Progressive bracket application: each bracket taxes only the
    slice of `base` between the previous bracket's `upper` and its
    own. The last bracket's `upper` may be `null`, meaning unbounded."""
    total = Decimal('0')
    lower = Decimal('0')
    for bracket in brackets:
        rate = Decimal(str(bracket['rate']))
        upper = bracket.get('upper')
        upper = Decimal(str(upper)) if upper is not None else None
        if base <= lower:
            break
        slice_top = min(base, upper) if upper is not None else base
        total += (slice_top - lower) * rate
        lower = slice_top
        if upper is not None and base <= upper:
            break
    return total.quantize(Decimal('0.01'))


def _statutory_deduction(rate_type, base_salary, as_of):
    rate_row = _current_rate(rate_type, as_of)
    if rate_row is None:
        return Decimal('0.00'), None
    brackets = rate_row.rates.get('brackets', [])
    return _apply_brackets(base_salary, brackets), rate_row


def _allowance_amount(allowance, base_salary):
    if allowance.amount_override is not None:
        return allowance.amount_override
    allowance_type = allowance.allowance_type
    if allowance_type.calculation_method == allowance_type.CALCULATION_PERCENTAGE:
        return (base_salary * allowance_type.amount_or_rate).quantize(Decimal('0.01'))
    return allowance_type.amount_or_rate


def calculate_run(payroll_run):
    """HRMS-FR-035 to HRMS-FR-042: compute a payslip + payslip_line set
    for every active employee, over the run's period. Idempotent: a
    prior calculation's payslips for this run are replaced, not
    duplicated, so re-running `calculate/` (e.g. a retried Celery task)
    is safe (HRMS-NFR-005)."""
    as_of = payroll_run.period_end
    with transaction.atomic():
        # PayslipLine.payslip is ON DELETE RESTRICT, so the lines of a
        # prior calculation must go first.
        PayslipLine.objects.filter(payslip__payroll_run=payroll_run).delete()
        Payslip.objects.filter(payroll_run=payroll_run).delete()
        for employee in Employee.objects.filter(employment_status=Employee.STATUS_ACTIVE):
            compensation = (
                CompensationRecord.objects
                .filter(employee=employee, is_superseded=False, effective_from__lte=as_of)
                .order_by('-effective_from')
                .first()
            )
            if compensation is None:
                continue
            base_salary = compensation.base_salary
            allowances = EmployeeAllowance.objects.filter(
                employee=employee, effective_from__lte=as_of,
            ).exclude(effective_to__lt=as_of).select_related('allowance_type')

            gross_pay = base_salary
            lines = [(
                PayslipLine.LINE_BASIC_SALARY, 'compensation_record', compensation.pk,
                'Basic salary', base_salary,
            )]
            for allowance in allowances:
                amount = _allowance_amount(allowance, base_salary)
                gross_pay += amount
                lines.append((
                    PayslipLine.LINE_ALLOWANCE, 'employee_allowance', allowance.pk,
                    allowance.allowance_type.name, amount,
                ))

            total_deductions = Decimal('0.00')
            for rate_type, line_type in DEDUCTION_RATE_TYPES:
                amount, rate_row = _statutory_deduction(rate_type, base_salary, as_of)
                if rate_row is None:
                    continue
                total_deductions += amount
                lines.append((
                    line_type, 'statutory_rate_table', rate_row.pk,
                    rate_row.get_rate_type_display(), amount,
                ))

            net_pay = gross_pay - total_deductions
            payslip = Payslip.objects.create(
                payroll_run=payroll_run, employee=employee,
                gross_pay=gross_pay, net_pay=net_pay,
            )
            PayslipLine.objects.bulk_create([
                PayslipLine(
                    payslip=payslip, line_type=line_type, source_type=source_type,
                    source_id=source_id, description=description, amount=amount,
                )
                for line_type, source_type, source_id, description, amount in lines
            ])
        payroll_run.status = PayrollRun.STATUS_CALCULATED
        payroll_run.save(update_fields=['status'])


def finalize_run(payroll_run):
    """HRMS-FR-047/HRMS-BR-008's atomic finalisation, `docs/06-api-
    contracts.md` §4.14: "a partial payroll is a corrupt payroll." Sets
    `finalized_at` and generates the bank transfer file and each
    payslip's PDF in the same transaction as the status write.
    Idempotent: a bank transfer file or payslip PDF that already
    exists (a retried task after a prior partial success) is not
    regenerated."""
    with transaction.atomic():
        if not hasattr(payroll_run, 'bank_transfer_file'):
            generate_bank_transfer_file(payroll_run)
        for payslip in payroll_run.payslips.filter(object_key__isnull=True).select_related('employee'):
            generate_payslip_pdf(payslip)
        payroll_run.status = PayrollRun.STATUS_FINALIZED
        payroll_run.finalized_at = timezone.now()
        payroll_run.save(update_fields=['status', 'finalized_at'])


def generate_bank_transfer_file(payroll_run):
    """HRMS-FR-046. Placeholder CSV — see module docstring. Columns:
    employee_number, employee_name, net_pay, currency. No bank account
    data exists anywhere in this schema (direct bank integration is out
    of scope, `docs/05-database-schema.md` §2), so this identifies
    employees by `employee_number` for a human/bank process to match
    against externally, not an account number this system holds."""
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['employee_number', 'employee_name', 'net_pay', 'currency'])
    for payslip in payroll_run.payslips.select_related('employee').order_by('employee__employee_number'):
        writer.writerow([
            payslip.employee.employee_number,
            f'{payslip.employee.first_name} {payslip.employee.last_name}',
            payslip.net_pay,
            payslip.currency,
        ])

    object_key = generate_bank_transfer_object_key(payroll_run.pk)
    save_file(object_key, buffer.getvalue().encode('utf-8'))
    return BankTransferFile.objects.create(payroll_run=payroll_run, object_key=object_key)


def generate_payslip_pdf(payslip):
    """`docs/06-api-contracts.md` §4.14's `/api/payslips/{id}/download/`.
    Renders the payslip's lines (already computed and immutable by the
    time `finalize_run` calls this) to a one-page PDF and stores it,
    setting `payslip.object_key`. Called once per payslip, at
    finalisation — a payslip is only ever downloaded once its run is
    finalized (`docs/07-iam-rbac.md` §4.2), so there is nothing to
    regenerate before then."""
    import io

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    def line(text, size=10, gap=7 * mm):
        nonlocal y
        pdf.setFont('Helvetica', size)
        pdf.drawString(20 * mm, y, text)
        y -= gap

    employee = payslip.employee
    line('Payslip', size=16, gap=12 * mm)
    line(f'Employee: {employee.first_name} {employee.last_name} ({employee.employee_number})')
    line(f'Period: {payslip.payroll_run.period_start} to {payslip.payroll_run.period_end}')
    line('')
    for payslip_line in payslip.lines.order_by('id'):
        line(f'{payslip_line.get_line_type_display()} — {payslip_line.description}: '
             f'{payslip_line.amount} {payslip.currency}')
    line('')
    line(f'Gross pay: {payslip.gross_pay} {payslip.currency}', size=12)
    line(f'Net pay: {payslip.net_pay} {payslip.currency}', size=12)
    pdf.showPage()
    pdf.save()

    object_key = generate_payslip_object_key(payslip.payroll_run_id, payslip.employee_id, payslip.pk)
    save_file(object_key, buffer.getvalue())
    payslip.object_key = object_key
    payslip.save(update_fields=['object_key'])
    return payslip
