"""`GET /api/employees/{id}/audit-history/`, `docs/06-api-contracts.md`
§4.1: HR Administrator, HR Officer, System Administrator read access
(HRMS-FR-010) — distinct from the full log's System-Administrator-only
row, since this is a filtered read scoped to one employee record.

Documented since M1 but never implemented — found by the `contracts`
app's M18 contract-test suite.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from audit.models import AuditLog

User = get_user_model()

DENIED_ROLES = ['Payroll Officer', 'Executive']


def _url(employee_id):
    return f'/api/employees/{employee_id}/audit-history/'


class EmployeeAuditHistoryTests(APITestCase):
    def setUp(self):
        AuditLog.objects.create(
            category=AuditLog.CATEGORY_RECORD_CHANGE, action='status_changed',
            target_type='employee', target_id=1,
        )
        AuditLog.objects.create(
            category=AuditLog.CATEGORY_RECORD_CHANGE, action='status_changed',
            target_type='employee', target_id=2,
        )
        AuditLog.objects.create(category=AuditLog.CATEGORY_LOGIN_ATTEMPT, action='login_success')
        # Colliding target_id with a different target_type — the null-target
        # row above is excluded by the id predicate alone, so this is the
        # row that actually proves the target_type='employee' filter holds.
        AuditLog.objects.create(
            category=AuditLog.CATEGORY_RECORD_CHANGE, action='status_changed',
            target_type='department', target_id=1,
        )

    def _user_in_group(self, email, group_name):
        user = User.objects.create_user(email=email, password='irrelevant')
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user

    def test_hr_administrator_can_read(self):
        user = self._user_in_group('hra@example.com', 'HR Administrator')
        self.client.force_authenticate(user)

        response = self.client.get(_url(1))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['target_id'], 1)

    def test_hr_officer_can_read(self):
        user = self._user_in_group('hro@example.com', 'HR Officer')
        self.client.force_authenticate(user)

        response = self.client.get(_url(1))

        self.assertEqual(response.status_code, 200)

    def test_system_administrator_can_read(self):
        user = self._user_in_group('sysadmin@example.com', 'System Administrator')
        self.client.force_authenticate(user)

        response = self.client.get(_url(1))

        self.assertEqual(response.status_code, 200)

    def test_scoped_to_the_named_employee_only(self):
        user = self._user_in_group('hra2@example.com', 'HR Administrator')
        self.client.force_authenticate(user)

        response = self.client.get(_url(1))

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['target_id'], 1)

    def test_excludes_non_employee_targets_with_colliding_ids(self):
        """A `department` row with `target_id=1` — the same id as the
        employee under test — must never surface here; excluding it
        requires the `target_type='employee'` filter to actually hold, not
        just the id predicate (which the null-target `login_attempt` row
        alone wouldn't prove)."""
        user = self._user_in_group('hra3@example.com', 'HR Administrator')
        self.client.force_authenticate(user)

        response = self.client.get(_url(1))

        self.assertTrue(all(row['target_type'] == 'employee' for row in response.data['results']))

    def test_anonymous_is_denied(self):
        response = self.client.get(_url(1))

        self.assertIn(response.status_code, (401, 403))

    def test_other_roles_are_denied(self):
        for role in DENIED_ROLES:
            with self.subTest(role=role):
                user = self._user_in_group(f'user_{role.replace(" ", "_").lower()}@example.com', role)
                self.client.force_authenticate(user)

                response = self.client.get(_url(1))

                self.assertEqual(response.status_code, 403)
