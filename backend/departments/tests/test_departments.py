"""`/api/departments/`, `docs/06-api-contracts.md` §4.4 and
`docs/07-iam-rbac.md` §4.2's HR configuration row: HR Administrator holds
C, R, U; HR Officer, Recruiter, and Payroll Officer hold R only."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, RECRUITER

User = get_user_model()

DEPARTMENTS_URL = '/api/departments/'


def _detail_url(pk):
    return f'/api/departments/{pk}/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class DepartmentListCreateTests(APITestCase):
    def setUp(self):
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)

    def test_hr_administrator_can_create_a_department(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Department.objects.filter(name='Engineering').exists())

    def test_hr_officer_cannot_create_a_department(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        self.assertEqual(response.status_code, 403)

    def test_hr_officer_can_read_departments(self):
        Department.objects.create(name='Engineering')
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(DEPARTMENTS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_recruiter_and_payroll_officer_can_read_departments(self):
        Department.objects.create(name='Engineering')

        for role in (RECRUITER, PAYROLL_OFFICER):
            user = _user_with_role(f'{role.lower().replace(" ", "")}@example.com', role)
            self.client.force_authenticate(user)

            response = self.client.get(DEPARTMENTS_URL)

            self.assertEqual(response.status_code, 200)

    def test_duplicate_name_is_rejected(self):
        Department.objects.create(name='Engineering')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        self.assertEqual(response.status_code, 400)

    def test_anonymous_is_denied(self):
        response = self.client.get(DEPARTMENTS_URL)

        self.assertEqual(response.status_code, 401)


class DepartmentDetailTests(APITestCase):
    def setUp(self):
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.department = Department.objects.create(name='Engineering')

    def test_hr_administrator_can_retire_a_department(self):
        """`PATCH {"is_active": false}` retires rather than deletes,
        `docs/05-database-schema.md` §2.3 — there is no `DELETE`."""
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.department.pk), {'is_active': False})

        self.assertEqual(response.status_code, 200)
        self.department.refresh_from_db()
        self.assertFalse(self.department.is_active)

    def test_hr_officer_cannot_update_a_department(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(_detail_url(self.department.pk), {'is_active': False})

        self.assertEqual(response.status_code, 403)
