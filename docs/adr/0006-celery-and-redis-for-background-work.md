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
| `redis-broker` | Celery broker; result backend only for tasks that declare a result | **`noeviction`** | AOF, `appendfsync everysec` |
| `redis-cache` | Django cache, rate-limiting counters | `allkeys-lru`, with `maxmemory` set | None. Contents are reconstructible |

**Result retention is explicit, because on a `noeviction` instance it is the queue's memory it consumes.** Celery's Redis result backend retains results for one day by default, and the backend shares `redis-broker`'s memory with the queue. `noeviction` means those result keys are never reclaimed to make room: past `maxmemory`, retained *results* stop *enqueues*, and the broker's refusal — correct in itself, see below — would be triggered by data the system no longer needs. The isolation this decision buys against the cache would then be undone from inside the broker. Three settings are therefore load-bearing rather than default:

1. **Results are off by default.** `task_ignore_result = True` globally. Most of the work here — payroll runs, payslip and bank-file generation, notification email, accrual — reports outcome through its own records, and a Celery result would be a second copy of a fact PostgreSQL already holds authoritatively.
2. **A task that needs a result opts in and bounds it.** `result_expires` is set explicitly at a value tied to how long the result is actually read for, not inherited.
3. **Result volume does not relax the broker.** If retained results ever become material against broker memory, the result backend moves off `redis-broker` — to PostgreSQL or its own instance. The `noeviction` policy and the persistence settings are not the thing that gives way, because they are the thing this decision is for.

Broker memory is monitored as queue depth *and* as result-key volume; the second is what fails silently as a design error rather than a load event.

**Separate logical databases on one instance would not achieve this.** `maxmemory` and `maxmemory-policy` are instance-level settings in Redis; they are not per-database. A single instance configured `allkeys-lru` to serve the cache would make queued Celery messages eligible for eviction under memory pressure, and selecting `SELECT 1` for the broker would not exempt them. Isolation therefore requires separate instances. This is the reason for the split; a logical-database split would look like isolation and provide none.

**The broker fails loudly.** Under `noeviction`, a broker at `maxmemory` refuses the write rather than making room by discarding a queued message, and the enqueue does not succeed. An enqueue that fails is visible to the caller and can be retried or surfaced; a task silently evicted from a queue is neither. Given HRMS-BR-008 and a payroll run that must not partially execute, a refused enqueue is the correct failure and a silent one is not acceptable at any memory setting.

**What "raises" does and does not mean.** Celery retries task *publication* by default — `task_publish_retry` is enabled — so `apply_async` raises only once `task_publish_retry_policy` is exhausted. The guarantee this decision relies on is therefore that a failed enqueue is **surfaced to the caller rather than silently dropped**, not that it is surfaced on the first attempt. That is the property HRMS-BR-008 needs, and publication retry does not weaken it: a retry that succeeds enqueued the task, and one that does not still raises.

Two consequences follow, and neither is left to the default:

- **The publish-retry policy is set explicitly**, at the caller for payroll enqueues. Celery's default policy is deliberately short — a few sub-second attempts — which is tuned to ride out a broker blip, not to wait out a full broker. A payroll caller that must not block on a broker at `maxmemory` sets the policy accordingly, up to disabling publication retry (`retry=False`) where an immediate raise is the requirement.
- **Whether a memory refusal is retryable at all is not assumed here.** Publication retry addresses connection errors; a refusal returned by a healthy broker is a different class of error, and how the pinned client versions classify it is a fact to verify at implementation against the versions actually installed, not to assert in this record. The design does not depend on the answer — the enqueue fails loudly either way — but the payroll caller's error handling does, and it must be written against the observed behaviour.

Broker memory use, queue depth, result-key volume, and AOF write failures are monitored, and this is what ADR-0009's deployment must provide.

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
- **Celery's defaults do not implement this decision.** Result retention, publication retry, and the broker's `maxmemory-policy` and persistence all have defaults, and on defaults the composition looks correct and behaves otherwise: results accrue for a day on the instance the queue depends on, and a payroll caller inherits a retry policy tuned for a different failure. Each is asserted in configuration and each is a place a later convenience change can quietly undo this record.
- Redis introduces a component whose durability configuration matters, and the configuration above is load-bearing rather than incidental. A broker deployed on defaults, or merged back onto the cache instance for convenience, silently reintroduces the eviction path this decision closes — and it reintroduces it as data loss with no error, which is the hardest failure to notice. The deployment must assert the broker's `maxmemory-policy` and persistence settings rather than assume them.

**Rejected alternatives**

- *Lighter task libraries* (Django-Q2, Dramatiq, django-rq). Adequate at this scale with less ceremony. Rejected in favour of the conventional choice.
- *Database-backed brokers* (e.g. procrastinate). Would remove Redis entirely. Rejected for the same reason.
