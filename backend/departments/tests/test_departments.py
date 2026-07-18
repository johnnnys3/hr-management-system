"""`/api/departments/`, `docs/06-api-contracts.md` §4.4 and
`docs/07-iam-rbac.md` §4.2's HR configuration row: HR Administrator holds
C, R, U; HR Officer, Recruiter, and Payroll Officer hold R only."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from audit.models import AuditLog
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

    def test_anonymous_cannot_create(self):
        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        self.assertEqual(response.status_code, 401)
        self.assertFalse(Department.objects.filter(name='Engineering').exists())

    def test_authenticated_user_with_no_group_is_denied(self):
        Department.objects.create(name='Engineering')
        bystander = User.objects.create_user(email='bystander@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.get(DEPARTMENTS_URL)

        self.assertEqual(response.status_code, 403)

    def test_break_glass_is_superuser_account_without_role_is_denied(self):
        """§7.2: `is_superuser` is reserved for break-glass, not a stand-in
        for HR Administrator group membership."""
        break_glass = User.objects.create_superuser(email='breakglass@example.com', password='x')
        self.client.force_authenticate(break_glass)

        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        self.assertEqual(response.status_code, 403)

    def test_departments_are_returned_ordered_by_name(self):
        Department.objects.create(name='Sales')
        Department.objects.create(name='Engineering')
        Department.objects.create(name='Marketing')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.get(DEPARTMENTS_URL)

        self.assertEqual(
            [row['name'] for row in response.data],
            ['Engineering', 'Marketing', 'Sales'],
        )

    def test_blank_name_is_rejected(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(DEPARTMENTS_URL, {'name': ''})

        self.assertEqual(response.status_code, 400)

    def test_missing_name_is_rejected(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(DEPARTMENTS_URL, {})

        self.assertEqual(response.status_code, 400)

    def test_read_only_fields_are_ignored_on_create(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(
            DEPARTMENTS_URL,
            {'name': 'Engineering', 'id': 999, 'created_at': '2000-01-01T00:00:00Z'},
        )

        self.assertEqual(response.status_code, 201)
        department = Department.objects.get(name='Engineering')
        self.assertNotEqual(department.pk, 999)
        self.assertNotEqual(department.created_at.year, 2000)

    def test_creating_a_department_records_an_audit_log_entry(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(DEPARTMENTS_URL, {'name': 'Engineering'})

        department_id = response.data['id']
        self.assertTrue(
            AuditLog.objects.filter(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='department_created',
                actor=self.hr_admin,
                target_type='department',
                target_id=department_id,
            ).exists()
        )


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

    def test_hr_administrator_can_update_a_department_name(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.department.pk), {'name': 'Product Engineering'})

        self.assertEqual(response.status_code, 200)
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, 'Product Engineering')

    def test_updating_to_a_duplicate_name_is_rejected(self):
        Department.objects.create(name='Marketing')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.department.pk), {'name': 'Marketing'})

        self.assertEqual(response.status_code, 400)

    def test_read_only_fields_are_ignored_on_update(self):
        self.client.force_authenticate(self.hr_admin)
        original_created_at = self.department.created_at

        response = self.client.patch(_detail_url(self.department.pk), {'created_at': '2000-01-01T00:00:00Z'})

        self.assertEqual(response.status_code, 200)
        self.department.refresh_from_db()
        self.assertEqual(self.department.created_at, original_created_at)

    def test_unknown_department_returns_404(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(999999), {'is_active': False})

        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_update(self):
        response = self.client.patch(_detail_url(self.department.pk), {'is_active': False})

        self.assertEqual(response.status_code, 401)

    def test_updating_a_department_records_an_audit_log_entry(self):
        self.client.force_authenticate(self.hr_admin)

        self.client.patch(_detail_url(self.department.pk), {'is_active': False})

        self.assertTrue(
            AuditLog.objects.filter(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='department_updated',
                actor=self.hr_admin,
                target_type='department',
                target_id=self.department.pk,
            ).exists()
        )
