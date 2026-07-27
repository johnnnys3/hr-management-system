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

  it('shows only My Work for a plain employee (no Admin group at all)', async () => {
    renderLayout(makeMe())
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Leave')).toBeInTheDocument()
    expect(screen.queryByText('Admin')).not.toBeInTheDocument()
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

  it('renders the unread notification count as a badge', async () => {
    renderLayout(makeMe())
    expect(await screen.findAllByText('2')).toHaveLength(2)
  })

  it('toggles collapse state and persists it', async () => {
    const user = userEvent.setup()
    renderLayout(makeMe())
    await screen.findByText('Dashboard')
    const trigger = screen.getByRole('button', { name: /collapse sidebar/i })
    await user.click(trigger)
    expect(window.localStorage.getItem('hrms.sidebar.collapsed')).toBe('true')
  })
})
