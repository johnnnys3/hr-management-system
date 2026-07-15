# ADR-0005: Access control via Django groups for actions and queryset scoping for rows

**Status:** Accepted
**Date:** 2026-07-15

## Context

The SRS specifies access control at two distinct levels, which are easily conflated.

**Action-level.** What operations a role may perform. A Payroll Officer may run payroll; a Recruiter has no need of payroll or compensation records (SRS §2.3.3). Seven user classes are defined in SRS §2.3.

**Row-level.** Which records a given user may see, among records of a type they are otherwise permitted to access:

- **HRMS-NFR-018 / HRMS-BR-007** — managers shall access only team data assigned to them.
- **HRMS-NFR-017 / HRMS-BR-006** — employees shall access only their own records and payslips.
- **HRMS-NFR-019** — payroll data shall be accessible only to authorised payroll users.

Django's built-in permission system operates at model level. It expresses "may view employee records" but not "may view *this* employee record". The row-level requirements fall outside it.

Two approaches to the row-level gap were considered: object-level permission records (django-guardian), and rule-based queryset scoping.

## Decision

**Action-level access** uses Django's built-in groups and permissions. Each **assigned** role maps to a group.

Roles are not one-to-one with the seven user classes above. ADR-0010 reconciles the two and settles the role model: six assigned roles map to groups; the two **derived** roles — Employee and Manager — are computed from employment and reporting data, are never granted, and have no group. Their action-level checks read the same organisational data as their visibility rules, on the reasoning below: a fact already held in the data is not copied into an access-control record.

**Row-level access** uses **queryset scoping**: a visibility rule per module, expressed as a manager method (`Employee.objects.visible_to(user)` and equivalents), deriving visibility from existing organisational data.

django-guardian is not used.

## Consequences

**Positive**

- **No duplicated source of truth.** HRMS-FR-008 requires the system to hold reporting relationships. A manager's team is therefore already a fact in the data. Object-level permission records would copy that fact into access-control rows, creating a second source of truth that drifts. When an employee's reporting manager changes, stale permission rows would leave the former manager with continued visibility of that employee's records — a live disclosure defect, not a theoretical one. Derived scoping cannot drift, because it reads the org structure at query time.
- **Extractable.** Visibility rules live in module service code as plain predicates, consistent with the reuse goal in ADR-0001.
- **Appropriate to the problem.** Object-level permission systems suit arbitrary per-object grants ("share this document with this person"). HRMS visibility is structural, derived from the organisation chart and record ownership.

**Negative**

- **Nothing enforces application.** A list endpoint that omits the scoped queryset returns unscoped data. This is a disclosure defect of the most serious kind — salary and identity data to unauthorised viewers.

  Mitigations, which are mandatory rather than optional:
  - Every endpoint returning employee-scoped data obtains its queryset through the scoping method. Default deny.
  - Permission tests accompany every module, asserting both allowed and denied paths. This is already required by the project testing strategy.
  - Review treats a missing scope call as a blocking defect.

- **Query complexity.** Deriving visibility from reporting structure requires traversal, which may need indexing attention or a materialised path once the organisation is large. Not a concern at the stated scale (HRMS-NFR-006), but a known ceiling.

**Rejected alternative**

- *django-guardian.* Well-established, but solves per-object grant assignment rather than structural visibility, and would introduce the drift defect described above.
