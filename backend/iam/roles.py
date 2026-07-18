"""The role model, `docs/07-iam-rbac.md` §2.

Assigned roles (§2.3) are Django groups, created once by
`0001_initial`'s data migration and never renamed here — `role_grant_request`
references a group by `auth_group.id`, per `docs/05-database-schema.md`
§4.3, precisely so a rename does not orphan a request.

Derived roles (§3) are not groups. `Employee` and `Manager` are computed
from the `employee` table, which Module 6 (Employee Management) has not
yet built. `is_employee`/`is_manager` below are the interface later
modules and this module's own visibility scaffolding call; until Module 6
exists there is no data to derive a "yes" from, so both return `False`
rather than raise — a user derives no role from a table that does not
exist yet, which is a true statement, not a placeholder.
"""

SYSTEM_ADMINISTRATOR = 'System Administrator'
HR_ADMINISTRATOR = 'HR Administrator'
HR_OFFICER = 'HR Officer'
RECRUITER = 'Recruiter'
PAYROLL_OFFICER = 'Payroll Officer'
EXECUTIVE = 'Executive'

ASSIGNED_ROLES = [
    SYSTEM_ADMINISTRATOR,
    HR_ADMINISTRATOR,
    HR_OFFICER,
    RECRUITER,
    PAYROLL_OFFICER,
    EXECUTIVE,
]

# `docs/07-iam-rbac.md` §7.3: a grant of any of these takes effect only on
# approval by an `iam.approve_role_grant` holder who is not the requester.
# All six assigned roles are privileged — the table lists every one of them.
PRIVILEGED_ROLES = [
    SYSTEM_ADMINISTRATOR,
    HR_ADMINISTRATOR,
    HR_OFFICER,
    PAYROLL_OFFICER,
    EXECUTIVE,
]


def is_employee(user):
    """§3.1: has an employee record whose status permits access. Always
    `False` until Module 6 supplies the `employee` table."""
    return False


def is_manager(user):
    """§3.2: has one or more direct reports. Always `False` until Module 6
    supplies the reporting-relationship data."""
    return False
