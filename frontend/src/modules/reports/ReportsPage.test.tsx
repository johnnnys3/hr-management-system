import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import * as reportsApi from '../../api/reports'
import { AuthContext } from '../../auth/AuthContext'
import { ReportsPage } from './ReportsPage'

function renderPage(groups: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          me: { id: 1, email: 'user@b.com', groups, is_employee: true, is_manager: false, second_factor_enrollment_pending: false },
          isLoading: false,
          refetch: async () => {},
          logout: async () => {},
        }}
      >
        <ReportsPage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('ReportsPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows an HR Officer the org report tabs but not payroll tabs', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(reportsApi, 'getHeadcountReport').mockResolvedValue({ aggregate: { total: 10 } })

    renderPage(['HR Officer'])

    expect(await screen.findByText('Headcount')).toBeInTheDocument()
    expect(screen.getByText('Leave Utilization')).toBeInTheDocument()
    expect(screen.getByText('Turnover')).toBeInTheDocument()
    expect(screen.queryByText('Payroll Cost')).not.toBeInTheDocument()
    expect(screen.queryByText('Payroll Summary')).not.toBeInTheDocument()
    expect(await screen.findByText('Total Headcount')).toBeInTheDocument()
  })

  it('shows a Payroll Officer the payroll tabs but not org report tabs', async () => {
    vi.spyOn(reportsApi, 'getPayrollCostReport').mockResolvedValue({ aggregate: { gross_pay: 1000, net_pay: 800 } })

    renderPage(['Payroll Officer'])

    expect(await screen.findByText('Payroll Cost')).toBeInTheDocument()
    expect(screen.getByText('Payroll Summary')).toBeInTheDocument()
    expect(screen.queryByText('Headcount')).not.toBeInTheDocument()
  })

  it('starts an export and shows the download link once the job completes', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(reportsApi, 'getHeadcountReport').mockResolvedValue({ aggregate: { total: 10 } })
    const createSpy = vi.spyOn(reportsApi, 'createReportExport').mockResolvedValue({
      id: 7,
      report_type: 'headcount',
      params: {},
      status: 'pending',
      download_url: null,
      failed_reason: null,
      generated_at: null,
      created_at: '',
    })
    vi.spyOn(reportsApi, 'getReportExport').mockResolvedValue({
      id: 7,
      report_type: 'headcount',
      params: {},
      status: 'complete',
      download_url: 'https://example.com/export.csv',
      failed_reason: null,
      generated_at: '2026-07-21T00:00:00Z',
      created_at: '',
    })

    renderPage(['HR Officer'])
    const user = userEvent.setup()

    await user.click(await screen.findByText('Export'))
    expect(createSpy).toHaveBeenCalledWith('headcount', { department_id: undefined })
    expect(await screen.findByText('Download')).toBeInTheDocument()
  })
})
