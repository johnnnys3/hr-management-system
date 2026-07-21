import { apiFetch } from './client'
import type { Candidate, CandidateApplication, Interview, JobPosting, JobRequisition, OfferLetter, PayGradeOption } from './types'

export function listPayGradeOptions(): Promise<PayGradeOption[]> {
  return apiFetch('/api/pay-grades/')
}

export function listJobRequisitions(status?: string): Promise<JobRequisition[]> {
  const suffix = status ? `?status=${status}` : ''
  return apiFetch(`/api/job-requisitions/${suffix}`)
}

export function createJobRequisition(data: { department: number; job_title: number }): Promise<JobRequisition> {
  return apiFetch('/api/job-requisitions/', { method: 'POST', body: data })
}

export function approveJobRequisition(id: number): Promise<JobRequisition> {
  return apiFetch(`/api/job-requisitions/${id}/approve/`, { method: 'POST' })
}

export function rejectJobRequisition(id: number): Promise<JobRequisition> {
  return apiFetch(`/api/job-requisitions/${id}/reject/`, { method: 'POST' })
}

export function listJobPostings(requisitionId?: number): Promise<JobPosting[]> {
  const suffix = requisitionId ? `?requisition_id=${requisitionId}` : ''
  return apiFetch(`/api/job-postings/${suffix}`)
}

export function createJobPosting(data: {
  requisition: number
  title: string
  description: string
  channel: 'internal' | 'external'
}): Promise<JobPosting> {
  return apiFetch('/api/job-postings/', { method: 'POST', body: data })
}

export function publishJobPosting(id: number): Promise<JobPosting> {
  return apiFetch(`/api/job-postings/${id}/publish/`, { method: 'POST' })
}

export function listCandidates(search?: string): Promise<Candidate[]> {
  const suffix = search ? `?search=${encodeURIComponent(search)}` : ''
  return apiFetch(`/api/candidates/${suffix}`)
}

export function getCandidate(id: number): Promise<Candidate> {
  return apiFetch(`/api/candidates/${id}/`)
}

export function createCandidate(data: {
  first_name: string
  last_name: string
  email: string
  phone?: string
  resume?: File
}): Promise<Candidate> {
  const body = new FormData()
  body.set('first_name', data.first_name)
  body.set('last_name', data.last_name)
  body.set('email', data.email)
  if (data.phone) body.set('phone', data.phone)
  if (data.resume) body.set('resume', data.resume)
  return apiFetch('/api/candidates/', { method: 'POST', body })
}

export function listCandidateApplications(candidateId: number): Promise<CandidateApplication[]> {
  return apiFetch(`/api/candidates/${candidateId}/applications/`)
}

export function createCandidateApplication(candidateId: number, postingId: number): Promise<CandidateApplication> {
  return apiFetch(`/api/candidates/${candidateId}/applications/`, { method: 'POST', body: { posting: postingId } })
}

export function listInterviews(applicationId: number): Promise<Interview[]> {
  return apiFetch(`/api/applications/${applicationId}/interviews/`)
}

export function createInterview(
  applicationId: number,
  data: { interviewer_employee?: number; scheduled_at: string },
): Promise<Interview> {
  return apiFetch(`/api/applications/${applicationId}/interviews/`, { method: 'POST', body: data })
}

export function updateInterview(
  applicationId: number,
  interviewId: number,
  data: Partial<{ status: string; feedback: string; scheduled_at: string }>,
): Promise<Interview> {
  return apiFetch(`/api/applications/${applicationId}/interviews/${interviewId}/`, { method: 'PATCH', body: data })
}

export function listOffers(applicationId: number): Promise<OfferLetter[]> {
  return apiFetch(`/api/applications/${applicationId}/offer/`)
}

export function createOffer(
  applicationId: number,
  offeredSalary: string,
  offeredPayGrade: number | null,
): Promise<OfferLetter> {
  return apiFetch(`/api/applications/${applicationId}/offer/`, {
    method: 'POST',
    body: { offered_salary: offeredSalary, offered_pay_grade: offeredPayGrade },
  })
}

export function decideOffer(
  offerId: number,
  decision: 'accepted' | 'rejected' | 'withdrawn',
): Promise<OfferLetter> {
  return apiFetch(`/api/offers/${offerId}/decide/`, { method: 'POST', body: { decision } })
}
