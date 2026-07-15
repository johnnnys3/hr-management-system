# Project Plan

**Human Resource Management System**

| | |
|---|---|
| Version | 1.0 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-15 |
| Status | Approved |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-15 | Initial project plan. Authored after `docs/03-tech-stack.md` and `docs/07-iam-rbac.md`; records the sequence, effort, and risk position for the remaining work | 1.0 |

---

## 1. Introduction

### 1.1 Purpose

This document plans the construction of the Human Resource Management System: what is delivered, in what order, by when, at what effort, and against what risks.

It does not restate requirements, which are held in the Software Requirements Specification, and it does not select technology, which is settled in `docs/03-tech-stack.md` and the architecture decision records. Where this document and the SRS disagree, the SRS governs.

This document is being authored out of sequence. It is deliverable 02; deliverable 03 and deliverable 07 were completed before it. Section 5.3 records that position rather than concealing it.

**Section 7 is the operative section of this plan.** It records that the confirmed scope does not fit the confirmed schedule, shows the arithmetic, and states the decision the project owner must take. A reader with time for one section should read that one.

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
| `docs/01-srs.md` | Software Requirements Specification v1.0. Authoritative |
| `docs/01-srs.pdf` | Rendering of the SRS at v1.0, for distribution. Not authoritative |
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

### 2.4 Requirements Without a Module

The confirmed module build order in Section 6.1 has no module that owns the following. This is recorded as a coverage gap, not resolved here, because assigning requirements to modules is an architecture decision belonging to `docs/04-system-architecture.md`.

| Requirements | Subject | Note |
|---|---|---|
| HRMS-FR-056 to HRMS-FR-062 | Salary structures, pay grades, bonus cycles, allowances, benefits enrolment, compensation history | SRS §4.6, a Phase 3 function. No module in the build order owns it. `docs/07-iam-rbac.md` §4.2 already assigns permissions for these requirements, so the design assumes an implementation surface the build order does not name |
| HRMS-FR-033, HRMS-FR-034 | Approval and decision notification, in-app and email (SRS §3.4) | Cross-cutting. Consumed by Recruitment, Onboarding, Leave, and Payroll. No module owns it |
| HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015 | Audit log | Cross-cutting. Design exists at `docs/07-iam-rbac.md` §7.3; no module owns the implementation |

Section 7.3 quantifies what closing this gap costs. Section 11 carries it as an open question.

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
| M1 | `docs/02-project-plan.md` | 2026-07-16 | This document |
| M2 | `docs/04-system-architecture.md` | 2026-07-21 | Within the 8-week window |
| M3 | `docs/05-database-schema.md` | 2026-07-27 | Within the 8-week window |
| M4 | `docs/06-api-contracts.md` | 2026-07-29 | Within the 8-week window |
| M5 | `docs/08-testing-plan.md` | 2026-07-30 | Within the 8-week window |
| M6 | `docs/09-deployment-plan.md` | **Not schedulable within the window** | See §7.2 and §8.3 |
| M7 | `docs/10-user-guide.md` | **Not schedulable within the window** | See §7.2 |

M6 and M7 carry no date because the arithmetic in Section 7 does not produce one inside 2026-09-09. A date is assigned when the owner takes the decision described in Section 7.5. M6 additionally cannot be *completed* on any schedule while TBD-003 is open; Section 8.3 explains.

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
| 7 | Recruitment | HRMS-FR-013 to HRMS-FR-021 |
| 8 | Onboarding | HRMS-FR-022 to HRMS-FR-024, HRMS-BR-013 |
| 9 | Employee Self-Service | HRMS-FR-025 to HRMS-FR-029, HRMS-FR-044, HRMS-NFR-017, HRMS-BR-006 |
| 10 | Manager Self-Service | HRMS-FR-030 to HRMS-FR-032, HRMS-NFR-018, HRMS-BR-007 |
| 11 | Leave Management | HRMS-FR-063 to HRMS-FR-071, HRMS-BR-009 to HRMS-BR-011, HRMS-DR-006 |
| 12 | Payroll | HRMS-FR-035 to HRMS-FR-048, HRMS-BR-008, HRMS-DR-005, HRMS-DR-009, HRMS-NFR-005, HRMS-NFR-009, HRMS-NFR-010 |
| 13 | Reports | HRMS-FR-049 to HRMS-FR-054 |
| 14 | Testing | HRMS-NFR-028, HRMS-NFR-029; `docs/08-testing-plan.md` |
| 15 | UAT | SRS §4 acceptance against stimulus/response sequences |
| 16 | Deployment | HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035; ADR-0009 |

A module is complete when its models, service layer, API endpoints, visibility rule, permission tests, and client interface are done and its tests pass. A module without permission tests asserting both the permitted and the denied path is not complete (ADR-0005; `docs/07-iam-rbac.md` §5).

### 6.2 Week-by-Week Allocation

Week boundaries fall on Wednesdays. Each week carries five working days.

| Week | Ends | Allocation |
|---|---|---|
| 1 | 2026-07-22 | `docs/02-project-plan.md` (1d); Environment Setup (2d); `docs/04-system-architecture.md` (2d) |
| 2 | 2026-07-29 | `docs/05-database-schema.md` (2d); `docs/06-api-contracts.md` (2d); `docs/08-testing-plan.md` (1d of 2) |
| 3 | 2026-08-05 | `docs/08-testing-plan.md` (1d); M1 Authentication (2d); M2 RBAC/IAM (2d of 3) |
| 4 | 2026-08-12 | M2 RBAC/IAM (1d); M3 Dashboard (1.5d); M4 Employee Management (2.5d of 4) |
| 5 | 2026-08-19 | M4 Employee Management (1.5d); M5 Departments (1d); M6 Reporting Structure (1.5d); M7 Recruitment (1d of 4) |
| 6 | 2026-08-26 | M7 Recruitment (3d); M8 Onboarding (2d) |
| 7 | 2026-09-02 | M9 Employee Self-Service (2.5d); M10 Manager Self-Service (2d); M11 Leave Management (0.5d of 4) |
| 8 | 2026-09-09 | M11 Leave Management (3.5d); M12 Payroll (1.5d of 8) |

**At 2026-09-09, the project is one and a half days into Payroll.** Modules 12 to 16, `docs/09-deployment-plan.md`, and `docs/10-user-guide.md` lie outside the window.

The table above is the honest consequence of the estimates in Section 7.1 laid against the confirmed order. It is not compressed to reach the end date. `docs/08-testing-plan.md` precedes development deliberately: tests are written against a plan, and writing the plan after the code it judges would defeat the only independent control this project has (Section 3).

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
| M7 Recruitment | 4 | 9 FRs, requisition approval, interview scheduling, offer generation |
| M8 Onboarding | 2 | |
| M9 Employee Self-Service | 2.5 | |
| M10 Manager Self-Service | 2 | |
| M11 Leave Management | 4 | 9 FRs, balance arithmetic, policy enforcement, calendar |
| M12 Payroll | 8 | 14 FRs; PAYE, SSNIT Tier 1, Tier 2, Tier 3; versioned rate tables; atomic finalisation; idempotent Celery tasks; payslips; bank transfer file |
| M13 Reports | 3 | |
| M14 Testing | 4 | Hardening beyond per-module tests |
| M15 UAT | 3 | |
| M16 Deployment | 3 | |
| `docs/09-deployment-plan.md` | 1.5 | |
| `docs/10-user-guide.md` | 1.5 | Nine guides at SRS §2.6, less the optional training videos |
| **Total** | **62.5** | |

### 7.2 The Arithmetic

- Available: 2026-07-15 to 2026-09-09 is 8 weeks at 5 working days for one person = **40 working days**.
- Required: **62.5 working days**.
- Shortfall: **22.5 working days**, approximately 4.5 further weeks.
- Ratio: **1.56 times the available capacity.**

Carried forward at the same rate with no slippage, completion falls on or about **2026-10-12**.

### 7.3 With the Coverage Gap Closed

Section 2.4 records requirements that no module in the build order owns. If they are given homes, the estimate grows:

| Item | Days |
|---|---|
| Compensation and Benefits — HRMS-FR-056 to HRMS-FR-062 | 4 |
| Notification — HRMS-FR-033, HRMS-FR-034 | 1.5 |
| Audit log implementation — HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022 | absorbed within M2 and M4 above |
| **Revised total** | **68** |

At 68 days the ratio is **1.7 times** the available capacity, the shortfall is **28 working days**, and completion falls on or about **2026-10-19**.

### 7.4 What the Estimates Are Worth

They are one person's judgement, uncalibrated against any completed work on this project or this stack. They are not story points, and no velocity has been measured. They should be read as a lower bound, for three reasons:

1. They include no allowance for public holidays, illness, rework, or CodeRabbit review turnaround.
2. They assume every requirement is understood well enough to build. Section 8.1 shows that eight of the fifteen open TBDs bear directly on modules in the build order, and that some cannot be closed by this project at all.
3. Uncalibrated software estimates by the person who will do the work are, as a class, optimistic. There is no reason to suppose these are the exception.

**The conclusion does not depend on the precision of the estimates.** Every module estimate would have to be wrong by more than a third, in the same direction, for 62.5 days to become 40.

### 7.5 Verdict and Options

**The confirmed scope does not fit the confirmed schedule.** 62.5 days of work, and probably 68, cannot be done in 40. This is recorded here rather than absorbed into an optimistic schedule, because a schedule that hides a 56% overrun fails at the only thing a plan is for.

Three options exist. They are stated for the project owner's decision; this plan does not take it, because re-baselining the release content is not a decision a planning document makes on its own authority.

**Option A — reduce the content of this release.** Deliver Phase 1 and Phase 2 by 2026-09-09 and re-baseline Phase 3 (SRS §2.2: Reporting and Analytics, Compensation and Benefits, Leave Management) into a later release. This does not remove anything from the SRS and does not touch SRS §6.4; it changes which release satisfies which phase, which is what SRS §1.4 and §2.1 already contemplate in describing phased development. It requires an SRS revision to record the re-baselined phase boundaries. Even under this option, Payroll's estimate of 8 days plus M14 to M16 at 10 days exceeds what remains, so Option A alone does not close the gap and must be combined with Option B.

**Option B — extend the end date.** Move the end date to on or about 2026-10-12 for the current scope, or 2026-10-19 with the Section 2.4 gap closed. Both figures assume no slippage, which Section 7.4 argues against. The plan's own recommendation, if asked for one, is that this is the only option that preserves both the SRS and the quality bar.

**Option C — lower the quality bar.** Rejected, and recorded here so that it is rejected explicitly rather than by drift. The obvious saving is the permission tests, at a meaningful fraction of every module estimate. ADR-0005 states that nothing enforces the application of a visibility rule and that an endpoint omitting it silently returns unscoped data; `docs/07-iam-rbac.md` §5 calls that a disclosure defect of the most serious kind. The permission tests are the control for that specific weakness, in a system holding salary figures, SSNIT and PAYE records, and identity documents, built by one person with no independent reviewer. Cutting them converts a schedule problem into a disclosure problem. The same reasoning bars cutting UAT, which is the only stage where the stimulus/response sequences of SRS §4 are exercised end to end.

**The decision is due at the M5 sign-off, 2026-07-30**, before development begins. Deferring it past that point spends capacity on a build order that a re-baseline may reorder.

---

## 8. Risks

### 8.1 The Open TBD Register

`docs/01-srs.md` Appendix C carries fifteen TBD items. Three are resolved. The rest are unresolved requirements sitting beneath a plan that treats the SRS as authoritative, and each is a live schedule risk. The register below states which deliverable each blocks and when it must be resolved.

| TBD | Subject | Status | Blocks | Must resolve by |
|---|---|---|---|---|
| TBD-001 | Final organization name | **Open. Not resolvable by this project.** There is no operating organisation | Stage 9 Deployment; role grants at deployment (`docs/07-iam-rbac.md` §8); the `payroll.approve_payroll_run` grant (§4.4); TBD-003 by dependency | Before Stage 9. Not before |
| TBD-002 | Final technology stack | **Resolved** by `docs/03-tech-stack.md` | — | — |
| TBD-003 | Hosting environment | **Open by decision.** ADR-0009 defers it; the decision rule is at ADR-0009 and `docs/03-tech-stack.md` §7.2 | `docs/09-deployment-plan.md`; M16 Deployment. Does not block development — ADR-0009 makes resolution a configuration change, not a code change | See §8.3 |
| TBD-004 | Database technology | **Resolved** by `docs/03-tech-stack.md` §5.1 (PostgreSQL); ADR-0003 | — | — |
| TBD-005 | Final payroll statutory rates | **Open. Not resolvable by this project.** Requires qualified payroll or finance confirmation (SRS §2.7, §6.3) | M12 Payroll: HRMS-FR-039 to HRMS-FR-042. Also `docs/08-testing-plan.md`, which cannot state expected payroll values without them | Before M12 completes. See §8.2 |
| TBD-006 | Bank transfer file format | **Open. Not resolvable by this project.** Depends on the organisation's bank (SRS §2.5), which depends on TBD-001 | M12 Payroll: HRMS-FR-046 | Before M12 completes. See §8.2 |
| TBD-007 | HR approval workflows | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | `docs/05-database-schema.md` (approval records); M7 Recruitment (HRMS-FR-014); M11 Leave Management (HRMS-BR-009) | **Before M3 sign-off, 2026-07-27.** The schema must model approval whether or not the workflow content is known |
| TBD-008 | Leave policy rules | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | M11 Leave Management: HRMS-FR-067, HRMS-FR-068, and the "unless policy allows" condition on both | Before M11 begins, 2026-09-02 |
| TBD-009 | Document retention policy | **Open. Not resolvable by this project** | `docs/09-deployment-plan.md`; audit log retention per `docs/07-iam-rbac.md` §7.3; M4 document storage per ADR-0007 | Before Stage 9 |
| TBD-010 | Exact user roles and permissions | **Resolved** by `docs/07-iam-rbac.md`; ADR-0010 | — | — |
| TBD-011 | Mobile app in first release | **Resolved** by SRS §2.5 and §6.4: web-first, native application out of scope. Recorded at `docs/03-tech-stack.md` §11. ADR-0004 depends on this holding | — | — |
| TBD-012 | External job board integration | **Open** | M7 Recruitment: HRMS-FR-015. SRS §2.5 notes external posting may depend on third-party API availability | Before M7 begins, 2026-08-19 |
| TBD-013 | Biometric attendance later | **Open, and inert for this release.** SRS §6.4 places it out of scope | Nothing in this plan | Not required |
| TBD-014 | Reporting dashboard KPIs | **Open. Not resolvable by this project** | M3 Dashboard; M13 Reports: HRMS-FR-049 to HRMS-FR-054 | Before M3 Dashboard begins, 2026-08-12 |
| TBD-015 | Data migration approach | **Open. Not resolvable by this project.** SRS §2.7 assumes the organisation provides employee data | Stage 9 Deployment; Stage 11 Handover | Before Stage 9 |

### 8.2 The Structural Risk Beneath the Register

**Nine of the twelve open TBDs cannot be closed by this project as constituted.** They require an operating organisation, its HR policy, its bank, its payroll authority, or qualified legal, payroll, and finance professionals. TBD-001 records that no such organisation exists, and every one of the nine depends on it directly or through a chain.

This is not a risk that better scheduling addresses, and it will not close before 2026-09-09.

The consequence for Payroll is the sharpest, and it is not a scheduling consequence. M12 implements HRMS-FR-039 to HRMS-FR-042 — PAYE, SSNIT Tier 1, Tier 2, Tier 3 — and HRMS-FR-046, the bank transfer file. TBD-005 leaves the rates unconfirmed and TBD-006 leaves the file format unknown. **Payroll can therefore be built but cannot be signed off as correct, on any schedule, including an extended one.** Option B in Section 7.5 buys time; it does not buy statutory rates.

What follows is a constraint on how M12 is built and on what its completion may claim:

- Rates are versioned configuration, never constants in code (`CONTEXT.md`; `docs/03-tech-stack.md` §5.1; SRS §2.5). The calculation engine is built against the rate-table structure, not against particular rates.
- Any rates used during development are recorded as provisional and unverified, in the repository, at the point of use. They are not represented as the rates in force.
- The bank transfer file is built behind an interface with one format implementation, which is replaced when TBD-006 closes. HRMS-FR-046 is not claimed complete until then.
- M12 completes as *calculation engine built, statutory correctness unverified*. It does not complete as *Payroll done*. SRS §6.3 requires confirmation by qualified professionals before go-live, and no test this project can write substitutes for it.

The same pattern applies at lower stakes to M11 under TBD-008 and to M3 and M13 under TBD-014: the mechanism is built against a documented provisional assumption, and the assumption is recorded as provisional rather than absorbed into the code as though it were a requirement.

### 8.3 Deployment Is Blocked, and Not by Effort

ADR-0009 defers the hosting target because Ghana's Data Protection Act 2012 (Act 843) position on data residency is unresolved, and because TBD-001 leaves no controller to register under section 27(1) and no counsel to advise. The decision rule at ADR-0009 requires three things before a hosting target is selected: written confirmation from qualified legal counsel, registration with the Data Protection Commission where applicable, and confirmation that the target satisfies HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035.

None of the three can be satisfied within this schedule, because all three presuppose an organisation.

Therefore:

- **Stage 9 Deployment does not conclude in this project.** M16's 3 days build and exercise the containerised composition; they do not produce a production deployment.
- `docs/09-deployment-plan.md` is written to ADR-0009's decision rule. It documents the composition, backup topology, and TLS position *conditionally on the target*, and records TBD-003 as open. It does not select a host, and a plan that did would contradict an accepted ADR.
- No development or demonstration deployment implies a hosting commitment (ADR-0009; `docs/03-tech-stack.md` §7.2).
- No production personal data of any Ghanaian employee is placed in any environment while TBD-003 is open. There is none to place, and this is recorded so that convenience does not later supply some.

### 8.4 Other Risks

| Risk | Consequence | Response |
|---|---|---|
| Single point of failure in resourcing | Any absence stops the project entirely. There is no second person and no partial capacity | Not mitigable by planning. Recorded as an accepted condition of a solo project. It compounds every estimate in §7.1 |
| No independent reviewer | Defects the author cannot see survive to UAT, which the same author runs | Partial mitigation only; see §9 |
| Visibility rule omitted from an endpoint | Silent disclosure of employee-scoped data. ADR-0005 states nothing enforces the rule's application | Permission tests per module asserting permitted and denied paths; review treats a missing scope call as blocking (`docs/07-iam-rbac.md` §5). This is why Option C is rejected |
| Payroll task retried, producing duplicate records | Corrupt payroll with monetary consequence | Idempotent task semantics as a first-order concern of M12's design (`docs/03-tech-stack.md` §4.2; ADR-0006) |
| Documents 04–06 contradict the already-complete 07 | Rework in a schedule with no slack | Reconciliation check at each of M2, M3, M4; see §5.3 |
| The build order is re-baselined after development starts | Capacity spent on modules a re-baseline reorders | The §7.5 decision is due at M5, 2026-07-30, before development begins |

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

- A change to *what the system does* is an SRS revision. This includes anything at SRS §6.4, and includes the re-baselining contemplated by Option A in Section 7.5.
- A change to *how the system is built* is an ADR. Where a change contradicts an accepted ADR, the contradiction is surfaced and the ADR is superseded by a new record, not silently overridden.
- A change to *when work happens* is a revision of this document, recorded in the Revision History.
- Work is tracked as GitHub issues per `docs/agents/issue-tracker.md`.

Where a document and the SRS disagree, the SRS governs and the document is wrong. Where `docs/01-srs.md` and `docs/01-srs.pdf` disagree, the Markdown governs.

---

## 11. Open Questions

Recorded because they are unresolved, not because they are minor. Each names what would resolve it.

| # | Question | Resolved by |
|---|---|---|
| 1 | Which module owns HRMS-FR-056 to HRMS-FR-062? The build order has no Compensation and Benefits module, yet `docs/07-iam-rbac.md` §4.2 already assigns permissions for those requirements across five roles | `docs/04-system-architecture.md`, at M2, 2026-07-21. Either a module is added to the build order or the requirements are assigned to existing modules |
| 2 | Which module owns notification, HRMS-FR-033 and HRMS-FR-034, and the in-app and email channels of SRS §3.4? | `docs/04-system-architecture.md`, at M2 |
| 3 | Is audit logging a module, or cross-cutting infrastructure consumed by every module? `docs/07-iam-rbac.md` §7.3 designs it; nothing implements it | `docs/04-system-architecture.md`, at M2 |
| 4 | What is the working calendar? The repository defines no public holiday schedule, and every estimate in §7.1 assumes five uninterrupted days per week | The project owner. Bears directly on §7.2 |
| 5 | Does Option A in §7.5 require a re-baselined SRS phase boundary, or a second release with its own SRS? SRS §1.4 describes three phases of one product and does not describe releases | The project owner, with the SRS revision, by 2026-07-30 |
| 6 | What does M15 UAT mean with no users? UAT is acceptance by the people who will use the system. TBD-001 leaves no organisation, so the sole participant is the author, who wrote the code and the SRS | The project owner. If it is self-verification against SRS §4, it should be named that, and `docs/08-testing-plan.md` should say so rather than call it acceptance |
| 7 | What does Stage 11 Handover mean with no recipient? SRS §2.7 assumes HR staff are trained before go-live; there are none | The project owner. Bears on `docs/10-user-guide.md`, whose nine guides at SRS §2.6 currently have no reader |
| 8 | Is HRMS-NFR-024 — multi-factor authentication for administrators and payroll users — in this release? It is a *should*, it is unestimated in §7.1, and no module in the build order carries it | The project owner, with `docs/04-system-architecture.md` at M2 |

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
| §7.5 Option C rejection | ADR-0005; `docs/07-iam-rbac.md` §5; HRMS-NFR-016 to HRMS-NFR-019 |
| §8.1 TBD register | SRS Appendix C, TBD-001 to TBD-015 |
| §8.2 payroll constraint | SRS §2.5, §6.3; ADR-0003; ADR-0006; HRMS-FR-039 to HRMS-FR-042, HRMS-FR-046 |
| §8.3 deployment block | ADR-0009; SRS §2.4, §6.3; HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035 |
| §9 quality controls | ADR-0003, ADR-0005; HRMS-DR-001 to HRMS-DR-010; HRMS-NFR-028, HRMS-NFR-029 |
