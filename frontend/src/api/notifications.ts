import { apiFetch } from './client'
import type { Notification, NotificationCategory } from './types'

export interface NotificationListParams {
  category?: NotificationCategory
  read_at__isnull?: boolean
}

export function listNotifications(params: NotificationListParams = {}): Promise<Notification[]> {
  const query = new URLSearchParams()
  if (params.category) query.set('category', params.category)
  if (params.read_at__isnull !== undefined) query.set('read_at__isnull', String(params.read_at__isnull))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return apiFetch(`/api/notifications/${suffix}`)
}

export function markNotificationRead(id: number): Promise<Notification> {
  return apiFetch(`/api/notifications/${id}/read/`, { method: 'POST' })
}
