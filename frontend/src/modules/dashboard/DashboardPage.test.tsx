import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as dashboardApi from '../../api/dashboard'
import { AuthContext } from '../../auth/AuthContext'
import { DashboardPage } from './DashboardPage'

function renderPage(groups: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 1, email: 'user@b.com', groups, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <DashboardPage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  it('shows an Employee their own leave balance and pending tasks, no aggregates', async () => {
    vi.spyOn(dashboardApi, 'getDashboard').mockResolvedValue({
      leave_balance: [
        { id: 1, employee: 1, leave_type: 1, period_start: '2026-01-01', period_end: '2026-12-31', entitled_days: '20.00', used_days: '5.00', created_at: '', updated_at: '' },
      ],
      pending_tasks: [
        { id: 1, category: 'pending_task', channel: 'in_app', subject: 'Sign contract', body: '', related_type: null, related_id: null, read_at: null, created_at: '' },
      ],
    })

    renderPage(['Employee'])

    expect(await screen.findByText(/2026-01-01/)).toBeInTheDocument()
    expect(screen.getByText('Sign contract')).toBeInTheDocument()
    expect(screen.queryByText('Headcount')).not.toBeInTheDocument()
  })

  it('shows an Executive aggregates only, never individual data', async () => {
    vi.spyOn(dashboardApi, 'getDashboard').mockResolvedValue({
      aggregates: {
        headcount: { total: 42 },
        leave_utilization: { entitled_days: 100, used_days: 30 },
        turnover: { hires: 3, terminations: 1 },
        payroll_cost: { gross_pay: 50000, net_pay: 40000 },
        payroll_summary: { gross_pay: 45000, net_pay: 35000, payslip_count: 42 },
      },
    })

    renderPage(['Executive'])

    expect(await screen.findByText('Headcount')).toBeInTheDocument()
    expect(screen.getAllByText('42').length).toBeGreaterThan(0)
    expect(screen.getByText(/50[,.]?000/)).toBeInTheDocument()
    expect(screen.getByText(/40[,.]?000/)).toBeInTheDocument()
    expect(screen.getByText(/45[,.]?000/)).toBeInTheDocument()
    expect(screen.getByText(/35[,.]?000/)).toBeInTheDocument()
    expect(screen.queryByText('My Leave Balance')).not.toBeInTheDocument()
    expect(screen.queryByText('Pending Tasks')).not.toBeInTheDocument()
  })

  it('shows a Manager the team pending-leave-request count alongside their own personal data', async () => {
    vi.spyOn(dashboardApi, 'getDashboard').mockResolvedValue({
      leave_balance: [
        { id: 1, employee: 1, leave_type: 1, period_start: '2026-01-01', period_end: '2026-12-31', entitled_days: '20.00', used_days: '5.00', created_at: '', updated_at: '' },
      ],
      pending_tasks: [
        { id: 1, category: 'pending_task', channel: 'in_app', subject: 'Sign contract', body: '', related_type: null, related_id: null, read_at: null, created_at: '' },
      ],
      team: { pending_leave_requests: 4 },
    })

    renderPage([])

    expect(await screen.findByText('Team Pending Leave Requests')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.getByText(/2026-01-01/)).toBeInTheDocument()
    expect(screen.getByText('Sign contract')).toBeInTheDocument()
  })
})
