"""`docs/06-api-contracts.md` §4.14: payroll-runs lifecycle
(create -> calculate -> submit-for-approval -> approve -> finalize)."""
from django.contrib.auth.models import Permission
from django.test import override_settings
from rest_framework.test import APITestCase

from iam.roles import PAYROLL_OFFICER

from ..models import BankTransferFile, PayrollRun
from .helpers import give_compensation, make_employee, user_with_role


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class PayrollRunLifecycleTests(APITestCase):
    def setUp(self):
        self.officer = user_with_role('officer@example.com', PAYROLL_OFFICER)
        self.client.force_authenticate(self.officer)
        employee = make_employee('E-1', 'Grace', 'Hopper')
        give_compensation(employee, base_salary='2000.00')

    def _approver(self):
        approver = user_with_role('approver@example.com', PAYROLL_OFFICER)
        approver.user_permissions.add(Permission.objects.get(codename='approve_payroll_run'))
        return approver

    def test_create_run(self):
        response = self.client.post('/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'draft')
        self.assertEqual(response.data['initiated_by'], self.officer.pk)

    def test_duplicate_period_is_conflict(self):
        self.client.post('/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'})

        response = self.client.post('/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'})

        self.assertEqual(response.status_code, 409)

    def test_hr_officer_is_denied(self):
        from iam.roles import HR_OFFICER
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get('/api/payroll-runs/')

        self.assertEqual(response.status_code, 403)

    def test_full_lifecycle_to_finalized(self):
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']

        calculate = self.client.post(f'/api/payroll-runs/{run_id}/calculate/')
        self.assertEqual(calculate.status_code, 202)
        self.assertEqual(self.client.get(f'/api/payroll-runs/{run_id}/').data['status'], 'calculated')

        submit = self.client.post(f'/api/payroll-runs/{run_id}/submit-for-approval/')
        self.assertEqual(submit.status_code, 200)
        self.assertEqual(submit.data['status'], 'pending_approval')

        approver = self._approver()
        self.client.force_authenticate(approver)
        approve = self.client.post(f'/api/payroll-runs/{run_id}/approve/')
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(approve.data['status'], 'approved')
        self.assertEqual(approve.data['approved_by'], approver.pk)

        finalize = self.client.post(f'/api/payroll-runs/{run_id}/finalize/')
        self.assertEqual(finalize.status_code, 202)
        detail = self.client.get(f'/api/payroll-runs/{run_id}/').data
        self.assertEqual(detail['status'], 'finalized')
        self.assertIsNotNone(detail['finalized_at'])
        self.assertTrue(BankTransferFile.objects.filter(payroll_run_id=run_id).exists())

        bank_file = self.client.get(f'/api/payroll-runs/{run_id}/bank-transfer-file/')
        self.assertEqual(bank_file.status_code, 200)
        self.assertIn('url', bank_file.data)

        from ..models import Payslip
        payslip = Payslip.objects.get(payroll_run_id=run_id)
        download = self.client.get(f'/api/payslips/{payslip.pk}/download/')
        self.assertEqual(download.status_code, 200)
        self.assertIn('url', download.data)

    def test_bank_transfer_file_404_before_finalisation(self):
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']

        response = self.client.get(f'/api/payroll-runs/{run_id}/bank-transfer-file/')

        self.assertEqual(response.status_code, 404)

    def test_initiator_cannot_approve_own_run_even_with_permission(self):
        """HRMS-BR-008, IAM §4.4: enforced regardless of any combination
        of roles/permissions the initiator holds."""
        self.officer.user_permissions.add(Permission.objects.get(codename='approve_payroll_run'))
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']
        self.client.post(f'/api/payroll-runs/{run_id}/calculate/')
        self.client.post(f'/api/payroll-runs/{run_id}/submit-for-approval/')

        response = self.client.post(f'/api/payroll-runs/{run_id}/approve/')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'self_approval_forbidden')

    def test_approve_without_permission_is_denied(self):
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']
        self.client.post(f'/api/payroll-runs/{run_id}/calculate/')
        self.client.post(f'/api/payroll-runs/{run_id}/submit-for-approval/')

        other_officer = user_with_role('other@example.com', PAYROLL_OFFICER)
        self.client.force_authenticate(other_officer)
        response = self.client.post(f'/api/payroll-runs/{run_id}/approve/')

        self.assertEqual(response.status_code, 403)

    def test_approve_wrong_status_is_rejected(self):
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']
        approver = self._approver()
        self.client.force_authenticate(approver)

        response = self.client.post(f'/api/payroll-runs/{run_id}/approve/')

        self.assertEqual(response.status_code, 400)

    def test_db_rejects_approver_equal_initiator(self):
        """`payroll_run_approver_not_initiator` is the actual
        enforcement; the API check is defence in depth over it."""
        run = PayrollRun.objects.create(period_start='2026-01-01', period_end='2026-01-31', initiated_by=self.officer)
        run.approved_by = self.officer
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            run.save()

    def test_calculate_is_denied_to_employee(self):
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']
        employee = make_employee('E-2', 'Ada', 'Lovelace')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email='ada@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.post(f'/api/payroll-runs/{run_id}/calculate/')

        self.assertEqual(response.status_code, 403)

    def test_calculate_denied_once_approved(self):
        """Recalculating an approved run would silently rewrite payslips
        an approver already signed off on — `calculate_run`'s
        idempotency (HRMS-NFR-005) covers retrying a stuck/failed
        calculation, not reopening a decided run."""
        run_id = self.client.post(
            '/api/payroll-runs/', {'period_start': '2026-01-01', 'period_end': '2026-01-31'}
        ).data['id']
        self.client.post(f'/api/payroll-runs/{run_id}/calculate/')
        self.client.post(f'/api/payroll-runs/{run_id}/submit-for-approval/')
        approver = self._approver()
        self.client.force_authenticate(approver)
        self.client.post(f'/api/payroll-runs/{run_id}/approve/')
        self.client.force_authenticate(self.officer)

        response = self.client.post(f'/api/payroll-runs/{run_id}/calculate/')

        self.assertEqual(response.status_code, 400)

    def test_anonymous_is_denied(self):
        self.client.force_authenticate(None)

        response = self.client.get('/api/payroll-runs/')

        self.assertEqual(response.status_code, 401)
