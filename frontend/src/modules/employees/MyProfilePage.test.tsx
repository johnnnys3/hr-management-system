import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as employeesApi from '../../api/employees'
import * as selfServiceApi from '../../api/selfService'
import { AuthContext } from '../../auth/AuthContext'
import { MyProfilePage } from './MyProfilePage'

function renderPage(groups: string[] = []) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 1, email: 'ada@b.com', groups, is_employee: true, is_manager: false, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <MyProfilePage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

const EMPLOYEE = {
  id: 42,
  employee_number: 'E-42',
  first_name: 'Ada',
  last_name: 'Lovelace',
  date_of_birth: '1990-01-01',
  department: 1,
  job_title: 1,
  employment_status: 'active' as const,
  hire_date: '2020-01-01',
  created_at: '',
  updated_at: '',
}

describe('MyProfilePage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the profile with name and date of birth read-only', async () => {
    vi.spyOn(selfServiceApi, 'getMyProfile').mockResolvedValue(EMPLOYEE)

    renderPage()

    expect(await screen.findByDisplayValue('E-42')).toBeInTheDocument()
    expect(screen.getByDisplayValue('active')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Ada')).toBeDisabled()
    expect(screen.getByDisplayValue('Lovelace')).toBeDisabled()
    expect(screen.getByText(/contact hr/i)).toBeInTheDocument()
    expect(screen.queryByText('Save')).not.toBeInTheDocument()
  })

  it('lists employment history and documents for the caller\'s own employee id', async () => {
    vi.spyOn(selfServiceApi, 'getMyProfile').mockResolvedValue(EMPLOYEE)
    vi.spyOn(employeesApi, 'listEmploymentHistory').mockResolvedValue([
      {
        id: 1, employee: 42, event_type: 'hired', effective_date: '2020-01-01',
        previous_value: null, new_value: { employment_status: 'active' }, recorded_by: null, created_at: '',
      },
    ])
    vi.spyOn(employeesApi, 'listEmployeeDocuments').mockResolvedValue([
      {
        id: 5, employee: 42, document_type: 'contract', file_name: 'contract.pdf',
        content_type: 'application/pdf', size_bytes: 1024, uploaded_by: null, created_at: '',
      },
    ])

    renderPage()
    const user = userEvent.setup()

    await screen.findByText('My Profile')
    await user.click(screen.getByText('Employment History'))
    expect(await screen.findByText('hired')).toBeInTheDocument()
    expect(employeesApi.listEmploymentHistory).toHaveBeenCalledWith(42)

    await user.click(screen.getByText('Documents'))
    expect(await screen.findByText('contract.pdf')).toBeInTheDocument()
    expect(employeesApi.listEmployeeDocuments).toHaveBeenCalledWith(42)
  })
})
