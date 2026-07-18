"""`reporting_relationship`, `docs/05-database-schema.md` §4.6."""
from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from reporting_structure.models import ReportingRelationship


def _hire(employee_number, department, job_title):
    return Employee.objects.create(
        employee_number=employee_number, first_name='Ada', last_name='Lovelace',
        date_of_birth='1990-01-01', department=department, job_title=job_title,
        hire_date=date.today(),
    )


class ReportingRelationshipModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')

    def test_an_employee_cannot_be_their_own_manager(self):
        """`CHECK (employee_id <> manager_employee_id)`, schema §4.6."""
        employee = _hire('E-1', self.department, self.job_title)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReportingRelationship.objects.create(
                    employee=employee, manager_employee=employee, effective_from=date.today(),
                )

    def test_an_employee_has_at_most_one_current_manager(self):
        """One row per employee — a current-state table, not history."""
        employee = _hire('E-1', self.department, self.job_title)
        manager_one = _hire('E-2', self.department, self.job_title)
        manager_two = _hire('E-3', self.department, self.job_title)
        ReportingRelationship.objects.create(
            employee=employee, manager_employee=manager_one, effective_from=date.today(),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReportingRelationship.objects.create(
                    employee=employee, manager_employee=manager_two, effective_from=date.today(),
                )
