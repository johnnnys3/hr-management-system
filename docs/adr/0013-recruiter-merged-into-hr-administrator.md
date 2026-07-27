# ADR-0013: Recruiter role merged into HR Administrator

**Status:** Accepted
**Date:** 2026-07-27
**Amends:** ADR-0010
**Bears on:** TBD-010 (Exact user roles and permissions)

## Context

ADR-0010 established six assigned roles serving seven SRS user classes, with Recruiter serving §2.3.3 as its own role, separate from HR Administrator and HR Officer.

Recruiter is retired as of SRS v1.5 (`docs/01-srs.md` revision history). §2.3.3 is folded into §2.3.2's HR class, which ADR-0010 already served with two roles rather than one. This ADR records which of the two absorbs Recruiter's permissions, and what that choice costs and preserves.

## Decision

**Recruiter's permissions are absorbed by HR Administrator, not HR Officer.** No new role is created; the assigned-role count returns to five.

HR Officer was the more obvious target — it already holds read access to recruitment records (`docs/07-iam-rbac.md` §4.2) so that it can react to an accepted offer (HRMS-BR-013 conversion). It is rejected anyway, on the same separation-of-duties ground ADR-0010 used to split HR Administrator from HR Officer in the first place.

## Rationale

### The pipeline/creation split was already a fraud control, not an accident

Under ADR-0010, Recruiter could create and progress requisitions, candidates, interviews, and offers, but held no permission to create an employee record — only HR Officer (and, for status/payroll fields, HR Administrator with narrower access) could do that. A candidate's entire path from requisition to accepted offer therefore sat behind a different role than the one with the power to turn that offer into a real employee.

This is the same shape as the control ADR-0010 §2.4 documents for HR Administrator/HR Officer: one role defines the framework (pay grades), a different role performs the transaction against it (assigning an employee to a grade), so that no single account can both fabricate an entry and give it effect. Recruiter/HR Officer split the hiring pipeline from employee-record creation for the identical reason: no single account should be able to invent a candidate, walk them through the pipeline, and create the resulting employee, alone.

Merging Recruiter into HR Officer would have destroyed that control outright — HR Officer already creates employee records, so the merged role would hold both ends. Merging into HR Administrator preserves it: HR Administrator was already barred from employee-record creation (`docs/07-iam-rbac.md` §4.2's Employee records row — HR Administrator holds `R, U status` only, not `C`), for the same reason ADR-0010 gave. Absorbing Recruiter's recruitment C/R/U does not change that.

### A different gap opens, and is closed the same way ADR-0010 closed its analogous one

HR Administrator already held requisition-approval authority (`CanDecideRequisition`, `docs/07-iam-rbac.md` §4.2's "Requisition approval" row). It now also gains requisition *creation* (absorbed from Recruiter). Unlike the employee-record path, nothing structural stops the same HR Administrator account from creating a requisition and then approving that same requisition — a self-approval gap the prior Recruiter/HR-Administrator split closed structurally, by having a requisition's creator and its approver hold different roles.

This is not a new kind of problem. HRMS-FR-047/HRMS-BR-008 faced the identical shape for payroll finalisation, and `docs/07-iam-rbac.md` §4.4 closed it with one constraint that does not depend on role separation: **the approver must not be the user who initiated the run.** The same constraint is adopted here for requisitions: **an HR Administrator may not approve a requisition they created.** This is enforced at the request level, regardless of which roles a user holds, exactly as §4.4 enforces it for payroll. Implementation detail moves to `docs/07-iam-rbac.md` §4.2/§4.3 and the corresponding `CanDecideRequisition` check; it is not restated as a new SRS business rule, on the same precedent HRMS-BR-008 set — it is the general rule, applied to a second workflow, not a second rule.

### What is not revisited

ADR-0010's reasoning for keeping HR Administrator and HR Officer as two separate roles is unaffected — Recruiter's merge target is one of those two roles, not a reason to reconsider the split between them. Executive, Payroll Officer, System Administrator, and the two derived roles are untouched.

## Consequences

**Positive**

- Assigned-role count returns to five without reopening the ghost-employee-adjacent control ADR-0010's §2.4 split protects: an account able to fabricate a hire still cannot single-handedly turn it into an employee record.
- Grant administration is simpler by one role: one fewer group to grant, one fewer entry in `PRIVILEGED_ROLES` bookkeeping to reason about (Recruiter was never privileged; see Consequences below).
- The new self-approval risk on requisitions is closed by the same mechanism already proven for payroll finalisation, not a new mechanism invented for this change.

**Negative**

- HR Administrator's scope grows: it now creates and updates recruitment records it previously could only read. An organisation that valued Recruiter as a narrower, lower-trust role — e.g. a third-party or contract recruiter who should not see HR Administrator's other configuration authority (departments, job titles, pay grades, leave types) — loses that separation. There is no narrower role left to grant such a person; granting HR Administrator gives them all of it.
- The non-self-approval constraint on requisitions is new surface to implement and test; it did not previously need to exist because the two roles were structurally distinct.
- `backend/recruitment/permissions.py`'s `CanAccessJobRequisitions`, `CanDecideRequisition`, and `IsRecruiter` all name `RECRUITER` directly and must be updated together with the group's retirement — not a design concern, but the blast radius is not limited to `iam/roles.py`.

## Related

- ADR-0010 — role model this ADR amends. Six assigned roles becomes five.
- `docs/07-iam-rbac.md` §2.4 — the HR Administrator/HR Officer split this decision extends the same reasoning to.
- `docs/07-iam-rbac.md` §4.4 — the payroll self-approval constraint this decision's requisition constraint is modelled on.
