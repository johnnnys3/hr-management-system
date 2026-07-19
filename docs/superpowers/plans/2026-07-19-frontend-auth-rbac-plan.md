# Frontend Auth + RBAC/IAM Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the INFRA-001 placeholder in `frontend/` with a real React SPA shell (Ant Design + TanStack Query + React Router) and ship the first frontend-batch module: login/logout/session bootstrap, password reset, a placeholder landing page, and RBAC/IAM screens (user management, role-grant request + decide), all consuming already-merged backend endpoints.

**Architecture:** A typed `api/` fetch client centralizes CSRF injection and the uniform error envelope; `auth/AuthContext` (populated from `GET /api/auth/me/`) plus a `ProtectedRoute` gate every screen but login/password-reset; `layout/AppLayout` (Ant Design `Layout`/`Menu`) wraps authenticated routes; `modules/auth` and `modules/rbac` hold the five screens. See `docs/superpowers/specs/2026-07-19-frontend-auth-rbac-design.md` for full rationale, including corrections found against the real backend code (no `GET /api/role-grant-requests/`, `/api/users/` is unpaginated, exact serializer field shapes, login's three response shapes).

**Tech Stack:** Vite, React 19, TypeScript, Ant Design (`antd`), TanStack Query (`@tanstack/react-query`), React Router (`react-router-dom`), Vitest + React Testing Library for tests.

---

## Before you start

- Task ID prefix for this module: `FRONTEND-AUTH-001`. Branch: `feature/frontend-auth-001-auth-rbac-client`, cut from `develop`.
- Open a GitHub issue first (`gh issue create`) titled "FRONTEND-AUTH-001: Auth + RBAC/IAM client interface", body summarizing the spec doc, before starting Task 1. Reference the spec: `docs/superpowers/specs/2026-07-19-frontend-auth-rbac-design.md`.
- All commands in this plan run from `frontend/` unless stated otherwise. `cd frontend` once at the start of your session.
- The backend must be running for manual verification steps: `docker compose up -d` from the repo root (brings up `django`, `django-migrate`, `caddy` at `http://localhost:8080`, etc. — no new Docker service is added by this plan; the Vite dev server proxies `/api` to `http://localhost:8080`, which Caddy already routes to Django per `caddy/Caddyfile`).
- No backend code changes in this plan. The missing `GET /api/role-grant-requests/` endpoint is a separate, out-of-scope backend follow-up (see spec §8) — open that as its own issue after this module ships; do not build it here.

---

### Task 1: Install dependencies and configure the dev proxy

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`

- [ ] **Step 1: Install runtime and test dependencies**

Run:
```bash
cd frontend
npm install antd @tanstack/react-query react-router-dom
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

- [ ] **Step 2: Add the Vite dev-server proxy so `npm run dev` reaches the backend through Caddy**

`frontend/vite.config.ts` — replace the full contents with:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Add a Vitest config alongside Vite's**

Create `frontend/vitest.config.ts`:

```ts
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      globals: true,
    },
  }),
)
```

- [ ] **Step 4: Add the jest-dom matcher setup file**

Create `frontend/src/test/setup.ts`:

```ts
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 5: Add a `test` script to package.json**

`frontend/package.json` — add `"test": "vitest run"` to `"scripts"`, so the block reads:

```json
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "oxlint",
    "preview": "vite preview",
    "test": "vitest run"
  },
```

- [ ] **Step 6: Verify the install and config are valid**

Run: `npm run test`
Expected: Vitest starts and reports "No test files found" (exit code 1 is fine here — this just confirms config loads without error; the next tasks add real tests).

- [ ] **Step 7: Commit**

```bash
cd /Users/mac/Desktop/hr-management-system
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/vitest.config.ts frontend/src/test/setup.ts
git commit -m "FRONTEND-AUTH-001: add antd, TanStack Query, React Router, Vitest

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: API client — CSRF injection and error-envelope parsing

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/client.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/api/client.test.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch, getCsrfToken } from './client'

describe('getCsrfToken', () => {
  afterEach(() => {
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  })

  it('reads the csrftoken cookie', () => {
    document.cookie = 'csrftoken=abc123'
    expect(getCsrfToken()).toBe('abc123')
  })

  it('returns null when no csrftoken cookie is set', () => {
    expect(getCsrfToken()).toBeNull()
  })
})

describe('apiFetch', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  })

  it('sends the CSRF header on POST when a csrftoken cookie exists', async () => {
    document.cookie = 'csrftoken=tok-1'
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    )

    await apiFetch('/api/auth/login/', { method: 'POST', body: { email: 'a@b.com' } })

    const [, init] = vi.mocked(fetch).mock.calls[0]
    expect((init?.headers as Record<string, string>)['X-CSRFToken']).toBe('tok-1')
  })

  it('does not send a CSRF header on GET', async () => {
    document.cookie = 'csrftoken=tok-1'
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }))

    await apiFetch('/api/auth/me/')

    const [, init] = vi.mocked(fetch).mock.calls[0]
    expect((init?.headers as Record<string, string> | undefined)?.['X-CSRFToken']).toBeUndefined()
  })

  it('parses the uniform error envelope and throws ApiError', async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(
        JSON.stringify({ error: { code: 'validation_error', message: 'Bad input.', fields: { email: ['Required.'] } } }),
        { status: 400 },
      ),
    )

    await expect(apiFetch('/api/auth/login/', { method: 'POST', body: {} })).rejects.toMatchObject({
      status: 400,
      code: 'validation_error',
      message: 'Bad input.',
      fields: { email: ['Required.'] },
    })
  })

  it('throws ApiError with status only for a non-JSON error body (e.g. 204/401 with no body)', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 401 }))

    await expect(apiFetch('/api/auth/me/')).rejects.toBeInstanceOf(ApiError)
  })

  it('returns undefined for a 204 No Content success response', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 204 }))

    const result = await apiFetch('/api/auth/logout/', { method: 'POST' })
    expect(result).toBeUndefined()
  })
})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `npm run test -- src/api/client.test.ts`
Expected: FAIL — `Cannot find module './client'` (file doesn't exist yet).

- [ ] **Step 3: Write the implementation**

Create `frontend/src/api/client.ts`:

```ts
export class ApiError extends Error {
  status: number
  code?: string
  fields?: Record<string, string[]>

  constructor(status: number, message: string, code?: string, fields?: Record<string, string[]>) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.fields = fields
  }
}

export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

const UNSAFE_METHODS = new Set(['POST', 'PATCH', 'PUT', 'DELETE'])

interface ApiFetchOptions {
  method?: string
  body?: unknown
}

export async function apiFetch<T = unknown>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const method = options.method ?? 'GET'
  const headers: Record<string, string> = {}

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (UNSAFE_METHODS.has(method)) {
    const token = getCsrfToken()
    if (token) {
      headers['X-CSRFToken'] = token
    }
  }

  const response = await fetch(path, {
    method,
    headers,
    credentials: 'same-origin',
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const text = await response.text()
  const data = text ? JSON.parse(text) : undefined

  if (!response.ok) {
    const errorBody = data?.error
    throw new ApiError(
      response.status,
      errorBody?.message ?? `Request failed with status ${response.status}`,
      errorBody?.code,
      errorBody?.fields,
    )
  }

  return data as T
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `npm run test -- src/api/client.test.ts`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/api/client.test.ts
git commit -m "FRONTEND-AUTH-001: add API client with CSRF injection and error parsing

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Typed endpoint functions for Auth + RBAC

**Files:**
- Create: `frontend/src/api/types.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/rbac.ts`

- [ ] **Step 1: Add the shared types**

Create `frontend/src/api/types.ts`:

```ts
export interface Me {
  id: number
  email: string
  groups: string[]
  second_factor_enrollment_pending: boolean
}

export interface LoginSuccess extends Me {
  second_factor_enrollment_required?: boolean
}

export interface LoginSecondFactorRequired {
  second_factor_required: true
}

export type LoginResponse = LoginSuccess | LoginSecondFactorRequired

export function isSecondFactorRequired(response: LoginResponse): response is LoginSecondFactorRequired {
  return 'second_factor_required' in response
}

export interface UserAccount {
  id: number
  email: string
  is_active: boolean
  groups: string[]
  created_at: string
  updated_at: string
}

export interface RoleGrantRequestRecord {
  id: number
  requester: number
  subject: number
  role: number
  status: 'pending' | 'approved' | 'refused'
  approver: number | null
  requested_at: string
  decided_at: string | null
}
```

- [ ] **Step 2: Add the auth endpoint functions**

Create `frontend/src/api/auth.ts`:

```ts
import { apiFetch } from './client'
import type { LoginResponse, Me } from './types'

export function bootstrapCsrf(): Promise<void> {
  return apiFetch('/api/auth/csrf/')
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch('/api/auth/login/', { method: 'POST', body: { email, password } })
}

export function logout(): Promise<void> {
  return apiFetch('/api/auth/logout/', { method: 'POST' })
}

export function fetchMe(): Promise<Me> {
  return apiFetch('/api/auth/me/')
}

export function requestPasswordReset(email: string): Promise<void> {
  return apiFetch('/api/auth/password-reset/', { method: 'POST', body: { email } })
}

export function confirmPasswordReset(uid: string, token: string, password: string): Promise<void> {
  return apiFetch('/api/auth/password-reset/confirm/', { method: 'POST', body: { uid, token, password } })
}
```

- [ ] **Step 3: Add the RBAC endpoint functions**

Create `frontend/src/api/rbac.ts`:

```ts
import { apiFetch } from './client'
import type { RoleGrantRequestRecord, UserAccount } from './types'

export function listUsers(): Promise<UserAccount[]> {
  return apiFetch('/api/users/')
}

export function createUser(data: { email: string; password: string; is_active?: boolean }): Promise<UserAccount> {
  return apiFetch('/api/users/', { method: 'POST', body: data })
}

export function updateUser(
  id: number,
  data: Partial<{ email: string; password: string; is_active: boolean }>,
): Promise<UserAccount> {
  return apiFetch(`/api/users/${id}/`, { method: 'PATCH', body: data })
}

export function createRoleGrantRequest(subjectUserId: number, roleId: number): Promise<RoleGrantRequestRecord> {
  return apiFetch('/api/role-grant-requests/', {
    method: 'POST',
    body: { subject_user_id: subjectUserId, role_id: roleId },
  })
}

export function decideRoleGrantRequest(
  id: number,
  decision: 'approved' | 'refused',
): Promise<RoleGrantRequestRecord> {
  return apiFetch(`/api/role-grant-requests/${id}/decide/`, { method: 'POST', body: { decision } })
}
```

- [ ] **Step 4: Type-check**

Run: `npx tsc -b --noEmit`
Expected: no errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/types.ts frontend/src/api/auth.ts frontend/src/api/rbac.ts
git commit -m "FRONTEND-AUTH-001: add typed auth and RBAC endpoint functions

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 4: AuthContext and ProtectedRoute

**Files:**
- Create: `frontend/src/auth/AuthContext.tsx`
- Create: `frontend/src/auth/ProtectedRoute.tsx`
- Create: `frontend/src/auth/ProtectedRoute.test.tsx`

- [ ] **Step 1: Write the failing test for ProtectedRoute**

Create `frontend/src/auth/ProtectedRoute.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthContext } from './AuthContext'
import { ProtectedRoute } from './ProtectedRoute'

function renderWithAuth(me: Parameters<typeof AuthContext.Provider>[0]['value']['me'], requireGroup?: string) {
  return render(
    <AuthContext.Provider value={{ me, isLoading: false, refetch: async () => {}, logout: async () => {} }}>
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route element={<ProtectedRoute requireGroup={requireGroup} />}>
            <Route path="/protected" element={<div>Secret content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when unauthenticated', () => {
    renderWithAuth(null)
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the route when authenticated', () => {
    renderWithAuth({ id: 1, email: 'a@b.com', groups: [], second_factor_enrollment_pending: false })
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })

  it('redirects when authenticated but missing the required group', () => {
    renderWithAuth(
      { id: 1, email: 'a@b.com', groups: ['HR Officer'], second_factor_enrollment_pending: false },
      'System Administrator',
    )
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders when authenticated and holding the required group', () => {
    renderWithAuth(
      { id: 1, email: 'a@b.com', groups: ['System Administrator'], second_factor_enrollment_pending: false },
      'System Administrator',
    )
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/auth/ProtectedRoute.test.tsx`
Expected: FAIL — `Cannot find module './AuthContext'`

- [ ] **Step 3: Write AuthContext**

Create `frontend/src/auth/AuthContext.tsx`:

```tsx
import { createContext, useContext } from 'react'
import type { Me } from '../api/types'

export interface AuthContextValue {
  me: Me | null
  isLoading: boolean
  refetch: () => Promise<unknown>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthContext.Provider')
  }
  return ctx
}
```

- [ ] **Step 4: Write ProtectedRoute**

Create `frontend/src/auth/ProtectedRoute.tsx`:

```tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function ProtectedRoute({ requireGroup }: { requireGroup?: string }) {
  const { me, isLoading } = useAuth()

  if (isLoading) {
    return null
  }
  if (!me) {
    return <Navigate to="/login" replace />
  }
  if (requireGroup && !me.groups.includes(requireGroup)) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
```

- [ ] **Step 5: Run to verify it passes**

Run: `npm run test -- src/auth/ProtectedRoute.test.tsx`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add frontend/src/auth/AuthContext.tsx frontend/src/auth/ProtectedRoute.tsx frontend/src/auth/ProtectedRoute.test.tsx
git commit -m "FRONTEND-AUTH-001: add AuthContext and ProtectedRoute

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 5: AuthProvider — wires AuthContext to the real API and TanStack Query

**Files:**
- Create: `frontend/src/auth/AuthProvider.tsx`
- Create: `frontend/src/auth/AuthProvider.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/auth/AuthProvider.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../api/auth'
import { AuthProvider } from './AuthProvider'
import { useAuth } from './AuthContext'

function Probe() {
  const { me, isLoading } = useAuth()
  if (isLoading) return <div>loading</div>
  return <div>{me ? `hello ${me.email}` : 'anonymous'}</div>
}

function renderProvider() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Probe />
      </AuthProvider>
    </QueryClientProvider>,
  )
}

describe('AuthProvider', () => {
  afterEach(() => vi.restoreAllMocks())

  it('bootstraps CSRF then loads /auth/me/, exposing the result', async () => {
    const bootstrapSpy = vi.spyOn(authApi, 'bootstrapCsrf').mockResolvedValue(undefined)
    vi.spyOn(authApi, 'fetchMe').mockResolvedValue({
      id: 1,
      email: 'a@b.com',
      groups: [],
      second_factor_enrollment_pending: false,
    })

    renderProvider()

    await waitFor(() => expect(screen.getByText('hello a@b.com')).toBeInTheDocument())
    expect(bootstrapSpy).toHaveBeenCalled()
  })

  it('exposes me as null when fetchMe returns 401', async () => {
    vi.spyOn(authApi, 'bootstrapCsrf').mockResolvedValue(undefined)
    vi.spyOn(authApi, 'fetchMe').mockRejectedValue(new Error('unauthenticated'))

    renderProvider()

    await waitFor(() => expect(screen.getByText('anonymous')).toBeInTheDocument())
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/auth/AuthProvider.test.tsx`
Expected: FAIL — `Cannot find module './AuthProvider'`

- [ ] **Step 3: Write AuthProvider**

Create `frontend/src/auth/AuthProvider.tsx`:

```tsx
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { type ReactNode, useEffect } from 'react'
import { bootstrapCsrf, fetchMe, logout as apiLogout } from '../api/auth'
import { AuthContext } from './AuthContext'

const ME_QUERY_KEY = ['auth', 'me']

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  useEffect(() => {
    void bootstrapCsrf()
  }, [])

  const { data: me, isLoading, refetch } = useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: fetchMe,
    retry: false,
  })

  const logout = async () => {
    await apiLogout()
    queryClient.setQueryData(ME_QUERY_KEY, null)
    queryClient.clear()
  }

  return (
    <AuthContext.Provider value={{ me: me ?? null, isLoading, refetch, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm run test -- src/auth/AuthProvider.test.tsx`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/auth/AuthProvider.tsx frontend/src/auth/AuthProvider.test.tsx
git commit -m "FRONTEND-AUTH-001: add AuthProvider wiring session bootstrap to TanStack Query

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 6: AppLayout

**Files:**
- Create: `frontend/src/layout/AppLayout.tsx`

- [ ] **Step 1: Write AppLayout** (no test — this is a thin Ant Design composition; behavior is covered by the routing tests in Task 8)

Create `frontend/src/layout/AppLayout.tsx`:

```tsx
import { Layout, Menu, Typography } from 'antd'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const { Header, Content } = Layout

export function AppLayout() {
  const { me, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const items = [
    { key: '/', label: <Link to="/">Home</Link> },
    { key: '/role-grant-requests', label: <Link to="/role-grant-requests">Role Grant Requests</Link> },
    ...(me?.groups.includes('System Administrator')
      ? [{ key: '/users', label: <Link to="/users">Users</Link> }]
      : []),
    { key: 'logout', label: 'Log out' },
  ]

  const handleClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      void logout().then(() => navigate('/login', { replace: true }))
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <Typography.Title level={4} style={{ color: 'white', margin: '0 24px 0 0' }}>
          HRMS
        </Typography.Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={items}
          onClick={handleClick}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: 24 }}>
        <Outlet />
      </Content>
    </Layout>
  )
}
```

- [ ] **Step 2: Type-check**

Run: `npx tsc -b --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/layout/AppLayout.tsx
git commit -m "FRONTEND-AUTH-001: add AppLayout shell

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 7: LoginPage

**Files:**
- Create: `frontend/src/modules/auth/LoginPage.tsx`
- Create: `frontend/src/modules/auth/LoginPage.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/modules/auth/LoginPage.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../api/auth'
import { ApiError } from '../../api/client'
import { AuthContext } from '../../auth/AuthContext'
import { LoginPage } from './LoginPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const refetch = vi.fn().mockResolvedValue(undefined)
  return {
    refetch,
    ...render(
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={{ me: null, isLoading: false, refetch, logout: async () => {} }}>
          <MemoryRouter>
            <LoginPage />
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>,
    ),
  }
}

describe('LoginPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits credentials and refetches the session on success', async () => {
    const loginSpy = vi.spyOn(authApi, 'login').mockResolvedValue({
      id: 1,
      email: 'a@b.com',
      groups: [],
      second_factor_enrollment_pending: false,
    })
    const { refetch } = renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(loginSpy).toHaveBeenCalledWith('a@b.com', 'secret123'))
    await waitFor(() => expect(refetch).toHaveBeenCalled())
  })

  it('shows the invalid-credentials error', async () => {
    vi.spyOn(authApi, 'login').mockRejectedValue(new ApiError(401, 'Invalid credentials.', 'not_authenticated'))
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.type(screen.getByLabelText(/password/i), 'wrong')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText('Invalid credentials.')).toBeInTheDocument()
  })

  it('shows a not-yet-supported message when the account requires second-factor verification', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({ second_factor_required: true })
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'admin@b.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText(/second-factor verification isn't available/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/modules/auth/LoginPage.test.tsx`
Expected: FAIL — `Cannot find module './LoginPage'`

- [ ] **Step 3: Write LoginPage**

Create `frontend/src/modules/auth/LoginPage.tsx`:

```tsx
import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { isSecondFactorRequired } from '../../api/types'

interface LoginFormValues {
  email: string
  password: string
}

export function LoginPage() {
  const { refetch } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: LoginFormValues) => {
    setError(null)
    setSubmitting(true)
    try {
      const response = await login(values.email, values.password)
      if (isSecondFactorRequired(response)) {
        setError("Second-factor verification isn't available in this client yet — contact your administrator.")
        return
      }
      if (response.second_factor_enrollment_required) {
        setError("Second-factor setup isn't available in this client yet — contact your administrator.")
        return
      }
      await refetch()
      navigate('/', { replace: true })
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <Card style={{ width: 360 }}>
        <Typography.Title level={3}>Log in</Typography.Title>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              Log in
            </Button>
          </Form.Item>
        </Form>
        <Link to="/password-reset">Forgot your password?</Link>
      </Card>
    </div>
  )
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm run test -- src/modules/auth/LoginPage.test.tsx`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/auth/LoginPage.tsx frontend/src/modules/auth/LoginPage.test.tsx
git commit -m "FRONTEND-AUTH-001: add LoginPage

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 8: PasswordResetPage

**Files:**
- Create: `frontend/src/modules/auth/PasswordResetPage.tsx`
- Create: `frontend/src/modules/auth/PasswordResetPage.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/modules/auth/PasswordResetPage.test.tsx`:

```tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../api/auth'
import { PasswordResetPage } from './PasswordResetPage'

function renderPage(initialEntries = ['/password-reset']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <PasswordResetPage />
    </MemoryRouter>,
  )
}

describe('PasswordResetPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits a reset request and shows a uniform confirmation', async () => {
    const spy = vi.spyOn(authApi, 'requestPasswordReset').mockResolvedValue(undefined)
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.click(screen.getByRole('button', { name: /send reset link/i }))

    await waitFor(() => expect(spy).toHaveBeenCalledWith('a@b.com'))
    expect(await screen.findByText(/if an account exists/i)).toBeInTheDocument()
  })

  it('shows the confirm form when uid and token are present in the URL, and submits it', async () => {
    const spy = vi.spyOn(authApi, 'confirmPasswordReset').mockResolvedValue(undefined)
    renderPage(['/password-reset?uid=abc&token=xyz'])
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/new password/i), 'newpass123')
    await user.click(screen.getByRole('button', { name: /set new password/i }))

    await waitFor(() => expect(spy).toHaveBeenCalledWith('abc', 'xyz', 'newpass123'))
    expect(await screen.findByText(/password has been reset/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/modules/auth/PasswordResetPage.test.tsx`
Expected: FAIL — `Cannot find module './PasswordResetPage'`

- [ ] **Step 3: Write PasswordResetPage**

Create `frontend/src/modules/auth/PasswordResetPage.tsx`:

```tsx
import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { confirmPasswordReset, requestPasswordReset } from '../../api/auth'
import { ApiError } from '../../api/client'

export function PasswordResetPage() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid')
  const token = searchParams.get('token')

  if (uid && token) {
    return <ConfirmForm uid={uid} token={token} />
  }
  return <RequestForm />
}

function RequestForm() {
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { email: string }) => {
    setSubmitting(true)
    try {
      await requestPasswordReset(values.email)
    } finally {
      setSubmitting(false)
      setDone(true)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <Card style={{ width: 360 }}>
        <Typography.Title level={3}>Reset your password</Typography.Title>
        {done ? (
          <Alert type="info" message="If an account exists for that email, a reset link has been sent." />
        ) : (
          <Form layout="vertical" onFinish={handleSubmit}>
            <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
              <Input autoComplete="username" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={submitting} block>
                Send reset link
              </Button>
            </Form.Item>
          </Form>
        )}
      </Card>
    </div>
  )
}

function ConfirmForm({ uid, token }: { uid: string; token: string }) {
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { password: string }) => {
    setError(null)
    setSubmitting(true)
    try {
      await confirmPasswordReset(uid, token, values.password)
      setDone(true)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <Card style={{ width: 360 }}>
        <Typography.Title level={3}>Set a new password</Typography.Title>
        {done ? (
          <Alert type="success" message="Your password has been reset. You may now log in." />
        ) : (
          <>
            {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
            <Form layout="vertical" onFinish={handleSubmit}>
              <Form.Item label="New password" name="password" rules={[{ required: true }]}>
                <Input.Password autoComplete="new-password" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={submitting} block>
                  Set new password
                </Button>
              </Form.Item>
            </Form>
          </>
        )}
      </Card>
    </div>
  )
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm run test -- src/modules/auth/PasswordResetPage.test.tsx`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/auth/PasswordResetPage.tsx frontend/src/modules/auth/PasswordResetPage.test.tsx
git commit -m "FRONTEND-AUTH-001: add PasswordResetPage (request + confirm)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 9: HomePage (placeholder landing page)

**Files:**
- Create: `frontend/src/modules/auth/HomePage.tsx`

- [ ] **Step 1: Write HomePage** (no dedicated test — a direct render of `AuthContext` data already covered by `ProtectedRoute`'s tests; this is a thin display component)

Create `frontend/src/modules/auth/HomePage.tsx`:

```tsx
import { Card, Tag, Typography } from 'antd'
import { useAuth } from '../../auth/AuthContext'

export function HomePage() {
  const { me } = useAuth()
  if (!me) return null

  return (
    <Card>
      <Typography.Title level={3}>Welcome, {me.email}</Typography.Title>
      <Typography.Paragraph type="secondary">
        This is a placeholder landing page. The Executive Dashboard (module 14) has its own screen, built
        later in the frontend batch.
      </Typography.Paragraph>
      <Typography.Text strong>Your roles: </Typography.Text>
      {me.groups.length === 0 ? (
        <Typography.Text type="secondary">none assigned</Typography.Text>
      ) : (
        me.groups.map((group) => <Tag key={group}>{group}</Tag>)
      )}
    </Card>
  )
}
```

- [ ] **Step 2: Type-check**

Run: `npx tsc -b --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/modules/auth/HomePage.tsx
git commit -m "FRONTEND-AUTH-001: add placeholder HomePage

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 10: UserManagementPage

**Files:**
- Create: `frontend/src/modules/rbac/UserManagementPage.tsx`
- Create: `frontend/src/modules/rbac/UserManagementPage.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/modules/rbac/UserManagementPage.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { UserManagementPage } from './UserManagementPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <UserManagementPage />
    </QueryClientProvider>,
  )
}

describe('UserManagementPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists users from GET /api/users/', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 1, email: 'admin@b.com', is_active: true, groups: ['System Administrator'], created_at: '', updated_at: '' },
    ])
    renderPage()

    expect(await screen.findByText('admin@b.com')).toBeInTheDocument()
  })

  it('creates a user via the New User form', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([])
    const createSpy = vi.spyOn(rbacApi, 'createUser').mockResolvedValue({
      id: 2,
      email: 'new@b.com',
      is_active: true,
      groups: [],
      created_at: '',
      updated_at: '',
    })
    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new user/i }))
    const dialog = within(screen.getByRole('dialog'))
    await user.type(dialog.getByLabelText(/email/i), 'new@b.com')
    await user.type(dialog.getByLabelText(/password/i), 'secret123')
    await user.click(dialog.getByRole('button', { name: /^create$/i }))

    await waitFor(() =>
      expect(createSpy).toHaveBeenCalledWith({ email: 'new@b.com', password: 'secret123', is_active: true }),
    )
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/modules/rbac/UserManagementPage.test.tsx`
Expected: FAIL — `Cannot find module './UserManagementPage'`

- [ ] **Step 3: Write UserManagementPage**

Create `frontend/src/modules/rbac/UserManagementPage.tsx`:

```tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Form, Input, Modal, Switch, Table, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import { createUser, listUsers, updateUser } from '../../api/rbac'
import { ApiError } from '../../api/client'
import type { UserAccount } from '../../api/types'

const USERS_QUERY_KEY = ['rbac', 'users']

export function UserManagementPage() {
  const queryClient = useQueryClient()
  const { data: users = [], isLoading } = useQuery({ queryKey: USERS_QUERY_KEY, queryFn: listUsers })
  const [modalUser, setModalUser] = useState<UserAccount | 'new' | null>(null)

  const invalidate = () => queryClient.invalidateQueries({ queryKey: USERS_QUERY_KEY })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3}>Users</Typography.Title>
        <Button type="primary" onClick={() => setModalUser('new')}>
          New User
        </Button>
      </div>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={users}
        pagination={{ pageSize: 25 }}
        onRow={(record) => ({ onClick: () => setModalUser(record) })}
        columns={[
          { title: 'Email', dataIndex: 'email' },
          {
            title: 'Active',
            dataIndex: 'is_active',
            render: (active: boolean) => (active ? <Tag color="green">Active</Tag> : <Tag>Inactive</Tag>),
          },
          {
            title: 'Roles',
            dataIndex: 'groups',
            render: (groups: string[]) => groups.map((g) => <Tag key={g}>{g}</Tag>),
          },
        ]}
      />
      {modalUser && (
        <UserFormModal
          user={modalUser === 'new' ? null : modalUser}
          onClose={() => setModalUser(null)}
          onSaved={() => {
            invalidate()
            setModalUser(null)
          }}
        />
      )}
    </div>
  )
}

interface UserFormValues {
  email: string
  password?: string
  is_active: boolean
}

function UserFormModal({
  user,
  onClose,
  onSaved,
}: {
  user: UserAccount | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form] = Form.useForm<UserFormValues>()

  const mutation = useMutation({
    mutationFn: (values: UserFormValues) =>
      user
        ? updateUser(user.id, values)
        : createUser({ email: values.email, password: values.password ?? '', is_active: values.is_active }),
    onSuccess: onSaved,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
  })

  return (
    <Modal
      open
      title={user ? 'Edit User' : 'New User'}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText={user ? 'Save' : 'Create'}
      confirmLoading={mutation.isPending}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ email: user?.email, is_active: user?.is_active ?? true }}
        onFinish={(values) => mutation.mutate(values)}
      >
        <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
          <Input disabled={!!user} />
        </Form.Item>
        <Form.Item label="Password" name="password" rules={[{ required: !user }]}>
          <Input.Password placeholder={user ? 'Leave blank to keep current password' : undefined} />
        </Form.Item>
        <Form.Item label="Active" name="is_active" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  )
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm run test -- src/modules/rbac/UserManagementPage.test.tsx`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/rbac/UserManagementPage.tsx frontend/src/modules/rbac/UserManagementPage.test.tsx
git commit -m "FRONTEND-AUTH-001: add UserManagementPage

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 11: RoleGrantRequestsPage (create + decide-by-ID; no list, per spec §8)

**Files:**
- Create: `frontend/src/modules/rbac/RoleGrantRequestsPage.tsx`
- Create: `frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { RoleGrantRequestsPage } from './RoleGrantRequestsPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <RoleGrantRequestsPage />
    </QueryClientProvider>,
  )
}

describe('RoleGrantRequestsPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits a new role grant request', async () => {
    const createSpy = vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 10,
      requester: 1,
      subject: 2,
      role: 3,
      status: 'pending',
      approver: null,
      requested_at: '',
      decided_at: null,
    })
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/subject user id/i), '2')
    await user.type(screen.getByLabelText(/role id/i), '3')
    await user.click(screen.getByRole('button', { name: /submit request/i }))

    await waitFor(() => expect(createSpy).toHaveBeenCalledWith(2, 3))
    expect(await screen.findByText(/request #10 submitted/i)).toBeInTheDocument()
  })

  it('decides a request by ID', async () => {
    vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 10,
      requester: 1,
      subject: 2,
      role: 3,
      status: 'pending',
      approver: null,
      requested_at: '',
      decided_at: null,
    })
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      id: 11,
      requester: 1,
      subject: 2,
      role: 3,
      status: 'approved',
      approver: 9,
      requested_at: '',
      decided_at: '',
    })
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/request id/i), '11')
    await user.click(screen.getByRole('button', { name: /^approve$/i }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'approved'))
    expect(await screen.findByText(/request #11 approved/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test -- src/modules/rbac/RoleGrantRequestsPage.test.tsx`
Expected: FAIL — `Cannot find module './RoleGrantRequestsPage'`

- [ ] **Step 3: Write RoleGrantRequestsPage**

Create `frontend/src/modules/rbac/RoleGrantRequestsPage.tsx`:

```tsx
import { Alert, Button, Card, Form, Input, InputNumber, Space, Typography } from 'antd'
import { useState } from 'react'
import { createRoleGrantRequest, decideRoleGrantRequest } from '../../api/rbac'
import { ApiError } from '../../api/client'

export function RoleGrantRequestsPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Typography.Paragraph type="secondary">
        There is currently no list view for pending requests (backend gap — tracked separately). Use these
        forms with a request ID from a notification.
      </Typography.Paragraph>
      <RaiseRequestForm />
      <DecideRequestForm />
    </Space>
  )
}

function RaiseRequestForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { subjectUserId: number; roleId: number }) => {
    setError(null)
    setSubmitting(true)
    try {
      const created = await createRoleGrantRequest(values.subjectUserId, values.roleId)
      setResult(`Request #${created.id} submitted.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Raise a role grant request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Form layout="inline" onFinish={handleSubmit}>
        <Form.Item label="Subject user ID" name="subjectUserId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item label="Role ID" name="roleId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting}>
            Submit request
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

function DecideRequestForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [requestId, setRequestId] = useState<number | null>(null)

  const decide = async (decision: 'approved' | 'refused') => {
    if (requestId == null) return
    setError(null)
    setSubmitting(true)
    try {
      const decided = await decideRoleGrantRequest(requestId, decision)
      setResult(`Request #${decided.id} ${decided.status}.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Decide a role grant request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Space>
        <label htmlFor="decide-request-id">Request ID</label>
        <InputNumber id="decide-request-id" onChange={(value) => setRequestId(value)} />
        <Button loading={submitting} onClick={() => decide('approved')}>
          Approve
        </Button>
        <Button loading={submitting} danger onClick={() => decide('refused')}>
          Refuse
        </Button>
      </Space>
    </Card>
  )
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm run test -- src/modules/rbac/RoleGrantRequestsPage.test.tsx`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/rbac/RoleGrantRequestsPage.tsx frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx
git commit -m "FRONTEND-AUTH-001: add RoleGrantRequestsPage (create + decide-by-ID)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 12: Routes and App.tsx — wire everything together, remove the placeholder

**Files:**
- Create: `frontend/src/routes.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`
- Delete: `frontend/src/App.css` (placeholder styling, no longer used)

- [ ] **Step 1: Write the route tree**

Create `frontend/src/routes.tsx`:

```tsx
import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './layout/AppLayout'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { HomePage } from './modules/auth/HomePage'
import { LoginPage } from './modules/auth/LoginPage'
import { PasswordResetPage } from './modules/auth/PasswordResetPage'
import { RoleGrantRequestsPage } from './modules/rbac/RoleGrantRequestsPage'
import { UserManagementPage } from './modules/rbac/UserManagementPage'

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/password-reset', element: <PasswordResetPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/', element: <HomePage /> },
          { path: '/role-grant-requests', element: <RoleGrantRequestsPage /> },
          {
            element: <ProtectedRoute requireGroup="System Administrator" />,
            children: [{ path: '/users', element: <UserManagementPage /> }],
          },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
])
```

- [ ] **Step 2: Rewrite App.tsx**

`frontend/src/App.tsx` — replace the full contents with:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import { router } from './routes'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ConfigProvider>
          <RouterProvider router={router} />
        </ConfigProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
```

- [ ] **Step 3: Simplify main.tsx** (drop the now-deleted App.css import)

`frontend/src/main.tsx` — replace the full contents with:

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 4: Delete the placeholder stylesheet**

Run: `rm frontend/src/App.css`

- [ ] **Step 5: Run the full test suite**

Run: `npm run test`
Expected: PASS, all test files from Tasks 2–11 green.

- [ ] **Step 6: Type-check the whole project**

Run: `npx tsc -b --noEmit`
Expected: no errors

- [ ] **Step 7: Lint**

Run: `npm run lint`
Expected: no errors (warnings acceptable if pre-existing from the antd/react-router type surface; fix anything flagged in files this plan touches)

- [ ] **Step 8: Commit**

```bash
git add frontend/src/routes.tsx frontend/src/App.tsx frontend/src/main.tsx
git rm frontend/src/App.css
git commit -m "FRONTEND-AUTH-001: wire routes, replace INFRA-001 placeholder shell

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 13: Manual E2E verification against the live Compose stack

No code changes — this task is a verification checklist, run before opening the PR. Matches the E2E bar every backend module in this project has been held to (per `feedback_hrms_review_loop` / the project's standing convention).

- [ ] **Step 1: Bring up the backend**

Run from the repo root: `docker compose up -d`
Wait for `django`, `django-migrate`, `caddy` to report healthy: `docker compose ps`

- [ ] **Step 2: Start the frontend dev server**

Run from `frontend/`: `npm run dev`
Open `http://localhost:5173` (Vite's default port; check the terminal output for the actual port).

- [ ] **Step 3: Verify login**

Log in with a known test account (check `docker compose run --rm --entrypoint "" django-migrate python manage.py shell` or existing E2E fixtures from prior modules for credentials, per this project's established pattern). Confirm redirect to `/` and "Welcome, {email}" renders.

- [ ] **Step 4: Verify session persistence**

Reload the page. Confirm the session survives (still on `/`, not bounced to `/login`).

- [ ] **Step 5: Verify logout**

Click "Log out" in the menu. Confirm redirect to `/login` and that reloading `/` afterward bounces back to `/login`.

- [ ] **Step 6: Verify password reset request**

Navigate to `/password-reset`, submit an email, confirm the uniform "if an account exists..." message (do not need a real email to arrive; the request path is what's under test).

- [ ] **Step 7: Verify role-grant request + decide, as two different users**

As a non-Administrator user, submit a role grant request via `/role-grant-requests`, note the returned request ID. As a user holding `iam.approve_role_grant`, use the decide form with that ID; confirm "approved" (or "refused") renders. Confirm the same request ID cannot be decided twice (second submission shows the `409 conflict` error message).

- [ ] **Step 8: Verify user management, as System Administrator**

Navigate to `/users`, confirm the table lists existing users. Create a new user via the modal; confirm it appears in the table. Edit that user's `is_active` flag; confirm the table reflects the change.

- [ ] **Step 9: Verify the System-Administrator-only gate**

Log in as a non-Administrator user; confirm `/users` is not in the menu, and navigating to `/users` directly redirects away rather than rendering the table.

- [ ] **Step 10: Record results**

If any step fails, fix the underlying issue and re-run from Step 1 (or the earliest affected step) before proceeding — do not open the PR with a known-failing manual check.

---

### Task 14: Open the PR

- [ ] **Step 1: Push the branch**

```bash
git push -u origin feature/frontend-auth-001-auth-rbac-client
```

- [ ] **Step 2: Open the PR into `develop`**

```bash
gh pr create --base develop --title "FRONTEND-AUTH-001: Auth + RBAC/IAM client interface" --body "$(cat <<'EOF'
## Summary
- First module of the 14-module frontend implementation batch (plan v1.10, DOC-011/012)
- Replaces the INFRA-001 placeholder with a real app shell: Ant Design + TanStack Query + React Router
- Login, logout, session bootstrap, password reset (request + confirm), placeholder landing page
- RBAC/IAM: user management (System Administrator only), role-grant request + decide-by-ID (no list view — GET /api/role-grant-requests/ doesn't exist on the backend yet; tracked as a separate follow-up)
- MFA enrollment/recovery screens deliberately deferred to a follow-up module (owner-confirmed 2026-07-19)

See `docs/superpowers/specs/2026-07-19-frontend-auth-rbac-design.md` for full design and the corrections found against the actual backend contract during planning.

## Test plan
- [x] Vitest unit/component tests pass (`npm run test`)
- [x] `tsc -b --noEmit` clean
- [x] `npm run lint` clean
- [x] Manual E2E verified against the live Compose stack: login, logout, session persistence, password reset request+confirm, role-grant request/decide (including double-decide 409), user create/edit, System-Administrator-only route gating

Closes #<issue-number>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Replace `<issue-number>` with the actual issue number from "Before you start."

- [ ] **Step 3: Wait for CodeRabbit's review, evaluate findings against current file content (not comment text), fix legitimate issues, then merge**

Follow this project's standing CodeRabbit loop: `gh pr view <n> --json statusCheckRollup` / the commit-status endpoint to confirm a clean review against the actual head SHA before merging, not just a `MERGEABLE` state. If the PR body's `Closes #N` doesn't auto-close the issue, close it explicitly after merge.

---

## Explicitly deferred (not built by this plan)

- Second-factor (MFA) enrollment, recovery-request, and decide screens — separate follow-up module.
- `GET /api/role-grant-requests/` backend endpoint and the resulting frontend list view — separate backend follow-up issue, opened after this PR merges.
- Any of the other 12 remaining frontend-batch modules (Departments, Employee Management, Reporting Structure, Recruitment, Onboarding, Notification, Employee/Manager Self-Service, Leave Management, Dashboard, Reports) or the excluded Compensation/Payroll pair.
- A Docker Compose service for the frontend dev server — this plan uses `npm run dev` with a Vite proxy to Caddy's host port (8080); a containerized frontend dev service, if wanted later, is a separate infra decision.
