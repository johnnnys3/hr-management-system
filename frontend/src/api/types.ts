export interface Me {
  id: number
  email: string
  groups: string[]
  second_factor_enrollment_pending: boolean
}

export interface LoginSuccess {
  id: number
  email: string
  groups: string[]
  second_factor_enrollment_required?: boolean
}

export interface LoginSecondFactorRequired {
  second_factor_required: true
}

export type LoginResponse = LoginSuccess | LoginSecondFactorRequired

export function isSecondFactorRequired(response: LoginResponse): response is LoginSecondFactorRequired {
  return 'second_factor_required' in response
}

export interface UserAccount {
  id: number
  email: string
  is_active: boolean
  groups: string[]
  created_at: string
  updated_at: string
}

export interface SecondFactorEnrollResponse {
  provisioning_uri: string
}

export interface SecondFactorRecoveryRequestRecord {
  id: number
  status: 'pending' | 'approved' | 'denied'
  requested_at: string
  decided_at: string | null
}

export interface Department {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface JobTitle {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type EmploymentStatus = 'active' | 'on_leave' | 'suspended' | 'terminated' | 'resigned' | 'retired'

export interface Employee {
  id: number
  employee_number: string
  first_name: string
  last_name: string
  date_of_birth: string
  department: number
  job_title: number
  employment_status: EmploymentStatus
  hire_date: string
  created_at: string
  updated_at: string
}

export interface EmploymentHistoryEntry {
  id: number
  employee: number
  event_type: 'hired' | 'status_change' | 'department_change' | 'job_title_change' | 'manager_change'
  effective_date: string
  previous_value: Record<string, unknown> | null
  new_value: Record<string, unknown>
  recorded_by: number | null
  created_at: string
}

export interface EmployeeDocument {
  id: number
  employee: number
  document_type: string
  file_name: string
  content_type: string
  size_bytes: number
  uploaded_by: number | null
  created_at: string
}

export interface EmergencyContact {
  id: number
  employee: number
  name: string
  relationship: string
  phone: string
  email: string | null
  is_primary: boolean
  created_at: string
  updated_at: string
}

export interface ReportingRelationship {
  id: number
  employee: number
  manager_employee: number
  effective_from: string
}

export type RequisitionStatus = 'draft' | 'pending_approval' | 'approved' | 'rejected' | 'closed'

export interface JobRequisition {
  id: number
  department: number
  job_title: number
  requested_by: number
  status: RequisitionStatus
  approved_by: number | null
  created_at: string
  updated_at: string
}

export interface JobPosting {
  id: number
  requisition: number
  title: string
  description: string
  channel: 'internal' | 'external'
  published_at: string | null
  closed_at: string | null
  created_at: string
  updated_at: string
}

export interface Candidate {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string | null
  resume_object_key: string | null
  created_at: string
}

export type ApplicationStage = 'applied' | 'screening' | 'interview' | 'offer' | 'hired' | 'rejected'

export interface CandidateApplication {
  id: number
  candidate: number
  posting: number
  stage: ApplicationStage
  applied_at: string
  updated_at: string
}

export interface Interview {
  id: number
  application: number
  interviewer_employee: number | null
  scheduled_at: string
  status: 'scheduled' | 'completed' | 'cancelled'
  feedback: string | null
  created_at: string
  updated_at: string
}

export interface OfferLetter {
  id: number
  application: number
  offered_salary: string
  offered_pay_grade: number | null
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn'
  issued_at: string
  decided_at: string | null
  document_object_key: string | null
}

export interface PayGradeOption {
  id: number
  name: string
  salary_structure_name: string
}

export type NotificationCategory = 'pending_task' | 'request_update'

export interface Notification {
  id: number
  category: NotificationCategory
  channel: 'in_app' | 'email' | 'both'
  subject: string
  body: string
  related_type: string | null
  related_id: number | null
  read_at: string | null
  created_at: string
}

export interface OnboardingChecklist {
  id: number
  employee: number
  application: number | null
  started_at: string
  completed_at: string | null
}

export type OnboardingTaskStatus = 'pending' | 'in_progress' | 'completed' | 'skipped'

export interface OnboardingTask {
  id: number
  checklist: number
  name: string
  is_required: boolean
  status: OnboardingTaskStatus
  completed_by: number | null
  completed_at: string | null
  created_at: string
}

export interface RoleGrantRequestRecord {
  id: number
  requester: number
  subject: number
  role: number
  status: 'pending' | 'approved' | 'refused'
  approver: number | null
  requested_at: string
  decided_at: string | null
}

export interface LeaveType {
  id: number
  name: string
  requires_approval: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LeaveBalance {
  id: number
  employee: number
  leave_type: number
  period_start: string
  period_end: string
  entitled_days: string
  used_days: string
  created_at: string
  updated_at: string
}

export type LeaveRequestStatus = 'pending' | 'approved' | 'rejected' | 'cancelled'

export interface LeaveRequest {
  id: number
  employee: number
  leave_type: number
  start_date: string
  end_date: string
  reason: string | null
  status: LeaveRequestStatus
  approved_by: number | null
  decided_at: string | null
  created_at: string
}

export interface DashboardAggregates {
  headcount: { total: number }
  leave_utilization: { entitled_days: number; used_days: number }
  turnover: { hires: number; terminations: number }
  payroll_cost: { gross_pay: number; net_pay: number }
  payroll_summary: { gross_pay: number; net_pay: number; payslip_count: number }
}

export interface DashboardData {
  aggregates?: DashboardAggregates
  leave_balance?: LeaveBalance[]
  pending_tasks?: Notification[]
  team?: { pending_leave_requests: number }
}

export type AuditLogCategory =
  | 'login_attempt'
  | 'record_change'
  | 'payroll_action'
  | 'approval'
  | 'permission_change'
  | 'second_factor_event'

export interface AuditLogEntry {
  id: number
  actor: number | null
  category: AuditLogCategory
  target_type: string | null
  target_id: number | null
  action: string
  detail: Record<string, unknown> | null
  occurred_at: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface HeadcountReport {
  aggregate: { total: number }
  breakdown?: { department_id: number; department__name: string; count: number }[]
}

export interface LeaveUtilizationReport {
  aggregate: { entitled_days: number; used_days: number }
  breakdown?: { leave_type_id: number; leave_type__name: string; entitled_days: number; used_days: number }[]
}

export interface TurnoverReport {
  aggregate: { hires: number; terminations: number }
  breakdown?: {
    hires_by_department: { department_id: number; department__name: string; count: number }[]
    terminations_by_department: { employee__department_id: number; employee__department__name: string; count: number }[]
  }
}

export interface PayrollCostReport {
  aggregate: { gross_pay: number; net_pay: number }
  breakdown?: { employee__department_id: number; employee__department__name: string; gross_pay: number; net_pay: number }[]
}

export interface PayrollSummaryReport {
  aggregate: { gross_pay: number; net_pay: number; payslip_count: number }
  breakdown?: { id: number; period_start: string; period_end: string; gross_pay: number; net_pay: number }[]
}

export type ReportType = 'headcount' | 'leave_utilization' | 'turnover' | 'payroll_cost' | 'payroll_summary'
export type ReportExportStatus = 'pending' | 'complete' | 'failed'

export interface ReportExportRecord {
  id: number
  report_type: ReportType
  params: Record<string, unknown>
  status: ReportExportStatus
  download_url: string | null
  failed_reason: string | null
  generated_at: string | null
  created_at: string
}
