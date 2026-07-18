"""Object storage helpers for `employee_document`, ADR-0007.

`object_key` is generated server-side, never taken from the client's
filename (ADR-0007). Content type is validated by inspecting the file's
magic bytes, not trusted from the client-supplied `Content-Type` header
alone — a mismatch (or an unrecognised signature) is rejected.
"""
import uuid

from django.core.files.storage import default_storage

# Signature -> content type, restricted to the document types HR uploads
# handle (HRMS-FR-006): identity/contract PDFs, scanned images, office
# documents. Not an exhaustive MIME sniffer — a narrow allowlist, per
# ADR-0007's "server-side content-type validation."
_SIGNATURES = [
    (b'%PDF-', 'application/pdf'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
    (b'PK\x03\x04', 'application/zip'),  # docx/xlsx/pptx are zip containers
]


def sniff_content_type(file_obj):
    """Reads the file's leading bytes and returns the matching content
    type, or `None` if no known signature matches."""
    header = file_obj.read(8)
    file_obj.seek(0)
    for signature, content_type in _SIGNATURES:
        if header.startswith(signature):
            return content_type
    return None


def generate_object_key(employee_id, file_name):
    extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    suffix = f'.{extension}' if extension else ''
    return f'employee-documents/{employee_id}/{uuid.uuid4().hex}{suffix}'


def save_document(object_key, file_obj):
    return default_storage.save(object_key, file_obj)


def signed_download_url(object_key):
    return default_storage.url(object_key)
