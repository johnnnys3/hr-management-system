from rest_framework.permissions import BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, is_employee

HR_READ_ROLES = [HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER]


def _in_groups(user, names):
    return user.groups.filter(name__in=names).exists()


class CanAccessSalaryFramework(BasePermission):
    """`GET, POST, PATCH /api/salary-structures/`, `/api/pay-grades/`,
    `docs/07-iam-rbac.md` §4.2's "Salary structures, pay grades" row:
    HR Administrator C/R/U, HR Officer and Payroll Officer R."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessPayGrades(BasePermission):
    """`GET, POST, PATCH /api/pay-grades/`: same as `CanAccessSalaryFramework`.

    Previously also granted Recruiter a blind-selection read (id/name
    only, no salary figures) to pick `offered_pay_grade` when issuing an
    offer (`docs/06-api-contracts.md` §4.6). Recruiter is retired
    (ADR-0013), merged into HR Administrator, which already holds full
    read here via `HR_READ_ROLES` — the narrower carve-out is moot, not
    reinstated for HR Administrator."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessCompensationRecords(BasePermission):
    """`GET, POST /api/employees/{id}/compensation-records/`,
    `docs/07-iam-rbac.md` §4.2's "Compensation history" row (R: HR
    Administrator, HR Officer, Payroll Officer) and "Assign employee to
    pay grade" row (C: HR Officer only). No employee self-read — §4.2
    does not name Employee against either row."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        if request.method == 'POST':
            return _in_groups(user, [HR_OFFICER])
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessBonusCycles(BasePermission):
    """`GET, POST, PATCH /api/bonus-cycles/`, `docs/07-iam-rbac.md` §4.2's
    "Bonus cycles, allowances, benefits" row: HR Administrator C/R/U, HR
    Officer and Payroll Officer R."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessBonusAwards(BasePermission):
    """`GET, POST /api/bonus-cycles/{id}/awards/`,
    `docs/06-api-contracts.md` §4.13: HR Administrator C/R only — no
    employee self-read, unlike allowances/benefits on the same IAM row."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and _in_groups(user, [HR_ADMINISTRATOR]))


class CanAccessAllowanceTypes(BasePermission):
    """`GET, POST, PATCH /api/allowance-types/`: HR Administrator C/R/U,
    HR Officer and Payroll Officer R."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessEmployeeAllowances(BasePermission):
    """`GET, POST /api/employees/{id}/allowances/`,
    `docs/07-iam-rbac.md` §4.2's "R own" cell: HR Administrator C/R, HR
    Officer/Payroll Officer R, Employee R own.

    The "own" scope is checked in `has_permission` against the URL's
    `pk`, not `has_object_permission` against a fetched row — an
    employee with zero allowances must still be denied access to
    another employee's (empty) list, and object-level checks against
    the first row of a possibly-empty queryset would skip that."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method == 'POST':
            return _in_groups(user, [HR_ADMINISTRATOR])
        if _in_groups(user, HR_READ_ROLES):
            return True
        return is_employee(user) and str(user.employee_id) == str(view.kwargs.get('pk'))


class CanAccessBenefits(BasePermission):
    """`GET, POST, PATCH /api/benefits/`: HR Administrator C/R/U, HR
    Officer and Payroll Officer R."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return _in_groups(user, HR_READ_ROLES)
        return _in_groups(user, [HR_ADMINISTRATOR])


class CanAccessBenefitEnrollments(BasePermission):
    """`GET, POST, PATCH /api/employees/{id}/benefit-enrollments/`:
    HR Administrator C/R/U, Employee R own.

    GET's "own" scope is checked in `has_permission` against the URL's
    `pk`, for the same reason as `CanAccessEmployeeAllowances` above —
    an empty list must not bypass the check. PATCH targets a specific
    enrollment row (via `enrollment_id`), so it is still checked with
    `has_object_permission` in the detail view."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ('POST', 'PATCH'):
            return _in_groups(user, [HR_ADMINISTRATOR])
        if _in_groups(user, [HR_ADMINISTRATOR]):
            return True
        return is_employee(user) and str(user.employee_id) == str(view.kwargs.get('pk'))

    def has_object_permission(self, request, view, enrollment):
        user = request.user
        if _in_groups(user, [HR_ADMINISTRATOR]):
            return True
        return is_employee(user) and enrollment.employee_id == user.employee_id
