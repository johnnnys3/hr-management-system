# Frontend Handoff

**Date:** 2026-07-19
**Author:** John Kessie (via Claude)
**Status:** Resolved 2026-07-19 — owner chose deliberate re-baseline; see `docs/02-project-plan.md` v1.9 revision history and DOC-011

## Purpose

This document hands off the state of the frontend to whoever picks it up next (including a future session of this same agent). It is not a plan revision — it records what exists, what §6.1 of `docs/02-project-plan.md` says should exist, and the size of the gap between them. Resolving the gap (retroactive build vs. deliberate re-baseline) is a decision for the project owner, not made here.

## 1. What Actually Exists

`frontend/` is the Environment Setup scaffold only — `INFRA-001`, PR #25, merged 2026-07-17. It is unmodified Vite + React + TypeScript boilerplate:

```text
frontend/src/App.tsx      — default Vite starter component
frontend/src/App.css      — default Vite starter styles
frontend/src/main.tsx     — default entry point
frontend/index.html
```

No routing, no API client, no auth flow, no components tied to any HRMS module. `frontend/dist/` contains a built artifact of that same starter template. Package manifest confirms the tech-stack selection (Vite, React, TypeScript) but no feature dependencies (no Ant Design, no TanStack Query, no React Router) are installed yet, despite all three being named in `docs/03-tech-stack.md` §2.

## 2. What the Plan Says Should Exist

`docs/02-project-plan.md` §6.1 states, twice (lines 277 and 297 as of v1.8):

> "A module is complete when its models, service layer, API endpoints, visibility rule, permission tests, and **client interface** are done and its tests pass."

Per the current module build order (v1.8), thirteen modules are merged into `develop` as of PR #67 (2026-07-19):

| # | Module | Backend status | Client interface |
|---|---|---|---|
| 1 | Audit | Merged | Not built |
| 2 | Mail dispatch | Merged | N/A — sends email, no UI surface of its own |
| 3 | Authentication | Merged | Not built |
| 4 | RBAC/IAM | Merged | Not built |
| 5 | Departments | Merged | Not built |
| 6 | Employee Management | Merged | Not built |
| 7 | Reporting Structure | Merged | Not built |
| 8 | Recruitment | Merged | Not built |
| 9 | Onboarding | Merged | Not built |
| 10 | Notification | Merged | Not built |
| 11 | Employee Self-Service | Merged (verification-only, no new endpoints) | Not built |
| 12 | Manager Self-Service | Merged (verification-only, no new endpoints) | Not built |
| 13 | Leave Management | Merged | Not built |
| 14 | Dashboard | Merged (PR #69, `6db57e7`) | Not built |

Twelve modules with a genuine API surface (Mail dispatch excepted) have zero corresponding frontend code, plus Dashboard — thirteen in total. By §6.1's own completion rule, none of modules 1, 3–14 except module 2 are actually complete — they are backend-complete and merged, but not module-complete.

## 3. Why This Happened

Reconstructed from commit history, not confirmed with the project owner: development has proceeded API-first, module by module on `develop`, with each PR (AUDIT-001, AUTH-001, RBAC-001 … LEAVE-001) covering only models/service layer/endpoints/permission tests. No PR in the merged history touches `frontend/src`. The plan itself does not record a decision to defer frontend — this looks like an execution drift against §6.1 rather than a deliberate, documented re-scope. Contrast with how every other deviation in this project has been handled (Notification split, Dashboard move, module 11/12 rescoping): each got a dated entry in the plan's revision history with reasoning and owner confirmation. This one hasn't.

## 4. What the API Surface Currently Looks Like

For whoever builds the client interfaces, current URL-routed endpoint counts per app (from `backend/*/urls.py`, includes both list/detail routes and router-registered viewsets — not a 1:1 count of distinct resources):

- `accounts` (Authentication) — 10 routes
- `iam` (RBAC/IAM) — 5 routes
- `departments` — 5 routes
- `employees` (Employee Management + Self-Service surface) — 9 routes
- `reporting_structure` — 4 routes
- `recruitment` — 15 routes
- `onboarding` — 5 routes
- `notifications` — 3 routes
- `leave` — 9 routes
- `dashboard` — 2 routes
- `audit` — 2 routes
- `health` — 2 routes

`docs/06-api-contracts.md` is the authoritative API specification and should be read before building any client — it's the source of truth for request/response shapes, not the URL files.

## 5. Open Question for the Project Owner

Two ways to close this gap, and the choice isn't this document's to make:

1. **Retroactive build.** Go back through modules 1–13 in order and build the missing client interface for each, treating this as unfinished work rather than new work. Module numbering and estimates stay as-is; only actual effort spent was under-recorded.
2. **Deliberate re-baseline.** Formally amend `docs/02-project-plan.md` §6.1 to record that frontend was intentionally batched after backend (all 13+ modules), with a new estimate for the batch and owner confirmation — following the same pattern every other plan deviation has used (dated revision-history entry, reasoning, explicit confirmation).

Either is legitimate. What isn't: continuing to merge "module complete" PRs that don't meet §6.1's own bar without one of these two happening first.

**Resolved 2026-07-19: the project owner chose path 2, deliberate re-baseline.** `docs/02-project-plan.md` v1.9 (DOC-011) adds a 12-day frontend implementation batch line item to §7.1, inserted into §6.3's schedule immediately after Dashboard and before Compensation and Benefits; the end date moves from 2026-11-10 to 2026-12-01. See that document's v1.9 revision-history row for the full accounting.

## 6. Immediate Next Step

Construction order for the thirteen retrofits is not fixed by the plan revision — start from Authentication (module 3) and RBAC/IAM (module 4): they are the first modules whose client interface every self-service and manager-facing screen downstream will depend on for session handling and permission gating, and both are already backend-complete.
