import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../api/auth'
import { ApiError } from '../../api/client'
import { AuthContext } from '../../auth/AuthContext'
import { LoginPage } from './LoginPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const refetch = vi.fn().mockResolvedValue(undefined)
  return {
    refetch,
    ...render(
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={{ me: null, isLoading: false, refetch, logout: async () => {} }}>
          <MemoryRouter>
            <LoginPage />
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>,
    ),
  }
}

describe('LoginPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits credentials and refetches the session on success', async () => {
    const loginSpy = vi.spyOn(authApi, 'login').mockResolvedValue({
      id: 1,
      email: 'a@b.com',
      groups: [],
    })
    const { refetch } = renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(loginSpy).toHaveBeenCalledWith('a@b.com', 'secret123'))
    await waitFor(() => expect(refetch).toHaveBeenCalled())
  })

  it('shows the invalid-credentials error', async () => {
    vi.spyOn(authApi, 'login').mockRejectedValue(new ApiError(401, 'Invalid credentials.', 'not_authenticated'))
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.type(screen.getByLabelText(/password/i), 'wrong')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText('Invalid credentials.')).toBeInTheDocument()
  })

  it('shows a not-yet-supported message when the account requires second-factor verification', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({ second_factor_required: true })
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'admin@b.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText(/second-factor verification isn't available/i)).toBeInTheDocument()
  })
})
