from rest_framework.permissions import BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, is_manager

HR_ROLES = [HR_OFFICER, HR_ADMINISTRATOR]


class CanAccessReportingRelationships(BasePermission):
    """`docs/06-api-contracts.md` §4.5: `GET /api/reporting-relationships/`
    is HR Officer/HR Administrator read only, grouped with Employee records
    access (`docs/04-system-architecture.md` §4's module 8 row: "no
    independent read restriction beyond Module 6's")."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name__in=HR_ROLES).exists())


class CanAccessDirectReports(BasePermission):
    """`GET /api/employees/{id}/direct-reports/`: HR Officer/HR
    Administrator read any `{id}`; Manager reads only where `{id}` is their
    own employee id — the endpoint's visibility is `manager_employee_id =
    caller's employee id`, so a Manager requesting any other `{id}` has
    nothing to see rather than another manager's team."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.groups.filter(name__in=HR_ROLES).exists() or is_manager(user)

    def has_object_permission(self, request, view, employee):
        user = request.user
        if user.groups.filter(name__in=HR_ROLES).exists():
            return True
        return is_manager(user) and employee.pk == user.employee_id


class CanChangeManager(BasePermission):
    """`PATCH /api/employees/{id}/manager/`: HR Officer only
    (`docs/06-api-contracts.md` §4.5)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_OFFICER).exists())
