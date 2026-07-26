import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { AuthContext } from '../../auth/AuthContext'
import { AccessPage } from './AccessPage'
import type { Me } from '../../api/types'

function makeMe(overrides: Partial<Me> = {}): Me {
  return {
    id: 1, email: 'a@b.com', groups: [], is_employee: true, is_manager: false,
    second_factor_enrollment_pending: false, ...overrides,
  }
}

function renderPage(me: Me) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([])
  vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
  vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([])
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={{ me, isLoading: false, refetch: async () => {}, logout: async () => {} }}>
        <AccessPage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('AccessPage', () => {
  it('shows only Grant Access for a System Administrator who is not also HR Administrator', async () => {
    renderPage(makeMe({ groups: ['System Administrator'] }))
    expect(await screen.findByText('Grant a user access')).toBeInTheDocument()
    expect(screen.queryByText('Pending approvals')).not.toBeInTheDocument()
  })

  it('shows only Access Approvals for an HR Administrator who is not also System Administrator', async () => {
    renderPage(makeMe({ groups: ['HR Administrator'] }))
    expect(await screen.findByText('Pending approvals')).toBeInTheDocument()
    expect(screen.queryByText('Grant a user access')).not.toBeInTheDocument()
  })

  it('shows both sections for a user holding both roles', async () => {
    renderPage(makeMe({ groups: ['System Administrator', 'HR Administrator'] }))
    expect(await screen.findByText('Grant a user access')).toBeInTheDocument()
    expect(await screen.findByText('Pending approvals')).toBeInTheDocument()
  })
})
