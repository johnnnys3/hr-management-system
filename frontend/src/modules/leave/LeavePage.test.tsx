import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as leaveApi from '../../api/leave'
import { AuthContext } from '../../auth/AuthContext'
import { LeavePage } from './LeavePage'

// Note: assertions here use getByText/queryByText rather than getByRole —
// getByRole's accessible-name computation walks and computes styles for the
// entire antd-rendered tree (icons included) and is orders of magnitude
// slower than text matching in this jsdom environment.

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
        <LeavePage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('LeavePage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lets an Employee cancel their own pending request and does not show HR-only tabs', async () => {
    vi.spyOn(leaveApi, 'listLeaveTypes').mockResolvedValue([
      { id: 1, name: 'Annual', requires_approval: true, is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(leaveApi, 'listLeaveBalances').mockResolvedValue([])
    vi.spyOn(leaveApi, 'listLeaveRequests').mockResolvedValue([
      {
        id: 10, employee: 42, leave_type: 1, start_date: '2026-08-01', end_date: '2026-08-03',
        reason: 'Trip', status: 'pending', approved_by: null, decided_at: null, created_at: '',
      },
    ])
    const cancelSpy = vi.spyOn(leaveApi, 'cancelLeaveRequest').mockResolvedValue({
      id: 10, employee: 42, leave_type: 1, start_date: '2026-08-01', end_date: '2026-08-03',
      reason: 'Trip', status: 'cancelled', approved_by: null, decided_at: null, created_at: '',
    })

    renderPage(['Employee'])
    const user = userEvent.setup()

    expect(await screen.findByText('Trip')).toBeInTheDocument()
    expect(screen.queryByText('Leave Types')).not.toBeInTheDocument()
    expect(screen.queryByText('Calendar')).not.toBeInTheDocument()

    await user.click(screen.getByText('Cancel'))
    expect(cancelSpy).toHaveBeenCalledWith(10)
  })

  it('lets an HR Officer correct or cancel any pending request but never approve/reject', async () => {
    vi.spyOn(leaveApi, 'listLeaveTypes').mockResolvedValue([
      { id: 1, name: 'Annual', requires_approval: true, is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(leaveApi, 'listLeaveBalances').mockResolvedValue([])
    vi.spyOn(leaveApi, 'listLeaveRequests').mockResolvedValue([
      {
        id: 11, employee: 43, leave_type: 1, start_date: '2026-08-05', end_date: '2026-08-06',
        reason: null, status: 'pending', approved_by: null, decided_at: null, created_at: '',
      },
    ])

    renderPage(['HR Officer'])

    expect(await screen.findByText('Correct')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.queryByText('Approve')).not.toBeInTheDocument()
    expect(screen.queryByText('Reject')).not.toBeInTheDocument()
    expect(screen.getByText('Leave Types')).toBeInTheDocument()
    expect(screen.getByText('Calendar')).toBeInTheDocument()
  })

  it('lets a non-HR viewer approve or reject a pending (direct report) request', async () => {
    vi.spyOn(leaveApi, 'listLeaveTypes').mockResolvedValue([
      { id: 1, name: 'Annual', requires_approval: true, is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(leaveApi, 'listLeaveBalances').mockResolvedValue([])
    vi.spyOn(leaveApi, 'listLeaveRequests').mockResolvedValue([
      {
        id: 12, employee: 44, leave_type: 1, start_date: '2026-08-10', end_date: '2026-08-11',
        reason: null, status: 'pending', approved_by: null, decided_at: null, created_at: '',
      },
    ])
    const approveSpy = vi.spyOn(leaveApi, 'approveLeaveRequest').mockResolvedValue({
      id: 12, employee: 44, leave_type: 1, start_date: '2026-08-10', end_date: '2026-08-11',
      reason: null, status: 'approved', approved_by: 1, decided_at: '', created_at: '',
    })

    renderPage([])
    const user = userEvent.setup()

    expect(await screen.findByText('Approve')).toBeInTheDocument()
    await user.click(screen.getByText('Approve'))
    expect(approveSpy).toHaveBeenCalledWith(12)
  })
})
