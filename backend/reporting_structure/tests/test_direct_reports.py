"""`/api/employees/{id}/direct-reports/`, `docs/06-api-contracts.md` §4.5."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_OFFICER
from reporting_structure.models import ReportingRelationship

User = get_user_model()


def _direct_reports_url(pk):
    return f'/api/employees/{pk}/direct-reports/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class DirectReportsTests(APITestCase):
    def setUp(self):
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.manager = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        self.report = Employee.objects.create(
            employee_number='E-2', first_name='Grace', last_name='Hopper',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        self.other_manager = Employee.objects.create(
            employee_number='E-3', first_name='Alan', last_name='Turing',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        self.other_report = Employee.objects.create(
            employee_number='E-4', first_name='Katherine', last_name='Johnson',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        ReportingRelationship.objects.create(
            employee=self.report, manager_employee=self.manager, effective_from=date.today(),
        )
        ReportingRelationship.objects.create(
            employee=self.other_report, manager_employee=self.other_manager, effective_from=date.today(),
        )
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.other_manager_user = User.objects.create_user(
            email='alan@example.com', password='x', employee=self.other_manager,
        )

    def test_manager_can_read_their_own_direct_reports(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.get(_direct_reports_url(self.manager.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employee_number'], 'E-2')

    def test_manager_cannot_read_another_managers_direct_reports(self):
        """The endpoint's visibility is `manager_employee_id = caller's
        employee id`, not any `{id}` a Manager happens to request.
        `other_manager` has their own direct report (`self.other_report`),
        so `is_manager` is `True` and this 403 comes from
        `has_object_permission`, not `has_permission`."""
        self.client.force_authenticate(self.other_manager_user)

        response = self.client.get(_direct_reports_url(self.manager.pk))

        self.assertEqual(response.status_code, 403)

    def test_hr_officer_can_read_any_managers_direct_reports(self):
        hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.client.force_authenticate(hr_officer)

        response = self.client.get(_direct_reports_url(self.manager.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_with_no_direct_reports_is_denied(self):
        employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.client.force_authenticate(employee_user)

        response = self.client.get(_direct_reports_url(self.report.pk))

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(_direct_reports_url(self.manager.pk))

        self.assertEqual(response.status_code, 401)
