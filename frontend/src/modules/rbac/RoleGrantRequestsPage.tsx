import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Card, Form, InputNumber, Popconfirm, Space, Table, Tag, Typography } from 'antd'
import { useState } from 'react'
import { createRoleGrantRequest, decideRoleGrantRequest, listRoleGrantRequests } from '../../api/rbac'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import type { RoleGrantRequestRecord } from '../../api/types'

const REQUESTS_QUERY_KEY = ['rbac', 'role-grant-requests']

export function RoleGrantRequestsPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <RaiseRequestForm />
      <RequestsTable />
    </Space>
  )
}

function RaiseRequestForm() {
  const queryClient = useQueryClient()
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { subjectUserId: number; roleId: number }) => {
    setError(null)
    setSubmitting(true)
    try {
      const created = await createRoleGrantRequest(values.subjectUserId, values.roleId)
      setResult(`Request #${created.id} submitted.`)
      queryClient.invalidateQueries({ queryKey: REQUESTS_QUERY_KEY })
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Raise a role grant request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Form layout="inline" onFinish={handleSubmit}>
        <Form.Item label="Subject user ID" name="subjectUserId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item label="Role ID" name="roleId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting}>
            Submit request
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

function RequestsTable() {
  const { me } = useAuth()
  const queryClient = useQueryClient()
  const { data: requests = [], isLoading } = useQuery({ queryKey: REQUESTS_QUERY_KEY, queryFn: listRoleGrantRequests })

  const mutation = useMutation({
    mutationFn: ({ id, decision }: { id: number; decision: 'approved' | 'refused' }) =>
      decideRoleGrantRequest(id, decision),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REQUESTS_QUERY_KEY }),
  })

  return (
    <Card title="Your requests and requests awaiting your decision">
      <Table<RoleGrantRequestRecord>
        rowKey="id"
        loading={isLoading}
        dataSource={requests}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'ID', dataIndex: 'id' },
          { title: 'Requester', dataIndex: 'requester' },
          { title: 'Subject', dataIndex: 'subject' },
          { title: 'Role', dataIndex: 'role' },
          {
            title: 'Status',
            dataIndex: 'status',
            render: (status: string) => (
              <Tag color={status === 'approved' ? 'green' : status === 'refused' ? 'red' : 'default'}>{status}</Tag>
            ),
          },
          {
            title: 'Actions',
            render: (_: unknown, record: RoleGrantRequestRecord) =>
              record.status === 'pending' && record.requester !== me?.id ? (
                <Space>
                  <Popconfirm
                    title="Approve this role grant request?"
                    onConfirm={() => mutation.mutate({ id: record.id, decision: 'approved' })}
                  >
                    <Button size="small" loading={mutation.isPending && mutation.variables?.id === record.id}>
                      Approve
                    </Button>
                  </Popconfirm>
                  <Popconfirm
                    title="Refuse this role grant request?"
                    onConfirm={() => mutation.mutate({ id: record.id, decision: 'refused' })}
                  >
                    <Button
                      size="small"
                      danger
                      loading={mutation.isPending && mutation.variables?.id === record.id}
                    >
                      Refuse
                    </Button>
                  </Popconfirm>
                </Space>
              ) : (
                <Typography.Text type="secondary">—</Typography.Text>
              ),
          },
        ]}
      />
    </Card>
  )
}
