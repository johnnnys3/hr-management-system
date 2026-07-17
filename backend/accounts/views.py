from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog

from . import services, totp
from .models import SecondFactor, SecondFactorRecoveryRequest, User
from .permissions import CanDecideSecondFactorRecovery
from .serializers import (
    LoginSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SecondFactorEnrollResponseSerializer,
    SecondFactorRecoveryDecisionSerializer,
    SecondFactorRecoveryRequestSerializer,
)


class CsrfBootstrapView(APIView):
    """`GET /api/auth/csrf/`. Not named in `docs/06-api-contracts.md` §4.2.

    DRF delegates CSRF enforcement to `SessionAuthentication.enforce_csrf`
    rather than Django's global middleware (`docs/03-tech-stack.md` §8.1's
    "not to be disabled" still holds — this only relocates the check). That
    check compares a submitted token against the `csrftoken` cookie, and
    the SPA has no way to obtain that cookie before its first state-changing
    call without one endpoint whose only job is to set it. Same category of
    contract gap as the password-reset confirm endpoint above.
    """

    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    """`POST /api/auth/login/`, `docs/06-api-contracts.md` §4.2.

    HRMS-NFR-024 requires second-factor presentation "on every
    authentication" for administrators and payroll users, which the
    contract's login row does not spell out as a second call. Rather than
    add an undocumented endpoint, this view accepts an optional
    `totp_code` on the same request: a credential-valid request from an
    account with an enrolled factor, made without one, is answered with
    `second_factor_required` and establishes no session. A credential-valid
    request from an account with no factor yet (or a disabled one) does
    establish a session and is answered with
    `second_factor_enrollment_required`, since enrolment itself needs one.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        totp_code = serializer.validated_data.get('totp_code', '')

        user = authenticate(request, username=email, password=password)
        if user is None or not user.is_active:
            audit.services.record(
                category=AuditLog.CATEGORY_LOGIN_ATTEMPT,
                action='login_failed',
                detail={'email': email},
            )
            return Response({'error': {'code': 'not_authenticated', 'message': 'Invalid credentials.'}},
                             status=status.HTTP_401_UNAUTHORIZED)

        if user.requires_second_factor():
            second_factor = getattr(user, 'second_factor', None)
            if second_factor is None or second_factor.disabled_at is not None:
                # No factor to present yet (never enrolled, or disabled by an
                # approved recovery). HRMS-NFR-024 requires presentation "on
                # every authentication," but enrolment is self-service
                # (`/api/auth/second-factor/`) and itself requires a session
                # — credentials alone establish one here so the account
                # holder can reach that endpoint, on the same reasoning any
                # mandatory-2FA product uses for first-time setup. No factor
                # exists yet, so nothing is bypassed that HRMS-NFR-024 asks
                # to be presented.
                login(request, user)
                audit.services.record(
                    category=AuditLog.CATEGORY_LOGIN_ATTEMPT,
                    action='login_success',
                    actor=user,
                    detail={'second_factor_enrollment_required': True},
                )
                return Response({**MeSerializer(user).data, 'second_factor_enrollment_required': True})
            if not totp_code or not totp.verify_code(second_factor.secret_ref, totp_code):
                audit.services.record(
                    category=AuditLog.CATEGORY_SECOND_FACTOR_EVENT,
                    action='second_factor_presentation_failed',
                    actor=user,
                )
                return Response({'second_factor_required': True}, status=status.HTTP_200_OK)

            second_factor.last_verified_at = timezone.now()
            second_factor.save(update_fields=['last_verified_at'])

        login(request, user)
        audit.services.record(
            category=AuditLog.CATEGORY_LOGIN_ATTEMPT,
            action='login_success',
            actor=user,
        )
        return Response(MeSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class PasswordResetRequestView(APIView):
    """`POST /api/auth/password-reset/`. Uniform response regardless of
    whether the address exists or the send succeeds (ADR-0011)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.request_password_reset(serializer.validated_data['email'])
        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetConfirmView(APIView):
    """`POST /api/auth/password-reset/confirm/`.

    Not named in `docs/06-api-contracts.md` §4.2, which specifies only the
    request step. A reset that cannot be completed satisfies no requirement;
    this endpoint is the necessary counterpart, added on the same reasoning
    the contract gives its own request endpoint, and should be folded into
    that document on review.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok = services.confirm_password_reset(
            serializer.validated_data['uid'],
            serializer.validated_data['token'],
            serializer.validated_data['password'],
        )
        if not ok:
            return Response({'error': {'code': 'validation_error', 'message': 'Invalid or expired reset link.'}},
                             status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SecondFactorEnrollView(APIView):
    """`POST /api/auth/second-factor/`. Self-enrolment only (HRMS-NFR-024)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if SecondFactor.objects.filter(user=request.user, disabled_at__isnull=True).exists():
            return Response({'error': {'code': 'conflict', 'message': 'A second factor is already enrolled.'}},
                             status=status.HTTP_409_CONFLICT)

        secret = totp.generate_secret()
        SecondFactor.objects.create(user=request.user, secret_ref=secret)
        audit.services.record(
            category=AuditLog.CATEGORY_SECOND_FACTOR_EVENT,
            action='second_factor_enrolled',
            actor=request.user,
        )
        uri = totp.provisioning_uri(secret, request.user.email)
        return Response(SecondFactorEnrollResponseSerializer({'provisioning_uri': uri}).data,
                         status=status.HTTP_201_CREATED)


class SecondFactorRecoveryRequestCreateView(APIView):
    """`POST /api/auth/second-factor/recovery-requests/`. Self only."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        recovery_request = SecondFactorRecoveryRequest.objects.create(user=request.user)
        audit.services.record(
            category=AuditLog.CATEGORY_SECOND_FACTOR_EVENT,
            action='second_factor_recovery_requested',
            actor=request.user,
        )
        return Response(SecondFactorRecoveryRequestSerializer(recovery_request).data,
                         status=status.HTTP_201_CREATED)


class SecondFactorRecoveryRequestDecideView(APIView):
    """`POST /api/auth/second-factor/recovery-requests/{id}/decide/`."""

    permission_classes = [IsAuthenticated, CanDecideSecondFactorRecovery]

    def post(self, request, pk):
        recovery_request = get_object_or_404(SecondFactorRecoveryRequest, pk=pk)
        self.check_object_permissions(request, recovery_request)

        serializer = SecondFactorRecoveryDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.validated_data['decision']

        recovery_request.status = decision
        recovery_request.decided_at = timezone.now()
        recovery_request.approver = request.user
        recovery_request.save(update_fields=['status', 'decided_at', 'approver'])

        if decision == 'approved':
            SecondFactor.objects.filter(user=recovery_request.user).update(disabled_at=timezone.now())

        audit.services.record(
            category=AuditLog.CATEGORY_SECOND_FACTOR_EVENT,
            action=f'second_factor_recovery_{decision}',
            actor=request.user,
            target_type='user_account',
            target_id=recovery_request.user_id,
        )
        return Response(SecondFactorRecoveryRequestSerializer(recovery_request).data)
