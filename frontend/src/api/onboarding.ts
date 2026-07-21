import { apiFetch } from './client'
import type { OnboardingChecklist, OnboardingTask, OnboardingTaskStatus } from './types'

export function convertFromApplication(data: {
  application_id: number
  employee_number: string
  date_of_birth: string
  department: number
  job_title: number
  hire_date: string
}): Promise<OnboardingChecklist> {
  return apiFetch('/api/onboarding/convert/', { method: 'POST', body: data })
}

export function convertDirectHire(data: {
  employee_number: string
  first_name: string
  last_name: string
  date_of_birth: string
  department: number
  job_title: number
  hire_date: string
}): Promise<OnboardingChecklist> {
  return apiFetch('/api/onboarding/convert/', { method: 'POST', body: data })
}

export function getOnboardingChecklist(id: number): Promise<OnboardingChecklist> {
  return apiFetch(`/api/onboarding-checklists/${id}/`)
}

export function listOnboardingTasks(checklistId: number): Promise<OnboardingTask[]> {
  return apiFetch(`/api/onboarding-checklists/${checklistId}/tasks/`)
}

export function createOnboardingTask(
  checklistId: number,
  data: { name: string; is_required: boolean },
): Promise<OnboardingTask> {
  return apiFetch(`/api/onboarding-checklists/${checklistId}/tasks/`, { method: 'POST', body: data })
}

export function updateOnboardingTaskStatus(
  checklistId: number,
  taskId: number,
  status: OnboardingTaskStatus,
): Promise<OnboardingTask> {
  return apiFetch(`/api/onboarding-checklists/${checklistId}/tasks/${taskId}/`, { method: 'PATCH', body: { status } })
}
