import { apiFetch } from './client'
import type { RoleGrantRequestRecord, UserAccount } from './types'

export function listUsers(): Promise<UserAccount[]> {
  return apiFetch('/api/users/')
}

export function createUser(data: { email: string; password: string; is_active?: boolean }): Promise<UserAccount> {
  return apiFetch('/api/users/', { method: 'POST', body: data })
}

export function updateUser(
  id: number,
  data: Partial<{ email: string; password: string; is_active: boolean }>,
): Promise<UserAccount> {
  return apiFetch(`/api/users/${id}/`, { method: 'PATCH', body: data })
}

export function listRoleGrantRequests(): Promise<RoleGrantRequestRecord[]> {
  return apiFetch('/api/role-grant-requests/')
}

export function createRoleGrantRequest(subjectUserId: number, roleId: number): Promise<RoleGrantRequestRecord> {
  return apiFetch('/api/role-grant-requests/', {
    method: 'POST',
    body: { subject_user_id: subjectUserId, role_id: roleId },
  })
}

export function decideRoleGrantRequest(
  id: number,
  decision: 'approved' | 'refused',
): Promise<RoleGrantRequestRecord> {
  return apiFetch(`/api/role-grant-requests/${id}/decide/`, { method: 'POST', body: { decision } })
}
