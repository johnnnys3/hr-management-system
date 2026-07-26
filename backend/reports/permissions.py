from rest_framework.permissions import BasePermission

from iam.roles import EXECUTIVE, HR_ADMINISTRATOR, PAYROLL_OFFICER, is_manager


def _in_group(user, name):
    return user.groups.filter(name=name).exists()


def _is_hr_administrator(user):
    return _in_group(user, HR_ADMINISTRATOR)


def _is_payroll_officer(user):
    return _in_group(user, PAYROLL_OFFICER)


def _is_executive(user):
    return _in_group(user, EXECUTIVE)


class CanAccessOrgReports(BasePermission):
    """Headcount, leave-utilization, turnover — `docs/07-iam-rbac.md`
    §4.2/`docs/06-api-contracts.md` §4.15: HR Administrator: R (org-wide);
    Manager: R (team-level); Executive: R (aggregate only,
    HRMS-NFR-019). HR Officer deliberately excluded — narrowed from the
    original design on the project owner's decision."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return _is_hr_administrator(user) or _is_executive(user) or is_manager(user)


class CanAccessPayrollReports(BasePermission):
    """Payroll cost, payroll summary — Payroll Officer: R (full detail);
    Executive: R (aggregate only, HRMS-NFR-019). Same cells
    `docs/07-iam-rbac.md` §4.2 gives Payroll processing's "R (payroll
    cost)"."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return _is_payroll_officer(user) or _is_executive(user)


def report_scope(user):
    """Returns one of 'full', 'team', 'aggregate' for the org reports
    (headcount/leave-utilization/turnover) — checked in this order so an
    Executive who also happens to hold an HR or Manager role still gets
    aggregate-only, per HRMS-NFR-019/`docs/07-iam-rbac.md` §4.3 ("never
    an individual employee record"), the same check-Executive-first
    short-circuit DASH-001 established for Dashboard."""
    if _is_executive(user):
        return 'aggregate'
    if _is_hr_administrator(user):
        return 'full'
    if is_manager(user):
        return 'team'
    return None


def payroll_report_scope(user):
    """Same short-circuit as `report_scope`, for the two payroll
    reports: Executive checked first, so an Executive who also holds
    Payroll Officer never gets full per-employee detail."""
    if _is_executive(user):
        return 'aggregate'
    if _is_payroll_officer(user):
        return 'full'
    return None
