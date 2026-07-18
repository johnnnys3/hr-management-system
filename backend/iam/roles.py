"""The role model, `docs/07-iam-rbac.md` §2.

Assigned roles (§2.3) are Django groups, created once by
`0001_initial`'s data migration and never renamed here — `role_grant_request`
references a group by `auth_group.id`, per `docs/05-database-schema.md`
§4.3, precisely so a rename does not orphan a request.

Derived roles (§3) are not groups. `Employee` and `Manager` are computed
from the `employee` and `reporting_relationship` tables respectively.
Module 6 (Employee Management) built `employee`, so `is_employee` below
derives from it. Module 8 (Reporting Structure) built
`reporting_relationship`, so `is_manager` now derives from it too.
"""

from employees.models import Employee
from reporting_structure.models import ReportingRelationship

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


EMPLOYEE_ACCESS_PERMITTED_STATUSES = [
    Employee.STATUS_ACTIVE,
    Employee.STATUS_ON_LEAVE,
    Employee.STATUS_SUSPENDED,
]


def is_employee(user):
    """§3.1: has an employee record whose status permits access.
    HRMS-BR-012: terminated, resigned, and retired employees lose access."""
    if not (user and user.is_authenticated):
        return False
    employee = getattr(user, 'employee', None)
    return employee is not None and employee.employment_status in EMPLOYEE_ACCESS_PERMITTED_STATUSES


def is_manager(user):
    """§3.2: has one or more direct reports, and their own employment status
    permits access — `docs/05-database-schema.md` §4.6's derivation query,
    applying the same permitting-status test §3.1 applies to the subject,
    here to the manager, so a manager whose own access has ended does not
    go on deriving the role from a `reporting_relationship` row that has
    not yet been reassigned."""
    if not (user and user.is_authenticated):
        return False
    employee = getattr(user, 'employee', None)
    if employee is None or employee.employment_status not in EMPLOYEE_ACCESS_PERMITTED_STATUSES:
        return False
    return ReportingRelationship.objects.filter(manager_employee_id=employee.pk).exists()
