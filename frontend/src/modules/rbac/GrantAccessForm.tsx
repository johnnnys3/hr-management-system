import { useMutation, useQuery } from '@tanstack/react-query'
import { Alert, Button, Form, Select, Typography } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { createRoleGrantRequest, listAssignedRoles, listUsers } from '../../api/rbac'

const ROLE_DESCRIPTIONS: Record<string, string> = {
  'System Administrator': 'Manage accounts, roles, and system configuration',
  'HR Administrator': 'Manage employee records, departments, and HR configuration',
  'HR Officer': 'Handle day-to-day HR operations and onboarding',
  'Recruiter': 'Manage job postings and candidates',
  'Payroll Officer': 'Process payroll and compensation',
  'Executive': 'View organization-wide reports',
}

export function GrantAccessForm() {
  const { data: users = [] } = useQuery({ queryKey: ['rbac', 'users'], queryFn: listUsers })
  const { data: roles = [] } = useQuery({ queryKey: ['rbac', 'roles'], queryFn: listAssignedRoles })
  const [subjectUserId, setSubjectUserId] = useState<number | null>(null)
  const [roleId, setRoleId] = useState<number | null>(null)
  const [confirmation, setConfirmation] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => createRoleGrantRequest(subjectUserId as number, roleId as number),
    onSuccess: (result) => {
      setError(null)
      setConfirmation(
        result.status === 'approved'
          ? `${result.role_name} access granted immediately.`
          : 'Request submitted — awaiting approval from an HR Administrator.',
      )
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.'),
  })

  return (
    <div>
      <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 14 }}>
        Grant a user access
      </Typography.Title>
      {confirmation && <Alert type="success" message={confirmation} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Form layout="vertical" onFinish={() => mutation.mutate()}>
        <Form.Item label="Who gets access" required>
          <Select
            aria-label="Who gets access"
            style={{ minWidth: 320 }}
            value={subjectUserId ?? undefined}
            onChange={(value) => setSubjectUserId(value)}
            showSearch
            optionFilterProp="label"
            options={users.map((u) => ({
              value: u.id,
              label: u.employee_name ? `${u.employee_name} (${u.email})` : u.email,
            }))}
          />
        </Form.Item>
        <Form.Item label="What access" required>
          <Select
            aria-label="What access"
            style={{ minWidth: 320 }}
            value={roleId ?? undefined}
            onChange={(value) => setRoleId(value)}
            options={roles.map((r) => ({
              value: r.id,
              label: `${r.name} — ${ROLE_DESCRIPTIONS[r.name] ?? ''}`,
            }))}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending} disabled={!subjectUserId || !roleId}>
            Submit
          </Button>
        </Form.Item>
      </Form>
    </div>
  )
}
