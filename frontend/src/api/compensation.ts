import { apiFetch } from './client'
import type { CompensationRecord, PayGrade, SalaryStructure } from './types'

export function listSalaryStructures(): Promise<SalaryStructure[]> {
  return apiFetch('/api/salary-structures/')
}

export function createSalaryStructure(data: { name: string; description?: string; effective_from: string }): Promise<SalaryStructure> {
  return apiFetch('/api/salary-structures/', { method: 'POST', body: data })
}

export function listPayGrades(): Promise<PayGrade[]> {
  return apiFetch('/api/pay-grades/')
}

export function createPayGrade(data: {
  salary_structure: number
  name: string
  min_salary: string
  max_salary: string
}): Promise<PayGrade> {
  return apiFetch('/api/pay-grades/', { method: 'POST', body: data })
}

export function listCompensationRecords(employeeId: number): Promise<CompensationRecord[]> {
  return apiFetch(`/api/employees/${employeeId}/compensation-records/`)
}

export function createCompensationRecord(
  employeeId: number,
  data: { pay_grade?: number | null; base_salary: string; currency?: string; effective_from: string },
): Promise<CompensationRecord> {
  return apiFetch(`/api/employees/${employeeId}/compensation-records/`, { method: 'POST', body: data })
}
