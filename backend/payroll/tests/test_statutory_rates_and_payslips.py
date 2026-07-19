from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, PAYROLL_OFFICER

from ..models import PayrollRun
from ..services import calculate_run, generate_payslip_pdf
from .helpers import give_compensation, make_employee, user_with_role

User = get_user_model()


class StatutoryRateTableTests(APITestCase):
    def test_payroll_officer_can_read(self):
        self.client.force_authenticate(user_with_role('officer@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/statutory-rates/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)  # seeded placeholder rates, 0002

    def test_hr_administrator_is_denied(self):
        """`docs/06-api-contracts.md` §4.14: 'Granted to Payroll Officer
        alone' — not a §4.2 matrix cell, a named exception."""
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.get('/api/statutory-rates/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/statutory-rates/')

        self.assertEqual(response.status_code, 401)


class PayslipVisibilityTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(self.employee, base_salary='1500.00')
        officer = user_with_role('officer@example.com', PAYROLL_OFFICER)
        self.payroll_run = PayrollRun.objects.create(
            period_start='2026-01-01', period_end='2026-01-31', initiated_by=officer,
        )
        calculate_run(self.payroll_run)
        self.payslip = self.payroll_run.payslips.get(employee=self.employee)

    def test_payroll_officer_can_read_all(self):
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/payslips/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_can_read_own(self):
        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/payslips/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.payslip.pk)

    def test_employee_cannot_read_anothers(self):
        other = make_employee('E-2', 'Ada', 'Lovelace')
        other_user = User.objects.create_user(email='ada@example.com', password='x', employee=other)
        self.client.force_authenticate(other_user)

        response = self.client.get(f'/api/payslips/{self.payslip.pk}/')

        self.assertEqual(response.status_code, 403)

    def test_payslip_detail_includes_lines(self):
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get(f'/api/payslips/{self.payslip.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['lines']), 0)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/payslips/')

        self.assertEqual(response.status_code, 401)

    def test_download_404_before_finalisation(self):
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get(f'/api/payslips/{self.payslip.pk}/download/')

        self.assertEqual(response.status_code, 404)

    def test_download_after_pdf_generated(self):
        generate_payslip_pdf(self.payslip)
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get(f'/api/payslips/{self.payslip.pk}/download/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.data)

    def test_employee_cannot_download_anothers(self):
        generate_payslip_pdf(self.payslip)
        other = make_employee('E-2', 'Ada', 'Lovelace')
        other_user = User.objects.create_user(email='ada2@example.com', password='x', employee=other)
        self.client.force_authenticate(other_user)

        response = self.client.get(f'/api/payslips/{self.payslip.pk}/download/')

        self.assertEqual(response.status_code, 403)
