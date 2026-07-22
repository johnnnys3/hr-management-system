# Testing Plan

**Human Resource Management System**

| | |
|---|---|
| Version | 1.1 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-16 |
| Status | Draft — pending owner acceptance at M5 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-16 | Initial testing plan, closing milestone M5 | 1.0 |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.5's Dashboard renumbering (module 5 → 14; modules 6–14 → 5–13).** Module-numbered rows below are still v1.4. Reconcile at M5 sign-off per plan §5.3 | 1.0 (unreconciled) |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.6's Employee Management/Departments swap (modules 5 ↔ 6 in the plan's numbering; module-numbered rows below still v1.4-numbered as 6 and 7).** Reconcile at M5 sign-off per plan §5.3 | 1.0 (unreconciled) |
| John Kessie | 2026-07-22 | **Reconciled to `docs/02-project-plan.md` v1.8, per the two rows above (both now resolved) plus the later v1.7 Dashboard-aggregates note.** §4's per-module table and §6.1's coverage matrix are renumbered and reordered to the current build order (Departments 5, Employee Management 6, Reporting Structure 7, Recruitment 8, Onboarding 9, Notification 10, Employee Self-Service 11, Manager Self-Service 12, Leave Management 13, Dashboard 14, Compensation and Benefits 15, Payroll 16, Reports 17); every in-prose cross-reference to a module number in §5 and §6 is corrected to match. No test obligation, tool selection, or control content changes — this is a pure renumbering, the same shape as DOC-007/008's reconciliation of `docs/04-system-architecture.md` and `docs/06-api-contracts.md`, which this document was the one left behind when those two were fixed. Filed as DOC-015 | 1.1 |

---

## 1. Introduction

### 1.1 Purpose

This document turns the six-row control table of `docs/02-project-plan.md` §9 into an actual testing strategy: what each control covers, how it is implemented, by which tool, and against which prior document's design it is checked. It states, for every module in the build order, what a complete set of tests for that module looks like, and it states the test data strategy the append-only and multi-actor constraints of `docs/05-database-schema.md` and `docs/07-iam-rbac.md` require.

It does not choose a testing tool, which `docs/03-tech-stack.md` §9 has already done; it does not design the permission matrix or the visibility rules, which `docs/07-iam-rbac.md` §4.2 and §5 have already done; and it does not restate the endpoint catalog, which `docs/06-api-contracts.md` §4 has already done. Where this document names a tool, a permission cell, a visibility rule, or an endpoint one of those sources already states, it cites the source rather than re-arguing it.

### 1.2 Intended Audience

The project owner reviewing this document before development begins, and the same person, wearing the developer's hat, who will write every test this document describes (`docs/02-project-plan.md` §3).

### 1.3 Relationship to Prior Documents

This document is downstream of six documents it does not revise:

- **`docs/01-srs.md`** (v1.1) — the requirement set, and specifically §4's stimulus/response sequences, which §6 below targets directly, and the nonfunctional requirements of §5, which §7 addresses. Authoritative; where this document and the SRS disagree, the SRS governs.
- **`CONTEXT.md`** — the domain glossary. Test names, fixture names, and factory names in this document and in the code it describes use its terms as defined (Employee vs. User, audit log vs. audit history, mail dispatch vs. notification), per its own instruction that avoided terms are avoided "including in issue titles, test names, module names, and commit messages."
- **`docs/02-project-plan.md`** (v1.4) — §9's six-row control table, expanded rather than re-derived in §3 below; §6.1's twenty-module build order, against which §4's per-module obligations are organised; and §8.1's TBD register, whose blocking effect on M16 Payroll and M18 Testing (TBD-005, TBD-006, TBD-016, TBD-017) this document inherits rather than resolves.
- **`docs/03-tech-stack.md`** (v1.0) §9 — pytest with pytest-django, factory_boy, Vitest with React Testing Library, Playwright, and drf-spectacular. Settled tool selections this document builds a strategy on top of, not chooses among.
- **`docs/04-system-architecture.md`** (v1.0) §2 — the completeness bar: "a module is architecturally complete when its models, service layer, API endpoints, visibility rule, and permission tests exist and its permission tests assert both the permitted and the denied path." §4 below operationalises this per module rather than restating it twenty times.
- **`docs/06-api-contracts.md`** (v1.0) §4 and `docs/07-iam-rbac.md` (v1.6) §4.2 and §5 — the endpoint catalog and the permission matrix and visibility-rule tables every permission and contract test in §4 below traces to. This document cites a cell or a row; it does not restate the predicate behind either.

### 1.4 Scope

In scope: expanding plan §9's six controls into per-module obligations (§4), the test data strategy for append-only and multi-actor constraints (§5), the end-to-end test strategy against SRS §4's stimulus/response sequences (§6), the treatment of the nonfunctional requirements SRS §5.1 states as thresholds this project cannot yet verify (§7), and the honest statement of what none of it catches (§8).

Out of scope, per `CONTEXT.md` "Scope boundary" and SRS §6.4: no test in this plan exercises biometric attendance, AI recruitment screening, learning management, performance appraisal, complex shift scheduling, ERP or accounting integration, automatic tax filing, direct bank integration, loan management, travel and expense management, disciplinary case management, union management, multi-country payroll, chatbot support, or a native mobile application. A test that would need one of these is a scope change requiring SRS revision, not a testing gap.

This document does not reopen plan §9's six-row control table, `docs/03-tech-stack.md` §9's tool selections, the permission matrix, the visibility rules, or the endpoint catalog. Where a test obligation depends on one of those, it cites the source rather than re-arguing it.

---

## 2. Reading Guide

§4's module table uses four columns, three of them citations rather than restatements, on the same pattern `docs/06-api-contracts.md` §3 fixed for its own tables:

**Permission tests** — cites the `docs/07-iam-rbac.md` §4.2 cell(s) the module's endpoints gate. A module whose matrix row lists five roles owes a denied-path test for every role not listed, not only a permitted-path test for the ones that are — the completeness bar (`docs/04-system-architecture.md` §2) is explicit that a module without both is incomplete, and the ratio this produces is usually lopsided: `docs/02-project-plan.md` §7.3 gives module 1 as the example, "the denied paths outnumber the permitted one eight to one."

**Visibility tests** — cites the `docs/07-iam-rbac.md` §5 row. Where §5 states "—" for a role, that role is rejected at the permission layer before a visibility rule is ever evaluated (`docs/06-api-contracts.md` §2.2), and no visibility test is owed for it; the permission test already covers the rejection.

**Contract tests** — names which `docs/06-api-contracts.md` §4 endpoints the module's contract tests hold the served API to, per the mechanism §3.2 below fixes once rather than per module.

**Functional/validation tests** — the module's own business logic and the `docs/01-srs.md` §6.2 data validation rules (HRMS-DR-001 to HRMS-DR-010) it is responsible for, where §6 of the schema document assigns them to a specific table this module owns.

A module's row in §4 is not a complete list of its tests; it is the obligations the four columns above name, at the same altitude `docs/06-api-contracts.md` §4 named endpoints — enough for a developer building the module to know what "done" requires, not a line-by-line test specification.

---

## 3. The Six Controls, Expanded

`docs/02-project-plan.md` §9 names six controls and, for each, what it catches. This section is where each becomes an actual test suite. It is the seed §5.1 of that document names, not a re-decision of it.

### 3.1 Permission Tests

**Tool: pytest with pytest-django** (`docs/03-tech-stack.md` §9). **Catches: an endpoint that omits its visibility rule** (plan §9; ADR-0005).

Every module with at least one endpoint returning employee-scoped data (`docs/06-api-contracts.md` §2.5) owns a permission test suite structured as one test class per endpoint, asserting, for every role named or excluded by the `docs/07-iam-rbac.md` §4.2 cell that endpoint's operation falls under:

- The **permitted** path: a request from a role §4.2 grants the operation to succeeds and returns the visibility-scoped result set (`docs/07-iam-rbac.md` §5).
- The **denied** path: a request from every other role returns `403` (action-level denial, `docs/06-api-contracts.md` §2.2) or, for a request naming a specific object outside the caller's visibility scope, `404` (row-level denial, same section) — and the two are asserted as the distinct outcomes they are, not collapsed into a single "fails" assertion, since `docs/06-api-contracts.md` §2.2 fixes them as different responses to different failures and a test that cannot tell them apart cannot catch a `visible_to()` call silently replaced by a broader one that still trips the `403`.

**Multi-role and derived-role cases are asserted explicitly, not incidentally.** Where a user holds more than one assigned role (`docs/07-iam-rbac.md` §6), or is simultaneously a derived Employee or Manager alongside an assigned role, the permission test suite for the affected module asserts the additive outcome directly — an HR Officer who is also someone's direct report sees their own payslip as an Employee and the employee records their HR Officer grant reaches, and neither grant narrows the other. This is not a separate test category; it is the same permitted/denied structure applied to a fixture combining roles rather than one holding a single role, using the multi-role factories §5.2 below defines.

**Self-approval and self-grant refusals are permission tests, not validation tests.** `docs/07-iam-rbac.md` §7.3's self-grant refusal, §4.4's payroll approver-not-initiator constraint, and the second-factor recovery approver's eligibility check (`docs/06-api-contracts.md` §4.2) are each asserted at two layers per §3.4 below: a permission test confirming the API returns `403` with `code: "self_approval_forbidden"` (`docs/06-api-contracts.md` §2.7), and the database constraint test of §3.4 confirming the `CHECK` constraint rejects the row even where application code is bypassed.

**The audit read surface (module 1) is the sharpest case of this control**, per `docs/02-project-plan.md` §7.3's own estimate: eight denied-path tests against one permitted-path test, since `docs/07-iam-rbac.md` §4.2 grants System Administrator alone **R** on the audit log. Module 4's role-grant and second-factor-recovery decision endpoints are the second sharpest, since both gate on an eligibility check (`docs/06-api-contracts.md` §4.9, §4.2) rather than a static role name, and the denied path there must additionally cover the case where the caller holds the permission but is the ineligible party — the case a role-based test alone would not catch.

### 3.2 Schema-Generated API Contracts

**Tool: drf-spectacular** (`docs/03-tech-stack.md` §9). **Catches: divergence between `docs/06-api-contracts.md` and the served API** (plan §9).

`docs/06-api-contracts.md` §1.2 states its own relationship to this control directly: it is "the document that precedes and constrains the generated OpenAPI schema," and "constrains" is operationalised here as two checks, run in CI on every push to `develop`:

1. **Existence and shape.** For every endpoint `docs/06-api-contracts.md` §4 lists, a contract test (pytest, using DRF's `APIClient` against the URL and method named) asserts the endpoint exists, accepts the method(s) listed, and its generated schema's request/response shape matches the resource fields §4's row names. This is not a hand-maintained OpenAPI diff; it is a pytest suite that imports the generated schema (`drf-spectacular`'s `SchemaGenerator`) and asserts against it, so the check runs against what DRF actually serves rather than against a document a developer might forget to update.
2. **No undocumented surface.** A CI step lists every URL pattern the Django URLconf registers and asserts it appears in `docs/06-api-contracts.md` §4's endpoint list (a generated inventory checked into the repository as a fixture, regenerated and diffed rather than hand-maintained, on the same reasoning `docs/02-project-plan.md` §6.1's `scripts/check-docs.py` gives for asserting derived facts rather than trusting prose to stay current). An endpoint that exists in code but not in the contract document fails CI; a contract document endpoint not yet implemented is expected during development and is not a failure — the check is one-directional until M18 Testing, at which point both directions hold.

The error envelope of `docs/06-api-contracts.md` §2.7 is asserted once, centrally, against DRF's custom `EXCEPTION_HANDLER` — not per endpoint — since §2.7 states it is uniform across every endpoint by design; a per-endpoint duplicate of the same assertion would test the framework wiring twenty times rather than testing each endpoint's own contract once.

### 3.3 Boundary Validation

**Tool: Zod, at the API boundary in the client** (`docs/03-tech-stack.md` §6.1). **Catches: backend contract drift, surfaced as an explicit error rather than an undefined value** (plan §9).

This is a frontend control, not a backend one, and its test surface is accordingly Vitest with React Testing Library (`docs/03-tech-stack.md` §9), not pytest. Each API resource `docs/06-api-contracts.md` §4 names has a corresponding Zod schema in the client; the test obligation is one unit test per schema asserting that a fixture matching `docs/06-api-contracts.md`'s documented shape parses successfully, and one asserting that a fixture missing a required field or carrying an unexpected type fails to parse and surfaces the envelope §2.7 defines — not that the component using the schema renders correctly, which is a component test, not a boundary-validation test, and belongs to that module's own frontend test suite rather than to this control.

### 3.4 Database Constraints

**Tool: PostgreSQL check and unique constraints, exercised through pytest-django against a real test database** (`docs/03-tech-stack.md` §5.1, §9; ADR-0003). **Catches: HRMS-DR-001, HRMS-DR-002, HRMS-DR-005, HRMS-DR-006, where application defects cannot bypass them** (plan §9).

Every constraint `docs/05-database-schema.md` §6 states is asserted by a test that attempts the violation directly against the database — not through the application's serializer, which would test validation twice at the layer that is not the point of this control — and asserts the database rejects it with an `IntegrityError` (`django.db.utils.IntegrityError`), independent of whether the application layer would have caught it first. This is deliberate duplication with the serializer-level validation tests §4's functional/validation column names: the control exists precisely because `docs/03-tech-stack.md` §5.1 places these checks "at the storage layer, where application defects cannot bypass them," and a test suite that only exercises the serializer path never proves the database layer holds if the serializer is ever changed or bypassed.

Two constraints carry a security or correctness consequence beyond ordinary data validation and are tested with that in mind, per §3.1's note above:

- `docs/05-database-schema.md` §3.5's `CHECK (approved_by IS NULL OR approved_by <> initiated_by)` on `payroll_run` — a direct `UPDATE` attempt setting `approved_by = initiated_by` against a test database, bypassing the application entirely, is rejected.
- The equivalent `CHECK` on `role_grant_request` (`docs/06-api-contracts.md` §4.9) — the same direct-`UPDATE` test, for the same reason.

### 3.5 Automated Review

**Tool: CodeRabbit on `develop`** (plan §9). **Catches: a second reading of every change; the nearest available substitute for a reviewer** (plan §9, recording the structural weakness of `docs/02-project-plan.md` §3 — no independent review).

This control has no test suite of its own; it is a review gate on pull requests into `develop`, per `docs/agents/issue-tracker.md`'s workflow. It is recorded here rather than omitted because plan §9's table lists it alongside the five test-suite controls, and a testing plan that silently dropped the sixth row would understate what the project actually relies on. Its scope and limits — auto-review timing, thread resolution, the discipline of revisiting a dismissed finding rather than treating the first read as final — are operational practice, not a testing artifact, and are not restated here beyond noting that this control's output (an accepted or reopened review thread) is not itself evidence any of the other five controls passed; each of those still runs and reports independently in CI.

### 3.6 End-to-End Tests

**Tool: Playwright** (`docs/03-tech-stack.md` §9). **Catches: the SRS §4 stimulus/response sequences** (plan §9). Detailed in §6 below.

---

## 4. Per-Module Test Obligations

Modules are numbered per `docs/02-project-plan.md` §6.1 (v1.8 numbering, reconciled at DOC-015 — see the revision history above; `docs/04-system-architecture.md` §4 and `docs/06-api-contracts.md` §4 were already reconciled to this same v1.8 numbering at DOC-007 and DOC-008, this document was the one left behind). Modules 18 to 20 are process modules, own no endpoint (`docs/06-api-contracts.md` §4), and are not rows in this table; their obligations are §6 (end-to-end testing) and §8 (UAT scope) and this document's own existence (M18's principal requirement is `docs/08-testing-plan.md` itself, per plan §6.1).

| # | Module | Permission tests | Visibility tests | Contract tests | Functional/validation tests |
|---|---|---|---|---|---|
| 1 | Audit | `docs/07-iam-rbac.md` §4.2 Audit log row — System Administrator **R**; eight denied-path tests (§3.1) | System Administrator only; no other role reaches the endpoint (§4.1) | `/api/audit-log/`, `/api/employees/{id}/audit-history/` (`docs/06-api-contracts.md` §4.1) | No `UPDATE`/`DELETE` capability at the database role (§3.4-adjacent, but exercised as a deployment-configuration test in M20, not a module-1 unit test — the grant is not application code); `audit-history` returns exactly the `target_type='employee'` filtered subset, asserted against a fixture spanning multiple `target_type`s |
| 2 | Mail dispatch | n/a — no endpoint, no employee-scoped read surface (`docs/04-system-architecture.md` §4) | n/a | n/a | Celery task: bounded retry count is exhausted and logged rather than retried indefinitely; a delivery failure writes to application logs and **not** to `audit_log` (ADR-0011, asserted as a negative — the audit table gains no row); template rendering for each consumer (password reset, onboarding, payroll communication, Notification's email channel) produces the expected recipient and does not leak another employee's data into a template context |
| 3 | Authentication | `docs/07-iam-rbac.md` §4.2 — login/logout/`me` require only authentication, not a role; second-factor enrolment and recovery-request creation: self only, denied for every attempt naming another user (HRMS-NFR-024) | n/a (pre-identity; `docs/06-api-contracts.md` §4.2) | `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/me/`, `/api/auth/password-reset/`, `/api/auth/second-factor/`, `/api/auth/second-factor/recovery-requests/` (`docs/06-api-contracts.md` §4.2) | Uniform response on login/password-reset failure regardless of account existence (`CONTEXT.md` "Deployment conditions"); session invalidation on logout; inactivity expiry (HRMS-NFR-023); second-factor presentation required on every authentication for System Administrator and Payroll Officer (HRMS-NFR-024) |
| 4 | RBAC / IAM | `docs/07-iam-rbac.md` §4.2 User accounts row — System Administrator only; role-grant self-refusal (§7.3) at both permission and constraint layers (§3.1, §3.4); recovery-decision eligibility (approver ≠ requester, approver does not administer the requester's credentials) | System Administrator: all `user_account` rows; no employee/payroll field expansion (`docs/06-api-contracts.md` §4.9) | `/api/users/`, `/api/role-grant-requests/`, `/api/role-grant-requests/{id}/decide/`, `/api/auth/second-factor/recovery-requests/{id}/decide/` (`docs/06-api-contracts.md` §4.9, §4.2) | `is_superuser` is never assigned to the System Administrator group (`docs/07-iam-rbac.md` §7.2 — a code-review and CI-lint obligation as much as a test, asserted by a test that fails if any fixture or migration grants it to a non-break-glass account); a privileged grant takes effect only after an eligible approver's decision, never on request creation alone |
| 5 | Departments | `docs/07-iam-rbac.md` §4.2 HR configuration row — HR Administrator C/U, HR Officer/Recruiter/Payroll Officer R | Organisation-wide; no per-role scoping (`docs/06-api-contracts.md` §4.4) | `/api/departments/`, `/api/job-titles/` (`docs/06-api-contracts.md` §4.4) | HRMS-BR-002 (every employee belongs to a department); `PATCH {"is_active": false}` retires rather than deletes (`docs/05-database-schema.md` §2.3) |
| 6 | Employee Management | `docs/07-iam-rbac.md` §4.2 Employee records row — HR Officer C/R/U, HR Administrator R/U-status, Payroll Officer R (payroll fields only), Manager R (direct reports), Employee R (own); denied paths for Recruiter, Executive | Employee: own only; Manager: direct reports; HR: all (`docs/07-iam-rbac.md` §5) | `/api/employees/`, `/api/employees/{id}/`, `/api/employees/me/`, `/api/employees/{id}/employment-history/`, `/api/employees/{id}/documents/`, `/api/employees/{id}/emergency-contacts/` (`docs/06-api-contracts.md` §4.3) | HRMS-DR-001 (unique employee ID), HRMS-DR-002 (unique email), HRMS-DR-003 (valid past DOB), HRMS-DR-004 (valid start date); HRMS-FR-027 — the `/me/` serializer rejects `employment_status`, `salary`, `job_title`, `department`, and `manager` fields even when present in the request body, asserted against the narrower serializer directly, not against the HR-facing one with a permission check bolted on (`docs/06-api-contracts.md` §4.3's stated reason); a status change writes `employment_history` (HRMS-FR-004); document upload validates content type by inspection, not extension, and enforces size server-side (ADR-0007) |
| 7 | Reporting Structure | `docs/07-iam-rbac.md` §4.2 — grouped with Employee records; HR read-all, Manager read-own-direct-reports | Manager: direct reports only, no transitive chain (`docs/07-iam-rbac.md` §5) — the negative case (a skip-level manager cannot see a report's report) is asserted explicitly, since it is the visibility rule most likely to be gotten wrong by a naive recursive query | `/api/reporting-relationships/`, `/api/employees/{id}/direct-reports/`, `/api/employees/{id}/manager/` (`docs/06-api-contracts.md` §4.5) | HRMS-BR-004 (every employee has a manager unless top management); a manager change writes a new `reporting_relationship` row and closes the prior one (current-state table, `docs/05-database-schema.md` §4.6), and simultaneously writes `employment_history` with `event_type = 'manager_change'` — asserted as one atomic write, not two |
| 8 | Recruitment | `docs/07-iam-rbac.md` §4.2 — Recruiter C/R/U, HR Administrator R, requisition approval HR Administrator **A** only | Recruiter: full; HR Administrator: read; others: none (`docs/04-system-architecture.md` §4) | `/api/job-requisitions/`, `.../approve/`, `.../reject/`, `/api/job-postings/`, `/api/candidates/`, `.../applications/`, `.../interviews/`, `.../offer/`, `/api/offers/{id}/decide/` (`docs/06-api-contracts.md` §4.6) | A job posting cannot be created against a requisition whose `status` is not `'approved'` (`docs/06-api-contracts.md` §4.6 — application-code enforcement, not a schema constraint, so this is a functional test rather than a §3.4 constraint test); an offer `decide` with `accepted` does **not** by itself create an employee record (HRMS-BR-013 — the conversion trigger is module 9, and this is asserted as a negative: no `employee` row exists immediately after acceptance) |
| 9 | Onboarding | `docs/07-iam-rbac.md` §4.2 Onboarding row — HR Officer C/R/U, HR Administrator/Recruiter R | Per-role, same scoping as Employee Management read (`docs/06-api-contracts.md` §4.7) | `/api/onboarding/convert/`, `/api/onboarding-checklists/{id}/`, `.../tasks/` (`docs/06-api-contracts.md` §4.7) | **HRMS-BR-013's conversion point.** `convert/` creates the `employee` row and the `onboarding_checklist` row referencing it atomically — a test that forces a failure partway through (e.g. checklist creation raising) asserts no orphan `employee` row survives the transaction, per `docs/06-api-contracts.md` §4.7's "a failure partway does not leave an `employee` row with no checklist"; task completion sets `completed_by`/`completed_at` |
| 10 | Notification | n/a — own-record equality, not a matrix cell (`docs/06-api-contracts.md` §3, §4.8) | `recipient_user_id = current user`, single equality (`docs/05-database-schema.md` §3.2) — a test attempting to read or mark-read another user's notification by `id` and receiving `404` | `/api/notifications/`, `/api/notifications/{id}/read/` (`docs/06-api-contracts.md` §4.8) | No client-facing `POST` exists (`docs/06-api-contracts.md` §4.8) — asserted as a negative, that the URLconf exposes no such route; notifications are written only by emitting-module service code, exercised as part of each emitting module's own functional tests, not module 10's |
| 11 | Employee Self-Service | Employee R/U own only (`docs/07-iam-rbac.md` §4.2) | Own record only (HRMS-NFR-017, HRMS-BR-006) | `/api/employees/me/` (shared row with module 6, `docs/06-api-contracts.md` §4.11) | See module 6's HRMS-FR-027 obligation, which this module's endpoint is the client of; no obligation duplicated here beyond confirming module 11's own consumption of module 10 (first consumer, per `docs/04-system-architecture.md` §4.1) |
| 12 | Manager Self-Service | Manager R own direct reports only (`docs/07-iam-rbac.md` §4.2) | Direct reports only (HRMS-NFR-018, HRMS-BR-007) | `/api/employees/{id}/direct-reports/` (shared row with module 7) | Approval/rejection consumes module 10 (pending-task and decision notices) — asserted by confirming a notification row is created on each transition, in the leave and requisition test suites that own those transitions, not duplicated here |
| 13 | Leave Management | `docs/07-iam-rbac.md` §4.2 — Employee C/R own, Manager A (own direct reports only), HR Officer R/U (not A — HRMS-BR-009's approval-workflow bypass this excludes), HR Administrator R | Employee: own; Manager: direct reports'; HR: all (`docs/07-iam-rbac.md` §5) | `/api/leave-types/`, `/api/leave-balances/`, `/api/leave-requests/`, `.../approve/`, `.../reject/`, `.../cancel/`, `/api/leave-calendar/` (`docs/06-api-contracts.md` §4.12) | HRMS-DR-006 (end date not before start date); HRMS-BR-010 (approval decrements `leave_balance.used_days`); HRMS-BR-011 (rejection does not); HRMS-FR-068 (request beyond balance is refused unless policy allows — asserted against whatever TBD-008 eventually supplies, and recorded as blocked on it until then, per §7 below); **the permission/action split** — an HR Officer's `PATCH` to a leave request is asserted to reject any attempt to write `status: 'approved'` through it, confirming the two paths (`PATCH` for correction, `approve/` for the gated transition) cannot converge on the same field through different permission classes (`docs/06-api-contracts.md` §4.12's stated reason) |
| 14 | Dashboard | Any authenticated user; content varies by role, no independent grant of its own (`docs/04-system-architecture.md` §4) | Delegates to the source module's `visible_to()` — asserted by confirming the dashboard never queries outside a source module's own scoped queryset, not by a separate rule | `/api/dashboard/` (`docs/06-api-contracts.md` §4.10) | An Executive's dashboard never includes an individual record, only aggregates (`docs/07-iam-rbac.md` §4.3) — the one functional assertion this module exists to make, since it is the module where an aggregate-only violation would first become visible |
| 15 | Compensation and Benefits | `docs/07-iam-rbac.md` §4.2 — HR Administrator C/R/U structures, HR Officer C/R/U assignment, Payroll Officer R; no Employee self-read of compensation history (§4.2's matrix omits it) | Per role, Employee records scope (`docs/06-api-contracts.md` §4.13) | `/api/salary-structures/`, `/api/pay-grades/`, `/api/employees/{id}/compensation-records/`, `/api/bonus-cycles/`, `.../awards/`, `/api/allowance-types/`, `/api/employees/{id}/allowances/`, `/api/benefits/`, `.../benefit-enrollments/` (`docs/06-api-contracts.md` §4.13) | **The append-only obligation is the load-bearing test in this module.** A `POST` of a new compensation record for an employee who already has a current one asserts three things in one test: the new row is inserted with its own `effective_from`; the prior row's `is_superseded` and `effective_to` are set, and are the *only* two columns of that row that change (`docs/05-database-schema.md` §3.4); and every value-bearing column of the prior row (`base_salary`, `pay_grade_id`, `effective_from`) is byte-for-byte unchanged, asserted by comparing the full row before and after rather than only the two columns expected to move — this is the test that would catch a future `PATCH` accidentally reaching a value column through this endpoint, since `docs/06-api-contracts.md` §4.13 states no client-facing `PATCH`/`DELETE` exists on this endpoint at all, and the assertion should fail loudly if one is ever added without a corresponding contract-document change (§3.2's control) |
| 16 | Payroll | `docs/07-iam-rbac.md` §4.2 — Payroll Officer C/R/U processing; finalisation approval is `‡`, resolved to `payroll.approve_payroll_run` (§4.4), granted to no role by default; self-approval refused regardless of role combination held | Payroll Officer: all payroll fields; Employee: own payslip only (HRMS-BR-006) | `/api/payroll-runs/`, `.../calculate/`, `.../submit-for-approval/`, `.../approve/`, `.../finalize/`, `.../bank-transfer-file/`, `/api/payslips/`, `.../download/`, `/api/statutory-rates/` (`docs/06-api-contracts.md` §4.14) | **The approver-not-initiator constraint is asserted at both the API and database layers** (§3.1, §3.4): an `approve/` call by the run's own `initiated_by` returns `403` with `code: "self_approval_forbidden"` regardless of which role combination the caller holds (`docs/07-iam-rbac.md` §4.4's "regardless of any combination of roles"), and a direct-`UPDATE` bypass attempt is rejected by the `CHECK` constraint; `finalize/` is atomic across `payroll_run`, `payslip`, `payslip_line` — a forced mid-transaction failure leaves no partial payslip set (ADR-0003, ADR-0006, "a partial payroll is a corrupt payroll"); payroll tasks are idempotent — a retried `calculate/` or `finalize/` Celery task does not produce duplicate payroll records (`docs/03-tech-stack.md` §4.2); PAYE, SSNIT Tier 1, Tier 2, Tier 3 calculations are asserted against the versioned rate table structure, not against particular rate values, per §7's TBD-005 treatment below; monetary values are `Decimal` end to end, never a binary float, in every assertion this module's tests make on an amount |
| 17 | Reports | `docs/07-iam-rbac.md` §4.2 — HR read, Manager team-level, Executive aggregate, Payroll Officer payroll-cost | Per source module's rule; Executive: aggregate only, never an individual record (`docs/07-iam-rbac.md` §4.3) | `/api/reports/headcount/`, `.../leave-utilization/`, `.../payroll-cost/`, `.../export/`, `/api/report-exports/{job_id}/` (`docs/06-api-contracts.md` §4.15) | HRMS-FR-053 (filter by department, role, date, employment status); **the Executive aggregate-only rule is tested as a disclosure control, not a display preference** — a request crafted to try to isolate a single employee's payroll-cost contribution through filtering is asserted to still return only an aggregate, since `docs/06-api-contracts.md` §4.15 states this is "where §4.3's aggregate-only rule is load-bearing rather than incidental"; export jobs poll to `complete`/`failed`, and a payroll-cost export emits an audit entry (`docs/04-system-architecture.md` §4's module 17 row) |

---

## 5. Test Data Strategy

**Tool: factory_boy** (`docs/03-tech-stack.md` §9), one factory per model, composed rather than duplicated across test modules.

### 5.1 Ordinary Factories

Every table in `docs/05-database-schema.md` §4's entity catalog has a corresponding factory producing a valid row against that table's constraints (§6 there), built with `Faker`-backed field values by default and explicit overrides where a test's assertion depends on a specific value (a `base_salary` a payroll test computes PAYE against, an `employment_status` a visibility test depends on). Factories compose through `factory.SubFactory` for foreign keys (an `EmployeeFactory` builds its own `DepartmentFactory` unless one is supplied), on the ordinary factory_boy pattern, and this document does not restate that pattern per model.

### 5.2 Multi-Actor Fixtures

Several constraints identified in §3 and §4 above cannot be exercised by a single-user factory, because the constraint's entire point is that two distinct identities are involved. These are named once here rather than per module:

- **Payroll approver ≠ initiator** (`docs/05-database-schema.md` §3.5). A `PayrollRunFactory` trait or helper produces a run with a distinct `initiated_by` and a distinct candidate `approved_by`, both Payroll Officer role holders, so that tests asserting the *rejection* of self-approval and tests asserting the *success* of a legitimate approval draw from the same factory shape rather than two ad hoc setups that could silently drift apart.
- **Role-grant requester ≠ approver, and approver eligibility** (`docs/07-iam-rbac.md` §7.3). A fixture pairing a System Administrator (requester) with a second System Administrator holding `iam.approve_role_grant` (approver) — and, separately, a fixture where the "approver" is the same identity as the requester, for the negative test.
- **Second-factor recovery approver ≠ credential administrator** (`docs/06-api-contracts.md` §4.2, HRMS-NFR-024). A fixture with three distinct identities: the account holder requesting recovery, an eligible approver who administers no accounts or credentials, and a System Administrator who is asserted *ineligible* to decide the request even if granted the underlying permission by test setup — this third identity is what makes the eligibility check's test meaningfully different from a role check, per §3.1's note that this is the case a role-based test alone would not catch.
- **Manager and direct report, across two or more levels** (`docs/07-iam-rbac.md` §5, "no transitive chain"). A fixture producing at least three tiers of `reporting_relationship` rows, so that module 7's negative visibility test (§4, row 7) has a skip-level manager to assert against, not only a direct one.
- **Leave request across employee and manager** (HRMS-BR-009 to HRMS-BR-011). An `EmployeeFactory`/`ManagerFactory` pair sharing a `reporting_relationship` row, used by every module 13 test that asserts an approval or rejection outcome, so the balance-decrement and no-decrement assertions run against the same two-identity shape.

### 5.3 Append-Only and Immutable-Store Fixtures

Two stores in `docs/05-database-schema.md` §3 are designed never to be overwritten, and their test fixtures are built to prove that rather than merely to populate them:

- **Compensation history** (§3.4 there). A fixture helper inserts an initial `compensation_record`, then performs the application-level "correction" (a new `POST`, per `docs/06-api-contracts.md` §4.13), and returns both the original row's captured state (fetched before the correction) and the post-correction state of both rows, so that every test asserting the append-only property compares against a captured snapshot rather than trusting the ORM's in-memory object, which could reflect a stale cache of the "before" state rather than what the database actually held.
- **Audit log** (§3.1 there). A fixture helper performs a domain action expected to emit an audit event (a login, a record change, a permission grant) and asserts the resulting `audit_log` row's `category` matches one of the six values `docs/05-database-schema.md` §3.1 fixes, rather than asserting only that a row was created — a wrong category is as much a defect as no row at all, since `docs/06-api-contracts.md` §4.1's `category` filter depends on it.

---

## 6. End-to-End Tests

**Tool: Playwright** (`docs/03-tech-stack.md` §9), run against the deployed composition of `docs/04-system-architecture.md` §6 (Caddy, Django/DRF, PostgreSQL, Redis, MinIO, Celery) rather than against a mocked backend, so that the single-origin session-cookie authentication path of ADR-0004 is exercised as deployed — the same reasoning `docs/03-tech-stack.md` §7.1 gives for serving the SPA and the API under one origin in every environment "including local development, so that the authentication path is exercised as deployed."

Each row below is one SRS §4 stimulus/response sequence, named as the SRS names it, with the Playwright test asserting every step of the stated sequence end to end — not the individual API calls the sequence makes, which the module-level test suites of §4 above already cover, but the user-facing path from stimulus to response.

**Scope against `docs/03-tech-stack.md` §9's "every module."** That section requires "functional, validation, permission, integration, browser, and end-to-end testing for every module," and this document does not read that as requiring a Playwright scenario per module. The SRS is authoritative (§1.4 above), and SRS §4 states eleven stimulus/response sequences across seven of the twenty modules — it does not state one for Audit, Mail dispatch, RBAC/IAM, Dashboard, Departments, Reporting Structure, Onboarding, Notification, Compensation and Benefits (beyond the pay-grade assignment below), or Reports (beyond headcount). Inventing a browser scenario for a module the SRS gives no user-facing sequence for would not be testing against the SRS; it would be testing against a scenario this document supplied, which is the same authorship risk §8 below warns against. **Every module still receives the "end-to-end" testing tech-stack §9 requires** — end to end through the layer the module actually exposes a contract at: the API-level integration tests of §3.2 and §4 above exercise a module's endpoints as full HTTP request/response cycles against a real database and a real Celery worker where applicable, which is "end to end" for a module with no distinct SRS-named user-facing flow. Playwright is reserved for the eleven sequences the SRS itself states as user-facing; it is not the only mechanism this plan calls end-to-end testing, and §4's table is where a reader finds each module's actual coverage.

| SRS reference | Sequence | Asserted end state |
|---|---|---|
| §4.1 | Create Employee Record | HR Officer submits the create form; the employee record exists and is retrievable, with a unique employee ID assigned (HRMS-BR-001) |
| §4.1 | Update Employee Record | HR Officer updates an allowed field; the record reflects the update and `employment_history` carries the change (HRMS-FR-010) |
| §4.2 | Create Job Requisition | Recruiter submits a requisition; it exists with an approval status (HRMS-FR-014) |
| §4.2 | Move Candidate to Offer Stage | Recruiter updates a candidate to Offer and generates an offer letter; the offer letter record exists (HRMS-FR-020) |
| §4.3 | Employee Updates Personal Details | Employee updates an allowed field; the update is saved, and an attempt to reach a restricted field (salary, job title, department, status, manager — HRMS-FR-027) through the same form is rejected client-side and, if forced past the client, server-side |
| §4.3 | Manager Approves Request | Manager receives and opens a pending request, approves it; the status updates and the employee is notified (HRMS-FR-034, module 10) |
| §4.4 | Process Payroll | Payroll Officer selects a period, the system calculates allowances and deductions, a distinct approver reviews and approves, and the run finalises with payslips and a bank transfer file generated — this sequence is the one most exposed to the async `202`-and-poll pattern of `docs/06-api-contracts.md` §4.14, and the Playwright test polls the same way the SPA does rather than assuming synchronous completion |
| §4.5 | Generate Headcount Report | HR Officer opens Reporting, selects the headcount report, applies a filter, and the system displays or exports it (HRMS-FR-053, HRMS-FR-054) |
| §4.6 | Assign Employee to Pay Grade | HR Officer opens an employee's compensation profile, selects a pay grade; the system validates and stores the compensation history per the append-only rule §5.3 above already unit-tests, exercised here end to end through the actual form |
| §4.7 | Submit Leave Request | Employee selects a leave type and dates; the system validates balance and routes the request to the manager |
| §4.7 | Approve Leave Request | Manager reviews and approves or rejects; leave status and balance update per HRMS-BR-010/HRMS-BR-011, exercised end to end through the actual approval screen |

### 6.1 Module Coverage Matrix

Every application module (`docs/04-system-architecture.md` §4, modules 1 to 17) appears below exactly once, against either the SRS §4 sequence that exercises it in Playwright or the reason it has none and the mechanism that instead gives it end-to-end coverage per §6's scoping note above. This is the coverage tech-stack §9's "for every module" is checked against; a module missing from this table is a gap in this document, not an assumed exclusion.

| # | Module | SRS §4 sequence(s) driving Playwright | If none: end-to-end coverage |
|---|---|---|---|
| 1 | Audit | — | No SRS §4 sequence names the audit read surface. Covered by `docs/06-api-contracts.md` §4.1's endpoints exercised as full request/response cycles in §4's module-1 permission and functional tests above, including the eight-role denied-path sweep |
| 2 | Mail dispatch | Consumed within Process Payroll (§4.4), Employee Updates Personal Details' password-reset path is Authentication's, not this module's own sequence | No SRS §4 sequence names mail dispatch directly — it is infrastructure a sequence consumes, not a user-facing flow of its own (`docs/04-system-architecture.md` §3.2: "it knows nothing about why a message is sent"). Covered by the Celery task, retry, and delivery-failure-logging tests of §4's module-2 row |
| 3 | Authentication | Login is the precondition of every sequence above, not a named sequence itself | Login, logout, session expiry, and HRMS-NFR-024 second-factor presentation/enrolment/recovery have no SRS §4 stimulus/response sequence of their own — SRS §4 begins after authentication. Covered by §4's module-3 row (functional tests for presentation, enrolment, recovery, and the denied paths on each) |
| 4 | RBAC / IAM | — | No SRS §4 sequence names role granting or the `is_superuser` prohibition. Covered by §4's module-4 row: the self-grant refusal and privileged-grant approval are exercised as full API request/response cycles, including the database-constraint bypass test of §3.4 |
| 5 | Departments | — | SRS §4 has no requisition-independent departments sequence; department assignment is folded into Create Employee Record's field set, not its own stimulus/response pair. Covered by §4's module-5 row (HRMS-BR-002, retire-not-delete) |
| 6 | Employee Management | §4.1 Create Employee Record; §4.1 Update Employee Record | — |
| 7 | Reporting Structure | — | No SRS §4 sequence names a manager change as its own flow. Covered by §4's module-7 row, including the skip-level negative-visibility test |
| 8 | Recruitment | §4.2 Create Job Requisition; §4.2 Move Candidate to Offer Stage | — |
| 9 | Onboarding | Implicit in Move Candidate to Offer Stage's downstream conversion, not itself named as a stimulus/response pair — HRMS-BR-013's conversion point has no SRS §4 sequence of its own | Covered by §4's module-9 row: the atomic employee/checklist creation test stands in for the missing SRS-named sequence, since it is the one assertion with a real functional consequence if it fails |
| 10 | Notification | Consumed within Manager Approves Request (§4.3) and Approve Leave Request (§4.7); no sequence exercises the notification feed itself (mark-read, own-record scoping) | Own-record scoping and mark-read are covered by §4's module-10 row |
| 11 | Employee Self-Service | §4.3 Employee Updates Personal Details | — |
| 12 | Manager Self-Service | §4.3 Manager Approves Request | — |
| 13 | Leave Management | §4.7 Submit Leave Request; §4.7 Approve Leave Request | — |
| 14 | Dashboard | Implicit precondition of every sequence above (each actor's landing page), not itself a named sequence | No SRS §4 sequence names the dashboard as its own stimulus/response pair. Covered by §4's module-14 row, asserting the Executive aggregate-only rule specifically |
| 15 | Compensation and Benefits | §4.6 Assign Employee to Pay Grade | Pay-grade assignment is the only SRS §4 sequence for this module; salary structures, bonus cycles, allowances, and benefits enrolment have none. Covered by §4's module-15 row, including the append-only column-comparison test |
| 16 | Payroll | §4.4 Process Payroll | — |
| 17 | Reports | §4.5 Generate Headcount Report | Leave-utilization and payroll-cost reports have no SRS §4 sequence of their own — only headcount does. Covered by §4's module-17 row, including the Executive aggregate-only disclosure test |

Modules 18 to 20 (Testing, UAT, Deployment) own no endpoint and no visibility rule (`docs/06-api-contracts.md` §4) and are process modules this table does not apply to, on the same reasoning `docs/05-database-schema.md` §4 gives them no table.

**What this level does not attempt.** Some sequences above are multi-actor: Process Payroll names a distinct approver besides the Payroll Officer who initiates, and Manager Approves Request and Approve Leave Request each presuppose an earlier submission by the employee the manager did not perform. Where the SRS states the hand-off as part of one sequence, the Playwright test drives both actors within that one run — logging in as each in turn, as the sequence itself requires — and that hand-off is in scope. **What is out of scope is elapsed time, not a second actor.** None of the eleven sequences the SRS states spans real calendar time (a payroll cycle spanning a full pay period, an onboarding checklist completed over several days); those are exercised as unit and integration tests against the underlying state machine (§4 above), not as a single Playwright run, since a browser-driven test that spans real elapsed time is not a practical CI artifact and the SRS does not state the sequences that way.

---

## 7. Nonfunctional Requirements: What Is Testable Now

`docs/02-project-plan.md` §9 states this document's own limit before it is written: "none of it catches a misunderstood requirement." Two of the nonfunctional requirement groups have a sharper limit, stated here rather than glossed over, following the pattern `docs/02-project-plan.md` §8.2 already set for M16 Payroll: **a mechanism can be built and exercised now; whether it satisfies the requirement cannot be verified until an open TBD closes.**

### 7.1 Response-Time and Load Requirements (HRMS-NFR-001 to HRMS-NFR-006)

SRS §5.1 fixes these as 95th-percentile thresholds, measured at the application server boundary, over a rolling 60-minute window, at the concurrent load HRMS-NFR-006 states — **against a data volume (TBD-016) and, for HRMS-NFR-005, an elapsed-time threshold (TBD-017) neither of which this project can supply** (`docs/02-project-plan.md` §8.1: both "not resolvable by this project," blocking M18 Testing until 2026-10-20).

Two things can be built without either TBD, and this document specifies both so they are ready when the data arrives rather than designed from scratch at M18:

- **Single-request timing.** A pytest-django suite records wall-clock time for the endpoints HRMS-NFR-001 to HRMS-NFR-004 name (common pages, employee search, profile pages, reports) against a fixture dataset this project generates, and asserts nothing beyond "the mechanism exists and produces a number" until TBD-016 fixes the dataset shape the percentile is meant to be measured against. Per `docs/02-project-plan.md` §8.2's own instruction for this pattern: "a performance figure measured against a dataset this project invented is a measurement of that dataset and is recorded as such; it is not evidence that HRMS-NFR-001 to HRMS-NFR-005 are met." Every such test's fixture-generation parameters (record count, document volume) are recorded alongside the result, so a reader of a future test run knows which invented dataset produced it.
- **Payroll elapsed time (HRMS-NFR-005).** M16's Celery-based `calculate/` and `finalize/` tasks (§4, row 16) are timed per run as a matter of course, since the async pattern already requires a poll-to-completion test; the elapsed time is recorded and compared against TBD-017 once it exists, and against nothing until then.

**What is not built without a tool selection this document does not make.** HRMS-NFR-006's concurrent-load condition — 200 simultaneous users sustaining HRMS-NFR-001 to HRMS-NFR-005 — requires a load-generation tool that issues concurrent requests at scale, and `docs/03-tech-stack.md` §9's QA tooling table names none: pytest-django, factory_boy, Vitest/RTL, Playwright, and drf-spectacular each verify correctness or a single request's behaviour, not concurrent throughput. This document does not select one. Introducing a load-testing tool is the kind of technology decision `docs/03-tech-stack.md` made for every other layer of this system, and this document is not the place to make it by implication — the same reasoning that document itself gives for declining to invent things below its altitude (`docs/06-api-contracts.md` §7's second-factor-mechanism item is the precedent). **This is recorded as an open item (§9 below) rather than resolved here**, and HRMS-NFR-006 is not verifiable by any test this document specifies until it is.

### 7.2 Availability and Backup Requirements (HRMS-NFR-012, HRMS-NFR-035)

`docs/04-system-architecture.md` §7 already states these are "explicitly deployment-dependent and open under TBD-003" and "not satisfied by [the architecture document], and this document does not claim otherwise." No test in this plan verifies 95–98% availability or a backup regime, for the same reason: both are properties of a hosting target ADR-0009 defers, not of application code this project builds. M20 Deployment's own scope (`docs/02-project-plan.md` §8.3) is unaffected by this document and is not restated here.

---

## 8. What This Plan Does Not Catch

`docs/02-project-plan.md` §9 states this limit for the whole quality approach and directs this document to detail the strategy while stating only the limit. This document does not narrow that statement, and restates it rather than paraphrasing it: **none of the six controls in §3 catches a misunderstood requirement.** The author reads the SRS, builds to that reading, tests against that reading, and accepts at UAT against the same reading. Where a requirement is ambiguous, the misunderstanding survives permission tests, contract tests, boundary validation, database constraints, automated review, and end-to-end tests alike, because every one of them is written by the same person against the same understanding.

**What UAT is, and what plan §11 question 6 leaves open.** SRS §4's stimulus/response sequences are the acceptance criteria M19 UAT exercises, and §6 above is where that exercise lives mechanically. `docs/02-project-plan.md` §11 question 6 asks what UAT means with no operating organisation and no independent user, and it is not resolved by this document or by the plan: the sole participant is the author, who wrote both the code and the SRS it is measured against. This document does not resolve that question either. It records, per the same question, that the Playwright suite of §6 is self-verification against SRS §4 by the person who authored both sides of the comparison, not acceptance by an independent user class — and that this is what the term "UAT" will mean for M19 unless the project owner answers question 6 differently before M19 begins.

`docs/02-project-plan.md` §8.1's TBD register is this project's partial defence against the ambiguities that are visible enough to have been named — TBD-005, TBD-006, TBD-007, TBD-008, TBD-014, TBD-016, TBD-017 each name a specific gap this document's per-module and nonfunctional sections above route around rather than paper over. It is not a complete defence, and the SRS's ambiguities beyond Appendix C are not enumerated anywhere, in this document or any other.

---

## 9. Open Items Inherited or Newly Surfaced

This document introduces one new open item and restates the ones from prior documents that bear directly on testing.

**Newly surfaced by this document:**

- **Load-generation tool for HRMS-NFR-006.** `docs/03-tech-stack.md` §9 names no tool capable of concurrent-load testing at the 200 simultaneous users SRS v1.1 pins the requirement to (`docs/01-srs.md` §5.1's own revision history: "a workload pinned to 200 concurrent users"). §7.1 above declines to select one by implication. This is a technology decision at the same altitude as `docs/03-tech-stack.md` §9's existing selections and belongs there or in a new ADR, not in this document's prose. Until it is made, HRMS-NFR-006 is not verifiable by any control this plan specifies.

**Restated from prior documents, because they bear on testing and a reader of this document should not assume they were resolved by it:**

- **TBD-005 (final payroll statutory rates) and TBD-006 (bank transfer file format).** Open, not resolvable by this project (`docs/02-project-plan.md` §8.1, §8.2). M16's tests verify the calculation engine against the versioned rate-table structure and the bank-file interface, not against confirmed values or a confirmed format; "M16 completes as *calculation engine built, statutory correctness unverified*" (plan §8.2), and this document's module 16 row (§4) is built to that limit rather than around it.
- **TBD-007 (HR approval workflows) and TBD-008 (leave policy rules).** Open, not resolvable by this project. HRMS-FR-068's "unless policy allows" condition (§4, row 13) cannot be given a concrete test until TBD-008 closes; the test asserts the mechanism against a documented provisional policy, per the pattern `docs/02-project-plan.md` §8.2 sets generally.
- **TBD-016 and TBD-017 (organisation size, data volumes, payroll elapsed-time threshold).** Open, not resolvable by this project, blocking M18 Testing until 2026-10-20 per plan §8.1. §7.1 above builds the timing mechanism now and records every measurement against an invented dataset as a measurement of that dataset, not as evidence HRMS-NFR-001 to HRMS-NFR-005 are met, per plan §8.2's instruction.
- **TBD-003 (hosting target).** Open by decision (ADR-0009). §7.2 above states no availability or backup test exists in this plan because both properties are deployment-dependent, not because they are out of scope.
- **Plan §11 question 6 (what UAT means with no independent user) and question 7 (what Handover means with no recipient).** Both open. §8 above states what question 6 means for this document's own scope until the owner answers it; question 7 does not bear on this document and is not restated further here.

---

## 10. Traceability

| Testing plan element | Serves |
|---|---|
| §3.1 permission tests | ADR-0005; `docs/07-iam-rbac.md` §4.2, §5, §6, §7.3, §4.4; `docs/04-system-architecture.md` §2 |
| §3.2 contract tests | `docs/03-tech-stack.md` §9; `docs/06-api-contracts.md` §1.2, §2.7 |
| §3.3 boundary validation | `docs/03-tech-stack.md` §6.1 |
| §3.4 database constraints | `docs/03-tech-stack.md` §5.1; ADR-0003; `docs/05-database-schema.md` §3.5, §6; HRMS-DR-001 to HRMS-DR-010 |
| §3.5 automated review | `docs/02-project-plan.md` §3, §9; `docs/agents/issue-tracker.md` |
| §3.6, §6 end-to-end tests | `docs/03-tech-stack.md` §9; SRS §4 |
| §4 per-module obligations | `docs/02-project-plan.md` §6.1 build order; `docs/04-system-architecture.md` §2, §4; `docs/06-api-contracts.md` §4; `docs/07-iam-rbac.md` §4.2, §5 |
| §5 test data strategy | `docs/03-tech-stack.md` §9; `docs/05-database-schema.md` §3.1 to §3.5 |
| §7 nonfunctional testing | SRS §5.1; `docs/02-project-plan.md` §8.1, §8.2; `docs/04-system-architecture.md` §7 |
| §8 what this plan does not catch | `docs/02-project-plan.md` §9, §11 question 6 |
| §9 open items | `docs/02-project-plan.md` §8.1, §11; ADR-0009 |

---

**Sign-off.** Per `docs/02-project-plan.md` §5.2, this milestone is met when the project owner has read this document and accepted it.
