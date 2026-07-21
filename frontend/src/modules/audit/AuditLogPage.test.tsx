import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as auditApi from '../../api/audit'
import { AuditLogPage } from './AuditLogPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuditLogPage />
    </QueryClientProvider>,
  )
}

describe('AuditLogPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists audit log entries from GET /api/audit-log/', async () => {
    vi.spyOn(auditApi, 'listAuditLog').mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          actor: 5,
          category: 'permission_change',
          target_type: 'role_grant_request',
          target_id: 9,
          action: 'approve',
          detail: { note: 'confirmed' },
          occurred_at: '2026-07-21T00:00:00Z',
        },
      ],
    })

    renderPage()

    expect(await screen.findByText('approve')).toBeInTheDocument()
    expect(screen.getByText('Permission change')).toBeInTheDocument()
    expect(screen.getByText('role_grant_request #9')).toBeInTheDocument()
  })

  it('refetches with the selected category filter', async () => {
    const listSpy = vi.spyOn(auditApi, 'listAuditLog').mockResolvedValue({
      count: 0,
      next: null,
      previous: null,
      results: [],
    })

    renderPage()

    await screen.findByText('Audit Log')
    expect(listSpy).toHaveBeenCalledWith({ category: undefined, page: 1 })
  })
})
