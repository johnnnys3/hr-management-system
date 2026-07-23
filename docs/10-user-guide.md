# User Guide

**Human Resource Management System**

| | |
|---|---|
| Version | 1.0 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-23 |
| Status | Draft — issued ahead of schedule, see §0 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-23 | Initial user guide, covering all eight IAM roles plus system operations. Issued out of the plan's own build order — see §0 for the exception and its terms. Written against `docs/07-iam-rbac.md` v1.6, `frontend/src/routes.tsx`, and the current backend app set | 1.0 |

---

## 0. Why This Document Exists Now, Out of Order

`docs/02-project-plan.md` §5.2 schedules this document as **M7**, the last deliverable in the schedule (working day 103, 2026-12-04), after M19 UAT and M20 Deployment. This draft is issued now, between M18 Testing and M19 UAT, on the project owner's explicit decision — a deliberate exception to the plan's own sequencing, not a silent reordering.

Two consequences of writing it early, stated plainly rather than glossed over:

- **It documents a system that has not yet passed UAT or been deployed.** Every workflow described below reflects the develop branch as of `a5eb078` (2026-07-23). Nothing here is a claim that the system is production-ready or organisationally accepted — that is exactly the open question `docs/02-project-plan.md` §11 question 6 records and this document does not resolve.
- **This does not retire M7.** The plan's M7 milestone and its 2026-12-04 date are unchanged; this draft is issued for early review and will be revised, not superseded, when M19/M20 land — most likely to add a deployment/access-provisioning section once TBD-003 (hosting) resolves.

This document answers SRS §2.6's nine named guides (System Administrator, HR Administrator, Employee self-service, Manager self-service, Payroll processing, Recruitment and onboarding, Leave management, Basic troubleshooting, FAQ) as sections of one file rather than nine separate files, matching `docs/02-project-plan.md` §7.1's single `docs/10-user-guide.md` deliverable. The optional tenth item — training videos — is out of scope, as the plan's own cost basis excludes it.

**One gap worth naming rather than silently patching:** SRS §2.6 names no guide for the Executive role, and no guide for the HR Officer/Recruiter split `docs/07-iam-rbac.md` §2.4 draws within the "HR Administrator" user class. §5 and §7 below cover HR Officer and Recruiter as their own sections despite the SRS's grouping, since `docs/07-iam-rbac.md` treats them as separate roles with materially different permissions and a merged section would misdescribe access. §8 covers Executive on the same reasoning — every assigned role gets a section, regardless of how SRS §2.6 grouped the underlying user classes. This is a documentation completeness choice, not an SRS revision, and does not change §2.6 itself.

### 0.1 How to Use This Document

Each role section below covers: what the role can see and do, the exact screens it reaches, and the workflow for its most common task. Section 10 (System Administration) is written for whoever operates the system, not for an end user — read it if you are provisioning accounts, running migrations, or seeding data, not if you are using the HR system day to day.

Screen names below match `frontend/src/routes.tsx` route labels. If a screen is not listed for your role, you do not have access to it — that is enforced by `docs/07-iam-rbac.md` §4.2's permission matrix, not by UI convention alone.

---

## 1. Roles at a Glance

Eight roles serve seven SRS user classes (`docs/07-iam-rbac.md` §2.2). Six are **assigned** by a System Administrator; two — Employee and Manager — are **derived** automatically from your employment record and never granted.

| Role | Kind | Section |
|---|---|---|
| System Administrator | Assigned | §10 |
| HR Administrator | Assigned | §4 |
| HR Officer | Assigned | §5 |
| Recruiter | Assigned | §7 |
| Payroll Officer | Assigned | §6 |
| Executive | Assigned | §8 |
| Employee | Derived | §2 |
| Manager | Derived | §3 |

If you hold more than one role — the system permits it (`docs/07-iam-rbac.md` §6) — every screen listed under each of your roles is available to you, and each screen behaves per that role's own permissions.

---

## 2. Employee (Self-Service)

Every person with an employee record and active employment status is an Employee, automatically — there is nothing to request. This is the baseline every other role adds to.

### 2.1 What you can do

- View and update your own profile (`/my-profile`): personal details, emergency contacts, documents.
- View your own compensation and payslip history, where applicable (`docs/07-iam-rbac.md` §4.2 — read own only, no editing).
- Submit and track your own leave requests (`/leave`).
- Read your own notifications (`/notifications`).
- Request an additional role, if your job requires one (`/role-grant-requests`) — this is reviewed and decided by a System Administrator, not granted automatically.

### 2.2 Common task: requesting leave

1. Go to **Leave** (`/leave`).
2. Choose **New Leave Request**, pick a leave type, start and end date.
3. Submit. Your balance is checked at submission but only decremented on approval (HRMS-BR-009 to HRMS-BR-011).
4. Your manager is notified and approves or rejects (see §3.2). You are notified of the decision either way.
5. Track status any time from the same screen — pending, approved, rejected, or cancelled.

### 2.3 What you cannot do

You cannot see any other employee's profile, leave, or compensation data, and you cannot approve your own leave request even if you also hold a role that can approve others' (self-approval is refused everywhere it would otherwise apply — see §6.4 for the sharpest version of this rule, in payroll).

---

## 3. Manager (Team Self-Service)

You become a Manager automatically the moment the org chart records one or more direct reports (`docs/07-iam-rbac.md` §3.2) — nothing is granted, and the role disappears automatically if your last report is reassigned. You keep every Employee capability from §2 as well.

### 3.1 What you can do

- View your team (`/my-team`): direct reports' profiles, at a read level appropriate to management oversight, not full HR access.
- Approve or reject your team's leave requests (`/leave`, viewed from the manager's perspective on the same screen) — this is the one action-level permission unique to Manager (`docs/07-iam-rbac.md` §4.2, "Leave approval — A" row).
- View team-level reports (`/reports`), where the Reports screen grants Manager a narrower, team-scoped view alongside HR/Executive/Payroll's broader access.

### 3.2 Common task: approving a leave request

1. Go to **Leave**. Requests from your direct reports awaiting your decision are shown there.
2. Open a request, review the dates and balance impact, and approve or reject.
3. On approval, the requester's leave balance is decremented immediately; on rejection, nothing changes and the requester is notified with the reason if one was given.
4. You cannot approve your own request, and you cannot approve a request from someone who is not your direct report — including a skip-level report; `docs/07-iam-rbac.md` §5 states there is no transitive chain, so a skip-level manager sees nothing of a report's report through this screen.

---

## 4. HR Administrator

Governance and configuration, not day-to-day record transactions — see `docs/07-iam-rbac.md` §2.4 for why this is split from HR Officer.

### 4.1 What you can do

- Define and maintain HR configuration (`/departments`): departments, job titles, leave types, pay grades, salary structures, approval workflow definitions.
- Read (not create/update) employee records, and update only employment **status** (`docs/07-iam-rbac.md` §4.2) — the record-maintenance actions themselves belong to HR Officer.
- Read employee documents, recruitment records, onboarding records, compensation history, and reports, across the organisation.
- Access Reports (`/reports`) at full HR scope.

### 4.2 What you cannot do

You cannot create or edit an individual employee record, and you cannot assign an employee to a pay grade — both are HR Officer actions. You hold no payroll processing access and no system-configuration/user-account access (that is System Administrator territory, held by no one else). This split exists specifically so that no single account can both invent a pay grade and create the employee record that benefits from it (`docs/07-iam-rbac.md` §2.4's ghost-employee fraud path).

### 4.3 Common task: defining a new leave type

1. Go to **Departments** (which also hosts leave-type and pay-grade configuration).
2. Create the leave type with its accrual rule and any approval-workflow specifics.
3. It becomes immediately available to HR Officer for balance assignment and to every Employee when submitting a new leave request.

---

## 5. HR Officer

Record maintenance and transactions — the day-to-day HR work, deliberately disjoint from HR Administrator's governance role, not a subset of it.

### 5.1 What you can do

- Create, read, and update individual employee records (`/employees`, `/employees/:id`) — the core of your role.
- Manage employee documents fully (create, read, update).
- Update self-service profile data on an employee's behalf where needed.
- Assign an employee to a pay grade (`docs/07-iam-rbac.md` §4.6) — this is an HR Officer action specifically, not HR Administrator's.
- Update (not approve) leave requests — corrections and cancellations, never approval (`docs/07-iam-rbac.md` §4.3 — approval is Manager-only, to prevent an HR bypass of the manager approval workflow).
- Handle onboarding (`/onboarding`, `/onboarding/:id`): convert a candidate to an employee record once recruitment reaches offer stage, and manage onboarding checklists.
- Read recruitment records and candidate detail (`/recruitment/candidates/:id`), narrower than Recruiter's own create/update access.

### 5.2 Common task: onboarding a new hire

1. Once Recruitment (see §7) has moved a candidate to offer stage, go to **Onboarding**.
2. Convert the candidate record to an employee record. This requires the candidate's application to be at `stage='offer'` — the system enforces the sequence.
3. Create the onboarding checklist (`/onboarding/:id`) and track task completion.
4. Assign the new employee to their pay grade, if not already set during the offer.

### 5.3 What you cannot do

You cannot define the pay grade structure itself (min/max figures, salary bands) or approve leave — both sit elsewhere by design, per §2.4's separation-of-duties reasoning.

---

## 6. Payroll Officer

The most tightly scoped assigned role, by design (HRMS-NFR-019): reads only what payroll requires, nothing recruitment- or document-related.

### 6.1 What you can do

- Process payroll end to end (`/payroll`): create and calculate payroll runs, submit for approval, view statutory rates, generate payslips and the bank transfer file.
- Read the employee fields payroll needs — identifiers, employment status, compensation, statutory numbers, bank details — nothing else.
- Read compensation structures and pay grades (read-only; HR Officer/Administrator own creating them).
- Access payroll-cost reporting (`/reports`), scoped to payroll figures.

### 6.2 Mandatory second factor

Payroll Officer is one of the roles HRMS-NFR-024 requires a second factor for. On first login you will be prompted to enrol (`/second-factor/enroll`) — this is self-service only; no administrator can enrol a second factor on your behalf (`docs/06-api-contracts.md` §4.2). If you lose your device, recovery (`/second-factor/recovery`) requires a designated approver who does not administer your account — see §10.4 for why that approver is deliberately not a System Administrator.

### 6.3 Common task: running payroll

1. Go to **Payroll**, start a new run, and **Calculate**. PAYE and SSNIT Tiers 1–3 are computed against the current versioned statutory rate table.
2. **Submit for approval.** Finalisation requires a second, distinct person's approval — you cannot approve your own run under any role combination you hold (§6.4).
3. Once approved, **Finalize**. This is atomic: payroll runs, payslips, and payslip lines commit together or not at all — there is no partially-finalised payroll state to recover from.
4. Generate the bank transfer file and download payslips for distribution.

### 6.4 Self-approval is refused, always

`docs/07-iam-rbac.md` §4.4: the person who initiated a payroll run can never approve its finalisation, "regardless of any combination of roles" they hold. This is enforced at both the API and the database layer — even a direct database write attempting to set the same user as both initiator and approver is rejected by a `CHECK` constraint, not only by application code.

### 6.5 A note on statutory rates (open item)

`docs/02-project-plan.md` TBD-005 records that final PAYE/SSNIT rates require confirmation by a qualified payroll or finance professional, not resolvable within this project. The calculation engine is built and tested against the versioned rate-table structure; the rates themselves are not yet confirmed for statutory correctness. Do not treat a completed payroll run as a claim that its figures are statutorily correct until TBD-005 closes.

---

## 7. Recruiter

### 7.1 What you can do

- Own the recruitment pipeline (`/recruitment`): job requisitions, postings, candidates, applications, interviews, offers.
- Read pay grade **names** only, to select an `offered_pay_grade` when issuing an offer — not the salary figures behind that grade, and not the salary structure itself (`docs/07-iam-rbac.md` §4.3 — a blind selection, not compensation visibility).
- Read onboarding records, to track a candidate's progress past offer.
- Read HR configuration (departments, job titles) at a reference level.

### 7.2 Common task: taking a candidate to offer

1. Go to **Recruitment**, create or select a requisition, and add candidates through the pipeline stages.
2. Schedule interviews and record outcomes on the candidate detail screen (`/recruitment/candidates/:id`).
3. When ready to extend an offer, select the `offered_pay_grade` by name from the list available to you.
4. Issuing the offer advances the candidate's application to offer stage, which is what unlocks HR Officer's conversion step in Onboarding (§5.2) — the two roles hand off at exactly this point.

### 7.3 What you cannot do

You cannot see actual compensation figures, cannot define or assign pay grades, and cannot see any payroll data. Requisition approval is HR Administrator's action, not yours — you create and manage the requisition, but its approval status changes elsewhere.

---

## 8. Executive

The narrowest-access assigned role by requirement, not by oversight: SRS §2.3.7 requires summarised reporting, and `docs/07-iam-rbac.md` §4.3 enforces that strictly.

### 8.1 What you can do

- Read the Reports and Dashboards screen (`/reports`, and the composite dashboard at `/`), aggregate figures only: headcount, leave utilisation, turnover, payroll cost.

### 8.2 What you cannot do

You never reach an individual employee record, an individual payslip, or any per-person figure through any path — this is tested as a disclosure control, not a display preference (`docs/08-testing-plan.md` §4, module 17 row): even a report filtered narrowly enough that only one employee could match still returns an aggregate, never that employee's own figure. There is no screen in this system, at any role, that gives Executive record-level access.

---

## 9. Frequently Asked Questions

**Why can't I see [some other employee's] information?**
Row-level visibility is enforced per module regardless of what your role can otherwise do (`docs/07-iam-rbac.md` §4.1's two-layer model). Being allowed to view "employee records" as an action does not mean every row is visible to you — only the rows your role's visibility rule returns.

**I have two roles — why does a screen behave differently than I expected?**
Each screen applies each of your roles' permissions independently; nothing merges them into a single, wider permission. If in doubt, check `docs/07-iam-rbac.md` §4.2's matrix cell for your specific role and module, not for "a user with your combination of roles" as a category.

**I lost access to a second-factor device and can't log in — what do I do?**
Go to `/second-factor/recovery`. Your request is decided by a designated approver who administers no account credentials — not by a System Administrator, and not automatically. Until an approver is designated (an open operational item, `docs/07-iam-rbac.md` §8), recovery on a privileged account requires manual, out-of-band resolution. This is the correct failure mode for a control meant to prevent self-service credential bypass, not a bug.

**Why did my leave balance not change immediately when I submitted a request?**
Balance is checked at submission (so you cannot request more than you have) but only decremented on manager approval (`docs/07-iam-rbac.md` §4.2; HRMS-BR-009 to HRMS-BR-011). A rejected or cancelled request never decrements it.

**Can I approve my own request/run/grant?**
No, anywhere this pattern exists (leave, payroll finalisation, role grants, second-factor recovery) — self-approval is refused structurally, not merely discouraged, and in payroll's case it is enforced at the database layer independent of the application.

---

## 10. System Administration

Written for whoever operates the system — provisioning accounts, running the stack, seeding data — not for a day-to-day HR user. System Administrator the *role* (§10.1–10.4) is one part of this; the rest is operational, for whoever has shell/infrastructure access regardless of in-app role.

### 10.1 What the System Administrator role can do, in-app

- Create, read, and update user accounts and role grants (`/users`) — this is the only route by which any assigned role (HR Administrator, HR Officer, Recruiter, Payroll Officer, Executive) is granted; none are self-service.
- Read the audit log (`/audit-log`) — full visibility, append-only, never edited.
- Maintain system configuration.

### 10.2 System Administrator is deliberately not `is_superuser`

`docs/07-iam-rbac.md` §7.2 and the README's bootstrapping section: Django's `is_superuser` flag is never used, specifically so that a System Administrator cannot silently bypass RBAC and reach HR or payroll data. There is no `createsuperuser` command in this system. Assigned-role groups are seeded by migration; no user is. See the README's "Bootstrapping the first account" section for the one-time shell command that creates the first account and grants it System Administrator.

### 10.3 System Administrator holds no HR or payroll access

This is a deliberate ceiling, not an oversight (`docs/07-iam-rbac.md` §4.3). If your job requires both administering the system and doing HR or payroll work, both roles must be granted explicitly to your account — holding System Administrator grants you nothing in either domain by itself.

### 10.4 Privileged recovery is a deployment condition, not a design gap

Second-factor enrollment and recovery approval, and payroll-finalisation approval, are both deliberately withheld from System Administrator (HRMS-NFR-024, `docs/07-iam-rbac.md` §7.3) — granting either to the same role that resets credentials would recreate the proxy-account path HRMS-NFR-024 exists to close. `docs/07-iam-rbac.md` §8 records this designation as **deferred to deployment**: until an organisation names who holds these approver permissions, there is no self-service recovery path for a privileged account's lost second factor. Treat that as the system correctly refusing an unsafe shortcut, not as a bug to route around.

### 10.5 Running the stack

See the repository root `README.md` for the authoritative, maintained instructions — this section only orients you to where things live, since README is what gets kept current as the stack changes:

- **First run**: `cp .env.example .env`, `docker compose up -d`, then run migrations via `docker compose run --rm django-migrate python manage.py migrate`.
- **Rebuilding after code changes**: backend changes rebuild `django`, `django-migrate`, `celery-worker`; frontend changes rebuild `caddy` (the SPA is built into that image).
- **Running tests**: `docker compose run --rm --entrypoint "" django-migrate python manage.py test`, optionally scoped to one app label.

### 10.6 Seeding test/demo data

`backend/accounts/management/commands/seed_e2e_fixtures.py` seeds a full set of role-covering test accounts, idempotently. It is hard-guarded behind `settings.ALLOW_E2E_FIXTURES` and refuses to run without it — this is a test-only tool, never a production seeding path, and its checked-in credentials must not be treated as a template for real accounts.

### 10.7 Known operational gaps at time of writing

- **Hosting environment is undecided** (TBD-003) — deployment configuration is deferred until an organisation is named, per ADR-0009.
- **Backups and HTTPS-in-production** (HRMS-NFR-012, HRMS-NFR-020) are pending the same hosting decision (`docs/03-tech-stack.md` §7.2).
- **Second-factor recovery approver and payroll-finalisation approver are both undesignated** (§10.4 above) — no organisation-specific choice has been made yet.
- **Statutory payroll rates and bank transfer file format are unconfirmed** (TBD-005, TBD-006) — the payroll engine is built and tested against its own structure, not against confirmed real-world values.

None of these block using the system as described in §2–§9 above; they block claiming the system is production-signed-off, which this document does not do.
