"""`docs/07-iam-rbac.md` §2, §3: the six assigned-role groups exist from
migration, and derived roles are not groups."""
from django.contrib.auth.models import Group
from django.test import TestCase

from iam.roles import ASSIGNED_ROLES, is_employee, is_manager


class AssignedRoleGroupsTests(TestCase):
    def test_all_six_assigned_role_groups_exist(self):
        self.assertEqual(Group.objects.filter(name__in=ASSIGNED_ROLES).count(), 6)


class DerivedRoleTests(TestCase):
    def test_is_employee_is_false_with_no_employee_table(self):
        """Module 6 (Employee Management) has not been built yet — there is
        no data to derive `True` from."""
        self.assertFalse(is_employee(object()))

    def test_is_manager_is_false_with_no_employee_table(self):
        self.assertFalse(is_manager(object()))
