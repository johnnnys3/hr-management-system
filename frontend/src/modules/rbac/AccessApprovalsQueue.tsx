import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, List, Popconfirm, Space, Tag, Typography } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { decideRoleGrantRequest, listRoleGrantRequests } from '../../api/rbac'
import type { RoleGrantRequestRecord } from '../../api/types'

const REQUESTS_QUERY_KEY = ['rbac', 'role-grant-requests']

export function AccessApprovalsQueue() {
  const queryClient = useQueryClient()
  const { data: requests = [] } = useQuery({ queryKey: REQUESTS_QUERY_KEY, queryFn: listRoleGrantRequests })
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: ({ id, decision }: { id: number; decision: 'approved' | 'refused' }) =>
      decideRoleGrantRequest(id, decision),
    onSuccess: () => {
      setError(null)
      queryClient.invalidateQueries({ queryKey: REQUESTS_QUERY_KEY })
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.'),
  })

  const pending = requests.filter((r) => r.status === 'pending')
  const decided = requests.filter((r) => r.status !== 'pending')

  return (
    <div>
      <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 14 }}>
        Pending approvals
      </Typography.Title>
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <List<RoleGrantRequestRecord>
        dataSource={pending}
        locale={{ emptyText: 'No requests waiting on your decision.' }}
        renderItem={(record) => (
          <List.Item
            actions={[
              <Popconfirm key="approve" title="Approve this request?" onConfirm={() => mutation.mutate({ id: record.id, decision: 'approved' })}>
                <Button size="small" loading={mutation.isPending && mutation.variables?.id === record.id && mutation.variables?.decision === 'approved'}>
                  Approve
                </Button>
              </Popconfirm>,
              <Popconfirm key="decline" title="Decline this request?" onConfirm={() => mutation.mutate({ id: record.id, decision: 'refused' })}>
                <Button size="small" danger loading={mutation.isPending && mutation.variables?.id === record.id && mutation.variables?.decision === 'refused'}>
                  Decline
                </Button>
              </Popconfirm>,
            ]}
          >
            {record.requester_email} requests {record.role_name} access for{' '}
            {record.subject_name ? `${record.subject_name} (${record.subject_email})` : record.subject_email}
          </List.Item>
        )}
      />
      <Typography.Title level={5} style={{ marginTop: 32, marginBottom: 14 }}>
        History
      </Typography.Title>
      <List<RoleGrantRequestRecord>
        dataSource={decided}
        locale={{ emptyText: 'No decided requests yet.' }}
        renderItem={(record) => (
          <List.Item>
            <Space>
              <Tag color={record.status === 'approved' ? 'green' : 'red'}>
                {record.status === 'approved' ? 'Approved' : 'Declined'}
              </Tag>
              {record.requester_email} requested {record.role_name} access for{' '}
              {record.subject_name ? `${record.subject_name} (${record.subject_email})` : record.subject_email}
            </Space>
          </List.Item>
        )}
      />
    </div>
  )
}
