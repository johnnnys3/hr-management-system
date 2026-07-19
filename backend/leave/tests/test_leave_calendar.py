"""`GET /api/leave-calendar/`, `docs/06-api-contracts.md` §4.12. HRMS-FR-071."""
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_OFFICER

from ..models import LeaveRequest
from .helpers import annual_leave_type, make_employee, make_manager_and_report, user_with_role

User = get_user_model()

URL = '/api/leave-calendar/'


class LeaveCalendarTests(APITestCase):
    def setUp(self):
        self.manager, self.report = make_manager_and_report()
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.other_employee = make_employee('E-3', 'Alan', 'Turing')

        self.approved_report_request = LeaveRequest.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 10), end_date=date(2026, 8, 14), status=LeaveRequest.STATUS_APPROVED,
        )
        self.pending_report_request = LeaveRequest.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            start_date=date(2026, 9, 1), end_date=date(2026, 9, 2),
        )
        self.approved_other_request = LeaveRequest.objects.create(
            employee=self.other_employee, leave_type=annual_leave_type(),
            start_date=date(2026, 8, 20), end_date=date(2026, 8, 21), status=LeaveRequest.STATUS_APPROVED,
        )

    def test_only_approved_requests_appear(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertNotIn(self.pending_report_request.pk, ids)

    def test_hr_officer_sees_organisation_wide(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.approved_report_request.pk, self.approved_other_request.pk})

    def test_manager_sees_only_direct_reports(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.approved_report_request.pk})

    def test_employee_is_denied(self):
        employee_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.client.force_authenticate(employee_user)

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 403)
