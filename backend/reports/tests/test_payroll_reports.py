from rest_framework.test import APITestCase

from iam.roles import EXECUTIVE, HR_OFFICER, PAYROLL_OFFICER
from payroll.models import PayrollRun
from payroll.services import calculate_run

from .helpers import give_compensation, make_employee, user_with_role


class PayrollReportTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(self.employee, base_salary='1500.00')
        officer = user_with_role('officer@example.com', PAYROLL_OFFICER)
        self.payroll_run = PayrollRun.objects.create(
            period_start='2026-01-01', period_end='2026-01-31', initiated_by=officer,
        )
        calculate_run(self.payroll_run)
        # Finalized status only, bypassing the real PDF/bank-transfer
        # side effects of `finalize_run` — irrelevant to what this
        # report aggregates.
        self.payroll_run.status = PayrollRun.STATUS_FINALIZED
        self.payroll_run.save(update_fields=['status'])

    def test_payroll_officer_gets_full_breakdown_on_cost_report(self):
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/reports/payroll-cost/')

        self.assertEqual(response.status_code, 200)
        self.assertGreater(float(response.data['aggregate']['gross_pay']), 0)
        self.assertIn('breakdown', response.data)

    def test_executive_gets_aggregate_only_on_cost_report(self):
        """HRMS-NFR-019: never a payslip or individual employee figure."""
        self.client.force_authenticate(user_with_role('exec@example.com', EXECUTIVE))

        response = self.client.get('/api/reports/payroll-cost/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakdown', response.data)

    def test_hr_officer_is_denied_payroll_cost(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get('/api/reports/payroll-cost/')

        self.assertEqual(response.status_code, 403)

    def test_payroll_summary_aggregates_per_run(self):
        """HRMS-FR-045: per-run, not per-payslip."""
        self.client.force_authenticate(user_with_role('other@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/reports/payroll-summary/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['payslip_count'], 1)

    def test_executive_who_also_holds_payroll_officer_gets_aggregate_only(self):
        user = user_with_role('both@example.com', EXECUTIVE)
        user.groups.add(user.groups.model.objects.get(name=PAYROLL_OFFICER))
        self.client.force_authenticate(user)

        response = self.client.get('/api/reports/payroll-cost/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakdown', response.data)
