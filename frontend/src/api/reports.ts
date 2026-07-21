import { apiFetch } from './client'
import type {
  HeadcountReport,
  LeaveUtilizationReport,
  PayrollCostReport,
  PayrollSummaryReport,
  ReportExportRecord,
  TurnoverReport,
} from './types'

function toQuery(params: Record<string, string | number | undefined>): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value))
  }
  const qs = query.toString()
  return qs ? `?${qs}` : ''
}

export function getHeadcountReport(params: { department_id?: number; employment_status?: string }): Promise<HeadcountReport> {
  return apiFetch(`/api/reports/headcount/${toQuery(params)}`)
}

export function getLeaveUtilizationReport(params: {
  department_id?: number
  leave_type_id?: number
  period_start?: string
  period_end?: string
}): Promise<LeaveUtilizationReport> {
  return apiFetch(`/api/reports/leave-utilization/${toQuery(params)}`)
}

export function getTurnoverReport(params: {
  department_id?: number
  period_start: string
  period_end: string
}): Promise<TurnoverReport> {
  return apiFetch(`/api/reports/turnover/${toQuery(params)}`)
}

export function getPayrollCostReport(params: {
  payroll_run_id?: number
  period_start?: string
  period_end?: string
}): Promise<PayrollCostReport> {
  return apiFetch(`/api/reports/payroll-cost/${toQuery(params)}`)
}

export function getPayrollSummaryReport(params: {
  payroll_run_id?: number
  period_start?: string
  period_end?: string
}): Promise<PayrollSummaryReport> {
  return apiFetch(`/api/reports/payroll-summary/${toQuery(params)}`)
}

const EXPORT_SLUGS: Record<string, string> = {
  headcount: 'headcount',
  leave_utilization: 'leave-utilization',
  turnover: 'turnover',
  payroll_cost: 'payroll-cost',
  payroll_summary: 'payroll-summary',
}

export function createReportExport(reportType: string, params: Record<string, unknown>): Promise<ReportExportRecord> {
  return apiFetch(`/api/reports/${EXPORT_SLUGS[reportType]}/export/`, { method: 'POST', body: { params } })
}

export function getReportExport(jobId: number): Promise<ReportExportRecord> {
  return apiFetch(`/api/report-exports/${jobId}/`)
}
