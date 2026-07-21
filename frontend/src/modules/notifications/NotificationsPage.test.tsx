import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as notificationsApi from '../../api/notifications'
import { NotificationsPage } from './NotificationsPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('NotificationsPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('defaults to unread, lets the user mark one read', async () => {
    const listSpy = vi.spyOn(notificationsApi, 'listNotifications').mockResolvedValue([
      {
        id: 1, category: 'pending_task', channel: 'in_app', subject: 'New onboarding task', body: 'Sign contract.',
        related_type: 'onboarding_task', related_id: 5, read_at: null, created_at: '2026-07-21T00:00:00Z',
      },
    ])
    const markReadSpy = vi.spyOn(notificationsApi, 'markNotificationRead').mockResolvedValue({
      id: 1, category: 'pending_task', channel: 'in_app', subject: 'New onboarding task', body: 'Sign contract.',
      related_type: 'onboarding_task', related_id: 5, read_at: '2026-07-21T01:00:00Z', created_at: '2026-07-21T00:00:00Z',
    })

    renderPage()
    const user = userEvent.setup()

    expect(await screen.findByText('New onboarding task')).toBeInTheDocument()
    expect(listSpy).toHaveBeenCalledWith({ read_at__isnull: true })

    await user.click(screen.getByRole('button', { name: 'Mark read' }))
    expect(markReadSpy.mock.calls[0][0]).toBe(1)
  })

  it('switches to All and requests without the unread filter', async () => {
    const listSpy = vi.spyOn(notificationsApi, 'listNotifications').mockResolvedValue([])

    renderPage()
    const user = userEvent.setup()
    await screen.findByText('No unread notifications.')

    await user.click(screen.getByText('All'))

    expect(await screen.findByText('No notifications.')).toBeInTheDocument()
    expect(listSpy).toHaveBeenCalledWith({})
  })
})
