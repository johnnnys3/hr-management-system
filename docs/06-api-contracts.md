# API Contracts

**Human Resource Management System**

| | |
|---|---|
| Version | 1.9 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-16 |
| Status | Draft — pending owner acceptance at M4 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-16 | Initial API contracts document, closing milestone M4 | 1.0 |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.5.** §4.10's Dashboard is module 5 there and module 14 in the plan as of v1.5; every module-numbered heading and cross-reference in §4 is still v1.4. Reconcile at M4 sign-off per plan §5.3, or before Module 5's real implementation begins, whichever comes first | 1.0 (unreconciled) |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.6's Employee Management/Departments swap (modules 5 ↔ 6 in the plan's numbering; §4.3/§4.4 headings below, still v1.4-numbered as module 6 and 7).** No endpoint contract changes; only the heading numbers and any build-order cross-references are stale. Reconcile at M4 sign-off per plan §5.3, or before Module 5's real implementation begins, whichever comes first | 1.0 (unreconciled) |
| John Kessie | 2026-07-18 | **Reconciled with `docs/02-project-plan.md` v1.6, per the two rows above.** Every module-numbered heading and cross-reference in §4 is renumbered to v1.6 (Departments 5, Reporting Structure 7, Recruitment 8, Onboarding 9, Notification 10, Employee/Manager Self-Service 11/12, Leave Management 13, Dashboard 14); section order (§4.1-§4.15) is unchanged, only the module labels and numbers within them. No endpoint, permission, or visibility-rule content changes. Filed as DOC-007 | 1.1 |
| John Kessie | 2026-07-18 | **§8's traceability table omitted HRMS-FR-030 and HRMS-FR-031 entirely — found while scoping Module 12 against DOC-010.** FR-030 (view team members) is addressed by §4.5's `/api/employees/{id}/direct-reports/`, already stated in that row's own text ("the endpoint a Manager Self-Service view ... calls to enumerate its team") but never added to §8's table. FR-031 is `docs/01-srs.md` v1.3's newly marked duplicate of HRMS-FR-064; it is not added, on the same convention DOC-009 set for FR-028/FR-029 — a duplicate requirement is traced through its canonical ID, not re-traced under the restating one. §8 gains a row for FR-030; no endpoint, permission, or visibility-rule content changes. Filed as DOC-010 | 1.2 |
| John Kessie | 2026-07-19 | **§8's traceability table cited HRMS-FR-045 (payroll summary reports) as addressed by §4.14, folded silently into the "HRMS-FR-035 to HRMS-FR-046" range — but §4.14's own endpoint table has no summary-report route, found reviewing PAYROLL-001 against `docs/01-srs.md` §4.4.** Same defect shape as FR-032 at v1.2 of the plan: a requirement genuinely belongs to Reports' aggregate read surface, not Payroll's per-run/per-payslip one. §4.15 gains `/api/reports/payroll-summary/`, same shape as the existing `/api/reports/payroll-cost/` row (Payroll Officer: R full detail; Executive: R aggregate only, HRMS-NFR-019); §8's FR-035–046 range is split to exclude FR-045, which moves to the FR-049–055 Reports line. No other endpoint, permission, or visibility-rule content changes. Matches `docs/02-project-plan.md` v1.11's resolution, owner-confirmed 2026-07-19 | 1.3 |
| John Kessie | 2026-07-19 | **§4.15's endpoint table had no route for HRMS-FR-050 (turnover reports) — named in the FR list on that row and in `docs/01-srs.md` line 566, but absent from the table, found while preparing the Module 17 handoff.** Same defect shape as FR-032 and FR-045 before it: a stated requirement with no endpoint built against it. §4.15 gains `/api/reports/turnover/`, same shape as the existing `/api/reports/headcount/` and `/api/reports/leave-utilization/` rows (HR Officer, HR Administrator: R; Manager: R team-level; Executive: R aggregate only, HRMS-NFR-019), computing hire/termination-date arithmetic over a period rather than a point-in-time count. No other endpoint, permission, or visibility-rule content changes. Owner-confirmed 2026-07-19 | 1.4 |
| John Kessie | 2026-07-21 | **§4.6's five `IsRecruiter`-gated endpoints (job postings, candidates, candidate applications, interviews, offers) never granted HR Officer any access, even though `docs/07-iam-rbac.md` §4.2's Recruitment row has stated "HR Officer: R" since that matrix was first written — found building FRONTEND-ONBOARD-001 (PR #97), where HR Officer has no way to reach an accepted offer to trigger HRMS-BR-013 conversion without it.** Not a new policy decision, a correction to match the IAM matrix's own already-documented intent. `backend/recruitment/permissions.py`'s `IsRecruiter` widened to grant HR Officer read (GET only; all writes, including `/api/offers/{id}/decide/`, remain Recruiter-only). §4.6's five affected rows updated. No change to `/api/job-requisitions/*` (a separate permission class, unaffected) | 1.5 |
| John Kessie | 2026-07-21 | **§4.6's `/api/applications/{id}/offer/` row never documented `offered_pay_grade`, even though COMP-001 (PR #73) added `offer_letter.offered_pay_grade_id` as a real, client-settable FK into `pay_grade` — found via FRONTEND-RECRUIT-001's Issue Offer form having no field to set it (issue #98).** `backend/recruitment/serializers.py`'s `OfferLetterSerializer` gains `offered_pay_grade` (writable `PrimaryKeyRelatedField`, nullable per the model); §4.6's offer row documents it. Recruiter — the only role that issues offers — had no way to look up a valid pay grade id, since §4.13's `/api/pay-grades/` grants read only to HR Administrator, HR Officer, Payroll Officer per `docs/07-iam-rbac.md` §2.4's compensation-access split; §4.13's row is widened to grant Recruiter a blind-selection read (`id`/`name` only, no `min_salary`/`max_salary`), preserving §2.4's intent that Recruiter never sees salary figures. Owner-confirmed 2026-07-21 | 1.6 |
| John Kessie | 2026-07-21 | **§4.10's Dashboard note said Executive's `aggregates` section returns `null` "until [module 17 Reports is built]" — Module 17 merged 2026-07-19 (PR #83), which deliberately left this wiring out of its own scope as a flagged follow-up (issue #100).** `backend/dashboard/views.py`'s Executive branch now calls `reports.services`' five report builders directly with `scope='aggregate'`, the same scope Executive resolves to at `/api/reports/*`, rather than round-tripping through those endpoints. Turnover has no caller-supplied period on this no-query-param endpoint; it defaults to the trailing 365 days, stated in the row's own note. §4.10's row updated to describe the real shape. No permission or visibility-rule content changes — Executive's access was already granted, only the placeholder is replaced | 1.7 |
| John Kessie | 2026-07-21 | **§4.7 only exposed `GET /api/onboarding-checklists/{id}/` — there was no way to look up a checklist by `employee_id` or `application_id`, only by an id learned once, at `POST /api/onboarding/convert/`'s response — found building FRONTEND-ONBOARD-001, PR #97 (issue #101).** `/api/onboarding-checklists/` gains a `GET` list, filterable by `employee_id`/`application_id`, same shape as `/api/leave-requests/`'s `status`/`leave_type_id` filters. Same permission as the existing detail endpoint (HR Officer: R; HR Administrator, Recruiter: R). No new access granted, no schema change | 1.8 |
| John Kessie | 2026-07-22 | **§4.12's `/api/leave-types/` row only granted HR Officer/HR Administrator read — a Manager viewing their team's leave requests gets a 403 resolving leave-type names, found live-testing FRONTEND-LEAVE-001 (issue #125).** `backend/leave/permissions.py`'s `CanAccessLeaveTypes` widened to also grant Manager read (`GET` only). Same shape as the Recruitment `IsRecruiter`/HR-Officer fix at v1.5. No schema or write-access change | 1.9 |

---

## 1. Introduction

### 1.1 Purpose

This document designs the REST API surface for the Human Resource Management System: the resources, endpoints, request and response shapes, and — for every endpoint returning employee-scoped data — the permission grant and visibility rule that gate it, organised against the module boundaries `docs/04-system-architecture.md` fixed and the tables `docs/05-database-schema.md` fixed.

It does not decompose the system into modules, which `docs/04-system-architecture.md` has done; it does not design the schema, which `docs/05-database-schema.md` has done; and it does not choose the access-control model, which `docs/07-iam-rbac.md` has done. Where this document restates a decision from an earlier one, it is carrying that decision into an endpoint contract, not re-deciding it.

### 1.2 What This Document Is, and Is Not

**This is the human-readable design document that precedes and constrains the generated OpenAPI schema, not a hand-maintained OpenAPI file.** `docs/03-tech-stack.md` §9 fixes `drf-spectacular` as the tool that generates the OpenAPI schema from the API implementation once code exists, and that generated schema — not this document — is the API Specification deliverable's source of truth from the point development begins. This document is upstream of that: it fixes resource shapes, endpoint conventions, and permission gates before a single view is written, so that implementation has a contract to build against and `drf-spectacular`'s output has something to be checked against rather than being the first record of the decision. No `.yaml` or `.json` OpenAPI artifact is produced by this milestone.

### 1.3 Intended Audience

Developers writing Django REST Framework views and serializers against this contract, and the project owner reviewing it before development begins.

### 1.4 Relationship to Prior Documents

This document is downstream of five documents it does not revise:

- **`docs/01-srs.md`** (v1.1) — the requirement set, and specifically its 71 functional requirements and the business rules of §5.5. Authoritative; where this document and the SRS disagree, the SRS governs.
- **`CONTEXT.md`** — the domain glossary. Where a term is defined there (Employee vs. User, visibility rule, mail dispatch vs. notification), this document uses it as defined.
- **`docs/03-tech-stack.md`** (v1.0) and **ADR-0002, ADR-0004** — Django REST Framework, session-cookie authentication with CSRF verification on state-changing endpoints, and `drf-spectacular` as the schema-generation tool this document precedes rather than replaces (§1.2 above).
- **`docs/04-system-architecture.md`** (v1.0) — the seventeen-application-module catalog, the visibility-rule seam (§3.3), and the audit/notification emission pattern (§3.1, §3.2) every endpoint below is designed against.
- **`docs/05-database-schema.md`** (v1.0) — the table and column names this document's resource shapes map onto. Endpoint request and response bodies name schema columns; where a resource's shape does not match a table one-to-one (Allowance, Deduction — see §4.11 and §4.16 below), this document states the split rather than inventing a single resource that hides it.
- **`docs/07-iam-rbac.md`** (v1.6) — produced out of order (plan §5.3), and binding on this document in the way plan §5.3 states directly: "`docs/07-iam-rbac.md` §4.2 assigns permissions per module against named requirement ranges. `docs/06-api-contracts.md` inherits that matrix as the specification of what each endpoint gates." Every endpoint's permission column below cites a cell of that matrix; none re-derives access control from scratch. Likewise §5's visibility-rule table is inherited as the specification of which rows an endpoint returns, not re-decided per endpoint.

### 1.5 Scope

In scope: the resource catalog for every module in `docs/04-system-architecture.md` §4 that owns data or exposes a read surface over data another module owns (§4 below), the request/response shape of each endpoint, the permission grant and visibility rule gating it, and the conventions (§2) that apply uniformly — URL structure, pagination, filtering, error shape, and authentication.

Out of scope, per `CONTEXT.md` "Scope boundary" and SRS §6.4: no endpoint exists for biometric attendance, AI recruitment screening, learning management, performance appraisal, complex shift scheduling, ERP/accounting integration, automatic tax filing, direct bank integration, loan management, travel and expense management, disciplinary case management, union management, multi-country payroll, or chatbot support. A request that would need one is a scope change requiring SRS revision, not an API addition.

This document does not reopen the three module placements plan §11 closed, the visibility-rule pattern, the role model, the permission matrix, ADR-0001 to ADR-0011, or any table or column decision in `docs/05-database-schema.md`. Where an endpoint's shape depends on one of those, it cites the source rather than re-arguing it.

---

## 2. Conventions

### 2.1 URL Structure and Versioning

Every endpoint is served under `/api/`, proxied by Caddy to the Django/DRF deployable per `docs/03-tech-stack.md` §7.1's single-origin composition. Resource collections are plural nouns in `kebab-case` matching the owning module's primary table, e.g. `/api/employees/`, `/api/leave-requests/`, `/api/payroll-runs/`. A single resource is addressed by its surrogate `id` (`docs/05-database-schema.md` §2.1): `/api/employees/{id}/`.

No version segment (`/api/v1/`) is included. The system has one deployable, one client (the SPA of `docs/03-tech-stack.md` §6), and no third-party API consumer (`docs/03-tech-stack.md` §8.1) — the conditions under which a version segment earns its cost do not hold here, and introducing one preemptively would be scope `docs/03-tech-stack.md` did not select. Should an external consumer or a native client enter scope, `docs/03-tech-stack.md` §8.1 already states that ADR-0004 is revisited rather than worked around; a version segment would enter at the same time, on the same reasoning.

### 2.2 Authentication and CSRF

Every endpoint except login (`POST /api/auth/login/`) and password reset (`POST /api/auth/password-reset/`, §4.2 — necessarily pre-authentication, since its caller has no session to authenticate with) requires an authenticated session per ADR-0004. The session cookie is `HttpOnly`, `Secure`, `SameSite=Lax` (`docs/03-tech-stack.md` §8.1); no endpoint accepts a bearer token. Every state-changing endpoint (`POST`, `PATCH`, `PUT`, `DELETE`) requires the CSRF token DRF's `SessionAuthentication` checks by default, and this document does not disable that check on any endpoint — `docs/03-tech-stack.md` §8.1 is explicit that CSRF verification "is not to be disabled."

An unauthenticated request to any endpoint but login returns `401`. An authenticated request lacking the action-level permission a §4 endpoint states returns `403`. A request for a specific object that exists but falls outside the caller's visibility rule (§2.5 below) returns `404`, not `403` — the deny-by-default principle (`docs/07-iam-rbac.md` §1.3) extends to not confirming a record's existence to a caller who cannot see it, the same reasoning DRF's `get_object_or_404` applies by default when a queryset is pre-scoped.

### 2.3 Pagination

Every collection endpoint (`GET` on a plural resource) is paginated using DRF's `PageNumberPagination`, page size 25, overridable per request with `?page_size=`, capped at 100. Response envelope:

```json
{
  "count": 143,
  "next": "https://.../api/employees/?page=3",
  "previous": "https://.../api/employees/?page=1",
  "results": [ ... ]
}
```

This is DRF's standard shape, chosen because `docs/03-tech-stack.md` §6.2 already commits to Ant Design's `Table` component, whose pagination control consumes a total count and a page of rows — the same shape `PageNumberPagination` produces without adaptation. Cursor pagination was not adopted: no endpoint in §4 serves a feed at a scale (`docs/03-tech-stack.md` §3: 50–200 concurrent users) where offset pagination's cost becomes material, and cursor pagination trades away the page-number jump Ant Design's control offers by default.

### 2.4 Filtering, Sorting, and Search

Collection endpoints accept `?ordering=field` and `?ordering=-field` (DRF's `OrderingFilter`) over the fields each endpoint's table in §4 lists as filterable, and `?search=` (DRF's `SearchFilter`) where §4 marks a text-search field. HRMS-FR-009 ("search and filter employee records") is satisfied by the employee collection endpoint's filter set (§4.3); `docs/05-database-schema.md` §8 leaves index selection to this document, and §4.3 below states which `employee` columns are indexed filter targets: `department_id`, `job_title_id`, `employment_status`, and `search` over `first_name`/`last_name`/`employee_number`.

Equality filters on foreign-key and enum columns use the column name directly as a query parameter (`?department_id=4`, `?employment_status=active`). No endpoint accepts an arbitrary filter expression language; the filter set is the finite list each §4 row states, because an open-ended filter surface over employee-scoped data is itself a disclosure surface the visibility rule (§2.5) would have to be re-verified against for every possible expression, which this design does not need to take on.

### 2.5 Visibility Scoping

**Every endpoint returning employee-scoped data obtains its queryset through the module's `visible_to(user)` method**, per `docs/04-system-architecture.md` §3.3 and `docs/07-iam-rbac.md` §5. This document states, per endpoint in §4, which visibility rule applies; it does not restate the rule's predicate, which `docs/07-iam-rbac.md` §5 already fixes and this document inherits rather than redesigns. An endpoint's `list` and `retrieve` actions apply the same rule; a `retrieve` for an `id` outside the caller's scope behaves as stated in §2.2 — `404`, not a distinguishing `403`.

### 2.6 Action-Level Permission

Each endpoint's permission column names the role(s) from `docs/07-iam-rbac.md` §4.2 whose matrix cell covers the operation, and the DRF permission class enforcing it is the corresponding Django group/permission check, per ADR-0005 and `docs/03-tech-stack.md` §8.2. Where §4.2's cell is `‡` (grantable, not fixed by that design — payroll finalisation approval), the endpoint's permission is `payroll.approve_payroll_run`, held by whichever role the deploying organisation grants it to, per `docs/07-iam-rbac.md` §4.4; this document states the permission name, not a role, for that one endpoint (§4.16.4).

### 2.7 Error Shape

Every non-2xx response returns:

```json
{
  "error": {
    "code": "validation_error",
    "message": "end_date cannot be earlier than start_date.",
    "fields": { "end_date": ["Must not precede start_date."] }
  }
}
```

`code` is a fixed machine-readable string. The endpoint-specific codes above (`validation_error`, `permission_denied`, `not_found`, `not_authenticated`, `conflict`, `self_approval_forbidden`) cover every error §4's endpoints raise deliberately; DRF's other built-in exception types are mapped to `method_not_allowed`, `throttled`, and `server_error` respectively, so that "every non-2xx response returns this shape" holds for the framework's own exceptions too, not only the ones this document names per endpoint. `message` is a human-readable summary, and `fields` is present only on `400` field-validation errors, keyed by field name, matching DRF's default `ValidationError` detail shape wrapped in the envelope above. This is a thin wrapper over DRF's default exception handling — a custom `EXCEPTION_HANDLER` supplies the `error` envelope and `code`, and the underlying DRF detail becomes `message`/`fields` — chosen so that the SPA's Zod boundary validation (`docs/03-tech-stack.md` §6.1) checks one stable shape across every endpoint rather than DRF's un-enveloped default, which varies by exception type. No endpoint in §4 departs from this shape; deviation is not offered as a per-endpoint option.

### 2.8 Write Semantics

`POST` creates; `PATCH` performs a partial update; no endpoint in this design uses `PUT`, since every writable resource below accepts partial updates and a full-replacement semantics adds a second update path with no requirement behind it. `DELETE` is not implemented on any business-record endpoint, per `docs/05-database-schema.md` §2.3: employee, payroll, compensation, leave, and recruitment resources transition status through a `PATCH` to a `status`-bearing field or a dedicated action endpoint (e.g. `POST /api/leave-requests/{id}/approve/`), never through HTTP `DELETE`. The narrow exceptions — deactivating (not deleting) reference data such as a department or leave type — are `PATCH {"is_active": false}` against the same resource, not a separate deactivation endpoint, since `is_active` is an ordinary field per `docs/05-database-schema.md` §2.3 and no additional side effect attaches to setting it.

### 2.9 Action Endpoints for State Transitions

Where a resource's `status` transition is gated by an approval or a constraint beyond ordinary field validation — leave approval (HRMS-BR-009), payroll finalisation (HRMS-BR-008), role-grant approval (`docs/07-iam-rbac.md` §7.3), offer decisions (HRMS-FR-021) — the transition is a dedicated `POST /api/{resource}/{id}/{action}/` endpoint rather than a `PATCH` to `status`. This keeps the constraint (who may call it, what else it writes — an `approved_by`, a `decided_at`, an audit entry) attached to one endpoint with its own permission and its own request body, rather than overloading a generic `PATCH` with per-value side effects a client would have to know about implicitly. Each such endpoint is listed individually in §4 rather than folded into its resource's general write row.

---

## 3. Permission and Visibility Reading Guide

§4's endpoint tables use two columns, both citations rather than restatements:

**Permission** — the role(s) and operation from `docs/07-iam-rbac.md` §4.2's matrix. A cell reading "HR Officer: C, R, U" against Employee records means the endpoint performing that operation requires the HR Officer group; where §4.2 lists more than one role for an operation (e.g. HR Administrator and HR Officer both read employee records), the endpoint's permission is satisfied by any listed role, consistent with §6.1's additive-roles reasoning in that document — a user need only hold one of the listed roles, not all.

**Visibility** — the module's rule from `docs/07-iam-rbac.md` §5. Where §5 states "—" for a role against a resource, that role's requests to the endpoint are rejected at the permission layer (§2.6) before a visibility rule is ever evaluated; the "—" is not restated as an empty visibility clause per endpoint.

Two endpoints depart from citing an existing matrix cell because no cell exists for them: `notification` (own-record equality, `docs/04-system-architecture.md` §3.2, not a `docs/07-iam-rbac.md` §5 row) and `second_factor`/`role_grant_request` (IAM mechanism itself, gated by the constraints `docs/07-iam-rbac.md` §7.3 states directly rather than by a matrix cell). Both are marked as such in §4.2 and §4.4 below.

---

## 4. Resource and Endpoint Catalog by Module

Modules are numbered per `docs/04-system-architecture.md` §4. A module owning no table (§4's "no entry" modules — Dashboard, Employee/Manager Self-Service, Reports) is given a read-surface entry below rather than omitted, since it exposes endpoints even though `docs/05-database-schema.md` gives it no table of its own. Modules 18 to 20 (Testing, UAT, Deployment) are process modules and own no endpoint, per the same reasoning `docs/05-database-schema.md` §4 gives them no table.

### 4.1 Module 1 — Audit

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/audit-log/` | GET | System Administrator: R (`docs/07-iam-rbac.md` §4.2) | System Administrator only; no other role reaches this endpoint at all (§5 "—" for every other role) | Filterable by `category`, `actor_user_id`, `target_type`, `occurred_at` range. No `POST`/`PATCH`/`DELETE` — `audit_log` is written only by the emitting module's own service code (`docs/04-system-architecture.md` §3.1), never by a client request, so this module exposes no write endpoint of its own |
| `/api/employees/{id}/audit-history/` | GET | HR Administrator, HR Officer, System Administrator (HRMS-FR-010 read access; §4.2's Employee records row for the base resource) | A filtered read of `audit_log` where `target_type = 'employee'` and `target_id = {id}` (`CONTEXT.md` — audit history is not a second store) | Not a second table's endpoint; this is `/api/audit-log/` pre-filtered, per `docs/05-database-schema.md` §3.1's "filtered read, not a second table." Access follows the base Employee records permission, not the Audit module's own System-Administrator-only row, since the requirement (HRMS-FR-010) is scoped to employee-record history, a different read surface than the full log |

### 4.2 Module 3 — Authentication

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/auth/csrf/` | GET | None (pre-authentication) | n/a | Sets the `csrftoken` cookie via `ensure_csrf_cookie`, no response body. DRF's `SessionAuthentication.enforce_csrf` (§2 above) needs this cookie present before the SPA's first state-changing call; found undocumented by the `contracts` app's M18 contract-test suite, matching the view's own docstring ("should be folded into that document on review") |
| `/api/auth/login/` | POST | None (pre-authentication) | n/a | Body: `email`, `password`. Uniform response on failure regardless of whether the account exists (`CONTEXT.md` "Deployment conditions" — a varying response discloses account existence). Emits `login_attempt` to `audit_log` |
| `/api/auth/logout/` | POST | Authenticated | n/a | Invalidates the server-side session (ADR-0004) |
| `/api/auth/me/` | GET | Authenticated | Own session only | Returns the caller's `user_account` fields, derived role set (Employee/Manager, `docs/07-iam-rbac.md` §3), and assigned groups — the SPA's one call for "who am I and what can I do," since no client-side token carries this the way a bearer token would elsewhere |
| `/api/auth/password-reset/` | POST | None (pre-authentication) | n/a | Body: `email`. Uniform response regardless of send success (ADR-0011; `CONTEXT.md` "Deployment conditions"). Delivery is best-effort via mail dispatch; a failure is logged to application logs, never `audit_log` (ADR-0011) |
| `/api/auth/password-reset/confirm/` | POST | None (pre-authentication) | n/a | Body: `uid`, `token`, `password`. Completes the reset the row above requests; found undocumented by the `contracts` app's M18 contract-test suite, matching the view's own docstring ("should be folded into that document on review"). `400` with `code: "validation_error"` on an invalid or expired link, `204` on success |
| `/api/auth/phone/` | POST | Authenticated (self only) | Own `user_account` row only | Body: `phone_number` (E.164). Generates a 6-digit code, stored hashed with a 5-minute TTL, sent via SMS dispatch (docs/superpowers/specs/2026-07-26-notifications-email-sms-design.md §4). Submitting a number clears any prior `phone_verified_at` |
| `/api/auth/phone/confirm/` | POST | Authenticated (self only) | Own `user_account` row only | Body: `code`. `400` with `code: "validation_error"` on a wrong or expired code (no distinction surfaced, same posture as password reset), `204` on success; sets `phone_verified_at` |
| `/api/auth/email/confirm/` | POST | Authenticated (self only) | Own `user_account` row only | Body: `code` (added 2026-07-27). Confirms the code sent to a newly created account's email at `/api/users/` POST time; same `validation_error`/`204` posture as phone confirm above. No corresponding `/api/auth/email/` request endpoint — sending happens once, at account creation, not on repeated user request |
| `/api/auth/second-factor/` | POST | Authenticated (self-enrolment only — HRMS-NFR-024: "enrollment shall be performed by the account holder") | Own `second_factor` row only; no endpoint lets one user enrol another's factor | Creates `second_factor` (`docs/05-database-schema.md` §4.2). Emits `second_factor_event` to `audit_log` |
| `/api/auth/second-factor/recovery-requests/` | POST | Authenticated (self only, same reasoning as enrolment) | Own request only | Creates `second_factor_recovery_request` (pending). No matrix cell — mechanism `docs/07-iam-rbac.md` §7.3/§4.2 module 4 fixes directly |
| `/api/auth/second-factor/recovery-requests/{id}/decide/` | POST | Holder of the deployment-designated recovery-approver permission (`docs/07-iam-rbac.md` §8 — deferred to deployment) | The approver must not administer the requester's credentials — an application-code eligibility check, not a queryset scope (`docs/05-database-schema.md` §4.2) | Body: `{"decision": "approved" \| "denied"}`. `approved`/`denied` sets `status`, `decided_at`, `approver_user_id` |

### 4.3 Module 6 — Employee Management

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/employees/` | GET | Employee: R own; Manager: R direct reports; HR Officer, HR Administrator: R all; Payroll Officer: R (payroll fields only, §4.13 below) (`docs/07-iam-rbac.md` §4.2) | Per role, `docs/07-iam-rbac.md` §5's Employee records row | Filterable: `department_id`, `job_title_id`, `employment_status`. Searchable: `first_name`, `last_name`, `employee_number` (HRMS-FR-009, §2.4 above) |
| `/api/employees/` | POST | HR Officer: C (`docs/07-iam-rbac.md` §4.2) | n/a (creation, not a read) | Body maps to `employee` (`docs/05-database-schema.md` §4.5): `employee_number`, `first_name`, `last_name`, `date_of_birth`, `department_id`, `job_title_id`, `hire_date`. `employment_status` defaults `active` and is not client-settable at creation — HRMS-FR-027 forbids an employee editing their own status, and this endpoint's caller is HR, not the employee, but the status transition endpoint below is the one path that changes it, keeping the rule uniform regardless of caller |
| `/api/employees/{id}/` | GET | Employee: R own; Manager: R direct reports; HR Officer, HR Administrator: R all; Payroll Officer: R (payroll fields only, §4.13 below) | Same as list | |
| `/api/employees/{id}/` | PATCH | HR Officer: U (full record); HR Administrator: U status only (`docs/07-iam-rbac.md` §4.2's "R, U status" cell) | HR Administrator/Officer: all | HR Administrator's `PATCH` is restricted to `employment_status` at the serializer layer — a narrower write scope than HR Officer's, per the matrix cell distinguishing "R, U status" from "C, R, U." A status change also writes `employment_history` (`docs/05-database-schema.md` §4.5) |
| `/api/employees/me/` | GET, PATCH | Employee: R, U own (self-service profile, HRMS-FR-025 to HRMS-FR-027) | Own record only | The Employee Self-Service (module 11) surface over this same table — see §4.11. `PATCH` here is restricted to non-master fields (HRMS-FR-027: salary, job title, department, status, and manager are not employee-writable); the serializer for this endpoint is a distinct, narrower one from `/api/employees/{id}/`'s HR-facing serializer, not the same serializer with a permission check bolted on, so that a future field addition to the HR serializer does not silently become employee-writable |
| `/api/employees/{id}/employment-history/` | GET | Same as `/api/employees/{id}/` read | Same as `/api/employees/{id}/` | Read-only over `employment_history` (`docs/05-database-schema.md` §4.5); written only by the status/department/job-title/manager-change endpoints, never directly |
| `/api/employees/{id}/documents/` | GET | HR Officer: R; Employee: R own (`docs/07-iam-rbac.md` §4.2) | Employee: own only; HR Officer: all | |
| `/api/employees/{id}/documents/` | POST | HR Officer: C (`docs/07-iam-rbac.md` §4.2) | n/a | Multipart upload. Server validates content type by inspection and size server-side (ADR-0007, `docs/05-database-schema.md` §4.5); `object_key` is generated, never taken from the client filename |
| `/api/employees/{id}/documents/{doc_id}/download/` | GET | HR Officer: R; Employee: R own | Same as documents list | Returns a short-lived signed URL (ADR-0007 — the bucket is private, no document is served from a directly addressable URL), not the file bytes |
| `/api/employees/{id}/emergency-contacts/` | GET, POST | HR Officer: C, R (grouped under Employee records, HRMS-FR-007) | Same as `/api/employees/{id}/` | Maps to `emergency_contact` (`docs/05-database-schema.md` §4.5) |
| `/api/employees/{id}/emergency-contacts/{contact_id}/` | PATCH | HR Officer: U | Same as `/api/employees/{id}/` | |

### 4.4 Module 5 — Departments and HR Configuration

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/departments/` | GET | HR Administrator: R; HR Officer, Recruiter, Payroll Officer: R (`docs/07-iam-rbac.md` §4.2's HR configuration row) | Organisation-wide; no per-role scoping — departments are reference data, not employee-scoped | |
| `/api/departments/` | POST | HR Administrator: C | n/a | |
| `/api/departments/{id}/` | PATCH | HR Administrator: U | n/a | `PATCH {"is_active": false}` retires rather than deletes (`docs/05-database-schema.md` §2.3) |
| `/api/job-titles/` | GET, POST | Same as departments (§4.2's HR configuration row groups them, `docs/05-database-schema.md` §4.4) | Same as departments | |
| `/api/job-titles/{id}/` | PATCH | Same as departments | Same as departments | `PATCH {"is_active": false}` retires rather than deletes, same as departments |

### 4.5 Module 7 — Reporting Structure

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/reporting-relationships/` | GET | HR Officer, HR Administrator: R (grouped with Employee records; `docs/04-system-architecture.md` §4's module 7 row states "no independent read restriction beyond Module 6's") | Same as Employee records | Filterable: `manager_employee_id` |
| `/api/employees/{id}/direct-reports/` | GET | Manager: R own direct reports; HR Officer, HR Administrator: R any | Manager: rows where `manager_employee_id = {caller's employee id}`; HR: any `{id}` (`docs/07-iam-rbac.md` §5 — direct reports only, no transitive chain) | The endpoint a Manager Self-Service view (module 12, §4.14) calls to enumerate its team; the query is `docs/05-database-schema.md` §4.6's derivation query, not a separate index |
| `/api/employees/{id}/manager/` | PATCH | HR Officer: U (a manager change is a `reporting_relationship` write, grouped under Employee records write access since HRMS-FR-008's relationship is HR-maintained) | n/a | Writes a new `reporting_relationship` row and closes/replaces the prior one (current-state table, `docs/05-database-schema.md` §4.6); also writes `employment_history` with `event_type = 'manager_change'` |

### 4.6 Module 8 — Recruitment

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/job-requisitions/` | GET, POST | Recruiter: C, R; HR Administrator: R (`docs/07-iam-rbac.md` §4.2) | Recruiter: full; HR Administrator: read (`docs/07-iam-rbac.md` §5 — no explicit requisition row; inherits Recruitment module's "Recruiter: full, HR Administrator: read, others: none" from `docs/04-system-architecture.md` §4's module 8 row) | |
| `/api/job-requisitions/{id}/` | GET, PATCH | Recruiter: R, U; HR Administrator: R | Recruiter: full; HR Administrator: read | |
| `/api/job-requisitions/{id}/approve/` | POST | HR Administrator: A (`docs/07-iam-rbac.md` §4.2's "Requisition approval" row) | n/a | Sets `status = 'approved'`, `approved_by`. Distinct endpoint per §2.9, since approval is a gated transition, not an ordinary field write |
| `/api/job-requisitions/{id}/reject/` | POST | HR Administrator: A | n/a | Sets `status = 'rejected'` |
| `/api/job-postings/` | GET, POST | Recruiter: C, R; HR Officer: R (`docs/07-iam-rbac.md` §4.2) | Recruiter: full; HR Officer: read | `POST` requires `requisition.status = 'approved'` — enforced in application code, not a schema constraint (`docs/05-database-schema.md` §4.7 states no such check) |
| `/api/job-postings/{id}/` | GET, PATCH | Recruiter: R, U; HR Officer: R | Recruiter: full; HR Officer: read | |
| `/api/job-postings/{id}/publish/` | POST | Recruiter: U | n/a | Sets `published_at` |
| `/api/candidates/` | GET, POST | Recruiter: C, R; HR Officer: R | Recruiter: full; HR Officer: read | `email` is not unique at this layer either (`docs/05-database-schema.md` §4.7 — a candidate may apply more than once); this endpoint does not attempt to deduplicate candidates by email |
| `/api/candidates/{id}/` | GET, PATCH | Recruiter: R, U; HR Officer: R | Recruiter: full; HR Officer: read | |
| `/api/candidates/{id}/applications/` | GET, POST | Recruiter: C, R; HR Officer: R | Recruiter: full; HR Officer: read | Maps to `candidate_application` |
| `/api/applications/{id}/interviews/` | GET, POST | Recruiter: C, R; HR Officer: R | Recruiter: full; HR Officer: read | `interviewer_employee_id` may reference any employee, not only Recruiters — HRMS-FR-018 does not restrict who may interview, only who may schedule |
| `/api/applications/{id}/interviews/{interview_id}/` | PATCH | Recruiter: U | Recruiter: full | |
| `/api/applications/{id}/offer/` | GET, POST | Recruiter: C, R; HR Officer: R | Recruiter: full; HR Officer: read | Creates `offer_letter`. Body accepts `offered_salary` and optional `offered_pay_grade` (FK into `pay_grade`). `document_object_key` is generated server-side once the offer is issued, same object-storage pattern as employee documents. HR Officer's read access exists so they can reach an accepted offer to trigger conversion (module 9) |
| `/api/offers/{id}/decide/` | POST | Recruiter: U (records the candidate's decision on their behalf, since a candidate has no account — `CONTEXT.md`: "a candidate is not an employee," and this system has no candidate-facing portal per SRS scope) | n/a | Body: `{"decision": "accepted" \| "rejected" \| "withdrawn"}`. An `accepted` decision does not itself create an employee record — HRMS-BR-013 requires onboarding initiation as the conversion trigger, which is module 9's endpoint below, not this one |

### 4.7 Module 9 — Onboarding

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/onboarding/convert/` | POST | HR Officer: C (`docs/07-iam-rbac.md` §4.2's Onboarding row) | n/a | Body: `{"application_id": ...}` or a direct-hire employee payload with no prior application. **This is the HRMS-BR-013 conversion point**: creates the `employee` row, then the `onboarding_checklist` row referencing it (`docs/05-database-schema.md` §4.8 — a checklist row cannot exist before the employee row it references). Atomic: a failure partway does not leave an `employee` row with no checklist |
| `/api/onboarding-checklists/` | GET | HR Officer: R; HR Administrator, Recruiter: R (`docs/07-iam-rbac.md` §4.2) | Per role, same scoping as Employee Management's read | Filterable: `employee_id`, `application_id`. `POST /api/onboarding/convert/` returns the checklist id at creation time, but that was the only way to learn it (issue #101) — this endpoint lets a caller who only has an employee or application id look the checklist back up |
| `/api/onboarding-checklists/{id}/` | GET | HR Officer: R; HR Administrator, Recruiter: R (`docs/07-iam-rbac.md` §4.2) | Per role, same scoping as Employee Management's read | |
| `/api/onboarding-checklists/{id}/tasks/` | GET, POST | HR Officer: C, R | Same as checklist | |
| `/api/onboarding-checklists/{id}/tasks/{task_id}/` | PATCH | HR Officer: U | Same as checklist | `PATCH {"status": "completed"}` sets `completed_by`, `completed_at` |

### 4.8 Module 10 — Notification

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/notifications/` | GET | Any authenticated user (own feed) | `recipient_user_id = current user` — a single equality, not a queryset traversal (`docs/05-database-schema.md` §3.2), so no matrix cell applies; every authenticated user reaches this endpoint over their own rows only | Filterable: `category` (`pending_task`, `request_update`), `read_at__isnull` |
| `/api/notifications/{id}/read/` | POST | Same — own notification only | Same | Sets `read_at`. No endpoint marks another user's notification read; the scoping above makes attempting one on someone else's `id` a `404` (§2.2) |
| `/api/notification-preferences/me/` | GET, PATCH | Any authenticated user (own preference only) | `user_id = current user` — same single-equality reasoning as the notification feed above, no matrix cell applies | Body/response: `email_enabled`, `sms_enabled` (docs/superpowers/specs/2026-07-26-notifications-email-sms-design.md §5). Created lazily on first access (`get_or_create`) rather than at account creation |

No `POST` for creating a notification is exposed to a client: notifications are written by the emitting module's own service code per consumer (`docs/04-system-architecture.md` §3.2), never by direct API call, the same reasoning §4.1 gives `audit_log`.

### 4.9 Module 4 — RBAC / IAM

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/users/` | GET, POST | System Administrator: C, R (`docs/07-iam-rbac.md` §4.2's "User accounts, roles, permissions" row) | System Administrator: all `user_account` rows; no other role reaches this endpoint | Creates/manages `user_account`. Does **not** expose employee, payroll, or compensation fields on any joined `employee` row — `docs/07-iam-rbac.md` §7.1: "the role receives no payroll, compensation, or employee record access." A `user_account.employee_id` is returned as an opaque foreign key, not an expanded employee object |
| `/api/users/{id}/` | PATCH | System Administrator: U | Same as `/api/users/` | |
| `/api/role-grant-requests/` | GET | Any authenticated user | Own requests as requester, plus pending requests awaiting the caller's decision (mirrors `CanDecideRoleGrantRequest`'s eligibility) | Found undocumented by the `contracts` app's M18 contract-test suite — the view already implemented and cited this section; only the row was missing |
| `/api/role-grant-requests/` | POST | Any authenticated user — requesting a grant carries no permission of its own; `docs/07-iam-rbac.md` §7.3 gates *effecting* the grant, not raising the request | Own request as requester; approver sees requests awaiting their decision | Body: `{"subject_user_id": ..., "role_id": ...}`. **Rejected at the database layer, not only application code, where `requester_user_id = subject_user_id`** (`docs/05-database-schema.md` §4.3's `CHECK` constraint carrying `docs/07-iam-rbac.md` §7.3's "self-grant is refused, not warned"). No matrix cell — this is IAM mechanism, gated by §7.3 directly, per §3's reading-guide note |
| `/api/role-grant-requests/{id}/decide/` | POST | Holder of `iam.approve_role_grant`, and not the requester (`docs/07-iam-rbac.md` §7.3) — enforced by the same `CHECK (approver_user_id IS NULL OR approver_user_id <> requester_user_id)` constraint | Only requests where the caller is eligible to approve | Body: `{"decision": "approved" \| "refused"}`. A `decision` that would violate the constraint is rejected with `code: "self_approval_forbidden"` (§2.7) even if it somehow reached this endpoint, since the database constraint is the actual enforcement and this is defence in depth at the API layer |
| `/api/audit-log/` (permission changes) | GET | Covered by §4.1's audit-log endpoint, filtered `?category=permission_change` | Same as §4.1 | Not a second endpoint |

### 4.10 Module 14 — Dashboard

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/dashboard/` | GET | Any authenticated user; content varies by role | Delegates entirely to the visibility rule of whichever module's data it renders (`docs/04-system-architecture.md` §4's module 14 row) | Returns a role-appropriate composite: an Employee sees their own leave balance and pending tasks (modules 13, 10); a Manager additionally sees team-level counts (module 13, `docs/07-iam-rbac.md` §5's "Team-level (FR-032)"); an Executive sees `aggregates.{headcount, leave_utilization, turnover, payroll_cost, payroll_summary}`, each the same `scope='aggregate'` object §4.15's Reports endpoints return for Executive there, called directly rather than via a second HTTP round trip — never an individual record. `turnover`'s period is not caller-supplied here (Dashboard takes no query params); it defaults to the trailing 365 days. This endpoint issues no query of its own that is not already scoped by the source module's `visible_to`; it is a read-only composition layer, not a new data-access decision |

### 4.11 Modules 11/12 — Employee and Manager Self-Service

Self-service is not a separate resource shape; it is a narrower read/write surface over resources modules 6, 7, and 13 already own, per `docs/04-system-architecture.md` §4's module 11/12 rows ("read Employee, Leave, and Notification without owning new storage"). This document does not duplicate those endpoints under a `/api/self-service/` prefix; the "own record" and "direct reports" scoping already stated per-endpoint in §4.3, §4.5, and §4.12 below **is** the self-service surface. `/api/employees/me/` (§4.3) is Employee Self-Service's profile endpoint; `/api/employees/{id}/direct-reports/` (§4.5) and the leave-approval endpoints of §4.12 are Manager Self-Service's.

### 4.12 Module 13 — Leave Management

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/leave-types/` | GET | HR Officer: R; HR Administrator: R; Manager: R (v1.9, fixes #125) | Organisation-wide reference data | |
| `/api/leave-balances/` | GET | Employee: R own; Manager: R direct reports'; HR Officer, HR Administrator: R, U all (`docs/07-iam-rbac.md` §4.2) | `docs/07-iam-rbac.md` §5's Leave requests row (balances follow the same scope) | |
| `/api/leave-requests/` | GET | Employee: R own; Manager: R direct reports'; HR Officer, HR Administrator: R all | `docs/07-iam-rbac.md` §5 | Filterable: `status`, `leave_type_id`, date range |
| `/api/leave-requests/` | POST | Employee: C own (`docs/07-iam-rbac.md` §4.2's "C, R own" cell) | n/a | `employee_id` is fixed to the caller, not client-supplied — an Employee cannot request leave on another employee's behalf through this endpoint regardless of body content |
| `/api/leave-requests/{id}/` | PATCH | HR Officer: U (correction/cancellation only — `docs/07-iam-rbac.md` §4.3: "HR Officer may update a leave request... but may not approve it") | HR Officer: all | This endpoint's permission class explicitly excludes writing `status` to `'approved'`; that transition is `approve/` below, held by Manager only, so the same field cannot be reached by two different permission paths |
| `/api/leave-requests/{id}/approve/` | POST | Manager: A, and only for the requester's direct manager (`docs/07-iam-rbac.md` §4.2's "Leave approval," Manager-only at action level per §4.3) | Manager: only requests from own direct reports (`docs/07-iam-rbac.md` §5) | Sets `status = 'approved'`, `approved_by`, `decided_at`; decrements `leave_balance.used_days` (HRMS-BR-010 — balance reduces only on approval). Emits a decision notice to module 10 (`docs/04-system-architecture.md` §4's module 13 row) |
| `/api/leave-requests/{id}/reject/` | POST | Manager: A, same scoping as approve | Same | Sets `status = 'rejected'`; balance is **not** decremented (HRMS-BR-011) |
| `/api/leave-requests/{id}/cancel/` | POST | Employee: U own (own pending request only) | Own request only | Sets `status = 'cancelled'` |
| `/api/leave-calendar/` | GET | HR Officer, HR Administrator: R; Manager: R (`docs/07-iam-rbac.md` §4.2's Leave calendar row) | HR: organisation-wide; Manager: direct reports' (`docs/07-iam-rbac.md` §5, same scope as leave requests) | HRMS-FR-071. Read-only composite over `leave_request` where `status = 'approved'`, not a separate table |

### 4.13 Module 15 — Compensation and Benefits

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/salary-structures/` | GET, POST | HR Administrator: C, R; HR Officer, Payroll Officer: R (`docs/07-iam-rbac.md` §4.2) | Organisation-wide | |
| `/api/salary-structures/{id}/` | PATCH | HR Administrator: U | Organisation-wide | |
| `/api/pay-grades/` | GET, POST | HR Administrator: C, R, U; HR Officer, Payroll Officer: R; Recruiter: R (blind selection only) | Organisation-wide | Recruiter's `GET` returns `id`, `name`, and the parent salary structure's `name` (not its other fields) — no `min_salary`/`max_salary`, needed to populate `offered_pay_grade` on §4.6's Issue Offer form without granting the salary-figure visibility `docs/07-iam-rbac.md` §2.4 withholds from Recruiter. The structure name disambiguates pay grades that share a name across different structures — `PayGrade.name` is unique only within a `salary_structure`, not organisation-wide (issue #107) |
| `/api/pay-grades/{id}/` | PATCH | HR Administrator: U | Organisation-wide | Listed under its own row rather than folded into the collection row above, to avoid implying a `PATCH` on `/api/pay-grades/` itself, which has no such method (issue #106) |
| `/api/employees/{id}/compensation-records/` | GET | HR Administrator: R; HR Officer: R; Payroll Officer: R (`docs/07-iam-rbac.md` §4.2's Compensation history row) | Per role, Employee records scope | Returns the append-only history (`docs/05-database-schema.md` §3.4), most recent first; no employee self-read of their own compensation history is granted by §4.2's matrix — HRMS-FR-058 does not name Employee among the roles that read it, so `/api/employees/me/` (§4.3) does not expose this sub-resource |
| `/api/employees/{id}/compensation-records/` | POST | HR Officer: C (§4.2's "Assign employee to pay grade" row — the transactional act, distinct from defining the pay grade framework itself, `docs/07-iam-rbac.md` §2.4) | n/a | **No client-facing `PATCH` or `DELETE` on an existing row exists on this endpoint.** A correction is a new `POST` with a later `effective_from`. That insert does perform one further, narrowly scoped write: it sets the prior current row's `is_superseded = true` and `effective_to`, server-side, within the same transaction — the two fields `docs/05-database-schema.md` §3.4 names as the append-only table's designed exception, "an in-band way to mark a row historical without ever rewriting the value it recorded." Every other column of that row (`base_salary`, `pay_grade_id`, `effective_from`) is never written again once inserted, and no endpoint accepts a request that would write them |
| `/api/bonus-cycles/` | GET, POST | HR Administrator: C, R; HR Officer, Payroll Officer: R (grouped under §4.2's "Bonus cycles, allowances, benefits" row) | Organisation-wide | |
| `/api/bonus-cycles/{id}/` | PATCH | HR Administrator: U | Organisation-wide | |
| `/api/bonus-cycles/{id}/awards/` | GET, POST | HR Administrator: C, R | Organisation-wide (HR); no employee self-read — §4.2 does not list Employee against this row the way it does allowances/benefits | |
| `/api/allowance-types/` | GET, POST | HR Administrator: C, R; HR Officer, Payroll Officer: R | Organisation-wide | Definitional half of "Allowance" (§4.16 below carries the computed-instance half onto `payslip_line`, per `docs/05-database-schema.md` §7's split) |
| `/api/allowance-types/{id}/` | PATCH | HR Administrator: U | Organisation-wide | |
| `/api/employees/{id}/allowances/` | GET | HR Administrator: R; HR Officer, Payroll Officer: R; Employee: R own (`docs/07-iam-rbac.md` §4.2's "R own" cell) | Employee: own; HR/Payroll: per role | Maps to `employee_allowance` — the per-employee assignment, still distinct from the payslip line amount computed from it |
| `/api/employees/{id}/allowances/` | POST | HR Administrator: C | n/a | |
| `/api/benefits/` | GET, POST | HR Administrator: C, R; HR Officer, Payroll Officer: R | Organisation-wide | |
| `/api/benefits/{id}/` | PATCH | HR Administrator: U | Organisation-wide | |
| `/api/employees/{id}/benefit-enrollments/` | GET, POST | HR Administrator: C, R; Employee: R own | Employee: own; HR: per role | |
| `/api/employees/{id}/benefit-enrollments/{enrollment_id}/` | PATCH | HR Administrator: U | Employee: own; HR: per role | `PATCH {"status": "cancelled"}` sets `cancelled_at` |

### 4.14 Module 16 — Payroll

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/statutory-rates/` | GET | Payroll Officer: R — a named exception, not a `docs/07-iam-rbac.md` §4.2 cell: that matrix has no row for `statutory_rate_table` (the definitional half of "Deduction," `docs/05-database-schema.md` §7), only for the payroll processing that reads it. Granted to Payroll Officer alone, on the same reasoning §4.2's Payroll processing row already restricts payroll configuration to that role | Payroll Officer only | Read-only through this API — rate table entry is an operational/configuration path (TBD-005, `docs/05-database-schema.md` §9), not modelled as a client-writable endpoint in this design; a future rate-management UI is not precluded but is not specified here |
| `/api/payroll-runs/` | GET | Payroll Officer: R (`docs/07-iam-rbac.md` §4.2) | Payroll Officer: all | Filterable: `status`, period range |
| `/api/payroll-runs/{id}/` | GET | Payroll Officer: R | Payroll Officer: all | The status-polling target for every async action below (`calculate/`, `finalize/`) and for `submit-for-approval/`/`approve/`; returns the current `status` and, once set, `approved_by`/`approved_at`/`finalized_at` |
| `/api/payroll-runs/` | POST | Payroll Officer: C | n/a | Body: `{"period_start": ..., "period_end": ...}`. `initiated_by` is fixed to the caller (`docs/05-database-schema.md` §4.12's `NOT NULL`, `ON DELETE RESTRICT` `initiated_by`), never client-supplied. `status` defaults `draft`. Enforces the `UNIQUE (period_start, period_end)` constraint — a duplicate period returns `409 conflict` |
| `/api/payroll-runs/{id}/calculate/` | POST | Payroll Officer: U | n/a | Triggers the Celery calculation task (`docs/03-tech-stack.md` §4.2 — payroll runs off the request cycle, HRMS-NFR-005). Response is `202 Accepted` with the run's `id`; the client polls `GET /api/payroll-runs/{id}/` (row above) for `status` progression to `calculated`, matching the async pattern every payroll-adjacent endpoint in this module uses rather than blocking the request thread on a multi-minute computation |
| `/api/payroll-runs/{id}/submit-for-approval/` | POST | Payroll Officer: U | n/a | Sets `status = 'pending_approval'` |
| `/api/payroll-runs/{id}/approve/` | POST | Holder of `payroll.approve_payroll_run` — granted to no role by default (`docs/07-iam-rbac.md` §4.4); the `‡` cell in §4.2, resolved to a permission name rather than a role per §2.6 above | n/a | **Rejected, `403` with `code: "self_approval_forbidden"`, where the caller is the run's `initiated_by`** — enforced first by `docs/05-database-schema.md` §3.5's `CHECK (approved_by IS NULL OR approved_by <> initiated_by)` at the database layer, restated here at the API layer as the first check this endpoint performs, per `docs/07-iam-rbac.md` §4.4: "regardless of any combination of roles a user may hold." Sets `status = 'approved'`, `approved_by`, `approved_at` |
| `/api/payroll-runs/{id}/finalize/` | POST | Same as approve, and only callable once `status = 'approved'` | n/a | Triggers the atomic finalisation transaction across `payroll_run`, `payslip`, `payslip_line` (`docs/05-database-schema.md` §4.12, ADR-0003, ADR-0006 — "a partial payroll is a corrupt payroll"). Async, `202` and the same `GET /api/payroll-runs/{id}/` poll target as `calculate/`. Sets `finalized_at` on completion |
| `/api/payroll-runs/{id}/bank-transfer-file/` | GET | Payroll Officer: R | Payroll Officer only | Returns a signed URL to the generated file (ADR-0007 pattern, same as employee documents), not the file bytes. `404` before finalisation — `bank_transfer_file` does not exist until then |
| `/api/payslips/` | GET | Employee: R own; Payroll Officer: R all (`docs/07-iam-rbac.md` §4.2's Payslips row) | Employee: own only (HRMS-BR-006); Payroll Officer: all | This is `/api/employees/me/payslips/` in effect for an Employee caller and the full collection for Payroll Officer — one endpoint, scoped by the visibility rule rather than two separate routes, since the rule already produces the narrower set for the Employee case |
| `/api/payslips/{id}/` | GET | Same as list | Same | Includes nested `payslip_line` rows — the computed-instance half of Allowance and Deduction (`docs/05-database-schema.md` §7), each carrying `line_type`, `amount`, and `source_type`/`source_id` as a non-FK reference back to the definitional row that produced it (allowance type or statutory rate table), so a finalised payslip remains fully readable even if that source configuration is later retired |
| `/api/payslips/{id}/download/` | GET | Same as retrieve | Same | Signed URL to a generated PDF, same object-storage pattern |

### 4.15 Module 17 — Reports

| Endpoint | Method | Permission | Visibility | Notes |
|---|---|---|---|---|
| `/api/reports/headcount/` | GET | HR Officer, HR Administrator: R; Manager: R (team-level); Executive: R (aggregate) | Per source module's rule; Executive: aggregate only, never an individual record (`docs/07-iam-rbac.md` §4.3) | Aggregates over module 6 |
| `/api/reports/leave-utilization/` | GET | HR Officer, HR Administrator: R; Manager: R (team-level); Executive: R (aggregate) | Same pattern | Aggregates over module 13 |
| `/api/reports/turnover/` | GET | HR Officer, HR Administrator: R; Manager: R (team-level); Executive: R (aggregate) | Same pattern | HRMS-FR-050, found unbacked by any endpoint while preparing the Module 17 handoff (same shape as FR-032, FR-045). Computes hires/terminations over a caller-specified date range, not a point-in-time count like `/api/reports/headcount/` |
| `/api/reports/payroll-cost/` | GET | Payroll Officer: R; Executive: R (aggregate) (`docs/07-iam-rbac.md` §4.2's "R (payroll cost)" cells) | Payroll Officer: full detail; Executive: aggregate only, and **never** a payslip or an individual employee's figure — this is where §4.3's aggregate-only rule is load-bearing rather than incidental, since payroll cost is exactly the data HRMS-NFR-019 restricts | Aggregates over module 16 |
| `/api/reports/payroll-summary/` | GET | Payroll Officer: R; Executive: R (aggregate) (same cells as the row above) | Same pattern as `/api/reports/payroll-cost/` — Payroll Officer full detail, Executive aggregate only, never an individual payslip | HRMS-FR-045, recorded as a residual of module 16 at `docs/02-project-plan.md` v1.11 (found unbacked by any endpoint during PAYROLL-001's review, same shape as FR-032). Aggregates over module 16, per-run rather than per-payslip |
| `/api/reports/{report}/export/` | POST | Same permission as the corresponding report endpoint | Same | Triggers an async export (`docs/03-tech-stack.md` §4.2 — "large report exports are batch operations"). Returns `202` with a `job_id`; same async pattern as §4.14's payroll actions |
| `/api/report-exports/{job_id}/` | GET | Same as the export's caller (own job only) | Own job only | The poll target for the row above: `status` (`pending`, `complete`, `failed`) and, once `complete`, a signed URL to the generated file (same object-storage pattern as §4.3, §4.14). Emits an audit entry where the export touches payroll cost (`docs/04-system-architecture.md` §4's module 17 row) |

---

## 5. Requirements Traceability

| Requirement | Addressed by |
|---|---|
| HRMS-FR-001 to HRMS-FR-004, HRMS-FR-009, HRMS-FR-011, HRMS-FR-012 (employee records) | §4.3 |
| HRMS-FR-005 (compensation on record creation) | §4.13 (`/api/employees/{id}/compensation-records/`) |
| HRMS-FR-006 (employee documents) | §4.3 |
| HRMS-FR-007 (emergency contacts) | §4.3 |
| HRMS-FR-008 (reporting relationships) | §4.5 |
| HRMS-FR-009 (search/filter) | §2.4, §4.3 |
| HRMS-FR-010 (audit history) | §4.1 |
| HRMS-FR-013 to HRMS-FR-021 (recruitment) | §4.6 |
| HRMS-FR-022 to HRMS-FR-024 (onboarding) | §4.7 |
| HRMS-FR-025 to HRMS-FR-027 (self-service profile) | §4.3, §4.11 |
| HRMS-FR-030 (manager views team) | §4.5, §4.11 |
| HRMS-FR-028, HRMS-FR-044 (payslips) | §4.14 |
| HRMS-FR-032 (manager team reports) | §4.15 |
| HRMS-FR-033, HRMS-FR-034 (notification) | §4.8 |
| HRMS-FR-035 to HRMS-FR-044, HRMS-FR-046, HRMS-FR-048 (payroll processing) | §4.14 |
| HRMS-FR-045 (payroll summary reports, residual of module 16 — `docs/02-project-plan.md` v1.11) | §4.15 |
| HRMS-FR-047 (payroll finalisation approval) | §4.14 (`approve/`, `finalize/`) |
| HRMS-FR-049, HRMS-FR-052 to HRMS-FR-055 (reports and dashboards) | §4.10, §4.15 |
| HRMS-FR-050 (turnover reports) | §4.15 (`/api/reports/turnover/`) |
| HRMS-FR-056, HRMS-FR-057 (salary structures, pay grades) | §4.13 |
| HRMS-FR-058 (compensation history) | §4.13 |
| HRMS-FR-059 (bonus cycles) | §4.13 |
| HRMS-FR-060 (allowances) | §4.13, §4.14 |
| HRMS-FR-061 (benefits) | §4.13 |
| HRMS-FR-063 to HRMS-FR-065, HRMS-FR-070 (leave requests, balances) | §4.12 |
| HRMS-FR-064 (leave approval) | §4.12 (`approve/`, `reject/`) |
| HRMS-FR-066 (leave types) | §4.12 |
| HRMS-FR-071 (leave calendar) | §4.12 |
| HRMS-NFR-005 (payroll elapsed time) | §4.14's async `202`-and-poll pattern |
| HRMS-NFR-007, HRMS-NFR-008 (file type/size) | §4.3's document-upload row |
| HRMS-NFR-013, HRMS-NFR-022 (audit logging) | §4.1; emission absorbed per endpoint, not restated per row (§4's introduction) |
| HRMS-NFR-014 (authentication required) | §2.2 |
| HRMS-NFR-016 (RBAC) | §2.6, §3, every Permission column in §4 |
| HRMS-NFR-017, HRMS-NFR-018, HRMS-NFR-019 (visibility) | §2.5, §3, every Visibility column in §4 |
| HRMS-NFR-021 (secure document storage) | §4.3, §4.14 (signed-URL pattern) |
| HRMS-NFR-024 (second-factor authentication) | §4.2 |
| HRMS-BR-006 (employees view own payslips) | §4.14 |
| HRMS-BR-007 (manager visibility) | §2.5, §3, §4.5 |
| HRMS-BR-008 (payroll approval, atomicity) | §4.14 (`approve/`, `finalize/`) |
| HRMS-BR-009 to HRMS-BR-011 (leave workflow, balance rules) | §4.12 |
| HRMS-BR-012 (terminated employees lose access) | §2.2, §2.5 — enforced beneath every endpoint via the Employee derivation, not an endpoint of its own |
| HRMS-BR-013 (candidate conversion) | §4.7 (`/api/onboarding/convert/`) |
| `docs/07-iam-rbac.md` §4.2 (permission matrix) | §2.6, §3, cited per endpoint throughout §4 |
| `docs/07-iam-rbac.md` §4.4 (payroll approver not initiator) | §4.14 (`approve/`) |
| `docs/07-iam-rbac.md` §5 (visibility rules) | §2.5, §3, cited per endpoint throughout §4 |
| `docs/07-iam-rbac.md` §7.3 (self-grant refused, privileged-grant approval) | §4.9 |

---

## 6. Re-reading `docs/07-iam-rbac.md` Against This Document

Per plan §5.3, this is part of M4 sign-off. The IAM document's fixed point for this milestone is stated directly at plan §5.3: "`docs/07-iam-rbac.md` §4.2 assigns permissions per module against named requirement ranges. `docs/06-api-contracts.md` inherits that matrix as the specification of what each endpoint gates." Every Permission column in §4 above cites a §4.2 cell or, where §4.2 states `‡`, resolves it to `payroll.approve_payroll_run` per §4.4 there, with one stated exception: `/api/statutory-rates/` (§4.14), which §4.2's matrix gives no row of its own, and which this document grants to Payroll Officer alone as a named exception rather than inventing a matrix cell that does not exist. No endpoint otherwise invents a role or permission §4.2 does not already name. Every Visibility column cites a §5 row, or, for the two surfaces §5 does not cover (Notification's own-record equality, IAM's own grant mechanism), cites the specific section of `docs/07-iam-rbac.md` that governs it directly (§3.2's citation in `docs/04-system-architecture.md` for the former, §7.3 for the latter), per §3's reading-guide note above.

No inconsistency was found. `docs/07-iam-rbac.md` §4.2 and §5 name no role, permission, or visibility scope this document's endpoints do not already accommodate; neither document required a change.

---

## 7. Open Items Inherited, Not Introduced

This document introduces no new TBD. The items below are open in documents this one is downstream of and bear on the API surface as designed.

- **TBD-005 (final payroll statutory rates).** Open. `/api/statutory-rates/` (§4.14) is read-only against whatever bracket structure `docs/05-database-schema.md` §4.12's `statutory_rate_table` eventually holds; no placeholder rate is exposed.
- **TBD-006 (bank transfer file format).** Open. `/api/payroll-runs/{id}/bank-transfer-file/` (§4.14) returns a signed URL to the generated file regardless of format; the format is not an API-layer decision.
- **`iam.approve_role_grant` and second-factor recovery approver holders.** Deferred to deployment (`docs/07-iam-rbac.md` §8). `/api/role-grant-requests/{id}/decide/` and `/api/auth/second-factor/recovery-requests/{id}/decide/` (§4.9, §4.2) function identically regardless of who is designated.
- **Payroll finalisation approver.** Resolved as a deployment-time grant (`docs/07-iam-rbac.md` §4.4). `/api/payroll-runs/{id}/approve/` (§4.14) enforces the approver-not-initiator constraint regardless of who holds the permission.
- **Second-factor mechanism (TOTP, WebAuthn, or otherwise).** Open — `docs/05-database-schema.md` §4.2 states this is a decision "`docs/06-api-contracts.md` or a later ADR settles, not a decision this schema makes." This document does not settle it either: `/api/auth/second-factor/` (§4.2) is specified at the level of "creates a `second_factor` row bound to `secret_ref`," not at the level of which challenge-response protocol the client and server exchange. Settling that is implementation detail below this document's altitude, on the same reasoning `docs/05-database-schema.md` gave for declining it; a later ADR is the right home if it turns out to carry a real trade-off (TOTP's offline verifiability against WebAuthn's phishing resistance), which this document does not attempt to adjudicate.
- **Report export formats and retention.** Open — `/api/reports/{report}/export/` (§4.15) is specified at the level of "async, signed-URL download," not at the level of file format (CSV, XLSX, PDF) or how long a generated export remains downloadable; neither is fixed by any upstream document and both are implementation detail, not an API contract this milestone needs to close.

---

**Sign-off.** Per `docs/02-project-plan.md` §5.2, this milestone is met when the project owner has read this document and accepted it.
