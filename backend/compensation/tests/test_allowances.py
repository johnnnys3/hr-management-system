"""`GET, POST, PATCH /api/allowance-types/`, `GET, POST /api/employees/{id}/allowances/`,
`docs/06-api-contracts.md` §4.13."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

from ..models import AllowanceType
from .helpers import make_employee, user_with_role

User = get_user_model()


class AllowanceTypeTests(APITestCase):
    def test_hr_administrator_can_create(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            '/api/allowance-types/',
            {'name': 'Transport', 'calculation_method': 'fixed', 'amount_or_rate': '200.00', 'is_taxable': False},
        )

        self.assertEqual(response.status_code, 201)

    def test_percentage_rate_above_one_is_rejected(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            '/api/allowance-types/',
            {
                'name': 'Housing', 'calculation_method': 'percentage_of_salary',
                'amount_or_rate': '1.5', 'is_taxable': True,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_can_read_but_not_create(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.post(
            '/api/allowance-types/',
            {'name': 'Transport', 'calculation_method': 'fixed', 'amount_or_rate': '200.00', 'is_taxable': False},
        )

        self.assertEqual(response.status_code, 403)


class EmployeeAllowanceTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.allowance_type = AllowanceType.objects.create(
            name='Transport', calculation_method='fixed', amount_or_rate='200.00', is_taxable=False,
        )
        self.url = f'/api/employees/{self.employee.pk}/allowances/'

    def test_hr_administrator_can_create(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            self.url, {'allowance_type': self.allowance_type.pk, 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 201)

    def test_employee_can_read_own(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        self.client.post(self.url, {'allowance_type': self.allowance_type.pk, 'effective_from': '2026-01-01'})

        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_cannot_read_anothers(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        self.client.post(self.url, {'allowance_type': self.allowance_type.pk, 'effective_from': '2026-01-01'})

        other = make_employee('E-2', 'Ada', 'Lovelace')
        other_user = User.objects.create_user(email='ada@example.com', password='x', employee=other)
        self.client.force_authenticate(other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_create(self):
        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.post(
            self.url, {'allowance_type': self.allowance_type.pk, 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 403)
