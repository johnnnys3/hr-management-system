"""TOTP per ADR-0012. A thin wrapper over pyotp so callers never touch the library directly."""
import pyotp


def generate_secret():
    return pyotp.random_base32()


def provisioning_uri(secret, email, issuer='HRMS'):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_code(secret, code):
    return pyotp.TOTP(secret).verify(code)
