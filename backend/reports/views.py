from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReportExport
from .permissions import CanAccessOrgReports, CanAccessPayrollReports, payroll_report_scope, report_scope
from .serializers import ReportExportCreateSerializer, ReportExportSerializer
from .services import (
    headcount_report,
    leave_utilization_report,
    payroll_cost_report,
    payroll_summary_report,
    turnover_report,
)
from .tasks import run_report_export_task

# Maps the contract's hyphenated URL slugs (`docs/06-api-contracts.md`
# §4.15) to `report_export.report_type`'s underscored values
# (`docs/05-database-schema.md` §4.13's own note on this mapping).
ORG_REPORT_SLUGS = {'headcount': 'headcount', 'leave-utilization': 'leave_utilization', 'turnover': 'turnover'}
PAYROLL_REPORT_SLUGS = {'payroll-cost': 'payroll_cost', 'payroll-summary': 'payroll_summary'}
ALL_REPORT_SLUGS = {**ORG_REPORT_SLUGS, **PAYROLL_REPORT_SLUGS}


class HeadcountReportView(APIView):
    permission_classes = [CanAccessOrgReports]

    def get(self, request):
        scope = report_scope(request.user)
        data = headcount_report(
            scope, request.user,
            department_id=request.query_params.get('department_id'),
            employment_status=request.query_params.get('employment_status'),
        )
        return Response(data)


class LeaveUtilizationReportView(APIView):
    permission_classes = [CanAccessOrgReports]

    def get(self, request):
        scope = report_scope(request.user)
        data = leave_utilization_report(
            scope, request.user,
            department_id=request.query_params.get('department_id'),
            leave_type_id=request.query_params.get('leave_type_id'),
            period_start=request.query_params.get('period_start'),
            period_end=request.query_params.get('period_end'),
        )
        return Response(data)


class TurnoverReportView(APIView):
    permission_classes = [CanAccessOrgReports]

    def get(self, request):
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        if not period_start or not period_end:
            raise ValidationError('period_start and period_end are required for the turnover report.')
        scope = report_scope(request.user)
        data = turnover_report(
            scope, request.user,
            department_id=request.query_params.get('department_id'),
            period_start=period_start,
            period_end=period_end,
        )
        return Response(data)


class PayrollCostReportView(APIView):
    permission_classes = [CanAccessPayrollReports]

    def get(self, request):
        scope = payroll_report_scope(request.user)
        data = payroll_cost_report(
            scope,
            payroll_run_id=request.query_params.get('payroll_run_id'),
            period_start=request.query_params.get('period_start'),
            period_end=request.query_params.get('period_end'),
        )
        return Response(data)


class PayrollSummaryReportView(APIView):
    permission_classes = [CanAccessPayrollReports]

    def get(self, request):
        scope = payroll_report_scope(request.user)
        data = payroll_summary_report(
            scope,
            payroll_run_id=request.query_params.get('payroll_run_id'),
            period_start=request.query_params.get('period_start'),
            period_end=request.query_params.get('period_end'),
        )
        return Response(data)


class ReportExportCreateView(APIView):
    """`POST /api/reports/{report}/export/`, `docs/06-api-contracts.md`
    §4.15: same permission as the corresponding report endpoint."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        report_type = ALL_REPORT_SLUGS.get(self.kwargs.get('report'))
        if report_type in PAYROLL_REPORT_SLUGS.values():
            return [CanAccessPayrollReports()]
        return [CanAccessOrgReports()]

    def post(self, request, report):
        report_type = ALL_REPORT_SLUGS.get(report)
        if report_type is None:
            raise Http404
        serializer = ReportExportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_export = ReportExport.objects.create(
            report_type=report_type,
            params=serializer.validated_data.get('params', {}),
            requested_by=request.user,
        )
        run_report_export_task.delay(report_export.pk)
        return Response(ReportExportSerializer(report_export).data, status=202)


class ReportExportDetailView(RetrieveAPIView):
    """`GET /api/report-exports/{job_id}/` — own job only."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReportExportSerializer

    def get_queryset(self):
        return ReportExport.objects.filter(requested_by=self.request.user)
