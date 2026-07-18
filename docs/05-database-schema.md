# Database Schema

**Human Resource Management System**

| | |
|---|---|
| Version | 1.1 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-16 |
| Status | Draft — pending owner acceptance at M3 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-16 | Initial database schema, closing milestone M3 | 1.0 |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.5's Dashboard renumbering (module 5 → 14; modules 6–14 → 5–13).** §4's module numbering below is still v1.4. Reconcile at M3 sign-off per plan §5.3 | 1.0 (unreconciled) |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.6's Employee Management/Departments swap (modules 5 ↔ 6 in the plan's numbering; modules 6 ↔ 7 below, still v1.4).** This document is the source of the finding: §4.4's `employee.department_id` is a NOT NULL foreign key into §4.5's `department`, but the build order these headings sit in still builds Employee Management before Departments. Reconciliation will swap §4.4 and §4.5's ordering and heading numbers; §4.6 Reporting Structure does not move — its foreign keys point into `employee`, not the reverse, so it has no schema-level reason to precede Employee Management. Reconcile at M3 sign-off per plan §5.3 | 1.0 (unreconciled) |
| John Kessie | 2026-07-18 | **Reconciled with `docs/02-project-plan.md` v1.6, per the two rows above.** §4.4 and §4.5 swap content (Departments now §4.4/module 5, Employee Management now §4.5/module 6), matching the build order; §4.6 Reporting Structure does not move. Every other module number in §4 is renumbered to v1.6 throughout (Recruitment 8, Onboarding 9, Notification 10, Employee/Manager Self-Service 11/12, Leave Management 13). No table, column, constraint, or requirement mapping changes — this is the renumbering the two rows above already called for, done. Filed as DOC-007 | 1.1 |

---

## 1. Introduction

### 1.1 Purpose

This document designs the relational schema for the Human Resource Management System: the tables, columns, types, and constraints that store the data `docs/01-srs.md` §6.1 requires, organised against the module boundaries `docs/04-system-architecture.md` already fixed.

It does not decompose the system into modules, which `docs/04-system-architecture.md` has done; it does not select technology, which `docs/03-tech-stack.md` and ADR-0001 to ADR-0011 have settled; and it does not specify the API surface, which `docs/06-api-contracts.md` will. Where this document restates a decision from an earlier one, it is carrying that decision into DDL, not re-deciding it.

### 1.2 Intended Audience

Developers writing Django models and migrations against this schema, and the project owner reviewing it before API design begins against it.

### 1.3 Relationship to Prior Documents

This document is downstream of five documents it does not revise:

- **`docs/01-srs.md`** (v1.1) — the requirement set, and specifically §6.1's list of 27 data entities, §6.2's ten data validation rules (HRMS-DR-001 to HRMS-DR-010), and the business rules of §5.5. Authoritative; where this document and the SRS disagree, the SRS governs.
- **`CONTEXT.md`** — the domain glossary. Where a term is defined there (Employee vs. User, compensation record, audit log vs. audit history, mail dispatch vs. notification), this document uses it as defined rather than restating the distinction.
- **`docs/03-tech-stack.md`** (v1.0) and **ADR-0003** — PostgreSQL, `NUMERIC` for money paired with `Decimal`, check and unique constraints at the storage layer, `JSONB` for versioned statutory rate tables. This document applies those choices; it does not re-argue them.
- **`docs/04-system-architecture.md`** (v1.0) — the twenty-module catalog, the dependency graph, and the two cross-cutting patterns (audit, mail dispatch/notification) this schema is designed against. §4's "Consumes" column and §3.3's visibility-rule seam are the basis for every foreign key and every module boundary below.
- **`docs/07-iam-rbac.md`** (v1.6) and **ADR-0005, ADR-0010, ADR-0011** — produced out of order (plan §5.3) and binding on this document in two specific ways this document must carry rather than choose: the Employee and Manager derived roles depend on employment status and reporting relationship existing as first-class columns (§3.3 below), and the payroll run record must enforce that its approver is not its initiator (§3.5 below). Per plan §5.3, `docs/07-iam-rbac.md` is re-read against this document as part of M3 sign-off; §9 records the result.

### 1.4 Scope

In scope: a table for every module in `docs/04-system-architecture.md` §4 that owns data (§4 below), the columns and constraints each table carries, the two schema obligations `docs/07-iam-rbac.md` fixes (§3.3, §3.5), and how the ten data validation rules of SRS §6.2 map to storage-layer constraints (§6).

Out of scope, per `CONTEXT.md` "Scope boundary" and SRS §6.4: no table exists for biometric attendance, AI recruitment screening, learning management, performance appraisal, complex shift scheduling, ERP/accounting integration, automatic tax filing, direct bank integration, loan management, travel and expense management, disciplinary case management, union management, multi-country payroll, or chatbot support. A request that would need one is a scope change requiring SRS revision, not a schema addition.

This document does not reopen the three module placements plan §11 closed (Audit at 1, Compensation and Benefits at 15, mail dispatch/Notification at 2/11), the visibility-rule pattern, or the role model. Where a table's existence depends on one of those placements, it cites the placement rather than re-arguing it.

---

## 2. Conventions

### 2.1 Naming and Types

Table and column names are `snake_case`, singular table names (`employee`, not `employees`). This document gives logical table names; Django's migration system derives the physical name from the app label of the module that owns the table (ADR-0001, ADR-0002) and this document does not restate that mechanical mapping per table.

Primary keys are surrogate `BIGINT` identity columns (Django's `BigAutoField`, the project default under Django 3.2+), listed as `id` and omitted from the column tables below unless a table's primary key is not the default surrogate. Natural keys required by the SRS (HRMS-BR-001's employee ID, HRMS-DR-002's email) are separate `UNIQUE` constraints on their own columns, not the primary key — a surrogate key does not change when a business identifier is corrected, which an exposed natural key forces on every referencing row.

Two columns (`user_account.email`, `candidate.email`, §4.2, §4.7) use `CITEXT` for case-insensitive comparison, so that `HRMS-DR-002`'s uniqueness rule and ordinary lookups do not depend on stored case. `CITEXT` is a contrib extension, not a built-in type: the first migration in the sequence must run `CREATE EXTENSION IF NOT EXISTS citext;` before any table using it is created. This is a migration-ordering requirement this document states rather than a deployment detail it defers, because a schema that names a type without naming its prerequisite is not fully specified.

### 2.2 Foreign Keys and Referential Action

Every foreign key specifies its `ON DELETE` behaviour explicitly; none is left to the database default. Two patterns cover this schema:

- **`RESTRICT`** where the referenced row is a business record whose disappearance would silently orphan history (an employee referenced by a payroll run, a department referenced by an employee). The application enforces status transitions (HRMS-FR-012, employment status change) rather than row deletion; §2.3 states why nothing in this schema hard-deletes a business record.
- **`SET NULL`** where the reference is optional and its absence is meaningful (an employee document's `uploaded_by`, once that user account is removed, becomes an anonymous historical upload rather than a broken row).

No foreign key in this schema uses `CASCADE` delete. Payroll, compensation, and audit data must survive the removal of the record that produced them (HRMS-NFR-010, HRMS-DR-010), and a cascading delete is the mechanism by which that guarantee would silently fail.

### 2.3 No Hard Delete on Business Records

Employee, payroll, compensation, leave, and recruitment rows are never deleted by the application; they transition status (`employment_status`, `payroll_run.status`, `leave_request.status`, and equivalents). This is not stated as a general principle to be re-derived per table: HRMS-NFR-010 forbids ordinary users from deleting payroll history outright, HRMS-DR-010 requires compensation to be stored as history, and HRMS-BR-012's derived-role mechanism (§3.3) depends on the employee row persisting through every employment status, including terminated. A schema that allowed deletion would need a second mechanism to reconstruct exactly the history these requirements already assume exists. Reference and configuration data (department, job title, leave type, pay grade) carry an `is_active` flag for the same reason: retiring a department must not orphan the employment history of everyone who once belonged to it.

### 2.4 Timestamps

Every table carries `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`, either under that name or as a domain-specific event timestamp that already marks the row's creation — a second, generic column beside one would duplicate rather than add information. `enrolled_at` (`second_factor`, `benefit_enrollment`), `requested_at` (`second_factor_recovery_request`, `role_grant_request`), `issued_at` (`offer_letter`), `started_at` (`onboarding_checklist`), `applied_at` (`candidate_application`), `awarded_at` (`bonus_award`), `generated_at` (`payslip`, `bank_transfer_file`), and `effective_from` (`reporting_relationship`) each serve this purpose on the one table where they are that table's defining event. Every table not named above states `created_at` explicitly in its column list.

Tables whose rows are mutated after creation additionally carry `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`, maintained by the application, unless a specific mutation timestamp already names the one transition the table permits (`disabled_at`, `decided_at`, `cancelled_at`, `completed_at`, and equivalents) — a generic `updated_at` beside a column that already states what changed says the same thing twice. Append-only tables (§3.4) and the audit log (§3.1) carry neither, because a column that invites an update on a row this schema forbids updating is a defect in the design, not a convenience.

### 2.5 Money

Every monetary column is `NUMERIC(14,2)` — two decimal places is sufficient for the Ghana cedi and every statutory scheme this system computes against, and `NUMERIC` (not `FLOAT` or `DOUBLE PRECISION`) is non-negotiable per ADR-0003 and `CONTEXT.md` "Money is exact." Application code pairs every such column with Python's `Decimal`; no monetary value crosses the Django ORM boundary as a native float at any point in this schema. A `currency` column accompanies monetary columns where the value could plausibly be non-cedi (compensation, payroll, offers); it is fixed at `GHS` by default and exists so a future multi-currency requirement is a data change, not a schema change — SRS §6.4 places multi-country payroll out of scope, so this is deliberately not built out further than that.

### 2.6 Versioned Configuration

Statutory rate tables use `JSONB`, per ADR-0003 and `CONTEXT.md` "Statutory rates change." §4.12 gives the one table this applies to. `JSONB` is not used elsewhere in this schema: the domain is otherwise relational and normalised, and reaching for `JSONB` on a column with a known, stable shape would trade constraint enforcement for a convenience this system does not need there.

---

## 3. Cross-Cutting Schema Obligations

Two concerns, per `docs/04-system-architecture.md` §3, are not confined to one module: each has an owned surface and per-module emission. A third and fourth obligation are schema-specific consequences of `docs/07-iam-rbac.md` that this document is not free to design differently. This section states all four once, so §4's catalog does not restate them per table.

### 3.1 Audit

**One table, module 1.** `audit_log` is the store SRS §6.1 names once ("Audit log") and `CONTEXT.md` confirms is the same store HRMS-FR-010 calls "audit history" — a filtered read where the target is an employee record, not a second table.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGINT | PK | |
| actor_user_id | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | Null for pre-authentication events (a failed login against a non-existent account) |
| category | TEXT | NOT NULL, CHECK IN ('login_attempt','record_change','payroll_action','approval','permission_change','second_factor_event') | The five HRMS-NFR-022 categories plus the HRMS-NFR-024 second-factor category `docs/07-iam-rbac.md` §7.3 adds |
| target_type | TEXT | NULL | The model the event concerns (e.g. `employee`, `payroll_run`); null for events with no single target (a login attempt) |
| target_id | BIGINT | NULL | Not a foreign key — the audit log must outlive the row it describes, including through hard-to-imagine cases (a target row's own deletion path, were one ever added) an FK constraint would block |
| action | TEXT | NOT NULL | e.g. `create`, `update`, `approve`, `refuse`, `login_success`, `login_failed`, `factor_enrolled` |
| detail | JSONB | NULL | Structured context (changed fields, before/after where the emitting module supplies it); §2.6's normalisation preference does not apply here — the audit log's contents are per-event by nature, not a fixed relational shape |
| occurred_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**No `updated_at`. No delete path in this schema.** Per `docs/07-iam-rbac.md` §7.3, the guarantee that makes this table immutable is a PostgreSQL grant — the application's database role holds `INSERT` and `SELECT` and neither `UPDATE` nor `DELETE` — not a Django permission and not a table-level mechanism this document specifies further. That grant, and the separate migration role §7.3 requires for schema changes to this table, are deployment configuration (module 20) and are restated here as a requirement this table's design must not obstruct: no column above is designed to be mutated after insert, and nothing in this table's shape requires the application role to hold `UPDATE`.

**Emission is per-module, absorbed.** §4's catalog does not repeat "writes to `audit_log`" on every row; a module emits into this table according to `docs/04-system-architecture.md` §4's "Emits audit" column, which this document does not restate.

### 3.2 Mail Dispatch and Notification

**Mail dispatch (module 2) owns no table.** It sends email off the request cycle (Celery task, template rendering, bounded retry) and, per ADR-0011, a delivery failure goes to application logs, never to a database table and never to the audit log. This document accordingly gives module 2 no entry in §4.

**Notification (module 10) owns one table.** SRS §6.1 does not name "Notification" among its 27 data entities — the SRS predates the module split ADR-0011 records — but `docs/04-system-architecture.md` §3.2 and §4 fix Notification as owning "the entity and the in-app feed," which this schema must therefore provide even though no SRS §6.1 row maps onto it directly. This is implementing an architecture decision already made, not adding scope; §7's traceability table marks it as such rather than silently folding it into an SRS row it does not belong to.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGINT | PK | |
| recipient_user_id | BIGINT | FK → user_account, ON DELETE RESTRICT | |
| category | TEXT | NOT NULL, CHECK IN ('pending_task','request_update') | SRS §3.4's two in-app kinds; HRMS-FR-033, HRMS-FR-034 |
| channel | TEXT | NOT NULL, CHECK IN ('in_app','email','both') | |
| subject | TEXT | NOT NULL | |
| body | TEXT | NOT NULL | |
| related_type | TEXT | NULL | Mirrors `audit_log.target_type`'s shape for the same reason: the referent varies by emitting module |
| related_id | BIGINT | NULL | Not a foreign key, for the same reason as `audit_log.target_id` |
| read_at | TIMESTAMPTZ | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

Visibility is `recipient_user_id = current user`, per `docs/04-system-architecture.md` §4's row for module 10 ("Employee/Manager: own notifications only"). No separate visibility rule is stated for it in §5 below: the predicate is a single equality, not a queryset traversal, and does not need the pattern §3.3 states for the modules that do.

### 3.3 The Derived-Role Columns

`docs/07-iam-rbac.md` §3 fixes two roles as derived rather than granted: **Employee**, from holding an employee record whose employment status permits access, and **Manager**, from having direct reports. `docs/04-system-architecture.md` §3.3 states that both derivations depend on module 6 and module 7 "existing with the right columns before any module can compute them" and names this a constraint on this document, not a choice it is free to make differently. This section is where that constraint is discharged.

**Employee derivation** reads `employee.employment_status` (§4.5). The column is `NOT NULL` (HRMS-BR-003, "every employee must have one employment status") and constrained to a fixed value set (§6, HRMS-DR rule table). Application code, not a database column, decides which values "permit access" — `docs/07-iam-rbac.md` §3.1 ties this to HRMS-BR-012 (terminated, resigned, and retired lose access "unless policy permits otherwise"), and "unless policy permits" is an organisational exception this schema does not attempt to encode as a second column; it is a derivation-time decision over the same enum, not a second source of truth to keep synchronised with it.

**Manager derivation** reads `reporting_relationship.manager_employee_id` (§4.6): an employee is a Manager if and only if at least one row in that table names them as manager **and their own `employee.employment_status` permits access** — the same permitting-status test §3.3 applies to the Employee derivation, applied here to the manager rather than the subject, so that a manager whose own access has ended does not go on deriving a role from a row that has not yet been reassigned. The query is given in full at §4.6. The table is owned by module 7, not embedded as a column on `employee`, because `docs/04-system-architecture.md` §4 gives Reporting Structure its own row, its own audit emission, and no dependency Employee Management has reason to carry; a `manager_id` column on `employee` would make Employee Management's table double as Reporting Structure's, which the module boundary does not do anywhere else in this schema.

Both tables are designed in §4.5 and §4.6 respectively; this section states the dependency the two designs jointly discharge, on the reasoning ADR-0005 already gives for derived scoping generally: a fact the organisational data already states is not copied into a second record that can drift from it.

### 3.4 Append-Only Compensation History

`CONTEXT.md` defines a compensation record as "a dated record of an employee's compensation... changes are stored as history, never overwritten" (HRMS-DR-010). `compensation_record` (§4.11) is designed so that a compensation change is a new row with a new `effective_from`, and never an `UPDATE` of `base_salary` or `pay_grade_id` on an existing row.

**This is enforced at the application layer, not by a database grant.** HRMS-DR-010 uses "should," not "shall" (SRS §1.2's convention), which is why this table does not receive the `INSERT`/`SELECT`-only database role restriction §3.1 gives the audit log — that mechanism is reserved for the one obligation the SRS states as mandatory. The distinction is deliberate: over-enforcing a *should* as a *shall* at the database grant level would make a legitimate future correction path (an erroneous compensation entry) unreachable by any means but a manual database intervention, which is a worse failure mode than the one the append-only convention exists to prevent. `is_superseded` and `effective_to` give the application an in-band way to mark a row historical without ever rewriting the value it recorded.

### 3.5 Payroll Approver-Not-Initiator

`docs/07-iam-rbac.md` §4.4 fixes one constraint as "not grantable and... enforced by the system: the approver must not be the user who initiated the payroll run," regardless of which role holds `payroll.approve_payroll_run`. Plan §5.3 names this a constraint belonging in this document.

`payroll_run` (§4.12) carries `initiated_by` and `approved_by` as two separate foreign keys to `user_account`, with:

```sql
CHECK (approved_by IS NULL OR approved_by <> initiated_by)
```

This is a database-level constraint, not only an application check, for the same reason `docs/07-iam-rbac.md` §4.4 states the rule applies "regardless of any combination of roles a user may hold": a self-approval attempt that reached the database despite an application-layer bug is rejected by the row itself. This is the one constraint in this schema doing double duty as both a data validation rule and a control `docs/07-iam-rbac.md` treats as security-bearing, and it is placed at the database layer for the reason ADR-0003 gives generally — "where application defects cannot bypass them."

---

## 4. Entity Catalog by Module

Tables are grouped by the module that owns them, in `docs/04-system-architecture.md` §4's numbering. A module not listed here owns no table: module 2 (Mail dispatch, §3.2), module 14 (Dashboard, reads modules 6/13/16/17 without a table of its own), modules 11 and 12 (Employee/Manager Self-Service, read Employee, Leave, and Notification without owning new storage), module 17 (Reports, aggregates read-only over modules 6/13/15/16), and modules 18 to 20 (Testing, UAT, Deployment — process modules, per `docs/04-system-architecture.md` §4's footnote, own no application data).

### 4.1 Module 1 — Audit

`audit_log` — designed in §3.1.

### 4.2 Module 3 — Authentication

**`user_account`.** The Django custom user model (`AUTH_USER_MODEL`, ADR-0002). SRS §6.1's "User account" entity. Distinct from Employee per `CONTEXT.md`: "most employees have a user account; not every user is an employee."

| Column | Type | Constraints | Notes |
|---|---|---|---|
| email | CITEXT | NOT NULL, UNIQUE | HRMS-DR-002 |
| password_hash | TEXT | NOT NULL | Django's password hasher output (ADR-0002); never plaintext |
| employee_id | BIGINT | FK → employee, ON DELETE SET NULL, UNIQUE, NULL | Nullable and unique: at most one user account per employee, and a user with no employee record is valid (`CONTEXT.md`) |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Deactivation, not deletion (§2.3) |
| last_login | TIMESTAMPTZ | NULL | |
| created_at, updated_at | — | — | §2.4 |

**`second_factor`.** HRMS-NFR-024's second factor. This document schemas the record of enrolment and its state; the cryptographic mechanism (TOTP, WebAuthn, or otherwise) is an implementation choice `docs/06-api-contracts.md` or a later ADR settles, not a decision this schema makes by naming a column `secret_ref`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| user_id | BIGINT | FK → user_account, ON DELETE RESTRICT, UNIQUE | One factor per account; HRMS-NFR-024 binds it to "the individual account holder" |
| secret_ref | TEXT | NOT NULL | Opaque reference to the enrolled credential; never the raw secret in this table |
| enrolled_at | TIMESTAMPTZ | NOT NULL | HRMS-NFR-024: "enrollment shall be performed by the account holder" |
| disabled_at | TIMESTAMPTZ | NULL | |
| last_verified_at | TIMESTAMPTZ | NULL | |

**`second_factor_recovery_request`.** HRMS-NFR-024: "recovery of a lost or unavailable second factor shall require approval by a user who does not administer user accounts or credentials." Unlike §3.5's payroll constraint, "does not administer credentials" is a role/permission property, not an identity comparison — it cannot be expressed as `approver_id <> requester_id` at the database layer, because the requester and a same-named administering approver are two different failure modes the SRS text does not conflate. This table records the request and its resolution; the eligibility check itself runs in application code against the permission grant `docs/07-iam-rbac.md` §8 defers to deployment.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| user_id | BIGINT | FK → user_account, ON DELETE RESTRICT | The account whose factor is lost |
| status | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','approved','denied') | |
| requested_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| approver_user_id | BIGINT | FK → user_account, ON DELETE RESTRICT, NULL | Eligibility enforced in application code, not by this schema (see above) |
| decided_at | TIMESTAMPTZ | NULL | |

### 4.3 Module 4 — RBAC / IAM

**Role and Permission map onto Django's built-in `auth_group`, `auth_permission`, `auth_group_permissions`, and the `user_account`–group membership table** (ADR-0002, ADR-0005). This document does not reinvent them: SRS §6.1 lists "Role" and "Permission" as data entities, and ADR-0005 already fixed action-level access as "Django's built-in groups and permissions," so a custom table here would be a second, drifting representation of a fact Django's auth app already stores. The six assigned roles (`docs/07-iam-rbac.md` §2.3) are six `auth_group` rows, seeded by a data migration, not five tables. The two derived roles (Employee, Manager) hold no group and therefore no row here at all — §3.3 is where they are actually computed, and their absence from this table is that decision's direct consequence, not an omission.

Two custom permissions this schema's constraints depend on being grantable — `payroll.approve_payroll_run` (§3.5) and `iam.approve_role_grant` (below) — are Django `Meta.permissions` entries on their owning models, which populate `auth_permission` through Django's migration framework rather than through a table this document defines.

**`role_grant_request`.** `docs/07-iam-rbac.md` §7.3 and ADR-0010 fix two constraints on the assigned-role grant path that are not deployment configuration but system mechanism: self-grant is refused, and a privileged role's grant takes effect only on approval by a holder of `iam.approve_role_grant` who is not the requester. Both are identity comparisons and both are expressible as database constraints, unlike §4.2's recovery-approver eligibility.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| requester_user_id | BIGINT | FK → user_account, ON DELETE RESTRICT | |
| subject_user_id | BIGINT | FK → user_account, ON DELETE RESTRICT | The user the role would be granted to |
| role_id | BIGINT | FK → auth_group, ON DELETE RESTRICT, NOT NULL | A foreign key rather than the group name as text — `auth_group.id` is stable across a rename, and a plain-text role column could reference a typo or a since-deleted group and still pass every constraint this table states. `NOT NULL` because a request with no role satisfies every other constraint here and still cannot be applied |
| status | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','approved','refused') | |
| approver_user_id | BIGINT | FK → user_account, ON DELETE RESTRICT, NULL | |
| requested_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| decided_at | TIMESTAMPTZ | NULL | |
| | | CHECK (requester_user_id <> subject_user_id) | Constraint 1, `docs/07-iam-rbac.md` §7.3: self-grant is refused, not warned |
| | | CHECK (approver_user_id IS NULL OR approver_user_id <> requester_user_id) | Constraint 2, same section: the approver is not the requester |

Neither check constraint can express the further condition `docs/07-iam-rbac.md` §7.3 and §8 leave as a deployment condition — that `iam.approve_role_grant`'s holder falls within HRMS-NFR-024's scope. That is a property of who holds the permission at a point in time, not of any row this table stores, and the IAM document is explicit that it is a deployment condition rather than a design one; this schema does not attempt to encode it.

### 4.4 Module 5 — Departments

**`department`.** HRMS-BR-002; SRS §2.7 HR configuration.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| name | TEXT | NOT NULL, UNIQUE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | §2.3 |
| created_at, updated_at | — | — | §2.4 |

**`job_title`.** HRMS-FR-003; grouped with Department under module 5 rather than Employee Management, on `docs/07-iam-rbac.md` §4.2's own grouping of "departments, job titles, leave types, approval workflows" as one HR-configuration permission row, and on plan §6.1's description of module 5's principal requirement as "SRS §2.7 HR configuration" rather than department alone.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| name | TEXT | NOT NULL, UNIQUE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | |
| created_at, updated_at | — | — | §2.4 |

### 4.5 Module 6 — Employee Management

**`employee`.** SRS §6.1's central entity; HRMS-FR-001 to HRMS-FR-004, HRMS-FR-009, HRMS-FR-011, HRMS-FR-012; HRMS-BR-001 to HRMS-BR-003.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_number | TEXT | NOT NULL, UNIQUE | HRMS-BR-001, HRMS-DR-001. Business identifier; §2.1 keeps it off the primary key |
| first_name | TEXT | NOT NULL | |
| last_name | TEXT | NOT NULL | |
| date_of_birth | DATE | NOT NULL, CHECK (date_of_birth < CURRENT_DATE) | HRMS-DR-003 |
| department_id | BIGINT | FK → department, ON DELETE RESTRICT, NOT NULL | HRMS-BR-002 |
| job_title_id | BIGINT | FK → job_title, ON DELETE RESTRICT, NOT NULL | HRMS-FR-003 |
| employment_status | TEXT | NOT NULL, CHECK IN ('active','on_leave','suspended','terminated','resigned','retired') | HRMS-BR-003; drives the Employee derivation, §3.3 |
| hire_date | DATE | NOT NULL | HRMS-DR-004: start date must be valid; enforced as not-null and not-future in application validation, since "valid" is not otherwise specified by the SRS |
| created_at, updated_at | — | — | §2.4 |

**`employment_history`.** HRMS-FR-004. One row per material change to an employee's job facts — status, department, job title, or reporting manager — kept apart from `reporting_relationship`'s current-state row (§4.6) because this table is a log and that one is not.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| event_type | TEXT | NOT NULL, CHECK IN ('hired','status_change','department_change','job_title_change','manager_change') | |
| effective_date | DATE | NOT NULL | |
| previous_value | JSONB | NULL | §2.6's normalisation preference does not apply: the shape of "previous value" varies by `event_type`, the same reasoning as `audit_log.detail` |
| new_value | JSONB | NOT NULL | |
| recorded_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| created_at | — | — | |

**`employee_document`.** HRMS-FR-006, HRMS-NFR-007, HRMS-NFR-008, HRMS-NFR-021. The file itself lives in S3-compatible object storage (ADR-0007, `docs/03-tech-stack.md` §5.2); this table holds only metadata and the storage key.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| document_type | TEXT | NOT NULL | |
| object_key | TEXT | NOT NULL, UNIQUE | ADR-0007: "stored object keys are generated rather than taken from client-supplied filenames" |
| file_name | TEXT | NOT NULL | Original filename, retained for display only, never used to derive `object_key` |
| content_type | TEXT | NOT NULL | Validated server-side by content inspection (ADR-0007), not trusted from this column alone |
| size_bytes | BIGINT | NOT NULL, CHECK (size_bytes > 0) | HRMS-NFR-008 enforces the upper bound in application code, where the configurable limit lives |
| uploaded_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| created_at | — | — | |

**`emergency_contact`.** HRMS-FR-007.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| name | TEXT | NOT NULL | |
| relationship | TEXT | NOT NULL | |
| phone | TEXT | NOT NULL | |
| email | TEXT | NULL | |
| is_primary | BOOLEAN | NOT NULL, DEFAULT false | |
| created_at, updated_at | — | — | §2.4 |

### 4.6 Module 7 — Reporting Structure

**`reporting_relationship`.** HRMS-FR-008, HRMS-BR-004. Current-state table: one row per employee who has a manager. An employee with none (top management, HRMS-BR-004's exception) has no row rather than a null-manager row, so that "no manager" and "manager not yet recorded" are not the same state expressed two ways.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT, UNIQUE | One current manager per employee |
| manager_employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| effective_from | DATE | NOT NULL | |
| | | CHECK (employee_id <> manager_employee_id) | An employee is not their own manager |

The Manager derivation (§3.3) is:

```sql
SELECT DISTINCT rr.manager_employee_id
FROM reporting_relationship rr
JOIN employee mgr ON mgr.id = rr.manager_employee_id
WHERE mgr.employment_status IN ('active', 'on_leave')
```

not a bare `SELECT DISTINCT manager_employee_id` — a manager whose own employment status no longer permits access must not continue deriving the role from a row that merely has not yet been reassigned. The join costs one line and reads a fact `employee` already states; a denormalised "is this manager row still valid" flag on `reporting_relationship` was rejected for the same reason ADR-0005 rejects duplicating any organisational fact into an access-control record — it would need to be kept synchronised with `employee.employment_status` by hand, and the synchronisation is exactly the step HRMS-BR-012 exists to make unnecessary.

**What this does not automate.** A terminated manager's direct reports keep their `reporting_relationship` row — pointing at a manager who can no longer act as one — until HR reassigns them; this table's own uniqueness constraint (one current row per employee) does not trigger that reassignment on its own. That is an operational gap in workflow automation, not in access control: the query above is what keeps the terminated manager from deriving the Manager role regardless, and the affected employees are left with a stale reporting line rather than a false grant of visibility to someone no longer entitled to it.

`docs/07-iam-rbac.md` §5 fixes manager visibility as direct reports only, not transitive — this table's shape (no chain, no self-referencing depth) is what makes that the only query it can express, which is the correct ceiling per that section rather than a limitation this schema works around.

### 4.7 Module 8 — Recruitment

**`job_requisition`.** HRMS-FR-013, HRMS-FR-014.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| department_id | BIGINT | FK → department, ON DELETE RESTRICT | |
| job_title_id | BIGINT | FK → job_title, ON DELETE RESTRICT | |
| requested_by | BIGINT | FK → user_account, ON DELETE RESTRICT | |
| status | TEXT | NOT NULL, DEFAULT 'draft', CHECK IN ('draft','pending_approval','approved','rejected','closed') | HRMS-FR-014: "approval statuses" |
| approved_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| created_at, updated_at | — | — | |

**`job_posting`.** HRMS-FR-015, distinct from requisition per `CONTEXT.md`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| requisition_id | BIGINT | FK → job_requisition, ON DELETE RESTRICT | |
| title | TEXT | NOT NULL | |
| description | TEXT | NOT NULL | |
| channel | TEXT | NOT NULL, CHECK IN ('internal','external') | |
| published_at | TIMESTAMPTZ | NULL | Set on publication; distinct from `created_at`, since a posting may be drafted before it is published |
| closed_at | TIMESTAMPTZ | NULL | |
| created_at, updated_at | — | — | §2.4 |

**`candidate`.** HRMS-FR-016. `CONTEXT.md`: "a candidate is not an employee." No foreign key to `employee` exists on this table; conversion (below) creates a new, independent `employee` row rather than mutating this one into it, which is what keeps the two entities from becoming the same row wearing two names.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| first_name | TEXT | NOT NULL | |
| last_name | TEXT | NOT NULL | |
| email | CITEXT | NOT NULL | Not unique — the same person may apply to more than one posting over time |
| phone | TEXT | NULL | |
| resume_object_key | TEXT | NULL | Same object-storage pattern as `employee_document` |
| created_at | — | — | |

**`candidate_application`.** HRMS-FR-017. Separates the candidate's identity from a specific application, since a candidate is not confined to one posting.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| candidate_id | BIGINT | FK → candidate, ON DELETE RESTRICT | |
| posting_id | BIGINT | FK → job_posting, ON DELETE RESTRICT | |
| stage | TEXT | NOT NULL, DEFAULT 'applied', CHECK IN ('applied','screening','interview','offer','hired','rejected') | |
| applied_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | — | — | |

**`interview`.** HRMS-FR-018, HRMS-FR-019.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| application_id | BIGINT | FK → candidate_application, ON DELETE RESTRICT | |
| interviewer_employee_id | BIGINT | FK → employee, ON DELETE SET NULL, NULL | |
| scheduled_at | TIMESTAMPTZ | NOT NULL | |
| status | TEXT | NOT NULL, DEFAULT 'scheduled', CHECK IN ('scheduled','completed','cancelled') | |
| feedback | TEXT | NULL | |
| created_at, updated_at | — | — | §2.4 |

**`offer_letter`.** HRMS-FR-020, HRMS-FR-021.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| application_id | BIGINT | FK → candidate_application, ON DELETE RESTRICT | |
| offered_salary | NUMERIC(14,2) | NOT NULL, CHECK (offered_salary >= 0) | §2.5; HRMS-DR-005's non-negative rule applies to any stored salary figure, not only `compensation_record` |
| offered_pay_grade_id | BIGINT | FK → pay_grade, ON DELETE RESTRICT, NULL | |
| status | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','accepted','rejected','withdrawn') | HRMS-FR-021 |
| issued_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| decided_at | TIMESTAMPTZ | NULL | |
| document_object_key | TEXT | NULL | Generated letter document, same storage pattern as §4.5 |

### 4.8 Module 9 — Onboarding

**`onboarding_checklist`.** HRMS-FR-022, HRMS-FR-023, HRMS-BR-013. Created only at conversion — HRMS-BR-013: "candidate records shall not become employee records until the offer is accepted and onboarding is initiated" — so this table's existence for a given employee is itself evidence that conversion has happened correctly, and a checklist row with no corresponding `employee` row is not a state this schema can represent.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT, UNIQUE | |
| application_id | BIGINT | FK → candidate_application, ON DELETE SET NULL, NULL | Traces back to the originating application where one exists |
| started_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| completed_at | TIMESTAMPTZ | NULL | |

**`onboarding_task`.** HRMS-FR-024.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| checklist_id | BIGINT | FK → onboarding_checklist, ON DELETE RESTRICT | |
| name | TEXT | NOT NULL | |
| is_required | BOOLEAN | NOT NULL, DEFAULT true | |
| status | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','in_progress','completed','skipped') | |
| completed_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| completed_at | TIMESTAMPTZ | NULL | |
| created_at | — | — | §2.4; no separate `updated_at` — `completed_at` is the one mutation this table's status enum permits |

### 4.9 Module 10 — Notification

`notification` — designed in §3.2.

### 4.10 Module 13 — Leave Management

**`leave_type`.** HRMS-FR-066. Grouped under Leave Management rather than module 5's HR-configuration tables, on plan §6.1's assignment of HRMS-FR-066 to module 13 specifically, distinct from the department/job-title grouping of §4.4.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| name | TEXT | NOT NULL, UNIQUE | |
| requires_approval | BOOLEAN | NOT NULL, DEFAULT true | |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | |
| created_at, updated_at | — | — | §2.4 |

**`leave_balance`.** HRMS-FR-065.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| leave_type_id | BIGINT | FK → leave_type, ON DELETE RESTRICT | |
| period_start | DATE | NOT NULL | |
| period_end | DATE | NOT NULL | |
| entitled_days | NUMERIC(6,2) | NOT NULL, CHECK (entitled_days >= 0) | |
| used_days | NUMERIC(6,2) | NOT NULL, DEFAULT 0, CHECK (used_days >= 0) | Decremented — correctly, increased in the sense of consumed — only on approval (HRMS-BR-010), never on request or rejection (HRMS-BR-011) |
| created_at, updated_at | — | — | §2.4 |
| | | UNIQUE (employee_id, leave_type_id, period_start) | |

**`leave_request`.** HRMS-FR-063, HRMS-FR-064, HRMS-BR-009 to HRMS-BR-011, HRMS-DR-006.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| leave_type_id | BIGINT | FK → leave_type, ON DELETE RESTRICT | |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| reason | TEXT | NULL | |
| status | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','approved','rejected','cancelled') | HRMS-BR-009 |
| approved_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| decided_at | TIMESTAMPTZ | NULL | |
| created_at | — | — | |
| | | CHECK (end_date >= start_date) | HRMS-DR-006 |

### 4.11 Module 15 — Compensation and Benefits

**`salary_structure`.** HRMS-FR-056. `CONTEXT.md`: "distinct from pay grade, which is the framework of grades" — this table is that framework; `pay_grade` rows belong to one.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| name | TEXT | NOT NULL, UNIQUE | |
| description | TEXT | NULL | |
| effective_from | DATE | NOT NULL | |
| created_at, updated_at | — | — | §2.4; `effective_from` is a business-effective date, not a row-creation timestamp, and does not substitute for it here the way it does on `reporting_relationship` |

**`pay_grade`.** HRMS-FR-057.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| salary_structure_id | BIGINT | FK → salary_structure, ON DELETE RESTRICT | |
| name | TEXT | NOT NULL | |
| min_salary | NUMERIC(14,2) | NOT NULL, CHECK (min_salary >= 0) | HRMS-DR-005 |
| max_salary | NUMERIC(14,2) | NOT NULL, CHECK (max_salary >= min_salary) | |
| created_at, updated_at | — | — | §2.4 |
| | | UNIQUE (salary_structure_id, name) | |

**`compensation_record`.** HRMS-FR-005, HRMS-FR-058, HRMS-DR-010. Append-only per §3.4.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| pay_grade_id | BIGINT | FK → pay_grade, ON DELETE RESTRICT, NULL | |
| base_salary | NUMERIC(14,2) | NOT NULL, CHECK (base_salary >= 0) | HRMS-DR-005 |
| currency | TEXT | NOT NULL, DEFAULT 'GHS' | §2.5 |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | NULL | Set when superseded; the row itself is never rewritten (§3.4) |
| is_superseded | BOOLEAN | NOT NULL, DEFAULT false | |
| recorded_by | BIGINT | FK → user_account, ON DELETE SET NULL, NULL | |
| created_at | — | — | |

**`bonus_cycle`** and **`bonus_award`.** HRMS-FR-059. Not separately named in SRS §6.1's entity list, which names "Compensation record" but not bonuses individually; included because HRMS-FR-059 ("the system shall manage bonus cycles") is a functional requirement this document must schema against, on the same reasoning §3.2 applies to Notification. §7 marks these as functional-requirement-derived rather than direct §6.1 entities.

| Table | Column | Type | Constraints | Notes |
|---|---|---|---|---|
| bonus_cycle | name | TEXT | NOT NULL | |
| bonus_cycle | period_start | DATE | NOT NULL | |
| bonus_cycle | period_end | DATE | NOT NULL | |
| bonus_cycle | status | TEXT | NOT NULL, DEFAULT 'open', CHECK IN ('open','closed') | |
| bonus_cycle | created_at, updated_at | — | — | §2.4 |
| bonus_award | bonus_cycle_id | BIGINT | FK → bonus_cycle, ON DELETE RESTRICT | |
| bonus_award | employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| bonus_award | amount | NUMERIC(14,2) | NOT NULL, CHECK (amount >= 0) | |
| bonus_award | awarded_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**`allowance_type`** and **`employee_allowance`.** HRMS-FR-060 ("Allowance" in SRS §6.1). Split between definition and per-employee assignment — the SRS names one entity, "Allowance," but §4.12's `payslip_line` is where an allowance's computed amount actually lands on a given payroll run; §7 traces "Allowance" across all three tables so the split is visible in one place rather than assumed.

| Table | Column | Type | Constraints | Notes |
|---|---|---|---|---|
| allowance_type | name | TEXT | NOT NULL, UNIQUE | |
| allowance_type | calculation_method | TEXT | NOT NULL, CHECK IN ('fixed','percentage_of_salary') | |
| allowance_type | amount_or_rate | NUMERIC(14,4) | NOT NULL, CHECK (amount_or_rate >= 0 AND (calculation_method <> 'percentage_of_salary' OR amount_or_rate <= 1)) | Higher precision than §2.5's default: a percentage rate (e.g. 0.0525) loses meaningful precision at two decimal places, where the resulting cedi amount, computed and stored on `payslip_line`, does not. Stored as a fraction, not a 0–100 percentage — the upper bound of 1 only binds `percentage_of_salary` rows; a `fixed` amount has no natural ceiling and keeps only the non-negative check |
| allowance_type | is_taxable | BOOLEAN | NOT NULL | Payroll (module 16) reads this when computing PAYE |
| allowance_type | created_at, updated_at | — | — | §2.4 |
| employee_allowance | employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| employee_allowance | allowance_type_id | BIGINT | FK → allowance_type, ON DELETE RESTRICT | |
| employee_allowance | amount_override | NUMERIC(14,2) | NULL, CHECK (amount_override IS NULL OR amount_override >= 0) | |
| employee_allowance | effective_from | DATE | NOT NULL | |
| employee_allowance | effective_to | DATE | NULL | |
| employee_allowance | created_at, updated_at | — | — | §2.4 |

**`benefit`** and **`benefit_enrollment`.** HRMS-FR-061.

| Table | Column | Type | Constraints | Notes |
|---|---|---|---|---|
| benefit | name | TEXT | NOT NULL, UNIQUE | |
| benefit | provider | TEXT | NULL | |
| benefit | cost | NUMERIC(14,2) | NULL, CHECK (cost IS NULL OR cost >= 0) | |
| benefit | created_at, updated_at | — | — | §2.4 |
| benefit_enrollment | employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | |
| benefit_enrollment | benefit_id | BIGINT | FK → benefit, ON DELETE RESTRICT | |
| benefit_enrollment | status | TEXT | NOT NULL, DEFAULT 'active', CHECK IN ('active','cancelled') | |
| benefit_enrollment | enrolled_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| benefit_enrollment | cancelled_at | TIMESTAMPTZ | NULL | |

### 4.12 Module 16 — Payroll

**`statutory_rate_table`.** SRS §6.1's "Deduction" entity, definitional half. `CONTEXT.md`: "statutory rates change... configuration, never constants in code." `JSONB` per §2.6.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| rate_type | TEXT | NOT NULL, CHECK IN ('paye','ssnit_tier1','ssnit_tier2','ssnit_tier3') | HRMS-FR-039 to HRMS-FR-042 |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | NULL | |
| rates | JSONB | NOT NULL | Bracket/threshold structure, shaped per rate type; deliberately not normalised into columns, since the bracket count and shape differ by `rate_type` and change independently of this schema (TBD-005) |
| created_at | — | — | §2.4; no `updated_at` — a rate change is a new row with a new `effective_from`, the same append-only convention §3.4 gives `compensation_record` |
| | | UNIQUE (rate_type, effective_from) | |

Payroll history must remain reproducible against the rates in force when it ran (`CONTEXT.md`); `payslip_line` (below) stores the computed amount, not a reference back to this table alone, so a later rate change cannot retroactively alter a finalised payslip's stated deduction.

**`payroll_run`.** HRMS-FR-035 to HRMS-FR-038, HRMS-FR-047, HRMS-FR-048, HRMS-BR-008. The approver-not-initiator constraint of §3.5.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| period_start | DATE | NOT NULL | |
| period_end | DATE | NOT NULL | |
| status | TEXT | NOT NULL, DEFAULT 'draft', CHECK IN ('draft','calculated','pending_approval','approved','finalized','failed') | |
| initiated_by | BIGINT | FK → user_account, ON DELETE RESTRICT, NOT NULL | |
| approved_by | BIGINT | FK → user_account, ON DELETE RESTRICT, NULL | |
| approved_at | TIMESTAMPTZ | NULL | |
| finalized_at | TIMESTAMPTZ | NULL | |
| created_at | — | — | |
| | | CHECK (approved_by IS NULL OR approved_by <> initiated_by) | §3.5 |
| | | UNIQUE (period_start, period_end) | HRMS-DR-009's spirit: one run per active period, not a per-row rule but a table-level one |

Finalisation writes across `payroll_run`, `payslip`, `payslip_line`, and `compensation_record`'s read (not write) within one database transaction, per ADR-0003 and ADR-0006: "a partial payroll is a corrupt payroll." This document does not restate the transaction boundary as a column; it is an application-layer guarantee this schema's foreign keys and `NOT NULL` constraints are shaped to support, not one a table definition can itself express.

**`payslip`.** HRMS-FR-043, HRMS-FR-044, HRMS-BR-006.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| payroll_run_id | BIGINT | FK → payroll_run, ON DELETE RESTRICT | |
| employee_id | BIGINT | FK → employee, ON DELETE RESTRICT | HRMS-DR-009: payroll records must link to active employee records; enforced in application code at generation time, since "active" is a point-in-time employment-status check this schema does not freeze into a constraint |
| gross_pay | NUMERIC(14,2) | NOT NULL | |
| net_pay | NUMERIC(14,2) | NOT NULL | |
| currency | TEXT | NOT NULL, DEFAULT 'GHS' | |
| generated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| | | UNIQUE (payroll_run_id, employee_id) | |

**`payslip_line`.** SRS §6.1's "Allowance" and "Deduction" entities, computed-instance half (definitional half at §4.11 and above). One row per component of a payslip.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| payslip_id | BIGINT | FK → payslip, ON DELETE RESTRICT | |
| line_type | TEXT | NOT NULL, CHECK IN ('basic_salary','allowance','deduction_statutory_paye','deduction_statutory_ssnit_tier1','deduction_statutory_ssnit_tier2','deduction_statutory_ssnit_tier3','deduction_other') | |
| source_type | TEXT | NULL | e.g. `allowance_type`, `statutory_rate_table`; not a foreign key, same reasoning as `audit_log.target_type` — a finalised payslip must remain readable even if the source configuration row is later retired |
| source_id | BIGINT | NULL | |
| description | TEXT | NOT NULL | |
| amount | NUMERIC(14,2) | NOT NULL, CHECK (amount >= 0) | §2.5; a deduction is stored as a positive magnitude with its `line_type` stating direction, not as a signed value, so that `SUM(amount)` grouped by `line_type` is never accidentally net against itself — the constraint is what actually holds that convention, not only the prose describing it |
| created_at | — | — | §2.4; no `updated_at` — a finalised payslip's line items are not mutated |

**`bank_transfer_file`.** HRMS-FR-046.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| payroll_run_id | BIGINT | FK → payroll_run, ON DELETE RESTRICT, UNIQUE | |
| object_key | TEXT | NOT NULL, UNIQUE | Same object-storage pattern as §4.5; format is TBD-006, open |
| generated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

## 5. Entity-Relationship Overview

Every arrow below reads "references" and points from the dependent table to the table it depends on — the same direction as the foreign key itself (`employee.department_id → department`, not the reverse), so the diagram cannot be read against the column tables above it.

```text
employee ──> department
employee ──> job_title
reporting_relationship ──> employee            (employee_id)
reporting_relationship ──> employee            (manager_employee_id)
employment_history ──> employee
employee_document ──> employee
emergency_contact ──> employee
onboarding_checklist ──> employee
onboarding_task ──> onboarding_checklist
compensation_record ──> employee
compensation_record ──> pay_grade ──> salary_structure
employee_allowance ──> employee
employee_allowance ──> allowance_type
benefit_enrollment ──> employee
benefit_enrollment ──> benefit
leave_balance ──> employee
leave_balance ──> leave_type
leave_request ──> employee
leave_request ──> leave_type
bonus_award ──> employee
bonus_award ──> bonus_cycle
payslip ──> employee
payslip ──> payroll_run
payslip_line ──> payslip

candidate_application ──> candidate
candidate_application ──> job_posting ──> job_requisition ──> department
job_requisition ──> job_title
interview ──> candidate_application
offer_letter ──> candidate_application
offer_letter ──> pay_grade

second_factor ──> user_account
second_factor_recovery_request ──> user_account
role_grant_request ──> user_account            (requester, subject, approver)
role_grant_request ──> auth_group              (role_id)
notification ──> user_account
audit_log ──> user_account                     (actor, nullable)

bank_transfer_file ──> payroll_run
statutory_rate_table (independent; read, not referenced, by payslip_line)
```

Foreign keys run from the dependent table to the table it depends on, matching `docs/04-system-architecture.md` §4.1's dependency graph at the module level: no arrow above points from a lower-numbered module's table to a higher-numbered one's, which is the same no-back-reference rule that document states for modules, carried down to tables.

---

## 6. Data Validation Rules

SRS §6.2's ten rules, and where this schema enforces each.

| Rule | Enforcement |
|---|---|
| HRMS-DR-001 — Employee ID must be unique | `employee.employee_number UNIQUE` (§4.5) |
| HRMS-DR-002 — Email address must be unique | `user_account.email UNIQUE` (§4.2). Not applied to `candidate.email` — a candidate may apply more than once (§4.7) — nor to `employee`, which has no email column of its own; an employee's login identity is their `user_account` row, per `CONTEXT.md`'s User/Employee distinction |
| HRMS-DR-003 — Date of birth must be a valid past date | `employee.date_of_birth CHECK (< CURRENT_DATE)` (§4.5) |
| HRMS-DR-004 — Employment start date must be valid | `employee.hire_date NOT NULL`; further validity (not future-dated) is an application-layer check, since the SRS does not define "valid" beyond existence and correct ordering |
| HRMS-DR-005 — Salary values must not be negative | `CHECK (>= 0)` on `compensation_record.base_salary`, `offer_letter.offered_salary`, `pay_grade.min_salary`, `bonus_award.amount`, `benefit.cost`, `allowance_type.amount_or_rate`, `employee_allowance.amount_override`, `payslip_line.amount` (§4.7, §4.11, §4.12) — the rule is stated against "salary" but applied to every stored monetary magnitude in this schema, on the reading that HRMS-DR-005's intent is monetary values generally, not the one column literally named "salary" |
| HRMS-DR-006 — Leave end date cannot be earlier than leave start date | `leave_request CHECK (end_date >= start_date)` (§4.10) |
| HRMS-DR-007 — Required fields must be completed before submission | `NOT NULL` throughout §4; this rule is not one constraint but the aggregate of every `NOT NULL` this document states, so no single row of this table names one |
| HRMS-DR-008 — Uploaded files must match allowed file formats | `employee_document.content_type`, validated server-side by content inspection at upload time (ADR-0007) — a check this schema records the column for but does not itself enforce, since the allowed-format list is application configuration, not a storage-layer constant |
| HRMS-DR-009 — Payroll records must be linked to active employee records | `payslip.employee_id` FK plus an application-layer status check at generation time (§4.12); "active" is a point-in-time fact about `employee.employment_status`, not a property a foreign key alone can express |
| HRMS-DR-010 — Changes to salary and compensation should be stored as history | `compensation_record`'s append-only design (§3.4) |

---

## 7. SRS §6.1 Entity Traceability

Every entity SRS §6.1 lists, and the table or tables that carry it. Where an entity splits across a definitional table and a computed-instance table, both are given, on the same pattern `docs/04-system-architecture.md` §3 already uses for audit and notification (an owned surface plus per-consumer emission) — applied here to data rather than to behaviour.

| SRS §6.1 entity | Table(s) | Module |
|---|---|---|
| Employee | `employee` | 6 |
| Department | `department` | 7 |
| Job title | `job_title` | 7 |
| Role | `auth_group` (Django built-in) | 4 |
| Reporting relationship | `reporting_relationship` | 8 |
| Employment history | `employment_history` | 6 |
| Compensation record | `compensation_record` | 15 |
| Employee document | `employee_document` | 6 |
| Emergency contact | `emergency_contact` | 6 |
| Job requisition | `job_requisition` | 9 |
| Job posting | `job_posting` | 9 |
| Candidate | `candidate`, `candidate_application` | 9 |
| Interview | `interview` | 9 |
| Offer letter | `offer_letter` | 9 |
| Onboarding checklist | `onboarding_checklist`, `onboarding_task` | 10 |
| Payroll record | `payroll_run` | 16 |
| Payslip | `payslip` | 16 |
| Allowance | `allowance_type`, `employee_allowance` (definition); `payslip_line` (computed instance) | 15, 16 |
| Deduction | `statutory_rate_table` (definition); `payslip_line` (computed instance) | 16 |
| Leave request | `leave_request` | 14 |
| Leave balance | `leave_balance` | 14 |
| Leave type | `leave_type` | 14 |
| Benefit | `benefit`, `benefit_enrollment` | 15 |
| Pay grade | `pay_grade`, `salary_structure` | 15 |
| Audit log | `audit_log` | 1 |
| User account | `user_account` | 3 |
| Permission | `auth_permission` (Django built-in) | 4 |

**Tables required by architecture but not named as SRS §6.1 entities:** `notification` (§3.2, required by `docs/04-system-architecture.md` §3.2/§4's ownership of the in-app feed), `second_factor` and `second_factor_recovery_request` (HRMS-NFR-024, a nonfunctional requirement with no §6.1 entity of its own), `role_grant_request` (`docs/07-iam-rbac.md` §7.3, ADR-0010), `bonus_cycle`/`bonus_award` (HRMS-FR-059, a functional requirement §6.1's entity list does not separately name), and `bank_transfer_file` (HRMS-FR-046, folded into "Payroll record" at the requirement level but requiring its own table because a run has zero-or-one file, not a field of the run). None of these is scope this document adds; each is a functional or architectural requirement already fixed elsewhere that has no matching row in §6.1's entity list because that list is not exhaustive of every table an SRS requirement implies.

---

## 8. Requirements Traceability

Requirements not already covered by §6 (validation rules) or §7 (entity list).

| Requirement | Addressed by |
|---|---|
| HRMS-FR-009 (search and filter employee records) | `employee` columns support standard indexing (department_id, job_title_id, employment_status); index selection is left to `docs/06-api-contracts.md` and migration design, not fixed here |
| HRMS-FR-010 (audit history) | §3.1 — a filtered read of `audit_log`, not a second table |
| HRMS-FR-033, HRMS-FR-034 (notification) | §3.2 |
| HRMS-BR-004 (reporting manager unless top management) | §4.6 — absence of a row, not a nullable column |
| HRMS-BR-008 (payroll approval) | §3.5 |
| HRMS-BR-012 (terminated/resigned/retired lose access) | §3.3 — `employee.employment_status`, read by the Employee derivation |
| HRMS-BR-013 (candidate conversion timing) | §4.8 — `onboarding_checklist.employee_id` cannot exist before conversion |
| HRMS-NFR-010 (no deletion of payroll history) | §2.2, §2.3 — no `CASCADE`, no hard delete on business records |
| HRMS-NFR-013, HRMS-NFR-022 (audit logging) | §3.1 |
| HRMS-NFR-024 (second-factor authentication) | §4.2 — `second_factor`, `second_factor_recovery_request` |
| `docs/07-iam-rbac.md` §3 (derived roles) | §3.3 |
| `docs/07-iam-rbac.md` §4.4 (payroll approver not initiator) | §3.5 |
| `docs/07-iam-rbac.md` §5 (visibility rules) | Every `employee_id`/`recipient_user_id` foreign key in §4 is the column each module's visibility rule filters on; this document does not restate the rule table, only the columns it operates against |
| `docs/07-iam-rbac.md` §7.3 (audit immutability grant) | §3.1 |

### Re-reading `docs/07-iam-rbac.md` Against This Document

Per plan §5.3, this is part of M3 sign-off. The IAM document's two schema-relevant fixed points — the derived-role dependency on employment status and reporting relationship (§3 there), and the payroll approver-not-initiator constraint (§4.4 there) — are both carried into this schema at §3.3 and §3.5. Its permission matrix (§4.2) and visibility-rule table (§5) name no entity this schema does not already provide a table for. No inconsistency was found; neither document required a change.

---

## 9. Open Items Inherited, Not Introduced

This document introduces no new TBD. The items below are open in documents this one is downstream of and bear on the schema as designed.

- **TBD-005 (final payroll statutory rates).** Open. `statutory_rate_table.rates` (§4.12) is shaped to hold whatever bracket structure the eventual rates require; no placeholder value is stored.
- **TBD-006 (bank transfer file format).** Open. `bank_transfer_file` (§4.12) stores the generated file's object key regardless of format; the format itself is not a schema decision.
- **TBD-009 (document retention policy).** Open. Bears on `employee_document` and `audit_log` retention; no retention column exists in this schema because no policy exists yet to encode — adding one now would be inventing a default the organisation has not set.
- **TBD-003 (hosting target).** Open by decision (ADR-0009). Nothing in this schema depends on where PostgreSQL runs.
- **`iam.approve_role_grant` and second-factor recovery approver holders.** Deferred to deployment (`docs/07-iam-rbac.md` §8). `role_grant_request` and `second_factor_recovery_request` (§4.2, §4.3) function identically regardless of who is designated.

---

**Sign-off.** Per `docs/02-project-plan.md` §5.2, this milestone is met when the project owner has read this document and accepted it.
