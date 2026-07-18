from django.urls import path

from .views import DirectReportsView, ManagerChangeView, ReportingRelationshipListView

urlpatterns = [
    path('reporting-relationships/', ReportingRelationshipListView.as_view(), name='reporting-relationships'),
    path('employees/<int:pk>/direct-reports/', DirectReportsView.as_view(), name='employee-direct-reports'),
    path('employees/<int:pk>/manager/', ManagerChangeView.as_view(), name='employee-manager-change'),
]
