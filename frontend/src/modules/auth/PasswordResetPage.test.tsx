import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../api/auth'
import { PasswordResetPage } from './PasswordResetPage'

function renderPage(initialEntries = ['/password-reset']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <PasswordResetPage />
    </MemoryRouter>,
  )
}

describe('PasswordResetPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('submits a reset request and shows a uniform confirmation', async () => {
    const spy = vi.spyOn(authApi, 'requestPasswordReset').mockResolvedValue(undefined)
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/email/i), 'a@b.com')
    await user.click(screen.getByRole('button', { name: /send reset link/i }))

    await waitFor(() => expect(spy).toHaveBeenCalledWith('a@b.com'))
    expect(await screen.findByText(/if an account exists/i)).toBeInTheDocument()
  })

  it('shows the confirm form when uid and token are present in the URL, and submits it', async () => {
    const spy = vi.spyOn(authApi, 'confirmPasswordReset').mockResolvedValue(undefined)
    renderPage(['/password-reset?uid=abc&token=xyz'])
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/new password/i), 'newpass123')
    await user.click(screen.getByRole('button', { name: /set new password/i }))

    await waitFor(() => expect(spy).toHaveBeenCalledWith('abc', 'xyz', 'newpass123'))
    expect(await screen.findByText(/password has been reset/i)).toBeInTheDocument()
  })
})
