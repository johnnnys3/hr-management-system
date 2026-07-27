import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { AccessApprovalsQueue } from './AccessApprovalsQueue'

function renderQueue() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AccessApprovalsQueue />
    </QueryClientProvider>,
  )
}

const pendingRequest = {
  id: 11, requester: 1, subject: 2, role: 3, status: 'pending' as const, approver: null,
  requested_at: '2026-07-27T00:00:00Z', decided_at: null,
  requester_email: 'admin@example.com', subject_email: 'jane@example.com',
  subject_name: 'Jane Doe', role_name: 'Payroll Officer',
}

describe('AccessApprovalsQueue', () => {
  afterEach(() => vi.restoreAllMocks())

  it('renders a pending request as a plain-language sentence', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    renderQueue()

    expect(await screen.findByText(/payroll officer access for jane doe \(jane@example\.com\)/i)).toBeInTheDocument()
  })

  it('approves a pending request', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      ...pendingRequest, status: 'approved', approver: 5, decided_at: '2026-07-27T01:00:00Z',
    })
    renderQueue()
    const user = userEvent.setup()

    await screen.findByText(/payroll officer/i)
    await user.click(screen.getByRole('button', { name: /^approve$/i }))
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'approved'))
  })

  it('declines a pending request', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      ...pendingRequest, status: 'refused', approver: 5, decided_at: '2026-07-27T01:00:00Z',
    })
    renderQueue()
    const user = userEvent.setup()

    await screen.findByText(/payroll officer/i)
    await user.click(screen.getByRole('button', { name: /decline/i }))
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'refused'))
  })

  it('shows decided requests as history, without approve/decline actions', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([
      { ...pendingRequest, status: 'approved', decided_at: '2026-07-27T01:00:00Z' },
    ])
    renderQueue()

    await screen.findByText(/payroll officer/i)
    expect(screen.queryByRole('button', { name: /^approve$/i })).not.toBeInTheDocument()
  })
})
