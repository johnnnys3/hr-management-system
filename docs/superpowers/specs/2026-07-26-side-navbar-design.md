# Side Navigation Bar — Design

| Field | Value |
|---|---|
| Date | 2026-07-26 |
| Status | Approved by owner (John Kessie), 2026-07-26 |
| Scope | First of three sequenced UX pieces requested by owner: (1) side navbar, (2) email + SMS notification channels, (3) MFA method choice for administrators/payroll officers. This spec covers (1) only. |

## 1. Context

The app shell (`frontend/src/layout/AppLayout.tsx`) currently renders a single horizontal top header: brand wordmark, a flat row of role-gated nav links (built from `me.groups`/`me.is_manager` via `AuthContext`), and a logout control. The owner asked for a side navbar and, generally, for the system to be more user-friendly.

Two related asks came up during brainstorming and were explicitly deferred, not folded into this spec:

- **Role-by-role feature audit** (missing features per role, and trimming features that shouldn't be there) — a separate follow-up spec, not a layout change.
- **Email + SMS notifications** and **MFA method choice** — sequenced after this spec, per owner decision 2026-07-26.

Quick research into comparable systems (BambooHR, Workday, Gusto — see Sources) surfaced two recurring patterns that shaped this design: role-scoped sidebar content (already true of this app) and category grouping once the item list grows past ~8–10 entries, which several of this app's roles (System Administrator, Payroll Officer, HR Administrator) already do.

## 2. Non-goals

- No change to routing, RBAC/visibility logic, `AuthContext`, or `MinimalLayout` (pre-auth pages: login, password reset).
- No change to which roles see which nav items — the existing gating conditions in `AppLayout.tsx` are carried over unchanged, only regrouped.
- No new pages, no new permissions, no backend changes.
- Grouping is fixed, not user-customizable (no drag-to-reorder, no per-user pinned items).

## 3. Layout structure

Replace the current `Layout.Header`-only shell with:

- **Top bar** (slim, ~56px): "HRMS" wordmark (left), notification bell — existing unread-count query (`listNotifications({ read_at__isnull: true })`, 30s poll) rendered as an icon with a badge instead of today's text link — and a user menu (avatar/name dropdown containing "Log out") on the right.
- **Sider** (`Layout.Sider`, left, full height below the top bar): Ant Design `Menu`, `mode="inline"`. Expanded width ~220px; collapsed to a ~64px icon rail via Ant's built-in collapse `trigger`. Collapse state persists in `localStorage` (key: `hrms.sidebar.collapsed`) so it survives reload and navigation.
- **Content**: unchanged `Outlet` region, padding adjusted to sit beside the Sider instead of below the old header.

`selectedKeys={[location.pathname]}` drives active-item highlight, replacing today's manual `active` prop comparison in `NavLink`.

## 4. Grouped navigation items

Items are grouped into four sections (Ant `Menu` `type: 'group'`), each rendered only if it has at least one visible item for the current user — no empty group headers:

| Group | Items (existing route → existing gating condition, unchanged) |
|---|---|
| **My Work** | Dashboard (all) · Notifications, badge (all) · Leave (all) · My Profile (all) |
| **People** | My Team (`me.is_manager`) · Employees (HR Administrator, HR Officer) · Departments (HR Administrator, HR Officer, Recruiter, Payroll Officer) · Recruitment (Recruiter, HR Administrator, HR Officer) · Onboarding (HR Officer) |
| **Payroll & Compensation** | Compensation (HR Administrator, HR Officer, Payroll Officer) · Payroll (Payroll Officer) · Reports (HR Administrator, Payroll Officer, Executive, or `me.is_manager`) |
| **Admin** | Users (System Administrator) · Audit Log (System Administrator) · Role Grant Requests (all — unchanged from today's ungated placement) |

Each group's item list, and every gating condition, is copied verbatim from the current `items` array in `AppLayout.tsx` (lines 43–73) — this spec reorganizes presentation only.

### Icons

One `@ant-design/icons` per item:

Dashboard → `DashboardOutlined` · Notifications → `BellOutlined` · Leave → `CalendarOutlined` · My Profile → `UserOutlined` · My Team → `TeamOutlined` · Employees → `IdcardOutlined` · Departments → `ApartmentOutlined` · Recruitment → `SolutionOutlined` · Onboarding → `RocketOutlined` · Compensation → `DollarOutlined` · Payroll → `WalletOutlined` · Reports → `BarChartOutlined` · Users → `UsergroupAddOutlined` · Audit Log → `FileSearchOutlined` · Role Grant Requests → `SafetyCertificateOutlined`.

### Notification badge

Currently an inline badge on the text link; moves to a trailing badge on the "Notifications" `Menu.Item`. Same query, same count, same 30s refetch — only the rendering target changes.

## 5. Testing

No test file exists for `AppLayout.tsx` today. Add one asserting behavior parity with the current implementation:

- For a representative fixture per role (System Administrator, HR Administrator, HR Officer, Recruiter, Payroll Officer, Executive, plain Employee, Employee who is also a manager), the set of visible nav items and groups matches exactly what today's flat list would show for that role — same items, same conditions, just grouped.
- A group with zero visible items for a given role does not render its header.
- Collapse toggle updates `localStorage` and re-renders the Sider at the collapsed width.
- Notification badge count and 30s poll behavior are unchanged.

## 6. Out of scope for this spec (deferred, tracked separately)

- Role-by-role feature gap audit (missing + unnecessary features per role).
- Email + SMS notification delivery channels.
- MFA method choice (email OTP vs. authenticator app) for administrators/payroll officers, scoped per `HRMS-NFR-024` — explicitly **not** extended to all roles (owner decision 2026-07-26).

## Sources

- [6 Best BambooHR Competitors & Alternatives](https://gusto.com/resources/guides/best-bamboohr-competitors)
- [BambooHR Review 2025](https://www.linktly.com/hr-software/bamboohr-review/)
- [BambooHR vs Workday: 10 Key Differences to Know in 2026](https://www.edstellar.com/blog/bamboohr-vs-workday)
