import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as employeesApi from '../../api/employees'
import * as recruitmentApi from '../../api/recruitment'
import { CandidateDetailPage } from './CandidateDetailPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/recruitment/candidates/1']}>
        <Routes>
          <Route path="/recruitment/candidates/:id" element={<CandidateDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('CandidateDetailPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the candidate and their applications, with offer/interview panels on expand', async () => {
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
})
