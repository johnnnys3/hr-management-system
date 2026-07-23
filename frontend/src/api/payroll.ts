import { apiFetch } from './client'
import type { Payslip, PayrollRun } from './types'

export function listPayrollRuns(): Promise<PayrollRun[]> {
  return apiFetch('/api/payroll-runs/')
}

export function getPayrollRun(id: number): Promise<PayrollRun> {
  return apiFetch(`/api/payroll-runs/${id}/`)
}

export function createPayrollRun(data: { period_start: string; period_end: string }): Promise<PayrollRun> {
  return apiFetch('/api/payroll-runs/', { method: 'POST', body: data })
}

export function calculatePayrollRun(id: number): Promise<void> {
  return apiFetch(`/api/payroll-runs/${id}/calculate/`, { method: 'POST' })
}

export function submitPayrollRunForApproval(id: number): Promise<PayrollRun> {
  return apiFetch(`/api/payroll-runs/${id}/submit-for-approval/`, { method: 'POST' })
}

export function approvePayrollRun(id: number): Promise<PayrollRun> {
  return apiFetch(`/api/payroll-runs/${id}/approve/`, { method: 'POST' })
}

export function finalizePayrollRun(id: number): Promise<void> {
  return apiFetch(`/api/payroll-runs/${id}/finalize/`, { method: 'POST' })
}

// /api/payslips/ has no server-side payroll_run filter — filter client-side.
export async function listPayslipsForRun(payrollRunId: number): Promise<Payslip[]> {
  const payslips = await apiFetch<Payslip[]>('/api/payslips/')
  return payslips.filter((p) => p.payroll_run === payrollRunId)
}
