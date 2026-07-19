import { apiFetch } from './client'
import type { Department, JobTitle } from './types'

export function listDepartments(): Promise<Department[]> {
  return apiFetch('/api/departments/')
}

export function createDepartment(data: { name: string; is_active?: boolean }): Promise<Department> {
  return apiFetch('/api/departments/', { method: 'POST', body: data })
}

export function updateDepartment(
  id: number,
  data: Partial<{ name: string; is_active: boolean }>,
): Promise<Department> {
  return apiFetch(`/api/departments/${id}/`, { method: 'PATCH', body: data })
}

export function listJobTitles(): Promise<JobTitle[]> {
  return apiFetch('/api/job-titles/')
}

export function createJobTitle(data: { name: string; is_active?: boolean }): Promise<JobTitle> {
  return apiFetch('/api/job-titles/', { method: 'POST', body: data })
}

export function updateJobTitle(id: number, data: Partial<{ name: string; is_active: boolean }>): Promise<JobTitle> {
  return apiFetch(`/api/job-titles/${id}/`, { method: 'PATCH', body: data })
}
