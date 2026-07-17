from rest_framework.permissions import BasePermission

SYSTEM_ADMINISTRATOR_GROUP = 'System Administrator'


class IsSystemAdministrator(BasePermission):
    """`docs/07-iam-rbac.md` §4.2: System Administrator holds R on the audit log; all other roles are denied."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name=SYSTEM_ADMINISTRATOR_GROUP).exists()
        )
