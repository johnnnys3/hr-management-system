# HRMS Context

The Human Resource Management System is a web-based platform for managing employee records, recruitment, onboarding, payroll, self-service, leave, compensation, benefits, and HR reporting for a Ghana-based organisation. It replaces manual HR processes: spreadsheets, paper files, email-based approvals, and disconnected payroll records.

The authoritative requirements are in the Software Requirements Specification (`docs/01-srs.md`), at v1.1. Where this document and the SRS disagree, the SRS governs and this document is wrong.

## Glossary

Use these terms as defined. Where the glossary marks a term as avoided, do not use it — including in issue titles, test names, module names, and commit messages.

### Domain

**Employee** — a person with an employment relationship to the organisation. Holds a unique employee ID (HRMS-BR-001), belongs to a department (HRMS-BR-002), and has exactly one employment status (HRMS-BR-003). Distinct from **User**.

**User** — an account that authenticates against the system. Most employees have a user account; not every user is an employee. Access control attaches to the user; employment facts attach to the employee. *Avoid* using "user" to mean "employee" or vice versa; they are separate records with separate lifecycles.

**Candidate** — a person under consideration for a role. A candidate is not an employee. Conversion occurs only on offer acceptance with onboarding initiated (HRMS-BR-013). *Avoid* "applicant" as a distinct concept; it is the same thing as candidate.

**Employment status** — the state of an employee's relationship with the organisation. Terminated, resigned, and retired employees lose self-service access unless policy permits otherwise (HRMS-BR-012). *Avoid* "active/inactive" as a synonym; status is a defined set, not a boolean.

**Reporting relationship** — the link between an employee and their reporting manager (HRMS-FR-008). Every employee should have one unless they are top management (HRMS-BR-004). This structure is the source of truth for manager visibility; see **visibility rule**.

**Manager** — an employee with others reporting to them. Managers see only their assigned team (HRMS-BR-007, HRMS-NFR-018). "Manager" is a relationship derived from the reporting structure as well as a role; both senses are in use and context distinguishes them.

**Pay grade** — a defined compensation band. Distinct from **salary structure**, which is the framework of grades.

**Compensation record** — a dated record of an employee's compensation. Changes are stored as history, never overwritten (HRMS-DR-010).

**Payroll run** — one execution of payroll for a period, over active employees. Cannot be finalised without approval from an authorised user (HRMS-BR-008). Produces payslips and a bank transfer file.

**Payslip** — the per-employee statement produced by a payroll run. Employees view only their own (HRMS-BR-006).

**PAYE** — Pay As You Earn, the statutory income tax deduction.

**SSNIT** — Social Security and National Insurance Trust.

**Tier 1** — mandatory basic national pension contribution. **Tier 2** — mandatory occupational pension contribution. **Tier 3** — voluntary provident or personal pension contribution.

**Statutory rates** — the PAYE and SSNIT rates in force. These change. They are configuration, never constants in code (SRS §2.5).

**Leave balance** — remaining entitlement, tracked per leave type. Approved leave reduces it (HRMS-BR-010); rejected leave does not (HRMS-BR-011).

**Leave type** — annual, sick, maternity, study, or organisation-defined (HRMS-FR-066).

**Job requisition** — an approved request to hire. Distinct from **job posting**, which is the published advertisement arising from it.

**Audit log** — the record of sensitive actions (HRMS-NFR-013, HRMS-BR-015): login attempts, record changes, payroll actions, approvals, permission changes (HRMS-NFR-022). One store, named once as a data entity by SRS §6.1.

**Audit history** — not a second store. It is HRMS-FR-010's name for a filtered read of the **audit log** where the target is an employee record, and record changes are one of the five categories above. The two terms are used interchangeably by the SRS and are distinguished here because they read as siblings: a second store would put employee-record changes outside the single database grant on which audit immutability rests (`docs/07-iam-rbac.md` §7.3).

### Architecture

**Module** — one functional area, implemented as one Django application. Domain logic lives in service code within the module, kept apart from HTTP and persistence concerns so it can be lifted into another project. See ADR-0001.

**Visibility rule** — the row-level access predicate for a module, expressed as a queryset scoping method (`visible_to(user)`). Derives visibility from organisational data rather than from stored permission records. Every endpoint returning employee-scoped data obtains its queryset through one. Omitting it is a disclosure defect. See ADR-0005.

**Role** — a permission-bearing identity governing *which actions* a user may perform. Distinct from **user class**, and distinct from **visibility rule**, which governs *which rows* a user may see. Action and row control are both required; neither substitutes for the other.

**User class** — a requirements concept from SRS §2.3 describing who uses the system. Not the same as a role, and not one-to-one with roles: eight roles serve the seven user classes. *Avoid* using the two terms interchangeably; conflating them is what allowed the role list to drift from the SRS.

**Assigned role** — a Django group, granted by a System Administrator and logged. Six exist: System Administrator, HR Administrator, HR Officer, Recruiter, Payroll Officer, Executive. Additive — a user may hold several. **No one may grant an assigned role to themselves**, and a privileged grant additionally requires an approver who is not the requester — an approver who must hold a second factor under HRMS-NFR-024, or the constraint separates identities without separating parties. See `docs/07-iam-rbac.md` §7.3.

**Derived role** — computed from existing data, never granted, cannot drift. Two exist: **Employee** (has an employee record whose employment status permits access — which makes HRMS-BR-012 self-enforcing) and **Manager** (has direct reports). See `docs/07-iam-rbac.md` §3.

*Note on naming:* SRS §2.3.1 says "System Administrator"; earlier project planning said "Super Admin". The SRS name governs. Earlier planning also omitted the Executive class; that omission was rejected, as removing a user class is a scope reduction requiring SRS revision.

**System Administrator** — administers accounts, roles, permissions, audit, and system configuration. Holds **no** payroll, compensation, or employee record access; HRMS-NFR-019 is a *shall*. Implemented as a group with explicit permissions, **never** as Django's `is_superuser` — that flag short-circuits every permission check and would make HRMS-NFR-019 unenforceable. `is_superuser` is reserved for a break-glass account. The role cannot reach payroll data by granting itself Payroll Officer either: self-grant is refused, and a privileged grant needs an approver who is not the requester. It cannot reach payroll data by resetting a payroll user's credentials and authenticating as them either: HRMS-NFR-024 is a *shall* as of SRS v1.1, so payroll users hold a second factor this role can neither enrol, reset, disable, nor bypass. It can still reset the password — SRS §2.3.1 is unchanged — but a password no longer authenticates the account. One narrow route remains: the privileged-grant constraint distinguishes **identities**, and acquires the force of distinct **parties** only where the approver is itself within HRMS-NFR-024's scope. An approver outside that scope can still be reset and impersonated, so who holds `iam.approve_role_grant` is a deployment condition, not a free choice. See `docs/07-iam-rbac.md` §7.

## Constraints that shape the design

**Money is exact.** Statutory deductions use `Decimal` in application code and `NUMERIC` in the database, end to end. Binary floating point is not used for monetary values anywhere. See ADR-0003.

**Payroll finalisation is atomic.** It writes across payslip, deduction, and history records. A partial payroll is a corrupt payroll. See ADR-0003, ADR-0006.

**Access is denied by default.** Both action-level and row-level. See ADR-0005.

**Data residency is unresolved and consequential.** Ghana's Data Protection Act 2012 (Act 843) requires a controller to register with the Data Protection Commission and to disclose the countries it transfers personal data to. Whether it further restricts *where* employee personal data may reside — and on what test — is an open question of legal interpretation for counsel, not a settled constraint; the Act sets out no adequacy regime of the GDPR's kind. Do not restate it as one. The architecture defers the hosting decision rather than pre-empting it in either direction. See ADR-0009.

**Statutory rates change.** Rate tables are versioned configuration. Payroll history must remain reproducible against the rates in force at the time it ran.

## Scope boundary

SRS §6.4 places the following out of scope. Treat a request touching these as scope change requiring SRS revision, not as a feature:

biometric and facial-recognition attendance; advanced AI recruitment screening; learning management; performance appraisal; complex shift scheduling; ERP and accounting integration; automatic tax filing with government portals; direct integration with all Ghanaian banks; employee loan management; travel and expense management; disciplinary case management; union management; multi-country payroll; chatbot support; native mobile application.

Mobile is web-first by decision (SRS §2.5, §6.4). This bears on ADR-0004: session cookie authentication assumes no native mobile client. Should that change, revisit the ADR rather than work around it.

## Related documents

- `docs/01-srs.md` — Software Requirements Specification v1.1. Authoritative.
- `docs/03-tech-stack.md` — technology selection.
- `docs/adr/` — architecture decision records.
- `docs/agents/` — issue tracker and domain documentation conventions.
