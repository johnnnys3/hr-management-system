from rest_framework.permissions import BasePermission

SYSTEM_ADMINISTRATOR_GROUP = 'System Administrator'
HR_ADMINISTRATOR_GROUP = 'HR Administrator'
HR_OFFICER_GROUP = 'HR Officer'


class IsSystemAdministrator(BasePermission):
    """`docs/07-iam-rbac.md` §4.2: System Administrator holds R on the audit log; all other roles are denied."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name=SYSTEM_ADMINISTRATOR_GROUP).exists()
        )


class CanAccessEmployeeAuditHistory(BasePermission):
    """`GET /api/employees/{id}/audit-history/`, `docs/06-api-contracts.md`
    §4.1: HR Administrator, HR Officer, System Administrator — HRMS-FR-010's
    read access, distinct from the full-log's System-Administrator-only row,
    since this is a filtered read of `audit_log` scoped to one employee
    record rather than the base resource."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(
                name__in=[SYSTEM_ADMINISTRATOR_GROUP, HR_ADMINISTRATOR_GROUP, HR_OFFICER_GROUP],
            ).exists()
        )
