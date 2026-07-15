# Project Plan

**Human Resource Management System**

| | |
|---|---|
| Version | 1.1 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-15 |
| Status | Approved |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-15 | Initial project plan. Authored after `docs/03-tech-stack.md` and `docs/07-iam-rbac.md`; records the sequence, effort, and risk position for the remaining work | 1.0 |
| John Kessie | 2026-07-15 | Schedule re-baselined to 2026-10-21 on the project owner's decision to take Option B of §7.5 and extend the end date rather than reduce the content of the release. Because scope is not reduced, the §2.4 coverage gap is closed rather than carried: Compensation and Benefits and Notification enter the build order, and the plan is baselined on the 68-day figure of §7.3 rather than the 62.5-day figure of §7.1. §§2.4, 5.2, 6.1, 6.2, 7, 8.2, 11 revised accordingly | 1.1 |

---

## 1. Introduction

### 1.1 Purpose

This document plans the construction of the Human Resource Management System: what is delivered, in what order, by when, at what effort, and against what risks.

It does not restate requirements, which are held in the Software Requirements Specification, and it does not select technology, which is settled in `docs/03-tech-stack.md` and the architecture decision records. Where this document and the SRS disagree, the SRS governs.

This document is being authored out of sequence. It is deliverable 02; deliverable 03 and deliverable 07 were completed before it. Section 5.3 records that position rather than concealing it.

**Section 7 is the operative section of this plan.** At v1.0 it recorded that the confirmed scope did not fit the confirmed schedule, showed the arithmetic, and stated the decision the project owner had to take. That decision has been taken: the end date moves to 2026-10-21 and the content of the release is not reduced. Section 7 now records the arithmetic that produced the new date, the margin it leaves, and the original finding, which is retained because a plan that deletes the overrun it once reported cannot be checked. A reader with time for one section should read that one.

### 1.2 Intended Audience

The project owner, and any developer, reviewer, or examiner who needs to know the state of the project and the basis on which its schedule was set. Sections 2, 5, 7, and 8 are the substance; Sections 3, 4, 9, and 10 record method.

### 1.3 Basis of Planning

1. The SRS is authoritative and is not reduced or extended by this plan.
2. Estimates are stated as working days of a single person and are the author's judgement. **No historical velocity exists for this project or this author on this stack.** The estimates are therefore uncalibrated, and Section 7.4 says what follows from that.
3. Where an input is unknown, the plan names it as unknown and names what would resolve it. It does not supply a figure to fill the gap.
4. A schedule that does not fit is reported as not fitting.

### 1.4 Related Documents

| Document | Content |
|---|---|
| `docs/01-srs.md` | Software Requirements Specification v1.1. Authoritative |
| `CONTEXT.md` | Domain glossary, design constraints, scope boundary |
| `docs/03-tech-stack.md` | Technology selection |
| `docs/07-iam-rbac.md` | IAM and role-based access control design |
| `docs/adr/` | Architecture decision records ADR-0001 to ADR-0010 |
| `docs/agents/issue-tracker.md` | Issue and pull request conventions |

---

## 2. Scope Baseline

### 2.1 What Is In

The requirement set of `docs/01-srs.md` v1.0: 71 functional requirements (HRMS-FR-001 to HRMS-FR-071), 36 nonfunctional requirements (HRMS-NFR-001 to HRMS-NFR-036), 15 business rules (HRMS-BR-001 to HRMS-BR-015), and 10 data validation rules (HRMS-DR-001 to HRMS-DR-010).

### 2.2 What Is Out

The items listed at SRS §6.4, reproduced in `CONTEXT.md` under "Scope boundary". A request touching any of them is a scope change requiring SRS revision. This plan makes no such request.

### 2.3 Deferred by the SRS Itself

HRMS-FR-055 requires predictive attrition analytics "in later versions where enough historical data exists". The condition is not met: the system holds no historical HR data and, per TBD-001, has no operating organisation to supply any. The requirement is therefore not built in this release. This is the SRS's own deferral, not a reduction made by this plan.

### 2.4 Requirements Without a Module, and How the Gap Was Closed

At v1.0 the module build order had no module that owned the requirements below. The gap was recorded rather than resolved, because assigning requirements to modules is an architecture decision belonging to `docs/04-system-architecture.md`.

The gap is now closed. It is closed because the owner's decision at §7.5 was to extend the end date and not to reduce the content of the release, and requirements with no module owner are requirements that do not get built. Carrying the gap forward under a decision that scope is not cut would have cut scope silently, which is the one outcome the decision excludes. The build order at §6.1 therefore names an owner for each row, and §7 is baselined on the resulting 68-day figure rather than the 62.5-day figure that omitted them.

| Requirements | Subject | Position at v1.0 | Owner at v1.1 |
|---|---|---|---|
| HRMS-FR-056 to HRMS-FR-062 | Salary structures, pay grades, bonus cycles, allowances, benefits enrolment, compensation history | SRS §4.6, a Phase 3 function. No module in the build order owned it. `docs/07-iam-rbac.md` §4.2 already assigned permissions for these requirements, so the design assumed an implementation surface the build order did not name | Compensation and Benefits, §6.1 module 13, 4 days. Placed immediately before Payroll on the dependency reasoning at §6.1. **Confirmed by the project owner, 2026-07-15** |
| HRMS-FR-033, HRMS-FR-034 | Approval and decision notification, in-app and email (SRS §3.4) | Cross-cutting. Consumed by Recruitment, Onboarding, Leave, and Payroll. No module owned it | Notification, §6.1 module 7, 1.5 days. Placed before the first module with an approval flow; §6.1 states why |
| HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015 | Audit log | Cross-cutting. Design existed at `docs/07-iam-rbac.md` §7.3; no module owned the implementation | Absorbed within M2 RBAC/IAM and M4 Employee Management, per §7.3. It is not a separate module and carries no separate estimate |

**The record that the gap existed is retained deliberately.** That `docs/07-iam-rbac.md` §4.2 assigned permissions for HRMS-FR-056 to HRMS-FR-062 across five roles before any module owned those requirements is a finding about how the documents were produced, not a clerical error to be tidied away. An accepted design gating an implementation surface that the build order did not name is the kind of divergence the reconciliation check at §5.3 exists to catch, and it was caught by planning rather than by discovering the missing module during development.

The placement of Compensation and Benefits immediately before Payroll is confirmed by the project owner, 2026-07-15, on the dependency reasoning set out at §6.1. **The placement of Notification at module 7 is the plan's inference and is not confirmed.** The owner confirmed the extension, confirmed that scope is not cut, and confirmed where Compensation and Benefits sits; he did not speak to Notification. Section 11 carries that placement as an open question for his confirmation, and `docs/04-system-architecture.md` remains the document that decides it at M2.

---

## 3. Resourcing

**The project is executed by one person.** John Kessie performs every role: Product Owner, Scrum Master, Architect, Backend Developer, Frontend Developer, Quality Assurance, DevOps, and Documentation.

This is a statement of fact with three consequences that the rest of this plan is built on.

**No parallelism.** Every hour spent on one role is not spent on another. The plan schedules one activity at a time and does not model concurrent workstreams. Where a conventional plan would overlap development with test authoring, this plan places them in sequence, because the same pair of hands performs both.

**No independent review.** Quality assurance is performed by the person who wrote the code. The mitigation is mechanical rather than social: automated permission tests, schema-generated API contracts, and CodeRabbit automated review on `develop`. Section 9 records what this does and does not achieve.

**Sign-off is self-review.** There is no approval board, steering committee, or external stakeholder gate, because there is no organisation (TBD-001). A milestone is reached when the project owner reviews the document and accepts it. Section 5.2 states this plainly so that the milestone list is not mistaken for external validation.

Capacity is taken as five working days per week for one person. The repository defines no working calendar and no public holiday schedule; Section 11 carries this as an open question, and no allowance for holidays, illness, or rework is included in any estimate in this document.

---

## 4. Lifecycle and Stages

Development follows eleven stages. None is skipped.

| # | Stage | Status |
|---|---|---|
| 1 | Discovery | Complete |
| 2 | Requirements Gathering | Complete — `docs/01-srs.md` v1.0 |
| 3 | Planning | **Delivered by this document** |
| 4 | System Architecture | Partially complete out of order — see §5.3 |
| 5 | Environment Setup | Not started |
| 6 | Development | Not started |
| 7 | Testing | Not started |
| 8 | UAT | Not started |
| 9 | Deployment | Blocked — see §8.3 |
| 10 | Documentation | Not started |
| 11 | Handover | Not started |

The SRS phases work into three groups (SRS §1.4, §2.2). The module build order in Section 6.1 follows those phases, with two departures the SRS permits: Authentication and RBAC precede Phase 1 functionality because every Phase 1 requirement depends on them, and Leave Management is built before Reports because Reports consumes leave data.

---

## 5. Deliverables and Milestones

### 5.1 Document Set

| Document | Subject | Status |
|---|---|---|
| `docs/01-srs.md` | Software Requirements Specification | **Complete** — accepted 2026-05-21 |
| `docs/02-project-plan.md` | Project Plan | This document |
| `docs/03-tech-stack.md` | Technology Stack | **Complete** — accepted 2026-07-15 |
| `docs/04-system-architecture.md` | System Architecture | Scheduled |
| `docs/05-database-schema.md` | Database Schema | Scheduled |
| `docs/06-api-contracts.md` | API Contracts | Scheduled |
| `docs/07-iam-rbac.md` | IAM and RBAC Design | **Complete** — accepted 2026-07-15. Out of order; see §5.3 |
| `docs/08-testing-plan.md` | Testing Plan | Scheduled |
| `docs/09-deployment-plan.md` | Deployment Plan | Scheduled, and constrained; see §8.3 |
| `docs/10-user-guide.md` | User Guide | Scheduled |

The confirmed document sequence is 04 → 05 → 06 → 07. Each depends on its predecessor: the schema is designed against the architecture, the API contracts against the schema, and the access control design against the API surface it gates.

### 5.2 Milestones

One milestone per document sign-off. A milestone is the document being accepted, not a phase ending.

**Sign-off means the project owner has read the document and accepted it.** Nothing more is implied. There is no approval body. The value of the milestone is that the document is finished and subsequent work may rely on it; its authority derives from consistency with the SRS, not from an endorsement.

| Milestone | Document | Target date | Basis |
|---|---|---|---|
| M1 | `docs/02-project-plan.md` | 2026-07-16 | Week 1 of §6.2 |
| M2 | `docs/04-system-architecture.md` | 2026-07-21 | Week 1 of §6.2 |
| M3 | `docs/05-database-schema.md` | 2026-07-27 | Week 2 of §6.2 |
| M4 | `docs/06-api-contracts.md` | 2026-07-29 | Week 2 of §6.2 |
| M5 | `docs/08-testing-plan.md` | 2026-07-30 | Weeks 2 and 3 of §6.2. Precedes development; see §6.2 |
| M6 | `docs/09-deployment-plan.md` | 2026-10-16, and constrained | Week 14 of §6.2. Schedulable; not completable while TBD-003 is open. See §8.3 |
| M7 | `docs/10-user-guide.md` | 2026-10-19 | Week 14 of §6.2 |

At v1.0, M6 and M7 carried no date, because the arithmetic then available produced none inside 2026-09-09. The window has moved to 2026-10-21 and both are now schedulable. The dates above are the first at which each document can be finished on the allocation at §6.2; they are not independent commitments and they inherit every qualification of §7.4.

**M6's separate constraint is unchanged by the extension.** It is now schedulable, and it still cannot be *completed* while TBD-003 is open, because the decision rule at ADR-0009 requires legal confirmation, registration where applicable, and a target satisfying HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035, none of which a longer schedule supplies. The 2026-10-16 date is when `docs/09-deployment-plan.md` is written to that decision rule with TBD-003 recorded as open. It is not when a hosting target is selected. Section 8.3 explains.

**The M5 decision deadline of 2026-07-30 is retired as a decision deadline.** At v1.0 it gated the Option A/B/C choice of §7.5, and that choice has been taken. Nothing is served by carrying a deadline for a decision already made, and carrying one would misrepresent the gate as still live.

What the gate protected does remain live, so it is repointed rather than dropped. The build order must be settled before development begins, and development begins in week 3 of §6.2. The two modules added at §6.1 are this plan's inference and are carried at §11 as questions 1 and 2 for the owner's confirmation; `docs/04-system-architecture.md` decides them at M2, 2026-07-21. **Their confirmation is therefore due at M2, and 2026-07-30 stands only as the last date by which it may slip without spending capacity on an order that may be revised.** The corresponding row of §8.4 is updated to match.

The milestones for `docs/01-srs.md`, `docs/03-tech-stack.md`, and `docs/07-iam-rbac.md` are already met.

### 5.3 Deliverable 07 Was Produced Out of Order

`docs/07-iam-rbac.md` is complete and accepted, ahead of 04, 05, and 06 on which it would normally depend. The plan records this rather than scheduling work that is already done.

This has a consequence the later documents must respect. The IAM design fixes decisions that 04, 05, and 06 would otherwise have been free to make:

- ADR-0005 and `docs/07-iam-rbac.md` §5 fix row-level access as queryset scoping through a per-module visibility rule. `docs/04-system-architecture.md` inherits this; it does not choose it.
- `docs/07-iam-rbac.md` §3 fixes the Employee and Manager roles as derived from employment status and from the reporting relationships of HRMS-FR-008. `docs/05-database-schema.md` must carry employment status and reporting relationship as first-class columns capable of supporting a query-time derivation, because the role model depends on it.
- `docs/07-iam-rbac.md` §4.2 assigns permissions per module against named requirement ranges. `docs/06-api-contracts.md` inherits that matrix as the specification of what each endpoint gates.
- `docs/07-iam-rbac.md` §4.4 requires that the payroll approver is not the initiator. This is a constraint on the payroll run record and belongs in `docs/05-database-schema.md`.

The risk of out-of-order authorship is that the earlier document assumed something the later one contradicts. Accordingly, on completion of 04, 05, and 06, `docs/07-iam-rbac.md` is re-read against each and any inconsistency is resolved in favour of whichever document the SRS supports. That check is part of the M2, M3, and M4 sign-offs and is not separately scheduled.

---

## 6. Schedule

### 6.1 Module Build Order

| # | Module | Principal requirements |
|---|---|---|
| 1 | Authentication | HRMS-NFR-014, HRMS-NFR-015, HRMS-NFR-020, HRMS-NFR-023; ADR-0004 |
| 2 | RBAC / IAM | HRMS-NFR-016 to HRMS-NFR-019, HRMS-BR-005, HRMS-BR-012, HRMS-BR-014; `docs/07-iam-rbac.md` |
| 3 | Dashboard | SRS §3.1 role-specific dashboards |
| 4 | Employee Management | HRMS-FR-001 to HRMS-FR-012, HRMS-BR-001 to HRMS-BR-003, HRMS-DR-001 to HRMS-DR-004, HRMS-DR-007, HRMS-DR-008, HRMS-DR-010, HRMS-NFR-007, HRMS-NFR-008 |
| 5 | Departments | HRMS-BR-002; SRS §2.7 HR configuration |
| 6 | Reporting Structure | HRMS-FR-008, HRMS-BR-004 |
| 7 | **Notification** | **HRMS-FR-033, HRMS-FR-034; SRS §3.4 in-app and email channels** |
| 8 | Recruitment | HRMS-FR-013 to HRMS-FR-021 |
| 9 | Onboarding | HRMS-FR-022 to HRMS-FR-024, HRMS-BR-013 |
| 10 | Employee Self-Service | HRMS-FR-025 to HRMS-FR-029, HRMS-FR-044, HRMS-NFR-017, HRMS-BR-006 |
| 11 | Manager Self-Service | HRMS-FR-030 to HRMS-FR-032, HRMS-NFR-018, HRMS-BR-007 |
| 12 | Leave Management | HRMS-FR-063 to HRMS-FR-071, HRMS-BR-009 to HRMS-BR-011, HRMS-DR-006 |
| 13 | **Compensation and Benefits** | **HRMS-FR-056 to HRMS-FR-062, HRMS-DR-010; `docs/07-iam-rbac.md` §4.2** |
| 14 | Payroll | HRMS-FR-035 to HRMS-FR-048, HRMS-BR-008, HRMS-DR-005, HRMS-DR-009, HRMS-NFR-005, HRMS-NFR-009, HRMS-NFR-010 |
| 15 | Reports | HRMS-FR-049 to HRMS-FR-054 |
| 16 | Testing | HRMS-NFR-028, HRMS-NFR-029; `docs/08-testing-plan.md` |
| 17 | UAT | SRS §4 acceptance against stimulus/response sequences |
| 18 | Deployment | HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035; ADR-0009 |

Modules 7 and 13 are new at v1.1 and close the coverage gap of §2.4. The modules that followed them are renumbered; references elsewhere in this document use the v1.1 numbers throughout.

**Why Compensation and Benefits precedes Payroll.** This placement is confirmed by the project owner, 2026-07-15, on the reasoning that follows. It is not placed at 13 because SRS §4.6 is a Phase 3 function and Phase 3 comes late. It is placed at 13 because Payroll cannot be built before it. `CONTEXT.md` defines a compensation record as a dated record of an employee's compensation whose changes are stored as history and never overwritten (HRMS-DR-010), and defines a payroll run as one execution of payroll for a period over active employees. Payroll computes over compensation records; HRMS-FR-035 to HRMS-FR-048 have nothing to compute over until the records exist. Building Payroll first would mean building a calculation engine against a table that does not exist, then revising it when the table arrives — rework in a schedule that §7.4 says has no room for any. The dependency runs one way: Compensation and Benefits does not require Payroll.

**Why Notification precedes Recruitment.** §2.4 records notification as consumed by Recruitment, Onboarding, Leave, and Payroll. It is placed at 7 because Recruitment is the earliest of those and is the first module in the order with an approval flow: HRMS-FR-014 gives job requisitions approval statuses, and HRMS-FR-033 and HRMS-FR-034 are the notification of a pending approval and of the decision on it. An approval flow built before the notification it fires either ships without notifying, which leaves HRMS-FR-033 and HRMS-FR-034 unmet in a module that needs them, or is revisited once Notification lands. Placing it at 7 costs 1.5 days once and serves four consumers; placing it later costs a return visit to each consumer already built. Modules 1 to 6 have no approval flow and do not need it.

**The two placements do not stand on the same authority, and the numbering reflects only one of them.** The owner confirmed Compensation and Benefits as sitting immediately before Payroll; that relation is what he confirmed, and it holds at module 13 here. It is numbered 13 rather than 12 solely because Notification occupies 7 and displaces everything after it by one. Should Notification be placed elsewhere or dropped from the order at M2, Compensation and Benefits returns to 12 with its confirmed relation to Payroll intact. **The Notification placement at 7 is the plan's inference and is carried at §11 as question 2 for the owner's confirmation.** `docs/04-system-architecture.md` decides it at M2, as §2.4 and §5.2 record.

A module is complete when its models, service layer, API endpoints, visibility rule, permission tests, and client interface are done and its tests pass. A module without permission tests asserting both the permitted and the denied path is not complete (ADR-0005; `docs/07-iam-rbac.md` §5).

### 6.2 Week-by-Week Allocation

Week boundaries fall on Wednesdays. Each week carries five working days. The window runs 2026-07-15 to 2026-10-21: 14 weeks, 70 working days, against the 68 required by §7.3.

| Week | Ends | Allocation |
|---|---|---|
| 1 | 2026-07-22 | `docs/02-project-plan.md` (1d); Environment Setup (2d); `docs/04-system-architecture.md` (2d) |
| 2 | 2026-07-29 | `docs/05-database-schema.md` (2d); `docs/06-api-contracts.md` (2d); `docs/08-testing-plan.md` (1d of 2) |
| 3 | 2026-08-05 | `docs/08-testing-plan.md` (1d); M1 Authentication (2d); M2 RBAC/IAM (2d of 3) |
| 4 | 2026-08-12 | M2 RBAC/IAM (1d); M3 Dashboard (1.5d); M4 Employee Management (2.5d of 4) |
| 5 | 2026-08-19 | M4 Employee Management (1.5d); M5 Departments (1d); M6 Reporting Structure (1.5d); M7 Notification (1d of 1.5) |
| 6 | 2026-08-26 | M7 Notification (0.5d); M8 Recruitment (4d); M9 Onboarding (0.5d of 2) |
| 7 | 2026-09-02 | M9 Onboarding (1.5d); M10 Employee Self-Service (2.5d); M11 Manager Self-Service (1d of 2) |
| 8 | 2026-09-09 | M11 Manager Self-Service (1d); M12 Leave Management (4d) |
| 9 | 2026-09-16 | M13 Compensation and Benefits (4d); M14 Payroll (1d of 8) |
| 10 | 2026-09-23 | M14 Payroll (5d) |
| 11 | 2026-09-30 | M14 Payroll (2d); M15 Reports (3d) |
| 12 | 2026-10-07 | M16 Testing (4d); M17 UAT (1d of 3) |
| 13 | 2026-10-14 | M17 UAT (2d); M18 Deployment (3d) |
| 14 | 2026-10-21 | `docs/09-deployment-plan.md` (1.5d); `docs/10-user-guide.md` (1.5d); **2d unallocated** |

Weeks 1 to 4 are unchanged from v1.0; the re-baseline does not disturb them, and they are not rewritten to look revised. Week 5 changes at its last day only, where Notification takes the slot Recruitment held. Everything from week 6 is displaced by the 5.5 days the two new modules add.

**The 2 unallocated days in week 14 are slack, and they are shown as slack.** 68 days of work are allocated against 70 days of capacity. The two days are not filled with work to make the table reach the end date, and no estimate elsewhere has been enlarged to absorb them, because a plan that pads its estimates to consume its margin has no margin and has also lost the ability to say what anything costs. They are the whole of the buffer between this schedule and 2026-10-21. Section 7.4 states what 2 days of buffer against 68 days of uncalibrated estimate is worth.

The table is the consequence of the estimates in Section 7.1 laid against the confirmed order. It is not compressed to reach the end date. `docs/08-testing-plan.md` precedes development deliberately: tests are written against a plan, and writing the plan after the code it judges would defeat the only independent control this project has (Section 3). The extension does not change this, and the testing plan is not moved later to bring development forward.

The allocation assumes work proceeds in the order given, with no module overrunning. Where a module overruns, it consumes the 2 days first and the end date afterwards. There is nothing else for it to consume.

---

## 7. Schedule Feasibility

### 7.1 Effort Estimate

Working days, one person, everything included: models, migrations, service layer, API, client, and tests.

| Item | Days | Note |
|---|---|---|
| `docs/02-project-plan.md` | 1 | |
| Environment Setup | 2 | Docker Compose composition per ADR-0009: Django, Celery worker and beat, Redis, PostgreSQL, MinIO, Caddy |
| `docs/04-system-architecture.md` | 2 | |
| `docs/05-database-schema.md` | 2 | 27 data entities at SRS §6.1 |
| `docs/06-api-contracts.md` | 2 | Generated by drf-spectacular per `docs/03-tech-stack.md` §9, but the surface must be designed first |
| `docs/08-testing-plan.md` | 2 | |
| M1 Authentication | 2 | |
| M2 RBAC / IAM | 3 | Groups, two derived roles, per-module visibility rules, the `is_superuser` prohibition of `docs/07-iam-rbac.md` §7.2 |
| M3 Dashboard | 1.5 | |
| M4 Employee Management | 4 | 12 FRs, document upload, audit history |
| M5 Departments | 1 | |
| M6 Reporting Structure | 1.5 | |
| M7 Notification | 1.5 | HRMS-FR-033, HRMS-FR-034; in-app and email channels of SRS §3.4. New at v1.1; see §7.3 |
| M8 Recruitment | 4 | 9 FRs, requisition approval, interview scheduling, offer generation |
| M9 Onboarding | 2 | |
| M10 Employee Self-Service | 2.5 | |
| M11 Manager Self-Service | 2 | |
| M12 Leave Management | 4 | 9 FRs, balance arithmetic, policy enforcement, calendar |
| M13 Compensation and Benefits | 4 | 7 FRs; salary structures, pay grades, bonus cycles, allowances, benefits enrolment; compensation history as dated records per HRMS-DR-010. New at v1.1; see §7.3 |
| M14 Payroll | 8 | 14 FRs; PAYE, SSNIT Tier 1, Tier 2, Tier 3; versioned rate tables; atomic finalisation; idempotent Celery tasks; payslips; bank transfer file |
| M15 Reports | 3 | |
| M16 Testing | 4 | Hardening beyond per-module tests |
| M17 UAT | 3 | |
| M18 Deployment | 3 | |
| `docs/09-deployment-plan.md` | 1.5 | |
| `docs/10-user-guide.md` | 1.5 | Nine guides at SRS §2.6, less the optional training videos |
| **Total** | **68** | Of which 62.5 was the v1.0 baseline and 5.5 is the §2.4 coverage gap now closed |

### 7.2 The Arithmetic

The window is 2026-07-15 to 2026-10-21: **14 weeks at 5 working days for one person = 70 working days.** Against the 68 required by §7.3:

- Available: **70 working days**.
- Required: **68 working days**.
- Margin: **2 working days**, approximately 3% of the required effort.
- Ratio: **0.97 times the available capacity.**

68 working days from 2026-07-15, at five days a week with no slippage, completes on **2026-10-16**, a Friday. The end date is set at 2026-10-21 rather than 2026-10-16 because week boundaries fall on Wednesdays and 2026-10-21 closes week 14; the three working days between are the margin above, less the half-day by which the user guide runs into 2026-10-19.

**The original finding stands as a finding, and is not deleted.** At v1.0 the window was 2026-07-15 to 2026-09-09: 8 weeks, **40 working days**, against 62.5 required and probably 68. That was a shortfall of 22.5 working days at the lower figure and 28 at the higher, a ratio of **1.56 times** the available capacity and **1.7 times** with the coverage gap closed. The scope has not shrunk and the estimates have not been revised downward. **The arithmetic balances only because the window moved.** That the original 8-week window was over by more than half, and that this was surfaced in the plan rather than absorbed into an optimistic schedule, is the record this document exists to keep. A reader comparing v1.0 and v1.1 should find the overrun reported at v1.0 and the same overrun accounted for at v1.1, not a plan that has quietly always fitted.

Two figures at v1.0 were stated as approximations and are corrected here. Completion of the 62.5-day scope falls on **2026-10-08**, not "on or about 2026-10-12"; completion of the 68-day scope falls on **2026-10-16**, not "on or about 2026-10-19". The approximations were not load-bearing at v1.0, since the point there was the size of the shortfall rather than the date. They are load-bearing now, because a date is being committed to, and they are stated precisely.

### 7.3 The Coverage Gap Is Closed, Not Carried

Section 2.4 recorded requirements that no module in the build order owned. At v1.0 this section quantified what closing the gap would cost and left it as a contingency. It is no longer a contingency. The owner's decision at §7.5 was to extend the end date and not to reduce the content of the release; requirements with no module owner do not get built, so leaving them unowned would have reduced the content of the release by omission. **The plan is therefore baselined on 68 days, not 62.5.**

| Item | Days | Owner at v1.1 |
|---|---|---|
| Compensation and Benefits — HRMS-FR-056 to HRMS-FR-062 | 4 | §6.1 module 13 |
| Notification — HRMS-FR-033, HRMS-FR-034 | 1.5 | §6.1 module 7 |
| Audit log implementation — HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015 | absorbed within M2 and M4 | No separate module; unchanged from v1.0 |
| v1.0 baseline | 62.5 | |
| **Baselined total** | **68** | |

The 62.5-day figure is retained above only to show what the closure cost. It is not an alternative baseline, and no part of this plan is scheduled against it.

### 7.4 What the Estimates Are Worth

They are one person's judgement, uncalibrated against any completed work on this project or this stack. They are not story points, and no velocity has been measured. They should be read as a lower bound, for three reasons:

1. They include no allowance for public holidays, illness, rework, or CodeRabbit review turnaround.
2. They assume every requirement is understood well enough to build. Section 8.1 shows that eight of the fifteen open TBDs bear directly on modules in the build order, and that some cannot be closed by this project at all.
3. Uncalibrated software estimates by the person who will do the work are, as a class, optimistic. There is no reason to suppose these are the exception.

Nothing in the re-baseline improves any of the three. The estimates at §7.1 are the same estimates, made by the same person, with the same absence of any completed work to calibrate against. Two of them — M7 Notification at 1.5 days and M13 Compensation and Benefits at 4 days — are new at v1.1 and are the least calibrated in the table, since they were produced during the re-baseline rather than examined at v1.0. The extension bought 30 working days and no information.

**The margin is 2 working days against 68 days of estimate that is, on the plan's own account, a lower bound. That is approximately 3%, and 3% of an uncalibrated estimate is not a margin.** It is a rounding artefact of where the week boundary happens to fall. A single module overrunning by half a day more than expected consumes a quarter of it; M14 Payroll at 8 days, the largest and most exposed estimate in the table, need be wrong by 25% to consume it four times over. §7.2 argues the reverse case at v1.0 — that every estimate would have to be wrong by more than a third for 62.5 to become 40 — and the same reasoning cuts this way now: **every estimate would have to be right, or the date moves.** Uncalibrated estimates are not, as a class, right.

**The arithmetic now balances. This does not make the date safe, and the reader should not take the one for the other.** At v1.0 the plan reported a shortfall of 22.5 days and the number carried its own warning. At v1.1 it reports a surplus of 2 days, and a surplus reads as comfort in a way a shortfall does not. It is not comfort. The v1.0 position was *this cannot be done in the time*; the v1.1 position is *this can be done in the time if nothing goes wrong, and the plan has no view on whether anything will go wrong, because it has never measured this author on this stack*. The second is a weaker claim than it looks, and 2026-10-21 should be read as the earliest date the work could finish rather than the date it will.

**The estimates would be worth more if the plan cited a source for them. It cannot, because there is none.** No historical velocity exists (§1.3), and the re-baseline does not create any. The first real evidence about these estimates arrives when M1 Authentication completes against its 2 days in week 3. That comparison is the only calibration this project will get before Payroll, and if it runs long, §7.2's arithmetic is void and the date at §5.2 should be revised at once rather than defended to 2026-10-21.

### 7.5 The Decision Taken

**At v1.0 this section recorded a verdict and three options: the confirmed scope did not fit the confirmed schedule, and 62.5 days of work, probably 68, could not be done in 40.** The verdict was correct and is not withdrawn. The options were stated for the project owner, because re-baselining the release is not a decision a planning document makes on its own authority.

**The project owner has taken Option B: the end date moves to 2026-10-21 and the content of the release is not reduced.** Decision recorded 2026-07-15. The owner separately confirmed the placement of Compensation and Benefits immediately before Payroll (§6.1). This section records the decision and the position of the options not taken; §7.2 gives the resulting arithmetic and §7.4 states what it is worth.

**Option A — reduce the content of this release. Not chosen.** It would have delivered Phase 1 and Phase 2 by 2026-09-09 and re-baselined Phase 3 (SRS §2.2: Reporting and Analytics, Compensation and Benefits, Leave Management) into a later release. The owner rejected reducing scope. Two things follow and are recorded because they constrain what may now be done quietly.

First, the option is not merely unexercised; its rejection is what closes the §2.4 coverage gap. Compensation and Benefits is a Phase 3 function and was the largest unowned item in that gap. Leaving it without a module while declining to re-baseline it out of the release would have achieved Option A's effect without Option A's SRS revision — the requirement dropped in fact and retained on paper. §2.4 and §7.3 therefore give it an owner and an estimate, and the plan is baselined at 68 days.

Second, Option A was never sufficient alone: Payroll at 8 days plus M16 to M18 at 10 days already exceeded what remained inside 2026-09-09, so it would have had to be combined with Option B in any case. The choice was never between A and B. It was whether B came with A attached, and the owner's answer is that it does not.

**Option C — lower the quality bar. Rejected, and the rejection is unaffected by the extension.** It is recorded here so that it is rejected explicitly rather than by drift. The obvious saving is the permission tests, at a meaningful fraction of every module estimate. ADR-0005 states that nothing enforces the application of a visibility rule and that an endpoint omitting it silently returns unscoped data; `docs/07-iam-rbac.md` §5 calls that a disclosure defect of the most serious kind. The permission tests are the control for that specific weakness, in a system holding salary figures, SSNIT and PAYE records, and identity documents, built by one person with no independent reviewer. Cutting them converts a schedule problem into a disclosure problem. The same reasoning bars cutting UAT, which is the only stage where the stimulus/response sequences of SRS §4 are exercised end to end.

**The extension makes Option C more tempting rather than less, and this is the reason the reasoning above is restated in full rather than referenced.** A schedule with 2 days of margin against uncalibrated estimates (§7.4) will come under pressure, and the pressure will arrive at Payroll, late, with a date already committed and the permission tests as the largest apparently discretionary line item in reach. The saving would be real and the cost would be silent, which is precisely the trade ADR-0005 says cannot be seen from inside the code. Nothing about 2026-10-21 changes the disclosure position of a system holding this data, built by one person, reviewed by nobody. **If the date cannot be met, the date moves. The tests do not.** That is the plan's position now and its position at the point where the pressure lands, and it is written here so that the later decision is measured against the earlier one.

The decision this section carried is taken; §5.2 records what became of the M5 decision deadline that gated it.

---

## 8. Risks

### 8.1 The Open TBD Register

`docs/01-srs.md` Appendix C carries fifteen TBD items. Four are resolved: TBD-002 and TBD-004 by `docs/03-tech-stack.md`, TBD-010 by `docs/07-iam-rbac.md`, and TBD-011 by the web-first decision of SRS §2.5 and §6.4. Eleven remain open.

Of those eleven, TBD-013 is inert for this release — SRS §6.4 places biometric attendance out of scope, so it blocks nothing here and is carried only for completeness. The other ten are unresolved requirements sitting beneath a plan that treats the SRS as authoritative, and each is a live schedule risk. The register below states which deliverable each blocks and when it must be resolved.

| TBD | Subject | Status | Blocks | Must resolve by |
|---|---|---|---|---|
| TBD-001 | Final organization name | **Open. Not resolvable by this project.** There is no operating organisation | Stage 9 Deployment; role grants at deployment (`docs/07-iam-rbac.md` §8); the `payroll.approve_payroll_run` grant (§4.4); TBD-003 by dependency | Before Stage 9. Not before |
| TBD-002 | Final technology stack | **Resolved** by `docs/03-tech-stack.md` | — | — |
| TBD-003 | Hosting environment | **Open by decision.** ADR-0009 defers it; the decision rule is at ADR-0009 and `docs/03-tech-stack.md` §7.2 | `docs/09-deployment-plan.md`; M18 Deployment. Does not block development — ADR-0009 makes resolution a configuration change, not a code change | See §8.3 |
| TBD-004 | Database technology | **Resolved** by `docs/03-tech-stack.md` §5.1 (PostgreSQL); ADR-0003 | — | — |
| TBD-005 | Final payroll statutory rates | **Open. Not resolvable by this project.** Requires qualified payroll or finance confirmation (SRS §2.7, §6.3) | M14 Payroll: HRMS-FR-039 to HRMS-FR-042. Also `docs/08-testing-plan.md`, which cannot state expected payroll values without them | Before M14 completes. See §8.2. **The extension does not bear on this** |
| TBD-006 | Bank transfer file format | **Open. Not resolvable by this project.** Depends on the organisation's bank (SRS §2.5), which depends on TBD-001 | M14 Payroll: HRMS-FR-046 | Before M14 completes. See §8.2. **The extension does not bear on this** |
| TBD-007 | HR approval workflows | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | `docs/05-database-schema.md` (approval records); M8 Recruitment (HRMS-FR-014); M12 Leave Management (HRMS-BR-009). Now also M7 Notification, which fires on the approval events HRMS-FR-033 and HRMS-FR-034 name | **Before M3 sign-off, 2026-07-27.** The schema must model approval whether or not the workflow content is known |
| TBD-008 | Leave policy rules | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | M12 Leave Management: HRMS-FR-067, HRMS-FR-068, and the "unless policy allows" condition on both | Before M12 begins, 2026-09-04 |
| TBD-009 | Document retention policy | **Open. Not resolvable by this project** | `docs/09-deployment-plan.md`; audit log retention per `docs/07-iam-rbac.md` §7.3; M4 document storage per ADR-0007 | Before Stage 9 |
| TBD-010 | Exact user roles and permissions | **Resolved** by `docs/07-iam-rbac.md`; ADR-0010 | — | — |
| TBD-011 | Mobile app in first release | **Resolved** by SRS §2.5 and §6.4: web-first, native application out of scope. Recorded at `docs/03-tech-stack.md` §11. ADR-0004 depends on this holding | — | — |
| TBD-012 | External job board integration | **Open** | M8 Recruitment: HRMS-FR-015. SRS §2.5 notes external posting may depend on third-party API availability | Before M8 begins, 2026-08-20 |
| TBD-013 | Biometric attendance later | **Open, and inert for this release.** SRS §6.4 places it out of scope | Nothing in this plan | Not required |
| TBD-014 | Reporting dashboard KPIs | **Open. Not resolvable by this project** | M3 Dashboard; M15 Reports: HRMS-FR-049 to HRMS-FR-054 | Before M3 Dashboard begins, 2026-08-12 |
| TBD-015 | Data migration approach | **Open. Not resolvable by this project.** SRS §2.7 assumes the organisation provides employee data | Stage 9 Deployment; Stage 11 Handover | Before Stage 9 |

### 8.2 The Structural Risk Beneath the Register

**Nine of the twelve open TBDs cannot be closed by this project as constituted.** They require an operating organisation, its HR policy, its bank, its payroll authority, or qualified legal, payroll, and finance professionals. TBD-001 records that no such organisation exists, and every one of the nine depends on it directly or through a chain.

This is not a risk that better scheduling addresses, and it will not close before 2026-10-21.

**The re-baseline does not touch any of it, and the new date must not be read as bearing on it.** The extension moved the end date by six weeks. It did not create an operating organisation, an HR policy, a bank, a payroll authority, or access to qualified legal, payroll, and finance professionals. Nine of the twelve open TBDs required one of those on 2026-07-15 and require one of those on 2026-10-21. The register at §8.1 is materially the same register it was at v1.0, with dates shifted and module numbers corrected; the only substantive change is that TBD-007 now bears on M7 Notification as well, because the notification module fires on the approval events whose workflow TBD-007 leaves undefined. That is a new consumer of an old unknown, not progress against it.

The consequence for Payroll is the sharpest, and it is not a scheduling consequence. M14 implements HRMS-FR-039 to HRMS-FR-042 — PAYE, SSNIT Tier 1, Tier 2, Tier 3 — and HRMS-FR-046, the bank transfer file. TBD-005 leaves the rates unconfirmed and TBD-006 leaves the file format unknown. **Payroll can therefore be built but cannot be signed off as correct, on any schedule, including this one.** Option B in Section 7.5 was taken and it buys time; **it does not buy statutory rates.** TBD-005 and TBD-006 made Payroll unsignable-off at v1.0 under a 2026-09-09 date and make it unsignable-off at v1.1 under a 2026-10-21 date. This is stated twice, here and at §7.5, because a re-baselined plan invites the reading that the problems it was written around have been dealt with, and these have not been. **No date this project can adopt closes them.**

What follows is a constraint on how M14 is built and on what its completion may claim. It is unchanged by the re-baseline:

- Rates are versioned configuration, never constants in code (`CONTEXT.md`; `docs/03-tech-stack.md` §5.1; SRS §2.5). The calculation engine is built against the rate-table structure, not against particular rates.
- Any rates used during development are recorded as provisional and unverified, in the repository, at the point of use. They are not represented as the rates in force.
- The bank transfer file is built behind an interface with one format implementation, which is replaced when TBD-006 closes. HRMS-FR-046 is not claimed complete until then.
- M14 completes as *calculation engine built, statutory correctness unverified*. It does not complete as *Payroll done*. SRS §6.3 requires confirmation by qualified professionals before go-live, and no test this project can write substitutes for it. **Reaching 2026-10-21 with M14 complete is not Payroll delivered, and the plan does not permit that claim.**

The same pattern applies at lower stakes to M12 under TBD-008 and to M3 and M15 under TBD-014: the mechanism is built against a documented provisional assumption, and the assumption is recorded as provisional rather than absorbed into the code as though it were a requirement.

M13 Compensation and Benefits, new at v1.1, enters this pattern rather than escaping it. It stores compensation history as dated records per HRMS-DR-010 and `CONTEXT.md`, and M14 computes over those records. Its structure is a design question the plan can answer; the rates and policies that populate it are not, and TBD-005 reaches it for the same reason it reaches Payroll.

### 8.3 Deployment Is Blocked, and Not by Effort

ADR-0009 defers the hosting target because Ghana's Data Protection Act 2012 (Act 843) position on data residency is unresolved, and because TBD-001 leaves no controller to register under section 27(1) and no counsel to advise. The decision rule at ADR-0009 requires three things before a hosting target is selected: written confirmation from qualified legal counsel, registration with the Data Protection Commission where applicable, and confirmation that the target satisfies HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035.

None of the three can be satisfied within this schedule, because all three presuppose an organisation. This was true of the 8-week schedule and is true of the 14-week one.

Therefore:

- **Stage 9 Deployment does not conclude in this project.** M18's 3 days build and exercise the containerised composition; they do not produce a production deployment. The extension does not change this: none of ADR-0009's three conditions is a matter of having more time.
- `docs/09-deployment-plan.md` is written to ADR-0009's decision rule. It documents the composition, backup topology, and TLS position *conditionally on the target*, and records TBD-003 as open. It does not select a host, and a plan that did would contradict an accepted ADR.
- No development or demonstration deployment implies a hosting commitment (ADR-0009; `docs/03-tech-stack.md` §7.2).
- No production personal data of any Ghanaian employee is placed in any environment while TBD-003 is open. There is none to place, and this is recorded so that convenience does not later supply some.

### 8.4 Other Risks

| Risk | Consequence | Response |
|---|---|---|
| Single point of failure in resourcing | Any absence stops the project entirely. There is no second person and no partial capacity | Not mitigable by planning. Recorded as an accepted condition of a solo project. It compounds every estimate in §7.1, and the 2 days of margin at §7.2 cover approximately two days of absence across 14 weeks |
| No independent reviewer | Defects the author cannot see survive to UAT, which the same author runs | Partial mitigation only; see §9 |
| Visibility rule omitted from an endpoint | Silent disclosure of employee-scoped data. ADR-0005 states nothing enforces the rule's application | Permission tests per module asserting permitted and denied paths; review treats a missing scope call as blocking (`docs/07-iam-rbac.md` §5). This is why Option C is rejected |
| Payroll task retried, producing duplicate records | Corrupt payroll with monetary consequence | Idempotent task semantics as a first-order concern of M14's design (`docs/03-tech-stack.md` §4.2; ADR-0006) |
| Documents 04–06 contradict the already-complete 07 | Rework in a schedule with 2 days of slack | Reconciliation check at each of M2, M3, M4; see §5.3 |
| The build order is revised after development starts | Capacity spent on modules a revision reorders | The §7.5 option decision is taken. What remains is the placement of M7 Notification, this plan's inference (§6.1), which `docs/04-system-architecture.md` decides at M2, 2026-07-21, and which must not slip past 2026-07-30; see §5.2 and §11 |
| The margin at §7.2 is read as slack rather than as rounding | An overrun is absorbed silently against 2 days that were never a buffer, and the first honest report of slippage arrives late | §7.4 states the margin as approximately 3% of an uncalibrated estimate. The M1 Authentication actual against its 2 days in week 3 is the first calibration point and is treated as one |
| The date is defended by cutting the permission tests when Payroll runs long | Disclosure defect per ADR-0005, converted from a schedule problem | §7.5 records the position in advance: if the date cannot be met, the date moves and the tests do not |

---

## 9. Quality Approach

Quality assurance is performed by the person who wrote the code (Section 3). This is a structural weakness, and the response is to prefer controls that do not depend on the author's judgement at the moment of review.

| Control | Mechanism | What it catches |
|---|---|---|
| Permission tests | pytest with pytest-django, per module, asserting both permitted and denied paths | The ADR-0005 weakness: an endpoint that omits its visibility rule |
| Schema-generated API contracts | drf-spectacular (`docs/03-tech-stack.md` §9) | Divergence between `docs/06-api-contracts.md` and the served API |
| Boundary validation | Zod at the API boundary in the client (`docs/03-tech-stack.md` §6.1) | Backend contract drift, surfaced as an error rather than an undefined value |
| Database constraints | PostgreSQL check and unique constraints (`docs/03-tech-stack.md` §5.1; ADR-0003) | HRMS-DR-001, HRMS-DR-002, HRMS-DR-005, HRMS-DR-006, where application defects cannot bypass them |
| Automated review | CodeRabbit on `develop` | A second reading of every change; the nearest available substitute for a reviewer |
| End-to-end tests | Playwright | The SRS §4 stimulus/response sequences |

What this does not achieve: none of it catches a misunderstood requirement. The author reads the SRS, builds to their reading, tests against their reading, and accepts at UAT against the same reading. Where the requirement is ambiguous, the misunderstanding survives every control above. Section 8.1's TBD register is the partial defence — an ambiguity named as a TBD is at least visible — but it is not a complete one, and the SRS's ambiguities beyond Appendix C are not enumerated anywhere.

`docs/08-testing-plan.md` details the strategy. This section states only its limit.

---

## 10. Change Control

The SRS is authoritative. This plan does not amend it and cannot.

- A change to *what the system does* is an SRS revision. This includes anything at SRS §6.4, and would have included the re-baselining contemplated by Option A in Section 7.5, which was not chosen. **The v1.1 re-baseline is a change to *when work happens* and to nothing else.** No requirement is added, removed, or deferred by it; §2.4 gives owners to requirements the SRS already carried, and no SRS revision is required or requested.
- A change to *how the system is built* is an ADR. Where a change contradicts an accepted ADR, the contradiction is surfaced and the ADR is superseded by a new record, not silently overridden.
- A change to *when work happens* is a revision of this document, recorded in the Revision History.
- Work is tracked as GitHub issues per `docs/agents/issue-tracker.md`.

Where a document and the SRS disagree, the SRS governs and the document is wrong.

---

## 11. Open Questions

Recorded because they are unresolved, not because they are minor. Each names what would resolve it.

| # | Question | Resolved by |
|---|---|---|
| 1 | **Resolved at v1.1.** Which module owns HRMS-FR-056 to HRMS-FR-062? The build order had no Compensation and Benefits module, yet `docs/07-iam-rbac.md` §4.2 already assigned permissions for those requirements across five roles | Resolved. §6.1 module 13, immediately before Payroll, **confirmed by the project owner 2026-07-15** on the dependency reasoning at §6.1. `docs/04-system-architecture.md` records the assignment at M2; it does not reopen the placement |
| 2 | **Where does Notification sit in the build order?** §6.1 places it at module 7, before M8 Recruitment, because Recruitment is the first module with an approval flow (HRMS-FR-014) and HRMS-FR-033 and HRMS-FR-034 are the notification of a pending approval and of the decision on it. **This is the plan's inference and is not confirmed.** The owner confirmed the extension, confirmed that scope is not cut, and confirmed the Compensation and Benefits placement; he did not speak to this one | The project owner, with `docs/04-system-architecture.md` at M2, 2026-07-21, and not later than 2026-07-30 (§5.2). Every week from 6 onward in §6.2 depends on the answer, and a later placement returns HRMS-FR-033 and HRMS-FR-034 to consumers already built |
| 3 | Is audit logging a module, or cross-cutting infrastructure consumed by every module? `docs/07-iam-rbac.md` §7.3 designs it; nothing implements it. §7.3 of this plan absorbs it within M2 and M4 and gives it no separate estimate, which presumes the second answer | `docs/04-system-architecture.md`, at M2. If it is a module, it carries an estimate that §7.1 does not include and the 68-day figure is low |
| 4 | What is the working calendar? The repository defines no public holiday schedule, and every estimate in §7.1 assumes five uninterrupted days per week | The project owner. Bears directly on §7.2, and more sharply at v1.1 than at v1.0: the schedule now runs to 2026-10-21 with 2 days of margin, so a single public holiday inside the window consumes half of it |
| 5 | **Retired at v1.1.** Whether Option A required a re-baselined SRS phase boundary or a second release with its own SRS | Retired. Option A was not chosen (§7.5); the question it asked does not arise. Recorded rather than deleted so that the v1.0 numbering can be followed |
| 6 | What does M17 UAT mean with no users? UAT is acceptance by the people who will use the system. TBD-001 leaves no organisation, so the sole participant is the author, who wrote the code and the SRS | The project owner. If it is self-verification against SRS §4, it should be named that, and `docs/08-testing-plan.md` should say so rather than call it acceptance |
| 7 | What does Stage 11 Handover mean with no recipient? SRS §2.7 assumes HR staff are trained before go-live; there are none | The project owner. Bears on `docs/10-user-guide.md`, whose nine guides at SRS §2.6 currently have no reader |
| 8 | Is HRMS-NFR-024 — multi-factor authentication for administrators and payroll users — in this release? It is a *should*, it is unestimated in §7.1, and no module in the build order carries it | The project owner, with `docs/04-system-architecture.md` at M2. The v1.1 closure of §2.4 does not reach it: HRMS-NFR-024 is unowned for the same reason it was unowned at v1.0, and if it is in the release the 68-day figure is low by its estimate |

---

## 12. Traceability

| Plan element | Serves |
|---|---|
| §2.1 scope baseline | HRMS-FR-001 to HRMS-FR-071, HRMS-NFR-001 to HRMS-NFR-036, HRMS-BR-001 to HRMS-BR-015, HRMS-DR-001 to HRMS-DR-010 |
| §2.2 exclusions | SRS §6.4 |
| §2.3 deferral of HRMS-FR-055 | SRS §4.5, which defers it by its own terms |
| §4 stage sequence | SRS §1.4, §2.1 phased development |
| §5.1 document set | SRS §3.3, which records the stack as TBD to be confirmed in technical architecture planning |
| §5.3 out-of-order reconciliation | `docs/07-iam-rbac.md` §3, §4.2, §4.4, §5; ADR-0005; ADR-0010 |
| §6.1 build order | SRS §2.2 phases; ADR-0001 module boundaries |
| §6.1 module 7 Notification | HRMS-FR-033, HRMS-FR-034; SRS §3.4 in-app and email channels |
| §6.1 module 13 Compensation and Benefits | HRMS-FR-056 to HRMS-FR-062; SRS §4.6; HRMS-DR-010; `CONTEXT.md` compensation record; `docs/07-iam-rbac.md` §4.2 |
| §7.5 Option C rejection | ADR-0005; `docs/07-iam-rbac.md` §5; HRMS-NFR-016 to HRMS-NFR-019 |
| §8.1 TBD register | SRS Appendix C, TBD-001 to TBD-015 |
| §8.2 payroll constraint | SRS §2.5, §6.3; ADR-0003; ADR-0006; HRMS-FR-039 to HRMS-FR-042, HRMS-FR-046 |
| §8.3 deployment block | ADR-0009; SRS §2.4, §6.3; HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035 |
| §9 quality controls | ADR-0003, ADR-0005; HRMS-DR-001 to HRMS-DR-010; HRMS-NFR-028, HRMS-NFR-029 |
