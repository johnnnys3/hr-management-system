import { apiFetch } from './client'
import type { EmergencyContact, Employee, EmployeeDocument, EmploymentHistoryEntry } from './types'

export interface EmployeeListParams {
  department_id?: number
  job_title_id?: number
  employment_status?: string
  search?: string
}

export function listEmployees(params: EmployeeListParams = {}): Promise<Employee[]> {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') query.set(key, String(value))
  })
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return apiFetch(`/api/employees/${suffix}`)
}

export function getEmployee(id: number): Promise<Employee> {
  return apiFetch(`/api/employees/${id}/`)
}

export function createEmployee(data: {
  employee_number: string
  first_name: string
  last_name: string
  date_of_birth: string
  department: number
  job_title: number
  hire_date: string
}): Promise<Employee> {
  return apiFetch('/api/employees/', { method: 'POST', body: data })
}

export function updateEmployee(id: number, data: Partial<Omit<Employee, 'id'>>): Promise<Employee> {
  return apiFetch(`/api/employees/${id}/`, { method: 'PATCH', body: data })
}

export function listEmploymentHistory(employeeId: number): Promise<EmploymentHistoryEntry[]> {
  return apiFetch(`/api/employees/${employeeId}/employment-history/`)
}

export function listEmployeeDocuments(employeeId: number): Promise<EmployeeDocument[]> {
  return apiFetch(`/api/employees/${employeeId}/documents/`)
}

export function uploadEmployeeDocument(
  employeeId: number,
  documentType: string,
  file: File,
): Promise<EmployeeDocument> {
  const body = new FormData()
  body.set('document_type', documentType)
  body.set('file', file)
  return apiFetch(`/api/employees/${employeeId}/documents/`, { method: 'POST', body })
}

export function getEmployeeDocumentDownloadUrl(employeeId: number, docId: number): Promise<{ url: string }> {
  return apiFetch(`/api/employees/${employeeId}/documents/${docId}/download/`)
}

export function listEmergencyContacts(employeeId: number): Promise<EmergencyContact[]> {
  return apiFetch(`/api/employees/${employeeId}/emergency-contacts/`)
}

export function createEmergencyContact(
  employeeId: number,
  data: { name: string; relationship: string; phone: string; email?: string; is_primary?: boolean },
): Promise<EmergencyContact> {
  return apiFetch(`/api/employees/${employeeId}/emergency-contacts/`, { method: 'POST', body: data })
}

export function updateEmergencyContact(
  employeeId: number,
  contactId: number,
  data: Partial<{ name: string; relationship: string; phone: string; email: string; is_primary: boolean }>,
): Promise<EmergencyContact> {
  return apiFetch(`/api/employees/${employeeId}/emergency-contacts/${contactId}/`, { method: 'PATCH', body: data })
}
