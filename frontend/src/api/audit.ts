import { apiFetch } from './client'
import type { AuditLogEntry, PaginatedResponse } from './types'

export function listAuditLog(params?: { category?: string; page?: number }): Promise<PaginatedResponse<AuditLogEntry>> {
  const query = new URLSearchParams()
  if (params?.category) query.set('category', params.category)
  if (params?.page) query.set('page', String(params.page))
  const qs = query.toString()
  return apiFetch(`/api/audit-log/${qs ? `?${qs}` : ''}`)
}
