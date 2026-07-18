"""`/api/leave-requests/`, `docs/06-api-contracts.md` §4.12."""
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from audit.models import AuditLog
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

from ..models import LeaveBalance, LeaveRequest
from .helpers import annual_leave_type, make_employee, make_manager_and_report, user_with_role

User = get_user_model()

LIST_URL = '/api/leave-requests/'


def detail_url(pk):
    return f'/api/leave-requests/{pk}/'


def approve_url(pk):
    return f'/api/leave-requests/{pk}/approve/'


def reject_url(pk):
    return f'/api/leave-requests/{pk}/reject/'


def cancel_url(pk):
    return f'/api/leave-requests/{pk}/cancel/'


class LeaveRequestCreateTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)

    def test_employee_can_submit_own_leave_request(self):
        self.client.force_authenticate(self.employee_user)

        response = self.client.post(LIST_URL, {
            'leave_type': annual_leave_type().pk,
            'start_date': '2026-08-10',
            'end_date': '2026-08-14',
            'reason': 'Family trip',
        })

        self.assertEqual(response.status_code, 201)
        leave_request = LeaveRequest.objects.get(pk=response.data['id'])
        self.assertEqual(leave_request.employee_id, self.employee.pk)
        self.assertEqual(leave_request.status, LeaveRequest.STATUS_PENDING)
        self.assertTrue(
            AuditLog.objects.filter(action='leave_request_created', target_id=leave_request.pk).exists()
        )

    def test_employee_id_is_not_client_settable(self):
        """§4.12: `employee_id` is fixed to the caller regardless of body content."""
        other_employee = make_employee('E-2', 'Ada', 'Lovelace')
        self.client.force_authenticate(self.employee_user)

        response = self.client.post(LIST_URL, {
            'employee': other_employee.pk,
            'leave_type': annual_leave_type().pk,
            'start_date': '2026-08-10',
            'end_date': '2026-08-14',
        })

        self.assertEqual(response.status_code, 201)
        leave_request = LeaveRequest.objects.get(pk=response.data['id'])
        self.assertEqual(leave_request.employee_id, self.employee.pk)

    def test_end_date_before_start_date_is_rejected(self):
        self.client.force_authenticate(self.employee_user)

        response = self.client.post(LIST_URL, {
            'leave_type': annual_leave_type().pk,
            'start_date': '2026-08-14',
            'end_date': '2026-08-10',
        })

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_cannot_create_a_leave_request(self):
        """HRMS-FR-063/§4.2: creation is `C, R own` for Employee; HR Officer holds `R, U` only."""
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.post(LIST_URL, {
            'leave_type': annual_leave_type().pk,
            'start_date': '2026-08-10',
            'end_date': '2026-08-14',
        })

        self.assertEqual(response.status_code, 403)


class LeaveRequestListVisibilityTests(APITestCase):
    def setUp(self):
        self.manager, self.report = make_manager_and_report()
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.report_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.other_employee = make_employee('E-3', 'Alan', 'Turing')
        self.other_user = User.objects.create_user(email='alan@example.com', password='x', employee=self.other_employee)
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)

        self.report_request = LeaveRequest.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14),
        )
        self.other_request = LeaveRequest.objects.create(
            employee=self.other_employee, leave_type=annual_leave_type(),
            start_date=date(2026, 9, 1), end_date=date(2026, 9, 3),
        )

    def test_employee_sees_only_own_requests(self):
        self.client.force_authenticate(self.report_user)

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, 200)
        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_request.pk})

    def test_manager_sees_only_direct_reports_requests(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, 200)
        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_request.pk})

    def test_hr_officer_sees_all_requests(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, 200)
        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_request.pk, self.other_request.pk})

    def test_anonymous_is_denied(self):
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, 401)


class LeaveRequestApproveTests(APITestCase):
    def setUp(self):
        self.manager, self.report = make_manager_and_report()
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.report_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.other_manager = make_employee('M-2', 'Alan', 'Turing')
        self.other_manager_user = User.objects.create_user(email='alan@example.com', password='x', employee=self.other_manager)

        self.balance = LeaveBalance.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
        )
        self.leave_request = LeaveRequest.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14),
        )

    def test_direct_manager_can_approve(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(approve_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 200)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_APPROVED)
        self.assertEqual(self.leave_request.approved_by_id, self.manager_user.pk)
        self.assertIsNotNone(self.leave_request.decided_at)

    def test_approval_decrements_the_covering_balance(self):
        """HRMS-BR-010: 5-day request (Aug 10 to Aug 14 inclusive)."""
        self.client.force_authenticate(self.manager_user)

        self.client.post(approve_url(self.leave_request.pk))

        self.balance.refresh_from_db()
        self.assertEqual(self.balance.used_days, 5)

    def test_approval_beyond_balance_is_rejected(self):
        """HRMS-FR-068."""
        self.balance.entitled_days = 3
        self.balance.save(update_fields=['entitled_days'])
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(approve_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 400)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_PENDING)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.used_days, 0)

    def test_non_direct_manager_cannot_approve(self):
        self.client.force_authenticate(self.other_manager_user)

        response = self.client.post(approve_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 403)

    def test_hr_officer_cannot_approve(self):
        """`docs/07-iam-rbac.md` §4.3: leave approval is Manager-only at action level."""
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.post(approve_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 403)

    def test_cannot_approve_a_non_pending_request(self):
        self.leave_request.status = LeaveRequest.STATUS_CANCELLED
        self.leave_request.save(update_fields=['status'])
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(approve_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 400)


class LeaveRequestRejectTests(APITestCase):
    def setUp(self):
        self.manager, self.report = make_manager_and_report()
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.balance = LeaveBalance.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
        )
        self.leave_request = LeaveRequest.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14),
        )

    def test_direct_manager_can_reject_and_balance_is_unchanged(self):
        """HRMS-BR-011."""
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(reject_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 200)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_REJECTED)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.used_days, 0)


class LeaveRequestCancelTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.other_employee = make_employee('E-2', 'Ada', 'Lovelace')
        self.other_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.other_employee)
        self.leave_request = LeaveRequest.objects.create(
            employee=self.employee, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14),
        )

    def test_owner_can_cancel_own_pending_request(self):
        self.client.force_authenticate(self.employee_user)

        response = self.client.post(cancel_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 200)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_CANCELLED)

    def test_other_employee_cannot_cancel(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.post(cancel_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 403)

    def test_cannot_cancel_an_approved_request(self):
        self.leave_request.status = LeaveRequest.STATUS_APPROVED
        self.leave_request.save(update_fields=['status'])
        self.client.force_authenticate(self.employee_user)

        response = self.client.post(cancel_url(self.leave_request.pk))

        self.assertEqual(response.status_code, 400)


class LeaveRequestCorrectionTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)
        self.hr_admin = user_with_role('hra@example.com', HR_ADMINISTRATOR)
        self.leave_request = LeaveRequest.objects.create(
            employee=self.employee, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14), reason='Trip',
        )

    def test_hr_officer_can_correct_reason(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(detail_url(self.leave_request.pk), {'reason': 'Corrected reason'})

        self.assertEqual(response.status_code, 200)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.reason, 'Corrected reason')

    def test_hr_officer_can_cancel_via_correction_endpoint(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(detail_url(self.leave_request.pk), {'status': LeaveRequest.STATUS_CANCELLED})

        self.assertEqual(response.status_code, 200)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_CANCELLED)

    def test_hr_officer_cannot_approve_via_correction_endpoint(self):
        """§4.12: this endpoint's permission class explicitly excludes writing `status` to `'approved'`."""
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(detail_url(self.leave_request.pk), {'status': LeaveRequest.STATUS_APPROVED})

        self.assertEqual(response.status_code, 400)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, LeaveRequest.STATUS_PENDING)

    def test_hr_administrator_cannot_correct(self):
        """§4.12: PATCH is HR Officer only."""
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(detail_url(self.leave_request.pk), {'reason': 'x'})

        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_correct_own_request(self):
        employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(employee_user)

        response = self.client.patch(detail_url(self.leave_request.pk), {'reason': 'x'})

        self.assertEqual(response.status_code, 403)
