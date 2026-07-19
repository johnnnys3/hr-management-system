import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as departmentsApi from '../../api/departments'
import { DepartmentsPage } from './DepartmentsPage'

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <DepartmentsPage />
    </QueryClientProvider>,
  )
}

describe('DepartmentsPage', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists departments from GET /api/departments/', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([
      { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    renderPage()

    expect(await screen.findByText('Engineering')).toBeInTheDocument()
  })

  it('creates a department via the New Department form', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    const createSpy = vi.spyOn(departmentsApi, 'createDepartment').mockResolvedValue({
      id: 2,
      name: 'Finance',
      is_active: true,
      created_at: '',
      updated_at: '',
    })
    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new department/i }))
    const dialog = within(screen.getByRole('dialog'))
    await user.type(dialog.getByLabelText(/name/i), 'Finance')
    await user.click(dialog.getByRole('button', { name: /^create$/i }))

    await waitFor(() => expect(createSpy).toHaveBeenCalledWith({ name: 'Finance', is_active: true }))
  })

  it('retires a department via row click and the Active switch', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([
      { id: 1, name: 'Engineering', is_active: true, created_at: '', updated_at: '' },
    ])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([])
    const updateSpy = vi.spyOn(departmentsApi, 'updateDepartment').mockResolvedValue({
      id: 1,
      name: 'Engineering',
      is_active: false,
      created_at: '',
      updated_at: '',
    })
    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByText('Engineering'))
    const dialog = within(screen.getByRole('dialog'))
    await user.click(dialog.getByRole('switch'))
    await user.click(dialog.getByRole('button', { name: /^save$/i }))

    await waitFor(() =>
      expect(updateSpy).toHaveBeenCalledWith(1, expect.objectContaining({ is_active: false })),
    )
  })

  it('lists job titles on the Job Titles tab', async () => {
    vi.spyOn(departmentsApi, 'listDepartments').mockResolvedValue([])
    vi.spyOn(departmentsApi, 'listJobTitles').mockResolvedValue([
      { id: 1, name: 'Software Engineer', is_active: true, created_at: '', updated_at: '' },
    ])
    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('tab', { name: /job titles/i }))

    expect(await screen.findByText('Software Engineer')).toBeInTheDocument()
  })
})
