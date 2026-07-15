# ADR-0006: Celery and Redis for background and scheduled work

**Status:** Accepted
**Date:** 2026-07-15

## Context

Several requirements describe work that cannot execute within a web request:

- **HRMS-NFR-005** — payroll processing should complete within a few minutes for small to medium organisations. This exceeds a reasonable HTTP request lifetime; payroll cannot run inside a request.
- **HRMS-FR-069** — leave balances update after approved leave, and accrual is periodic. Accrual is triggered by the calendar, not by a user action.
- **HRMS-FR-043, HRMS-FR-046** — payslip generation and bank transfer file generation are batch operations over the active employee population.
- **SRS §3.4** — email notification for approvals, onboarding, password reset, and payroll communication.
- **HRMS-FR-054** — report export, which at larger data volumes exceeds the response time budget in HRMS-NFR-004.

A background execution capability is therefore required, not optional.

## Decision

**Celery** provides task execution, with **Celery Beat** for scheduled work and **Redis** as the message broker.

## Consequences

**Positive**

- Payroll runs, payslip generation, and bank file generation execute outside the request cycle, satisfying HRMS-NFR-005 without holding an HTTP connection.
- Celery Beat provides the scheduler for periodic leave accrual.
- Redis additionally serves as a cache and rate-limiting store without adding a further component.
- Celery is the established background processing system for Django. The operational patterns and failure modes are well documented.
- Both worker and broker are containers in the existing composition (ADR-0009), consistent with the deployment model.

**Negative**

- **Operational weight.** Three additional processes to run, monitor, and debug: worker, scheduler, broker. This exceeds what the stated load (HRMS-NFR-006, 50–200 concurrent users) strictly demands. The choice favours conventional practice over minimal machinery, deliberately.
- **Task semantics require care.** Payroll tasks must be idempotent; a retried task must not double-write payroll records. Worker failure mid-task, retry storms, and lost tasks are real failure modes that the payroll design must address explicitly rather than assume away. Given HRMS-BR-008 and the monetary consequences, this is a first-order design concern for the Payroll module, not an operational afterthought.
- Redis introduces a component whose durability configuration matters. A broker losing a queued payroll task must be detectable.

**Rejected alternatives**

- *Lighter task libraries* (Django-Q2, Dramatiq, django-rq). Adequate at this scale with less ceremony. Rejected in favour of the conventional choice.
- *Database-backed brokers* (e.g. procrastinate). Would remove Redis entirely. Rejected for the same reason.
