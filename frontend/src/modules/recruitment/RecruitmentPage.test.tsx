import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import * as recruitmentApi from '../../api/recruitment'
import { AuthContext } from '../../auth/AuthContext'
import { RecruitmentPage } from './RecruitmentPage'

function renderPage(groups: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 1, email: 'hr@b.com', groups, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <MemoryRouter>
          <RecruitmentPage />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('RecruitmentPage', () => {
  afterEach(() => vi.restoreAllMocks())

  // ponytail: slow under jsdom (antd Table + two useQuery + a mutation), not stuck — give it headroom.
  it('shows only the Requisitions tab for HR Administrator, with Approve/Reject', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([
      { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([
      { id: 1, name: 'Software Engineer', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(recruitmentApi, 'listJobRequisitions').mockResolvedValue([
      { id: 1, department: 1, job_title: 1, requested_by: 5, status: 'pending_approval', approved_by: null, created_at: '', updated_at: '' },
    ])
    const approveSpy = vi.spyOn(recruitmentApi, 'approveJobRequisition').mockResolvedValue({
      id: 1, department: 1, job_title: 1, requested_by: 5, status: 'approved', approved_by: 1, created_at: '', updated_at: '',
    })
    renderPage(['HR Administrator'])
    const user = userEvent.setup()

    expect(await screen.findByText('Engineering')).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: /postings/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: /candidates/i })).not.toBeInTheDocument()

    await user.click(await screen.findByRole('button', { name: /^approve$/i }))
    await waitFor(() => expect(approveSpy).toHaveBeenCalledWith(1))
  }, 15000)

  it('shows all tabs and a New Requisition button for Recruiter', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    vi.spyOn(recruitmentApi, 'listJobRequisitions').mockResolvedValue([])
    vi.spyOn(recruitmentApi, 'listJobPostings').mockResolvedValue([])
    vi.spyOn(recruitmentApi, 'listCandidates').mockResolvedValue([])
    renderPage(['Recruiter'])

    expect(await screen.findByRole('tab', { name: /postings/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /candidates/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /new requisition/i })).toBeInTheDocument()
  })
})
