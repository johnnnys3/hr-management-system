from django.urls import path

from .views import AuditLogListView, EmployeeAuditHistoryView

urlpatterns = [
    path('audit-log/', AuditLogListView.as_view(), name='audit-log-list'),
    path('employees/<int:pk>/audit-history/', EmployeeAuditHistoryView.as_view(), name='employee-audit-history'),
]
