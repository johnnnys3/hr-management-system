from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from iam.roles import EXECUTIVE, HR_OFFICER
from leave.models import LeaveBalance, LeaveRequest, LeaveType
from notifications.models import Notification
from reporting_structure.models import ReportingRelationship

from .helpers import make_employee, make_manager_and_report, user_with_role


class DashboardViewTests(APITestCase):
    """`GET /api/dashboard/`, `docs/06-api-contracts.md` §4.10."""

    def setUp(self):
        self.url = reverse('dashboard')
        self.leave_type = LeaveType.objects.get(name='Annual leave')

    def test_unauthenticated_is_rejected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_employee_sees_own_leave_balance_and_pending_tasks(self):
        employee = make_employee('DASH-E-2', 'Alan', 'Turing')
        user = user_with_role('alan@example.com', employee=employee)
        balance = LeaveBalance.objects.create(
            employee=employee, leave_type=self.leave_type,
            period_start=date.today(), period_end=date.today() + timedelta(days=365),
            entitled_days=20,
        )
        pending = Notification.objects.create(
            recipient=user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Complete onboarding task', body='...',
        )
        # A read pending-task and a request-update notification must not appear.
        Notification.objects.create(
            recipient=user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Already read', body='...', read_at=timezone.now(),
        )
        Notification.objects.create(
            recipient=user, category=Notification.CATEGORY_REQUEST_UPDATE, channel=Notification.CHANNEL_IN_APP,
            subject='Leave approved', body='...',
        )

        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['id'] for row in response.data['leave_balance']], [balance.pk])
        self.assertEqual([row['id'] for row in response.data['pending_tasks']], [pending.pk])
        self.assertNotIn('team', response.data)
        self.assertNotIn('aggregates', response.data)

    def test_employee_without_data_sees_empty_lists_not_error(self):
        employee = make_employee('DASH-E-3', 'Barbara', 'Liskov')
        user = user_with_role('barbara@example.com', employee=employee)

        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['leave_balance'], [])
        self.assertEqual(response.data['pending_tasks'], [])

    def test_manager_sees_own_data_plus_team_pending_leave_count(self):
        manager, report = make_manager_and_report()
        manager_user = user_with_role('ada@example.com', employee=manager)
        LeaveRequest.objects.create(
            employee=report, leave_type=self.leave_type,
            start_date=date.today(), end_date=date.today() + timedelta(days=1),
        )
        # Not counted: the report's own approved request.
        LeaveRequest.objects.create(
            employee=report, leave_type=self.leave_type,
            start_date=date.today(), end_date=date.today(), status=LeaveRequest.STATUS_APPROVED,
        )
        # Not counted: another manager's report's pending request.
        other_manager, other_report = make_employee('DASH-M-2', 'Edsger', 'Dijkstra'), make_employee('DASH-E-4', 'Donald', 'Knuth')
        ReportingRelationship.objects.create(employee=other_report, manager_employee=other_manager, effective_from=date.today())
        LeaveRequest.objects.create(
            employee=other_report, leave_type=self.leave_type,
            start_date=date.today(), end_date=date.today(),
        )

        self.client.force_authenticate(manager_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('leave_balance', response.data)
        self.assertIn('pending_tasks', response.data)
        self.assertEqual(response.data['team'], {'pending_leave_requests': 1})
        self.assertNotIn('aggregates', response.data)

    def test_executive_sees_empty_aggregates_and_no_employee_data(self):
        user = user_with_role('exec@example.com', EXECUTIVE)

        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['aggregates'])
        self.assertNotIn('leave_balance', response.data)
        self.assertNotIn('pending_tasks', response.data)
        self.assertNotIn('team', response.data)

    def test_role_with_no_applicable_section_sees_empty_composite(self):
        user = user_with_role('hro@example.com', HR_OFFICER)

        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {})
