from django.urls import path

from .views import DepartmentDetailView, DepartmentListCreateView, JobTitleDetailView, JobTitleListCreateView

urlpatterns = [
    path('departments/', DepartmentListCreateView.as_view(), name='departments'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('job-titles/', JobTitleListCreateView.as_view(), name='job-titles'),
    path('job-titles/<int:pk>/', JobTitleDetailView.as_view(), name='job-title-detail'),
]
