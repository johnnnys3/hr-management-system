from django.urls import path

from .views import (
    EmergencyContactDetailView,
    EmergencyContactListCreateView,
    EmployeeDetailView,
    EmployeeDocumentDownloadView,
    EmployeeDocumentListCreateView,
    EmployeeListCreateView,
    EmployeeMeView,
    EmploymentHistoryListView,
)

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employees'),
    path('employees/me/', EmployeeMeView.as_view(), name='employee-me'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/employment-history/', EmploymentHistoryListView.as_view(), name='employee-employment-history'),
    path('employees/<int:pk>/documents/', EmployeeDocumentListCreateView.as_view(), name='employee-documents'),
    path(
        'employees/<int:pk>/documents/<int:doc_id>/download/',
        EmployeeDocumentDownloadView.as_view(),
        name='employee-document-download',
    ),
    path('employees/<int:pk>/emergency-contacts/', EmergencyContactListCreateView.as_view(), name='employee-emergency-contacts'),
    path(
        'employees/<int:pk>/emergency-contacts/<int:contact_id>/',
        EmergencyContactDetailView.as_view(),
        name='employee-emergency-contact-detail',
    ),
]
