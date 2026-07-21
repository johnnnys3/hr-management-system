import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as reportingApi from '../../api/reporting'
import * as selfServiceApi from '../../api/selfService'
import { MyTeamPage } from './MyTeamPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MyTeamPage />
    </QueryClientProvider>,
  )
}

describe('MyTeamPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it("lists the caller's direct reports, looked up against their own employee id", async () => {
    vi.spyOn(selfServiceApi, 'getMyProfile').mockResolvedValue({
      id: 7, employee_number: 'E-7', first_name: 'Grace', last_name: 'Hopper', date_of_birth: '1980-01-01',
      department: 1, job_title: 1, employment_status: 'active', hire_date: '2020-01-01', created_at: '', updated_at: '',
    })
    const listSpy = vi.spyOn(reportingApi, 'listDirectReports').mockResolvedValue([
      {
        id: 42, employee_number: 'E-42', first_name: 'Ada', last_name: 'Lovelace', date_of_birth: '1990-01-01',
        department: 1, job_title: 1, employment_status: 'active', hire_date: '2021-01-01', created_at: '', updated_at: '',
      },
    ])

    renderPage()

    expect(await screen.findByText('Ada')).toBeInTheDocument()
    expect(listSpy).toHaveBeenCalledWith(7)
  })

  it('shows an empty state for a caller with no direct reports', async () => {
    vi.spyOn(selfServiceApi, 'getMyProfile').mockResolvedValue({
      id: 8, employee_number: 'E-8', first_name: 'Alan', last_name: 'Turing', date_of_birth: '1980-01-01',
      department: 1, job_title: 1, employment_status: 'active', hire_date: '2020-01-01', created_at: '', updated_at: '',
    })
    vi.spyOn(reportingApi, 'listDirectReports').mockResolvedValue([])

    renderPage()

    expect(await screen.findByText('You have no direct reports.')).toBeInTheDocument()
  })
})
