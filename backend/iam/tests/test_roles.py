"""`docs/07-iam-rbac.md` §2, §3: the six assigned-role groups exist from
migration, and derived roles are not groups."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import ASSIGNED_ROLES, SYSTEM_ADMINISTRATOR, is_employee, is_manager
from reporting_structure.models import ReportingRelationship

User = get_user_model()


class AssignedRoleGroupsTests(TestCase):
    def test_all_six_assigned_role_groups_exist(self):
        self.assertEqual(Group.objects.filter(name__in=ASSIGNED_ROLES).count(), 6)


class AssignedRolesListViewTests(APITestCase):
    def test_system_administrator_sees_all_six_assigned_roles(self):
        admin = User.objects.create_user(email='admin2@example.com', password='x')
        admin.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))
        self.client.force_authenticate(admin)

        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual({r['name'] for r in response.data}, set(ASSIGNED_ROLES))

    def test_non_system_administrator_is_denied(self):
        non_admin = User.objects.create_user(email='non-admin2@example.com', password='x')
        self.client.force_authenticate(non_admin)

        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 401)


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

    def _hire(self, employee_number, first_name):
        department = Department.objects.first() or Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.first() or JobTitle.objects.create(name='Engineer')
        return Employee.objects.create(
            employee_number=employee_number, first_name=first_name, last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )

    def test_is_manager_is_false_for_anonymous_user(self):
        self.assertFalse(is_manager(AnonymousUser()))

    def test_is_manager_is_false_with_no_direct_reports(self):
        employee = self._hire('E-1', 'Ada')
        user = User.objects.create_user(email='ada@example.com', password='x', employee=employee)

        self.assertFalse(is_manager(user))

    def test_is_manager_is_true_with_a_direct_report(self):
        """`docs/05-database-schema.md` §4.6's derivation query."""
        manager = self._hire('E-1', 'Ada')
        report = self._hire('E-2', 'Grace')
        ReportingRelationship.objects.create(employee=report, manager_employee=manager, effective_from=date.today())
        user = User.objects.create_user(email='ada@example.com', password='x', employee=manager)

        self.assertTrue(is_manager(user))

    def test_is_manager_is_false_once_the_manager_is_terminated(self):
        """A terminated manager must not go on deriving the Manager role
        from a `reporting_relationship` row that has not yet been
        reassigned (schema §4.6's stale-reporting-line note)."""
        manager = self._hire('E-1', 'Ada')
        report = self._hire('E-2', 'Grace')
        ReportingRelationship.objects.create(employee=report, manager_employee=manager, effective_from=date.today())
        manager.employment_status = Employee.STATUS_TERMINATED
        manager.save()
        user = User.objects.create_user(email='ada@example.com', password='x', employee=manager)

        self.assertFalse(is_manager(user))
