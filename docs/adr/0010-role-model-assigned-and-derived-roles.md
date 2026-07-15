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
5. **Self-grant of an assigned role is refused, and a privileged grant requires a second party.** A System Administrator cannot grant themselves any assigned role, and cannot complete a grant of a privileged role alone.
6. **System Administrator is not a superuser.** It is a group with explicit permissions.
7. **The SRS name governs.** "System Administrator", not "Super Admin".

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

**Self-grant is refused; privileged grants take two.** The System Administrator administers roles. An earlier draft of this record concluded that self-granting Payroll Officer was therefore inherent to the function and could not be designed away, leaving detection as the only control. That conclusion was wrong, and it mattered: HRMS-NFR-019 is a *shall*, and a route by which the holder of the administration function reaches payroll data at will leaves it unenforced. The `is_superuser` prohibition above closes one such route; this decision closes the direct grant route, which had been left open.

Two constraints, both at the grant path and neither configurable:

1. **The actor may not be the subject.** A grant of any assigned role where the granting user is the target user is refused. Self-grant is not a warning; it is not a permitted grant.
2. **A privileged grant requires an approver who is not the requester.** Payroll Officer, HR Administrator, HR Officer, Executive, and System Administrator are privileged. A System Administrator *requests* such a grant; it takes effect only when a holder of `iam.approve_role_grant` approves it, and the approver may not be the requester. This follows the mechanism already established for payroll finalisation at `docs/07-iam-rbac.md` §4.4: the permission exists, is granted to no role by default per deny-by-default, and the organisation designates its holder at deployment.

**This does not enforce a *should* as a *shall*.** SRS §2.3.6 recommends separating the Payroll Officer from general HR roles, and the decision above still leaves that combination available — an approver may grant it, and §6.1 of the IAM design warns rather than blocks, unchanged. What the constraint governs is *who may effect a grant*, not *which combinations are permissible*. Its basis is HRMS-NFR-019, which is a *shall*, not §2.3.6, which is not.

**What is enforced by code, what by policy, and what by neither.** Constraints 1 and 2 are code, at the single grant path, and hold regardless of role combination. They bind the grant of an **assigned role**, and they operate on the *authenticated identities* of the requester, the subject, and the approver. They presuppose what §4.4 and §7.3 of the IAM design already state: that assignment of a permission to a role — `iam.approve_role_grant` included — is deployment configuration and not a runtime operation reachable from the role administration function. The load-bearing policy element is that `iam.approve_role_grant` is **not** held by a System Administrator: this is a deployment-time grant like `payroll.approve_payroll_run`, and an organisation that grants it to the same person who administers roles has reduced the control back to detection. The system cannot prevent that choice, because there is no operating organisation to constrain (TBD-001); it can only refuse the default and log the grant.

Two routes remain open and are stated rather than assumed away:

- **Proxy account.** A System Administrator administers user accounts and may create one. That account reaches payroll only through a privileged grant, which constraint 2 refers to an approver who is not the requester. Account creation alone therefore confers nothing. **But constraint 2 closes this route only where the approver's identity is outside the requester's control, and under SRS §2.3.1 it is not.** The System Administrator administers every account, the designated approver's included. It can reset that approver's credentials and authenticate as them to approve its own request. Constraint 2 establishes that the requesting and approving identities differ; it cannot establish that they answer to different people. An earlier draft of this record called the proxy route closed. That was too strong: the route does not stand or fall on its own, it collapses into the credential-reset residual below, and it is closed exactly as far as that residual is — which is not at all.
- **Credential reset of an existing Payroll Officer.** SRS §2.3.1 places user accounts within the System Administrator's scope, so resetting an existing payroll user's credentials is within the role as the SRS defines it. That route changes no role membership and therefore triggers no grant approval; constraints 1 and 2 do not reach it. Nor, as the bullet above records, do they survive it: an actor able to authenticate as an arbitrary account can satisfy constraint 2 as readily as it can bypass the grant path altogether. This is the single residual, and both routes reduce to it. It is detected — HRMS-NFR-022 logs the record change and the subsequent login — and it is not prevented. Closing it requires either binding a second factor to payroll users, which HRMS-NFR-024 only asks be *considered*, or removing credential administration from the System Administrator, which contradicts SRS §2.3.1. Both are SRS-level questions and neither is settled here. This is the residual, and it is the honest limit of what this ADR enforces.

## Consequences

**Positive**

- Every SRS user class is served. No requirement is orphaned.
- HRMS-BR-012 and manager visibility are self-enforcing, following from data rather than from remembered administrative steps.
- Separation of duties is available to the organisation without being imposed on it.
- The privileged role has a bounded, stated scope consistent with HRMS-NFR-019, and two of the routes by which it could have reached payroll data unilaterally — `is_superuser`, and self-grant — are closed by construction rather than by instruction. This list is not exhaustive; the routes that run through account administration are not closed, and are stated in the rationale above rather than left to be discovered.
- The grant path is a single enforcement point. Both constraints sit on it, so they hold for every assigned role and every combination of roles without per-role special-casing.

**Negative**

- Derived roles are not Django's native model. Manager and Employee determination requires custom permission logic rather than group membership, and must be applied consistently.
- Derivation cannot express **delegation**: an acting manager, or approval while a manager is absent. This is not in scope per the SRS. Should it enter scope, it requires an explicit delegation record and an SRS amendment, not an adjustment to the derivation.
- Separation of duties between the two HR roles depends on grant policy rather than system enforcement. A single user granted both reproduces the risk the split was intended to reduce. The warning and the audit record are the mitigations; SRS §2.3.6 is a *should*, so this is deliberate.
- **The privileged-grant control is only as good as the `iam.approve_role_grant` grant.** An organisation that gives it to a System Administrator restores the position this decision was written to fix, and does so without any code change and without any warning the system can usefully issue. The default is the control; the default is also overridable by the party it constrains.
- **A grant now requires a second party, so a grant can now be blocked.** With `iam.approve_role_grant` held by one person who is unavailable, no privileged role can be granted at all. This is the correct failure direction, but it is a real operational cost and the organisation must hold the permission widely enough to function.
- Reserving `is_superuser` for break-glass requires an operational procedure that does not yet exist, and one cannot be written without an operating organisation (TBD-001). Recorded as an open item at `docs/07-iam-rbac.md` §8.
- The credential-reset route to payroll data is detected and not prevented, and cannot be closed without an SRS revision. It also bounds constraint 2: the requirement for a second party holds against a requester who cannot authenticate as the approver, and the System Administrator can. The constraint is therefore worth what the residual leaves it worth, and no more. See the rationale above.

## Related

- ADR-0005 — access control via groups and queryset scoping. This ADR applies its reasoning to role membership.
- ADR-0004 — session authentication; HRMS-BR-012 revocation depends on it.
- `docs/07-iam-rbac.md` — the permission matrix and visibility rules.
