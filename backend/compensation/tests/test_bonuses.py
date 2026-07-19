"""`GET, POST, PATCH /api/bonus-cycles/`, `GET, POST /api/bonus-cycles/{id}/awards/`,
`docs/06-api-contracts.md` §4.13."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

from ..models import BonusCycle
from .helpers import make_employee, user_with_role

User = get_user_model()


class BonusCycleTests(APITestCase):
    def test_hr_administrator_can_create_and_update(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        create = self.client.post(
            '/api/bonus-cycles/',
            {'name': 'Q1 2026', 'period_start': '2026-01-01', 'period_end': '2026-03-31'},
        )
        update = self.client.patch(f"/api/bonus-cycles/{create.data['id']}/", {'status': 'closed'})

        self.assertEqual(create.status_code, 201)
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.data['status'], 'closed')

    def test_hr_officer_can_read_but_not_create(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.post(
            '/api/bonus-cycles/', {'name': 'Q1 2026', 'period_start': '2026-01-01', 'period_end': '2026-03-31'}
        )

        self.assertEqual(response.status_code, 403)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/bonus-cycles/')

        self.assertEqual(response.status_code, 403)


class BonusAwardTests(APITestCase):
    def setUp(self):
        self.cycle = BonusCycle.objects.create(name='Q1 2026', period_start='2026-01-01', period_end='2026-03-31')
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.url = f'/api/bonus-cycles/{self.cycle.pk}/awards/'

    def test_hr_administrator_can_create(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(self.url, {'employee': self.employee.pk, 'amount': '500.00'})

        self.assertEqual(response.status_code, 201)

    def test_hr_officer_is_denied(self):
        """§4.13: bonus awards are HR Administrator only — no HR Officer
        read/write, unlike allowances/benefits on the same IAM row."""
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_employee_self_read_is_denied(self):
        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
