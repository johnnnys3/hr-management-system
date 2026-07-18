"""Object storage helpers for `candidate.resume_object_key` and
`offer_letter.document_object_key`, same pattern as `employees.storage`
(ADR-0007). Content-type sniffing is shared with `employees.storage` rather
than duplicated — it is a generic magic-byte check, not employee-specific.
"""
import uuid

from django.core.files.storage import default_storage

from employees.storage import CONTENT_TYPE_EXTENSIONS, sniff_content_type  # noqa: F401


def generate_resume_object_key(candidate_id, content_type):
    extension = CONTENT_TYPE_EXTENSIONS[content_type]
    return f'candidate-resumes/{candidate_id}/{uuid.uuid4().hex}.{extension}'


def generate_offer_letter_object_key(offer_id):
    # A generated text document, not a PDF — this project has no PDF
    # rendering dependency yet, and HRMS-FR-020/021 require only that the
    # letter exist as a stored, retrievable document.
    return f'offer-letters/{offer_id}/{uuid.uuid4().hex}.txt'


def save_document(object_key, file_obj):
    return default_storage.save(object_key, file_obj)


def delete_document(object_key):
    default_storage.delete(object_key)


def signed_download_url(object_key):
    return default_storage.url(object_key)
