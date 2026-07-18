"""`GET /api/leave-balances/`, `docs/06-api-contracts.md` §4.12."""
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_OFFICER

from ..models import LeaveBalance
from .helpers import annual_leave_type, make_employee, make_manager_and_report, user_with_role

User = get_user_model()

URL = '/api/leave-balances/'


class LeaveBalanceVisibilityTests(APITestCase):
    def setUp(self):
        self.manager, self.report = make_manager_and_report()
        self.manager_user = User.objects.create_user(email='ada@example.com', password='x', employee=self.manager)
        self.report_user = User.objects.create_user(email='grace@example.com', password='x', employee=self.report)
        self.other_employee = make_employee('E-3', 'Alan', 'Turing')
        self.other_user = User.objects.create_user(email='alan@example.com', password='x', employee=self.other_employee)

        self.report_balance = LeaveBalance.objects.create(
            employee=self.report, leave_type=annual_leave_type(),
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
        )
        self.other_balance = LeaveBalance.objects.create(
            employee=self.other_employee, leave_type=annual_leave_type(),
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
        )

    def test_employee_sees_only_own_balance(self):
        self.client.force_authenticate(self.report_user)

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_balance.pk})

    def test_manager_sees_direct_reports_balances(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_balance.pk})

    def test_hr_officer_sees_all_balances(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get(URL)

        ids = {row['id'] for row in response.data}
        self.assertEqual(ids, {self.report_balance.pk, self.other_balance.pk})

    def test_anonymous_is_denied(self):
        response = self.client.get(URL)

        self.assertEqual(response.status_code, 401)
