# HRMS Context

The Human Resource Management System is a web-based platform for managing employee records, recruitment, onboarding, payroll, self-service, leave, compensation, benefits, and HR reporting for a Ghana-based organisation. It replaces manual HR processes: spreadsheets, paper files, email-based approvals, and disconnected payroll records.

The authoritative requirements are in the Software Requirements Specification (`docs/01-srs.md`). Where this document and the SRS disagree, the SRS governs and this document is wrong. `docs/01-srs.pdf` is a rendering of v1.0 retained for distribution; where the two disagree, the Markdown governs and the PDF is stale.

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

**Audit log** — the record of sensitive actions (HRMS-NFR-013, HRMS-BR-015): login attempts, record changes, payroll actions, approvals, permission changes (HRMS-NFR-022).

### Architecture

**Module** — one functional area, implemented as one Django application. Domain logic lives in service code within the module, kept apart from HTTP and persistence concerns so it can be lifted into another project. See ADR-0001.

**Visibility rule** — the row-level access predicate for a module, expressed as a queryset scoping method (`visible_to(user)`). Derives visibility from organisational data rather than from stored permission records. Every endpoint returning employee-scoped data obtains its queryset through one. Omitting it is a disclosure defect. See ADR-0005.

**Role** — a permission-bearing identity governing *which actions* a user may perform. Distinct from **user class**, and distinct from **visibility rule**, which governs *which rows* a user may see. Action and row control are both required; neither substitutes for the other.

**User class** — a requirements concept from SRS §2.3 describing who uses the system. Not the same as a role, and not one-to-one with roles: eight roles serve the seven user classes. *Avoid* using the two terms interchangeably; conflating them is what allowed the role list to drift from the SRS.

**Assigned role** — a Django group, granted by a System Administrator and logged. Six exist: System Administrator, HR Administrator, HR Officer, Recruiter, Payroll Officer, Executive. Additive — a user may hold several. **No one may grant an assigned role to themselves**, and a privileged grant additionally requires an approver who is not the requester. See `docs/07-iam-rbac.md` §7.3.

**Derived role** — computed from existing data, never granted, cannot drift. Two exist: **Employee** (has an employee record whose employment status permits access — which makes HRMS-BR-012 self-enforcing) and **Manager** (has direct reports). See `docs/07-iam-rbac.md` §3.

*Note on naming:* SRS §2.3.1 says "System Administrator"; earlier project planning said "Super Admin". The SRS name governs. Earlier planning also omitted the Executive class; that omission was rejected, as removing a user class is a scope reduction requiring SRS revision.

**System Administrator** — administers accounts, roles, permissions, audit, and system configuration. Holds **no** payroll, compensation, or employee record access; HRMS-NFR-019 is a *shall*. Implemented as a group with explicit permissions, **never** as Django's `is_superuser` — that flag short-circuits every permission check and would make HRMS-NFR-019 unenforceable. `is_superuser` is reserved for a break-glass account. The role cannot reach payroll data by granting itself Payroll Officer either: self-grant is refused and a privileged grant needs a second party. One route remains open — the role administers accounts (SRS §2.3.1) and can reset a payroll user's credentials; that is logged, not blocked, and closing it is an SRS question. See `docs/07-iam-rbac.md` §7.

## Constraints that shape the design

**Money is exact.** Statutory deductions use `Decimal` in application code and `NUMERIC` in the database, end to end. Binary floating point is not used for monetary values anywhere. See ADR-0003.

**Payroll finalisation is atomic.** It writes across payslip, deduction, and history records. A partial payroll is a corrupt payroll. See ADR-0003, ADR-0006.

**Access is denied by default.** Both action-level and row-level. See ADR-0005.

**Data residency is unresolved and consequential.** Ghana's Data Protection Act 2012 (Act 843) constrains where employee personal data may reside, and the position is not settled. The architecture defers the hosting decision rather than pre-empting it. See ADR-0009.

**Statutory rates change.** Rate tables are versioned configuration. Payroll history must remain reproducible against the rates in force at the time it ran.

## Scope boundary

SRS §6.4 places the following out of scope. Treat a request touching these as scope change requiring SRS revision, not as a feature:

biometric and facial-recognition attendance; advanced AI recruitment screening; learning management; performance appraisal; complex shift scheduling; ERP and accounting integration; automatic tax filing with government portals; direct integration with all Ghanaian banks; employee loan management; travel and expense management; disciplinary case management; union management; multi-country payroll; chatbot support; native mobile application.

Mobile is web-first by decision (SRS §2.5, §6.4). This bears on ADR-0004: session cookie authentication assumes no native mobile client. Should that change, revisit the ADR rather than work around it.

## Related documents

- `docs/01-srs.md` — Software Requirements Specification v1.0. Authoritative.
- `docs/01-srs.pdf` — rendering of the SRS at v1.0, retained for distribution. Not authoritative.
- `docs/03-tech-stack.md` — technology selection.
- `docs/adr/` — architecture decision records.
- `docs/agents/` — issue tracker and domain documentation conventions.
