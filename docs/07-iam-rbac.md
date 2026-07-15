# IAM and Role-Based Access Control Design

**Human Resource Management System**

| | |
|---|---|
| Version | 1.2 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | July 2026 |
| Status | Approved |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | July 2026 | Initial IAM and RBAC design; reconciles role list against SRS §2.3 user classes | 1.0 |
| John Kessie | 2026-07-15 | §7.3 revised: self-grant of an assigned role is refused and a privileged grant requires an approver who is not the requester, closing the grant route to payroll data left open against HRMS-NFR-019. The credential-reset route is recorded as detected-not-prevented and referred to the project owner as an SRS question. §8 gains the `iam.approve_role_grant` holder, the break-glass procedure, and the credential-reset question as open items; the break-glass item was previously cited to a section that did not exist. §9 traceability updated | 1.1 |
| John Kessie | 2026-07-15 | §7.3 audit immutability re-based from a Django permission to a PostgreSQL grant. The prior guarantee — that no role holds update or delete permission on audit records — did not bind the §7.2 break-glass account, which holds no role and bypasses `has_perm()` entirely. The application's database role now holds `INSERT` and `SELECT` only. The operational ceiling above that grant is stated, and an off-host audit sink is recorded in §8 against TBD-003 | 1.2 |

---

## 1. Introduction

### 1.1 Purpose

This document defines the identity and access control design for the HRMS: the role model, how roles are assigned or derived, what each role may do, which records each may see, and the constraints governing privileged access.

It partially resolves TBD-010 (exact user roles and permissions). Section 8 records what remains open.

### 1.2 Scope

This document covers authorisation. Authentication mechanism is recorded in ADR-0004 and `docs/03-tech-stack.md` §8.1. The access control mechanism — groups for actions, queryset scoping for rows — is recorded in ADR-0005. This document applies those decisions to a concrete role model.

### 1.3 Governing Principle

**Access is denied by default.** A permission not granted is absent. A record not matched by a visibility rule is not returned.

### 1.4 Related Documents

| Document | Content |
|---|---|
| `docs/01-srs.md` | Software Requirements Specification v1.0. Authoritative |
| `docs/01-srs.pdf` | Rendering of the SRS at v1.0, for distribution. Not authoritative |
| `docs/03-tech-stack.md` | Technology selection |
| `CONTEXT.md` | Domain glossary |
| ADR-0004 | Session cookie authentication |
| ADR-0005 | Groups for actions, queryset scoping for rows |

---

## 2. User Classes and Roles

### 2.1 The Distinction

SRS §2.3 defines seven **user classes** — a requirements concept describing who uses the system. A **role** is an implementation concept carrying permissions. The two need not correspond one to one.

Conflating them is the source of the discrepancy this document resolves: project planning had drifted to a partly different list of seven items, mixing the two concepts.

### 2.2 Reconciliation

Every SRS user class is served. No class is removed; none is added.

| SRS §2.3 user class | Served by role | Note |
|---|---|---|
| §2.3.1 System Administrator | System Administrator | Assigned |
| §2.3.2 HR Administrator / HR Officer | HR Administrator **and** HR Officer | One class, two roles. See §2.4 |
| §2.3.3 Recruiter | Recruiter | Assigned |
| §2.3.4 Employee | Employee | Derived. See §3 |
| §2.3.5 Manager / Supervisor | Manager | Derived. See §3 |
| §2.3.6 Payroll Officer | Payroll Officer | Assigned |
| §2.3.7 Executive / Management User | Executive | Assigned |

Eight roles serve seven user classes.

The earlier planning list omitted Executive. That omission is not adopted: SRS §2.3.7 defines the class with substance, and the Phase 3 reporting requirements (HRMS-FR-049 to HRMS-FR-055) exist substantially to serve it. Removing a user class would be a scope reduction requiring SRS revision, not a design choice.

The planning list used "Super Admin". The SRS name **System Administrator** is used throughout, since the SRS is authoritative and no purpose is served by documentation and implementation disagreeing on a term.

### 2.3 Assigned and Derived Roles

| Role | Kind |
|---|---|
| System Administrator | Assigned |
| HR Administrator | Assigned |
| HR Officer | Assigned |
| Recruiter | Assigned |
| Payroll Officer | Assigned |
| Executive | Assigned |
| Employee | **Derived** |
| Manager | **Derived** |

**Assigned** roles are Django groups. Membership is granted by a System Administrator and logged (HRMS-NFR-022).

**Derived** roles are computed from existing data. They are not groups and are never granted. See §3.

### 2.4 Why HR Administrator and HR Officer Are Separate

SRS §2.3.2 names the class "HR Administrator / HR Officer". The separation into two roles serves that one class with graduated access, and is a separation-of-duties control.

SRS §2.7 assumes HR will define departments, roles, job titles, pay grades, leave types, and approval workflows. That is configuration, distinct from record maintenance, and it is not System Administrator work — SRS §2.3.1 confines that role to technical configuration, accounts, permissions, and audit.

Were configuration and record maintenance held by one role, a single account could create an employee record (HRMS-FR-001) and define the pay grade structure (HRMS-FR-057). That is the ghost-employee fraud path, reachable by one compromised or dishonest account.

The split follows SRS §4.6 exactly: its stimulus sequence has the **HR Officer** assigning an employee to a pay grade — the transaction — while defining the grades themselves is governance. Preparation and framework are held apart.

SRS §2.3.2 anticipates graduation: the class "should not automatically access technical system configuration unless assigned". That sentence presupposes that access within HR is not flat.

**The two roles are disjoint by default, not nested.** HR Administrator is not a superset of HR Officer. Nesting would restore the single-account fraud path and defeat the split. Where one person genuinely performs both jobs, both roles are granted explicitly — see §6.

---

## 3. Derived Roles

Derived roles are computed from data the system already holds. They are not granted and cannot drift from the facts they express. This applies the reasoning of ADR-0005 to the role model itself.

### 3.1 Employee

**Derivation:** the user has an associated employee record **and** that employee's employment status permits system access.

**Rationale.** HRMS-BR-012 requires that terminated, resigned, and retired employees lose self-service access unless policy permits otherwise. Employment status is data. Deriving the role from it makes HRMS-BR-012 self-enforcing: status changes to Terminated, access ends on the next request.

Were Employee a granted group, HRMS-BR-012 would depend on someone remembering to revoke membership — a manual step, omitted on precisely the occasions when it matters most.

### 3.2 Manager

**Derivation:** the employee has one or more direct reports, per the reporting relationships required by HRMS-FR-008.

**Rationale.** The organisational structure already records who manages whom. A granted Manager group would duplicate that fact and drift from it. On promotion, an unsynchronised group leaves the new manager unable to approve their team's requests; the workflow breaks while the org chart says otherwise.

### 3.3 Known Ceiling

Derivation cannot express **delegation** — an acting manager, or approval authority while a manager is on leave. No such requirement exists in the SRS, so it is out of scope.

Should delegation enter scope, it requires a delegation record with its own validity period and audit trail. It is not a patch on the derivation, and it should enter through SRS revision rather than as an implementation improvisation.

---

## 4. Permission Model

### 4.1 Two Layers

Both layers apply to every request. Neither substitutes for the other.

**Action-level** — may this role perform this operation? Django groups and permissions.

**Row-level** — among records of a type this role may access, which may this user see? Queryset scoping via a visibility rule per module (ADR-0005).

A role permitted to view employee records still sees only the rows its visibility rule returns.

### 4.2 Permission Matrix

Legend: **C** create, **R** read, **U** update, **A** approve, **—** no access, **‡** grantable, not fixed by this design — see §4.4. Row scope in §5.

| Module | Sys Admin | HR Admin | HR Officer | Recruiter | Payroll Officer | Executive | Manager | Employee |
|---|---|---|---|---|---|---|---|---|
| Employee records (FR-001–012) | — | R, U status | C, R, U | — | R (payroll fields) | — | R | R own |
| HR configuration — departments, job titles, leave types, approval workflows (§2.7) | — | C, R, U | R | R | R | — | — | — |
| Employee documents (FR-006) | — | R | C, R, U | — | — | — | — | R own |
| Recruitment (FR-013–024) | — | R | R | C, R, U | — | — | — | — |
| Requisition approval (FR-014) | — | A | — | — | — | — | — | — |
| Onboarding (FR-023–024) | — | R | C, R, U | R | — | — | — | — |
| Self-service profile (FR-025–027) | — | — | R, U | — | — | — | — | R, U own |
| Payslips (FR-028, FR-044) | — | — | — | — | C, R | — | — | R own |
| Payroll processing (FR-035–046, FR-048) | — | — | — | — | C, R, U | — | — | — |
| Payroll finalisation approval (FR-047, BR-008) | — | ‡ | ‡ | ‡ | ‡ | ‡ | — | — |
| Salary structures, pay grades (FR-056–057) | — | C, R, U | R | — | R | — | — | — |
| Assign employee to pay grade (§4.6) | — | — | C, R, U | — | — | — | — | — |
| Compensation history (FR-058) | — | R | R | — | R | — | — | — |
| Bonus cycles, allowances, benefits (FR-059–061) | — | C, R, U | R | — | R | — | — | R own |
| Leave requests (FR-063) | — | R | R, U | — | — | — | R | C, R own |
| Leave approval (FR-064) | — | — | — | — | — | — | A | — |
| Leave balances, history (FR-065, FR-070) | — | R | R, U | — | — | — | R | R own |
| Leave calendar (FR-071) | — | R | R | — | — | — | R | — |
| Reports and dashboards (FR-049–055) | — | R | R | — | R (payroll cost) | R | R | — |
| User accounts, roles, permissions (§2.3.1) | C, R, U | — | — | — | — | — | — | — |
| Audit log (NFR-013, NFR-022) | R | — | — | — | — | — | — | — |
| System configuration (§2.3.1) | C, R, U | — | — | — | — | — | — | — |

### 4.3 Notes on the Matrix

**System Administrator holds no HR or payroll access.** See §7.

**Executive is read-only and aggregate.** SRS §2.3.7 requires summarised reports, not full operational access. Executive reaches dashboards and analytics only, never an individual employee record or payslip. This satisfies HRMS-NFR-019 without exception.

**Recruiter has no payroll or compensation access**, per SRS §2.3.3.

**Payroll Officer reads only the employee fields payroll requires** — identifiers, employment status, compensation, statutory numbers, bank details. Not recruitment records, not documents unrelated to payroll. HRMS-NFR-019 restricts payroll data to payroll users; the converse restriction applies equally.

**Leave approval is Manager-only at action level.** HR Officer may update a leave request (correction, cancellation) but may not approve it. HRMS-BR-009 requires leave to follow the approval workflow; permitting HR to approve would provide a bypass.

### 4.4 Payroll Finalisation Approval

HRMS-FR-047 and HRMS-BR-008 require approval before payroll is finalised. The SRS does not state which role approves, and **this design does not fix one.**

Who signs off payroll is an organisational authority decision, not a system design decision. It varies legitimately: executive, finance director, HR administrator, or a designated approver, depending on the organisation's delegation of financial authority. The SRS cannot say because TBD-001 leaves the organisation undetermined, and this document should not invent an answer the organisation owns.

No new mechanism is required. The permission model in §4.1 already expresses this:

- A permission, `payroll.approve_payroll_run`, gates finalisation.
- **It is granted to no role by default**, per the deny-by-default principle in §1.3. Payroll cannot be finalised until the organisation grants it, which is the correct failure mode: HRMS-BR-008 holds from the first deployment.
- The organisation grants it to whichever role its policy designates, at deployment. The grant is logged (HRMS-NFR-022) and appears in the matrix above wherever it has been made.

**One constraint is not grantable and is enforced by the system: the approver must not be the user who initiated the payroll run.** A preparer approving their own work is not a control, and HRMS-BR-008 exists to be one. This is enforced regardless of which role holds the permission, and regardless of any combination of roles a user may hold under §6.

Self-approval attempts are rejected and logged.

---

## 5. Visibility Rules

Each rule is a queryset scoping method on the module's manager. **Every endpoint returning employee-scoped data obtains its queryset through one.** Omitting the call returns unscoped data; this is a disclosure defect of the most serious kind and is treated as a blocking review finding (ADR-0005).

| Role | Employee records | Payslips | Leave requests | Reports |
|---|---|---|---|---|
| Employee | Own only (NFR-017) | Own only (BR-006) | Own only | — |
| Manager | Direct reports (BR-007, NFR-018) | — | Direct reports' | Team-level (FR-032) |
| HR Officer | All | — | All | Organisation-wide |
| HR Administrator | All | — | All | Organisation-wide |
| Recruiter | — | — | — | — |
| Payroll Officer | All, payroll fields (NFR-019) | All | — | Payroll cost |
| Executive | — | — | — | Aggregate only |
| System Administrator | — | — | — | — |

**Manager scope is direct reports.** HRMS-BR-007 states managers view employees *assigned to them*, which is read as those reporting directly to the manager. Visibility does not extend transitively down the reporting chain: a manager two levels above an employee does not see that employee, nor their leave requests, nor their records.

Team-level reports (HRMS-FR-032) are computed over the same set. A manager's reports cover their direct reports and no one else.

Should chain visibility ever be required, it is an SRS clarification with a real disclosure consequence — it would widen every manager's view of salary-adjacent data — and not an implementation adjustment.

---

## 6. Multiple Roles

**Assigned roles are additive.** A user may hold several. Derived roles attach automatically and independently; they require no grant and never conflict.

Additivity is unavoidable. An HR Officer has their own payslip and takes leave. A Payroll Officer takes leave. An HR Administrator may manage a team. Each is simultaneously an Employee, and possibly a Manager, by derivation.

### 6.1 Separation of Duties: Warn, Do Not Block

SRS §2.3.6 states the Payroll Officer "**should** have restricted access separated from general HR roles."

Per SRS §1.2, **should** denotes a recommendation; **shall** denotes a requirement. The system therefore permits the combination, warns at grant time, and logs it. Enforcing a *should* as a *shall* would over-implement the requirement and would be wrong for a small organisation where one person legitimately performs both jobs.

Combinations warned at grant time:

| Combination | Concern |
|---|---|
| Payroll Officer + any HR role | SRS §2.3.6. Payroll data separated from general HR |
| HR Administrator + HR Officer | Defeats §2.4. One account may define a pay grade structure and create the employee assigned to it |
| System Administrator + any operational role | §2.3.1 confines this role to technical administration. Combining grants an account both the data and the power to alter who may see it |

The system provides the *capability* to separate duties. The organisation decides whether to exercise it. The audit log records the decision.

---

## 7. Privileged Access

### 7.1 System Administrator Is Not Unrestricted

SRS §2.3.1 confines the role to system configuration, user accounts, roles, permissions, and audit access. Employee records, payroll, and compensation are absent from that list.

**HRMS-NFR-019 is mandatory:** payroll data *shall* only be accessible to authorised payroll users. A System Administrator is not one. The role receives no payroll, compensation, or employee record access.

### 7.2 The `is_superuser` Prohibition

**The System Administrator role is a Django group with explicit permissions. It must not be implemented as `is_superuser`.**

Django's `is_superuser` flag short-circuits every permission check: `has_perm()` returns `True` unconditionally, consulting no group and no permission. An account carrying it would pass every action-level control in §4.2, rendering HRMS-NFR-019 unenforceable at that layer — not weakened, absent.

Row-level scoping (§5) is application code and is not bypassed by the flag, so record visibility would still hold. Action gating would not. The result would be a role able to execute payroll while this document states it cannot.

`is_superuser` is reserved for a **break-glass account**: not used for routine administration, credentials held under separate control, use logged and reviewed.

### 7.3 Escalation: Self-Grant Is Prevented, the Residual Is Detected

A System Administrator manages roles. Unconstrained, the role could therefore grant itself Payroll Officer and reach payroll data at will, which **HRMS-NFR-019 forbids as a *shall***. §7.2 closes the `is_superuser` route to the same outcome. This section closes the grant route.

**Two constraints on the grant path. Neither is configurable.**

| Constraint | Enforcement |
|---|---|
| A grant of an assigned role where the granting user is the target user is **refused** | System. Not a warning, not an override |
| A grant of a **privileged** role takes effect only on approval by a holder of `iam.approve_role_grant` who is **not** the requester | System. Applies to Payroll Officer, HR Administrator, HR Officer, Executive, System Administrator |

`iam.approve_role_grant` follows §4.4 exactly: the permission exists, is **granted to no role by default** per the deny-by-default principle of §1.3, and the organisation designates its holder at deployment. It is **not** granted to System Administrator. A privileged grant is therefore a request by one party and an approval by another, both logged under HRMS-NFR-022.

**This does not enforce §2.3.6's *should* as a *shall*.** §6.1 stands unchanged: Payroll Officer combined with an HR role is still permitted, still warned, still logged, and an approver may still grant it. These constraints govern *who may effect a grant*, not *which combinations are permissible*. Their basis is HRMS-NFR-019, a *shall*.

**What this does not close.**

| Route | Position |
|---|---|
| **Proxy account.** A System Administrator creates an account and grants it Payroll Officer | Closed by the second constraint. The grant still needs an approver who is not the requester. Account creation alone confers no payroll access |
| **Credential reset.** A System Administrator resets an existing Payroll Officer's credentials and authenticates as them | **Open. Detected, not prevented.** SRS §2.3.1 places user accounts in this role's scope, so the route is within the role as the SRS defines it. It changes no role membership, so no grant approval is triggered. HRMS-NFR-022 logs the record change and the login; nothing blocks it |

The credential-reset route cannot be closed by this design. Closing it needs either a second factor bound to payroll users — HRMS-NFR-024 asks only that MFA be *considered*, so it is not currently required — or the removal of credential administration from the System Administrator, which contradicts SRS §2.3.1. Both are SRS questions. Recorded in §8.

**Detection, for what the constraints do not reach.** HRMS-NFR-022 requires permission changes to be logged. Refused self-grants, privileged grant requests, approvals, and credential resets on accounts holding a privileged role are each recorded with actor, target, role, and timestamp, and are reportable events.

Detection is only a control if the record survives the party it incriminates. That is the subject of the rest of this section.

**Audit immutability is enforced by the database, not by a permission.**

An earlier version of this design stated that the audit log is append-only because no role, System Administrator included, holds update or delete permission on audit records. That is not sufficient, and §7.2 is the reason why. The break-glass account carries `is_superuser`, which makes `has_perm()` return `True` unconditionally. It holds no role, so a control expressed as "no role has this permission" does not bind it. It could delete audit records through the Django admin or the ORM, and the design would not have noticed the hole because the guarantee was stated in terms of the one mechanism `is_superuser` bypasses.

Django permissions are therefore the wrong layer for this guarantee. The control:

| Control | Mechanism | Binds `is_superuser`? |
|---|---|---|
| The application's database role holds `INSERT` and `SELECT` on audit tables, and **no `UPDATE` and no `DELETE`** | PostgreSQL grant (ADR-0003) | **Yes.** `is_superuser` short-circuits `has_perm()`, a Python check. It confers no SQL privilege. An admin or ORM delete is refused by the database |
| Schema changes to audit tables run as a separate migration role whose credentials the application process does not hold | Deployment configuration | Yes, for the running application |
| No role, break-glass included, is granted Django `change`/`delete` permission on audit models | Django permission | No — defence in depth only, not the guarantee |

The first row is the guarantee. The third is retained because it makes the intent visible in the code and removes the affordance from the admin interface, but it is not what enforces immutability and this design no longer claims it is.

HRMS-NFR-010 establishes the pattern for payroll history; it applies with greater force to the audit trail, since the account able to grant permissions must not be able to erase the evidence of having done so.

**The ceiling.** A holder of the database owner or PostgreSQL superuser credentials, or of host or backup access, can still alter audit rows; a grant does not bind the party who can rewrite grants. No application-layer design closes this, and this document does not claim to. It is an operational control — custody of database credentials separate from application credentials, and audit events shipped off-host to storage the application's deployment cannot rewrite. Shipping to an external append-only sink is the stronger control and is not specifiable while the hosting target is open (TBD-003, ADR-0009); it is recorded in §8 for resolution alongside it.

Log retention and review cadence depend on the operating organisation and remain open (TBD-009).

---

## 8. Open Items

| Item | Status |
|---|---|
| TBD-010 — exact user roles and permissions | **Resolved** by this document. The role model, derivation rules, permission matrix, visibility rules, and privileged access constraints are settled |
| Payroll finalisation approver | **Resolved as a deployment-time grant** (§4.4), not a design-time choice. The permission exists and is granted to no role by default; the organisation designates the holder. Self-approval is blocked by the system regardless |
| Manager visibility depth | **Resolved** (§5). Direct reports only; no transitive chain visibility |
| TBD-009 — document retention policy | **Open.** Bears on §7.3 audit log retention |
| Off-host audit sink | **Open, tied to TBD-003.** §7.3 enforces audit immutability by database grant, which binds the application and the break-glass account but not a holder of database owner, host, or backup credentials. Shipping audit events off-host to storage the deployment cannot rewrite closes that ceiling and cannot be specified until the hosting target is (ADR-0009) |
| `iam.approve_role_grant` holder | **Deferred to deployment** (§7.3), not a design-time choice, on the same reasoning as §4.4. The permission is granted to no role by default and **must not be granted to a System Administrator** — doing so reduces the §7.3 control to detection. Requires an operating organisation (TBD-001) |
| Break-glass account procedure | **Open.** §7.2 reserves `is_superuser` for break-glass but no operational procedure exists for credential custody, invocation, or review. Not writable without an operating organisation (TBD-001) |
| Credential reset as a route to payroll data | **Open. Requires an SRS decision, not a design decision** (§7.3). SRS §2.3.1 places user accounts within the System Administrator's scope, so the role can reset a Payroll Officer's credentials and authenticate as them. Closing it requires either MFA bound to payroll users — HRMS-NFR-024 asks only that it be *considered* — or narrowing §2.3.1. Both are SRS revisions. Referred to the project owner |
| Delegation of manager authority | **Out of scope.** Not in the SRS. See §3.3 |
| Role grant configuration at deployment | **Deferred to deployment**, by design. Which users hold which assigned roles, and who holds `payroll.approve_payroll_run`, are organisational decisions requiring an operating organisation (TBD-001) |

---

## 9. Requirements Traceability

| Requirement | Addressed by |
|---|---|
| HRMS-NFR-014 (authentication required) | ADR-0004 |
| HRMS-NFR-016 (role-based access control) | §2, §4 |
| HRMS-NFR-017 (employees access own records) | §4.2, §5 |
| HRMS-NFR-018 (managers access assigned team) | §4.2, §5 |
| HRMS-NFR-019 (payroll data restricted) | §4.2, §4.3, §5, §7.1, §7.2, §7.3 |
| HRMS-NFR-022 (log permission changes) | §2.3, §6.1, §7.3 |
| HRMS-NFR-013 (audit log) | §4.2, §7.3 |
| HRMS-BR-005 (only authorised HR modify master records) | §4.2 |
| HRMS-BR-006 (employees view own payslips) | §4.2, §5 |
| HRMS-BR-007 (managers view assigned employees) | §5 |
| HRMS-BR-008 (payroll approval) | §4.4 |
| HRMS-BR-009 (leave approval workflow) | §4.3 |
| HRMS-BR-012 (terminated employees lose access) | §3.1 |
| HRMS-BR-014 (sensitive data to authorised roles) | §4.2, §5 |
| HRMS-BR-015 (critical actions logged) | §7.3 |
| HRMS-FR-008 (reporting relationships) | §3.2 |
| HRMS-FR-027 (employees cannot edit salary, job title, department, status, manager) | §4.2 |
| HRMS-FR-032 (managers view team reports) | §4.2, §5 |
| SRS §2.3.1–§2.3.7 (user classes) | §2.2 |
