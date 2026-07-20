import { apiFetch } from './client'
import type { Employee, ReportingRelationship } from './types'

export function listReportingRelationships(managerEmployeeId?: number): Promise<ReportingRelationship[]> {
  const suffix = managerEmployeeId ? `?manager_employee_id=${managerEmployeeId}` : ''
  return apiFetch(`/api/reporting-relationships/${suffix}`)
}

export function listDirectReports(employeeId: number): Promise<Employee[]> {
  return apiFetch(`/api/employees/${employeeId}/direct-reports/`)
}

export function changeManager(employeeId: number, managerEmployeeId: number): Promise<ReportingRelationship> {
  return apiFetch(`/api/employees/${employeeId}/manager/`, {
    method: 'PATCH',
    body: { manager_employee_id: managerEmployeeId },
  })
}
