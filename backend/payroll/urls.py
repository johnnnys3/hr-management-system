from django.urls import path

from .views import (
    PayrollRunApproveView,
    PayrollRunBankTransferFileView,
    PayrollRunCalculateView,
    PayrollRunDetailView,
    PayrollRunFinalizeView,
    PayrollRunListCreateView,
    PayrollRunSubmitForApprovalView,
    PayslipDetailView,
    PayslipDownloadView,
    PayslipListView,
    StatutoryRateTableListView,
)

urlpatterns = [
    path('statutory-rates/', StatutoryRateTableListView.as_view(), name='statutory-rates'),
    path('payroll-runs/', PayrollRunListCreateView.as_view(), name='payroll-runs'),
    path('payroll-runs/<int:pk>/', PayrollRunDetailView.as_view(), name='payroll-run-detail'),
    path('payroll-runs/<int:pk>/calculate/', PayrollRunCalculateView.as_view(), name='payroll-run-calculate'),
    path(
        'payroll-runs/<int:pk>/submit-for-approval/',
        PayrollRunSubmitForApprovalView.as_view(),
        name='payroll-run-submit-for-approval',
    ),
    path('payroll-runs/<int:pk>/approve/', PayrollRunApproveView.as_view(), name='payroll-run-approve'),
    path('payroll-runs/<int:pk>/finalize/', PayrollRunFinalizeView.as_view(), name='payroll-run-finalize'),
    path(
        'payroll-runs/<int:pk>/bank-transfer-file/',
        PayrollRunBankTransferFileView.as_view(),
        name='payroll-run-bank-transfer-file',
    ),
    path('payslips/', PayslipListView.as_view(), name='payslips'),
    path('payslips/<int:pk>/', PayslipDetailView.as_view(), name='payslip-detail'),
    path('payslips/<int:pk>/download/', PayslipDownloadView.as_view(), name='payslip-download'),
]
