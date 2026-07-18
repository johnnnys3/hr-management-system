"""`/api/reporting-relationships/`, `docs/06-api-contracts.md` §4.5."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER
from reporting_structure.models import ReportingRelationship

User = get_user_model()

RELATIONSHIPS_URL = '/api/reporting-relationships/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class ReportingRelationshipListTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
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
        self.relationship = ReportingRelationship.objects.create(
            employee=self.report, manager_employee=self.manager, effective_from=date.today(),
        )

    def test_hr_officer_can_read_reporting_relationships(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(RELATIONSHIPS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_hr_administrator_can_read_reporting_relationships(self):
        hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(hr_admin)

        response = self.client.get(RELATIONSHIPS_URL)

        self.assertEqual(response.status_code, 200)

    def test_filterable_by_manager_employee_id(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(RELATIONSHIPS_URL, {'manager_employee_id': self.manager.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(RELATIONSHIPS_URL, {'manager_employee_id': self.report.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_employee_without_hr_role_is_denied(self):
        employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.client.force_authenticate(employee_user)

        response = self.client.get(RELATIONSHIPS_URL)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(RELATIONSHIPS_URL)

        self.assertEqual(response.status_code, 401)
