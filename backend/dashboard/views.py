from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from iam.roles import EXECUTIVE, is_employee, is_manager
from leave.models import LeaveBalance, LeaveRequest
from leave.serializers import LeaveBalanceSerializer
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from reporting_structure.models import ReportingRelationship
from reports.services import headcount_report, leave_utilization_report, payroll_cost_report, payroll_summary_report, turnover_report

TURNOVER_WINDOW_DAYS = 365


class DashboardView(APIView):
    """`GET /api/dashboard/`, `docs/06-api-contracts.md` §4.10. A read-only
    composite over modules 6, 10, 13, 17 — every section below reuses the
    source module's own visibility rule rather than deciding access itself."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.groups.filter(name=EXECUTIVE).exists():
            # `docs/07-iam-rbac.md` §4.3: "Executive is read-only and
            # aggregate ... never an individual employee record." Checked
            # first and returned alone, so an Executive who also happens to
            # hold an employee/manager record never gets the individual
            # sections below alongside it.
            #
            # Reused directly from Reports (module 17) with scope='aggregate'
            # — the same scope `reports.permissions.report_scope`/
            # `payroll_report_scope` resolve to for Executive — rather than
            # going through `/api/reports/*` a second time. Turnover has no
            # caller-supplied period here (Dashboard takes no query params),
            # so it defaults to the trailing 365 days, a standard annual
            # turnover window.
            today = timezone.now().date()
            turnover_period_start = today - timedelta(days=TURNOVER_WINDOW_DAYS)
            return Response({'aggregates': {
                'headcount': headcount_report('aggregate', user)['aggregate'],
                'leave_utilization': leave_utilization_report('aggregate', user)['aggregate'],
                'turnover': turnover_report('aggregate', user, None, turnover_period_start, today)['aggregate'],
                'payroll_cost': payroll_cost_report('aggregate')['aggregate'],
                'payroll_summary': payroll_summary_report('aggregate')['aggregate'],
            }})

        data = {}

        if is_employee(user):
            data['leave_balance'] = LeaveBalanceSerializer(
                LeaveBalance.objects.filter(employee_id=user.employee_id).order_by('leave_type_id', 'period_start'),
                many=True,
            ).data
            data['pending_tasks'] = NotificationSerializer(
                Notification.objects.filter(
                    recipient=user, category=Notification.CATEGORY_PENDING_TASK, read_at__isnull=True,
                ),
                many=True,
            ).data

        if is_manager(user):
            report_ids = ReportingRelationship.objects.filter(manager_employee_id=user.employee_id).values('employee_id')
            data['team'] = {
                'pending_leave_requests': LeaveRequest.objects.filter(
                    employee_id__in=report_ids, status=LeaveRequest.STATUS_PENDING,
                ).count(),
            }

        return Response(data)
