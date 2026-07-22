from rest_framework.generics import ListAPIView

from .models import AuditLog
from .permissions import CanAccessEmployeeAuditHistory, IsSystemAdministrator
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


class EmployeeAuditHistoryView(ListAPIView):
    """`GET /api/employees/{id}/audit-history/`, `docs/06-api-contracts.md`
    §4.1: a filtered read of `audit_log` where `target_type = 'employee'`
    and `target_id = {id}` — not a second store (`CONTEXT.md`)."""

    serializer_class = AuditLogSerializer
    permission_classes = [CanAccessEmployeeAuditHistory]

    def get_queryset(self):
        return AuditLog.objects.filter(target_type='employee', target_id=self.kwargs['pk'])
