"""`payroll.services.calculate_run`, HRMS-FR-039 to HRMS-FR-042. Tests
the calculation engine directly (not the async view) — see
`test_payroll_runs.py` for the HTTP-layer `calculate/` action."""
from decimal import Decimal

from django.test import TestCase

from compensation.models import AllowanceType, EmployeeAllowance
from employees.models import Employee

from ..models import PayrollRun, PayslipLine
from ..services import calculate_run
from .helpers import give_compensation, make_employee


class CalculateRunTests(TestCase):
    def _run(self, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        initiator = User.objects.create_user(email='initiator@example.com', password='x')
        defaults = dict(period_start='2026-01-01', period_end='2026-01-31', initiated_by=initiator)
        defaults.update(kwargs)
        return PayrollRun.objects.create(**defaults)

    def test_computes_basic_salary_only_when_no_allowances(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='1500.00')
        payroll_run = self._run()

        calculate_run(payroll_run)

        payroll_run.refresh_from_db()
        self.assertEqual(payroll_run.status, PayrollRun.STATUS_CALCULATED)
        payslip = payroll_run.payslips.get(employee=employee)
        self.assertEqual(payslip.gross_pay, Decimal('1500.00'))
        basic = payslip.lines.get(line_type=PayslipLine.LINE_BASIC_SALARY)
        self.assertEqual(basic.amount, Decimal('1500.00'))

    def test_fixed_allowance_adds_to_gross_pay(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='1500.00')
        allowance_type = AllowanceType.objects.create(
            name='Transport', calculation_method='fixed', amount_or_rate='200.00', is_taxable=False,
        )
        EmployeeAllowance.objects.create(employee=employee, allowance_type=allowance_type, effective_from='2026-01-01')
        payroll_run = self._run()

        calculate_run(payroll_run)

        payslip = payroll_run.payslips.get(employee=employee)
        self.assertEqual(payslip.gross_pay, Decimal('1700.00'))

    def test_percentage_allowance_computed_against_base_salary(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='1000.00')
        allowance_type = AllowanceType.objects.create(
            name='Housing', calculation_method='percentage_of_salary', amount_or_rate='0.10', is_taxable=True,
        )
        EmployeeAllowance.objects.create(employee=employee, allowance_type=allowance_type, effective_from='2026-01-01')
        payroll_run = self._run()

        calculate_run(payroll_run)

        payslip = payroll_run.payslips.get(employee=employee)
        self.assertEqual(payslip.gross_pay, Decimal('1100.00'))

    def test_statutory_deductions_reduce_net_pay_below_gross(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='3000.00')
        payroll_run = self._run()

        calculate_run(payroll_run)

        payslip = payroll_run.payslips.get(employee=employee)
        self.assertLess(payslip.net_pay, payslip.gross_pay)
        self.assertTrue(payslip.lines.filter(line_type=PayslipLine.LINE_DEDUCTION_PAYE).exists())
        self.assertTrue(payslip.lines.filter(line_type=PayslipLine.LINE_DEDUCTION_SSNIT_TIER1).exists())

    def test_terminated_employee_is_excluded(self):
        active = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(active, base_salary='1500.00')
        terminated = make_employee('E-2', 'Ada', 'Lovelace', employment_status=Employee.STATUS_TERMINATED)
        give_compensation(terminated, base_salary='1500.00')
        payroll_run = self._run()

        calculate_run(payroll_run)

        self.assertEqual(payroll_run.payslips.count(), 1)
        self.assertTrue(payroll_run.payslips.filter(employee=active).exists())

    def test_employee_with_no_compensation_record_is_skipped(self):
        make_employee('E-1', 'Grace', 'Hopper')
        payroll_run = self._run()

        calculate_run(payroll_run)

        self.assertEqual(payroll_run.payslips.count(), 0)

    def test_recalculating_replaces_not_duplicates(self):
        """HRMS-NFR-005: idempotent — a re-run (e.g. a retried Celery
        task) must not leave two payslips for the same employee/run."""
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='1500.00')
        payroll_run = self._run()

        calculate_run(payroll_run)
        calculate_run(payroll_run)

        self.assertEqual(payroll_run.payslips.filter(employee=employee).count(), 1)
