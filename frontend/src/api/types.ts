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
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn'
  issued_at: string
  decided_at: string | null
  document_object_key: string | null
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
