"""Normalizes DRF's default error shape into the `{error: {message, code,
fields}}` envelope `frontend/src/api/client.ts` expects everywhere
(accounts/iam views already return it by hand; this covers every other
view so a validation error — e.g. SalaryStructure.name's unique
constraint — surfaces its real message instead of a generic fallback)."""
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None or isinstance(response.data, dict) and 'error' in response.data:
        return response

    detail = response.data
    if isinstance(detail, dict):
        fields = {k: [str(e) for e in v] if isinstance(v, list) else [str(v)] for k, v in detail.items()}
        message = next(iter(fields.values()))[0]
    else:
        fields = None
        message = str(detail[0]) if isinstance(detail, list) else str(detail)

    response.data = {'error': {'code': 'validation_error', 'message': message, 'fields': fields}}
    return response
