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

**Two Redis instances, not one.** Broker durability and cache eviction are opposite requirements and are not co-tenantable:

| Instance | Serves | `maxmemory-policy` | Persistence |
|---|---|---|---|
| `redis-broker` | Celery broker and result backend | **`noeviction`** | AOF, `appendfsync everysec` |
| `redis-cache` | Django cache, rate-limiting counters | `allkeys-lru`, with `maxmemory` set | None. Contents are reconstructible |

**Separate logical databases on one instance would not achieve this.** `maxmemory` and `maxmemory-policy` are instance-level settings in Redis; they are not per-database. A single instance configured `allkeys-lru` to serve the cache would make queued Celery messages eligible for eviction under memory pressure, and selecting `SELECT 1` for the broker would not exempt them. Isolation therefore requires separate instances. This is the reason for the split; a logical-database split would look like isolation and provide none.

**The broker fails loudly.** Under `noeviction`, a broker at `maxmemory` refuses the write and `apply_async` raises. An enqueue that fails is visible to the caller and can be retried or surfaced; a task silently evicted from a queue is neither. Given HRMS-BR-008 and a payroll run that must not partially execute, a refused enqueue is the correct failure and a silent one is not acceptable at any memory setting. Broker memory use, queue depth, and AOF write failures are monitored, and this is what ADR-0009's deployment must provide.

## Consequences

**Positive**

- Payroll runs, payslip generation, and bank file generation execute outside the request cycle, satisfying HRMS-NFR-005 without holding an HTTP connection.
- Celery Beat provides the scheduler for periodic leave accrual.
- Redis additionally serves as a cache and rate-limiting store, reusing a technology already present rather than adding a further one. It does add a second instance of it; see below.
- Celery is the established background processing system for Django. The operational patterns and failure modes are well documented.
- Worker, scheduler, broker, and cache are all containers in the existing composition (ADR-0009), consistent with the deployment model. The broker/cache split is expressed there as two services with distinct configuration, not as one service with two clients.

**Negative**

- **Operational weight.** Four additional processes to run, monitor, and debug: worker, scheduler, broker, cache. This exceeds what the stated load (HRMS-NFR-006, 50–200 concurrent users) strictly demands. The choice favours conventional practice over minimal machinery, deliberately.
- **The second Redis instance is a cost paid for isolation, not for capacity.** At HRMS-NFR-006's load one instance would be ample on throughput and memory. The split buys the guarantee that a cache filling up cannot discard a queued payroll task, which single-instance configuration cannot express at any size.
- **Rate limiting shares the evicting instance and therefore fails open.** Under memory pressure `allkeys-lru` may discard rate-limit counters, resetting a window and briefly permitting more requests than the limit. This is accepted: rate limiting here is a throttle, not an authorisation control, and no requirement in §5.3 depends on it. Nothing that gates access is stored on this instance. Were a rate limit ever to become a security control, it needs its own durable store and this consequence must be revisited rather than inherited.
- **Task semantics require care.** Payroll tasks must be idempotent; a retried task must not double-write payroll records. Worker failure mid-task, retry storms, and lost tasks are real failure modes that the payroll design must address explicitly rather than assume away. Given HRMS-BR-008 and the monetary consequences, this is a first-order design concern for the Payroll module, not an operational afterthought.
- Redis introduces a component whose durability configuration matters, and the configuration above is load-bearing rather than incidental. A broker deployed on defaults, or merged back onto the cache instance for convenience, silently reintroduces the eviction path this decision closes — and it reintroduces it as data loss with no error, which is the hardest failure to notice. The deployment must assert the broker's `maxmemory-policy` and persistence settings rather than assume them.

**Rejected alternatives**

- *Lighter task libraries* (Django-Q2, Dramatiq, django-rq). Adequate at this scale with less ceremony. Rejected in favour of the conventional choice.
- *Database-backed brokers* (e.g. procrastinate). Would remove Redis entirely. Rejected for the same reason.
