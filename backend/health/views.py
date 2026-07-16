from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Confirms the composition is wired correctly: Django reaches Postgres and redis-cache."""
    checks = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception as exc:
        checks['database'] = f'error: {exc}'

    try:
        cache.set('health_check', 'ok', timeout=5)
        checks['cache'] = 'ok' if cache.get('health_check') == 'ok' else 'error: readback mismatch'
    except Exception as exc:
        checks['cache'] = f'error: {exc}'

    status = 'ok' if all(v == 'ok' for v in checks.values()) else 'degraded'
    return Response({'status': status, 'checks': checks})
