import { apiFetch } from './client'
import type { LoginResponse, Me, SecondFactorEnrollResponse, SecondFactorRecoveryRequestRecord } from './types'

export function bootstrapCsrf(): Promise<void> {
  return apiFetch('/api/auth/csrf/')
}

export function login(email: string, password: string, totpCode?: string): Promise<LoginResponse> {
  return apiFetch('/api/auth/login/', {
    method: 'POST',
    body: totpCode ? { email, password, totp_code: totpCode } : { email, password },
  })
}

export function enrollSecondFactor(): Promise<SecondFactorEnrollResponse> {
  return apiFetch('/api/auth/second-factor/', { method: 'POST' })
}

export function requestSecondFactorRecovery(): Promise<SecondFactorRecoveryRequestRecord> {
  return apiFetch('/api/auth/second-factor/recovery-requests/', { method: 'POST' })
}

export function decideSecondFactorRecovery(
  id: number,
  decision: 'approved' | 'denied',
): Promise<SecondFactorRecoveryRequestRecord> {
  return apiFetch(`/api/auth/second-factor/recovery-requests/${id}/decide/`, {
    method: 'POST',
    body: { decision },
  })
}

export function logout(): Promise<void> {
  return apiFetch('/api/auth/logout/', { method: 'POST' })
}

export function fetchMe(): Promise<Me> {
  return apiFetch('/api/auth/me/')
}

export function requestPasswordReset(email: string): Promise<void> {
  return apiFetch('/api/auth/password-reset/', { method: 'POST', body: { email } })
}

export function confirmPasswordReset(uid: string, token: string, password: string): Promise<void> {
  return apiFetch('/api/auth/password-reset/confirm/', { method: 'POST', body: { uid, token, password } })
}
