"""`docs/07-iam-rbac.md` §4.2: System Administrator holds R on the audit
log; every other role is denied. `docs/02-project-plan.md` §7.3 costs most
of M1's estimate into asserting the denied path.

Six assigned roles exist (`docs/07-iam-rbac.md` §2.3): System
Administrator, HR Administrator, HR Officer, Recruiter, Payroll Officer,
Executive — modelled here as Django groups, seeded ad hoc since IAM/RBAC
(module 4) has not built the real seed data yet. Employee and Manager are
derived roles, never granted as groups (§3); a user with no employee
record and no group membership is the closest proxy available before
Employee Management (module 6) exists, and is asserted here as
"authenticated, no groups."
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from audit.models import AuditLog
from audit.permissions import SYSTEM_ADMINISTRATOR_GROUP

User = get_user_model()

ASSIGNED_ROLES_OTHER_THAN_SYSTEM_ADMINISTRATOR = [
    'HR Administrator',
    'HR Officer',
    'Recruiter',
    'Payroll Officer',
    'Executive',
]

AUDIT_LOG_URL = '/api/audit-log/'


class AuditLogReadSurfaceTests(APITestCase):
    def setUp(self):
        AuditLog.objects.create(category=AuditLog.CATEGORY_LOGIN_ATTEMPT, action='login_success')

    def _user_in_group(self, username, group_name):
        user = User.objects.create_user(username=username, password='irrelevant')
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user

    def test_system_administrator_can_read(self):
        user = self._user_in_group('sysadmin', SYSTEM_ADMINISTRATOR_GROUP)
        self.client.force_authenticate(user)

        response = self.client.get(AUDIT_LOG_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_anonymous_is_denied(self):
        response = self.client.get(AUDIT_LOG_URL)

        self.assertIn(response.status_code, (401, 403))

    def test_authenticated_user_with_no_group_is_denied(self):
        """Proxy for the derived Employee/Manager roles until module 6 exists."""
        user = User.objects.create_user(username='no_group', password='irrelevant')
        self.client.force_authenticate(user)

        response = self.client.get(AUDIT_LOG_URL)

        self.assertEqual(response.status_code, 403)

    def test_other_assigned_roles_are_denied(self):
        for role in ASSIGNED_ROLES_OTHER_THAN_SYSTEM_ADMINISTRATOR:
            with self.subTest(role=role):
                user = self._user_in_group(f'user_{role.replace(" ", "_").lower()}', role)
                self.client.force_authenticate(user)

                response = self.client.get(AUDIT_LOG_URL)

                self.assertEqual(response.status_code, 403)

    def test_read_surface_exposes_no_write_methods(self):
        user = self._user_in_group('sysadmin2', SYSTEM_ADMINISTRATOR_GROUP)
        self.client.force_authenticate(user)

        self.assertEqual(self.client.post(AUDIT_LOG_URL, {}).status_code, 405)
        self.assertEqual(self.client.put(AUDIT_LOG_URL, {}).status_code, 405)
        self.assertEqual(self.client.delete(AUDIT_LOG_URL).status_code, 405)
