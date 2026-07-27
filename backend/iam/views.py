from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import accounts.services
import audit.services
from accounts.models import User
from audit.models import AuditLog

from .models import RoleGrantRequest
from .permissions import CanDecideRoleGrantRequest, IsFullyAuthenticated, IsSystemAdministrator
from .roles import ASSIGNED_ROLES, RECRUITER
from .serializers import (
    RoleGrantRequestCreateSerializer,
    RoleGrantRequestDecisionSerializer,
    RoleGrantRequestSerializer,
    UserAdminSerializer,
)


class UserListCreateView(APIView):
    """`GET, POST /api/users/`, `docs/06-api-contracts.md` §4.9."""

    permission_classes = [IsSystemAdministrator]

    def get(self, request):
        serializer = UserAdminSerializer(User.objects.order_by('id'), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        accounts.services.send_email_verification(user)
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='user_account_created',
            actor=request.user,
            target_type='user_account',
            target_id=user.pk,
        )
        return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """`PATCH /api/users/{id}/`, `docs/06-api-contracts.md` §4.9."""

    permission_classes = [IsSystemAdministrator]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserAdminSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='user_account_updated',
            actor=request.user,
            target_type='user_account',
            target_id=user.pk,
        )
        return Response(UserAdminSerializer(user).data)


class AssignedRolesListView(APIView):
    """`GET /api/roles/`. Lists the six assigned-role groups with their
    database ids, so a client can build a role picker without hardcoding
    group ids. System-Administrator-only, since only System Administrator
    raises role-grant requests
    (`docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`).
    """

    permission_classes = [IsSystemAdministrator]

    def get(self, request):
        groups = Group.objects.filter(name__in=ASSIGNED_ROLES).order_by('name')
        return Response([{'id': g.pk, 'name': g.name} for g in groups])


class RoleGrantRequestCreateView(APIView):
    """`POST /api/role-grant-requests/`, `docs/06-api-contracts.md` §4.9.

    Raising a request is restricted to System Administrator
    (`docs/07-iam-rbac.md` §7.3, amended 2026-07-27) — narrowed from "any
    authenticated user" as part of the Access redesign
    (`docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`).
    `GET` on this same view stays open to any authenticated user, since it
    only ever returns the caller's own requests plus requests awaiting
    their decision — narrowing `POST` doesn't change what `GET` can show.

    The self-grant refusal is enforced by the database `CHECK` constraint;
    this view turns the resulting `IntegrityError`-shaped failure into the
    documented `self_grant_forbidden` response rather than a 500, since a
    self-grant is a routine, expected rejection, not a server fault.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSystemAdministrator()]
        return [IsFullyAuthenticated()]

    def get(self, request):
        """`GET /api/role-grant-requests/`, `docs/06-api-contracts.md` §4.9:
        own requests as requester, plus pending requests awaiting the
        caller's decision (mirrors `CanDecideRoleGrantRequest`'s eligibility
        — holds the permission, is not the requester, and is not the
        `is_superuser` break-glass account, §7.2)."""
        queryset = RoleGrantRequest.objects.filter(requester=request.user)
        if not request.user.is_superuser and request.user.has_perm('iam.approve_role_grant'):
            queryset |= RoleGrantRequest.objects.filter(
                status=RoleGrantRequest.STATUS_PENDING,
            ).exclude(requester=request.user)
        serializer = RoleGrantRequestSerializer(queryset.order_by('-requested_at'), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleGrantRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = serializer.validated_data['subject']
        role = serializer.validated_data['role']

        if subject.pk == request.user.pk:
            return Response(
                {'error': {'code': 'self_grant_forbidden', 'message': 'A user may not request a role grant for themselves.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            grant_request = RoleGrantRequest.objects.create(requester=request.user, subject=subject, role=role)
            audit.services.record(
                category=AuditLog.CATEGORY_PERMISSION_CHANGE,
                action='role_grant_requested',
                actor=request.user,
                target_type='user_account',
                target_id=subject.pk,
                detail={'role': role.name},
            )

            if role.name == RECRUITER:
                # `docs/07-iam-rbac.md` §7.3: the approval constraint
                # applies to the five privileged roles. Recruiter is the
                # one assigned role outside that set, and its grant takes
                # effect immediately — a request no one is required to
                # decide would otherwise sit pending forever. Matched
                # explicitly against `RECRUITER` rather than "not
                # privileged" — `role_name` is already constrained to the
                # six assigned-role groups by the serializer, but an
                # explicit allow-list here means a future role added to
                # `ASSIGNED_ROLES` without an explicit privileged/
                # non-privileged classification fails closed (stays
                # pending) rather than auto-granting by omission.
                grant_request.status = RoleGrantRequest.STATUS_APPROVED
                grant_request.decided_at = timezone.now()
                grant_request.save(update_fields=['status', 'decided_at'])
                subject.groups.add(role)
                audit.services.record(
                    category=AuditLog.CATEGORY_PERMISSION_CHANGE,
                    action='role_grant_approved',
                    actor=request.user,
                    target_type='user_account',
                    target_id=subject.pk,
                    detail={'role': role.name},
                )

        return Response(RoleGrantRequestSerializer(grant_request).data, status=status.HTTP_201_CREATED)


class RoleGrantRequestDecideView(APIView):
    """`POST /api/role-grant-requests/{id}/decide/`, `docs/06-api-contracts.md` §4.9.

    Only privileged-role requests (§7.3's five roles) require this decision
    to take effect; the group membership is granted immediately on
    approval, since a pending request that is never applied satisfies no
    requirement.
    """

    permission_classes = [IsFullyAuthenticated, CanDecideRoleGrantRequest]

    def post(self, request, pk):
        serializer = RoleGrantRequestDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.validated_data['decision']

        with transaction.atomic():
            grant_request = get_object_or_404(
                RoleGrantRequest.objects.select_for_update(), pk=pk
            )
            self.check_object_permissions(request, grant_request)

            if grant_request.status != RoleGrantRequest.STATUS_PENDING:
                return Response(
                    {'error': {'code': 'conflict', 'message': 'This request has already been decided.'}},
                    status=status.HTTP_409_CONFLICT,
                )

            grant_request.status = decision
            grant_request.decided_at = timezone.now()
            grant_request.approver = request.user
            grant_request.save(update_fields=['status', 'decided_at', 'approver'])

            if decision == RoleGrantRequest.STATUS_APPROVED:
                grant_request.subject.groups.add(grant_request.role)

            audit.services.record(
                category=AuditLog.CATEGORY_PERMISSION_CHANGE,
                action=f'role_grant_{decision}',
                actor=request.user,
                target_type='user_account',
                target_id=grant_request.subject_id,
                detail={'role': grant_request.role.name},
            )
        return Response(RoleGrantRequestSerializer(grant_request).data)
