"""TOTP per ADR-0012. A thin wrapper over pyotp so callers never touch the
library directly, plus at-rest encryption of the shared secret and replay
protection on verification.
"""
import hmac
import time

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.utils import timezone


def _fernet():
    return Fernet(settings.TOTP_ENCRYPTION_KEY)


def generate_secret():
    return pyotp.random_base32()


def encrypt_secret(secret):
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_secret(secret_ref):
    return _fernet().decrypt(secret_ref.encode()).decode()


def provisioning_uri(secret, email, issuer='HRMS'):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_and_consume(second_factor, code):
    """True if `code` is currently valid for `second_factor` and has not
    already been accepted. A ±1 time-step window is allowed (ADR-0012's
    "single-step tolerance"); accepting a step records it on
    `last_verified_step` so the identical code cannot be replayed.
    """
    if not code:
        return False

    try:
        secret = decrypt_secret(second_factor.secret_ref)
    except InvalidToken:
        return False

    totp = pyotp.TOTP(secret)
    current_step = int(time.time() // totp.interval)
    last_verified_step = second_factor.last_verified_step

    for step in (current_step, current_step - 1, current_step + 1):
        # Monotonic, not just not-equal: a step at or before the last one
        # accepted is rejected even if it isn't an exact repeat, since the
        # ±1 window can otherwise let an out-of-order older code through
        # after a later one has already been consumed.
        if last_verified_step is not None and step <= last_verified_step:
            continue
        # TOTP.at() takes a Unix timestamp, not a step count.
        if hmac.compare_digest(totp.at(step * totp.interval), code):
            second_factor.last_verified_step = step
            second_factor.last_verified_at = timezone.now()
            second_factor.save(update_fields=['last_verified_step', 'last_verified_at'])
            return True
    return False
