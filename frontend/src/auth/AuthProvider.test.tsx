import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../api/auth'
import { AuthProvider } from './AuthProvider'
import { useAuth } from './AuthContext'

function Probe() {
  const { me, isLoading } = useAuth()
  if (isLoading) return <div>loading</div>
  return <div>{me ? `hello ${me.email}` : 'anonymous'}</div>
}

function renderProvider() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Probe />
      </AuthProvider>
    </QueryClientProvider>,
  )
}

describe('AuthProvider', () => {
  afterEach(() => vi.restoreAllMocks())

  it('bootstraps CSRF then loads /auth/me/, exposing the result', async () => {
    const bootstrapSpy = vi.spyOn(authApi, 'bootstrapCsrf').mockResolvedValue(undefined)
    vi.spyOn(authApi, 'fetchMe').mockResolvedValue({
      id: 1,
      email: 'a@b.com',
      groups: [],
      is_employee: true, is_manager: false, second_factor_enrollment_pending: false,
    })

    renderProvider()

    await waitFor(() => expect(screen.getByText('hello a@b.com')).toBeInTheDocument())
    expect(bootstrapSpy).toHaveBeenCalled()
  })

  it('exposes me as null when fetchMe returns 401', async () => {
    vi.spyOn(authApi, 'bootstrapCsrf').mockResolvedValue(undefined)
    vi.spyOn(authApi, 'fetchMe').mockRejectedValue(new Error('unauthenticated'))

    renderProvider()

    await waitFor(() => expect(screen.getByText('anonymous')).toBeInTheDocument())
  })
})
