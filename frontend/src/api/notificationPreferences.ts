import { apiFetch } from './client'
import type { NotificationPreference } from './types'

export function getNotificationPreference(): Promise<NotificationPreference> {
  return apiFetch('/api/notification-preferences/me/')
}

export function updateNotificationPreference(
  patch: Partial<NotificationPreference>,
): Promise<NotificationPreference> {
  return apiFetch('/api/notification-preferences/me/', { method: 'PATCH', body: patch })
}

export function requestPhoneVerification(phoneNumber: string): Promise<void> {
  return apiFetch('/api/auth/phone/', { method: 'POST', body: { phone_number: phoneNumber } })
}

export function confirmPhoneVerification(code: string): Promise<void> {
  return apiFetch('/api/auth/phone/confirm/', { method: 'POST', body: { code } })
}
