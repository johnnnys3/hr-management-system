from rest_framework.permissions import BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, is_employee, is_manager
from reporting_structure.models import ReportingRelationship

HR_ROLES = [HR_OFFICER, HR_ADMINISTRATOR]


def _hr(user):
    return user.groups.filter(name__in=HR_ROLES).exists()


class CanAccessLeaveTypes(BasePermission):
    """`GET /api/leave-types/`, `docs/06-api-contracts.md` §4.12: HR
    Officer, HR Administrator read; Manager also needs read to resolve
    leave-type names on their team's requests (issue #125)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (_hr(user) or is_manager(user)))


class CanAccessLeaveBalances(BasePermission):
    """`GET /api/leave-balances/`, `docs/07-iam-rbac.md` §5's leave-requests
    row: Employee own, Manager direct reports', HR Officer/Administrator
    all."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return _hr(user) or is_manager(user) or is_employee(user)

    def has_object_permission(self, request, view, balance):
        user = request.user
        if _hr(user):
            return True
        if is_manager(user):
            return ReportingRelationship.objects.filter(
                employee_id=balance.employee_id, manager_employee_id=user.employee_id
            ).exists()
        return is_employee(user) and balance.employee_id == user.employee_id


class CanAccessLeaveRequests(BasePermission):
    """`GET, POST /api/leave-requests/`, `docs/06-api-contracts.md` §4.12."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method == 'POST':
            return is_employee(user)
        return _hr(user) or is_manager(user) or is_employee(user)

    def has_object_permission(self, request, view, leave_request):
        user = request.user
        if _hr(user):
            return True
        if is_manager(user):
            if ReportingRelationship.objects.filter(
                employee_id=leave_request.employee_id, manager_employee_id=user.employee_id
            ).exists():
                return True
        return is_employee(user) and leave_request.employee_id == user.employee_id


class CanCorrectLeaveRequest(BasePermission):
    """`PATCH /api/leave-requests/{id}/`, `docs/06-api-contracts.md` §4.12:
    HR Officer only (correction/cancellation, never approval — enforced by
    the serializer)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_OFFICER).exists())


class CanDecideLeaveRequest(BasePermission):
    """`POST /api/leave-requests/{id}/approve|reject/`,
    `docs/07-iam-rbac.md` §4.2's Leave approval row: Manager-only at action
    level, scoped to the requester's direct manager."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and is_manager(user))

    def has_object_permission(self, request, view, leave_request):
        return ReportingRelationship.objects.filter(
            employee_id=leave_request.employee_id, manager_employee_id=request.user.employee_id
        ).exists()


class CanCancelLeaveRequest(BasePermission):
    """`POST /api/leave-requests/{id}/cancel/`: Employee, own pending
    request only."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and is_employee(user))

    def has_object_permission(self, request, view, leave_request):
        return leave_request.employee_id == request.user.employee_id


class CanAccessLeaveCalendar(BasePermission):
    """`GET /api/leave-calendar/`, `docs/07-iam-rbac.md` §4.2's Leave
    calendar row: HR Officer, HR Administrator, Manager."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return _hr(user) or is_manager(user)
