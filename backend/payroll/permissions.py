from rest_framework.permissions import BasePermission

from iam.roles import PAYROLL_OFFICER, is_employee


def _payroll_officer(user):
    return user.groups.filter(name=PAYROLL_OFFICER).exists()


class IsPayrollOfficer(BasePermission):
    """Statutory rates (read-only), payroll-run CRUD, calculate/submit/
    bank-transfer-file: Payroll Officer only, `docs/07-iam-rbac.md`
    §4.2's Payroll processing row."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and _payroll_officer(user))


def can_decide_payroll_run(user, payroll_run):
    """`docs/07-iam-rbac.md` §4.4: `payroll.approve_payroll_run` is
    granted to no role by default — this design does not fix an
    approver role, on the same shape as `iam.approve_role_grant`
    (`iam/permissions.py`). Callers check the initiator case
    separately first, since api-contracts §4.14 asks for a
    distinguishable `self_approval_forbidden` code on that specific
    rejection rather than a bare 403 — this function covers the
    remaining "does this user hold the permission at all" question."""
    if user.is_superuser:
        # Same reasoning as iam.permissions.CanDecideRoleGrantRequest:
        # is_superuser short-circuits has_perm() to True, which would
        # make break-glass an unconditional payroll approver — exactly
        # what HRMS-NFR-019/§4.4 restricts payroll access away from a
        # role administering accounts, not toward.
        return False
    return user.has_perm('payroll.approve_payroll_run')


class CanAccessPayslips(BasePermission):
    """`GET /api/payslips/`, `docs/07-iam-rbac.md` §4.2's Payslips row:
    Employee R own, Payroll Officer R all."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return _payroll_officer(user) or is_employee(user)

    def has_object_permission(self, request, view, payslip):
        user = request.user
        if _payroll_officer(user):
            return True
        return is_employee(user) and payslip.employee_id == user.employee_id
