# System Architecture Document

**Human Resource Management System**

| | |
|---|---|
| Version | 1.0 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-16 |
| Status | Draft — pending owner acceptance at M2 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-16 | Initial system architecture document, closing milestone M2 | 1.0 |
| John Kessie | 2026-07-18 | **Not yet reconciled with `docs/02-project-plan.md` v1.5.** The plan moved Dashboard from module 5 to module 14 (provider-precedes-consumer: Dashboard reads modules 10 and 13, not the reverse) and modules 6–14 below renumber to 5–13 accordingly. This document still uses the v1.4 numbering throughout §4 and elsewhere. Reconcile at M2 sign-off per plan §5.3, or before Module 5's real implementation begins, whichever comes first | 1.0 (unreconciled) |

---

## 1. Introduction

### 1.1 Purpose

This document decomposes the Human Resource Management System into modules, states each module's boundary and dependencies, and shows how the two cross-cutting concerns of this system — audit and notification — sit across that decomposition without becoming modules unto themselves everywhere they touch.

It does not select technology, which `docs/03-tech-stack.md` and ADR-0001 to ADR-0009 have already settled; it does not design the schema, which `docs/05-database-schema.md` will; and it does not specify the API surface, which `docs/06-api-contracts.md` will. Where this document repeats a decision from an earlier one, it is recording that decision for the module catalog below, not re-deciding it.

### 1.2 Intended Audience

Developers building each module, and the project owner reviewing the module boundaries before schema and API work begins against them.

### 1.3 Relationship to Prior Documents

This document is downstream of four documents it does not revise:

- **`docs/01-srs.md`** (v1.1) — the requirement set. Authoritative; where this document and the SRS disagree, the SRS governs.
- **`docs/02-project-plan.md`** (v1.4) — the twenty-module build order at §6.1, with its requirement assignment. This document is what §5.2 calls "records the assignment at M2" for module 1 (Audit) and module 11 (Notification), and what plan §11 questions 1 to 3 call the same for modules 15 and 1. **None of the three placements is reopened here.**
- **`docs/03-tech-stack.md`** (v1.0) and **ADR-0001 to ADR-0009** — the technology and architecture decisions this document builds against: modular monolith with a separate SPA (ADR-0001), Django/DRF (ADR-0002), PostgreSQL (ADR-0003), session-cookie authentication (ADR-0004), groups plus queryset scoping (ADR-0005), Celery/Redis (ADR-0006), S3-compatible storage (ADR-0007), Ant Design (ADR-0008), containerised deployment with hosting deferred (ADR-0009).
- **`docs/07-iam-rbac.md`** (v1.6) and **ADR-0010, ADR-0011** — produced out of order (plan §5.3). The role model, the permission matrix, the visibility-rule table, and the mail-dispatch/notification split are fixed inputs here, not choices this document makes.

Where this document names a requirement, a placement, or a constraint that one of those five sources already states, it cites the source rather than restating the argument.

### 1.4 Scope

In scope: the module decomposition (§4), the dependency structure between modules (§4, §5), how each module expresses the two access-control layers of ADR-0005 (§3.3), how audit and notification emission sit at each module (§3.1, §3.2), and the deployment topology those modules run under (§6).

Out of scope, per `CONTEXT.md` "Scope boundary" and SRS §6.4: biometric and facial-recognition attendance, AI recruitment screening, learning management, performance appraisal, complex shift scheduling, ERP and accounting integration, automatic tax filing, direct bank integration, loan management, travel and expense management, disciplinary case management, union management, multi-country payroll, chatbot support, native mobile application. A request touching any of these is a scope change requiring SRS revision, not an architecture decision.

---

## 2. Architectural Style

The system is a **modular monolith**: one Django/DRF deployable, divided into one Django application per application module of the build order at §4 — modules 1 to 17; modules 18 to 20 are process, not application, modules, and own no Django app (see the note at the foot of §4) — consumed by a separate React SPA under a single origin (ADR-0001; `docs/03-tech-stack.md` §3). This document's contribution is naming the modules, their boundaries, and the seams between them; the shape of the deployable is ADR-0001's decision, not this one's.

Two structural rules hold across every module, both inherited from ADR-0005 and applied here rather than chosen here:

- **Action-level access** is Django groups and permissions, checked once per endpoint against the permission matrix at `docs/07-iam-rbac.md` §4.2.
- **Row-level access** is a visibility rule — a queryset-scoping manager method, `<Model>.objects.visible_to(user)` — checked on every query returning employee-scoped data. §5 of the IAM document gives the rule per module; §3.3 below states the pattern that makes every module's rule the same shape.

A module is architecturally complete when its models, service layer, API endpoints, visibility rule, and permission tests exist and its permission tests assert both the permitted and the denied path (`docs/02-project-plan.md` §6.1; ADR-0005). This document does not restate that definition per module; it applies once, here.

---

## 3. Cross-Cutting Concerns

Two concerns recur in nearly every module and neither is a single piece of machinery. Plan §2.4 found this the hard way for audit (§11 question 3) and for notification (§11 question 2): each concern splits into an **owned surface**, built once, and **emission**, absorbed into each consumer. This section states the pattern once so the module catalog in §4 does not restate it twenty times.

### 3.1 Audit

**Owned surface: module 1, Audit.** One entity (SRS §6.1 "Audit log"; `CONTEXT.md` — audit log and audit history are the same store, not two), one append-only writer, one read surface restricted to System Administrator (`docs/07-iam-rbac.md` §4.2), and one database grant: the application's database role holds `INSERT` and `SELECT` on audit tables and neither `UPDATE` nor `DELETE` (`docs/07-iam-rbac.md` §7.3). This is what makes the log immutable — not a Django permission, which the break-glass account's `is_superuser` flag bypasses entirely.

**Emission: every module, absorbed.** HRMS-NFR-022 names five categories — login attempts, record changes, payroll actions, approvals, permission changes — plus the HRMS-NFR-024 second-factor events `docs/07-iam-rbac.md` §7.3 adds. A module writes to the audit log when one of its own actions falls into a category that applies to it; nothing central decides this for it. The module catalog in §4 marks which modules emit audit events and into which category, so that a module doing so has somewhere to look rather than inventing the shape of the call.

**Why module 1 precedes every other module.** Authentication (module 3) is the first consumer — login attempts are audited from the first request the system serves — so the provider must precede it. Audit consumes nothing itself: an append-only table, a writer, and a database grant need no other module to exist first. This is plan §6.1's own placement, and it is the one module number in the build order that is an absolute claim ("nothing precedes it") rather than a relative one; this document does not find anything that precedes it, and the placement stands.

### 3.2 Mail Dispatch and Notification

These are two modules, not one, per ADR-0011, and neither is the other's alias.

**Mail dispatch (module 2)** sends email reliably off the request cycle — Celery task, template rendering, bounded retry, delivery-failure logging (ADR-0006 provides the task queue; this module provides the domain logic wrapped around it) — and knows nothing about why a message is sent. Its consumers: password reset in Authentication (module 3), onboarding (module 10), Notification (module 11) for its email channel, and payroll communication (module 16). Delivery is best-effort: the domain action that triggered the email commits whether or not the send succeeds, and a delivery failure is written to application logs, never to the audit log — `CONTEXT.md` fixes the audit log's five categories and delivery failure is in none of them.

**Notification (module 11)** owns the entity and the in-app feed of pending tasks and request updates that SRS §3.4 describes and HRMS-FR-033/034 require. It is a consumer of mail dispatch for its email channel, not the channel itself. Its own consumers are the SRS §4.3 self-service modules and Leave Management — Employee Self-Service (module 12) is the first, which is why Notification sits immediately before it.

**Emission, for both, is absorbed per consumer**, on the same pattern as audit: a module decides which of its own events raises a notification or sends mail, and that decision is costed into the module, not into modules 2 or 11. The module catalog marks which modules emit into which provider.

**What does not emit into Notification.** Two approval flows already exist inside RBAC/IAM (module 4) before Notification is built — the ADR-0010 privileged-role-grant approval and the HRMS-NFR-024 second-factor recovery approval — and neither notifies its approver in this release. This was considered and declined (ADR-0011 rationale) because no SRS requirement asks for it: HRMS-FR-033 names *managers*, and a role-grant or recovery approver is not one by that requirement's own term. `CONTEXT.md` "Deployment conditions" records the resulting availability cost — an unnotified recovery approver, unreachable out-of-band, leaves a locked-out payroll user until someone looks, against the HRMS-NFR-005 elapsed-time bound on payroll. This document does not reopen that refusal; widening it is an SRS-scope question, not an implementation one.

### 3.3 The Visibility-Rule Seam

Every module that returns employee-scoped data implements one method with the same signature — `visible_to(user)` — on its primary queryset manager, and every endpoint reading that data obtains its queryset through it (ADR-0005; `docs/07-iam-rbac.md` §5). The rule reads organisational data already held elsewhere in the system (the reporting relationship of module 8, the employment status of module 6) rather than a permission record copied from it, for the reason ADR-0005 gives: a copy drifts, a derivation cannot.

This is the one seam that runs through every module in §4 without exception, so it is stated once here rather than per row: **a module without a stated visibility rule in §4 is a module whose row-level access this document has not yet answered**, and every row below answers it.

Two roles are wholly derived from this seam rather than granted through it (`docs/07-iam-rbac.md` §3): **Employee**, derived from holding an employee record whose employment status (module 6) permits access, and **Manager**, derived from having direct reports in the reporting relationship (module 8). Both derivations depend on module 6 and module 8 existing with the right columns before any module can compute them — a constraint this document states for `docs/05-database-schema.md` to carry, per plan §5.3's reconciliation requirement, rather than a design choice this document is free to make differently.

---

## 4. Module Catalog

The table gives, for each of the twenty modules of `docs/02-project-plan.md` §6.1 (v1.4 numbering — see that document's warning that sixteen of the twenty numbers changed at v1.4 and the change is not uniform), its principal requirements (restated from the plan, not re-derived), what it depends on within the build order, and how it participates in the two cross-cutting concerns of §3. "Consumes" lists modules whose data or capability this module reads or calls; it is not the build sequence, which plan §6.1 already fixes and this document does not reopen.

| # | Module | Consumes | Emits audit (§3.1) | Emits mail / notification (§3.2) | Visibility rule (§3.3) |
|---|---|---|---|---|---|
| 1 | Audit | — (see §3.1) | *is* the store | — | System Administrator only (read); no other role |
| 2 | Mail dispatch | — (Celery/Redis broker per ADR-0006; infrastructure, not a module dependency) | — | *is* the mail channel | — (no employee-scoped read surface) |
| 3 | Authentication | Module 1 (login events), Module 2 (password reset) | Login attempts, second-factor events (HRMS-NFR-024) | Sends via Module 2; consumes nothing from Module 11 | — (pre-identity; sessions are not employee-scoped data) |
| 4 | RBAC / IAM | Module 1 (permission-change events), Module 3 (authenticated identity) | Role grants, refused self-grants, privileged-grant approvals, credential resets on privileged accounts | Approvers not notified in this release (§3.2) | — (governs the mechanism other modules' rules use) |
| 5 | Dashboard | Modules 6, 14, 16, 17 (read-only, per role) | — | — | Delegates to the visibility rule of whichever module's data it renders |
| 6 | Employee Management | Module 7 (department), Module 8 (reporting relationship) | Record changes (HRMS-FR-010) | Emits notification-eligible events to Module 11 where a change concerns the affected employee | Employee: own record. Manager: direct reports. HR Officer/HR Administrator: all (`docs/07-iam-rbac.md` §5) |
| 7 | Departments | — | Configuration changes | — | HR Administrator: create/update. All HR/Recruiter/Payroll: read |
| 8 | Reporting Structure | Module 6 (employee identities) | Record changes | — | Feeds the Manager derivation (§3.3); no independent read restriction beyond Module 6's |
| 9 | Recruitment | Module 6 (conversion target), Module 8 (approving manager, if any) | Requisition and offer decisions | Consumes neither Module 2 nor Module 11 (ADR-0011 rationale — no SRS requirement names a recruitment notification) | Recruiter: full. HR Administrator: read. Others: none |
| 10 | Onboarding | Module 9 (candidate conversion), Module 6 (employee record created) | Onboarding task completion | Sends via Module 2 (email-only; ADR-0011 §"Why the surface sits at 11") | HR Officer: create/read/update. HR Administrator, Recruiter: read |
| 11 | Notification | Module 2 (email channel) | — | *is* the in-app store; emission absorbed per consumer (§3.2) | Employee/Manager: own notifications only |
| 12 | Employee Self-Service | Module 6 (own record), Module 11 (own notifications) | Self-service updates routed for approval | Consumes Module 11 (first consumer — why Notification precedes this module) | Employee: own record only (HRMS-NFR-017, HRMS-BR-006) |
| 13 | Manager Self-Service | Module 8 (direct reports), Module 11 (approval tasks) | Approval/rejection decisions | Consumes Module 11 | Manager: direct reports only (HRMS-NFR-018, HRMS-BR-007) |
| 14 | Leave Management | Module 6 (employee), Module 13 (manager approval) | Leave approval/rejection (HRMS-BR-010, HRMS-BR-011) | Consumes Module 11 for pending-approval and decision notices | Employee: own requests. Manager: direct reports'. HR: all |
| 15 | Compensation and Benefits | Module 6 (employee identity) | Compensation history changes (HRMS-DR-010: never overwritten) | — | HR Administrator: create/read/update structures. HR Officer: assign, read. Payroll Officer: read |
| 16 | Payroll | Module 15 (compensation records), Module 2 (payroll communication) | Payroll actions; finalisation approvals, including refused self-approvals — approver must not be the initiator (HRMS-BR-008; `docs/07-iam-rbac.md` §4.4) | Sends via Module 2 | Payroll Officer: all payroll fields. Employee: own payslip only (HRMS-BR-006) |
| 17 | Reports | Modules 6, 14, 15, 16 (read-only aggregation) | Report exports where they touch payroll cost | — | Per source module's rule; Executive: aggregate only, never an individual record (`docs/07-iam-rbac.md` §4.3) |
| 18 | Testing | All prior modules | — | — | n/a |
| 19 | UAT | All prior modules | — | — | n/a |
| 20 | Deployment | All prior modules | — | — | n/a |

Modules 18 to 20 are process, not application modules; they appear in the plan's build order and are listed here for completeness, but own no visibility rule or emission of their own — plan §6.1 gives their principal requirements as testing standards, SRS §4 acceptance sequences, and ADR-0009's decision rule respectively, none of which this document's catalog format applies to.

### 4.1 The Dependency Graph

```
1  Audit               <- (nothing; §3.1)
2  Mail dispatch       <- (nothing; sequenced after Audit in build order only — Celery/Redis is ADR-0006 infrastructure, not a module)
3  Authentication      <- 1, 2
4  RBAC / IAM          <- 1, 3
5  Dashboard           <- 6, 14, 16, 17
6  Employee Mgmt       <- 7, 8
7  Departments         <- (nothing beyond 1, 3, 4 as every module has)
8  Reporting Structure <- 6
9  Recruitment         <- 6, 8
10 Onboarding          <- 9, 6, 2
11 Notification        <- 2
12 Employee Self-Svc   <- 6, 11
13 Manager Self-Svc    <- 8, 11
14 Leave Management    <- 6, 13, 11
15 Compensation        <- 6
16 Payroll             <- 15, 2
17 Reports             <- 6, 14, 15, 16
```

Every module after 4 additionally depends on Authentication and RBAC/IAM for identity and action-level permission, which is why the arrows above start at 5: modules 1 to 4 are the base every later module builds on, and restating that dependency on each of sixteen rows would say the same thing sixteen times. **No arrow points backward** — this is the same provider-precedes-consumer rule plan §6.1 states and applies to Audit and to mail dispatch/Notification; §4's table is this document's check that the rule holds for the other fifteen modules too, not only the three plan §11 settled by name.

**One dependency this graph deliberately excludes:** Authentication does not depend on Notification. That non-relation is ADR-0011's finding, not an omission — plan §2.4 v1.1 to v1.3 implied it did, by listing Notification (then at module 8) as password reset's provider, and ADR-0011 corrected it: Authentication consumes mail dispatch directly.

---

## 5. Requirement Assignment

This section is the record plan §5.2 asks for: it restates the three placements plan §11 closed by owner confirmation, without reopening any of them.

**Module 1, Audit — HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015.** Placed first because it has no consumer among the twenty modules and one consumer — Authentication — that must not precede it (§3.1). Confirmed by the project owner 2026-07-15 (plan §6.1, §11 question 3).

**Modules 2 and 11, Mail dispatch and Notification — SRS §3.3, §3.4; HRMS-FR-033, HRMS-FR-034.** Split three ways per ADR-0011: sending (module 2), the in-app store (module 11), emission (absorbed, every consumer). Confirmed by the project owner 2026-07-15 (plan §6.1, §11 question 2).

**Module 15, Compensation and Benefits — HRMS-FR-056 to HRMS-FR-062.** Placed immediately before Payroll because Payroll computes over compensation records that must already exist (`CONTEXT.md` — compensation record; HRMS-DR-010). Confirmed by the project owner 2026-07-15 (plan §6.1, §11 question 1).

This document finds no fourth placement that needs the same treatment: §4.1's dependency graph has no back-reference, and the visibility-rule seam of §3.3 is uniform across the remaining sixteen modules. Per plan §5.3, `docs/07-iam-rbac.md` is re-read against this document as part of this milestone's sign-off: no inconsistency was found. The IAM document's derived-role dependency on modules 6 and 8 (§3.3 above) and its payroll-approver-not-initiator constraint (`docs/07-iam-rbac.md` §4.4) are both already reflected in the module 6/8 ordering and in module 16's row above; neither required a change to either document.

---

## 6. Deployment Topology

Restated from ADR-0009 and `docs/03-tech-stack.md` §7.1 for this document's own completeness, not re-decided:

```
                        Caddy (reverse proxy, single origin)
                         /                              \
              /  (static)                          /api  (proxied)
     React SPA build                    Django + DRF (all 17 application
                                          modules of §4, one deployable)
                                                |
                    +---------------------------+---------------------------+
                    |                           |                           |
              PostgreSQL                 redis-broker                redis-cache
           (all HRMS data;              (Celery queue,              (Django cache,
          NUMERIC for money,             noeviction, AOF)            rate limiting,
           ADR-0003)                          |                       allkeys-lru)
                                        Celery worker + beat
                                        (payroll, accrual, mail
                                         dispatch, report export)
                                               |
                                            MinIO
                                     (S3-compatible object
                                      store, employee documents;
                                      private bucket, signed URLs)
```

One deployable for all seventeen application modules (ADR-0001); one Celery worker pool consuming one queue, serving payroll processing, leave accrual, payslip/bank-file generation, mail dispatch, and report export (ADR-0006); two Redis instances, isolated so that cache eviction cannot discard a queued payroll task (ADR-0006, and `docs/03-tech-stack.md` §4.2). The hosting target this composition runs on is open — TBD-003, ADR-0009 — and this document does not narrow it; the composition is chosen to run identically wherever that target lands.

---

## 7. Non-Functional Requirements Placed

This document does not re-derive the non-functional requirements SRS §5 states or the technology choices `docs/03-tech-stack.md` already assigns to them. What follows is where each is architecturally satisfied, so a reader does not have to cross-reference two documents to find out.

| Requirement | Where satisfied |
|---|---|
| HRMS-NFR-005 (payroll elapsed time) | Module 16, off the request cycle via the Celery worker of §6 (ADR-0006) |
| HRMS-NFR-006 (50–200 concurrent users) | The modular-monolith shape of §2; ADR-0001 found no scaling boundary this system approaches |
| HRMS-NFR-013, HRMS-NFR-022 (audit logging) | Module 1, §3.1 |
| HRMS-NFR-016 to HRMS-NFR-019 (RBAC, row-level restriction) | Module 4 for action-level; §3.3's visibility-rule seam, applied per module in §4, for row-level |
| HRMS-NFR-024 (second-factor authentication) | Modules 3 and 4, per `docs/07-iam-rbac.md` §7.3 |
| HRMS-NFR-020 (HTTPS) | §6's composition — Caddy terminates TLS as part of the deployable itself, independent of hosting target |
| HRMS-NFR-012 (backups), HRMS-NFR-035 (availability) | Explicitly deployment-dependent and open under TBD-003 (ADR-0009): "backup topology and availability measures... cannot be finalised until the target is known." Not satisfied by §6, and this document does not claim otherwise |
| HRMS-NFR-029 (cross-module data consistency) | PostgreSQL transactional boundaries within the single deployable of §2 (ADR-0003); no distributed-transaction concern exists because there is one database |
| HRMS-NFR-030, HRMS-NFR-032 (modular architecture, extensibility) | The module boundary itself — §2, §4 |

---

## 8. Traceability

| Architecture element | Serves |
|---|---|
| §2 architectural style | ADR-0001; SRS §2.1 |
| §3.1 audit pattern | HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015; `docs/02-project-plan.md` §6.1, §11 question 3; `docs/07-iam-rbac.md` §7.3 |
| §3.2 mail/notification pattern | SRS §3.3, §3.4; HRMS-FR-033, HRMS-FR-034; ADR-0011 |
| §3.3 visibility-rule seam | ADR-0005; `docs/07-iam-rbac.md` §3, §5 |
| §4 module catalog | `docs/02-project-plan.md` §6.1 build order, in full |
| §5 requirement assignment | `docs/02-project-plan.md` §11 questions 1, 2, 3; §2.4 |
| §6 deployment topology | ADR-0009; `docs/03-tech-stack.md` §7.1; ADR-0006 |
| §7 non-functional placement | SRS §5.1 to §5.4 |

---

## 9. Open Items Inherited, Not Introduced

This document introduces no new TBD. The items below are open in the documents this one is downstream of, bear on the architecture as described, and are restated here only so a reader of this document is not left to assume they were resolved by it.

- **TBD-003 (hosting target).** Open by decision (ADR-0009). §6's topology runs unchanged regardless of the eventual target.
- **Which roles HRMS-NFR-024 covers, beyond System Administrator and Payroll Officer.** Open (`docs/07-iam-rbac.md` §8). Bears on module 4's second-factor scope, not on the module boundary itself.
- **`iam.approve_role_grant` and second-factor recovery approver holders.** Deferred to deployment (`docs/07-iam-rbac.md` §8; `CONTEXT.md` "Deployment conditions"). Module 4's design does not depend on who is designated, only on someone being.
- **Payroll finalisation approver.** Resolved as a deployment-time grant, not a design-time choice (`docs/07-iam-rbac.md` §4.4). Module 16 enforces the approver-not-initiator constraint regardless of who holds the permission.

---

**Sign-off.** Per `docs/02-project-plan.md` §5.2, this milestone is met when the project owner has read this document and accepted it.
