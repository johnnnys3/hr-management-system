from django.urls import path

from .views import (
    HeadcountReportView,
    LeaveUtilizationReportView,
    PayrollCostReportView,
    PayrollSummaryReportView,
    ReportExportCreateView,
    ReportExportDetailView,
    TurnoverReportView,
)

urlpatterns = [
    path('reports/headcount/', HeadcountReportView.as_view(), name='report-headcount'),
    path('reports/leave-utilization/', LeaveUtilizationReportView.as_view(), name='report-leave-utilization'),
    path('reports/turnover/', TurnoverReportView.as_view(), name='report-turnover'),
    path('reports/payroll-cost/', PayrollCostReportView.as_view(), name='report-payroll-cost'),
    path('reports/payroll-summary/', PayrollSummaryReportView.as_view(), name='report-payroll-summary'),
    path('reports/<str:report>/export/', ReportExportCreateView.as_view(), name='report-export-create'),
    path('report-exports/<int:pk>/', ReportExportDetailView.as_view(), name='report-export-detail'),
]
