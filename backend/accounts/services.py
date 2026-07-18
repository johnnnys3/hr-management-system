"""Authentication's application logic, kept out of views per the pattern audit/mail use.

Password reset (ADR-0011, §4.2): mail dispatch is consumed directly, and the
response is uniform regardless of whether the address exists or whether the
send succeeds — a varying response is an enumeration oracle.
"""
import logging

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

import mail.services
from .models import User

logger = logging.getLogger('accounts')

password_reset_token_generator = PasswordResetTokenGenerator()


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
