# ADR-0010: Role model — assigned roles and derived roles

**Status:** Accepted
**Date:** 2026-07-15
**Bears on:** TBD-010 (Exact user roles and permissions)

## Context

Two role lists were in circulation and had diverged.

SRS §2.3 defines seven **user classes**: System Administrator; HR Administrator / HR Officer; Recruiter; Employee; Manager / Supervisor; Payroll Officer; Executive / Management User.

Project planning had referred to a different set: Super Admin; HR Admin; HR Officer; Manager; Employee; Recruiter; Payroll Officer — splitting the HR class in two, renaming the administrator, and omitting Executive entirely.

The divergence arose from conflating two distinct concepts. A **user class** is a requirements concept describing who uses the system. A **role** is an implementation concept in access control. They need not correspond one-to-one. One user class may be served by two roles at different privilege levels; conversely, some access follows from data rather than from any grant.

## Decision

**Eight roles serve the seven SRS user classes.**

**Six assigned roles**, implemented as Django groups:

| Role | Serves SRS class |
|---|---|
| System Administrator | §2.3.1 |
| HR Administrator | §2.3.2 |
| HR Officer | §2.3.2 |
| Recruiter | §2.3.3 |
| Payroll Officer | §2.3.6 |
| Executive | §2.3.7 |

**Two derived roles**, computed from data rather than granted:

| Role | Derivation | Serves SRS class |
|---|---|---|
| Employee | Holds an employee record whose employment status permits access | §2.3.4 |
| Manager | Has direct reports in the reporting structure | §2.3.5 |

**Supporting decisions:**

1. **Executive is retained.** Omitting it was scope reduction against an approved SRS.
2. **The HR class is served by two roles**, on separation-of-duties grounds.
3. **Roles are additive.** A user may hold several assigned roles; derived roles attach automatically.
4. **Separation-of-duties conflicts warn rather than block.**
5. **System Administrator is not a superuser.** It is a group with explicit permissions.
6. **The SRS name governs.** "System Administrator", not "Super Admin".

## Rationale

### Executive retained

SRS §2.3.7 defines the class with substance: read-only access to approved dashboards and analytics, summarised reports rather than operational access. HRMS-FR-049 to HRMS-FR-055 exist substantially to serve it. Dropping it would orphan those requirements and would constitute a change to an approved SRS, requiring revision and re-approval rather than silent omission. The role is also the least costly in the system, consisting largely of an absence of permission.

### HR class served by two roles

SRS §2.7 assumes that HR will define departments, roles, job titles, pay grades, leave types, and approval workflows. This is configuration, distinct from record maintenance, and it is not System Administrator work — §2.3.1 confines that role to technical configuration, accounts, permissions, and audit.

Placed in a single role, one account could both create an employee record (HRMS-FR-001, HRMS-BR-005) and define what that employee is paid (HRMS-FR-057). A single compromised or dishonest account would then suffice to introduce a fictitious employee and set their compensation, with payroll processing it downstream. Separating the roles requires two.

SRS §2.3.2 supports graduated access within the class: the HR class "should not automatically access technical system configuration unless assigned."

This is not a departure from the SRS. One user class served by two roles is consistent with the distinction drawn above.

### Employee and Manager derived

ADR-0005 established that facts already held in organisational data are not duplicated into access-control records, because the duplicate drifts. That reasoning applies to role membership itself.

**Manager.** HRMS-FR-008 requires the system to hold reporting relationships. Whether a person manages others is therefore already a fact in the data. As an assigned group, membership would require manual synchronisation with the organisation chart; a promotion with no corresponding grant leaves a manager unable to approve their own team's requests. Derived from direct reports, it cannot drift.

**Employee.** HRMS-BR-012 requires that terminated, resigned, and retired employees lose self-service access. Derivation from employment status makes this self-enforcing: a status change ends access with no group membership to remember to revoke. As an assigned group, HRMS-BR-012 would depend on a manual step performed at the moment it matters most.

### Roles additive, conflicts warned not blocked

Additivity is unavoidable: an HR Officer has their own payslip and takes leave. Because Employee and Manager are derived, they attach without grant.

For assigned roles, SRS §2.3.6 states that the Payroll Officer "**should** have restricted access separated from general HR roles." Under the SRS §1.2 conventions, *shall* is mandatory, *should* is recommended, *may* is optional. This is therefore a recommendation. Implementing it as a hard prohibition would enforce a *should* as a *shall*, and would be wrong for a small organisation in which one person legitimately performs both functions.

The system provides the capability to separate duties. The organisation decides whether to exercise it. HRMS-NFR-022 already requires permission changes to be logged, so the choice is on the record.

### System Administrator is not a superuser

Two grounds.

**The SRS forbids it.** HRMS-NFR-019 states that payroll data **shall** only be accessible to authorised payroll users — mandatory. SRS §2.3.1 confines the System Administrator to system configuration, user accounts, roles, permissions, and audit access. Employee records, payroll, and compensation are absent from that scope.

**Django's `is_superuser` would void the control.** The flag short-circuits permission checking: `has_perm()` returns `True` unconditionally without consulting any group or permission. A System Administrator carrying that flag would make HRMS-NFR-019 unenforceable at the permission layer — not weakened, but absent — while documentation claimed otherwise. Row-level scoping (ADR-0005) would still apply, since it is application code, but action-level control would be void.

Accordingly, `is_superuser` is reserved for a break-glass account: not used for routine administration, credentials held separately, use logged and reviewed.

**Escalation is detected, not prevented.** The System Administrator administers roles and can therefore grant themselves Payroll Officer. This is inherent to the function and cannot be designed away. The control is HRMS-NFR-022 permission-change logging, with the audit log append-only from the application, so that the party able to grant a permission cannot silently remove the record of having done so.

## Consequences

**Positive**

- Every SRS user class is served. No requirement is orphaned.
- HRMS-BR-012 and manager visibility are self-enforcing, following from data rather than from remembered administrative steps.
- Separation of duties is available to the organisation without being imposed on it.
- The privileged role has a bounded, stated scope consistent with HRMS-NFR-019.

**Negative**

- Derived roles are not Django's native model. Manager and Employee determination requires custom permission logic rather than group membership, and must be applied consistently.
- Derivation cannot express **delegation**: an acting manager, or approval while a manager is absent. This is not in scope per the SRS. Should it enter scope, it requires an explicit delegation record and an SRS amendment, not an adjustment to the derivation.
- Separation of duties depends on grant policy rather than system enforcement. A single user granted both HR roles reproduces the risk the split was intended to reduce. The warning and the audit record are the mitigations.
- Reserving `is_superuser` for break-glass requires an operational procedure that does not yet exist. Recorded in Section 11 of the IAM/RBAC design.

## Related

- ADR-0005 — access control via groups and queryset scoping. This ADR applies its reasoning to role membership.
- ADR-0004 — session authentication; HRMS-BR-012 revocation depends on it.
- `docs/07-iam-rbac.md` — the permission matrix and visibility rules.
