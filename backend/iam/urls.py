from django.urls import path

from .views import (
    AssignedRolesListView,
    RoleGrantRequestCreateView,
    RoleGrantRequestDecideView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='iam-users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='iam-user-detail'),
    path('roles/', AssignedRolesListView.as_view(), name='iam-roles'),
    path('role-grant-requests/', RoleGrantRequestCreateView.as_view(), name='iam-role-grant-requests'),
    path('role-grant-requests/<int:pk>/decide/', RoleGrantRequestDecideView.as_view(),
         name='iam-role-grant-request-decide'),
]
