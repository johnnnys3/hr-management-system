# ADR-0002: Django and Django REST Framework as the backend framework

**Status:** Accepted
**Date:** 2026-07-15

## Context

The backend must support requirements that are heavy on domain logic rather than on request throughput:

- Statutory payroll calculation for Ghana (PAYE, SSNIT Tier 1, Tier 2, Tier 3) with configurable rates, per HRMS-FR-039 to HRMS-FR-042 and the constraint in SRS §2.5 that rates change over time.
- Payroll processing expected to complete within a few minutes (HRMS-NFR-005), which exceeds the lifetime of a web request and therefore requires scheduled and background execution.
- Role-based access control across seven user classes (HRMS-NFR-016).
- An administrative surface for HR operations staff performing record maintenance (HRMS-FR-001 to HRMS-FR-012).
- Audit logging of sensitive actions (HRMS-NFR-013, HRMS-BR-015).

Node-based full-stack frameworks were evaluated and rejected. Framework comparison guidance is direct on the point: API routes in such frameworks are suitable as glue code but are not a replacement for a backend framework where complex domain logic, queues, and scheduled jobs are involved. The HRMS requires all three.

Laravel (PHP) was considered a legitimate alternative, with precedent in this exact domain: OrangeHRM, the largest open-source HRMS, runs a modular PHP monolith. Django carries comparable precedent in Horilla, an open-source HRMS built on Django.

## Decision

The backend uses **Django** with **Django REST Framework** for the API layer.

The Django application concept provides the module unit described in ADR-0001: one Django app per functional area, with domain logic in service modules within each app.

## Consequences

**Positive**

- Django's application structure maps directly onto the modular boundaries required by ADR-0001.
- Python's `Decimal` type provides exact arithmetic for statutory deduction calculation. Binary floating point is unsuitable for monetary values and would introduce rounding error into PAYE and SSNIT figures.
- Django's authentication, group, and permission systems provide the foundation for role-based access control (see ADR-0005).
- The Django administrative interface provides an immediate maintenance surface for HR record management, reducing bespoke screen work.
- Django REST Framework is the established API layer for Django, with schema generation available for the API contract deliverable.
- The ecosystem is mature and the skills are widely held, which matters for a system intended to be maintained beyond its initial author.

**Negative**

- Two languages in the project: Python on the backend, TypeScript on the frontend. Context switching is a real cost.
- Django REST Framework serializers and frontend validation schemas describe overlapping rules and must be kept in agreement. This is the duplication cost accepted in ADR-0001.
- Django's ORM encourages logic to accumulate in model classes. Keeping domain logic in service modules requires deliberate discipline to preserve the extractability goal.

**Rejected alternatives**

- *Node full-stack framework.* Lacks native background job, scheduling, and administrative capabilities that this system requires. Each would be assembled from third-party components.
- *Laravel.* A sound fit with strong domain precedent. Django was preferred for exact decimal arithmetic ergonomics and for consistency with the Python ecosystem.
