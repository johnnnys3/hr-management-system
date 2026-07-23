"""Idempotent test-data seed for the Playwright suite
(`frontend/e2e/`, `docs/08-testing-plan.md` §6). Never run against a real
deployment — passwords are fixed and public in this file.

Not a migration: this is test-only data, invoked explicitly by CI/local
`docker compose run` before the E2E suite, the same way `docs/README.md`'s
account-bootstrap snippet is invoked explicitly rather than shipped as a
migration.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from accounts import totp
from accounts.models import SecondFactor
from compensation.models import CompensationRecord, PayGrade, SalaryStructure
from departments.models import Department, JobTitle
from employees.models import Employee
from reporting_structure.models import ReportingRelationship

User = get_user_model()
PASSWORD = 'E2eTestpass123!'
# HRMS-NFR-024 requires TOTP on every login for Payroll Officer/System
# Administrator — fixed rather than random so frontend/e2e/helpers/totp.ts
# can compute a matching code without reading it back out of the database.
TOTP_SECRET = 'JBSWY3DPEHPK3PXP'


class Command(BaseCommand):
    help = 'Seed deterministic fixtures for the Playwright E2E suite. Test-only, idempotent.'

    def handle(self, *args, **options):
        department = Department.objects.get_or_create(name='E2E Engineering')[0]
        job_title = JobTitle.objects.get_or_create(name='E2E Engineer')[0]

        manager_employee = self._employee('E2E-MGR', 'Manager', 'Person', department, job_title)
        report_employee = self._employee('E2E-EMP', 'Employee', 'Person', department, job_title)
        target_employee = self._employee('E2E-TGT', 'Target', 'Person', department, job_title)
        ReportingRelationship.objects.get_or_create(
            employee=report_employee,
            defaults={'manager_employee': manager_employee, 'effective_from': date(2024, 1, 1)},
        )

        salary_structure = SalaryStructure.objects.get_or_create(
            name='E2E Structure', defaults={'effective_from': date(2024, 1, 1)},
        )[0]
        PayGrade.objects.get_or_create(
            salary_structure=salary_structure, name='E2E Grade 1',
            defaults={'min_salary': '1000.00', 'max_salary': '5000.00'},
        )
        CompensationRecord.objects.get_or_create(
            employee=report_employee, is_superseded=False,
            defaults={'base_salary': '3000.00', 'effective_from': date(2024, 1, 1)},
        )

        self._user('e2e.hro@example.com', 'HR Officer')
        self._user('e2e.hra@example.com', 'HR Administrator')
        self._user('e2e.recruiter@example.com', 'Recruiter')
        payroll_initiator = self._user('e2e.payroll1@example.com', 'Payroll Officer')
        payroll_approver = self._user('e2e.payroll2@example.com', 'Payroll Officer')
        # payroll.approve_payroll_run is granted to no role by default
        # (docs/07-iam-rbac.md §4.4 — deployment-deferred, same shape as
        # iam.approve_role_grant); this is the distinct approver HRMS-BR-008
        # requires, granted the permission directly, not via a group.
        payroll_approver.user_permissions.add(Permission.objects.get(codename='approve_payroll_run'))
        self._enroll_second_factor(payroll_initiator)
        self._enroll_second_factor(payroll_approver)
        # Manager is a derived role (`iam.roles.is_manager`), never an
        # assigned group — this account's manager status comes entirely
        # from the ReportingRelationship row above naming it as a manager.
        self._user('e2e.manager@example.com', None, employee=manager_employee)
        self._user('e2e.employee@example.com', None, employee=report_employee)

        self.stdout.write(self.style.SUCCESS('E2E fixtures seeded.'))

    def _employee(self, number, first_name, last_name, department, job_title):
        return Employee.objects.get_or_create(
            employee_number=number,
            defaults={
                'first_name': first_name, 'last_name': last_name, 'date_of_birth': date(1990, 1, 1),
                'department': department, 'job_title': job_title, 'hire_date': date(2024, 1, 1),
            },
        )[0]

    def _user(self, email, group_name, employee=None):
        # Password always reset, not only on creation: an email address
        # this script uses can already exist from an unrelated earlier
        # session with a different password (found the hard way — this
        # command silently produced an account whose password didn't
        # match what it just claimed to seed).
        user, _created = User.objects.get_or_create(email=email, defaults={'employee': employee})
        user.set_password(PASSWORD)
        if employee is not None and user.employee_id != employee.id:
            user.employee = employee
        user.save()
        if group_name:
            user.groups.add(Group.objects.get(name=group_name))
        return user

    def _enroll_second_factor(self, user):
        SecondFactor.objects.update_or_create(
            user=user,
            defaults={'secret_ref': totp.encrypt_secret(TOTP_SECRET), 'disabled_at': None},
        )
