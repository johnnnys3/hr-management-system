"""Object storage helpers for `report_export`, ADR-0007. Same
save/signed-URL pattern as `payroll.storage`."""
import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone


def generate_export_object_key(report_export_id, report_type):
    return f'reports/exports/{report_type}/{report_export_id}-{timezone.now().strftime("%Y%m%dT%H%M%S")}.json'


def save_export_file(object_key, data):
    return default_storage.save(object_key, ContentFile(json.dumps(data, default=str).encode('utf-8')))


def signed_download_url(object_key):
    return default_storage.url(object_key)
