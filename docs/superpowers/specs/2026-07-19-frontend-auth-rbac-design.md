# Frontend Auth + RBAC/IAM Module — Design

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Status | Approved by owner (John Kessie), 2026-07-19 |
| Scope | First module of the 14-module frontend implementation batch (plan v1.10, DOC-011/012) |

## 1. Context

Per `docs/02-project-plan.md` §6.1, module completion requires a client interface; modules 1–17's backend is fully merged but none has one. This is the first of 14 retrofits. Construction order is unfixed by the plan (DOC-011's own note); owner confirmed starting with **Authentication (module 3) + RBAC/IAM (module 4)**, since every other module's screens need the session/permission gate this provides. Compensation & Benefits (M15) and Payroll (M16) remain out of the 14-module batch — owner-confirmed deliberate exclusion, 2026-07-19.

A `frontend/` directory already exists (INFRA-001, PR #25) but is only a default Vite+React+TS health-check placeholder (`App.tsx` fetches `/api/health/`) — no Ant Design, no TanStack Query, no routing, no app structure. This module replaces it wholesale; nothing in it is preserved.

Tech stack is fixed, not open: React SPA, Vite, TypeScript, Ant Design, TanStack Query (`docs/03-tech-stack.md`), served under one origin with the Django/DRF backend via Caddy. Session-cookie authentication with CSRF verification (ADR-0004, `docs/03-tech-stack.md` §8.1) — no bearer token, no JWT.

Routing library is not fixed by any doc. Owner chose **React Router** over TanStack Router for this project (lower risk for a solo-maintained first frontend module; simpler Ant Design `Menu`/`Layout` integration).

MFA (second-factor) screens are explicitly deferred to a follow-up module — owner-confirmed 2026-07-19 — since Auth+RBAC's core session/permission gate does not require them to exist first.

## 2. Backend contract this module builds against

Per `docs/06-api-contracts.md` §4.2 (Module 3 — Authentication) and §4.9 (Module 4 — RBAC/IAM), and `backend/accounts/urls.py`/`views.py`:

- `GET /api/auth/csrf/` — bootstraps CSRF cookie
- `POST /api/auth/login/` — body `email`, `password`; uniform failure response
- `POST /api/auth/logout/` — invalidates server-side session
- `GET /api/auth/me/` — caller's `user_account` fields, derived role set, assigned groups
- `POST /api/auth/password-reset/` — body `email`; uniform response
- `POST /api/auth/password-reset/confirm/`
- `GET, POST, PATCH /api/users/` — System Administrator only
- `POST /api/role-grant-requests/` — any authenticated user
- `POST /api/role-grant-requests/{id}/decide/` — holder of `iam.approve_role_grant`, not the requester

Out of scope for this module (deferred): `/api/auth/second-factor/` and `/api/auth/second-factor/recovery-requests/` (+`/decide/`).

Every state-changing request requires the CSRF token (`X-CSRFToken` header, from the CSRF cookie) per §2.2. Error responses use the uniform envelope `{"error": {"code", "message", "fields"}}` (§2.7). Collections are paginated (`count`/`next`/`previous`/`results`, page size 25) per §2.3. A `401` means unauthenticated; `403` means authenticated but lacking permission; `404` means the object exists but falls outside the caller's visibility rule (§2.2, deny-by-default).

## 3. App shell structure

```
frontend/src/
  api/          # typed fetch client: one function per endpoint, CSRF header injection,
                 # uniform error-envelope parsing
  auth/         # AuthContext (populated from /auth/me/), ProtectedRoute, login/logout logic
  layout/       # AppLayout (Ant Design Layout/Menu), rendered only when authenticated
  modules/
    auth/       # LoginPage, PasswordResetPage
    rbac/       # UserManagementPage, RoleGrantRequestsPage
  routes.tsx    # React Router route tree
  App.tsx       # QueryClientProvider + RouterProvider root
```

The existing placeholder files (`App.tsx`, `App.css`) are replaced, not extended. `index.html`, `vite.config.ts`, `tsconfig*.json`, and the Docker/Caddy build wiring from INFRA-001 are unaffected — this module adds dependencies (`antd`, `@tanstack/react-query`, `react-router-dom`) and application code only.

## 4. Data flow & session handling

- On app load: `GET /api/auth/csrf/` (sets CSRF cookie), then `GET /api/auth/me/` via TanStack Query. `401` → render `/login`. Success → populate `AuthContext` (user, derived roles, permissions) and render `AppLayout` around the matched route.
- `LoginPage` submits `POST /api/auth/login/`; on success, invalidate/refetch the `/auth/me/` query and redirect to `/`.
- `AppLayout`'s logout action calls `POST /api/auth/logout/`, clears the TanStack Query cache, and redirects to `/login`.
- The API client centralizes CSRF header injection for every `POST`/`PATCH`/`PUT`/`DELETE` — individual screens never read the CSRF cookie directly.
- `ProtectedRoute` wraps every route except `/login` and `/password-reset`; unauthenticated access redirects to `/login`. `/users` additionally requires the System Administrator role from `AuthContext`; `/role-grant-requests` is reachable by any authenticated user per §4.9, with the decide action visually gated to eligible approvers (the backend enforces this regardless — the frontend check is UX, not the security boundary).
- A `401` on any authenticated request (session expiry mid-use) triggers a global redirect-to-login via the API client's response interceptor.

## 5. Screens in this module

1. **LoginPage** — email/password form → `POST /api/auth/login/`. Uniform error display (no "account not found" vs "wrong password" distinction, matching the backend's own uniform-response design).
2. **PasswordResetPage** — request form (`POST /api/auth/password-reset/`) and confirm form (`POST /api/auth/password-reset/confirm/`), uniform response messaging matching backend behavior.
3. **Landing/home page** (`/`) — placeholder only: "Welcome, {name}" plus a role/permission summary read from `/auth/me/`. Does not reach into Dashboard's (module 14) own screen, which is a separate, later batch item.
4. **UserManagementPage** (`/users`) — Ant Design `Table` over `GET /api/users/` (paginated per §2.3), create/edit via `Modal` + `Form` against `POST`/`PATCH /api/users/`. System-Administrator-only route.
5. **RoleGrantRequestsPage** (`/role-grant-requests`) — list of the caller's own requests plus requests awaiting their decision; `Form` to raise a request (`POST /api/role-grant-requests/`); approve/refuse action (`POST /api/role-grant-requests/{id}/decide/`) shown only to eligible approvers.

## 6. Error handling

The API client maps the uniform error envelope (§2.7) to Ant Design `Form` field errors (`fields`) and `message.error()` toasts (`message`) uniformly across every screen — no screen hand-rolls error parsing. `403`/`404` on a direct navigation (not a form submission) render an Ant Design `Result` component inline rather than crashing the route. `401` is handled globally (see §4), not per-screen.

## 7. Testing

- Vitest + React Testing Library: form validation, `AuthContext`/`ProtectedRoute` gating logic, API client's CSRF-injection and error-envelope-mapping behavior (mocked responses).
- No backend test changes — this module is a pure consumer of already-merged, already-tested endpoints.
- Manual E2E verification against the live Compose stack before the module is called done: login, logout, session persistence across a page reload, password-reset request+confirm round trip, role-grant request → decide (both approve and refuse paths), user create/edit as System Administrator. Matches the E2E-verification bar every backend module in this project has been held to.

## 8. Corrections found during plan-writing (2026-07-19)

Checked against the actual backend code (`backend/accounts/views.py`, `accounts/serializers.py`, `iam/views.py`, `iam/serializers.py`, `iam/urls.py`) rather than trusting `docs/06-api-contracts.md` §4.2/§4.9 alone:

- **`GET /api/role-grant-requests/` does not exist.** `iam/urls.py` wires only `POST /api/role-grant-requests/` (create) and `POST /api/role-grant-requests/{id}/decide/`. The contract's "approver sees requests awaiting their decision" read surface was never built. Owner-confirmed 2026-07-19: this module ships the create form and a decide-by-ID form only (the decider enters/selects an ID they already know, e.g. from a notification); it does not build a list view. A backend follow-up issue to add the missing `GET` is opened separately, out of this module's scope.
- **`/api/users/` and `/api/users/{id}/` return a plain JSON array/object, not the paginated envelope** §2.3 describes for collections — `UserListCreateView.get` returns `Response(serializer.data)` directly. `UserManagementPage`'s table uses Ant Design's client-side pagination over the full array rather than a server-paginated `Table`.
- **`MeSerializer` fields are `id`, `email`, `groups`** (list of group names) — not the richer "derived role set... and assigned groups" the contract prose implies. `AuthContext` is typed against the actual shape: `{id, email, groups: string[], second_factor_enrollment_pending: boolean}`. There is no separate "permissions" list; role-based UI gating in this module derives from `groups` membership only (e.g. `groups.includes('System Administrator')`).
- **Login has three response shapes**, all still in scope since login itself is not deferred, only the MFA *enrollment/challenge screens* are: (1) normal success → `MeSerializer` data, session established; (2) `{...MeSerializer data, second_factor_enrollment_required: true}` → session established but pending (account has no active second factor yet); (3) `{second_factor_required: true}` (200, no session) → account has an active factor and the login request needs a `totp_code` this client cannot yet collect. This module's `LoginPage` handles (1) normally, and for (2)/(3) shows an explanatory message ("second-factor setup/verification isn't available in this client yet — contact your administrator") rather than crashing or silently retrying. No accounts currently have an enrolled factor (no enrollment UI has ever existed), so (3) is a defensive path, not an expected one, in this deployment's current state.
- **`UserAdminSerializer.fields`** are `id`, `email`, `is_active`, `groups` (read-only), `password` (write-only, optional), `created_at`, `updated_at` — `groups` is not settable through this endpoint (role assignment is exclusively through role-grant-requests, per the serializer's own docstring); `UserManagementPage`'s create/edit form only exposes `email`, `is_active`, `password`.

## 9. Explicitly out of scope for this module

- Second-factor (MFA) enrollment, recovery-request, and decide screens — deferred to a follow-up, per owner decision 2026-07-19. Note that Administrator and Payroll Officer accounts are not spec-compliant (HRMS-NFR-024) without MFA UI eventually existing; this is a tracked gap, not a closed one.
- Dashboard's own screen (module 14) — this module's landing page is a placeholder only.
- Any of the other 12 remaining frontend-batch modules (Departments, Employee Management, Reporting Structure, Recruitment, Onboarding, Notification, Employee/Manager Self-Service, Leave Management, Dashboard, Reports) or the excluded Compensation/Payroll pair.
