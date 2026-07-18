from rest_framework.generics import ListAPIView

from .models import AuditLog
from .permissions import IsSystemAdministrator
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    """The System Administrator read surface. `docs/07-iam-rbac.md` §4.2 grants R and nothing else.

    `?category=...` filters to one of `AuditLog.CATEGORY_CHOICES` —
    `docs/06-api-contracts.md` §4.9 names `?category=permission_change` as
    this endpoint's RBAC/IAM view rather than a second endpoint.
    """

    serializer_class = AuditLogSerializer
    permission_classes = [IsSystemAdministrator]

    def get_queryset(self):
        queryset = AuditLog.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
