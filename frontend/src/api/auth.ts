import { apiFetch } from './client'
import type { LoginResponse, Me } from './types'

export function bootstrapCsrf(): Promise<void> {
  return apiFetch('/api/auth/csrf/')
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch('/api/auth/login/', { method: 'POST', body: { email, password } })
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
