import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import * as employeesApi from '../../api/employees'
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

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/employees/1']}>
        <Routes>
          <Route path="/employees/:id" element={<EmployeeDetailPage />} />
        </Routes>
      </MemoryRouter>
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
})
