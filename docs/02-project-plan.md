# Project Plan

**Human Resource Management System**

| | |
|---|---|
| Version | 1.2 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-15 |
| Status | Approved |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-15 | Initial project plan. Authored after `docs/03-tech-stack.md` and `docs/07-iam-rbac.md`; records the sequence, effort, and risk position for the remaining work | 1.0 |
| John Kessie | 2026-07-15 | Schedule re-baselined to 2026-10-21 on the project owner's decision to take Option B of §7.5 and extend the end date rather than reduce the content of the release. Because scope is not reduced, the §2.4 coverage gap is closed rather than carried: Compensation and Benefits and Notification enter the build order, and the plan is baselined on the 68-day figure of §7.3 rather than the 62.5-day figure of §7.1. §§2.4, 5.2, 6.1, 6.2, 7, 8.2, 11 revised accordingly | 1.1 |
| John Kessie | 2026-07-15 | Re-baselined to 2026-11-03 against `docs/01-srs.md` v1.1, and the week convention pinned. Two changes, of different kinds. **First, a defect fix.** v1.1 held that week boundaries fall on Wednesdays and that each week carries five working days; the two are inconsistent, and the unpinned convention produced dates that contradicted each other — §7's 2026-10-16 against §6.2's user guide running into 2026-10-19, and §5.2's M1 of 2026-07-16 against its M2 of 2026-07-21. New §6.2 pins a week as Wednesday to Tuesday inclusive, week *N* ending on working day 5*N* from 2026-07-15, and every date in the document is recomputed from that rule alone. Week 1 ends 2026-07-21. M1, M3, M4, and M5 move earlier; M2 is unchanged at 2026-07-21, which is what working day 5 yields under either reading; no work is resequenced. **Second, a re-baseline.** SRS v1.1 promotes HRMS-NFR-024 to a *shall*, making multi-factor authentication mandatory for administrators and payroll users with the second factor outside the control of the roles that administer accounts and credentials. §11 question 8 had carried it as unowned and unestimated, and is resolved by the requirement changing rather than by any decision of this plan. §6.1 gives it owners in modules 1 and 2; §7.3 estimates it at 10 days, taking the baseline from 68 to 78 and the window to 16 weeks and 80 working days. Margin remains 2 days and is therefore thinner: 2.6% against v1.1's 2.9%. §8.1 carries TBD-016 and TBD-017, new at SRS v1.1, taking the register to seventeen items, four resolved and thirteen open, and corrects §8.2's "nine of the twelve", which matched neither its own register nor the true count. The extension to 2026-11-03 was put to the project owner as the plan's inference rather than his decision, since he had named 2026-10-21 before HRMS-NFR-024 became mandatory; **he confirmed 2026-11-03 on 2026-07-15**, and §11 question 9 records that sequence. **He separately confirmed the 78-day baseline itself on 2026-07-15**, recorded at §7.3; confirming the figure accepts it as the one the plan is scheduled against and is not a finding that it is correct, and §7.4 stands in full. No scope is added, reduced, or deferred by this revision, and no SRS revision is requested. §§1.1, 2.1, 2.3, 2.4, 5.2, 6, 7, 8, 11, 12 revised accordingly | 1.2 |
| John Kessie | 2026-07-15 | Re-baselined to 2026-11-10. **§11 question 3 is resolved, and resolving it cost 3 days and moved the date a third time.** The question asked whether audit logging is a module or cross-cutting infrastructure. **Both answers were wrong, and that is the finding.** Audit splits: an owned surface — the audit log entity of SRS §6.1, an append-only writer, the System Administrator read surface the `docs/07-iam-rbac.md` §4.2 matrix grants, and the `INSERT`/`SELECT`-only database grant of that document's §7.3 — and cross-cutting emission at each consumer. The absorption recorded at v1.0 was defensible for emission only, and silently assumed nobody built the other half. §6.1 gives the owned half **module 1, before Authentication**, on this plan's own reasoning for Notification at v1.1: a provider precedes its first consumer, and `CONTEXT.md` makes login attempts an audited action, so M1 Authentication was the first consumer of a thing §7.3 placed two modules after it. All eighteen modules renumber by one. §7.1 costs it at 3 days, taking the baseline from 78 to 81 and the window to 17 weeks and 85 working days; margin is 4 days, 4.9%, and §7.4's reading of what a margin against uncalibrated estimate is worth stands in full. **The project owner confirmed the placement, the 3-day estimate, the single-store reading, and 2026-11-10 on 2026-07-15**, and resolved the question on the §11 question 1 precedent: `docs/04-system-architecture.md` records the assignment at M2 and does not reopen it. **His confirmation of 2026-11-03 and of the 78-day baseline, both given on 2026-07-15 and recorded at v1.2, are superseded within the same day** — §11 question 9 says so rather than quietly restating the figures. One term is sharpened rather than left to be re-derived: HRMS-FR-010's "audit history" is not a second store but a filtered read of the audit log where the target is an employee record, so M5 Employee Management stays at 4 days and `CONTEXT.md` now says so. No scope is added, reduced, or deferred by this revision, and no SRS revision is requested. §§2.4, 5.2, 6.1, 6.3, 7, 8, 11, 12 revised accordingly | 1.3 |

---

## 1. Introduction

### 1.1 Purpose

This document plans the construction of the Human Resource Management System: what is delivered, in what order, by when, at what effort, and against what risks.

It does not restate requirements, which are held in the Software Requirements Specification, and it does not select technology, which is settled in `docs/03-tech-stack.md` and the architecture decision records. Where this document and the SRS disagree, the SRS governs.

This document is being authored out of sequence. It is deliverable 02; deliverable 03 and deliverable 07 were completed before it. Section 5.3 records that position rather than concealing it.

**Section 7 is the operative section of this plan.** At v1.0 it recorded that the confirmed scope did not fit the confirmed schedule, showed the arithmetic, and stated the decision the project owner had to take. That decision has been taken: the end date moves and the content of the release is not reduced. The date is now 2026-11-10, having been 2026-09-09 at v1.0, 2026-10-21 at v1.1, and 2026-11-03 at v1.2. Section 7 records the arithmetic that produced it, the margin it leaves, the original finding — retained because a plan that deletes the overrun it once reported cannot be checked — and **the fact that this is the third time the date has moved, all three times before any code was written.** A reader with time for one section should read that one, and §7.4 in particular: the third move was not caused by anything outside this plan.

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

The requirement set of `docs/01-srs.md` v1.1: 71 functional requirements (HRMS-FR-001 to HRMS-FR-071), 36 nonfunctional requirements (HRMS-NFR-001 to HRMS-NFR-036), 15 business rules (HRMS-BR-001 to HRMS-BR-015), and 10 data validation rules (HRMS-DR-001 to HRMS-DR-010).

SRS v1.1 adds and removes no requirement, and the counts are those of v1.0. What it changes is modality and testability: HRMS-NFR-024 becomes a *shall*, which §7.3 costs; HRMS-NFR-001 to HRMS-NFR-006 become measurable, which §8.1 costs in unknowns rather than days. **The scope baseline is unchanged and this plan does not reduce or extend it.**

### 2.2 What Is Out

The items listed at SRS §6.4, reproduced in `CONTEXT.md` under "Scope boundary". A request touching any of them is a scope change requiring SRS revision. This plan makes no such request.

### 2.3 Deferred by the SRS Itself

HRMS-FR-055 requires predictive attrition analytics "in later versions where enough historical data exists". The condition is not met: the system holds no historical HR data and, per TBD-001, has no operating organisation to supply any. The requirement is therefore not built in this release. This is the SRS's own deferral, not a reduction made by this plan.

**HRMS-FR-051 joins it at SRS v1.1.** Training completion reports were deferred on the same pattern as HRMS-FR-055, the training data their condition presupposed being excluded by SRS §6.4. The deferral is the SRS's, made under its own change control, and is recorded here because §2.1 baselines this plan on v1.1 and a reader must be able to see which of the 71 functional requirements this release does not build. It changes no estimate at §7.1: M16 Reports was estimated against HRMS-FR-049 to HRMS-FR-054 and is unaffected, and the plan does not reduce the estimate to claim a saving from a requirement it never costed.

### 2.4 Requirements Without a Module, and How the Gap Was Closed

At v1.0 the module build order had no module that owned the requirements below. The gap was recorded rather than resolved, because assigning requirements to modules is an architecture decision belonging to `docs/04-system-architecture.md`.

The gap is now closed. It is closed because the owner's decision at §7.5 was to extend the end date and not to reduce the content of the release, and requirements with no module owner are requirements that do not get built. Carrying the gap forward under a decision that scope is not cut would have cut scope silently, which is the one outcome the decision excludes. The build order at §6.1 therefore names an owner for each row, and §7 was baselined at v1.1 on the resulting 68-day figure rather than the 62.5-day figure that omitted them.

**A fourth row would have been added at v1.2 had HRMS-NFR-024 still been a *should*.** It was unowned at v1.0 and v1.1 for the same reason the rows below were unowned, and §11 question 8 carried it. SRS v1.1 promoted it to a *shall*, which settled the question this table exists to raise; §6.1 modules 2 and 3 now own it and §7.3 costs it at 10 days, taking the baseline to 78. It is recorded here rather than only at §7.3 because the pattern is the point: **this plan has now three times discovered requirements it was committed to but had not costed, and the mechanism that caught all three was writing down what had no owner.**

**The third discovery is the audit row above, and it is the worst of the three, because this table had already found it and then mis-answered it.** The other two rows were unowned and were given owners. The audit row was unowned, was given an answer — *absorbed, no separate estimate* — and the answer was not an owner. Absorption named two modules that would emit audit events; it named nobody to build the thing they emit into. The distinction the row missed is that audit is not one kind of work but two:

- **Cross-cutting emission.** Every module records its sensitive actions. This genuinely is absorbed into each consumer, and no estimate line is owed for it.
- **An owned surface.** The **audit log** entity of SRS §6.1, an append-only writer, the System Administrator read surface that the `docs/07-iam-rbac.md` §4.2 matrix grants with **R**, and the `INSERT`/`SELECT`-only database grant that document's §7.3 makes the whole immutability guarantee rest on. None of this is emitted by a consumer. It is built once, by someone, and until v1.3 that someone was nobody.

**§11 question 3 offered a two-way choice and both answers were wrong.** *Module* was wrong because emission cannot be centralised into one module. *Cross-cutting infrastructure* was wrong because infrastructure does not build itself, and this plan has no line item that would have built it. The question was answerable only by refusing its terms, which is why it survived two re-baselines while looking answered.

**The placement follows this plan's own reasoning, applied where it had not been applied.** §6.1 argues that Notification sits at module 8 because a provider must precede its first consumer. `CONTEXT.md` defines the audit log as recording login attempts among sensitive actions, and §11 question 3 itself conceded that HRMS-NFR-024 made M1 and M2 audit-log consumers. **The plan therefore named Authentication as a consumer of a store it placed two modules later.** Every login attempt in the first module would have been written to a table that did not yet exist. Audit is module 1 for the same reason Notification is module 8, and the reason had been written down for a version before it was applied here.

**What this row costs, and what the sequence of three costs.** Three days, and a third date. Each discovery individually was caught by the mechanism this section describes, and the section is entitled to that. **The sequence is a different matter, and §7.4 is where it is read.** Three uncosted commitments found in one day, in a scope the SRS has held since 2026-05-21, is not a baseline being refined. A plan that has never estimated wrong — because it has never estimated anything against a measured outcome — has now been wrong about what it was *estimating*, three times, before writing a line of code.

| Requirements | Subject | Position at v1.0 | Owner at v1.1 |
|---|---|---|---|
| HRMS-FR-056 to HRMS-FR-062 | Salary structures, pay grades, bonus cycles, allowances, benefits enrolment, compensation history | SRS §4.6, a Phase 3 function. No module in the build order owned it. `docs/07-iam-rbac.md` §4.2 already assigned permissions for these requirements, so the design assumed an implementation surface the build order did not name | Compensation and Benefits, §6.1 module 14, 4 days. Placed immediately before Payroll on the dependency reasoning at §6.1. **Confirmed by the project owner, 2026-07-15** |
| HRMS-FR-033, HRMS-FR-034 | Approval and decision notification, in-app and email (SRS §3.4) | Cross-cutting. Consumed by Recruitment, Onboarding, Leave, and Payroll. No module owned it | Notification, §6.1 module 8, 1.5 days. Placed before the first module with an approval flow; §6.1 states why |
| HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015 | Audit log | Cross-cutting. Design existed at `docs/07-iam-rbac.md` §7.3; no module owned the implementation | **Superseded at v1.2 and resolved at v1.3.** v1.1 recorded it as absorbed within RBAC/IAM and Employee Management, not a separate module, carrying no separate estimate. That was wrong, and §11 question 3 is where it was caught. §6.1 module 1, 3 days, **confirmed by the project owner, 2026-07-15**. See below |

**The record that the gap existed is retained deliberately.** That `docs/07-iam-rbac.md` §4.2 assigned permissions for HRMS-FR-056 to HRMS-FR-062 across five roles before any module owned those requirements is a finding about how the documents were produced, not a clerical error to be tidied away. An accepted design gating an implementation surface that the build order did not name is the kind of divergence the reconciliation check at §5.3 exists to catch, and it was caught by planning rather than by discovering the missing module during development.

The placement of Compensation and Benefits immediately before Payroll is confirmed by the project owner, 2026-07-15, on the dependency reasoning set out at §6.1. The placement of Audit at module 1 is confirmed by him on the same date, with its 3-day estimate and the single-store reading of HRMS-FR-010. **The placement of Notification at module 8 is the plan's inference and remains unconfirmed.** The owner confirmed the extension, confirmed that scope is not cut, confirmed where Compensation and Benefits sits, and has now confirmed Audit; he has never spoken to Notification. Section 11 carries that placement as an open question for his confirmation, and `docs/04-system-architecture.md` remains the document that decides it at M2.

**Two rows of this table are closed by owner confirmation and one is not, and the reason is not that architecture has yet to run.** It is that he was asked about two and not about the third. A question left open because the owner has not answered it, and a question left open because the deciding document has not been written, are different states that this plan has previously allowed to look alike. §11 distinguishes them from v1.3.

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

Every date below is a working day number under §6.2 resolved to a calendar date, and is derived from the allocation at §6.3 by no other route. The working day is given so that the derivation can be checked rather than taken.

| Milestone | Document | Target date | Basis |
|---|---|---|---|
| M1 | `docs/02-project-plan.md` | 2026-07-15 | Working day 1; week 1 of §6.3 |
| M2 | `docs/04-system-architecture.md` | 2026-07-21 | Working day 5; week 1 of §6.3 |
| M3 | `docs/05-database-schema.md` | 2026-07-23 | Working day 7; week 2 of §6.3 |
| M4 | `docs/06-api-contracts.md` | 2026-07-27 | Working day 9; week 2 of §6.3 |
| M5 | `docs/08-testing-plan.md` | 2026-07-29 | Working day 11; weeks 2 and 3 of §6.3. Precedes development; see §6.3 |
| M6 | `docs/09-deployment-plan.md` | 2026-11-03, and constrained | Working day 80; week 16 of §6.3. Schedulable; not completable while TBD-003 is open. See §8.3 |
| M7 | `docs/10-user-guide.md` | 2026-11-04 | Working day 81; weeks 16 and 17 of §6.3 |

**Every date in this table except M2 moved at v1.2. Only two move at v1.3.** M1 to M5 are unchanged from v1.2: they fall in weeks 1 and 2, before development begins on working day 12, and the audit module enters the allocation *at* working day 12, so nothing preceding it is disturbed. M6 and M7 move later by three working days each, which is the audit module of §7.3 displacing the tail.

**The v1.2 and v1.3 moves are of different kinds, and this table is where the difference is visible.** v1.2 moved M1 to M5 *earlier* — a correction, from §6.2 pinning a convention that v1.1 left unstated — and moved M6 and M7 later, a re-baseline. **v1.3 contains no correction.** No date here is wrong under the convention; §6.2 is untouched, and every date above was derived from it at v1.2 and re-derived from it now. The only change is three days of work inserted at day 12. A reader who found v1.2's mixture of corrections and re-baselines hard to separate will find v1.3 simpler and worse: **it is re-baseline only.**

**M6 now falls on 2026-11-03 — the date that was the end of the project at v1.2.** A reader comparing versions should not read that as coincidence or as slippage of the deployment plan specifically. It is the arithmetic: the tail moved three days, and the old end date is where the deployment plan now lands.

**M1 falls on 2026-07-15, the date this document carries.** That is what working day 1 yields for a one-day deliverable, and it is stated rather than adjusted. v1.1 gave M1 as 2026-07-16 while giving M2 as 2026-07-21, and no single reading of week 1 produces both: the pair is the B1 defect in miniature.

At v1.0, M6 and M7 carried no date, because the arithmetic then available produced none inside 2026-09-09. The window has moved to 2026-11-10 and both are schedulable. The dates above are the first at which each document can be finished on the allocation at §6.3; they are not independent commitments and they inherit every qualification of §7.4.

**M6's separate constraint is unchanged by any of the three extensions.** It is schedulable, and it still cannot be *completed* while TBD-003 is open, because the decision rule at ADR-0009 requires legal confirmation, registration where applicable, and a target satisfying HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035, none of which a longer schedule supplies. The 2026-11-03 date is when `docs/09-deployment-plan.md` is written to that decision rule with TBD-003 recorded as open. It is not when a hosting target is selected. Section 8.3 explains.

**The M5 decision deadline is retired as a decision deadline.** At v1.0 it gated the Option A/B/C choice of §7.5, and that choice has been taken. Nothing is served by carrying a deadline for a decision already made, and carrying one would misrepresent the gate as still live.

What the gate protected does remain live, so it is repointed rather than dropped. The build order must be settled before development begins, and development begins on working day 12, 2026-07-30, with **M1 Audit** in week 3 of §6.3. Of the three modules added at §6.1 across v1.1 and v1.3, two are confirmed by the owner — Compensation and Benefits at v1.1, Audit at v1.3 — and **only Notification remains this plan's inference**, carried at §11 as question 2; `docs/04-system-architecture.md` decides it at M2, 2026-07-21. **Its confirmation is therefore due at M2, and 2026-07-29 — M5, the last working day before development begins — stands as the last date by which it may slip without spending capacity on an order that may be revised.** v1.1 gave this date as 2026-07-30 under the unpinned convention; under §6.2 that is the day development starts rather than the day before it, and a slip limit falling on the first day of the work it protects protects nothing. The corresponding row of §8.4 is updated to match.

**The gate is tighter at v1.3 than the unchanged date suggests, and in one respect it has already failed.** Development now begins with a module that did not exist in the build order this morning. Had §11 question 3 gone unanswered until M2 as its own "Resolved by" column directed, working day 12 would have started Authentication — module 1 under the v1.2 order — and the audit table would have been discovered as missing *from inside* the first module that needed it — which is the return visit §6.1 refuses for Notification. **The question was answered five days before the gate rather than by it**, and that margin is the only reason the order is settled. §7.4 reads what it means that the plan needed a separate session to look at a question it had itself written down twice.

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
| 1 | **Audit** | **HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015; the audit log entity of SRS §6.1; `docs/07-iam-rbac.md` §7.3 immutability grant** |
| 2 | Authentication | HRMS-NFR-014, HRMS-NFR-015, HRMS-NFR-020, HRMS-NFR-023; **HRMS-NFR-024 second factor: enrolment by the account holder, and presentation on every authentication**; ADR-0004 |
| 3 | RBAC / IAM | HRMS-NFR-016 to HRMS-NFR-019, HRMS-BR-005, HRMS-BR-012, HRMS-BR-014; **HRMS-NFR-024 recovery approval and the prohibition on factor administration**; `docs/07-iam-rbac.md` |
| 4 | Dashboard | SRS §3.1 role-specific dashboards |
| 5 | Employee Management | HRMS-FR-001 to HRMS-FR-012, HRMS-BR-001 to HRMS-BR-003, HRMS-DR-001 to HRMS-DR-004, HRMS-DR-007, HRMS-DR-008, HRMS-DR-010, HRMS-NFR-007, HRMS-NFR-008 |
| 6 | Departments | HRMS-BR-002; SRS §2.7 HR configuration |
| 7 | Reporting Structure | HRMS-FR-008, HRMS-BR-004 |
| 8 | **Notification** | **HRMS-FR-033, HRMS-FR-034; SRS §3.4 in-app and email channels** |
| 9 | Recruitment | HRMS-FR-013 to HRMS-FR-021 |
| 10 | Onboarding | HRMS-FR-022 to HRMS-FR-024, HRMS-BR-013 |
| 11 | Employee Self-Service | HRMS-FR-025 to HRMS-FR-029, HRMS-FR-044, HRMS-NFR-017, HRMS-BR-006 |
| 12 | Manager Self-Service | HRMS-FR-030 to HRMS-FR-032, HRMS-NFR-018, HRMS-BR-007 |
| 13 | Leave Management | HRMS-FR-063 to HRMS-FR-071, HRMS-BR-009 to HRMS-BR-011, HRMS-DR-006 |
| 14 | **Compensation and Benefits** | **HRMS-FR-056 to HRMS-FR-062, HRMS-DR-010; `docs/07-iam-rbac.md` §4.2** |
| 15 | Payroll | HRMS-FR-035 to HRMS-FR-048, HRMS-BR-008, HRMS-DR-005, HRMS-DR-009, HRMS-NFR-005, HRMS-NFR-009, HRMS-NFR-010 |
| 16 | Reports | HRMS-FR-049 to HRMS-FR-054 |
| 17 | Testing | HRMS-NFR-028, HRMS-NFR-029; `docs/08-testing-plan.md` |
| 18 | UAT | SRS §4 acceptance against stimulus/response sequences |
| 19 | Deployment | HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035; ADR-0009 |

Notification and Compensation and Benefits are new at v1.1 and close two rows of the coverage gap of §2.4. **Audit is new at v1.3 and closes the third**, per §2.4 and §11 question 3. Each insertion renumbered the modules that followed it; **references elsewhere in this document use the v1.3 numbers throughout, and a reader comparing versions should expect every module number after the first to have moved by one at v1.3.**

**Why Audit precedes Authentication.** This placement is confirmed by the project owner, 2026-07-15, on the reasoning that follows. It is module 1 for the reason Notification is module 8: **a provider precedes its first consumer**, and the plan had already written that reasoning down at v1.1 without applying it here. `CONTEXT.md` defines the audit log as the record of sensitive actions and names **login attempts** first among them. Authentication is where login attempts happen. HRMS-NFR-024 adds second-factor enrolment, recovery, disablement, and failed presentation to the audited set, all of which belong to modules 2 and 3. **Authentication is therefore the first consumer of the audit log, and no module can be its provider except one that precedes it.** The absorption answer of v1.0 to v1.2 placed the provider in RBAC/IAM, which follows Authentication — every login attempt in module 2 would have been written to a table that module 3 had not yet created.

The dependency runs one way and is worth stating in that direction too: **Audit does not require Authentication.** An append-only table, a writer, and a database grant do not need a login form to exist. Nothing in module 1 waits on anything.

**What module 1 builds, and what it deliberately does not.** It builds the audit log entity of SRS §6.1, one append-only writer, the System Administrator read surface, and the `INSERT`/`SELECT`-only grant of `docs/07-iam-rbac.md` §7.3. It does **not** build the audit calls in other modules: each module emits its own events, absorbed into that module's estimate, exactly as §2.4 says. Module 1 is the thing they emit *into*.

**One store, not two.** HRMS-FR-010 says "audit history" and HRMS-NFR-013 says "audit log", and the two are the same store. Audit history is a filtered read of the audit log where the target is an employee record; record changes are one of the five categories `CONTEXT.md` lists. **This is confirmed by the project owner, 2026-07-15**, and it is why M5 Employee Management remains at 4 days rather than shedding an audit line to module 1: there was never a separable audit store in M5 to move, only a query against module 1's table. SRS §6.1 names one entity, **Audit log**, and a second store would put employee-record changes outside the single grant on which §7.3 rests its entire immutability argument.

**Why the read surface is not folded into M16 Reports.** M16 already builds filtering and export (HRMS-FR-053, HRMS-FR-054), and folding audit reads into it would save roughly a day and a half. It is refused. The `docs/07-iam-rbac.md` §4.2 matrix gives System Administrator **no access** to the Reports row and **R** on the audit log row; reaching audit through Reports would require granting that role the Reports surface, which HRMS-NFR-019 and SRS §2.3.1 forbid. **The saving is real and the cost is a *shall*.**

**Why the read surface is not the Django admin.** It would be free. `docs/07-iam-rbac.md` §7.3 removes audit models from the admin deliberately, and the break-glass account of that document's §7.2 is precisely the identity that admin access cannot be scoped away from. Building the audit read path through the admin would undo the control that the same section exists to establish.

A module is complete when its models, service layer, API endpoints, visibility rule, permission tests, and client interface are done and its tests pass. A module without permission tests asserting both the permitted and the denied path is not complete (ADR-0005; `docs/07-iam-rbac.md` §5). **Module 1 is where this rule bites hardest and where its cost is most visible**: the audit read surface needs the denied path asserted for all eight roles other than System Administrator, and that, with the grant and the migration-role separation, is most of its 3 days. The models and the writer are not the expensive part.

**Why Compensation and Benefits precedes Payroll.** This placement is confirmed by the project owner, 2026-07-15, on the reasoning that follows. It is not placed at 13 because SRS §4.6 is a Phase 3 function and Phase 3 comes late. It is placed at 13 because Payroll cannot be built before it. `CONTEXT.md` defines a compensation record as a dated record of an employee's compensation whose changes are stored as history and never overwritten (HRMS-DR-010), and defines a payroll run as one execution of payroll for a period over active employees. Payroll computes over compensation records; HRMS-FR-035 to HRMS-FR-048 have nothing to compute over until the records exist. Building Payroll first would mean building a calculation engine against a table that does not exist, then revising it when the table arrives — rework in a schedule that §7.4 says has no room for any. The dependency runs one way: Compensation and Benefits does not require Payroll.

**Why Notification precedes Recruitment.** §2.4 records notification as consumed by Recruitment, Onboarding, Leave, and Payroll. It is placed at 8 because Recruitment is the earliest of those and is the first module in the order with an approval flow: HRMS-FR-014 gives job requisitions approval statuses, and HRMS-FR-033 and HRMS-FR-034 are the notification of a pending approval and of the decision on it. An approval flow built before the notification it fires either ships without notifying, which leaves HRMS-FR-033 and HRMS-FR-034 unmet in a module that needs them, or is revisited once Notification lands. Placing it at 8 costs 1.5 days once and serves four consumers; placing it later costs a return visit to each consumer already built. Modules 2 to 7 have no approval flow and do not need it.

**This paragraph is the reasoning that v1.3 applied to Audit, and a reader should notice it was available a version earlier.** Substitute *audit log* for *notification* and *Authentication* for *Recruitment* and the argument survives word for word — a provider built after its consumer either ships without the provider or forces a return visit. The plan wrote this reasoning at v1.1, and at v1.2 still had audit absorbed into a module that follows its first consumer. **The principle was not missing. It was simply not applied to the row that §2.4 had already flagged**, which is the more uncomfortable finding of the two.

**The three placements do not stand on the same authority, and the numbering reflects two of them.** The owner confirmed Compensation and Benefits as sitting immediately before Payroll; that relation is what he confirmed, and it holds at module 14 here. He confirmed Audit at module 1; that is an absolute position rather than a relation, and nothing displaces it, because nothing precedes it. Compensation and Benefits is numbered 14 rather than 12 because Audit occupies 1 and Notification occupies 8, and each displaces everything after it by one. Should Notification be placed elsewhere or dropped from the order at M2, Compensation and Benefits returns to 13 with its confirmed relation to Payroll intact. **The Notification placement at 8 is the plan's inference and is carried at §11 as question 2 for the owner's confirmation.** `docs/04-system-architecture.md` decides it at M2, as §2.4 and §5.2 record.

**Audit's number is the one number in this table that cannot move without the argument moving with it.** Every other module's position is relative — before Payroll, after Recruitment — and survives renumbering. Module 1 is a claim that *nothing precedes it*, and it rests on there being no module Audit consumes. If `docs/04-system-architecture.md` finds one at M2, the placement is wrong and not merely renumbered.

A module is complete when its models, service layer, API endpoints, visibility rule, permission tests, and client interface are done and its tests pass. A module without permission tests asserting both the permitted and the denied path is not complete (ADR-0005; `docs/07-iam-rbac.md` §5).

### 6.2 The Week Convention

**A week runs Wednesday to Tuesday inclusive and carries exactly five working days: Wednesday, Thursday, Friday, Monday, Tuesday. Week *N* ends on the working day numbered 5*N*, counting 2026-07-15 as working day 1. Every date in this document is derived from that rule and from no other.**

The convention is stated here, once, because v1.1 did not state it and the omission propagated. v1.1 said that week boundaries fall on Wednesdays and that each week carries five working days. **Those two sentences contradict each other.** 2026-07-15 to 2026-07-22, Wednesday to Wednesday inclusive, is six working days, not five: Wednesday, Thursday, Friday, Monday, Tuesday, Wednesday. A reader could take the Wednesday boundary or the five-day week but not both, and the two readings produce different dates for every milestone in §5.2.

That is not a presentational defect. It is why v1.1 stated at its §7 that 68 working days complete on 2026-10-16 while its §6.2 allocated the user guide into 2026-10-19 with 2 slack days after it — two incompatible positions on the same fortnight, each correct under a different reading of an unstated convention. It is also why v1.1's §5.2 gave M1 as 2026-07-16 and M2 as 2026-07-21, which no single reading of week 1 produces. Pinning the convention is therefore the first act of this revision, and the arithmetic at §7.2 follows from it rather than sitting alongside it.

The Wednesday-to-Tuesday reading is chosen over the alternative — retaining Wednesday end-markers and defining them as exclusive — for one reason: an inclusive boundary is the one a reader assumes. A table whose "Ends" column names a date on which no work happens invites exactly the off-by-one that produced B1, and it would invite it again from the next reader. The end-marker convention is defensible and would have been cheaper to introduce; it is not chosen, because the cost of this convention is paid once, here, and the cost of the other is paid by every reader who does not notice the word "exclusive". Week 1 accordingly ends on **2026-07-21**, a Tuesday, not on 2026-07-22.

The project start of 2026-07-15 is a Wednesday and is unchanged. It is what makes Wednesday the natural week start; nothing else recommends it.

### 6.3 Week-by-Week Allocation

The window runs 2026-07-15 to 2026-11-10: 17 weeks, 85 working days, against the 81 required by §7.3.

| Week | Ends | Allocation |
|---|---|---|
| 1 | 2026-07-21 | `docs/02-project-plan.md` (1d); Environment Setup (2d); `docs/04-system-architecture.md` (2d) |
| 2 | 2026-07-28 | `docs/05-database-schema.md` (2d); `docs/06-api-contracts.md` (2d); `docs/08-testing-plan.md` (1d of 2) |
| 3 | 2026-08-04 | `docs/08-testing-plan.md` (1d of 2); M1 Audit (3d); M2 Authentication (1d of 2) |
| 4 | 2026-08-11 | M2 Authentication (1d of 2); M2 second factor (4d of 6) |
| 5 | 2026-08-18 | M2 second factor (2d of 6); M3 RBAC/IAM (3d) |
| 6 | 2026-08-25 | M3 factor recovery and administration prohibition (4d); M4 Dashboard (1d of 1.5) |
| 7 | 2026-09-01 | M4 Dashboard (0.5d of 1.5); M5 Employee Management (4d); M6 Departments (0.5d of 1) |
| 8 | 2026-09-08 | M6 Departments (0.5d of 1); M7 Reporting Structure (1.5d); M8 Notification (1.5d); M9 Recruitment (1.5d of 4) |
| 9 | 2026-09-15 | M9 Recruitment (2.5d of 4); M10 Onboarding (2d); M11 Employee Self-Service (0.5d of 2.5) |
| 10 | 2026-09-22 | M11 Employee Self-Service (2d of 2.5); M12 Manager Self-Service (2d); M13 Leave Management (1d of 4) |
| 11 | 2026-09-29 | M13 Leave Management (3d of 4); M14 Compensation and Benefits (2d of 4) |
| 12 | 2026-10-06 | M14 Compensation and Benefits (2d of 4); M15 Payroll (3d of 8) |
| 13 | 2026-10-13 | M15 Payroll (5d of 8) |
| 14 | 2026-10-20 | M16 Reports (3d); M17 Testing (2d of 4) |
| 15 | 2026-10-27 | M17 Testing (2d of 4); M18 UAT (3d) |
| 16 | 2026-11-03 | M19 Deployment (3d); `docs/09-deployment-plan.md` (1.5d); `docs/10-user-guide.md` (0.5d of 1.5) |
| 17 | 2026-11-10 | `docs/10-user-guide.md` (1d of 1.5); **4d unallocated** |

Weeks 1 and 2 are unchanged in content and in date from v1.2: the audit module enters at working day 12, and nothing before it moves. Week 3 absorbs the 3 days of §7.3. Everything from week 3 is displaced by those 3 days and renumbered by one, and is otherwise the v1.2 sequence unaltered: **no module has been reordered, resized, or resequenced by this revision**, and the tail from M2 onward is the v1.2 tail shifted three days and renamed.

**Every module number in this table moved at v1.3, and the reader should not read the shift as resequencing.** M15 Payroll here is M14 Payroll at v1.2, at the same 8 days, in the same relation to everything around it. The one real change is at working day 12.

**The 4 unallocated days in week 17 are slack, and they are shown as slack.** 81 days of work are allocated against 85 days of capacity. The four days are not filled with work to make the table reach the end date, and no estimate elsewhere has been enlarged to absorb them, because a plan that pads its estimates to consume its margin has no margin and has also lost the ability to say what anything costs. They are the whole of the buffer between this schedule and 2026-11-10. Section 7.4 states what 4 days of buffer against 81 days of uncalibrated estimate is worth.

**That the margin doubled from 2 days to 4 is not the plan becoming safer, and it must not be read that way.** It is what the week grid happens to leave: 81 days requires 17 weeks because 16 weeks is 80, and the 85 days those 17 weeks supply leave 4 over. The same arithmetic left 2 over at v1.1 and v1.2. **The margin is a rounding artefact of where the week boundary falls, and it grew because the work grew past a week boundary — not because anyone sized a reserve.** A reader who takes 4 days as twice the protection of 2 has mistaken an accident for a decision. §7.4 gives the ratio, which is the only form of this number worth reading.

The table is the consequence of the estimates in Section 7.1 laid against the confirmed order. It is not compressed to reach the end date. `docs/08-testing-plan.md` precedes development deliberately: tests are written against a plan, and writing the plan after the code it judges would defeat the only independent control this project has (Section 3). The extension does not change this, and the testing plan is not moved later to bring development forward.

The allocation assumes work proceeds in the order given, with no module overrunning. Where a module overruns, it consumes the 4 days first and the end date afterwards. There is nothing else for it to consume.

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
| M1 Audit | 3 | The audit log entity of SRS §6.1; one append-only writer; the System Administrator read surface granted **R** by `docs/07-iam-rbac.md` §4.2, with the denied path asserted for the other eight roles per ADR-0005; the `INSERT`/`SELECT`-only database grant and separate migration role of that document's §7.3. Excludes per-module emission, which is absorbed by each consumer. New at v1.3; see §7.3 |
| M2 Authentication | 8 | 2 for session authentication per ADR-0004; 6 for the HRMS-NFR-024 second factor — integration, enrolment by the account holder outside administrative control, presentation on every authentication. Newly mandatory and estimated at v1.2; see §7.3 |
| M3 RBAC / IAM | 7 | 3 for groups, two derived roles, per-module visibility rules, the `is_superuser` prohibition of `docs/07-iam-rbac.md` §7.2; 4 for the HRMS-NFR-024 recovery flow gated on a non-account-administering approver and the permission plumbing that bars the System Administrator from the factor. Newly mandatory and estimated at v1.2; see §7.3 |
| M4 Dashboard | 1.5 | |
| M5 Employee Management | 4 | 12 FRs, document upload, audit history. **Unchanged at v1.3.** HRMS-FR-010's audit history is a filtered read of M1's store, not a second store; there was no separable audit line here to move to module 1. See §6.1 |
| M6 Departments | 1 | |
| M7 Reporting Structure | 1.5 | |
| M8 Notification | 1.5 | HRMS-FR-033, HRMS-FR-034; in-app and email channels of SRS §3.4. New at v1.1; see §7.3 |
| M9 Recruitment | 4 | 9 FRs, requisition approval, interview scheduling, offer generation |
| M10 Onboarding | 2 | |
| M11 Employee Self-Service | 2.5 | |
| M12 Manager Self-Service | 2 | |
| M13 Leave Management | 4 | 9 FRs, balance arithmetic, policy enforcement, calendar |
| M14 Compensation and Benefits | 4 | 7 FRs; salary structures, pay grades, bonus cycles, allowances, benefits enrolment; compensation history as dated records per HRMS-DR-010. New at v1.1; see §7.3 |
| M15 Payroll | 8 | 14 FRs; PAYE, SSNIT Tier 1, Tier 2, Tier 3; versioned rate tables; atomic finalisation; idempotent Celery tasks; payslips; bank transfer file |
| M16 Reports | 3 | |
| M17 Testing | 4 | Hardening beyond per-module tests |
| M18 UAT | 3 | |
| M19 Deployment | 3 | |
| `docs/09-deployment-plan.md` | 1.5 | |
| `docs/10-user-guide.md` | 1.5 | Nine guides at SRS §2.6, less the optional training videos |
| **Total** | **81** | Of which 62.5 was the v1.0 baseline, 5.5 is the §2.4 coverage gap closed at v1.1, 10 is HRMS-NFR-024 at v1.2, and 3 is the audit module at v1.3 |

### 7.2 The Arithmetic

The window is 2026-07-15 to 2026-11-10. On the convention pinned at §6.2: **17 weeks at 5 working days for one person = 85 working days.** Against the 81 required by §7.3:

- Available: **85 working days**.
- Required: **81 working days**.
- Margin: **4 working days**, approximately 4.9% of the required effort.
- Ratio: **0.953 times the available capacity.**

81 working days from 2026-07-15, at five days a week with no slippage, completes on **2026-11-04**, a Wednesday — working day 81 under §6.2. The end date is set at 2026-11-10 rather than 2026-11-04 because 2026-11-10 is working day 85 and closes week 17, which is the rule that set 2026-11-03 over 2026-10-30 at v1.2. The four working days between are the margin above and are the 4 days shown unallocated at §6.3. No figure in this section and no date at §5.2 is derived by any route other than §6.2's rule.

**2026-11-04 was available as an end date and was not taken, and the reason is the same rule, not a preference for slack.** Ending on working day 81 would mean ending mid-week with zero margin, which is the position §7.2 declined at v1.2 when it set 2026-11-03 over 2026-10-30. A plan that ends on the last day its own arithmetic allows has no arithmetic left.

**The figures inherited from earlier versions are unchanged and are retained only to show what each closure cost.** Completion of the 78-day scope falls on 2026-10-30, working day 78, as v1.2 stated. Completion of the 68-day scope falls on 2026-10-16 and of the 62.5-day scope on 2026-10-09, as v1.2 corrected them. **None is an alternative baseline and no part of this plan is scheduled against any of them.**

**The original finding stands as a finding, and is not deleted.** At v1.0 the window was 2026-07-15 to 2026-09-09: 8 weeks, **40 working days**, against 62.5 required and probably 68. That was a shortfall of 22.5 working days at the lower figure and 28 at the higher, a ratio of **1.56 times** the available capacity and **1.7 times** with the coverage gap closed. The scope has not shrunk and the estimates have not been revised downward. **The arithmetic balances only because the window keeps moving.** That the original 8-week window was over by more than half, and that this was surfaced in the plan rather than absorbed into an optimistic schedule, is the record this document exists to keep. A reader comparing v1.0, v1.1, and v1.2 should find the overrun reported at v1.0 and the same overrun accounted for at each re-baseline since, not a plan that has quietly always fitted.

**This is the third time the end date has moved, and the three moves are not of the same kind.** v1.1 moved it because the scope did not fit the window. v1.2 moved it because the scope grew: HRMS-NFR-024 became a *shall* in the SRS and the plan had no estimate for it. **v1.3 moves it for neither reason. The scope did not change and the SRS did not change** — the plan discovered that an answer it had already given was wrong. Audit was recorded as owned at v1.0, in the section whose purpose is recording what is unowned, and the record said *absorbed, no estimate*. No requirement moved; the plan simply had not built what it said was covered. None of the three moves was caused by work running late, because no work has yet been done. §7.4 says what a reader should take from that, and v1.3 makes the reading worse rather than better: **a plan can be re-baselined against a changing SRS indefinitely and still be sound. A plan re-baselined against its own prior answer is evidence about the answers it has not yet checked.**

Three figures inherited from earlier versions are corrected here, all of them by the convention at §6.2 rather than by any change of estimate. Completion of the 62.5-day scope falls on **2026-10-09**, not "on or about 2026-10-12" and not the 2026-10-08 stated at v1.1: 62.5 days end halfway through working day 63, which is 2026-10-09. Completion of the 68-day scope falls on **2026-10-16**, working day 68, which v1.1 stated correctly. The v1.0 window's own end date of 2026-09-09 is one day past working day 40, which is 2026-09-08; the 40-day capacity figure is unaffected and the shortfall above stands. That two of the three were wrong by exactly one day, in a document that never pinned its week, is the defect §6.2 describes rather than three separate slips.

### 7.3 The Coverage Gap Is Closed, and HRMS-NFR-024 Is Owned

Section 2.4 recorded requirements that no module in the build order owned. At v1.0 this section quantified what closing the gap would cost and left it as a contingency. It is no longer a contingency. The owner's decision at §7.5 was to extend the end date and not to reduce the content of the release; requirements with no module owner do not get built, so leaving them unowned would have reduced the content of the release by omission. **The plan was therefore baselined on 68 days at v1.1, not 62.5, on 78 days at v1.2, and is baselined on 81 days at v1.3.**

**The gap was declared closed at v1.1 and was not closed.** Three rows were recorded; two got module owners and estimates; the third got the word *absorbed* and no estimate, and that was counted as closure. It was not, and §11 question 3 said so for two versions while this section said the gap was shut. **A row that names no module and no estimate is an unowned requirement with a note attached.** The audit row is closed at v1.3 in the way the other two were closed at v1.1: a module, a number, and an owner's confirmation.

| Item | Days | Owner |
|---|---|---|
| v1.0 baseline | 62.5 | |
| Compensation and Benefits — HRMS-FR-056 to HRMS-FR-062 | 4 | §6.1 module 13. New at v1.1 |
| Notification — HRMS-FR-033, HRMS-FR-034 | 1.5 | §6.1 module 7. New at v1.1 |
| Audit log implementation — HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015 | ~~absorbed within M2 and M4~~ | ~~No separate module; unchanged from v1.0~~ **Superseded at v1.3; see below** |
| v1.1 baseline | 68 | |
| Second factor — HRMS-NFR-024 enrolment and presentation | 6 | §6.1 module 2. Newly mandatory and estimated at v1.2 |
| Factor recovery and the prohibition on factor administration — HRMS-NFR-024 | 4 | §6.1 module 3. Newly mandatory and estimated at v1.2 |
| v1.2 baseline | 78 | |
| Audit module — the entity, the append-only writer, the read surface, the immutability grant | 3 | §6.1 module 1. New at v1.3 |
| **Baselined total** | **81** | |

The 62.5-day and 68-day figures are retained above only to show what each closure cost. Neither is an alternative baseline, and no part of this plan is scheduled against either.

**The project owner confirmed the 81-day baseline on 2026-07-15**, separately from his confirmation of 2026-11-10 at §7.5. The two are recorded separately because they are different acts. Confirming the date accepts a commitment, which is his to make. Confirming the baseline accepts 81 as the figure this plan is scheduled against — also his to make, and now made. **Neither is a finding that 81 is correct, and §7.4 is unaffected in full.** No one has calibrated these estimates, the owner included; he is accepting the number the plan gave him, not certifying it. An estimate does not become right by being agreed to, and §7.4's reading stands unchanged: 81 is a lower bound, the 4-day margin is 4.9% of it, and 2026-11-10 is the earliest date the work could finish rather than the date it will.

**He confirmed 78 on the same day, and this section recorded that confirmation in these same words.** That is not an embarrassment to be tidied away, and the plan does not restate the figure as though 81 had always been it. The sequence was: the plan gave him 78, he accepted 78, and within the same day the plan discovered that 78 omitted a module it had recorded as owned since v1.0. **What his confirmation of 78 demonstrates is exactly what this paragraph claims — that owner confirmation is acceptance of a figure, not verification of it.** He could not have caught the omission; nothing he was shown contained it. §11 question 9 carries the same point for the date, and the pair of them is the strongest evidence in this document for §7.4's position: **an uncalibrated estimate confirmed by the person it commits is still an uncalibrated estimate, and 81 is now the third figure to be confirmed in one day.**

**Why the audit module costs 3 days and why it was not costed before.** It was not costed because this section said it did not need costing. The v1.1 row above — struck through rather than deleted — read *absorbed within M2 and M4, no separate module, no separate estimate*, and §11 question 3 recorded that if the answer were wrong the figure was low. **The answer was wrong and the figure was low, exactly as the question said.** §2.4 sets out why both of that row's readings failed. What follows is only the estimate.

The requirement is not satisfied by adding a `models.py` with a timestamp column. The 3 days are the sum of four pieces, and the cheap-looking part is not the expensive part:

- **The entity and the append-only writer.** One table and one service function. `JSONB` is already justified by `docs/03-tech-stack.md` §9 for versioned rate tables, so the event detail column needs no new dependency and no per-module audit tables. This is the genuinely small part, and it is roughly a day.
- **The System Administrator read surface.** `docs/07-iam-rbac.md` §4.2 grants **R**. An endpoint, a client interface, and — per ADR-0005 and §6.1's completion rule — permission tests asserting the *denied* path for the eight roles that hold no audit access. The denied paths outnumber the permitted one eight to one, and HRMS-NFR-019 is what they enforce.
- **The immutability grant.** The application's database role restricted to `INSERT` and `SELECT`, with schema changes run by a separate migration role the application process does not hold. This is deployment configuration, and Environment Setup's 2 days at §7.1 cover Docker Compose composition only. **It is the whole of `docs/07-iam-rbac.md` §7.3's guarantee**: that section argues at length that Django permissions are the wrong layer because `is_superuser` bypasses them, and the grant is what binds the break-glass account instead.
- **Emission at each consumer.** Zero days here, by design. Each module records its own events within its own estimate, which is the one thing the absorption row got right.

**The 3 days are the least calibrated figure in this plan, and that is saying something.** §7.4 holds that the HRMS-NFR-024 estimate is the newest and therefore weakest number in §7.1. This one is newer. It was produced during a re-baseline, in a single day, against no code, by the same author whose estimates have never been measured — and it is the figure on which a third date now rests. **It carries §7.4's qualification in full and then one qualification of its own: the other estimates in §7.1 were at least wrong about how long known work takes. This one is the cost of discovering that the plan did not know what the work was.**

**Why HRMS-NFR-024 costs 10 days and why it was not costed before.** At v1.0 and v1.1 it was a *should*, it was unowned, and §11 carried it as question 8 — the plan recorded that if it entered the release the 68-day figure was low by its estimate, and it did not supply the estimate. SRS v1.1 promoted it to a *shall*. The condition §11 named has occurred, and the plan is now obliged to own it. This is not scope the plan has added; it is scope the SRS made mandatory and the plan is now costing for the first time.

The requirement is not satisfied by adding a one-time-password prompt to the login form. HRMS-NFR-024 requires four separable pieces of work, and the estimate is the sum of them:

- A second-factor integration, and its presentation on **every** authentication of an administrator or payroll user.
- An enrolment flow performed by the account holder and reachable by no role that administers accounts, credentials, roles, or permissions. Enrolment is where the requirement is usually lost: a factor an administrator can enrol on another user's behalf is a factor that administrator can also present.
- A recovery flow for a lost or unavailable factor, gated on an approver who does not administer accounts or credentials, with a password reset explicitly insufficient to restore access to an enrolled account.
- Permission plumbing that bars the System Administrator from enrolling, resetting, disabling, or bypassing a factor, alongside the `is_superuser` prohibition already at `docs/07-iam-rbac.md` §7.2 — and permission tests asserting the denied path for each, per ADR-0005 and §6.1's completion rule.

The split across modules 2 and 3 follows what each module owns rather than what is convenient to schedule. Presentation and enrolment are authentication; recovery approval and the administrative prohibition are authorisation, and belong with the role model that `docs/07-iam-rbac.md` fixes. Neither half is useful alone: the enrolment flow of module 2 is not outside administrative control until module 3's prohibition exists, so the requirement is not met until working day 29 (§6.3), and no intermediate point claims it is.

**The 10 days are this plan's estimate and carry §7.4's qualification in full.** They are the newest and therefore least calibrated figures in §7.1, produced during a re-baseline rather than examined at v1.0, and the same is true of the four days for the recovery flow in particular, which depends on an approver role whose grant is not settled until `docs/04-system-architecture.md` at M2. The requirement is mandatory regardless; the estimate is not thereby made reliable.

**HRMS-NFR-024 closes the gap against HRMS-NFR-019, and that is why it is not negotiable against the date.** SRS v1.1 records that HRMS-NFR-019 — a *shall* — was unenforceable while a System Administrator could reset a payroll user's credentials and authenticate as them. Deferring HRMS-NFR-024 to hold 2026-10-21 would reopen that gap while leaving HRMS-NFR-019 on the books as a *shall*, which is Option C's trade in a different costume and is refused on the same reasoning (§7.5).

### 7.4 What the Estimates Are Worth

They are one person's judgement, uncalibrated against any completed work on this project or this stack. They are not story points, and no velocity has been measured. They should be read as a lower bound, for three reasons:

1. They include no allowance for public holidays, illness, rework, or CodeRabbit review turnaround.
2. They assume every requirement is understood well enough to build. Section 8.1 shows that ten of the thirteen open TBDs bear directly on modules in the build order, and that eleven cannot be closed by this project at all.
3. Uncalibrated software estimates by the person who will do the work are, as a class, optimistic. There is no reason to suppose these are the exception.

Nothing in any of the three re-baselines improves any of the three reasons. The estimates at §7.1 are the same estimates, made by the same person, with the same absence of any completed work to calibrate against. Five of them are newer than v1.0 and are the least calibrated in the table, since they were produced during a re-baseline rather than examined at the outset: M8 Notification at 1.5 days and M14 Compensation and Benefits at 4 days, new at v1.1; the 6 and 4 days of HRMS-NFR-024 within M2 and M3, new at v1.2; and M1 Audit at 3 days, new at v1.3 and newer than all of them. **The extensions have bought 45 working days and no information.**

**The margin is 4 working days against 81 days of estimate that is, on the plan's own account, a lower bound. That is approximately 4.9%, and 4.9% of an uncalibrated estimate is not a margin.** It is a rounding artefact of where the week boundary happens to fall, as §6.3 says. M15 Payroll at 8 days, the largest and most exposed estimate in the table, need be wrong by 50% to consume it entirely. §7.2 argues the reverse case at v1.0 — that every estimate would have to be wrong by more than a third for 62.5 to become 40 — and the same reasoning cuts this way now: **every estimate would have to be right, or the date moves.** Uncalibrated estimates are not, as a class, right.

**The margin doubled at v1.3, and a reader who reads that as the plan getting safer has read it backwards.** 2 days against 78 was approximately 2.6%; 4 days against 81 is approximately 4.9%. The ratio nearly doubled. **Nobody decided this and it protects nothing that was not protected before.** 81 days crossed the 80-day boundary of 16 weeks, so the grid supplied a seventeenth week, and 4 of its 5 days are unallocated because the work stopped at 81. Had the audit module cost 2 days instead of 3, the margin would be 0 and the date would be 2026-11-03; had it cost 7, the margin would be 3 and the date 2026-11-10 still. **The margin is a function of where 81 falls between two multiples of five, not of anyone's judgement about risk.** v1.2 warned that an unchanged "2 days" concealed growing exposure unless read against the denominator. v1.3 inverts the trap: a doubled margin conceals that the thing it defends grew again, and that the defence was issued by arithmetic rather than by anyone deciding the plan needed it.

**A reader should take the pattern, not the instance.** The date has now moved three times: 2026-09-09 to 2026-10-21 at v1.1, to 2026-11-03 at v1.2, and to 2026-11-10 at v1.3. All three moves happened before a single line of application code was written, and none was caused by the work going badly. They were caused by the plan finding out what it had already committed to — first that the coverage gap of §2.4 was real work, then that HRMS-NFR-024 was mandatory, then that the third row of that same coverage gap had never actually been closed. Each individual move was correct and is defended above; **the sequence of them is evidence about the plan's ability to see its own scope, and that evidence is not favourable and got worse at v1.3.**

**The third move is the one that should change a reader's estimate of this plan, and it is different in kind from the first two.** v1.1 and v1.2 were the plan responding to things outside it: a window that was too short, and an SRS that promoted a requirement. A plan cannot be blamed for either, and both were caught. **v1.3 is the plan correcting itself.** Nothing outside it moved. §2.4 had already identified audit as unowned at v1.0, printed it in a table whose entire purpose is to prevent exactly this, given it an answer that was not an owner, and declared the gap closed. §11 question 3 then carried the doubt for two versions and two re-baselines, naming the precise consequence — *if it is a module, the figure is low* — and both re-baselines passed over it while recomputing every other number in the document. **The mechanism §2.4 celebrates did not fail. It fired, was read, and was not acted on.** Three corrections in one day, from a scope the SRS has held since 2026-05-21, is not a settled baseline adjusted three times. It is a baseline whose remaining unknowns have not been exhausted, and §8.1 names thirteen still open. **The honest reading is that 2026-11-10 is the fourth date, not the last one, and the plan now has a demonstrated mechanism for producing a fifth: its own open questions, which it writes down and does not resolve.**

**The arithmetic balances. This does not make the date safe, and the reader should not take the one for the other.** At v1.0 the plan reported a shortfall of 22.5 days and the number carried its own warning. At v1.1, v1.2, and now v1.3 it reports a surplus, and a surplus reads as comfort in a way a shortfall does not. It is not comfort. The v1.0 position was *this cannot be done in the time*; the position now is *this can be done in the time if nothing goes wrong, and the plan has no view on whether anything will go wrong, because it has never measured this author on this stack*. The second is a weaker claim than it looks, and **2026-11-10 is the earliest date the work could finish, not the date it will.**

**The estimates would be worth more if the plan cited a source for them. It cannot, because there is none.** No historical velocity exists (§1.3), and no re-baseline creates any. **The one thing v1.3 improves is when the first evidence arrives.** At v1.2 the first calibration point was M1 Authentication against its 8 days, finishing in week 4, and that figure was 6 parts new estimate to 2 parts old. At v1.3 the first calibration point is **M1 Audit against its 3 days, finishing on working day 14 in week 3** — a full week earlier, and a pure estimate rather than a blend, since none of its 3 days predates today. It is a smaller number and therefore a noisier signal; 3 days is too few to distinguish a bad estimate from a bad week. But it arrives before Authentication, before RBAC/IAM, and before the 10 days of HRMS-NFR-024 are spent, which is the first point at which overrun could still be acted on rather than reported. **If module 1 runs long, §7.2's arithmetic is void on working day 14, and the date at §5.2 should be revised at once rather than defended to 2026-11-10.** The plan has spent three versions discovering scope late. Module 1 is the first opportunity it has to discover anything early, and it exists only because §11 question 3 was finally answered.

### 7.5 The Decision Taken

**At v1.0 this section recorded a verdict and three options: the confirmed scope did not fit the confirmed schedule, and 62.5 days of work, probably 68, could not be done in 40.** The verdict was correct and is not withdrawn. The options were stated for the project owner, because re-baselining the release is not a decision a planning document makes on its own authority.

**The project owner has taken Option B: the end date moves and the content of the release is not reduced.** Decision recorded 2026-07-15. The owner separately confirmed the placement of Compensation and Benefits immediately before Payroll (§6.1). This section records the decision and the position of the options not taken; §7.2 gives the resulting arithmetic and §7.4 states what it is worth.

**The date the decision named was 2026-10-21; the date is now 2026-11-10.** The owner chose Option B's *principle* — extend rather than cut — and that principle governs the v1.2 and v1.3 re-baselines as it governed v1.1. He did not choose 2026-11-03 or 2026-11-10 when he took Option B; neither existed as a candidate on 2026-07-15 at the moment of that decision, and this plan does not represent him as having done so. What §7.3 adds at v1.2 is the cost of a requirement the SRS made mandatory after his decision, and at v1.3 the cost of a module this plan had failed to own. Applying his stated principle to both is the plan's inference, and it is the safe inference in one direction only: had the plan instead held the date by deferring HRMS-NFR-024 or by leaving the audit log unbuilt, it would have cut scope under a decision that scope is not cut, which is exactly the silent reduction §2.4 and Option A's rejection exist to prevent. **The project owner confirmed 2026-11-03 on 2026-07-15, and then confirmed 2026-11-10 on 2026-07-15**, each after the extension was put to him as the plan's inference rather than his decision. The date is his. §11 question 9 records the sequence, because a plan whose dates are owner-confirmed should show which were named and which were inferred and then ratified — **and should show, as that question now does, that the plan asked him to ratify a date twice in one day and does not present the second as sturdier than the first.**

**The audit module's 3 days are not the same kind of cost as HRMS-NFR-024's 10, and Option B's principle covers them for a different reason.** The 10 days were scope the SRS added; extending for them protects a decision the owner made against a change he did not. The 3 days are scope this plan had always carried and had mis-recorded as free. **There was no version of v1.3 in which the audit log was optional**: HRMS-NFR-013 is a *shall*, it has been a *shall* since v1.0, and the only question was whether the plan admitted it had no line item for it. Extending here is not applying Option B's principle to new scope. It is paying a bill that was already outstanding.

**Option A — reduce the content of this release. Not chosen.** It would have delivered Phase 1 and Phase 2 by 2026-09-09 and re-baselined Phase 3 (SRS §2.2: Reporting and Analytics, Compensation and Benefits, Leave Management) into a later release. The owner rejected reducing scope. Two things follow and are recorded because they constrain what may now be done quietly.

First, the option is not merely unexercised; its rejection is what closes the §2.4 coverage gap. Compensation and Benefits is a Phase 3 function and was the largest unowned item in that gap. Leaving it without a module while declining to re-baseline it out of the release would have achieved Option A's effect without Option A's SRS revision — the requirement dropped in fact and retained on paper. §2.4 and §7.3 therefore give it an owner and an estimate, and the plan is baselined at 68 days.

Second, Option A was never sufficient alone: Payroll at 8 days plus M16 to M18 at 10 days already exceeded what remained inside 2026-09-09, so it would have had to be combined with Option B in any case. The choice was never between A and B. It was whether B came with A attached, and the owner's answer is that it does not.

Option A is also no longer available in the form it was offered, and the plan records this rather than leaving a rejected option looking like a live fallback. Option A would have re-baselined Phase 3 into a later release. HRMS-NFR-024 is not a Phase 3 function; it is authentication, module 2 in the build order, on which every module depends. **Deferring Phase 3 today would not recover the 10 days that moved the date to 2026-11-03, nor the 3 that moved it to 2026-11-10** — the audit log is not a Phase 3 function either; it is module 1, on which every module depends for HRMS-NFR-013. A reader looking for a way back to 2026-10-21 will not find one in Option A.

**Option C — lower the quality bar. Rejected, and the rejection is unaffected by the extension.** It is recorded here so that it is rejected explicitly rather than by drift. The obvious saving is the permission tests, at a meaningful fraction of every module estimate. ADR-0005 states that nothing enforces the application of a visibility rule and that an endpoint omitting it silently returns unscoped data; `docs/07-iam-rbac.md` §5 calls that a disclosure defect of the most serious kind. The permission tests are the control for that specific weakness, in a system holding salary figures, SSNIT and PAYE records, and identity documents, built by one person with no independent reviewer. Cutting them converts a schedule problem into a disclosure problem. The same reasoning bars cutting UAT, which is the only stage where the stimulus/response sequences of SRS §4 are exercised end to end.

**Each extension makes Option C more tempting rather than less, and this is the reason the reasoning above is restated in full rather than referenced.** A schedule with 4 days of margin against uncalibrated estimates (§7.4) will come under pressure, and the pressure will arrive at Payroll, late, with a date already committed and the permission tests as the largest apparently discretionary line item in reach. The saving would be real and the cost would be silent, which is precisely the trade ADR-0005 says cannot be seen from inside the code. Nothing about 2026-11-10 changes the disclosure position of a system holding this data, built by one person, reviewed by nobody. **If the date cannot be met, the date moves. The tests do not.** That is the plan's position now and its position at the point where the pressure lands, and it is written here so that the later decision is measured against the earlier one.

**v1.3 adds a third target of the same kind, and it is barred for the same reason.** M1 Audit's 3 days are, by §7.3's own breakdown, mostly permission tests asserting the denied path for eight roles, plus a database grant that no feature demo will ever show. It is the most cuttable-looking module in the plan and the first one scheduled. Cutting its tests leaves an audit log that HRMS-NFR-019 cannot rely on and that `docs/07-iam-rbac.md` §7.3 calls the detection control for everything its constraints do not reach; cutting its grant leaves the log erasable by the account it exists to incriminate. **A module that is cheap to cut and invisible when missing is exactly the module this section exists to protect.** The date moves before it does.

**v1.2 adds a second target of the same kind, and it is barred for the same reason.** HRMS-NFR-024's 10 days at §7.3 are now the largest single increment in the plan, they sit in modules 2 and 3 at the very start of development, and a schedule under pressure in week 4 will find them before it finds anything else. The permission tests barring the System Administrator from the second factor are the cheapest-looking part of that 10 days and are the part that makes the requirement true; without them, module 2 ships a second factor an administrator can enrol, which is HRMS-NFR-019's gap reopened and HRMS-NFR-024 unmet while appearing met. **A second factor that the account administrator controls is not a second factor. Cutting the tests that prove otherwise converts a schedule problem into the disclosure problem the requirement was promoted to close.** The date moves before this does, on the same terms as above.

The decision this section carried is taken; §5.2 records what became of the M5 decision deadline that gated it.

---

## 8. Risks

### 8.1 The Open TBD Register

`docs/01-srs.md` Appendix C carries seventeen TBD items. TBD-016 and TBD-017 are new at SRS v1.1, which restated HRMS-NFR-001 to HRMS-NFR-006 as measurable thresholds and recorded the data volumes they are verified against, and HRMS-NFR-005's elapsed-time threshold, as TBDs rather than stating figures it had no basis for. Four are resolved: TBD-002 and TBD-004 by `docs/03-tech-stack.md`, TBD-010 by `docs/07-iam-rbac.md`, and TBD-011 by the web-first decision of SRS §2.5 and §6.4. **Thirteen remain open.**

**The two new items are not a deterioration of the requirements; they are a disclosure.** At v1.0 the performance requirements were stated as ranges and were unverifiable, and the plan did not record that as a risk because an unverifiable requirement raises no TBD. SRS v1.1 made them testable and, in doing so, made visible the two inputs that were always missing. The register is longer because the SRS is more honest, not because more is unknown.

Of the thirteen, TBD-013 is inert for this release — SRS §6.4 places biometric attendance out of scope, so it blocks nothing here and is carried only for completeness. The other twelve are unresolved requirements sitting beneath a plan that treats the SRS as authoritative, and each is a live schedule risk. The register below states which deliverable each blocks and when it must be resolved.

**"Before M*n* begins" means the last working day preceding the module's first day, not the first day itself.** The distinction is not pedantry: a deadline falling on the day the work starts leaves no day on which the input can be acted upon, and is the B1 defect of §6.2 in another place — a convention left unstated, silently resolving to an off-by-one. v1.3 stated it and corrected TBD-008, TBD-012, TBD-014, TBD-016, and TBD-017, each of which had named its module's own first day. `scripts/check-docs.py` asserts it from v1.3.

| TBD | Subject | Status | Blocks | Must resolve by |
|---|---|---|---|---|
| TBD-001 | Final organization name | **Open. Not resolvable by this project.** There is no operating organisation | Stage 9 Deployment; role grants at deployment (`docs/07-iam-rbac.md` §8); the `payroll.approve_payroll_run` grant (§4.4); TBD-003 by dependency | Before Stage 9. Not before |
| TBD-002 | Final technology stack | **Resolved** by `docs/03-tech-stack.md` | — | — |
| TBD-003 | Hosting environment | **Open by decision.** ADR-0009 defers it; the decision rule is at ADR-0009 and `docs/03-tech-stack.md` §7.2 | `docs/09-deployment-plan.md`; M19 Deployment. Does not block development — ADR-0009 makes resolution a configuration change, not a code change | See §8.3 |
| TBD-004 | Database technology | **Resolved** by `docs/03-tech-stack.md` §5.1 (PostgreSQL); ADR-0003 | — | — |
| TBD-005 | Final payroll statutory rates | **Open. Not resolvable by this project.** Requires qualified payroll or finance confirmation (SRS §2.7, §6.3) | M15 Payroll: HRMS-FR-039 to HRMS-FR-042. Also `docs/08-testing-plan.md`, which cannot state expected payroll values without them | Before M15 completes, 2026-10-13. See §8.2. **Neither extension bears on this** |
| TBD-006 | Bank transfer file format | **Open. Not resolvable by this project.** Depends on the organisation's bank (SRS §2.5), which depends on TBD-001 | M15 Payroll: HRMS-FR-046 | Before M15 completes, 2026-10-13. See §8.2. **Neither extension bears on this** |
| TBD-007 | HR approval workflows | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | `docs/05-database-schema.md` (approval records); M9 Recruitment (HRMS-FR-014); M13 Leave Management (HRMS-BR-009). Also M8 Notification, which fires on the approval events HRMS-FR-033 and HRMS-FR-034 name. Also M3, whose HRMS-NFR-024 recovery flow requires an approver who administers no accounts — the approval is defined by the requirement, but who holds it is not | **Before M3 sign-off, 2026-07-23.** The schema must model approval whether or not the workflow content is known |
| TBD-008 | Leave policy rules | **Open. Not resolvable by this project.** SRS §2.7 assumes HR defines them | M13 Leave Management: HRMS-FR-067, HRMS-FR-068, and the "unless policy allows" condition on both | Before M13 begins, 2026-09-21 |
| TBD-009 | Document retention policy | **Open. Not resolvable by this project** | `docs/09-deployment-plan.md`; audit log retention per `docs/07-iam-rbac.md` §7.3; M4 document storage per ADR-0007 | Before Stage 9 |
| TBD-010 | Exact user roles and permissions | **Resolved** by `docs/07-iam-rbac.md`; ADR-0010 | — | — |
| TBD-011 | Mobile app in first release | **Resolved** by SRS §2.5 and §6.4: web-first, native application out of scope. Recorded at `docs/03-tech-stack.md` §11. ADR-0004 depends on this holding | — | — |
| TBD-012 | External job board integration | **Open** | M9 Recruitment: HRMS-FR-015. SRS §2.5 notes external posting may depend on third-party API availability | Before M9 begins, 2026-09-04 |
| TBD-013 | Biometric attendance later | **Open, and inert for this release.** SRS §6.4 places it out of scope | Nothing in this plan | Not required |
| TBD-014 | Reporting dashboard KPIs | **Open. Not resolvable by this project** | M4 Dashboard; M16 Reports: HRMS-FR-049 to HRMS-FR-054 | Before M4 Dashboard begins, 2026-08-24 |
| TBD-015 | Data migration approach | **Open. Not resolvable by this project.** SRS §2.7 assumes the organisation provides employee data | Stage 9 Deployment; Stage 11 Handover | Before Stage 9 |
| TBD-016 | Organization size and data volumes against which HRMS-NFR-001 to HRMS-NFR-005 are verified: employee record count, payroll history volume, document storage volume | **Open. Not resolvable by this project.** It is the size of an organisation that does not exist, and SRS Appendix C records it as depending on TBD-001. New at SRS v1.1 | M17 Testing: HRMS-NFR-001 to HRMS-NFR-005 cannot be verified without the volumes they are verified over. `docs/08-testing-plan.md`, which cannot state a performance expectation against an unstated dataset. M15 Payroll for HRMS-NFR-005. M16 Reports for HRMS-NFR-004 | Before M17 Testing begins, 2026-10-16. `docs/08-testing-plan.md` at M5, 2026-07-29, records it as open rather than waiting on it |
| TBD-017 | Payroll processing elapsed time threshold for HRMS-NFR-005 | **Open. Not resolvable by this project.** SRS Appendix C records it as depending on TBD-016, which depends on TBD-001. New at SRS v1.1 | M17 Testing: HRMS-NFR-005 has no threshold to test against. M15 Payroll, whose run duration is the quantity measured | Before M17 Testing begins, 2026-10-16. As TBD-016 |

### 8.2 The Structural Risk Beneath the Register

**Eleven of the thirteen open TBDs cannot be closed by this project as constituted.** They are TBD-001, TBD-003, TBD-005 to TBD-009, and TBD-014 to TBD-017. They require an operating organisation, its HR policy, its bank, its payroll authority, its size, or qualified legal, payroll, and finance professionals. TBD-001 records that no such organisation exists, and every one of the eleven depends on it directly or through a chain. Only TBD-012 is open and closable here; TBD-013 is inert.

The count at v1.1 was stated as "nine of the twelve" against a register of eleven open items, and neither figure was right: the closable-by-nobody count was nine and the open count was eleven. The figures are restated above and the register is the arithmetic, not the sentence. This is the same class of defect as B1 and is corrected on the same principle — a number in prose that no longer matches the table beneath it is a defect whether or not anything depends on it.

This is not a risk that better scheduling addresses, and it will not close before 2026-11-10.

**Neither re-baseline touches any of it, and the new date must not be read as bearing on it.** The two extensions have moved the end date by eight weeks in total. They did not create an operating organisation, an HR policy, a bank, a payroll authority, or access to qualified legal, payroll, and finance professionals. Eleven of the thirteen open TBDs required one of those on 2026-07-15 and require one of those on 2026-11-10. The register at §8.1 is materially the register it was at v1.0, with dates shifted and module numbers corrected. Three things have changed and none is progress: TBD-007 now bears on M8 Notification, and on M3's HRMS-NFR-024 recovery approver; and TBD-016 and TBD-017 have appeared, which is SRS v1.1 naming two unknowns that the v1.0 requirements were too vague to expose. **The unknowns count went up, and that is the register becoming more accurate rather than the project getting worse.** Neither is movement toward closing anything.

The consequence for Payroll is the sharpest, and it is not a scheduling consequence. M15 implements HRMS-FR-039 to HRMS-FR-042 — PAYE, SSNIT Tier 1, Tier 2, Tier 3 — and HRMS-FR-046, the bank transfer file. TBD-005 leaves the rates unconfirmed and TBD-006 leaves the file format unknown. **Payroll can therefore be built but cannot be signed off as correct, on any schedule, including this one.** Option B in Section 7.5 was taken and it buys time; **it does not buy statutory rates.** TBD-005 and TBD-006 made Payroll unsignable-off at v1.0 under a 2026-09-09 date, at v1.1 under a 2026-10-21 date, at v1.2 under a 2026-11-03 date, and at v1.3 under a 2026-11-10 date. This is stated twice, here and at §7.5, because a re-baselined plan invites the reading that the problems it was written around have been dealt with, and these have not been. **No date this project can adopt closes them.** A fourth date changes nothing about this, and the fact that the date has now moved three times without touching TBD-005 or TBD-006 is the demonstration rather than the exception.

TBD-017 now joins them at lower stakes but on the same footing. HRMS-NFR-005 states that payroll processing completes within an elapsed time that TBD-017 does not supply, for an organisation size that TBD-016 does not supply. M14 can be built and its duration measured; **it cannot be shown to meet HRMS-NFR-005, because HRMS-NFR-005 does not yet say what it requires.** That is a requirement the project cannot verify rather than a test the project has not written, and no schedule closes it either.

What follows is a constraint on how M14 is built and on what its completion may claim. It is unchanged by the re-baseline:

- Rates are versioned configuration, never constants in code (`CONTEXT.md`; `docs/03-tech-stack.md` §5.1; SRS §2.5). The calculation engine is built against the rate-table structure, not against particular rates.
- Any rates used during development are recorded as provisional and unverified, in the repository, at the point of use. They are not represented as the rates in force.
- The bank transfer file is built behind an interface with one format implementation, which is replaced when TBD-006 closes. HRMS-FR-046 is not claimed complete until then.
- M15 completes as *calculation engine built, statutory correctness unverified*. It does not complete as *Payroll done*. SRS §6.3 requires confirmation by qualified professionals before go-live, and no test this project can write substitutes for it. **Reaching 2026-11-10 with M15 complete is not Payroll delivered, and the plan does not permit that claim.**

The same pattern applies at lower stakes to M13 under TBD-008, to M4 and M16 under TBD-014, and to M17 under TBD-016 and TBD-017: the mechanism is built against a documented provisional assumption, and the assumption is recorded as provisional rather than absorbed into the code as though it were a requirement. For M17 specifically, a performance figure measured against a dataset this project invented is a measurement of that dataset and is recorded as such; it is not evidence that HRMS-NFR-001 to HRMS-NFR-005 are met.

M14 Compensation and Benefits, new at v1.1, enters this pattern rather than escaping it. It stores compensation history as dated records per HRMS-DR-010 and `CONTEXT.md`, and M15 computes over those records. Its structure is a design question the plan can answer; the rates and policies that populate it are not, and TBD-005 reaches it for the same reason it reaches Payroll.

### 8.3 Deployment Is Blocked, and Not by Effort

ADR-0009 defers the hosting target because Ghana's Data Protection Act 2012 (Act 843) position on data residency is unresolved, and because TBD-001 leaves no controller to register under section 27(1) and no counsel to advise. The decision rule at ADR-0009 requires three things before a hosting target is selected: written confirmation from qualified legal counsel, registration with the Data Protection Commission where applicable, and confirmation that the target satisfies HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035.

None of the three can be satisfied within this schedule, because all three presuppose an organisation. This was true of the 8-week schedule, of the 14-week one, and is true of the 16-week one.

Therefore:

- **Stage 9 Deployment does not conclude in this project.** M18's 3 days build and exercise the containerised composition; they do not produce a production deployment. Neither extension changes this: none of ADR-0009's three conditions is a matter of having more time.
- `docs/09-deployment-plan.md` is written to ADR-0009's decision rule. It documents the composition, backup topology, and TLS position *conditionally on the target*, and records TBD-003 as open. It does not select a host, and a plan that did would contradict an accepted ADR.
- No development or demonstration deployment implies a hosting commitment (ADR-0009; `docs/03-tech-stack.md` §7.2).
- No production personal data of any Ghanaian employee is placed in any environment while TBD-003 is open. There is none to place, and this is recorded so that convenience does not later supply some.

### 8.4 Other Risks

| Risk | Consequence | Response |
|---|---|---|
| Single point of failure in resourcing | Any absence stops the project entirely. There is no second person and no partial capacity | Not mitigable by planning. Recorded as an accepted condition of a solo project. It compounds every estimate in §7.1, and the 4 days of margin at §7.2 cover approximately four days of absence across 17 weeks |
| No independent reviewer | Defects the author cannot see survive to UAT, which the same author runs | Partial mitigation only; see §9 |
| Visibility rule omitted from an endpoint | Silent disclosure of employee-scoped data. ADR-0005 states nothing enforces the rule's application | Permission tests per module asserting permitted and denied paths; review treats a missing scope call as blocking (`docs/07-iam-rbac.md` §5). This is why Option C is rejected |
| Payroll task retried, producing duplicate records | Corrupt payroll with monetary consequence | Idempotent task semantics as a first-order concern of M14's design (`docs/03-tech-stack.md` §4.2; ADR-0006) |
| Documents 04–06 contradict the already-complete 07 | Rework in a schedule with 2 days of slack | Reconciliation check at each of M2, M3, M4; see §5.3 |
| The build order is revised after development starts | Capacity spent on modules a revision reorders | The §7.5 option decision is taken. What remains is the placement of M8 Notification, this plan's inference (§6.1), which `docs/04-system-architecture.md` decides at M2, 2026-07-21, and which must not slip past 2026-07-29, the day before development begins; see §5.2 and §11 |
| The margin at §7.2 is read as slack rather than as rounding, and v1.3's doubling of it makes this likelier | An overrun is absorbed silently against 4 days that were never a buffer, and the first honest report of slippage arrives late | §7.4 states the margin as approximately 4.9% of an uncalibrated estimate, and warns that its doubling at v1.3 is a rounding artefact rather than added protection. The M1 Audit actual against its 3 days on working day 14 is the first calibration point, a week earlier than v1.2's, and is treated as one |
| A further requirement is found to be unowned or unestimated, and the date moves a fourth time | The date loses whatever meaning a reader still attaches to it, and each move arrives as a surprise rather than as a forecast | Not mitigable by planning, and not presented as mitigated. **This risk materialised at v1.3 and is no longer hypothetical**: §11 question 3 was the unestimated item, the plan had written it down twice, and it moved the date anyway. §7.4 states that 2026-11-10 is the fourth date rather than the last. The plan's defence is that §11 names what it does not know — and v1.3 is the demonstration that naming a thing is not resolving it |
| HRMS-NFR-024 is descoped, deferred, or built without its permission tests to recover the 10 days | HRMS-NFR-019's gap reopens while HRMS-NFR-019 remains a *shall*. A second factor the account administrator can enrol is not a second factor, and the system would appear to meet a requirement it does not | §7.3 and §7.5 record the position in advance: the date moves before this does. The 10 days are not the plan's discretionary spend; they are an SRS *shall* the plan is costing for the first time |
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
| 1 | **Resolved at v1.1.** Which module owns HRMS-FR-056 to HRMS-FR-062? The build order had no Compensation and Benefits module, yet `docs/07-iam-rbac.md` §4.2 already assigned permissions for those requirements across five roles | Resolved. §6.1 module 14, immediately before Payroll, **confirmed by the project owner 2026-07-15** on the dependency reasoning at §6.1. `docs/04-system-architecture.md` records the assignment at M2; it does not reopen the placement |
| 2 | **Where does Notification sit in the build order?** §6.1 places it at module 8, before M9 Recruitment, because Recruitment is the first module with an approval flow (HRMS-FR-014) and HRMS-FR-033 and HRMS-FR-034 are the notification of a pending approval and of the decision on it. **This is the plan's inference and is not confirmed.** The owner confirmed the extension, confirmed that scope is not cut, and confirmed the Compensation and Benefits placement; he did not speak to this one | The project owner, with `docs/04-system-architecture.md` at M2, 2026-07-21, and not later than 2026-07-29 (§5.2). Every week from 8 onward in §6.3 depends on the answer, and a later placement returns HRMS-FR-033 and HRMS-FR-034 to consumers already built |
| 3 | **Resolved at v1.3, and the question was wrong.** Is audit logging a module, or cross-cutting infrastructure consumed by every module? `docs/07-iam-rbac.md` §7.3 designs it; nothing implements it. §7.3 of this plan absorbed it within RBAC/IAM and Employee Management and gave it no separate estimate, which presumed the second answer | Resolved. **Neither answer was right, and the two-way framing is what let this survive two re-baselines.** Audit is an owned surface — the SRS §6.1 entity, an append-only writer, the System Administrator read surface, the `docs/07-iam-rbac.md` §7.3 immutability grant — **plus** cross-cutting emission absorbed by each consumer. *Module* was wrong because emission cannot be centralised; *infrastructure* was wrong because infrastructure does not build itself. §6.1 gives the owned half **module 1**, before Authentication, since `CONTEXT.md` makes login attempts audited and this plan had placed the provider two modules after its first consumer. §7.1 costs it at **3 days**; the 78-day figure was low by exactly that, **as this question said it would be**. **Confirmed by the project owner 2026-07-15** — placement, estimate, and the single-store reading of HRMS-FR-010 — on the question 1 precedent. `docs/04-system-architecture.md` records the assignment at M2; it does not reopen it. **The question named its own consequence for two versions and was passed over by both re-baselines that recomputed everything around it; §7.4 reads what that is worth** |
| 4 | What is the working calendar? The repository defines no public holiday schedule, and every estimate in §7.1 assumes five uninterrupted days per week | The project owner. Bears directly on §7.2, and more sharply at each re-baseline: the schedule now runs to 2026-11-10 with 4 days of margin against 81. The margin doubled at v1.3 and the exposure did not halve — §7.4 explains why the grid, not a decision, produced it. Four public holidays inside the window consume it entirely, and the plan does not know how many there are — which is the question |
| 5 | **Retired at v1.1.** Whether Option A required a re-baselined SRS phase boundary or a second release with its own SRS | Retired. Option A was not chosen (§7.5); the question it asked does not arise. Recorded rather than deleted so that the v1.0 numbering can be followed |
| 6 | What does M18 UAT mean with no users? UAT is acceptance by the people who will use the system. TBD-001 leaves no organisation, so the sole participant is the author, who wrote the code and the SRS | The project owner. If it is self-verification against SRS §4, it should be named that, and `docs/08-testing-plan.md` should say so rather than call it acceptance |
| 7 | What does Stage 11 Handover mean with no recipient? SRS §2.7 assumes HR staff are trained before go-live; there are none | The project owner. Bears on `docs/10-user-guide.md`, whose nine guides at SRS §2.6 currently have no reader |
| 8 | **Resolved at v1.2, and not by this plan.** Is HRMS-NFR-024 — multi-factor authentication for administrators and payroll users — in this release? At v1.0 and v1.1 it was a *should*, unestimated in §7.1, and owned by no module. The question recorded that if it entered the release the 68-day figure was low by its estimate | Resolved. SRS v1.1 promotes HRMS-NFR-024 to a *shall*, closing the gap against HRMS-NFR-019. It is therefore in the release, not by the plan's election but by the SRS's. §6.1 gives it owners in modules 2 and 3, §7.3 estimates it at 10 days, and the 68-day figure was low by exactly that, as this question said it would be. **The question was answered by the requirement changing, not by the owner deciding**, and §11 question 9 carries the schedule consequence he has not yet seen |
| 9 | **Resolved at v1.2, superseded at v1.3, on the same day.** Is the extension to 2026-11-03 accepted? The owner took Option B on 2026-07-15 and named 2026-10-21 (§7.5). SRS v1.1 then made HRMS-NFR-024 mandatory, and §7.3 costs it at 10 days, which no longer fit inside 2026-10-21. This plan applied his stated principle — extend rather than cut — and re-baselined to 2026-11-03 on that inference | **He confirmed 2026-11-03 on 2026-07-15. It held for part of one day.** Resolving question 3 added the audit module's 3 days, taking the baseline to 81, which does not fit inside 2026-11-03; **he confirmed 2026-11-10 on 2026-07-15**, and separately confirmed the 81-day baseline (§7.3). **The plan records that it obtained his confirmation of a figure that was already wrong when he gave it**, rather than restating 81 and 2026-11-10 as though they had always been the numbers. He could not have caught the omission: it was in a row of §2.4 that said *absorbed*, and nothing he was shown contained it. **This is the clearest evidence in the document for §7.4's position that owner confirmation is acceptance, not verification.** Two dates and two baselines confirmed in one day, and the plan does not represent the second pair as more durable than the first |

---

## 12. Traceability

| Plan element | Serves |
|---|---|
| §2.1 scope baseline | HRMS-FR-001 to HRMS-FR-071, HRMS-NFR-001 to HRMS-NFR-036, HRMS-BR-001 to HRMS-BR-015, HRMS-DR-001 to HRMS-DR-010 |
| §2.2 exclusions | SRS §6.4 |
| §2.3 deferral of HRMS-FR-055 and HRMS-FR-051 | SRS §4.5, which defers both by their own terms |
| §4 stage sequence | SRS §1.4, §2.1 phased development |
| §5.1 document set | SRS §3.3, which records the stack as TBD to be confirmed in technical architecture planning |
| §5.3 out-of-order reconciliation | `docs/07-iam-rbac.md` §3, §4.2, §4.4, §5; ADR-0005; ADR-0010 |
| §6.1 build order | SRS §2.2 phases; ADR-0001 module boundaries |
| §6.1 module 1 Audit | HRMS-FR-010, HRMS-NFR-013, HRMS-NFR-022, HRMS-BR-015; SRS §6.1 audit log entity; SRS §2.3.1 System Administrator audit access; `CONTEXT.md` audit log; `docs/07-iam-rbac.md` §4.2 read grant and §7.3 immutability |
| §6.1 module 8 Notification | HRMS-FR-033, HRMS-FR-034; SRS §3.4 in-app and email channels |
| §6.1 module 14 Compensation and Benefits | HRMS-FR-056 to HRMS-FR-062; SRS §4.6; HRMS-DR-010; `CONTEXT.md` compensation record; `docs/07-iam-rbac.md` §4.2 |
| §6.1 modules 2 and 3, HRMS-NFR-024 | HRMS-NFR-024; HRMS-NFR-019, whose gap it closes; ADR-0004; ADR-0010; `docs/07-iam-rbac.md` §7.2 |
| §6.2 week convention | Nothing in the SRS. It is this plan's own, and governs only this plan's dates |
| §7.3 HRMS-NFR-024 estimate | HRMS-NFR-024; ADR-0005 and `docs/07-iam-rbac.md` §5 for the permission tests it requires |
| §7.3 audit module estimate | HRMS-NFR-013; ADR-0003 for the PostgreSQL grant; ADR-0005 and `docs/07-iam-rbac.md` §5 for the denied-path tests; `docs/03-tech-stack.md` §9 for the `JSONB` detail column |
| §7.5 Option C rejection | ADR-0005; `docs/07-iam-rbac.md` §5; HRMS-NFR-016 to HRMS-NFR-019 |
| §8.1 TBD register | SRS Appendix C, TBD-001 to TBD-017 |
| §8.1 TBD-016, TBD-017 | SRS §5.1, HRMS-NFR-001 to HRMS-NFR-005; SRS Appendix C |
| §8.2 payroll constraint | SRS §2.5, §6.3; ADR-0003; ADR-0006; HRMS-FR-039 to HRMS-FR-042, HRMS-FR-046 |
| §8.3 deployment block | ADR-0009; SRS §2.4, §6.3; HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035 |
| §9 quality controls | ADR-0003, ADR-0005; HRMS-DR-001 to HRMS-DR-010; HRMS-NFR-028, HRMS-NFR-029 |
