from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
import notifications.services
from audit.models import AuditLog
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, is_employee, is_manager
from notifications.models import Notification
from reporting_structure.models import ReportingRelationship

from .models import LeaveBalance, LeaveRequest, LeaveType
from .permissions import (
    CanAccessLeaveBalances,
    CanAccessLeaveCalendar,
    CanAccessLeaveRequests,
    CanAccessLeaveTypes,
    CanCancelLeaveRequest,
    CanCorrectLeaveRequest,
    CanDecideLeaveRequest,
)
from .serializers import (
    LeaveBalanceSerializer,
    LeaveRequestCorrectionSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestSerializer,
    LeaveTypeSerializer,
)


class LeaveTypeListView(APIView):
    """`GET /api/leave-types/`, `docs/06-api-contracts.md` §4.12."""

    permission_classes = [CanAccessLeaveTypes]

    def get(self, request):
        return Response(LeaveTypeSerializer(LeaveType.objects.order_by('name'), many=True).data)


def _visible_leave_queryset(user, queryset, employee_field='employee_id'):
    """Row-level scope for leave requests/balances, `docs/07-iam-rbac.md`
    §5: HR sees all, Manager sees direct reports', Employee sees own."""
    if user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists():
        return queryset
    if is_manager(user):
        report_ids = ReportingRelationship.objects.filter(manager_employee_id=user.employee_id).values('employee_id')
        return queryset.filter(**{f'{employee_field}__in': report_ids})
    if is_employee(user):
        return queryset.filter(**{employee_field: user.employee_id})
    return queryset.none()


class LeaveBalanceListView(APIView):
    """`GET /api/leave-balances/`, `docs/06-api-contracts.md` §4.12."""

    permission_classes = [CanAccessLeaveBalances]

    def get(self, request):
        queryset = _visible_leave_queryset(request.user, LeaveBalance.objects.order_by('employee_id', 'leave_type_id'))
        return Response(LeaveBalanceSerializer(queryset, many=True).data)


class LeaveRequestListCreateView(APIView):
    """`GET, POST /api/leave-requests/`, `docs/06-api-contracts.md` §4.12."""

    permission_classes = [CanAccessLeaveRequests]

    def get(self, request):
        queryset = _visible_leave_queryset(request.user, LeaveRequest.objects.order_by('-created_at'))
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        leave_type_id = request.query_params.get('leave_type_id')
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        return Response(LeaveRequestSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            leave_request = serializer.save(employee=request.user.employee)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='leave_request_created',
                actor=request.user,
                target_type='leave_request',
                target_id=leave_request.pk,
            )
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)


class LeaveRequestDetailView(APIView):
    """`PATCH /api/leave-requests/{id}/`, `docs/06-api-contracts.md` §4.12.
    HR Officer correction/cancellation only, never approval."""

    permission_classes = [CanCorrectLeaveRequest]

    def patch(self, request, pk):
        with transaction.atomic():
            leave_request = get_object_or_404(LeaveRequest.objects.select_for_update(), pk=pk)
            if leave_request.status != LeaveRequest.STATUS_PENDING:
                return Response(
                    {'detail': f'leave request cannot be corrected from status {leave_request.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = LeaveRequestCorrectionSerializer(leave_request, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            leave_request = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='leave_request_corrected',
                actor=request.user,
                target_type='leave_request',
                target_id=leave_request.pk,
            )
        return Response(LeaveRequestSerializer(leave_request).data)


def _applicable_balance(leave_request):
    """The `leave_balance` row whose period covers the request's dates, if
    any. `leave_request` carries no FK to `leave_balance` (schema §4.10);
    coverage is found by period, not stored."""
    return LeaveBalance.objects.select_for_update().filter(
        employee_id=leave_request.employee_id,
        leave_type_id=leave_request.leave_type_id,
        period_start__lte=leave_request.start_date,
        period_end__gte=leave_request.end_date,
    ).first()


class LeaveRequestApproveView(APIView):
    """`POST /api/leave-requests/{id}/approve/`, `docs/06-api-contracts.md`
    §4.12. HRMS-BR-010: balance reduces only on approval. HRMS-FR-068:
    a request is not approved beyond the covering balance's remaining days
    — enforced here, at the point the balance actually changes, rather
    than at submission, since `used_days` (and so "available balance")
    only ever reflects approved requests (HRMS-BR-011)."""

    permission_classes = [CanDecideLeaveRequest]

    def post(self, request, pk):
        with transaction.atomic():
            leave_request = get_object_or_404(LeaveRequest.objects.select_for_update(), pk=pk)
            self.check_object_permissions(request, leave_request)
            if leave_request.status != LeaveRequest.STATUS_PENDING:
                return Response(
                    {'detail': f'leave request cannot be approved from status {leave_request.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            balance = _applicable_balance(leave_request)
            duration = (leave_request.end_date - leave_request.start_date).days + 1
            if balance is not None and balance.used_days + duration > balance.entitled_days:
                return Response(
                    {'detail': 'leave request exceeds the available balance for this leave type and period.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            leave_request.status = LeaveRequest.STATUS_APPROVED
            leave_request.approved_by = request.user
            leave_request.decided_at = timezone.now()
            leave_request.save(update_fields=['status', 'approved_by', 'decided_at'])
            if balance is not None:
                balance.used_days = balance.used_days + duration
                balance.save(update_fields=['used_days', 'updated_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='leave_request_approved',
                actor=request.user,
                target_type='leave_request',
                target_id=leave_request.pk,
            )
            recipient = getattr(leave_request.employee, 'user_account', None)
            if recipient is not None:
                notifications.services.send(
                    recipient=recipient,
                    category=Notification.CATEGORY_REQUEST_UPDATE,
                    channel=Notification.CHANNEL_IN_APP,
                    subject='Leave request approved',
                    body=f'Your leave request #{leave_request.pk} has been approved.',
                    related_type='leave_request',
                    related_id=leave_request.pk,
                )
        return Response(LeaveRequestSerializer(leave_request).data)


class LeaveRequestRejectView(APIView):
    """`POST /api/leave-requests/{id}/reject/`, `docs/06-api-contracts.md`
    §4.12. HRMS-BR-011: balance is not decremented."""

    permission_classes = [CanDecideLeaveRequest]

    def post(self, request, pk):
        with transaction.atomic():
            leave_request = get_object_or_404(LeaveRequest.objects.select_for_update(), pk=pk)
            self.check_object_permissions(request, leave_request)
            if leave_request.status != LeaveRequest.STATUS_PENDING:
                return Response(
                    {'detail': f'leave request cannot be rejected from status {leave_request.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            leave_request.status = LeaveRequest.STATUS_REJECTED
            leave_request.approved_by = request.user
            leave_request.decided_at = timezone.now()
            leave_request.save(update_fields=['status', 'approved_by', 'decided_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='leave_request_rejected',
                actor=request.user,
                target_type='leave_request',
                target_id=leave_request.pk,
            )
            recipient = getattr(leave_request.employee, 'user_account', None)
            if recipient is not None:
                notifications.services.send(
                    recipient=recipient,
                    category=Notification.CATEGORY_REQUEST_UPDATE,
                    channel=Notification.CHANNEL_IN_APP,
                    subject='Leave request rejected',
                    body=f'Your leave request #{leave_request.pk} has been rejected.',
                    related_type='leave_request',
                    related_id=leave_request.pk,
                )
        return Response(LeaveRequestSerializer(leave_request).data)


class LeaveRequestCancelView(APIView):
    """`POST /api/leave-requests/{id}/cancel/`, `docs/06-api-contracts.md`
    §4.12. Employee, own pending request only."""

    permission_classes = [CanCancelLeaveRequest]

    def post(self, request, pk):
        with transaction.atomic():
            leave_request = get_object_or_404(LeaveRequest.objects.select_for_update(), pk=pk)
            self.check_object_permissions(request, leave_request)
            if leave_request.status != LeaveRequest.STATUS_PENDING:
                return Response(
                    {'detail': f'leave request cannot be cancelled from status {leave_request.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            leave_request.status = LeaveRequest.STATUS_CANCELLED
            leave_request.save(update_fields=['status'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='leave_request_cancelled',
                actor=request.user,
                target_type='leave_request',
                target_id=leave_request.pk,
            )
        return Response(LeaveRequestSerializer(leave_request).data)


class LeaveCalendarView(APIView):
    """`GET /api/leave-calendar/`, `docs/06-api-contracts.md` §4.12.
    HRMS-FR-071. Read-only composite over `leave_request` where
    `status = 'approved'`, not a separate table."""

    permission_classes = [CanAccessLeaveCalendar]

    def get(self, request):
        queryset = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_APPROVED).order_by('start_date')
        if not request.user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists():
            report_ids = ReportingRelationship.objects.filter(
                manager_employee_id=request.user.employee_id
            ).values('employee_id')
            queryset = queryset.filter(employee_id__in=report_ids)
        return Response(LeaveRequestSerializer(queryset, many=True).data)
