"""Row-level scoping, `docs/07-iam-rbac.md` §5 / §1.3's "a record not
matched by a visibility rule is not returned."

Action-level access (Django groups/permissions) and row-level access are
two independent layers (§4.1); this module is the second layer only.
There is no queryset to scope yet — every table §5's matrix names
(`employee`, payslips, leave requests, reports) belongs to a module later
than this one. What this module owns is the interface those modules
implement, so a later module cannot reinvent row scoping ad hoc and drift
from the one rule this document states per table.
"""

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, SYSTEM_ADMINISTRATOR, is_employee, is_manager


class VisibilityRule:
    """One rule per module, per §5's table. A module's manager calls
    `scope(queryset, user)` to obtain the rows `user` may see; it must not
    return an unscoped queryset by any other path (§5: omitting this call
    is a disclosure defect and a blocking review finding).

    Subclasses implement `scope`. This base class provides no default —
    "no rule" and "see nothing" must not be the same code path as
    "forgot to call the rule."
    """

    def scope(self, queryset, user):
        raise NotImplementedError


def user_has_organisation_wide_read(user, *, all_roles=(HR_OFFICER, HR_ADMINISTRATOR)):
    """True where `user`'s assigned roles give organisation-wide read per
    §5's table (HR Officer, HR Administrator, by default). A module whose
    §5 row differs passes its own `all_roles`."""
    return user.groups.filter(name__in=all_roles).exists()


def user_has_payroll_wide_read(user):
    """Payroll Officer's §5 row: all rows, payroll fields only (NFR-019).
    Field-level restriction is the caller's job; this is the row half."""
    return user.groups.filter(name=PAYROLL_OFFICER).exists()


def user_is_system_administrator(user):
    """§5: System Administrator has no row-level access to any table this
    section scopes — the row exists so a caller does not have to special-case
    "no role at all" and "System Administrator" as different reasons to see
    nothing."""
    return user.groups.filter(name=SYSTEM_ADMINISTRATOR).exists()


__all__ = [
    'VisibilityRule',
    'user_has_organisation_wide_read',
    'user_has_payroll_wide_read',
    'user_is_system_administrator',
    'is_employee',
    'is_manager',
]
