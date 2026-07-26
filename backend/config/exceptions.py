"""Normalizes DRF's default error shape into the `{error: {message, code,
fields}}` envelope `frontend/src/api/client.ts` expects everywhere
(accounts/iam views already return it by hand; this covers every other
view so a validation error — e.g. SalaryStructure.name's unique
constraint — surfaces its real message instead of a generic fallback)."""
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def _has_valid_error_envelope(data):
    error = data.get('error') if isinstance(data, dict) else None
    return isinstance(error, dict) and {'code', 'message', 'fields'} <= error.keys()


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None or _has_valid_error_envelope(response.data):
        return response

    if not isinstance(exc, ValidationError):
        detail = response.data.get('detail', response.data) if isinstance(response.data, dict) else response.data
        code = getattr(exc, 'default_code', 'error')
        response.data = {'error': {'code': code, 'message': str(detail), 'fields': None}}
        return response

    detail = response.data
    if isinstance(detail, dict):
        fields = {k: [str(e) for e in v] if isinstance(v, list) else [str(v)] for k, v in detail.items() if v}
        message = next(iter(fields.values()))[0] if fields else 'Validation failed.'
    else:
        fields = None
        message = str(detail[0]) if isinstance(detail, list) and detail else (str(detail) if detail else 'Validation failed.')

    response.data = {'error': {'code': 'validation_error', 'message': message, 'fields': fields}}
    return response
