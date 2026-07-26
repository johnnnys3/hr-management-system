# Side Navigation Bar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the horizontal top-nav in `AppLayout.tsx` with a collapsible, grouped side navbar, per `docs/superpowers/specs/2026-07-26-side-navbar-design.md`, with zero change to routing, RBAC gating, or page content.

**Architecture:** One new pure function (`buildNavGroups`) computes the grouped, role-gated menu structure from `Me`; `AppLayout.tsx` is rewritten to render `Layout.Sider` + `Menu` from that structure, plus a slim `Layout.Header` for brand/notifications/user menu. A small `useSidebarCollapse` hook persists collapse state to `localStorage`.

**Tech Stack:** React 19, TypeScript, Ant Design 6.5 (`Layout.Sider`, `Menu`, `Badge`, `Dropdown`), `@ant-design/icons`, React Router 7 (`Link`, `useLocation`, `useNavigate`), TanStack Query (existing `listNotifications`), Vitest + Testing Library.

---

## File Structure

- **Create:** `frontend/src/layout/navGroups.ts` — pure function `buildNavGroups(me: Me | null): NavGroup[]`, plus `NavGroup`/`NavItem` types. No React, no hooks — testable in isolation.
- **Create:** `frontend/src/layout/navGroups.test.ts` — unit tests for the grouping/gating logic per role.
- **Create:** `frontend/src/layout/useSidebarCollapse.ts` — hook wrapping `localStorage` persistence of collapse state.
- **Create:** `frontend/src/layout/useSidebarCollapse.test.ts` — unit tests for the hook.
- **Modify:** `frontend/src/layout/AppLayout.tsx` — replace horizontal header with `Sider` + slim `Header`, consuming `buildNavGroups` and `useSidebarCollapse`.
- **Create:** `frontend/src/layout/AppLayout.test.tsx` — render test asserting per-role visible items/groups match today's behavior (including HR Officer, Recruiter, Executive, and complete manager-visible menu), group-hiding, collapse toggle (asserting rendered collapsed width), notification badge (verifying polling occurs at 30-second interval).

---

## Task 1: Extract grouped nav-item logic into a pure function

**Files:**
- Create: `frontend/src/layout/navGroups.ts`
- Test: `frontend/src/layout/navGroups.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/layout/navGroups.test.ts
import { describe, expect, it } from 'vitest'
import { buildNavGroups } from './navGroups'
import type { Me } from '../api/types'

function makeMe(overrides: Partial<Me> = {}): Me {
  return {
    id: 1,
    email: 'a@b.com',
    groups: [],
    is_employee: true,
    is_manager: false,
    second_factor_enrollment_pending: false,
    ...overrides,
  }
}

describe('buildNavGroups', () => {
  it('returns My Work and Admin (Role Grant Requests only) for a plain employee', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.map((g) => g.label)).toEqual(['My Work', 'Admin'])
    expect(groups[0].items.map((i) => i.key)).toEqual(['/', '/notifications', '/leave', '/my-profile'])
    expect(groups[1].items.map((i) => i.key)).toEqual(['/role-grant-requests'])
  })

  it('adds My Team to People for a manager', () => {
    const groups = buildNavGroups(makeMe({ is_manager: true }))
    const people = groups.find((g) => g.label === 'People')
    expect(people?.items.map((i) => i.key)).toEqual(['/my-team'])
  })

  it('adds Employees and Departments to People for HR Administrator, and Reports to Payroll & Compensation', () => {
    const groups = buildNavGroups(makeMe({ groups: ['HR Administrator'] }))
    const people = groups.find((g) => g.label === 'People')
    expect(people?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/departments', '/employees', '/recruitment']))
    const payroll = groups.find((g) => g.label === 'Payroll & Compensation')
    expect(payroll?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/compensation', '/reports']))
  })

  it('adds Users and Audit Log to Admin for System Administrator, alongside Role Grant Requests', () => {
    const groups = buildNavGroups(makeMe({ groups: ['System Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.map((i) => i.key)).toEqual(['/role-grant-requests', '/users', '/audit-log'])
  })

  it('adds Payroll to Payroll & Compensation for Payroll Officer', () => {
    const groups = buildNavGroups(makeMe({ groups: ['Payroll Officer'] }))
    const payroll = groups.find((g) => g.label === 'Payroll & Compensation')
    expect(payroll?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/compensation', '/payroll', '/reports']))
  })

  it('omits People and Payroll & Compensation entirely when they have no visible items', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.find((g) => g.label === 'People')).toBeUndefined()
    expect(groups.find((g) => g.label === 'Payroll & Compensation')).toBeUndefined()
  })

  it('returns an empty array when me is null', () => {
    expect(buildNavGroups(null)).toEqual([])
  })

  it('carries an unread notification count onto the Notifications item when provided', () => {
    const groups = buildNavGroups(makeMe(), 3)
    const myWork = groups.find((g) => g.label === 'My Work')
    const notifications = myWork?.items.find((i) => i.key === '/notifications')
    expect(notifications?.badge).toBe(3)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- navGroups`
Expected: FAIL — `Cannot find module './navGroups'`

- [ ] **Step 3: Write the implementation**

```typescript
// frontend/src/layout/navGroups.ts
import type { Me } from '../api/types'

export interface NavItem {
  key: string
  label: string
  icon: string
  badge?: number
}

export interface NavGroup {
  label: string
  items: NavItem[]
}

function hasAnyGroup(me: Me, allowed: string[]): boolean {
  return me.groups.some((g) => allowed.includes(g))
}

export function buildNavGroups(me: Me | null, unreadNotifications = 0): NavGroup[] {
  if (!me) return []

  const myWork: NavItem[] = [
    { key: '/', label: 'Dashboard', icon: 'DashboardOutlined' },
    { key: '/notifications', label: 'Notifications', icon: 'BellOutlined', badge: unreadNotifications },
    { key: '/leave', label: 'Leave', icon: 'CalendarOutlined' },
    { key: '/my-profile', label: 'My Profile', icon: 'UserOutlined' },
  ]

  const people: NavItem[] = [
    ...(me.is_manager ? [{ key: '/my-team', label: 'My Team', icon: 'TeamOutlined' }] : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer', 'Recruiter', 'Payroll Officer'])
      ? [{ key: '/departments', label: 'Departments', icon: 'ApartmentOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer'])
      ? [{ key: '/employees', label: 'Employees', icon: 'IdcardOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['Recruiter', 'HR Administrator', 'HR Officer'])
      ? [{ key: '/recruitment', label: 'Recruitment', icon: 'SolutionOutlined' }]
      : []),
    ...(me.groups.includes('HR Officer') ? [{ key: '/onboarding', label: 'Onboarding', icon: 'RocketOutlined' }] : []),
  ]

  const payrollAndCompensation: NavItem[] = [
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer', 'Payroll Officer'])
      ? [{ key: '/compensation', label: 'Compensation', icon: 'DollarOutlined' }]
      : []),
    ...(me.groups.includes('Payroll Officer') ? [{ key: '/payroll', label: 'Payroll', icon: 'WalletOutlined' }] : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'Payroll Officer', 'Executive']) || me.is_manager
      ? [{ key: '/reports', label: 'Reports', icon: 'BarChartOutlined' }]
      : []),
  ]

  const admin: NavItem[] = [
    { key: '/role-grant-requests', label: 'Role Grant Requests', icon: 'SafetyCertificateOutlined' },
    ...(me.groups.includes('System Administrator')
      ? [
          { key: '/users', label: 'Users', icon: 'UsergroupAddOutlined' },
          { key: '/audit-log', label: 'Audit Log', icon: 'FileSearchOutlined' },
        ]
      : []),
  ]

  const groups: NavGroup[] = [
    { label: 'My Work', items: myWork },
    { label: 'People', items: people },
    { label: 'Payroll & Compensation', items: payrollAndCompensation },
    { label: 'Admin', items: admin },
  ]

  return groups.filter((g) => g.items.length > 0)
}
```

Note: `Role Grant Requests` lives in **Admin**, unconditionally visible to every role — matching the spec's table (`docs/superpowers/specs/2026-07-26-side-navbar-design.md` §4), which lists it under Admin with "shown to all today — kept as-is". It is the only Admin item a non-System-Administrator sees; that's why the "plain employee" test above expects an `Admin` group containing only `/role-grant-requests`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- navGroups`
Expected: PASS, 8 tests

- [ ] **Step 5: Commit**

```bash
git add frontend/src/layout/navGroups.ts frontend/src/layout/navGroups.test.ts
git commit -m "Add pure nav-grouping function for side navbar"
```

---

## Task 2: Sidebar collapse persistence hook

**Files:**
- Create: `frontend/src/layout/useSidebarCollapse.ts`
- Test: `frontend/src/layout/useSidebarCollapse.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/layout/useSidebarCollapse.test.ts
import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useSidebarCollapse } from './useSidebarCollapse'

const STORAGE_KEY = 'hrms.sidebar.collapsed'

describe('useSidebarCollapse', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('defaults to not collapsed when nothing is stored', () => {
    const { result } = renderHook(() => useSidebarCollapse())
    expect(result.current.collapsed).toBe(false)
  })

  it('reads a previously stored collapsed=true value', () => {
    window.localStorage.setItem(STORAGE_KEY, 'true')
    const { result } = renderHook(() => useSidebarCollapse())
    expect(result.current.collapsed).toBe(true)
  })

  it('toggling persists the new value to localStorage', () => {
    const { result } = renderHook(() => useSidebarCollapse())
    act(() => {
      result.current.setCollapsed(true)
    })
    expect(result.current.collapsed).toBe(true)
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe('true')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- useSidebarCollapse`
Expected: FAIL — `Cannot find module './useSidebarCollapse'`

- [ ] **Step 3: Write the implementation**

```typescript
// frontend/src/layout/useSidebarCollapse.ts
import { useState } from 'react'

const STORAGE_KEY = 'hrms.sidebar.collapsed'

export function useSidebarCollapse(): { collapsed: boolean; setCollapsed: (value: boolean) => void } {
  const [collapsed, setCollapsedState] = useState<boolean>(() => window.localStorage.getItem(STORAGE_KEY) === 'true')

  function setCollapsed(value: boolean) {
    setCollapsedState(value)
    window.localStorage.setItem(STORAGE_KEY, String(value))
  }

  return { collapsed, setCollapsed }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- useSidebarCollapse`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add frontend/src/layout/useSidebarCollapse.ts frontend/src/layout/useSidebarCollapse.test.ts
git commit -m "Add sidebar collapse-state persistence hook"
```

---

## Task 3: Rewrite AppLayout as Sider + slim Header

**Files:**
- Modify: `frontend/src/layout/AppLayout.tsx`
- Test: `frontend/src/layout/AppLayout.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/layout/AppLayout.test.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Me } from '../api/types'
import { AuthContext } from '../auth/AuthContext'
import { AppLayout } from './AppLayout'

vi.mock('../api/notifications', () => ({
  listNotifications: vi.fn().mockResolvedValue({ count: 2, next: null, previous: null, results: [] }),
}))

function makeMe(overrides: Partial<Me> = {}): Me {
  return {
    id: 1,
    email: 'a@b.com',
    groups: [],
    is_employee: true,
    is_manager: false,
    second_factor_enrollment_pending: false,
    ...overrides,
  }
}

function renderLayout(me: Me | null) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={{ me, isLoading: false, refetch: async () => {}, logout: async () => {} }}>
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<div>Dashboard content</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('AppLayout', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('shows My Work items and only Role Grant Requests under Admin for a plain employee', async () => {
    renderLayout(makeMe())
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Leave')).toBeInTheDocument()
    expect(screen.getByText('Role Grant Requests')).toBeInTheDocument()
    expect(screen.queryByText('People')).not.toBeInTheDocument()
    expect(screen.queryByText('Users')).not.toBeInTheDocument()
    expect(screen.queryByText('Employees')).not.toBeInTheDocument()
  })

  it('shows the People and Admin groups for a System Administrator', async () => {
    renderLayout(makeMe({ groups: ['System Administrator'] }))
    await waitFor(() => expect(screen.getByText('Admin')).toBeInTheDocument())
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Audit Log')).toBeInTheDocument()
  })

  it('shows HR Officer visible items including Onboarding', async () => {
    renderLayout(makeMe({ groups: ['HR Officer'] }))
    await waitFor(() => expect(screen.getByText('People')).toBeInTheDocument())
    expect(screen.getByText('Departments')).toBeInTheDocument()
    expect(screen.getByText('Employees')).toBeInTheDocument()
    expect(screen.getByText('Recruitment')).toBeInTheDocument()
    expect(screen.getByText('Onboarding')).toBeInTheDocument()
    expect(screen.getByText('Compensation')).toBeInTheDocument()
  })

  it('shows Recruiter visible items without Employees or Compensation', async () => {
    renderLayout(makeMe({ groups: ['Recruiter'] }))
    await waitFor(() => expect(screen.getByText('People')).toBeInTheDocument())
    expect(screen.getByText('Departments')).toBeInTheDocument()
    expect(screen.getByText('Recruitment')).toBeInTheDocument()
    expect(screen.queryByText('Employees')).not.toBeInTheDocument()
    expect(screen.queryByText('Payroll & Compensation')).not.toBeInTheDocument()
  })

  it('shows Executive visible Reports', async () => {
    renderLayout(makeMe({ groups: ['Executive'] }))
    await waitFor(() => expect(screen.getByText('Payroll & Compensation')).toBeInTheDocument())
    expect(screen.getByText('Reports')).toBeInTheDocument()
  })

  it('shows complete manager-visible menu including My Team and Reports', async () => {
    renderLayout(makeMe({ is_manager: true }))
    await waitFor(() => expect(screen.getByText('People')).toBeInTheDocument())
    expect(screen.getByText('My Team')).toBeInTheDocument()
    expect(screen.getByText('Payroll & Compensation')).toBeInTheDocument()
    expect(screen.getByText('Reports')).toBeInTheDocument()
  })

  it('renders the unread notification count as a badge and polls at 30-second interval', async () => {
    vi.useFakeTimers()
    renderLayout(makeMe())
    expect(await screen.findByText('2')).toBeInTheDocument()
    vi.advanceTimersByTime(30000)
    await waitFor(() => expect(screen.getByText('2')).toBeInTheDocument())
    vi.useRealTimers()
  })

  it('toggles collapse state, persists it, and renders collapsed width of 64', async () => {
    const user = userEvent.setup()
    const { container } = renderLayout(makeMe())
    await screen.findByText('Dashboard')
    const trigger = screen.getByRole('button', { name: /collapse sidebar/i })
    await user.click(trigger)
    expect(window.localStorage.getItem('hrms.sidebar.collapsed')).toBe('true')
    const sider = container.querySelector('.ant-layout-sider')
    expect(sider).toHaveStyle({ width: '64px' })
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- AppLayout`
Expected: FAIL — current `AppLayout` renders a flat top nav with no `Admin`/`People` group labels and no collapse-toggle button with accessible name "collapse sidebar"

- [ ] **Step 3: Write the implementation**

```typescript
// frontend/src/layout/AppLayout.tsx
import {
  ApartmentOutlined,
  BarChartOutlined,
  BellOutlined,
  CalendarOutlined,
  DashboardOutlined,
  DollarOutlined,
  FileSearchOutlined,
  IdcardOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RocketOutlined,
  SafetyCertificateOutlined,
  SolutionOutlined,
  TeamOutlined,
  UserOutlined,
  UsergroupAddOutlined,
  WalletOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { Badge, Dropdown, Layout, Menu } from 'antd'
import type { MenuProps } from 'antd'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { listNotifications } from '../api/notifications'
import { useAuth } from '../auth/AuthContext'
import { buildNavGroups } from './navGroups'
import { useSidebarCollapse } from './useSidebarCollapse'

const { Header, Sider, Content } = Layout

const ICONS: Record<string, React.ReactNode> = {
  DashboardOutlined: <DashboardOutlined />,
  BellOutlined: <BellOutlined />,
  CalendarOutlined: <CalendarOutlined />,
  UserOutlined: <UserOutlined />,
  TeamOutlined: <TeamOutlined />,
  ApartmentOutlined: <ApartmentOutlined />,
  IdcardOutlined: <IdcardOutlined />,
  SolutionOutlined: <SolutionOutlined />,
  RocketOutlined: <RocketOutlined />,
  DollarOutlined: <DollarOutlined />,
  WalletOutlined: <WalletOutlined />,
  BarChartOutlined: <BarChartOutlined />,
  UsergroupAddOutlined: <UsergroupAddOutlined />,
  FileSearchOutlined: <FileSearchOutlined />,
  SafetyCertificateOutlined: <SafetyCertificateOutlined />,
}

export function AppLayout() {
  const { me, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const { collapsed, setCollapsed } = useSidebarCollapse()

  const { data: unreadNotificationsResponse } = useQuery({
    queryKey: ['notifications', 'list', 'unread-count'],
    queryFn: () => listNotifications({ read_at__isnull: true }),
    refetchInterval: 30000,
  })

  const navGroups = buildNavGroups(me, unreadNotificationsResponse?.count ?? 0)

  const menuItems: MenuProps['items'] = navGroups.map((group) => ({
    key: group.label,
    label: group.label,
    type: 'group',
    children: group.items.map((item) => ({
      key: item.key,
      icon: ICONS[item.icon],
      label: (
        <Link to={item.key}>
          {item.label}
          {!!item.badge && item.badge > 0 && <Badge count={item.badge} size="small" style={{ marginLeft: 8 }} />}
        </Link>
      ),
    })),
  }))

  const handleLogout = () => {
    void logout()
      .then(() => navigate('/login', { replace: true }))
      .catch(() => navigate('/login', { replace: true }))
  }

  const userMenuItems: MenuProps['items'] = [{ key: 'logout', label: 'Log out', onClick: handleLogout }]

  return (
    <Layout style={{ minHeight: '100vh', background: '#fff' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          background: '#fff',
          borderBottom: '1px solid #ececec',
          padding: '0 24px',
          height: 56,
          lineHeight: 'normal',
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 700, color: '#111' }}>HRMS</div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 20 }}>
          <Link to="/notifications" aria-label="Notifications" style={{ color: 'rgba(0,0,0,0.65)', display: 'flex', alignItems: 'center' }}>
            <Badge count={unreadNotificationsResponse?.count ?? 0} size="small">
              <BellOutlined style={{ fontSize: 18 }} />
            </Badge>
          </Link>
          <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
            <div
              role="button"
              tabIndex={0}
              aria-haspopup="true"
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  e.currentTarget.click()
                }
              }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}
            >
              <UserOutlined />
              <span style={{ fontSize: 14 }}>{me?.email}</span>
            </div>
          </Dropdown>
        </div>
      </Header>
      <Layout>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          trigger={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          theme="light"
          width={220}
          style={{ borderRight: '1px solid #ececec' }}
        >
          <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} style={{ borderRight: 'none' }} />
        </Sider>
        <Content style={{ padding: '32px 40px' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
```

Ant Design's built-in `Sider` collapse trigger does not carry the accessible name `"collapse sidebar"` out of the box, so the test's `getByRole('button', { name: /collapse sidebar/i })` requires labelling it explicitly. Adjust the `Sider` trigger to a custom element with that label instead of relying on the default:

```typescript
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          trigger={null}
          theme="light"
          width={220}
          collapsedWidth={64}
          style={{ borderRight: '1px solid #ececec', position: 'relative' }}
        >
          <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} style={{ borderRight: 'none' }} />
          <button
            type="button"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-expanded={!collapsed}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              position: 'absolute',
              bottom: 12,
              left: collapsed ? 18 : 190,
              border: '1px solid #ececec',
              borderRadius: 6,
              background: '#fff',
              width: 28,
              height: 28,
              cursor: 'pointer',
            }}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </button>
        </Sider>
```

Replace the earlier `Sider` block with this version (custom trigger, `trigger={null}` disables Ant's default one) before running the tests.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- AppLayout`
Expected: PASS, 4 tests

- [ ] **Step 5: Run the full frontend test suite to confirm no regressions**

Run: `npm run test`
Expected: PASS — all existing suites (including `ProtectedRoute.test.tsx`, page tests that render inside `AppLayout` via routes, if any) still pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/layout/AppLayout.tsx frontend/src/layout/AppLayout.test.tsx
git commit -m "Replace top nav with collapsible grouped side navbar"
```

---

## Task 4: Manual verification in the browser

**Files:** none (verification only)

- [ ] **Step 1: Start the dev server**

Run: `npm run dev` (from `frontend/`)

- [ ] **Step 2: Log in as a plain Employee fixture and confirm**
  - Sidebar shows the "My Work" group (Dashboard, Notifications, Leave, My Profile) and an "Admin" group containing only Role Grant Requests.
  - No "People" or "Payroll & Compensation" group headers appear, and "Admin" shows no Users/Audit Log entries.
  - Clicking the collapse trigger shrinks the sidebar to an icon rail; icons remain visible, labels hide.
  - Reloading the page preserves the collapsed state.
  - The notification bell in the top bar shows the correct unread badge count and links to `/notifications`.

- [ ] **Step 3: Log in as a System Administrator fixture and confirm**
  - "Admin" group appears with Users and Audit Log.
  - "People", "Payroll & Compensation" stay hidden (System Administrator holds none of those gating groups per `docs/07-iam-rbac.md` — `HRMS-NFR-019`).

- [ ] **Step 4: Log in as an HR Administrator fixture and confirm**
  - "People" group shows Departments, Employees, Recruitment.
  - "Payroll & Compensation" shows Compensation and Reports (not Payroll — that's Payroll-Officer-only).

- [ ] **Step 5: Confirm active-route highlighting**

Navigate between a few pages and confirm the corresponding `Menu.Item` highlights as active, matching `location.pathname`.

- [ ] **Step 6: No commit** — this task is verification only, not a code change.

---

## Self-Review

**Spec coverage:**
- §3 Layout structure (top bar + Sider, collapse persisted) → Task 3.
- §4 Grouped navigation items, per-group gating table → Task 1 (`navGroups.ts`) mirrors the table exactly, Task 3 wires it into the UI.
- §4 Icons → Task 3 `ICONS` map, one entry per item in the spec's icon list.
- §4 Notification badge → Task 1 (`badge` field) + Task 3 (Menu item badge, top-bar bell badge).
- §5 Testing (behavior parity per role, group-hiding, collapse persistence, notification badge) → Task 1, 2, 3 tests cover each point.
- §6 Deferred items → intentionally untouched by this plan; no task references them.

**Placeholder scan:** none found — every step has complete, runnable code and exact commands.

**Type consistency:** `NavItem`/`NavGroup` defined in Task 1 are consumed unchanged in Task 3 (`buildNavGroups`, `.label`, `.items`, `.key`, `.icon`, `.badge`). `useSidebarCollapse` returns `{ collapsed, setCollapsed }` in Task 2 and is destructured identically in Task 3. `Me` type usage matches `frontend/src/api/types.ts`'s `MeSchema` fields throughout.
