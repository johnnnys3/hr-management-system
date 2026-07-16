# ADR-0011: Mail dispatch separated from notification

**Status:** Accepted
**Date:** 2026-07-15
**Bears on:** `docs/02-project-plan.md` §11 question 2 (where Notification sits in the build order)

## Context

`docs/02-project-plan.md` v1.1 introduced a Notification module and placed it at module 8, immediately before Recruitment. The placement was the plan's inference and was never confirmed by the project owner; §11 carried it as question 2, and §2.4 and §5.2 named this document as the one that decides it.

The reason given at §6.1 was:

> Notification precedes Recruitment ... because Recruitment is the earliest of those and is the first module in the order with an approval flow: HRMS-FR-014 gives job requisitions approval statuses, and HRMS-FR-033 and HRMS-FR-034 are the notification of a pending approval and of the decision on it.

**That reason misreads three sentences of the SRS, and each misreading is load-bearing.**

1. **HRMS-FR-033 and HRMS-FR-034 are not Recruitment requirements.** They appear in SRS §4.3, *Employee Self-Service and Manager Self-Service* — not §4.2, *Recruitment and Onboarding*. The approval they concern is named in §4.3's stimulus/response sequence: "Manager Approves Request: Manager receives a notification, opens request details, approves or rejects the request, and the system updates the status and notifies the employee." That is the self-service request flow, whose approval is HRMS-FR-031. The plan grafted §4.3's requirements onto §4.2's approval status.

2. **HRMS-FR-014 requires no notification.** It states that job requisitions shall have approval statuses. A status is not a notification, no requirement asks that a requisition approval be announced to anyone, and HRMS-FR-033 speaks of notifying *managers*, which a Recruiter is not. Recruitment has no notification requirement at all.

3. **The SRS distinguishes notifications from password reset emails.** SRS §3.3 gives the Email Service the purpose "Send notifications **and** password reset emails". SRS §3.4 lists the consumers of email as "approvals, onboarding, password reset, and payroll-related communication". Plan §2.4 rendered that list as "Recruitment, Onboarding, Leave, and Payroll" — substituting Recruitment for approvals, and **dropping password reset entirely**.

The third misreading is the consequential one. Password reset belongs to Authentication, which is module 2 in the v1.3 order. **Notification at module 8 therefore sat six modules after its first consumer** — a violation of the plan's own rule that a provider precedes its first consumer, which is the identical defect §11 question 3 found in the audit placement and which ADR-0010's residual analysis found in a different form. It is the third instance of the same error in the same document.

**The question as posed could not be answered.** "Where does Notification sit?" presumes Notification is one thing occupying one position. It is not.

## Decision

**Notification splits three ways, and the pieces occupy different positions in the build order.**

| Piece | Position | Estimate | What it owns |
|---|---|---|---|
| **Mail dispatch** | Module 2, between Audit and Authentication | 2 days | Sending email reliably off the request cycle: the Celery task, SMTP configuration, template rendering, bounded retry, delivery-failure logging |
| **Notification** | Module 11, immediately before Employee Self-Service | 2 days | The notification entity and the in-app feed of pending tasks and request updates (SRS §3.4); HRMS-FR-033 and HRMS-FR-034 |
| **Emission** | Cross-cutting | Absorbed per consumer | Each module deciding which of its own events fires a notification |

**Mail dispatch knows nothing about why a message is sent.** Its consumers are password reset in Authentication (module 3), onboarding (module 10), Notification (module 11), and payroll communication (module 16).

**Notification is a consumer of mail dispatch, not the channel itself.** It may deliver in-app, by email, or both.

**Authentication does not depend on Notification.** That relation does not exist. It consumes mail dispatch directly, and the plan's §2.4 consumer list obscured this by describing email consumers as notification consumers.

**Supporting decisions:**

1. **Mail dispatch is a module, not Environment Setup.**
2. **The in-app surface sits at 11, and role-grant and second-factor recovery approvers are not notified in this release.**
3. **Delivery is best-effort. The domain action commits regardless.** Bounded Celery retry; a send failure does not roll back an approval or a reset.
4. **Delivery failures go to application logs, not the audit log.**
5. **Password reset returns a uniform response** whether or not the address exists and whether or not the mail sent.
6. **The names are chosen so the boundary cannot be misread again.** The module at position 2 is *mail dispatch*, not "notification transport".

## Rationale

### Mail dispatch is a module, not Environment Setup

The tempting answer is that mail dispatch is plumbing: SMTP settings against a Celery/Redis broker ADR-0006 already committed to, landing inside Environment Setup's 2 days in week 1, well before Authentication needs it on working day 12.

**The audit precedent forecloses it.** Plan §11 question 3 found that "*infrastructure* was wrong because infrastructure does not build itself". Absorbing audit into infrastructure hid three days of work through two re-baselines, and hid them in a row of §2.4 that said *absorbed*. Filing mail dispatch under Environment Setup does the same thing to it: those 2 days were estimated for a development environment, not for a Celery task, template rendering, and delivery-failure handling, and nothing would recost them.

There is also a substantive ground. **Delivery failure is a domain question, not a configuration question.** If a password reset email does not send, does the reset fail, does the user learn of it, does it retry, is it recorded? Environment Setup has nowhere to record that answer. A module does — and this ADR does, at decisions 3 to 5.

### Why the surface sits at 11 and not earlier

SRS §3.4 separates the channels by purpose: "Email notifications for approvals, onboarding, password reset, and payroll-related communication. In-app notifications for pending tasks and request updates."

Onboarding and payroll communication are therefore **email-only**: they consume mail dispatch at module 2 and never touch the in-app surface. HRMS-FR-033 is a pending task and HRMS-FR-034 is a request update, so the in-app surface exists for those two, and their consumers are the §4.3 self-service modules and Leave Management. Recruitment, per the Context above, consumes neither.

The first of those consumers is Employee Self-Service. The surface precedes it.

**A candidate for placing it at module 4 was considered and rejected.** RBAC/IAM carries two approval flows already: a privileged role grant requires an approver who is not the requester (ADR-0010), and HRMS-NFR-024 requires that recovery of a lost second factor be approved by a user who does not administer credentials. Those approvers hold pending tasks. Were they notified in-app, the surface's first consumer would be module 4 and the surface would move eight positions.

**No requirement asks for it.** HRMS-FR-033 speaks of notifying *managers*, and a role-grant approver is not a manager — reading it otherwise is the same substitution that produced the module 8 placement, performed in the opposite direction. Notifying approvers is a scope addition against an SRS whose scope has held since 2026-05-21, and §7.4 of the plan is substantially about uncosted work arriving late.

The rejection has a cost, and it is recorded as a deployment condition rather than absorbed. See Consequences.

### Delivery semantics

**Failures do not belong in the audit log.** `CONTEXT.md` fixes that store's contents as the five categories of HRMS-NFR-022 — login attempts, record changes, payroll actions, approvals, permission changes — together with HRMS-NFR-024's second-factor events. Email delivery failure is in none of them. Admitting it would widen a store whose immutability rests on the `INSERT`/`SELECT`-only grant at `docs/07-iam-rbac.md` §7.3, and would mix operational telemetry into a security trail. Application logs carry it.

**The action does not depend on the send.** An approval that rolls back because SMTP was unavailable is a worse system than one whose manager finds the pending request in the in-app feed. This is a second reason the surface matters independently of the channel: **in-app is the durable record of a pending task; email is the nudge.**

**Password reset must not become an enumeration oracle.** A response that varies with whether the address exists, or with whether the mail sent, tells an unauthenticated caller which accounts exist. The response is therefore uniform, and the reset flow cannot surface "we could not email you". This is a security property, not a UX preference, and its cost is recorded below.

### The names

"Notification transport" was the working name for the module at position 2 and it was wrong. **Password reset is not a notification.** Nobody is being informed that something happened which concerns them; they asked for a link. SRS §3.3 draws exactly this distinction with its conjunction, and the SRS is the more careful of the two sentences.

The shared capability at module 2 is *sending email*. Notification is one of its consumers, not its identity. Under the rejected name, a reader would reasonably ask why "notification transport" sits nine modules before Notification and the answer would sound like an evasion. Under the chosen one there is no puzzle to answer.

## Consequences

**Positive**

- The build order satisfies the provider-precedes-consumer rule for the first time with respect to email. Password reset in module 3 has a channel; under the v1.3 order it would have had none until module 8.
- The requirement assignment now follows the SRS's own section structure rather than a paraphrase of it. HRMS-FR-033 and HRMS-FR-034 sit with the §4.3 modules that raise them.
- Delivery failure has an owner and a recorded answer, which it did not have under either the module-8 placement or an Environment Setup absorption.
- The audit log's categories are unchanged, and its immutability grant is untouched.
- The naming makes the nine-position gap between modules 2 and 11 self-explaining, which is the failure mode this record exists to prevent.

**Negative**

- **Most module numbers change for the second time on 2026-07-15; M1, M9, and M10 retain their numbers, and M20 is new.** Audit's renumbering at v1.3 displaced eighteen modules by one; this displaces them again. Audit remains module 1 — mail dispatch is not a module Audit consumes, so the claim at plan §6.1 that nothing precedes Audit is untouched.
- **The estimate rises from 1.5 days to 4, and the 1.5 cannot be split into the 4.** It was never an estimate of these two things; it costed a module placed on a reason that does not hold. Both figures are new, made on 2026-07-15, with no completed work to calibrate against, for a boundary decided the same day. Plan §7.4's qualification applies to them in full and with more force than to the estimates it was written about.
- **The baseline moves from 81 working days to 83.5, and the margin from 4 days to 1.5.** Earliest finish moves from 2026-11-04 to 2026-11-09. The committed end date of 2026-11-10 is unchanged and **was not re-confirmed when this decision was taken**; plan §11 question 9 records why a confirmation given in the same breath as a change is worth little. Plan §11 question 4 observes that the working calendar is unknown and that public holidays inside the window consume the margin. **Two now suffice where four did before.**
- **Role-grant approvers are not notified.** The grant stalls until someone thinks to look. This is fail-closed and benign: the failure direction is that privilege is *not* granted.
- **Second-factor recovery approvers are not notified, and this one has teeth.** HRMS-NFR-024 makes the second factor unresettable by any administering role — the property that closed the HRMS-NFR-019 gap. A Payroll Officer who loses their second factor is therefore locked out, and the only route back is an approver who does not administer credentials and whom nothing has told. Until a human notices, **payroll cannot run**, against an HRMS-NFR-005 elapsed-time bound. The security property bought on 2026-07-15 for 10 days has an availability cost, and this is where it falls. The 4 days §7.1 allots the recovery flow buy the mechanism, not the procedure. **The recovery approver must be reachable out-of-band and the organisation must have a procedure for it; the system will not tell them.** This is a deployment condition of the same species as the holder of `iam.approve_role_grant` (ADR-0010, `CONTEXT.md`), and it is recorded there.
- **A password reset that fails to send fails silently**, by construction. The user sees the same response as on success and has no route back through the system. Recovery is a support path — and plan §11 questions 6 and 7 establish that there is no support desk, no trained HR staff, and no organisation (TBD-001). The support path is precisely as real as this system's users, which is to say it is a deployment assumption and not a mechanism.
- Notifying approvers, should it be wanted, is an SRS revision rather than a design adjustment. It was declined here on scope grounds, not on merit.

## Related

- ADR-0006 — Celery and Redis for background work. Mail dispatch is a consumer; this ADR does not choose the broker.
- ADR-0010 — role model. Its privileged-grant approver is one of the two approvers left unnotified above.
- `docs/02-project-plan.md` §6.1, §7.1, §11 question 2 — the placement this record decides, and the estimates it moves.
- `docs/04-system-architecture.md` — records the assignment at M2; it does not reopen it.
- `CONTEXT.md` — the glossary entries for mail dispatch and notification, and the deployment conditions arising here.
