import logging

from django.core.cache import cache
from django.db import connection
from rest_framework import status as http_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Confirms the composition is wired correctly: Django reaches Postgres and redis-cache."""
    checks = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception:
        logger.exception('Health check: database connectivity failed')
        checks['database'] = 'error'

    try:
        cache.set('health_check', 'ok', timeout=5)
        checks['cache'] = 'ok' if cache.get('health_check') == 'ok' else 'error'
    except Exception:
        logger.exception('Health check: cache connectivity failed')
        checks['cache'] = 'error'

    degraded = any(v != 'ok' for v in checks.values())
    response_status = http_status.HTTP_503_SERVICE_UNAVAILABLE if degraded else http_status.HTTP_200_OK
    return Response(
        {'status': 'degraded' if degraded else 'ok', 'checks': checks},
        status=response_status,
    )
