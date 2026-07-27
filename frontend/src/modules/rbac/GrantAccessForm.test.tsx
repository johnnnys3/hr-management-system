import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { GrantAccessForm } from './GrantAccessForm'

function renderForm() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <GrantAccessForm />
    </QueryClientProvider>,
  )
}

describe('GrantAccessForm', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists users by email when unlinked to an employee', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))

    expect(await screen.findByText('jane@example.com')).toBeInTheDocument()
  })

  it('lists users by name and email when linked to an employee', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: 'Jane Doe', created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))

    expect(await screen.findByText('Jane Doe (jane@example.com)')).toBeInTheDocument()
  })

  it('shows a plain-language description for each role option', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 3, name: 'HR Administrator' }])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/what access/i))

    expect(await screen.findByText(/manage employee records, departments/i)).toBeInTheDocument()
  })

  it('submits a request and shows the pending-approval confirmation for a privileged role', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: 'Jane Doe', created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 3, name: 'Payroll Officer' }])
    const createSpy = vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 10, requester: 1, subject: 2, role: 3, status: 'pending', approver: null,
      requested_at: '', decided_at: null, requester_email: 'admin@example.com',
      subject_email: 'jane@example.com', subject_name: 'Jane Doe', role_name: 'Payroll Officer',
    })
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))
    await user.click(await screen.findByText('Jane Doe (jane@example.com)'))
    await user.click(screen.getByLabelText(/what access/i))
    await user.click(await screen.findByText(/process payroll and compensation/i))
    await user.click(screen.getByRole('button', { name: /submit/i }))

    await waitFor(() => expect(createSpy).toHaveBeenCalledWith(2, 'Payroll Officer'))
    expect(await screen.findByText(/awaiting approval from an hr administrator/i)).toBeInTheDocument()
  })

  it('shows the immediate-grant confirmation for Recruiter', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 4, name: 'Recruiter' }])
    vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 11, requester: 1, subject: 2, role: 4, status: 'approved', approver: null,
      requested_at: '', decided_at: '', requester_email: 'admin@example.com',
      subject_email: 'jane@example.com', subject_name: null, role_name: 'Recruiter',
    })
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))
    await user.click(await screen.findByText('jane@example.com'))
    await user.click(screen.getByLabelText(/what access/i))
    await user.click(await screen.findByText(/manage job postings and candidates/i))
    await user.click(screen.getByRole('button', { name: /submit/i }))

    expect(await screen.findByText(/recruiter access granted immediately/i)).toBeInTheDocument()
  })
})
