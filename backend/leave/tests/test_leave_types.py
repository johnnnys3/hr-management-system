"""`GET /api/leave-types/`, `docs/06-api-contracts.md` §4.12."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

from .helpers import make_employee, user_with_role

User = get_user_model()

URL = '/api/leave-types/'


class LeaveTypeListTests(APITestCase):
    def test_hr_officer_can_read(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_hr_administrator_can_read(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(URL)

        self.assertEqual(response.status_code, 401)
