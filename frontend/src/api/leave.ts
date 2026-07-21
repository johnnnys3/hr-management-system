import { apiFetch } from './client'
import type { LeaveBalance, LeaveRequest, LeaveType } from './types'

export function listLeaveTypes(): Promise<LeaveType[]> {
  return apiFetch('/api/leave-types/')
}

export function listLeaveBalances(): Promise<LeaveBalance[]> {
  return apiFetch('/api/leave-balances/')
}

export function listLeaveRequests(params?: { status?: string; leave_type_id?: number }): Promise<LeaveRequest[]> {
  const query = new URLSearchParams()
  if (params?.status) query.set('status', params.status)
  if (params?.leave_type_id) query.set('leave_type_id', String(params.leave_type_id))
  const qs = query.toString()
  return apiFetch(`/api/leave-requests/${qs ? `?${qs}` : ''}`)
}

export function createLeaveRequest(data: {
  leave_type: number
  start_date: string
  end_date: string
  reason?: string
}): Promise<LeaveRequest> {
  return apiFetch('/api/leave-requests/', { method: 'POST', body: data })
}

export function correctLeaveRequest(
  id: number,
  data: Partial<{ leave_type: number; start_date: string; end_date: string; reason: string; status: 'cancelled' }>,
): Promise<LeaveRequest> {
  return apiFetch(`/api/leave-requests/${id}/`, { method: 'PATCH', body: data })
}

export function approveLeaveRequest(id: number): Promise<LeaveRequest> {
  return apiFetch(`/api/leave-requests/${id}/approve/`, { method: 'POST' })
}

export function rejectLeaveRequest(id: number): Promise<LeaveRequest> {
  return apiFetch(`/api/leave-requests/${id}/reject/`, { method: 'POST' })
}

export function cancelLeaveRequest(id: number): Promise<LeaveRequest> {
  return apiFetch(`/api/leave-requests/${id}/cancel/`, { method: 'POST' })
}

export function getLeaveCalendar(): Promise<LeaveRequest[]> {
  return apiFetch('/api/leave-calendar/')
}
