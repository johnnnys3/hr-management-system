"""`/api/users/`, `docs/06-api-contracts.md` §4.9 and `docs/07-iam-rbac.md`
§7.1: System Administrator only, no employee/payroll field exposure, no
route to `is_superuser`."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from iam.roles import SYSTEM_ADMINISTRATOR

User = get_user_model()

USERS_URL = '/api/users/'


def _detail_url(pk):
    return f'/api/users/{pk}/'


class UserListCreateTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@example.com', password='x')
        self.admin.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))

    def test_system_administrator_can_create_a_user(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(USERS_URL, {'email': 'new@example.com', 'password': 'x'})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_created_user_has_a_usable_password(self):
        self.client.force_authenticate(self.admin)

        self.client.post(USERS_URL, {'email': 'new@example.com', 'password': 'a-real-password'})

        user = User.objects.get(email='new@example.com')
        self.assertTrue(user.check_password('a-real-password'))

    def test_response_never_exposes_is_superuser_or_is_staff(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(USERS_URL, {'email': 'new@example.com', 'password': 'x'})

        self.assertNotIn('is_superuser', response.data)
        self.assertNotIn('is_staff', response.data)

    def test_is_superuser_in_the_request_body_is_ignored(self):
        self.client.force_authenticate(self.admin)

        self.client.post(USERS_URL, {'email': 'new@example.com', 'password': 'x', 'is_superuser': True})

        user = User.objects.get(email='new@example.com')
        self.assertFalse(user.is_superuser)

    def test_ordinary_user_cannot_reach_the_endpoint(self):
        bystander = User.objects.create_user(email='bystander@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, 403)

    def test_break_glass_is_superuser_account_is_not_a_system_administrator(self):
        """§7.2: `is_superuser` is reserved for break-glass, not a stand-in
        for group membership. This endpoint's permission check is
        deliberately not `has_perm`-based, so an `is_superuser` account
        with no System Administrator membership must not pass."""
        break_glass = User.objects.create_superuser(email='breakglass@example.com', password='x')
        self.client.force_authenticate(break_glass)

        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, 401)


class UserDetailTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@example.com', password='x')
        self.admin.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))
        self.target = User.objects.create_user(email='target@example.com', password='x')

    def test_system_administrator_can_deactivate_a_user(self):
        self.client.force_authenticate(self.admin)

        response = self.client.patch(_detail_url(self.target.pk), {'is_active': False})

        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_groups_field_is_read_only(self):
        """Role assignment goes through `/api/role-grant-requests/`, where
        §7.3's constraints are enforced — this endpoint must not offer a
        second, unconstrained grant path."""
        payroll = Group.objects.get(name='Payroll Officer')
        self.client.force_authenticate(self.admin)

        self.client.patch(_detail_url(self.target.pk), {'groups': [payroll.pk]})

        self.assertFalse(self.target.groups.filter(name='Payroll Officer').exists())
