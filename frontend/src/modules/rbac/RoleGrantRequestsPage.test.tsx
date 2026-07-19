import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { AuthContext } from '../../auth/AuthContext'
import { RoleGrantRequestsPage } from './RoleGrantRequestsPage'

function renderPage(meId = 1) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: meId, email: 'a@b.com', groups: [], second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <RoleGrantRequestsPage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('RoleGrantRequestsPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits a new role grant request', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([])
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

  it('lists requests from GET /api/role-grant-requests/', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([
      {
        id: 11, requester: 2, subject: 3, role: 4, status: 'pending',
        approver: null, requested_at: '', decided_at: null,
      },
    ])
    renderPage(1)

    expect(await screen.findByText('11')).toBeInTheDocument()
  })

  it('decides a pending request from the table row action', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([
      {
        id: 11, requester: 2, subject: 3, role: 4, status: 'pending',
        approver: null, requested_at: '', decided_at: null,
      },
    ])
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      id: 11, requester: 2, subject: 3, role: 4, status: 'approved',
      approver: 1, requested_at: '', decided_at: '',
    })
    renderPage(1)
    const user = userEvent.setup()

    await screen.findByText('11')
    await user.click(screen.getByRole('button', { name: /^approve$/i }))
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'approved'))
  })

  it("does not show decide actions for the requester's own pending request", async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([
      {
        id: 12, requester: 1, subject: 3, role: 4, status: 'pending',
        approver: null, requested_at: '', decided_at: null,
      },
    ])
    renderPage(1)

    await screen.findByText('12')
    expect(screen.queryByRole('button', { name: /^approve$/i })).not.toBeInTheDocument()
  })
})
