import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthContext } from './AuthContext'
import { ProtectedRoute } from './ProtectedRoute'

function renderWithAuth(me: Parameters<typeof AuthContext.Provider>[0]['value']['me'], requireGroup?: string) {
  return render(
    <AuthContext.Provider value={{ me, isLoading: false, refetch: async () => {}, logout: async () => {} }}>
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route element={<ProtectedRoute requireGroup={requireGroup} />}>
            <Route path="/protected" element={<div>Secret content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when unauthenticated', () => {
    renderWithAuth(null)
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the route when authenticated', () => {
    renderWithAuth({ id: 1, email: 'a@b.com', groups: [], second_factor_enrollment_pending: false })
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })

  it('redirects when authenticated but missing the required group', () => {
    renderWithAuth(
      { id: 1, email: 'a@b.com', groups: ['HR Officer'], second_factor_enrollment_pending: false },
      'System Administrator',
    )
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders when authenticated and holding the required group', () => {
    renderWithAuth(
      { id: 1, email: 'a@b.com', groups: ['System Administrator'], second_factor_enrollment_pending: false },
      'System Administrator',
    )
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })
})
