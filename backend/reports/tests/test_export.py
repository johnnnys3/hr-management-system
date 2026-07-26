from django.test import override_settings
from rest_framework.test import APITestCase

from audit.models import AuditLog
from iam.roles import EXECUTIVE, HR_ADMINISTRATOR, PAYROLL_OFFICER
from payroll.models import PayrollRun
from payroll.services import calculate_run

from ..models import ReportExport
from .helpers import give_compensation, make_employee, user_with_role


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class ReportExportTests(APITestCase):
    def setUp(self):
        make_employee('E-1', 'Grace', 'Hopper')

    def test_export_returns_202_and_job_id(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_ADMINISTRATOR))

        response = self.client.post('/api/reports/headcount/export/')

        self.assertEqual(response.status_code, 202)
        self.assertIn('id', response.data)

    def test_export_completes_and_poll_returns_download_url(self):
        user = user_with_role('hr@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(user)

        create = self.client.post('/api/reports/headcount/export/')
        job_id = create.data['id']

        poll = self.client.get(f'/api/report-exports/{job_id}/')

        self.assertEqual(poll.status_code, 200)
        self.assertEqual(poll.data['status'], ReportExport.STATUS_COMPLETE)
        self.assertIsNotNone(poll.data['download_url'])

    def test_export_uses_same_permission_as_report_endpoint(self):
        """§4.15: "Same permission as the corresponding report endpoint."
        Payroll cost export is Payroll-Officer/Executive only, an HR
        Officer must be denied even though they can export org reports."""
        self.client.force_authenticate(user_with_role('hr@example.com', HR_ADMINISTRATOR))

        response = self.client.post('/api/reports/payroll-cost/export/')

        self.assertEqual(response.status_code, 403)

    def test_unknown_report_slug_is_404(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_ADMINISTRATOR))

        response = self.client.post('/api/reports/not-a-real-report/export/')

        self.assertEqual(response.status_code, 404)

    def test_poll_is_scoped_to_own_job_only(self):
        owner = user_with_role('hr@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(owner)
        create = self.client.post('/api/reports/headcount/export/')
        job_id = create.data['id']

        other = user_with_role('other@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(other)
        response = self.client.get(f'/api/report-exports/{job_id}/')

        self.assertEqual(response.status_code, 404)

    def test_payroll_cost_export_emits_audit_entry(self):
        employee = make_employee('E-2', 'Ada', 'Lovelace')
        give_compensation(employee, base_salary='1500.00')
        officer = user_with_role('officer@example.com', PAYROLL_OFFICER)
        run = PayrollRun.objects.create(period_start='2026-01-01', period_end='2026-01-31', initiated_by=officer)
        calculate_run(run)

        self.client.force_authenticate(officer)
        self.client.post('/api/reports/payroll-cost/export/')

        self.assertTrue(AuditLog.objects.filter(category=AuditLog.CATEGORY_PAYROLL_ACTION, action='report_export.payroll_cost').exists())

    def test_headcount_export_does_not_emit_audit_entry(self):
        """§4.15's note: only the export touching payroll cost emits an
        audit entry, not the other four report types."""
        self.client.force_authenticate(user_with_role('hr@example.com', HR_ADMINISTRATOR))

        self.client.post('/api/reports/headcount/export/')

        self.assertFalse(AuditLog.objects.filter(action__startswith='report_export').exists())

    def test_executive_export_completes_with_aggregate_scope(self):
        self.client.force_authenticate(user_with_role('exec@example.com', EXECUTIVE))

        create = self.client.post('/api/reports/headcount/export/')
        job_id = create.data['id']
        poll = self.client.get(f'/api/report-exports/{job_id}/')

        self.assertEqual(poll.data['status'], ReportExport.STATUS_COMPLETE)

    def test_rerunning_export_reuses_same_object_key(self):
        """A retried task must overwrite the same storage object rather
        than orphaning the previous run's file — CodeRabbit's nitpick
        on the first draft, which included a timestamp in the key."""
        from ..models import ReportExport as RE
        from ..tasks import run_report_export

        report_export = RE.objects.create(
            report_type=RE.REPORT_HEADCOUNT, requested_by=user_with_role('hr2@example.com', HR_ADMINISTRATOR),
        )
        run_report_export(report_export)
        first_key = report_export.object_key

        run_report_export(report_export)

        self.assertEqual(report_export.object_key, first_key)
