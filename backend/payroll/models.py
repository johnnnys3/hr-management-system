from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from employees.models import Employee

NON_NEGATIVE = MinValueValidator(Decimal('0'))


class StatutoryRateTable(models.Model):
    """`statutory_rate_table`, `docs/05-database-schema.md` §4.12.
    HRMS-FR-039 to HRMS-FR-042. Append-only per §3.4/§4.12 — a rate
    change is a new row with a new `effective_from`, never an update to
    an existing one, so a finalised payslip remains reproducible against
    the rates in force when it ran.

    `rates` is deliberately a placeholder shape as of PAYROLL-001:
    TBD-005 (statutory PAYE/SSNIT rates) is open, and this project
    cannot invent real rates. Seeded brackets are clearly-labelled test
    data (see the data migration), not statutory fact — loading real
    rates once TBD-005 resolves is a new row here, not a code change.
    """

    RATE_TYPE_PAYE = 'paye'
    RATE_TYPE_SSNIT_TIER1 = 'ssnit_tier1'
    RATE_TYPE_SSNIT_TIER2 = 'ssnit_tier2'
    RATE_TYPE_SSNIT_TIER3 = 'ssnit_tier3'
    RATE_TYPE_CHOICES = [
        (RATE_TYPE_PAYE, 'PAYE'),
        (RATE_TYPE_SSNIT_TIER1, 'SSNIT Tier 1'),
        (RATE_TYPE_SSNIT_TIER2, 'SSNIT Tier 2'),
        (RATE_TYPE_SSNIT_TIER3, 'SSNIT Tier 3'),
    ]

    rate_type = models.CharField(max_length=16, choices=RATE_TYPE_CHOICES)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    rates = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'statutory_rate_table'
        constraints = [
            models.UniqueConstraint(fields=['rate_type', 'effective_from'], name='statutory_rate_unique_type_period'),
        ]

    def __str__(self):
        return f'{self.rate_type} @ {self.effective_from}'


class PayrollRun(models.Model):
    """`payroll_run`, `docs/05-database-schema.md` §4.12. HRMS-FR-035 to
    HRMS-FR-038, HRMS-FR-047, HRMS-FR-048, HRMS-BR-008. The
    approver-not-initiator constraint (§3.5) is enforced both here at
    the DB layer and again at the API layer (HRMS-BR-008,
    `docs/07-iam-rbac.md` §4.4: "regardless of any combination of
    roles a user may hold")."""

    STATUS_DRAFT = 'draft'
    STATUS_CALCULATED = 'calculated'
    STATUS_PENDING_APPROVAL = 'pending_approval'
    STATUS_APPROVED = 'approved'
    STATUS_FINALIZED = 'finalized'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_CALCULATED, 'Calculated'),
        (STATUS_PENDING_APPROVAL, 'Pending approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_FINALIZED, 'Finalized'),
        (STATUS_FAILED, 'Failed'),
    ]

    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='initiated_payroll_runs',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True, blank=True, related_name='+',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payroll_run'
        permissions = [('approve_payroll_run', 'Can approve a payroll run for finalisation')]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(approved_by__isnull=True) | ~models.Q(approved_by=models.F('initiated_by')),
                name='payroll_run_approver_not_initiator',
            ),
            models.UniqueConstraint(fields=['period_start', 'period_end'], name='payroll_run_unique_period'),
        ]

    def __str__(self):
        return f'{self.period_start}..{self.period_end} ({self.status})'


class Payslip(models.Model):
    """`payslip`, `docs/05-database-schema.md` §4.12. HRMS-FR-043,
    HRMS-FR-044, HRMS-BR-006."""

    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.RESTRICT, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='payslips')
    gross_pay = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    net_pay = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    currency = models.CharField(max_length=8, default='GHS')
    generated_at = models.DateTimeField(auto_now_add=True)
    object_key = models.CharField(max_length=512, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'payslip'
        constraints = [
            models.UniqueConstraint(fields=['payroll_run', 'employee'], name='payslip_unique_run_employee'),
        ]

    def __str__(self):
        return f'{self.employee_id} / {self.payroll_run_id}'


class PayslipLine(models.Model):
    """`payslip_line`, `docs/05-database-schema.md` §4.12. Computed-instance
    half of Allowance and Deduction (definitional half: `compensation.
    AllowanceType`, `StatutoryRateTable`). `source_type`/`source_id` are
    deliberately not foreign keys (same reasoning as `audit_log.
    target_type`): a finalised payslip must remain readable even if the
    source configuration row is later retired."""

    LINE_BASIC_SALARY = 'basic_salary'
    LINE_ALLOWANCE = 'allowance'
    LINE_DEDUCTION_PAYE = 'deduction_statutory_paye'
    LINE_DEDUCTION_SSNIT_TIER1 = 'deduction_statutory_ssnit_tier1'
    LINE_DEDUCTION_SSNIT_TIER2 = 'deduction_statutory_ssnit_tier2'
    LINE_DEDUCTION_SSNIT_TIER3 = 'deduction_statutory_ssnit_tier3'
    LINE_DEDUCTION_OTHER = 'deduction_other'
    LINE_TYPE_CHOICES = [
        (LINE_BASIC_SALARY, 'Basic salary'),
        (LINE_ALLOWANCE, 'Allowance'),
        (LINE_DEDUCTION_PAYE, 'PAYE'),
        (LINE_DEDUCTION_SSNIT_TIER1, 'SSNIT Tier 1'),
        (LINE_DEDUCTION_SSNIT_TIER2, 'SSNIT Tier 2'),
        (LINE_DEDUCTION_SSNIT_TIER3, 'SSNIT Tier 3'),
        (LINE_DEDUCTION_OTHER, 'Other deduction'),
    ]

    DEDUCTION_TYPES = [
        LINE_DEDUCTION_PAYE, LINE_DEDUCTION_SSNIT_TIER1, LINE_DEDUCTION_SSNIT_TIER2,
        LINE_DEDUCTION_SSNIT_TIER3, LINE_DEDUCTION_OTHER,
    ]

    payslip = models.ForeignKey(Payslip, on_delete=models.RESTRICT, related_name='lines')
    line_type = models.CharField(max_length=40, choices=LINE_TYPE_CHOICES)
    source_type = models.CharField(max_length=64, null=True, blank=True)
    source_id = models.BigIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payslip_line'
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name='payslip_line_amount_gte_0'),
        ]

    def __str__(self):
        return f'{self.payslip_id} / {self.line_type} ({self.amount})'


class BankTransferFile(models.Model):
    """`bank_transfer_file`, `docs/05-database-schema.md` §4.12.
    HRMS-FR-046. Format is TBD-006, open — generated as a
    clearly-labelled placeholder CSV as of PAYROLL-001 (see
    `payroll.services.generate_bank_transfer_file`); swapping the
    format later is a change to that function, not to this table.
    `object_key` points at the file; no bank account data exists
    anywhere in this schema (direct bank integration is out of scope
    per `docs/05-database-schema.md` §2's scope boundary), so the file
    identifies employees by `employee_number` only, for a human/bank
    process to match against externally."""

    payroll_run = models.OneToOneField(PayrollRun, on_delete=models.RESTRICT, related_name='bank_transfer_file')
    object_key = models.CharField(max_length=512, unique=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bank_transfer_file'

    def __str__(self):
        return f'{self.payroll_run_id} / {self.object_key}'
