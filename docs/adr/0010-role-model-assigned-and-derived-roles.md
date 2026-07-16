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

The routes that run through account administration are stated rather than assumed away. Both turn on one question, and it is not the question constraint 2 settles: not whether the requester and the approver are distinct *identities*, but whether the party that administers credentials can present as either of them. SRS v1.1 changed the answer.

- **Proxy account.** A System Administrator administers user accounts and may create one. That account reaches payroll only through a privileged grant, which constraint 2 refers to an approver who is not the requester. Account creation alone therefore confers nothing. **But constraint 2 closes this route only where the approver's identity is outside the requester's control.** An earlier draft of this record called the proxy route closed. That was too strong, and under SRS §2.3.1 alone it remains too strong: the System Administrator administers every account, the designated approver's included, and can reset that approver's credentials and authenticate as them to approve its own request. Constraint 2 establishes that the requesting and approving identities differ; on its own it cannot establish that they answer to different people. The route does not stand or fall by itself — it reduces to the credential-reset route below, and it is closed exactly as far as that route is.
- **Credential reset of an existing Payroll Officer.** SRS §2.3.1 places user accounts within the System Administrator's scope, so resetting an existing payroll user's credentials is within the role as the SRS defines it. That route changes no role membership and therefore triggers no grant approval; constraints 1 and 2 do not reach it, and an actor able to authenticate as an arbitrary account could satisfy constraint 2 as readily as it could bypass the grant path altogether. **This route is closed as of SRS v1.1.** HRMS-NFR-024 is now a *shall*: multi-factor authentication is required for administrators and payroll users on every authentication; the second factor is bound to the individual account holder; and no role that administers accounts, credentials, roles, or permissions may enrol, reset, disable, or bypass it. Resetting a password does not by itself restore access to an account whose second factor is enrolled. The System Administrator may still reset the password — §2.3.1 is unchanged — but a password no longer authenticates the account. The reset stays logged under HRMS-NFR-022, now as a detected failure rather than a successful route.

**This record has been wrong here before, and the correction is the requirement's, not this ADR's.** An earlier version of this section called the credential reset the single residual and the honest limit of what this ADR enforces, and recorded that closing it would take either a second factor bound to payroll users — which HRMS-NFR-024 then only asked be *considered* — or the removal of credential administration from the System Administrator, contradicting SRS §2.3.1. That was accurate against the SRS as it then stood, and it named the right two options. SRS v1.1 took the first of them and promoted HRMS-NFR-024 to a *shall*. `docs/02-project-plan.md` §11 question 8 carried the same matter as open and was resolved at v1.2 on the same ground. So the reasoning above is not superseded; its condition was met. What is stale is only the statement of the requirement's force, and it is corrected rather than quietly rewritten, because a reader of this ADR needs to know that the residual narrowed when the SRS moved and not because the design found a better argument.

**What survives is narrower, and it is a deployment condition rather than a design flaw.** HRMS-NFR-024 binds authentication, and only for the accounts within its scope. Constraint 2 therefore acquires the force of a second *party* exactly where the approver is itself within that scope, and retains only the force of a second *identity* where the approver is outside it. An approver outside the scope can still be reset and impersonated, and the proxy route above is open against them. This is no longer a limit the design cannot pass: it is a condition on operating the system — **the holder of `iam.approve_role_grant` must be an account within HRMS-NFR-024's scope**. It is recorded as such in `CONTEXT.md` under "Deployment conditions" and at `docs/07-iam-rbac.md` §7.3. It is bounded by a question the SRS does not settle: HRMS-NFR-024 says "administrators and payroll users", which covers System Administrator and Payroll Officer unambiguously and leaves HR Administrator and Executive unsettled (`docs/07-iam-rbac.md` §8).

Two things HRMS-NFR-024 does not reach, and this ADR does not claim to close. It does not bind the break-glass account above, whose control is custody rather than authentication. It does not bind the operational ceiling: a party holding database owner, host, or backup credentials reaches payroll data without authenticating at all (`docs/07-iam-rbac.md` §7.3).

## Consequences

**Positive**

- Every SRS user class is served. No requirement is orphaned.
- HRMS-BR-012 and manager visibility are self-enforcing, following from data rather than from remembered administrative steps.
- Separation of duties is available to the organisation without being imposed on it.
- The privileged role has a bounded, stated scope consistent with HRMS-NFR-019, and `is_superuser` and self-grant are closed by construction; credential reset is closed for covered accounts, and the proxy route is closed only when `iam.approve_role_grant` is held by an account within HRMS-NFR-024's scope. What survives is one narrow opening, stated in the rationale above rather than left to be discovered.
- **The residual narrowed because a requirement changed, and the change is recorded rather than absorbed.** The credential-reset route was open on this ADR's own analysis, and that analysis named binding a second factor to payroll users as one of the two things that would close it. SRS v1.1 did exactly that. The prior position is left visible in the rationale, so the record shows the design holding a known gap open until the SRS closed it.
- The grant path is a single enforcement point. Both constraints sit on it, so they hold for every assigned role and every combination of roles without per-role special-casing.

**Negative**

- Derived roles are not Django's native model. Manager and Employee determination requires custom permission logic rather than group membership, and must be applied consistently.
- Derivation cannot express **delegation**: an acting manager, or approval while a manager is absent. This is not in scope per the SRS. Should it enter scope, it requires an explicit delegation record and an SRS amendment, not an adjustment to the derivation.
- Separation of duties between the two HR roles depends on grant policy rather than system enforcement. A single user granted both reproduces the risk the split was intended to reduce. The warning and the audit record are the mitigations; SRS §2.3.6 is a *should*, so this is deliberate.
- **The privileged-grant control is only as good as the `iam.approve_role_grant` grant.** An organisation that gives it to a System Administrator restores the position this decision was written to fix, and does so without any code change and without any warning the system can usefully issue. The default is the control; the default is also overridable by the party it constrains.
- **A grant now requires a second party, so a grant can now be blocked.** With `iam.approve_role_grant` held by one person who is unavailable, no privileged role can be granted at all. This is the correct failure direction, but it is a real operational cost and the organisation must hold the permission widely enough to function.
- Reserving `is_superuser` for break-glass requires an operational procedure that does not yet exist, and one cannot be written without an operating organisation (TBD-001). Recorded as an open item at `docs/07-iam-rbac.md` §8.
- **Constraint 2 is worth a second *party* only where the approver holds a second factor.** HRMS-NFR-024 closes the credential-reset route for the accounts it covers, but it bounds constraint 2 rather than removing the bound: against an approver outside the requirement's scope, the System Administrator can still reset and impersonate, and the constraint separates identities without separating parties. Who holds `iam.approve_role_grant` is therefore a deployment condition, not a free choice — recorded in `CONTEXT.md` under "Deployment conditions" and at `docs/07-iam-rbac.md` §7.3. Which roles the requirement covers is itself unsettled beyond System Administrator and Payroll Officer, and is open at `docs/07-iam-rbac.md` §8.
- **The control bought against HRMS-NFR-019 has an availability cost.** A second factor no administering role can reset is exactly what closed the route, and it is also why a payroll user who loses that factor cannot be restored by the people who administer their account. Recovery needs an approver who does not administer credentials, the system does not notify them (ADR-0011), and payroll cannot run meanwhile against an HRMS-NFR-005 bound. The mechanism is in the release; the procedure is the organisation's. Recorded in `CONTEXT.md` under "Deployment conditions".

## Related

- ADR-0005 — access control via groups and queryset scoping. This ADR applies its reasoning to role membership.
- ADR-0004 — session authentication; HRMS-BR-012 revocation depends on it.
- `docs/07-iam-rbac.md` — the permission matrix and visibility rules.
