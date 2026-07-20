import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import * as employeesApi from '../../api/employees'
import { EmployeesPage } from './EmployeesPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <EmployeesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('EmployeesPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists employees from GET /api/employees/', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([
      { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([
      { id: 1, name: 'Software Engineer', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([
      {
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
      },
    ])
    renderPage()

    expect(await screen.findByText('Ada')).toBeInTheDocument()
    expect(await screen.findByText('Engineering')).toBeInTheDocument()
  })

  it('re-fetches with a search term when searching', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    const listSpy = vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([])
    renderPage()
    const user = userEvent.setup()

    const searchInput = await screen.findByPlaceholderText(/search name or employee number/i)
    await user.type(searchInput, 'Ada{enter}')

    await waitFor(() => expect(listSpy).toHaveBeenCalledWith(expect.objectContaining({ search: 'Ada' })))
  })
})
