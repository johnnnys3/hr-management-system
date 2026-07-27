import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as compensationApi from '../../api/compensation'
import * as employeesApi from '../../api/employees'
import * as recruitmentApi from '../../api/recruitment'
import { AuthContext } from '../../auth/AuthContext'
import { CandidateDetailPage } from './CandidateDetailPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 1, email: 'hradmin@b.com', groups: ['HR Administrator'], is_employee: true, is_manager: false, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <MemoryRouter initialEntries={['/recruitment/candidates/1']}>
          <Routes>
            <Route path="/recruitment/candidates/:id" element={<CandidateDetailPage />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('CandidateDetailPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the candidate and their applications, with offer/interview panels on expand', { timeout: 15000 }, async () => {
    vi.spyOn(recruitmentApi, 'getCandidate').mockResolvedValue({
      id: 1, first_name: 'Grace', last_name: 'Hopper', email: 'grace@b.com', phone: null, resume_object_key: null, created_at: '',
    })
    vi.spyOn(recruitmentApi, 'listCandidateApplications').mockResolvedValue([
      { id: 10, candidate: 1, posting: 20, stage: 'interview', applied_at: '', updated_at: '' },
    ])
    vi.spyOn(recruitmentApi, 'listJobPostings').mockResolvedValue([
      { id: 20, requisition: 1, title: 'Backend Engineer', description: '', channel: 'external', published_at: null, closed_at: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(recruitmentApi, 'listInterviews').mockResolvedValue([])
    vi.spyOn(recruitmentApi, 'listOffers').mockResolvedValue([])
    vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([])
    renderPage()
    const user = userEvent.setup()

    expect(await screen.findByText('Grace Hopper')).toBeInTheDocument()
    expect(await screen.findByText('Backend Engineer')).toBeInTheDocument()

    await user.click(screen.getByLabelText(/expand row/i));

    expect(await screen.findByText('Interviews')).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /issue offer/i })).toBeInTheDocument()
  })

  it('issues an offer with the selected pay grade id, or null when none is chosen', { timeout: 15000 }, async () => {
    vi.spyOn(recruitmentApi, 'getCandidate').mockResolvedValue({
      id: 1, first_name: 'Grace', last_name: 'Hopper', email: 'grace@b.com', phone: null, resume_object_key: null, created_at: '',
    })
    vi.spyOn(recruitmentApi, 'listCandidateApplications').mockResolvedValue([
      { id: 10, candidate: 1, posting: 20, stage: 'interview', applied_at: '', updated_at: '' },
    ])
    vi.spyOn(recruitmentApi, 'listJobPostings').mockResolvedValue([
      { id: 20, requisition: 1, title: 'Backend Engineer', description: '', channel: 'external', published_at: null, closed_at: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(recruitmentApi, 'listInterviews').mockResolvedValue([])
    vi.spyOn(recruitmentApi, 'listOffers').mockResolvedValue([])
    vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([])
    vi.spyOn(compensationApi, 'listPayGrades').mockResolvedValue([
      { id: 5, salary_structure: 100, name: 'Level 3', min_salary: '1000.00', max_salary: '2000.00', created_at: '', updated_at: '' },
      { id: 6, salary_structure: 200, name: 'Level 3', min_salary: '1500.00', max_salary: '2500.00', created_at: '', updated_at: '' },
    ])
    vi.spyOn(compensationApi, 'listSalaryStructures').mockResolvedValue([
      { id: 100, name: 'Engineering Ladder', description: null, effective_from: '', created_at: '', updated_at: '' },
      { id: 200, name: 'Sales Ladder', description: null, effective_from: '', created_at: '', updated_at: '' },
    ])
    const createOffer = vi.spyOn(recruitmentApi, 'createOffer').mockResolvedValue({
      id: 100, application: 10, offered_salary: '90000', offered_pay_grade: 5, status: 'pending',
      issued_at: '', decided_at: null, document_object_key: null,
    })
    renderPage()
    const user = userEvent.setup()

    expect(await screen.findByText('Grace Hopper')).toBeInTheDocument()
    await user.click(screen.getByLabelText(/expand row/i))
    await user.click(await screen.findByRole('button', { name: /issue offer/i }))

    await user.type(screen.getByPlaceholderText('Offered salary'), '90000')
    await user.click(screen.getByRole('combobox'))
    await user.click(await screen.findByText('Level 3 (Engineering Ladder)'))
    await user.click(screen.getByRole('button', { name: /^issue$/i }))

    expect(createOffer).toHaveBeenCalledWith(10, '90000', 5)

    createOffer.mockClear()
    await user.click(await screen.findByRole('button', { name: /issue offer/i }))
    await user.type(screen.getByPlaceholderText('Offered salary'), '80000')
    await user.click(screen.getByRole('button', { name: /^issue$/i }))

    expect(createOffer).toHaveBeenCalledWith(10, '80000', null)
  })
})
