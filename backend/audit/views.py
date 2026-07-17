from rest_framework.generics import ListAPIView

from .models import AuditLog
from .permissions import IsSystemAdministrator
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    """The System Administrator read surface. `docs/07-iam-rbac.md` §4.2 grants R and nothing else."""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsSystemAdministrator]
