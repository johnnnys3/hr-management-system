import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import * as employeesApi from '../../api/employees'
import * as reportingApi from '../../api/reporting'
import { AuthContext } from '../../auth/AuthContext'
import type { Employee } from '../../api/types'
import { EmployeeDetailPage } from './EmployeeDetailPage'

const employee: Employee = {
  id: 1,
  employee_number: 'EMP001',
  first_name: 'Ada',
  last_name: 'Lovelace',
  date_of_birth: '1990-01-01',
  department: 1,
  job_title: 1,
  employment_status: 'active',
  hire_date: '2020-01-01',
  created_at: '',
  updated_at: '',
}

function renderPage(groups: string[] = []) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 99, email: 'hr@b.com', groups, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <MemoryRouter initialEntries={['/employees/1']}>
          <Routes>
            <Route path="/employees/:id" element={<EmployeeDetailPage />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('EmployeeDetailPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the profile tab with employee data', async () => {
    vi.spyOn(employeesApi, 'getEmployee').mockResolvedValue(employee)
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([
      { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([
      { id: 1, name: 'Software Engineer', is_active: true, created_at: '', updated_at: '' },
    ])
    renderPage()

    expect(await screen.findByText('Ada Lovelace')).toBeInTheDocument()
    expect(await screen.findByDisplayValue('EMP001')).toBeInTheDocument()
  })

  it('shows employment history on the History tab', async () => {
    vi.spyOn(employeesApi, 'getEmployee').mockResolvedValue(employee)
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    vi.spyOn(employeesApi, 'listEmploymentHistory').mockResolvedValue([
      {
        id: 1,
        employee: 1,
        event_type: 'hired',
        effective_date: '2020-01-01',
        previous_value: null,
        new_value: { employment_status: 'active' },
        recorded_by: null,
        created_at: '',
      },
    ])
    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('tab', { name: /employment history/i }))

    expect(await screen.findByText('hired')).toBeInTheDocument()
  })

  it('shows manager and direct reports on the Reporting tab, with Change Manager for HR Officer', async () => {
    vi.spyOn(employeesApi, 'getEmployee').mockImplementation((id) =>
      Promise.resolve(id === 2 ? { ...employee, id: 2, first_name: 'Grace', last_name: 'Hopper' } : employee),
    )
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    vi.spyOn(reportingApi, 'listReportingRelationships').mockResolvedValue([
      { id: 1, employee: 1, manager_employee: 2, effective_from: '2020-01-01' },
    ])
    vi.spyOn(reportingApi, 'listDirectReports').mockResolvedValue([])
    renderPage(['HR Officer'])
    const user = userEvent.setup()

    await user.click(await screen.findByRole('tab', { name: /reporting/i }))

    expect(await screen.findByText('Grace Hopper (EMP001)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /change manager/i })).toBeInTheDocument()
  })
})
