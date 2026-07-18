from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, is_employee


class CanAccessEmployeeRecords(BasePermission):
    """`docs/07-iam-rbac.md` §4.2's Employee records row: HR Officer holds
    C, R, U; HR Administrator holds R, U status only (the status-only write
    restriction is enforced by the view choosing a narrower serializer, not
    here); Employee holds R own (row-scoped, not action-scoped — granted
    here, narrowed to "own" by the view's queryset).

    Manager's "R direct reports" cell is not implemented: `reporting_relationship`
    is Module 8, not yet built. `is_manager` stays stubbed `False`
    (`iam/roles.py`), so a Manager with no other role reaches nothing here.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists() or is_employee(user)
        if request.method == 'POST':
            return user.groups.filter(name=HR_OFFICER).exists()
        # PATCH: HR Officer (full record) or HR Administrator (status only,
        # narrowed by the view's serializer choice).
        return user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists()


class CanAccessEmployeeDocuments(BasePermission):
    """`docs/07-iam-rbac.md` §4.2's Employee documents row: HR Officer
    holds C, R, U; HR Administrator holds R; Employee holds R own."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists() or is_employee(user)
        return user.groups.filter(name=HR_OFFICER).exists()


class CanAccessEmergencyContacts(BasePermission):
    """Grouped under Employee records per `docs/06-api-contracts.md` §4.3:
    HR Officer holds C, R, U."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.groups.filter(name=HR_OFFICER).exists()


class IsOwnEmployeeRecord(BasePermission):
    """`/api/employees/me/`, `docs/06-api-contracts.md` §4.3: Employee R, U
    own — self-service only, no HR role reaches this endpoint."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and is_employee(user))
