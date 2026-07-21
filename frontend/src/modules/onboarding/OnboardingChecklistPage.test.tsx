import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as employeesApi from '../../api/employees'
import * as onboardingApi from '../../api/onboarding'
import { AuthContext } from '../../auth/AuthContext'
import { OnboardingChecklistPage } from './OnboardingChecklistPage'

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
        <MemoryRouter initialEntries={['/onboarding/5']}>
          <Routes>
            <Route path="/onboarding/:id" element={<OnboardingChecklistPage />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('OnboardingChecklistPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows tasks and lets an HR Officer advance a pending task, hiding actions for other roles', async () => {
    vi.spyOn(onboardingApi, 'getOnboardingChecklist').mockResolvedValue({
      id: 5, employee: 42, application: null, started_at: '2026-07-21T00:00:00Z', completed_at: null,
    })
    vi.spyOn(employeesApi, 'getEmployee').mockResolvedValue({
      id: 42, employee_number: 'E-42', first_name: 'Ada', last_name: 'Lovelace', date_of_birth: '1990-01-01',
      department: 1, job_title: 1, employment_status: 'active', hire_date: '2026-07-21', created_at: '', updated_at: '',
    })
    vi.spyOn(onboardingApi, 'listOnboardingTasks').mockResolvedValue([
      { id: 1, checklist: 5, name: 'Sign contract', is_required: true, status: 'pending', completed_by: null, completed_at: null, created_at: '' },
    ])
    const updateSpy = vi.spyOn(onboardingApi, 'updateOnboardingTaskStatus').mockResolvedValue({
      id: 1, checklist: 5, name: 'Sign contract', is_required: true, status: 'in_progress', completed_by: null, completed_at: null, created_at: '',
    })

    renderPage(['HR Officer'])
    const user = userEvent.setup()

    expect(await screen.findByText('Onboarding — Ada Lovelace')).toBeInTheDocument()
    expect(await screen.findByText('Sign contract')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Start' }))
    expect(updateSpy).toHaveBeenCalledWith(5, 1, 'in_progress')
  })

  it('hides task actions and Add Task for a read-only role', async () => {
    vi.spyOn(onboardingApi, 'getOnboardingChecklist').mockResolvedValue({
      id: 5, employee: 42, application: null, started_at: '2026-07-21T00:00:00Z', completed_at: null,
    })
    vi.spyOn(employeesApi, 'getEmployee').mockResolvedValue({
      id: 42, employee_number: 'E-42', first_name: 'Ada', last_name: 'Lovelace', date_of_birth: '1990-01-01',
      department: 1, job_title: 1, employment_status: 'active', hire_date: '2026-07-21', created_at: '', updated_at: '',
    })
    vi.spyOn(onboardingApi, 'listOnboardingTasks').mockResolvedValue([
      { id: 1, checklist: 5, name: 'Sign contract', is_required: true, status: 'pending', completed_by: null, completed_at: null, created_at: '' },
    ])

    renderPage(['Recruiter'])

    expect(await screen.findByText('Sign contract')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Start' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Add Task' })).not.toBeInTheDocument()
  })
})
