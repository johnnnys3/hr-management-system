"""`/api/employees/{id}/manager/`, `docs/06-api-contracts.md` §4.5."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee, EmploymentHistory
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER
from reporting_structure.models import ReportingRelationship

User = get_user_model()


def _manager_url(pk):
    return f'/api/employees/{pk}/manager/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class ManagerChangeTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='E-1', first_name='Grace', last_name='Hopper',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        self.manager_one = Employee.objects.create(
            employee_number='E-2', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        self.manager_two = Employee.objects.create(
            employee_number='E-3', first_name='Alan', last_name='Turing',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )

    def test_hr_officer_can_set_a_manager(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.manager_one.pk})

        self.assertEqual(response.status_code, 200)
        relationship = ReportingRelationship.objects.get(employee=self.employee)
        self.assertEqual(relationship.manager_employee_id, self.manager_one.pk)
        self.assertTrue(
            EmploymentHistory.objects.filter(
                employee=self.employee, event_type=EmploymentHistory.EVENT_MANAGER_CHANGE,
            ).exists()
        )

    def test_reassigning_replaces_the_current_row_rather_than_adding_a_second(self):
        self.client.force_authenticate(self.hr_officer)
        self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.manager_one.pk})

        response = self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.manager_two.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReportingRelationship.objects.filter(employee=self.employee).count(), 1)
        relationship = ReportingRelationship.objects.get(employee=self.employee)
        self.assertEqual(relationship.manager_employee_id, self.manager_two.pk)

        history = EmploymentHistory.objects.filter(
            employee=self.employee, event_type=EmploymentHistory.EVENT_MANAGER_CHANGE,
        ).order_by('id').last()
        self.assertEqual(history.previous_value, {'manager_employee_id': self.manager_one.pk})
        self.assertEqual(history.new_value, {'manager_employee_id': self.manager_two.pk})

    def test_an_employee_cannot_be_set_as_their_own_manager(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.employee.pk})

        self.assertEqual(response.status_code, 400)

    def test_hr_administrator_cannot_change_a_manager(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.manager_one.pk})

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.patch(_manager_url(self.employee.pk), {'manager_employee_id': self.manager_one.pk})

        self.assertEqual(response.status_code, 401)
