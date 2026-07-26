import { describe, expect, it } from 'vitest'
import {
  AuditLogEntrySchema,
  CandidateApplicationSchema,
  CandidateSchema,
  DashboardAggregatesSchema,
  DashboardDataSchema,
  DepartmentSchema,
  EmergencyContactSchema,
  EmployeeDocumentSchema,
  EmployeeSchema,
  EmploymentHistoryEntrySchema,
  HeadcountReportSchema,
  InterviewSchema,
  JobPostingSchema,
  JobRequisitionSchema,
  JobTitleSchema,
  LeaveBalanceSchema,
  LeaveRequestSchema,
  LeaveTypeSchema,
  LeaveUtilizationReportSchema,
  LoginSecondFactorRequiredSchema,
  LoginSuccessSchema,
  MeSchema,
  NotificationSchema,
  OfferLetterSchema,
  OnboardingChecklistSchema,
  OnboardingTaskSchema,
  PayGradeOptionSchema,
  PayrollCostReportSchema,
  PayrollSummaryReportSchema,
  ReportExportRecordSchema,
  RoleGrantRequestRecordSchema,
  SecondFactorEnrollResponseSchema,
  SecondFactorRecoveryRequestRecordSchema,
  TurnoverReportSchema,
  UserAccountSchema,
} from './types'

// docs/08-testing-plan.md §3.3: one valid fixture (matching
// docs/06-api-contracts.md's documented shape) and one broken fixture
// (a required field deleted or given the wrong type) per schema. Table-
// driven rather than 35 near-identical describe blocks — each row is the
// full obligation the control asks for, nothing more.
const CASES: { name: string; schema: { parse: (v: unknown) => unknown }; valid: unknown; breakField: string }[] = [
  {
    name: 'Me', schema: MeSchema, breakField: 'is_manager',
    valid: { id: 1, email: 'a@b.com', groups: ['HR Officer'], is_employee: true, is_manager: false, second_factor_enrollment_pending: false },
  },
  {
    name: 'LoginSuccess', schema: LoginSuccessSchema, breakField: 'email',
    valid: { id: 1, email: 'a@b.com', groups: [] },
  },
  {
    name: 'LoginSecondFactorRequired', schema: LoginSecondFactorRequiredSchema, breakField: 'second_factor_required',
    valid: { second_factor_required: true },
  },
  {
    name: 'UserAccount', schema: UserAccountSchema, breakField: 'is_active',
    valid: { id: 1, email: 'a@b.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
  },
  {
    name: 'SecondFactorEnrollResponse', schema: SecondFactorEnrollResponseSchema, breakField: 'provisioning_uri',
    valid: { provisioning_uri: 'otpauth://...' },
  },
  {
    name: 'SecondFactorRecoveryRequestRecord', schema: SecondFactorRecoveryRequestRecordSchema, breakField: 'status',
    valid: { id: 1, status: 'pending', requested_at: '', decided_at: null },
  },
  {
    name: 'Department', schema: DepartmentSchema, breakField: 'name',
    valid: { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
  },
  {
    name: 'JobTitle', schema: JobTitleSchema, breakField: 'name',
    valid: { id: 1, name: 'Engineer', is_active: true, created_at: '', updated_at: '' },
  },
  {
    name: 'Employee', schema: EmployeeSchema, breakField: 'employment_status',
    valid: {
      id: 1, employee_number: 'E-1', first_name: 'Ada', last_name: 'Lovelace', date_of_birth: '1990-01-01',
      department: 1, job_title: 1, employment_status: 'active', hire_date: '2020-01-01', created_at: '', updated_at: '',
    },
  },
  {
    name: 'EmploymentHistoryEntry', schema: EmploymentHistoryEntrySchema, breakField: 'event_type',
    valid: {
      id: 1, employee: 1, event_type: 'hired', effective_date: '2020-01-01',
      previous_value: null, new_value: {}, recorded_by: null, created_at: '',
    },
  },
  {
    name: 'EmployeeDocument', schema: EmployeeDocumentSchema, breakField: 'size_bytes',
    valid: {
      id: 1, employee: 1, document_type: 'contract', file_name: 'x.pdf', content_type: 'application/pdf',
      size_bytes: 100, uploaded_by: null, created_at: '',
    },
  },
  {
    name: 'EmergencyContact', schema: EmergencyContactSchema, breakField: 'is_primary',
    valid: { id: 1, employee: 1, name: 'Grace', relationship: 'spouse', phone: '555', email: null, is_primary: true, created_at: '', updated_at: '' },
  },
  {
    name: 'JobRequisition', schema: JobRequisitionSchema, breakField: 'status',
    valid: { id: 1, department: 1, job_title: 1, requested_by: 1, status: 'draft', approved_by: null, created_at: '', updated_at: '' },
  },
  {
    name: 'JobPosting', schema: JobPostingSchema, breakField: 'channel',
    valid: { id: 1, requisition: 1, title: 'Engineer', description: '', channel: 'external', published_at: null, closed_at: null, created_at: '', updated_at: '' },
  },
  {
    name: 'Candidate', schema: CandidateSchema, breakField: 'email',
    valid: { id: 1, first_name: 'Grace', last_name: 'Hopper', email: 'g@h.com', phone: null, resume_object_key: null, created_at: '' },
  },
  {
    name: 'CandidateApplication', schema: CandidateApplicationSchema, breakField: 'stage',
    valid: { id: 1, candidate: 1, posting: 1, stage: 'applied', applied_at: '', updated_at: '' },
  },
  {
    name: 'Interview', schema: InterviewSchema, breakField: 'status',
    valid: { id: 1, application: 1, interviewer_employee: null, scheduled_at: '', status: 'scheduled', feedback: null, created_at: '', updated_at: '' },
  },
  {
    name: 'OfferLetter', schema: OfferLetterSchema, breakField: 'status',
    valid: { id: 1, application: 1, offered_salary: '50000', offered_pay_grade: null, status: 'pending', issued_at: '', decided_at: null, document_object_key: null },
  },
  {
    name: 'PayGradeOption', schema: PayGradeOptionSchema, breakField: 'name',
    valid: { id: 1, name: 'Grade 1', salary_structure_name: 'Default' },
  },
  {
    name: 'Notification', schema: NotificationSchema, breakField: 'channel',
    valid: { id: 1, category: 'pending_task', channel: 'in_app', subject: 's', body: 'b', related_type: null, related_id: null, read_at: null, created_at: '' },
  },
  {
    name: 'OnboardingChecklist', schema: OnboardingChecklistSchema, breakField: 'started_at',
    valid: { id: 1, employee: 1, application: null, started_at: '', completed_at: null },
  },
  {
    name: 'OnboardingTask', schema: OnboardingTaskSchema, breakField: 'status',
    valid: { id: 1, checklist: 1, name: 'Sign form', is_required: true, status: 'pending', completed_by: null, completed_at: null, created_at: '' },
  },
  {
    name: 'RoleGrantRequestRecord', schema: RoleGrantRequestRecordSchema, breakField: 'status',
    valid: {
      id: 1, requester: 1, subject: 2, role: 1, status: 'pending', approver: null, requested_at: '', decided_at: null,
      requester_email: 'a@b.com', subject_email: 'c@d.com', subject_name: null, role_name: 'HR Officer',
    },
  },
  {
    name: 'LeaveType', schema: LeaveTypeSchema, breakField: 'requires_approval',
    valid: { id: 1, name: 'Annual leave', requires_approval: true, is_active: true, created_at: '', updated_at: '' },
  },
  {
    name: 'LeaveBalance', schema: LeaveBalanceSchema, breakField: 'entitled_days',
    valid: { id: 1, employee: 1, leave_type: 1, period_start: '', period_end: '', entitled_days: '20', used_days: '5', created_at: '', updated_at: '' },
  },
  {
    name: 'LeaveRequest', schema: LeaveRequestSchema, breakField: 'status',
    valid: { id: 1, employee: 1, leave_type: 1, start_date: '', end_date: '', reason: null, status: 'pending', approved_by: null, decided_at: null, created_at: '' },
  },
  {
    name: 'DashboardAggregates', schema: DashboardAggregatesSchema, breakField: 'headcount',
    valid: {
      headcount: { total: 1 }, leave_utilization: { entitled_days: 1, used_days: 1 }, turnover: { hires: 1, terminations: 0 },
      payroll_cost: { gross_pay: 1, net_pay: 1 }, payroll_summary: { gross_pay: 1, net_pay: 1, payslip_count: 1 },
    },
  },
  { name: 'DashboardData', schema: DashboardDataSchema, breakField: '__none__', valid: {} },
  {
    name: 'AuditLogEntry', schema: AuditLogEntrySchema, breakField: 'category',
    valid: { id: 1, actor: null, category: 'login_attempt', target_type: null, target_id: null, action: 'login_success', detail: null, occurred_at: '' },
  },
  {
    name: 'HeadcountReport', schema: HeadcountReportSchema, breakField: 'aggregate',
    valid: { aggregate: { total: 1 } },
  },
  {
    name: 'LeaveUtilizationReport', schema: LeaveUtilizationReportSchema, breakField: 'aggregate',
    valid: { aggregate: { entitled_days: 1, used_days: 1 } },
  },
  {
    name: 'TurnoverReport', schema: TurnoverReportSchema, breakField: 'aggregate',
    valid: { aggregate: { hires: 1, terminations: 0 } },
  },
  {
    name: 'PayrollCostReport', schema: PayrollCostReportSchema, breakField: 'aggregate',
    valid: { aggregate: { gross_pay: 1, net_pay: 1 } },
  },
  {
    name: 'PayrollSummaryReport', schema: PayrollSummaryReportSchema, breakField: 'aggregate',
    valid: { aggregate: { gross_pay: 1, net_pay: 1, payslip_count: 1 } },
  },
  {
    name: 'ReportExportRecord', schema: ReportExportRecordSchema, breakField: 'status',
    valid: { id: 1, report_type: 'headcount', params: {}, status: 'pending', download_url: null, failed_reason: null, generated_at: null, created_at: '' },
  },
]

describe('API resource schemas (docs/08-testing-plan.md §3.3)', () => {
  for (const { name, schema, valid, breakField } of CASES) {
    describe(name, () => {
      it('parses a fixture matching the documented shape', () => {
        expect(() => schema.parse(valid)).not.toThrow()
      })

      if (breakField !== '__none__') {
        it('rejects a fixture missing a required field', () => {
          const broken = { ...(valid as Record<string, unknown>) }
          delete broken[breakField]
          expect(() => schema.parse(broken)).toThrow()
        })
      }
    })
  }
})
