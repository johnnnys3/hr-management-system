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
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'approved'))
    expect(await screen.findByText(/request #11 approved/i)).toBeInTheDocument()
  })
})
