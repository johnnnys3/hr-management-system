"""`docs/08-testing-plan.md` §3.4 completeness sweep: every constraint
`docs/05-database-schema.md` §6 names for HRMS-DR-001, -002, -005, -006
gets a test that attempts the violation directly against the database
(a raw model `.save()`/`.create()` bypassing any serializer), asserting
`IntegrityError` — independent of whether a serializer would also catch
it. Building the M18 contract/E2E suites found several of these tables
had only serializer-level (400) coverage, never a direct-database-bypass
test proving the `CHECK`/`UNIQUE` constraint itself holds.

HRMS-DR-006 (`leave_request`) and HRMS-DR-005's `compensation_record` and
`payroll_run`/`role_grant_request`'s self-approval `CHECK`s already have
this coverage in their own apps' test suites (leave/tests/test_models.py,
compensation/tests/test_compensation_records.py, payroll/tests/
test_payroll_runs.py, iam/tests/test_role_grant_requests.py) and are not
duplicated here — this module is only the gaps.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from compensation.models import (
    AllowanceType,
    Benefit,
    BonusAward,
    BonusCycle,
    EmployeeAllowance,
)
from compensation.tests.helpers import make_employee, make_pay_grade
from departments.models import Department, JobTitle
from employees.models import Employee
from payroll.models import Payslip, PayslipLine, PayrollRun
from recruitment.models import Candidate, CandidateApplication, JobPosting, JobRequisition, OfferLetter

User = get_user_model()


class HrmsDr001EmployeeIdUniquenessTests(TestCase):
    """HRMS-DR-001: `employee.employee_number UNIQUE`."""

    def test_duplicate_employee_number_is_rejected_at_the_database(self):
        department = Department.objects.create(name='DR-001 Dept')
        job_title = JobTitle.objects.create(name='DR-001 Role')
        Employee.objects.create(
            employee_number='DUP-1', first_name='A', last_name='One',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Employee.objects.create(
                employee_number='DUP-1', first_name='B', last_name='Two',
                date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
            )


class HrmsDr002EmailUniquenessTests(TestCase):
    """HRMS-DR-002: `user_account.email UNIQUE`."""

    def test_duplicate_email_is_rejected_at_the_database(self):
        User.objects.create_user(email='dup@example.com', password='x')
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(email='dup@example.com', password='y')


class HrmsDr005NonNegativeMoneyTests(TestCase):
    """HRMS-DR-005: every stored monetary magnitude this schema names,
    for the tables `compensation_record`'s own test doesn't already cover."""

    def test_pay_grade_min_salary_gte_0(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_pay_grade(min_salary='-1.00', max_salary='2000.00')

    def test_offer_letter_offered_salary_gte_0(self):
        employee = make_employee('DR5-1', 'A', 'One')
        candidate = Candidate.objects.create(first_name='C', last_name='D', email='c@example.com')
        requisition = JobRequisition.objects.create(
            department=employee.department, job_title=employee.job_title, requested_by=User.objects.create_user(
                email='dr5-requester@example.com', password='x',
            ), status=JobRequisition.STATUS_APPROVED,
        )
        posting = JobPosting.objects.create(
            requisition=requisition, title='DR5 Posting', description='...', channel=JobPosting.CHANNEL_INTERNAL,
        )
        application = CandidateApplication.objects.create(candidate=candidate, posting=posting)
        with self.assertRaises(IntegrityError), transaction.atomic():
            OfferLetter.objects.create(application=application, offered_salary='-1.00')

    def test_bonus_award_amount_gte_0(self):
        employee = make_employee('DR5-2', 'A', 'One')
        cycle = BonusCycle.objects.create(name='DR5 Cycle', period_start=date.today(), period_end=date.today())
        with self.assertRaises(IntegrityError), transaction.atomic():
            BonusAward.objects.create(bonus_cycle=cycle, employee=employee, amount='-1.00')

    def test_allowance_type_amount_or_rate_gte_0(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            AllowanceType.objects.create(
                name='DR5 Allowance', calculation_method=AllowanceType.CALCULATION_FIXED,
                amount_or_rate='-1.00', is_taxable=False,
            )

    def test_employee_allowance_amount_override_gte_0(self):
        employee = make_employee('DR5-3', 'A', 'One')
        allowance_type = AllowanceType.objects.create(
            name='DR5 Allowance Type', calculation_method=AllowanceType.CALCULATION_FIXED,
            amount_or_rate='10.00', is_taxable=False,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmployeeAllowance.objects.create(
                employee=employee, allowance_type=allowance_type, amount_override='-1.00',
                effective_from=date.today(),
            )

    def test_benefit_cost_gte_0(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Benefit.objects.create(name='DR5 Benefit', cost='-1.00')

    def test_payslip_gross_pay_and_net_pay_gte_0(self):
        employee = make_employee('DR5-4', 'A', 'One')
        initiator = User.objects.create_user(email='dr5-4-initiator@example.com', password='x')
        payroll_run = PayrollRun.objects.create(
            period_start=date(2031, 1, 1), period_end=date(2031, 1, 31), initiated_by=initiator,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Payslip.objects.create(payroll_run=payroll_run, employee=employee, gross_pay='-1.00', net_pay='0.00')

    def test_payslip_line_amount_gte_0(self):
        employee = make_employee('DR5-5', 'A', 'One')
        initiator = User.objects.create_user(email='dr5-5-initiator@example.com', password='x')
        payroll_run = PayrollRun.objects.create(
            period_start=date(2031, 2, 1), period_end=date(2031, 2, 28), initiated_by=initiator,
        )
        payslip = Payslip.objects.create(payroll_run=payroll_run, employee=employee, gross_pay='0.00', net_pay='0.00')
        with self.assertRaises(IntegrityError), transaction.atomic():
            PayslipLine.objects.create(payslip=payslip, line_type='allowance', description='x', amount='-1.00')
