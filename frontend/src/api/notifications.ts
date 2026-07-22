import { apiFetch } from './client'
import type { Notification, NotificationCategory } from './types'

export interface NotificationListParams {
  category?: NotificationCategory
  read_at__isnull?: boolean
}

interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export async function listNotifications(params: NotificationListParams = {}): Promise<Notification[]> {
  const query = new URLSearchParams()
  if (params.category) query.set('category', params.category)
  if (params.read_at__isnull !== undefined) query.set('read_at__isnull', String(params.read_at__isnull))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  const response = await apiFetch<PaginatedResponse<Notification>>(`/api/notifications/${suffix}`)
  return response.results
}

export function markNotificationRead(id: number): Promise<Notification> {
  return apiFetch(`/api/notifications/${id}/read/`, { method: 'POST' })
}
