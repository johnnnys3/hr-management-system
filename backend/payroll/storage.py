"""Object storage helpers for `bank_transfer_file`/`payslip`, ADR-0007.
Same save/signed-URL pattern as `employees.storage`/`recruitment.storage`
— object keys are generated here, server-side, not left to callers to
compose inline."""
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone


def generate_bank_transfer_object_key(payroll_run_id):
    return f'payroll/bank-transfer/{payroll_run_id}-{timezone.now().strftime("%Y%m%dT%H%M%S")}.csv'


def generate_payslip_object_key(payroll_run_id, employee_id, payslip_id):
    return f'payroll/payslips/{payroll_run_id}/{employee_id}-{payslip_id}.pdf'


def save_file(object_key, content_bytes):
    return default_storage.save(object_key, ContentFile(content_bytes))


def signed_download_url(object_key):
    return default_storage.url(object_key)
