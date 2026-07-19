from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from iam.roles import EXECUTIVE, is_employee, is_manager
from leave.models import LeaveBalance, LeaveRequest
from leave.serializers import LeaveBalanceSerializer
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from reporting_structure.models import ReportingRelationship


class DashboardView(APIView):
    """`GET /api/dashboard/`, `docs/06-api-contracts.md` §4.10. A read-only
    composite over modules 6, 10, 13 (and, for Executive, module 17 once
    built) — every section below reuses the source module's own visibility
    rule rather than deciding access itself."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
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

        if user.groups.filter(name=EXECUTIVE).exists():
            # Aggregate figures belong to Reports (module 17), not yet
            # built — `docs/06-api-contracts.md` §4.10's note. Empty rather
            # than omitted, so an Executive can distinguish "no data yet"
            # from "this section doesn't apply to my role."
            data['aggregates'] = None

        return Response(data)
