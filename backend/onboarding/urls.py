from django.urls import path

from .views import (
    ConvertView,
    OnboardingChecklistDetailView,
    OnboardingTaskDetailView,
    OnboardingTaskListCreateView,
)

urlpatterns = [
    path('onboarding/convert/', ConvertView.as_view(), name='onboarding-convert'),
    path('onboarding-checklists/<int:pk>/', OnboardingChecklistDetailView.as_view(), name='onboarding-checklist-detail'),
    path('onboarding-checklists/<int:pk>/tasks/', OnboardingTaskListCreateView.as_view(), name='onboarding-tasks'),
    path(
        'onboarding-checklists/<int:pk>/tasks/<int:task_id>/',
        OnboardingTaskDetailView.as_view(),
        name='onboarding-task-detail',
    ),
]
