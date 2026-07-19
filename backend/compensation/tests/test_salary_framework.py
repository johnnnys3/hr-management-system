"""`GET, POST, PATCH /api/salary-structures/`, `/api/pay-grades/`,
`docs/06-api-contracts.md` §4.13."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER

from .helpers import make_employee, make_pay_grade, user_with_role

User = get_user_model()


class SalaryStructureTests(APITestCase):
    def test_hr_administrator_can_create(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 201)

    def test_hr_officer_can_read_but_not_create(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        read = self.client.get('/api/salary-structures/')
        write = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(read.status_code, 200)
        self.assertEqual(write.status_code, 403)

    def test_payroll_officer_can_read(self):
        self.client.force_authenticate(user_with_role('payroll@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 200)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 401)


class PayGradeTests(APITestCase):
    def test_hr_administrator_can_create_and_update(self):
        user = user_with_role('hra@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(user)
        structure_id = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        ).data['id']

        create = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': structure_id, 'name': 'Grade 1', 'min_salary': '1000.00', 'max_salary': '2000.00'},
        )
        update = self.client.patch(f"/api/pay-grades/{create.data['id']}/", {'max_salary': '2500.00'})

        self.assertEqual(create.status_code, 201)
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.data['max_salary'], '2500.00')

    def test_max_salary_below_min_salary_is_rejected(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        structure_id = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        ).data['id']

        response = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': structure_id, 'name': 'Grade 1', 'min_salary': '2000.00', 'max_salary': '1000.00'},
        )

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_can_read_but_not_create(self):
        make_pay_grade()
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get('/api/pay-grades/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/pay-grades/')

        self.assertEqual(response.status_code, 403)
