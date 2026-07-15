# ADR-0001: Modular monolith backend with a separate React SPA client

**Status:** Accepted
**Date:** 2026-07-15

## Context

The HRMS spans eight functional modules across three delivery phases: Core HR, Recruitment and Onboarding, Employee and Manager Self-Service, Payroll, Reporting and Analytics, Compensation and Benefits, and Leave Management. The system must remain maintainable as modules are added phase by phase, and portions of the domain logic (statutory payroll calculation, leave policy enforcement) should be extractable for reuse in unrelated projects.

Three shapes were considered:

1. A single deployable serving both server-rendered pages and business logic.
2. A modular monolith backend exposing an API, consumed by a separate frontend client.
3. Independently deployable services per domain (microservices).

Prevailing industry guidance in 2026 favours starting with a modular monolith and extracting services only when a specific operational need justifies the added complexity. Reported experience supports this: a 2025 CNCF survey found approximately 42% of organisations that adopted microservices subsequently consolidated at least some services back into larger deployable units, and Thoughtworks analysis reports more than 40% of organisations regretting at least some microservices decisions, citing operational complexity and cost.

Option 3 was rejected on those grounds. The system serves 50–200 concurrent users (HRMS-NFR-006) and presents no scaling boundary that would justify independent deployables.

## Decision

The backend is a **modular monolith**: one deployable, internally divided into modules with explicit boundaries, one per functional area. Business logic within each module resides in framework-light Python service code, separated from HTTP handling and persistence concerns.

The frontend is a **separate React single-page application** consuming a REST API exposed by that backend.

Both are served under a single origin (see ADR-0004 and ADR-0009).

## Consequences

**Positive**

- Domain logic per module is independently testable and extractable. Copying a module's service code into another project does not drag framework or transport concerns with it.
- One backend deployment, one database, one place to debug. No distributed transaction concerns across payroll, leave, and employee data.
- Module boundaries make later extraction to a service straightforward should a genuine need appear.
- The frontend/backend split reflects mainstream practice and keeps the API available for future consumers.

**Negative**

- Two deployable artefacts rather than one. The API surface must be versioned and maintained as a contract.
- Validation logic is duplicated: the API enforces rules server-side, the client duplicates a subset for responsive feedback. This is inherent to the split and accepted.
- Module boundaries within a monolith are enforced by convention and review, not by process isolation. Discipline is required to prevent cross-module coupling.

**Rejected alternatives**

- *Single deployable with server-rendered pages.* Simpler operationally, but the project explicitly prioritises a rich client experience and a conventional API-backed architecture.
- *Microservices.* Rejected as disproportionate to the scale and load of the system.
