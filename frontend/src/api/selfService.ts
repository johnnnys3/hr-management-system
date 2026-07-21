import { apiFetch } from './client'
import type { Employee } from './types'

export function getMyProfile(): Promise<Employee> {
  return apiFetch('/api/employees/me/')
}

export function updateMyProfile(
  data: Partial<{ first_name: string; last_name: string; date_of_birth: string }>,
): Promise<Employee> {
  return apiFetch('/api/employees/me/', { method: 'PATCH', body: data })
}
