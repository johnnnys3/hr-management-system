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
      { id: 1, email: 'admin@b.com', is_active: true, groups: ['System Administrator'], employee_name: null, created_at: '', updated_at: '' },
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
      employee_name: null,
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

  it('edits a user via row click, without sending an empty password', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 1, email: 'admin@b.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
    ])
    const updateSpy = vi.spyOn(rbacApi, 'updateUser').mockResolvedValue({
      id: 1,
      email: 'admin@b.com',
      is_active: false,
      groups: [],
      employee_name: null,
      created_at: '',
      updated_at: '',
    })
    renderPage()
    const user = userEvent.setup()

    const row = await screen.findByText('admin@b.com')
    await user.click(row)
    const dialog = within(screen.getByRole('dialog'))
    await user.click(dialog.getByRole('switch'))
    await user.click(dialog.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(updateSpy).toHaveBeenCalledWith(1, expect.objectContaining({ is_active: false })))
    const [, payload] = updateSpy.mock.calls[0]
    expect(payload).not.toHaveProperty('password', '')
  })
})
