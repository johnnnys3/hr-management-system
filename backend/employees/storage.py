"""Object storage helpers for `employee_document`, ADR-0007.

`object_key` is generated server-side, never taken from the client's
filename (ADR-0007). Content type is validated by inspecting the file's
magic bytes, not trusted from the client-supplied `Content-Type` header
alone — a mismatch (or an unrecognised signature) is rejected.
"""
import uuid
import zipfile

from django.core.files.storage import default_storage

DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
PPTX = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

# Signature -> content type, restricted to the document types HR uploads
# handle (HRMS-FR-006): identity/contract PDFs, scanned images, office
# documents. Not an exhaustive MIME sniffer — a narrow allowlist, per
# ADR-0007's "server-side content-type validation."
_SIGNATURES = [
    (b'%PDF-', 'application/pdf'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
]

# docx/xlsx/pptx are all ZIP containers distinguished only by their
# internal member paths — a bare `PK\x03\x04` signature match would accept
# any ZIP file, not just an office document, so a ZIP-signed upload is
# opened and its member paths are checked against these OOXML markers.
_OOXML_MARKERS = [
    ('word/', DOCX),
    ('xl/', XLSX),
    ('ppt/', PPTX),
]

CONTENT_TYPE_EXTENSIONS = {
    'application/pdf': 'pdf',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    DOCX: 'docx',
    XLSX: 'xlsx',
    PPTX: 'pptx',
}


def _sniff_ooxml(file_obj):
    try:
        with zipfile.ZipFile(file_obj) as archive:
            names = archive.namelist()
    except zipfile.BadZipFile:
        return None
    finally:
        file_obj.seek(0)
    for prefix, content_type in _OOXML_MARKERS:
        if any(name.startswith(prefix) for name in names):
            return content_type
    return None


def sniff_content_type(file_obj):
    """Reads the file's leading bytes (and, for a ZIP container, its member
    paths) and returns the matching content type, or `None` if nothing
    recognised matches — including a ZIP archive that is not one of the
    supported OOXML formats."""
    header = file_obj.read(8)
    file_obj.seek(0)
    for signature, content_type in _SIGNATURES:
        if header.startswith(signature):
            return content_type
    if header.startswith(b'PK\x03\x04'):
        return _sniff_ooxml(file_obj)
    return None


def generate_object_key(employee_id, content_type):
    """The canonical extension is derived from the detected content type,
    not the client-supplied filename (ADR-0007) — a mismatched or absent
    client extension cannot produce a misleading stored key."""
    extension = CONTENT_TYPE_EXTENSIONS[content_type]
    return f'employee-documents/{employee_id}/{uuid.uuid4().hex}.{extension}'


def save_document(object_key, file_obj):
    return default_storage.save(object_key, file_obj)


def delete_document(object_key):
    default_storage.delete(object_key)


def signed_download_url(object_key):
    return default_storage.url(object_key)
