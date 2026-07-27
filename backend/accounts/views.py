from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog

from . import services, totp
from .models import SecondFactor, SecondFactorRecoveryRequest, User
from .permissions import (
    SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY,
    CanDecideSecondFactorRecovery,
    IsFullyAuthenticated,
)
from .serializers import (
    LoginSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationRequestSerializer,
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

    @method_decorator(csrf_protect)
    def post(self, request):
        # DRF's SessionAuthentication only enforces CSRF against a request
        # that already carries an authenticated session — an anonymous
        # login POST is invisible to it, which would otherwise leave this
        # endpoint open to a login-CSRF (forcing a victim's browser to
        # authenticate as an attacker's account). csrf_protect runs
        # Django's check explicitly, independent of DRF's exemption.
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
            # Locked for the duration of the check-and-consume: without this,
            # two concurrent requests carrying the same code could both read
            # last_verified_step before either write lands, and both succeed.
            with transaction.atomic():
                second_factor = SecondFactor.objects.select_for_update().filter(user=user).first()
                if second_factor is None or second_factor.disabled_at is not None:
                    # No factor to present yet (never enrolled, or disabled by
                    # an approved recovery). HRMS-NFR-024 requires
                    # presentation "on every authentication," but enrolment
                    # is self-service (`/api/auth/second-factor/`) and itself
                    # requires a session — credentials alone establish one
                    # here so the account holder can reach that endpoint, on
                    # the same reasoning any mandatory-2FA product uses for
                    # first-time setup. No factor exists yet, so nothing is
                    # bypassed that HRMS-NFR-024 asks to be presented. The
                    # session is marked pending: only enrolment and logout
                    # are reachable until it clears (`IsFullyAuthenticated`),
                    # so this isn't a full grant.
                    login(request, user)
                    request.session[SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY] = True
                    audit.services.record(
                        category=AuditLog.CATEGORY_LOGIN_ATTEMPT,
                        action='login_success',
                        actor=user,
                        detail={'second_factor_enrollment_required': True},
                    )
                    return Response({**MeSerializer(user).data, 'second_factor_enrollment_required': True})
                if not totp.verify_and_consume(second_factor, totp_code):
                    audit.services.record(
                        category=AuditLog.CATEGORY_SECOND_FACTOR_EVENT,
                        action='second_factor_presentation_failed',
                        actor=user,
                    )
                    return Response({'second_factor_required': True}, status=status.HTTP_200_OK)

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
    """Reachable in the pending, not-fully-authenticated state too (unlike
    most endpoints, which require `IsFullyAuthenticated`) — the SPA's one
    "who am I" call needs to see `second_factor_enrollment_pending` to know
    to route to the enrolment screen after a page reload."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = MeSerializer(request.user).data
        data['second_factor_enrollment_pending'] = bool(
            request.session.get(SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY, False)
        )
        return Response(data)


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


class PhoneVerificationRequestView(APIView):
    """`POST /api/auth/phone/`. Self only — a user verifies their own
    delivery number, same reasoning as second-factor self-enrolment."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.request_phone_verification(request.user, serializer.validated_data['phone_number'])
        return Response(status=status.HTTP_202_ACCEPTED)


class PhoneVerificationConfirmView(APIView):
    """`POST /api/auth/phone/confirm/`. Generic failure on wrong or expired
    code — no distinction surfaced, same posture as password reset."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok = services.confirm_phone_verification(request.user, serializer.validated_data['code'])
        if not ok:
            return Response({'error': {'code': 'validation_error', 'message': 'Invalid or expired code.'}},
                             status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerificationConfirmView(APIView):
    """`POST /api/auth/email/confirm/`. Self only — confirms the code sent
    when a System Administrator created the account. Generic failure on
    wrong or expired code, same posture as password reset/phone confirm."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok = services.confirm_email_verification(request.user, serializer.validated_data['code'])
        if not ok:
            return Response({'error': {'code': 'validation_error', 'message': 'Invalid or expired code.'}},
                             status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SecondFactorEnrollView(APIView):
    """`POST /api/auth/second-factor/`. Self-enrolment only (HRMS-NFR-024).

    Reachable in the pending, not-fully-authenticated state (unlike most
    endpoints) — it's the one thing a session in that state exists to reach.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Locks the user row for the duration of the read-then-write below —
        # without it, two concurrent enrolment requests could both see no
        # active factor and both proceed, one of them hitting the
        # OneToOneField's unique constraint only after doing real work.
        with transaction.atomic():
            User.objects.select_for_update().get(pk=request.user.pk)
            existing = SecondFactor.objects.select_for_update().filter(user=request.user).first()
            if existing is not None and existing.disabled_at is None:
                return Response({'error': {'code': 'conflict', 'message': 'A second factor is already enrolled.'}},
                                 status=status.HTTP_409_CONFLICT)

            secret = totp.generate_secret()
            encrypted = totp.encrypt_secret(secret)
            if existing is not None:
                # A previously disabled factor (approved recovery) re-enrols
                # onto the same row rather than a second one — `user` is
                # OneToOneField, so a bare create() here would fail on the
                # unique constraint instead of ever reaching this point cleanly.
                existing.secret_ref = encrypted
                existing.disabled_at = None
                existing.last_verified_at = None
                existing.last_verified_step = None
                existing.save(update_fields=['secret_ref', 'disabled_at', 'last_verified_at', 'last_verified_step'])
            else:
                SecondFactor.objects.create(user=request.user, secret_ref=encrypted)

        request.session.pop(SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY, None)
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

    permission_classes = [IsFullyAuthenticated]

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

    permission_classes = [IsFullyAuthenticated, CanDecideSecondFactorRecovery]

    def post(self, request, pk):
        serializer = SecondFactorRecoveryDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.validated_data['decision']

        with transaction.atomic():
            recovery_request = get_object_or_404(
                SecondFactorRecoveryRequest.objects.select_for_update(), pk=pk
            )
            self.check_object_permissions(request, recovery_request)

            if recovery_request.status != SecondFactorRecoveryRequest.STATUS_PENDING:
                return Response(
                    {'error': {'code': 'conflict', 'message': 'This request has already been decided.'}},
                    status=status.HTTP_409_CONFLICT,
                )

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
