import { apiFetch } from './client'
import type { DashboardData } from './types'

export function getDashboard(): Promise<DashboardData> {
  return apiFetch('/api/dashboard/')
}
