"""Authentication's application logic, kept out of views per the pattern audit/mail use.

Password reset (ADR-0011, §4.2): mail dispatch is consumed directly, and the
response is uniform regardless of whether the address exists or whether the
send succeeds — a varying response is an enumeration oracle.
"""
import logging
import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

import mail.services
import sms.services
from .models import User

logger = logging.getLogger('accounts')

password_reset_token_generator = PasswordResetTokenGenerator()

PHONE_CODE_TTL_SECONDS = 300


def request_password_reset(email):
    """Always returns None. The caller learns nothing from this call — the
    HTTP layer returns the same response whether or not this did anything,
    whether or not queuing the mail dispatch task itself raised."""
    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token_generator.make_token(user)
    try:
        mail.services.send(
            template='password_reset',
            recipient=user.email,
            context={'uid': uid, 'token': token},
        )
    except Exception:
        # send() only enqueues (mail/services.py) — a failure here is the
        # broker being unreachable, not a delivery failure, but it must not
        # surface any differently than a quiet success (ADR-0011).
        logger.exception('password reset: failed to queue mail dispatch')


def confirm_password_reset(uid, token, new_password):
    """Returns True if the reset was applied, False otherwise. Unlike the
    request step, this is a state-changing action on a specific token and
    is allowed to report success/failure — knowing a token is invalid does
    not disclose account existence the way a varying request-step response
    would."""
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return False

    if not password_reset_token_generator.check_token(user, token):
        return False

    user.set_password(new_password)
    user.save(update_fields=['password'])
    return True


def _generate_code():
    return f'{secrets.randbelow(1_000_000):06d}'


def request_phone_verification(user, phone_number):
    """Always stores the new number and queues a code, clearing any prior
    verification — a new number must be reverified before use (spec §4)."""
    code = _generate_code()
    user.phone_number = phone_number
    user.phone_verified_at = None
    user.phone_verification_code_hash = make_password(code)
    user.phone_verification_expires_at = timezone.now() + timezone.timedelta(seconds=PHONE_CODE_TTL_SECONDS)
    user.save(update_fields=[
        'phone_number', 'phone_verified_at', 'phone_verification_code_hash', 'phone_verification_expires_at',
    ])
    sms.services.send(to=phone_number, body=f'Your HRMS verification code is {code}')


def confirm_phone_verification(user, code):
    """Returns True if the code matched and was not expired."""
    if (
        user.phone_verification_code_hash is None
        or user.phone_verification_expires_at is None
        or timezone.now() > user.phone_verification_expires_at
    ):
        return False
    if not check_password(code, user.phone_verification_code_hash):
        return False

    user.phone_verified_at = timezone.now()
    user.phone_verification_code_hash = None
    user.phone_verification_expires_at = None
    user.save(update_fields=['phone_verified_at', 'phone_verification_code_hash', 'phone_verification_expires_at'])
    return True
