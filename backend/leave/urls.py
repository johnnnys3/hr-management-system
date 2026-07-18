from django.urls import path

from .views import (
    LeaveBalanceListView,
    LeaveCalendarView,
    LeaveRequestApproveView,
    LeaveRequestCancelView,
    LeaveRequestDetailView,
    LeaveRequestListCreateView,
    LeaveRequestRejectView,
    LeaveTypeListView,
)

urlpatterns = [
    path('leave-types/', LeaveTypeListView.as_view(), name='leave-types'),
    path('leave-balances/', LeaveBalanceListView.as_view(), name='leave-balances'),
    path('leave-requests/', LeaveRequestListCreateView.as_view(), name='leave-requests'),
    path('leave-requests/<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-request-detail'),
    path('leave-requests/<int:pk>/approve/', LeaveRequestApproveView.as_view(), name='leave-request-approve'),
    path('leave-requests/<int:pk>/reject/', LeaveRequestRejectView.as_view(), name='leave-request-reject'),
    path('leave-requests/<int:pk>/cancel/', LeaveRequestCancelView.as_view(), name='leave-request-cancel'),
    path('leave-calendar/', LeaveCalendarView.as_view(), name='leave-calendar'),
]
