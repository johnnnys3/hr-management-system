# Role Grant / Access Redesign — Design

| Field | Value |
|---|---|
| Date | 2026-07-27 |
| Status | Approved by owner (John Kessie), 2026-07-27 |
| Scope | Follow-up UX request: "the role grant request can be more user friendly — right now it looks too technical," escalated by the owner to "I even think we should remove the role grant request thing and redo in a more intuitive and user friendly [way]." |

## 1. Context

The current `/role-grant-requests` page (`frontend/src/modules/rbac/RoleGrantRequestsPage.tsx`) exposes the raw mechanics of the underlying model: a "Subject user ID" and "Role ID" as bare `InputNumber` fields, a table of numeric `requester`/`subject`/`role` IDs, and a plain status `Tag`. It is also shown, unconditionally, to every authenticated user regardless of role — an artifact of the side-navbar redesign (`docs/superpowers/specs/2026-07-26-side-navbar-design.md` §4), which kept it "shown to all today — kept as-is" as a deliberate non-goal at the time.

The owner's escalation ("remove... and redo") was checked against `docs/07-iam-rbac.md` §7.3 and ADR-0010 before any redesign was scoped: `role_grant_request` is not a UI convenience, it is the mechanism enforcing two database-level constraints — self-grant is refused, and a privileged role's grant takes effect only on approval by an `iam.approve_role_grant` holder who is not the requester. This closes a specific privilege-escalation route against HRMS-NFR-019. Removing the mechanism would reopen that gap. Confirmed with the owner: the request is a UI/UX redesign around the same mechanism, not removal of it.

Two real (not cosmetic) decisions came out of clarifying this with the owner:

1. **Who may raise a request** narrows from "any authenticated user" (current, documented explicitly in `RoleGrantRequestCreateView`'s docstring) to **System Administrator only**.
2. **Who approves** narrows from "deployment-configured, unspecified" (current open item, `docs/07-iam-rbac.md` §8) to **HR Administrator by default**, closing that open item. HR Administrator already satisfies the constraint the approver must meet — it's already in `SECOND_FACTOR_REQUIRED_GROUPS` (`backend/accounts/models.py`), so this doesn't reopen the HRMS-NFR-024 gap `docs/07-iam-rbac.md` §7.3 closed. It is also, per that same section, not System Administrator — the constraint that requester and approver are held to genuinely distinct roles is preserved, not just distinct accounts.

## 2. Non-goals

- No change to the self-grant `CHECK` constraint, the distinct-approver enforcement, or any other part of `docs/07-iam-rbac.md` §7.3's core guarantee.
- No change to Recruiter's auto-approve behavior (the one non-privileged assigned role).
- Not building a generic "assign any Django permission" tool. This stays scoped to the six existing assigned roles (`iam.roles.ASSIGNED_ROLES`).
- Not adding a name field to `User` or otherwise merging the User/Employee entities (`CONTEXT.md`'s "avoid conflating User and Employee" holds) — where an Employee is linked, its name is *joined in for display*, not copied onto `User`.

## 3. Backend access control changes

- `RoleGrantRequestCreateView.post` (`backend/iam/views.py`): permission narrows from `IsFullyAuthenticated` to System-Administrator-only, reusing the existing `audit.permissions.IsSystemAdministrator` (already re-exported via `iam.permissions`, used by `/api/users/`). Docstring updated to match — it currently states "any authenticated user may raise a request," which becomes false.
- New `iam` migration grants `iam.approve_role_grant` to the HR Administrator group, following the exact pattern of `iam/migrations/0002_create_assigned_role_groups.py`: hardcoded group/permission names (not imported from `iam.roles`, so a later rename of that constant doesn't silently rewrite what this migration does), no-op reverse (undoing this migration must not retroactively strip a permission that approvals have already been made under).
- `docs/07-iam-rbac.md` amended: §7.3's "any authenticated user may raise a request" becomes "System Administrator"; §8's `iam.approve_role_grant` holder row moves from **open item** ("deferred to deployment... requires an operating organisation, TBD-001") to **resolved: HR Administrator by default**. Gets a proper revision-history row, same convention as every other change to that document.
- `docs/06-api-contracts.md` §4.9 updated to state the narrowed permission on `POST /api/role-grant-requests/`.

## 4. Readable data, not raw IDs

- `/api/users/` (System-Administrator-only; permission unchanged) gains the linked employee's name where one exists (`user.employee.first_name`/`last_name`, via the existing `User.employee` one-to-one), falling back to email-only when no Employee is linked — matching `CONTEXT.md`'s "not every user is an employee." Additive field on the existing serializer, no new endpoint.
- `RoleGrantRequestSerializer` (`backend/iam/serializers.py`) gains `requester_email`, `subject_email`, `subject_name` (nullable), and `role_name` alongside the existing numeric `requester`/`subject`/`role` fields. Additive — nothing existing is removed, so nothing else reading the raw IDs breaks.

## 5. Frontend navigation changes

In [navGroups.ts](frontend/src/layout/navGroups.ts), the single "Role Grant Requests" item (Admin group, shown unconditionally to everyone) is replaced by two role-gated items:

- **"Grant Access"** — visible only to System Administrator.
- **"Access Approvals"** — visible only to accounts that can approve, gated on `me.groups.includes('HR Administrator')`. The frontend has no general mechanism for checking a specific Django permission (`iam.approve_role_grant`) client-side, so this gates on group membership as a proxy for the permission — correct given §3 defaults that permission to the HR Administrator group, and noted with a code comment as the coupling to revisit if the deployment-configured model is ever exercised differently in a real deployment.

A plain Employee, Recruiter, Payroll Officer, or Executive sees neither link — resolving the original complaint that the feature was "everywhere."

## 6. Page redesign

Single route, `/access` (replacing `/role-grant-requests`), containing two independently-gated sections — a System Administrator who is *not* also an HR Administrator sees only the first, and vice versa; an account holding both group memberships sees both:

**Grant Access** (System Administrator only):
- A searchable employee picker (Ant Design `Select` with search, backed by the enriched `/api/users/` from §4) showing "Jane Doe (jane@example.com)" or "jane@example.com" alone when unlinked — replaces the raw "Subject user ID" `InputNumber`.
- A role picker with plain-language labels and one-line descriptions, replacing the raw "Role ID" `InputNumber`:

  | Role | Description |
  |---|---|
  | System Administrator | Manage accounts, roles, and system configuration |
  | HR Administrator | Manage employee records, departments, and HR configuration |
  | HR Officer | Handle day-to-day HR operations and onboarding |
  | Recruiter | Manage job postings and candidates *(granted immediately — no approval needed)* |
  | Payroll Officer | Process payroll and compensation |
  | Executive | View organization-wide reports |

- On submit: "Request submitted — awaiting approval from an HR Administrator" for the five privileged roles, or "Recruiter access granted immediately" for the one non-privileged case — replacing the current bare "Request #14 submitted."

**Access Approvals** (HR Administrator only):
- Pending requests read as a sentence, not a table of IDs: "**System Administrator** requests **Recruiter** access for **Jane Doe (jane@example.com)**" with **Approve**/**Decline** buttons.
- Decided requests (approved/declined) shown below as history, same plain-language rendering.

Both sections consume the existing `createRoleGrantRequest`/`decideRoleGrantRequest`/`listRoleGrantRequests` functions in [rbac.ts](frontend/src/api/rbac.ts) unchanged in shape — only the new serializer fields from §4 and two new components (`GrantAccessForm`, `AccessApprovalsQueue`) replacing the current `RaiseRequestForm`/`RequestsTable`.

## 7. Testing

**Backend:**
- Permission test: a non-System-Administrator gets `403` from `POST /api/role-grant-requests/` (currently any authenticated user succeeds — this test's expected status is the one real behavior change in this spec).
- Migration test (or a post-migrate data check): HR Administrator holds `iam.approve_role_grant` after migrating.
- Serializer tests: `RoleGrantRequestSerializer`'s new readable fields, `/api/users/`'s employee-name join including the no-linked-employee fallback.

**Frontend:**
- Nav visibility per role, extending the existing `navGroups.test.ts`/`AppLayout.test.tsx` pattern: System Administrator sees "Grant Access" only; HR Administrator sees "Access Approvals" only; an account holding both sees both; every other role/plain Employee sees neither.
- `GrantAccessForm` rendering: employee picker options, role descriptions, submit confirmation copy (privileged vs. Recruiter).
- `AccessApprovalsQueue` rendering: pending-request sentence construction from the enriched fields, approve/decline actions, decided-request history section.
