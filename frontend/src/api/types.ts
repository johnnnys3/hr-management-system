import { z } from 'zod'

// docs/08-testing-plan.md §3.3: a Zod schema per API resource, checked
// against docs/06-api-contracts.md's documented shape by
// src/api/types.test.ts. Schemas are the single source of truth — every
// exported `type` below is derived via z.infer, not hand-duplicated, so
// the shape can't drift between the two.

export const MeSchema = z.object({
  id: z.number(),
  email: z.string(),
  groups: z.array(z.string()),
  is_employee: z.boolean(),
  is_manager: z.boolean(),
  second_factor_enrollment_pending: z.boolean(),
  phone_verified_at: z.string().nullable().optional(),
})
export type Me = z.infer<typeof MeSchema>

export const LoginSuccessSchema = z.object({
  id: z.number(),
  email: z.string(),
  groups: z.array(z.string()),
  second_factor_enrollment_required: z.boolean().optional(),
})
export type LoginSuccess = z.infer<typeof LoginSuccessSchema>

export const LoginSecondFactorRequiredSchema = z.object({
  second_factor_required: z.literal(true),
})
export type LoginSecondFactorRequired = z.infer<typeof LoginSecondFactorRequiredSchema>

export const LoginResponseSchema = z.union([LoginSuccessSchema, LoginSecondFactorRequiredSchema])
export type LoginResponse = z.infer<typeof LoginResponseSchema>

export function isSecondFactorRequired(response: LoginResponse): response is LoginSecondFactorRequired {
  return 'second_factor_required' in response
}

export const UserAccountSchema = z.object({
  id: z.number(),
  email: z.string(),
  is_active: z.boolean(),
  groups: z.array(z.string()),
  employee_name: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type UserAccount = z.infer<typeof UserAccountSchema>

export const SecondFactorEnrollResponseSchema = z.object({
  provisioning_uri: z.string(),
})
export type SecondFactorEnrollResponse = z.infer<typeof SecondFactorEnrollResponseSchema>

export const SecondFactorRecoveryRequestRecordSchema = z.object({
  id: z.number(),
  status: z.enum(['pending', 'approved', 'denied']),
  requested_at: z.string(),
  decided_at: z.string().nullable(),
})
export type SecondFactorRecoveryRequestRecord = z.infer<typeof SecondFactorRecoveryRequestRecordSchema>

export const DepartmentSchema = z.object({
  id: z.number(),
  name: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type Department = z.infer<typeof DepartmentSchema>

export const JobTitleSchema = z.object({
  id: z.number(),
  name: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type JobTitle = z.infer<typeof JobTitleSchema>

export const EmploymentStatusSchema = z.enum(['active', 'on_leave', 'suspended', 'terminated', 'resigned', 'retired'])
export type EmploymentStatus = z.infer<typeof EmploymentStatusSchema>

export const EmployeeSchema = z.object({
  id: z.number(),
  employee_number: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  date_of_birth: z.string(),
  department: z.number(),
  job_title: z.number(),
  employment_status: EmploymentStatusSchema,
  hire_date: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type Employee = z.infer<typeof EmployeeSchema>

export const EmploymentHistoryEntrySchema = z.object({
  id: z.number(),
  employee: z.number(),
  event_type: z.enum(['hired', 'status_change', 'department_change', 'job_title_change', 'manager_change']),
  effective_date: z.string(),
  previous_value: z.record(z.string(), z.unknown()).nullable(),
  new_value: z.record(z.string(), z.unknown()),
  recorded_by: z.number().nullable(),
  created_at: z.string(),
})
export type EmploymentHistoryEntry = z.infer<typeof EmploymentHistoryEntrySchema>

export const EmployeeDocumentSchema = z.object({
  id: z.number(),
  employee: z.number(),
  document_type: z.string(),
  file_name: z.string(),
  content_type: z.string(),
  size_bytes: z.number(),
  uploaded_by: z.number().nullable(),
  created_at: z.string(),
})
export type EmployeeDocument = z.infer<typeof EmployeeDocumentSchema>

export const EmergencyContactSchema = z.object({
  id: z.number(),
  employee: z.number(),
  name: z.string(),
  relationship: z.string(),
  phone: z.string(),
  email: z.string().nullable(),
  is_primary: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type EmergencyContact = z.infer<typeof EmergencyContactSchema>

export const ReportingRelationshipSchema = z.object({
  id: z.number(),
  employee: z.number(),
  manager_employee: z.number(),
  effective_from: z.string(),
})
export type ReportingRelationship = z.infer<typeof ReportingRelationshipSchema>

export const RequisitionStatusSchema = z.enum(['draft', 'pending_approval', 'approved', 'rejected', 'closed'])
export type RequisitionStatus = z.infer<typeof RequisitionStatusSchema>

export const JobRequisitionSchema = z.object({
  id: z.number(),
  department: z.number(),
  job_title: z.number(),
  requested_by: z.number(),
  status: RequisitionStatusSchema,
  approved_by: z.number().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type JobRequisition = z.infer<typeof JobRequisitionSchema>

export const JobPostingSchema = z.object({
  id: z.number(),
  requisition: z.number(),
  title: z.string(),
  description: z.string(),
  channel: z.enum(['internal', 'external']),
  published_at: z.string().nullable(),
  closed_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type JobPosting = z.infer<typeof JobPostingSchema>

export const CandidateSchema = z.object({
  id: z.number(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  phone: z.string().nullable(),
  resume_object_key: z.string().nullable(),
  created_at: z.string(),
})
export type Candidate = z.infer<typeof CandidateSchema>

export const ApplicationStageSchema = z.enum(['applied', 'screening', 'interview', 'offer', 'hired', 'rejected'])
export type ApplicationStage = z.infer<typeof ApplicationStageSchema>

export const CandidateApplicationSchema = z.object({
  id: z.number(),
  candidate: z.number(),
  posting: z.number(),
  stage: ApplicationStageSchema,
  applied_at: z.string(),
  updated_at: z.string(),
})
export type CandidateApplication = z.infer<typeof CandidateApplicationSchema>

export const InterviewSchema = z.object({
  id: z.number(),
  application: z.number(),
  interviewer_employee: z.number().nullable(),
  scheduled_at: z.string(),
  status: z.enum(['scheduled', 'completed', 'cancelled']),
  feedback: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type Interview = z.infer<typeof InterviewSchema>

export const OfferLetterSchema = z.object({
  id: z.number(),
  application: z.number(),
  offered_salary: z.string(),
  offered_pay_grade: z.number().nullable(),
  status: z.enum(['pending', 'accepted', 'rejected', 'withdrawn']),
  issued_at: z.string(),
  decided_at: z.string().nullable(),
  document_object_key: z.string().nullable(),
})
export type OfferLetter = z.infer<typeof OfferLetterSchema>

export const NotificationCategorySchema = z.enum(['pending_task', 'request_update'])
export type NotificationCategory = z.infer<typeof NotificationCategorySchema>

export const NotificationSchema = z.object({
  id: z.number(),
  category: NotificationCategorySchema,
  channel: z.enum(['in_app', 'email', 'both']),
  subject: z.string(),
  body: z.string(),
  related_type: z.string().nullable(),
  related_id: z.number().nullable(),
  read_at: z.string().nullable(),
  created_at: z.string(),
})
export type Notification = z.infer<typeof NotificationSchema>

export const NotificationPreferenceSchema = z.object({
  email_enabled: z.boolean(),
  sms_enabled: z.boolean(),
})
export type NotificationPreference = z.infer<typeof NotificationPreferenceSchema>

export const OnboardingChecklistSchema = z.object({
  id: z.number(),
  employee: z.number(),
  application: z.number().nullable(),
  started_at: z.string(),
  completed_at: z.string().nullable(),
})
export type OnboardingChecklist = z.infer<typeof OnboardingChecklistSchema>

export const OnboardingTaskStatusSchema = z.enum(['pending', 'in_progress', 'completed', 'skipped'])
export type OnboardingTaskStatus = z.infer<typeof OnboardingTaskStatusSchema>

export const OnboardingTaskSchema = z.object({
  id: z.number(),
  checklist: z.number(),
  name: z.string(),
  is_required: z.boolean(),
  status: OnboardingTaskStatusSchema,
  completed_by: z.number().nullable(),
  completed_at: z.string().nullable(),
  created_at: z.string(),
})
export type OnboardingTask = z.infer<typeof OnboardingTaskSchema>

export const RoleGrantRequestRecordSchema = z.object({
  id: z.number(),
  requester: z.number(),
  subject: z.number(),
  role: z.number(),
  status: z.enum(['pending', 'approved', 'refused']),
  approver: z.number().nullable(),
  requested_at: z.string(),
  decided_at: z.string().nullable(),
  requester_email: z.string(),
  subject_email: z.string(),
  subject_name: z.string().nullable(),
  role_name: z.string(),
})
export type RoleGrantRequestRecord = z.infer<typeof RoleGrantRequestRecordSchema>

export const LeaveTypeSchema = z.object({
  id: z.number(),
  name: z.string(),
  requires_approval: z.boolean(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type LeaveType = z.infer<typeof LeaveTypeSchema>

export const LeaveBalanceSchema = z.object({
  id: z.number(),
  employee: z.number(),
  leave_type: z.number(),
  period_start: z.string(),
  period_end: z.string(),
  entitled_days: z.string(),
  used_days: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type LeaveBalance = z.infer<typeof LeaveBalanceSchema>

export const LeaveRequestStatusSchema = z.enum(['pending', 'approved', 'rejected', 'cancelled'])
export type LeaveRequestStatus = z.infer<typeof LeaveRequestStatusSchema>

export const LeaveRequestSchema = z.object({
  id: z.number(),
  employee: z.number(),
  leave_type: z.number(),
  start_date: z.string(),
  end_date: z.string(),
  reason: z.string().nullable(),
  status: LeaveRequestStatusSchema,
  approved_by: z.number().nullable(),
  decided_at: z.string().nullable(),
  created_at: z.string(),
})
export type LeaveRequest = z.infer<typeof LeaveRequestSchema>

export const DashboardAggregatesSchema = z.object({
  headcount: z.object({ total: z.number() }),
  leave_utilization: z.object({ entitled_days: z.number(), used_days: z.number() }),
  turnover: z.object({ hires: z.number(), terminations: z.number() }),
  payroll_cost: z.object({ gross_pay: z.number(), net_pay: z.number() }),
  payroll_summary: z.object({ gross_pay: z.number(), net_pay: z.number(), payslip_count: z.number() }),
})
export type DashboardAggregates = z.infer<typeof DashboardAggregatesSchema>

export const DashboardDataSchema = z.object({
  aggregates: DashboardAggregatesSchema.optional(),
  leave_balance: z.array(LeaveBalanceSchema).optional(),
  pending_tasks: z.array(NotificationSchema).optional(),
  team: z.object({ pending_leave_requests: z.number() }).optional(),
})
export type DashboardData = z.infer<typeof DashboardDataSchema>

export const AuditLogCategorySchema = z.enum([
  'login_attempt',
  'record_change',
  'payroll_action',
  'approval',
  'permission_change',
  'second_factor_event',
])
export type AuditLogCategory = z.infer<typeof AuditLogCategorySchema>

export const AuditLogEntrySchema = z.object({
  id: z.number(),
  actor: z.number().nullable(),
  category: AuditLogCategorySchema,
  target_type: z.string().nullable(),
  target_id: z.number().nullable(),
  action: z.string(),
  detail: z.record(z.string(), z.unknown()).nullable(),
  occurred_at: z.string(),
})
export type AuditLogEntry = z.infer<typeof AuditLogEntrySchema>

export function paginatedResponseSchema<T extends z.ZodTypeAny>(item: T) {
  return z.object({
    count: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
    results: z.array(item),
  })
}
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export const HeadcountReportSchema = z.object({
  aggregate: z.object({ total: z.number() }),
  breakdown: z.array(z.object({ department_id: z.number(), department__name: z.string(), count: z.number() })).optional(),
})
export type HeadcountReport = z.infer<typeof HeadcountReportSchema>

export const LeaveUtilizationReportSchema = z.object({
  aggregate: z.object({ entitled_days: z.number(), used_days: z.number() }),
  breakdown: z.array(
    z.object({
      leave_type_id: z.number(),
      leave_type__name: z.string(),
      entitled_days: z.number(),
      used_days: z.number(),
    }),
  ).optional(),
})
export type LeaveUtilizationReport = z.infer<typeof LeaveUtilizationReportSchema>

export const TurnoverReportSchema = z.object({
  aggregate: z.object({ hires: z.number(), terminations: z.number() }),
  breakdown: z.object({
    hires_by_department: z.array(z.object({ department_id: z.number(), department__name: z.string(), count: z.number() })),
    terminations_by_department: z.array(
      z.object({
        employee__department_id: z.number(),
        employee__department__name: z.string(),
        count: z.number(),
      }),
    ),
  }).optional(),
})
export type TurnoverReport = z.infer<typeof TurnoverReportSchema>

export const PayrollCostReportSchema = z.object({
  aggregate: z.object({ gross_pay: z.number(), net_pay: z.number() }),
  breakdown: z.array(
    z.object({
      employee__department_id: z.number(),
      employee__department__name: z.string(),
      gross_pay: z.number(),
      net_pay: z.number(),
    }),
  ).optional(),
})
export type PayrollCostReport = z.infer<typeof PayrollCostReportSchema>

export const PayrollSummaryReportSchema = z.object({
  aggregate: z.object({ gross_pay: z.number(), net_pay: z.number(), payslip_count: z.number() }),
  breakdown: z.array(
    z.object({
      id: z.number(),
      period_start: z.string(),
      period_end: z.string(),
      gross_pay: z.number(),
      net_pay: z.number(),
    }),
  ).optional(),
})
export type PayrollSummaryReport = z.infer<typeof PayrollSummaryReportSchema>

export const ReportTypeSchema = z.enum(['headcount', 'leave_utilization', 'turnover', 'payroll_cost', 'payroll_summary'])
export type ReportType = z.infer<typeof ReportTypeSchema>
export const ReportExportStatusSchema = z.enum(['pending', 'complete', 'failed'])
export type ReportExportStatus = z.infer<typeof ReportExportStatusSchema>

export const ReportExportRecordSchema = z.object({
  id: z.number(),
  report_type: ReportTypeSchema,
  params: z.record(z.string(), z.unknown()),
  status: ReportExportStatusSchema,
  download_url: z.string().nullable(),
  failed_reason: z.string().nullable(),
  generated_at: z.string().nullable(),
  created_at: z.string(),
})
export type ReportExportRecord = z.infer<typeof ReportExportRecordSchema>

export const SalaryStructureSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  effective_from: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type SalaryStructure = z.infer<typeof SalaryStructureSchema>

export const PayGradeSchema = z.object({
  id: z.number(),
  salary_structure: z.number(),
  name: z.string(),
  min_salary: z.string(),
  max_salary: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type PayGrade = z.infer<typeof PayGradeSchema>

export const CompensationRecordSchema = z.object({
  id: z.number(),
  employee: z.number(),
  pay_grade: z.number().nullable(),
  base_salary: z.string(),
  currency: z.string(),
  effective_from: z.string(),
  effective_to: z.string().nullable(),
  is_superseded: z.boolean(),
  recorded_by: z.number().nullable(),
  created_at: z.string(),
})
export type CompensationRecord = z.infer<typeof CompensationRecordSchema>

export const PayrollRunStatusSchema = z.enum(['draft', 'calculated', 'pending_approval', 'approved', 'finalized', 'failed'])
export type PayrollRunStatus = z.infer<typeof PayrollRunStatusSchema>

export const PayrollRunSchema = z.object({
  id: z.number(),
  period_start: z.string(),
  period_end: z.string(),
  status: PayrollRunStatusSchema,
  initiated_by: z.number().nullable(),
  approved_by: z.number().nullable(),
  approved_at: z.string().nullable(),
  finalized_at: z.string().nullable(),
  created_at: z.string(),
})
export type PayrollRun = z.infer<typeof PayrollRunSchema>

export const PayslipSchema = z.object({
  id: z.number(),
  payroll_run: z.number(),
  employee: z.number(),
  gross_pay: z.string(),
  net_pay: z.string(),
  currency: z.string(),
  generated_at: z.string(),
  object_key: z.string().nullable(),
})
export type Payslip = z.infer<typeof PayslipSchema>
