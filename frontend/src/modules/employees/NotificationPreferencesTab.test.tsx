import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as api from '../../api/notificationPreferences'
import { AuthContext } from '../../auth/AuthContext'
import { NotificationPreferencesTab } from './NotificationPreferencesTab'

vi.mock('../../api/notificationPreferences')

function renderTab() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: {
            id: 1,
            email: 'ada@b.com',
            groups: [],
            is_employee: true,
            is_manager: false,
            second_factor_enrollment_pending: false,
            phone_verified_at: null,
          },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <NotificationPreferencesTab />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('NotificationPreferencesTab', () => {
  beforeEach(() => {
    vi.mocked(api.getNotificationPreference).mockResolvedValue({ email_enabled: true, sms_enabled: false })
  })

  it('renders email enabled and sms disabled from the loaded preference', async () => {
    renderTab()
    expect(await screen.findByRole('switch', { name: /email/i })).toBeChecked()
    expect(screen.getByRole('switch', { name: /sms/i })).not.toBeChecked()
  })

  it('disables the sms switch and shows a verify prompt when phone is unverified', async () => {
    renderTab()
    await screen.findByRole('switch', { name: /email/i })
    expect(screen.getByRole('switch', { name: /sms/i })).toBeDisabled()
    expect(screen.getByText(/verify your phone number/i)).toBeInTheDocument()
  })

  it('requests a verification code and confirms it', async () => {
    const user = userEvent.setup()
    vi.mocked(api.requestPhoneVerification).mockResolvedValue(undefined)
    vi.mocked(api.confirmPhoneVerification).mockResolvedValue(undefined)
    renderTab()
    await screen.findByRole('switch', { name: /email/i })

    await user.type(screen.getByLabelText(/phone number/i), '+15559998888')
    await user.click(screen.getByRole('button', { name: /send code/i }))
    expect(api.requestPhoneVerification).toHaveBeenCalledWith('+15559998888', expect.anything())

    await waitFor(() => expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument())
    await user.type(screen.getByLabelText(/verification code/i), '123456')
    await user.click(screen.getByRole('button', { name: /confirm/i }))
    expect(api.confirmPhoneVerification).toHaveBeenCalledWith('123456', expect.anything())
  })

  it('toggles email preference on change', async () => {
    const user = userEvent.setup()
    vi.mocked(api.updateNotificationPreference).mockResolvedValue({ email_enabled: false, sms_enabled: false })
    renderTab()

    const emailSwitch = await screen.findByRole('switch', { name: /email/i })
    await user.click(emailSwitch)

    expect(api.updateNotificationPreference).toHaveBeenCalledWith({ email_enabled: false }, expect.anything())
  })
})
