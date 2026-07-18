"""`docs/07-iam-rbac.md` §2, §3: the six assigned-role groups exist from
migration, and derived roles are not groups."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import ASSIGNED_ROLES, is_employee, is_manager

User = get_user_model()


class AssignedRoleGroupsTests(TestCase):
    def test_all_six_assigned_role_groups_exist(self):
        self.assertEqual(Group.objects.filter(name__in=ASSIGNED_ROLES).count(), 6)


class DerivedRoleTests(TestCase):
    def test_is_employee_is_false_for_anonymous_user(self):
        self.assertFalse(is_employee(AnonymousUser()))

    def test_is_employee_is_false_with_no_employee_record(self):
        user = User.objects.create_user(email='nobody@example.com', password='x')
        self.assertFalse(is_employee(user))

    def test_is_employee_is_true_with_an_active_employee_record(self):
        """Module 6 (Employee Management) supplies `employee`, which this
        derivation now reads (`docs/07-iam-rbac.md` §3.1)."""
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=employee)

        self.assertTrue(is_employee(user))

    def test_is_employee_is_false_once_terminated(self):
        """HRMS-BR-012: terminated, resigned, and retired employees lose access."""
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(), employment_status=Employee.STATUS_TERMINATED,
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=employee)

        self.assertFalse(is_employee(user))

    def test_is_manager_is_false_with_no_reporting_relationship_table(self):
        """Module 8 (Reporting Structure) has not been built yet — there is
        no data to derive `True` from."""
        self.assertFalse(is_manager(object()))
