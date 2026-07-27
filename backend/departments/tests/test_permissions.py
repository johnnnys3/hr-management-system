"""`CanAccessHRConfiguration`, `docs/07-iam-rbac.md` §4.2's HR
configuration row: HR Administrator holds C, R, U; HR Officer and
Payroll Officer hold R only. Unit-tests `has_permission` directly,
independent of the view-level integration tests in `test_departments.py`
and `test_job_titles.py`."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from departments.permissions import READ_ROLES, CanAccessHRConfiguration
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER

User = get_user_model()


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class CanAccessHRConfigurationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CanAccessHRConfiguration()

    def _has_permission(self, method, user):
        request = getattr(self.factory, method.lower())('/api/departments/')
        request.user = user
        return self.permission.has_permission(request, view=None)

    def test_read_roles_are_exactly_the_three_hr_configuration_read_roles(self):
        self.assertCountEqual(READ_ROLES, [HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER])

    def test_anonymous_user_is_denied_read(self):
        self.assertFalse(self._has_permission('GET', AnonymousUser()))

    def test_anonymous_user_is_denied_write(self):
        self.assertFalse(self._has_permission('POST', AnonymousUser()))

    def test_hr_administrator_can_read_and_write(self):
        user = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)

        self.assertTrue(self._has_permission('GET', user))
        self.assertTrue(self._has_permission('POST', user))
        self.assertTrue(self._has_permission('PATCH', user))

    def test_hr_officer_can_read_but_not_write(self):
        user = _user_with_role('hrofficer@example.com', HR_OFFICER)

        self.assertTrue(self._has_permission('GET', user))
        self.assertFalse(self._has_permission('POST', user))
        self.assertFalse(self._has_permission('PATCH', user))

    def test_payroll_officer_can_read_but_not_write(self):
        user = _user_with_role('payroll@example.com', PAYROLL_OFFICER)

        self.assertTrue(self._has_permission('GET', user))
        self.assertFalse(self._has_permission('POST', user))

    def test_authenticated_user_with_no_group_is_denied_read_and_write(self):
        user = User.objects.create_user(email='nogroup@example.com', password='x')

        self.assertFalse(self._has_permission('GET', user))
        self.assertFalse(self._has_permission('POST', user))

    def test_break_glass_is_superuser_account_without_role_is_denied(self):
        """§7.2: `is_superuser` is not a stand-in for HR Administrator
        group membership."""
        break_glass = User.objects.create_superuser(email='breakglass@example.com', password='x')

        self.assertFalse(self._has_permission('GET', break_glass))
        self.assertFalse(self._has_permission('POST', break_glass))