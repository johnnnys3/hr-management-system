"""Object storage helpers for `bank_transfer_file`, ADR-0007. Same
save/signed-URL pattern as `employees.storage`/`recruitment.storage`."""
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def save_bank_transfer_file(object_key, content_bytes):
    return default_storage.save(object_key, ContentFile(content_bytes))


def save_payslip_pdf(object_key, content_bytes):
    return default_storage.save(object_key, ContentFile(content_bytes))


def signed_download_url(object_key):
    return default_storage.url(object_key)
