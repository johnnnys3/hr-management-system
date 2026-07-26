from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog

from .models import PayrollRun, Payslip, StatutoryRateTable
from .permissions import CanAccessPayslips, CanViewPayrollRuns, IsPayrollOfficer, _payroll_officer, can_decide_payroll_run
from .serializers import (
    BankTransferFileSerializer,
    PayrollRunCreateSerializer,
    PayrollRunSerializer,
    PayslipSerializer,
    StatutoryRateTableSerializer,
)
from .storage import signed_download_url
from .tasks import calculate_run_task, finalize_run_task


class StatutoryRateTableListView(APIView):
    """`GET /api/statutory-rates/`, `docs/06-api-contracts.md` §4.14."""

    permission_classes = [IsPayrollOfficer]

    def get(self, request):
        rates = StatutoryRateTable.objects.order_by('rate_type', '-effective_from')
        return Response(StatutoryRateTableSerializer(rates, many=True).data)


class PayrollRunListCreateView(APIView):
    """`GET, POST /api/payroll-runs/`, `docs/06-api-contracts.md` §4.14.
    Creating a run stays Payroll Officer-only; listing also needs to
    reach whoever holds `approve_payroll_run` (§4.4), or an approver's
    own Payroll page would never show them a run to act on."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsPayrollOfficer()]
        return [CanViewPayrollRuns()]

    def get(self, request):
        queryset = PayrollRun.objects.order_by('-period_start')
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        period_start = request.query_params.get('period_start')
        if period_start:
            queryset = queryset.filter(period_start__gte=period_start)
        period_end = request.query_params.get('period_end')
        if period_end:
            queryset = queryset.filter(period_end__lte=period_end)
        return Response(PayrollRunSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = PayrollRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                if PayrollRun.objects.filter(
                    period_start=serializer.validated_data['period_start'],
                    period_end=serializer.validated_data['period_end'],
                ).exists():
                    return Response({'detail': 'a payroll run already exists for this period.'}, status=status.HTTP_409_CONFLICT)
                payroll_run = serializer.save(initiated_by=request.user)
                audit.services.record(
                    category=AuditLog.CATEGORY_RECORD_CHANGE,
                    action='payroll_run_created',
                    actor=request.user,
                    target_type='payroll_run',
                    target_id=payroll_run.pk,
                )
        except IntegrityError as e:
            if 'payroll_run_unique_period' in str(e):
                return Response({'detail': 'a payroll run already exists for this period.'}, status=status.HTTP_409_CONFLICT)
            raise
        return Response(PayrollRunSerializer(payroll_run).data, status=status.HTTP_201_CREATED)


class PayrollRunDetailView(APIView):
    """`GET /api/payroll-runs/{id}/`, `docs/06-api-contracts.md` §4.14 —
    the status-polling target for every async action below, including
    the approver's own poll after calling approve/finalize."""

    permission_classes = [CanViewPayrollRuns]

    def get(self, request, pk):
        payroll_run = get_object_or_404(PayrollRun, pk=pk)
        return Response(PayrollRunSerializer(payroll_run).data)


class PayrollRunCalculateView(APIView):
    """`POST /api/payroll-runs/{id}/calculate/`, `docs/06-api-contracts.md`
    §4.14. Async: `202`, poll `GET .../{id}/` for `status`. Only callable
    from `draft`, `calculated`, or `failed` — `calculate_run` is
    idempotent by design (a retry safely rebuilds this run's payslips),
    but that idempotency must not extend to a run already
    `pending_approval` or beyond: recalculating there would silently
    rewrite payslips an approver has already signed off, or that are
    already finalized."""

    permission_classes = [IsPayrollOfficer]
    CALCULABLE_STATUSES = {PayrollRun.STATUS_DRAFT, PayrollRun.STATUS_CALCULATED, PayrollRun.STATUS_FAILED}

    def post(self, request, pk):
        payroll_run = get_object_or_404(PayrollRun, pk=pk)
        if payroll_run.status not in self.CALCULABLE_STATUSES:
            return Response(
                {'detail': f'payroll run cannot be calculated from status {payroll_run.status!r}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        calculate_run_task.delay(payroll_run.pk)
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='payroll_run_calculate_requested',
            actor=request.user,
            target_type='payroll_run',
            target_id=payroll_run.pk,
        )
        return Response({'id': payroll_run.pk}, status=status.HTTP_202_ACCEPTED)


class PayrollRunSubmitForApprovalView(APIView):
    """`POST /api/payroll-runs/{id}/submit-for-approval/`."""

    permission_classes = [IsPayrollOfficer]

    def post(self, request, pk):
        with transaction.atomic():
            payroll_run = get_object_or_404(PayrollRun.objects.select_for_update(), pk=pk)
            if payroll_run.status != PayrollRun.STATUS_CALCULATED:
                return Response(
                    {'detail': f'payroll run cannot be submitted for approval from status {payroll_run.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payroll_run.status = PayrollRun.STATUS_PENDING_APPROVAL
            payroll_run.save(update_fields=['status'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='payroll_run_submitted_for_approval',
                actor=request.user,
                target_type='payroll_run',
                target_id=payroll_run.pk,
            )
        return Response(PayrollRunSerializer(payroll_run).data)


class PayrollRunApproveView(APIView):
    """`POST /api/payroll-runs/{id}/approve/`, `docs/06-api-contracts.md`
    §4.14. HRMS-BR-008: rejected `403` with `code:
    "self_approval_forbidden"` where the caller initiated the run —
    checked first, before the general permission and status checks,
    since it is the more fundamental control and api-contracts asks
    for a distinguishable code on this specific rejection."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            payroll_run = get_object_or_404(PayrollRun.objects.select_for_update(), pk=pk)
            if request.user.pk == payroll_run.initiated_by_id:
                return Response(
                    {'code': 'self_approval_forbidden', 'detail': 'the initiator of a payroll run cannot approve it.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not can_decide_payroll_run(request.user, payroll_run):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if payroll_run.status != PayrollRun.STATUS_PENDING_APPROVAL:
                return Response(
                    {'detail': f'payroll run cannot be approved from status {payroll_run.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payroll_run.status = PayrollRun.STATUS_APPROVED
            payroll_run.approved_by = request.user
            payroll_run.approved_at = timezone.now()
            payroll_run.save(update_fields=['status', 'approved_by', 'approved_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='payroll_run_approved',
                actor=request.user,
                target_type='payroll_run',
                target_id=payroll_run.pk,
            )
        return Response(PayrollRunSerializer(payroll_run).data)


class PayrollRunFinalizeView(APIView):
    """`POST /api/payroll-runs/{id}/finalize/`. Same approver rule as
    `approve/`, and only callable once `status = 'approved'`. Async:
    `202`, same poll target."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        payroll_run = get_object_or_404(PayrollRun, pk=pk)
        if request.user.pk == payroll_run.initiated_by_id:
            return Response(
                {'code': 'self_approval_forbidden', 'detail': 'the initiator of a payroll run cannot finalize it.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not can_decide_payroll_run(request.user, payroll_run):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if payroll_run.status != PayrollRun.STATUS_APPROVED:
            return Response(
                {'detail': f'payroll run cannot be finalized from status {payroll_run.status!r}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finalize_run_task.delay(payroll_run.pk)
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='payroll_run_finalize_requested',
            actor=request.user,
            target_type='payroll_run',
            target_id=payroll_run.pk,
        )
        return Response({'id': payroll_run.pk}, status=status.HTTP_202_ACCEPTED)


class PayrollRunBankTransferFileView(APIView):
    """`GET /api/payroll-runs/{id}/bank-transfer-file/`. `404` before
    finalisation — the file does not exist until then."""

    permission_classes = [IsPayrollOfficer]

    def get(self, request, pk):
        payroll_run = get_object_or_404(PayrollRun, pk=pk)
        if not hasattr(payroll_run, 'bank_transfer_file'):
            raise Http404
        return Response({
            **BankTransferFileSerializer(payroll_run.bank_transfer_file).data,
            'url': signed_download_url(payroll_run.bank_transfer_file.object_key),
        })


class PayslipListView(APIView):
    """`GET /api/payslips/`, `docs/06-api-contracts.md` §4.14. Employee:
    own only. Payroll Officer: all."""

    permission_classes = [CanAccessPayslips]

    def get(self, request):
        queryset = Payslip.objects.select_related('payroll_run').prefetch_related('lines').order_by('-generated_at')
        if not _payroll_officer(request.user):
            queryset = queryset.filter(employee_id=request.user.employee_id)
        return Response(PayslipSerializer(queryset, many=True).data)


class PayslipDetailView(APIView):
    """`GET /api/payslips/{id}/`. Same visibility as the list."""

    permission_classes = [CanAccessPayslips]

    def get(self, request, pk):
        payslip = get_object_or_404(Payslip.objects.prefetch_related('lines'), pk=pk)
        self.check_object_permissions(request, payslip)
        return Response(PayslipSerializer(payslip).data)


class PayslipDownloadView(APIView):
    """`GET /api/payslips/{id}/download/`, `docs/06-api-contracts.md`
    §4.14. Returns a short-lived signed URL, never the file bytes
    (ADR-0007), same shape as `EmployeeDocumentDownloadView`. `404`
    before the owning run is finalized — the PDF does not exist until
    then (`payroll.services.generate_payslip_pdf` runs in
    `finalize_run`)."""

    permission_classes = [CanAccessPayslips]

    def get(self, request, pk):
        payslip = get_object_or_404(Payslip, pk=pk)
        self.check_object_permissions(request, payslip)
        if not payslip.object_key:
            raise Http404
        return Response({'url': signed_download_url(payslip.object_key)})
