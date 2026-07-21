import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, DatePicker, Form, Input, List, Table, Tabs, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { ApiError } from '../../api/client'
import { getEmployeeDocumentDownloadUrl, listEmployeeDocuments, listEmploymentHistory } from '../../api/employees'
import { getMyProfile, updateMyProfile } from '../../api/selfService'
import type { Employee, EmployeeDocument } from '../../api/types'

function ProfileError({ error }: { error: unknown }) {
  return (
    <Alert
      type="error"
      message="Failed to load your profile"
      description={error instanceof ApiError ? error.message : 'An error occurred while loading your profile.'}
    />
  )
}

export function MyProfilePage() {
  const { data: employee, isLoading, error } = useQuery({ queryKey: ['self-service', 'me'], queryFn: getMyProfile })

  if (error) return <ProfileError error={error} />
  if (isLoading || !employee) return null

  const items = [
    { key: 'profile', label: 'Profile', children: <ProfileTab employee={employee} /> },
    { key: 'history', label: 'Employment History', children: <EmploymentHistoryTab employeeId={employee.id} /> },
    { key: 'documents', label: 'Documents', children: <DocumentsTab employeeId={employee.id} /> },
  ]

  return (
    <div>
      <Typography.Title level={3}>My Profile</Typography.Title>
      <Tabs items={items} />
    </div>
  )
}

function ProfileTab({ employee }: { employee: Employee }) {
  const queryClient = useQueryClient()
  const [form] = Form.useForm()

  const updateMutation = useMutation({
    mutationFn: updateMyProfile,
    onSuccess: () => {
      message.success('Profile updated.')
      queryClient.invalidateQueries({ queryKey: ['self-service', 'me'] })
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to update profile.'),
  })

  return (
    <Form
      form={form}
      layout="vertical"
      style={{ maxWidth: 480 }}
      initialValues={{
        first_name: employee.first_name,
        last_name: employee.last_name,
        date_of_birth: dayjs(employee.date_of_birth),
      }}
      onFinish={(values) =>
        updateMutation.mutate({
          first_name: values.first_name,
          last_name: values.last_name,
          date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
        })
      }
    >
      <Form.Item label="Employee Number">
        <Input value={employee.employee_number} disabled />
      </Form.Item>
      <Form.Item name="first_name" label="First Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="last_name" label="Last Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="date_of_birth" label="Date of Birth" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="Employment Status">
        <Input value={employee.employment_status} disabled />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={updateMutation.isPending}>
        Save
      </Button>
    </Form>
  )
}

function EmploymentHistoryTab({ employeeId }: { employeeId: number }) {
  const { data: history = [], isLoading, error } = useQuery({
    queryKey: ['employees', 'employment-history', employeeId],
    queryFn: () => listEmploymentHistory(employeeId),
  })

  if (error) return <ProfileError error={error} />

  return (
    <Table
      rowKey="id"
      loading={isLoading}
      dataSource={history}
      pagination={{ pageSize: 25 }}
      columns={[
        { title: 'Event', dataIndex: 'event_type' },
        { title: 'Effective Date', dataIndex: 'effective_date' },
        { title: 'Previous', dataIndex: 'previous_value', render: (v: unknown) => (v ? JSON.stringify(v) : '—') },
        { title: 'New', dataIndex: 'new_value', render: (v: unknown) => JSON.stringify(v) },
      ]}
    />
  )
}

function DocumentsTab({ employeeId }: { employeeId: number }) {
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['employees', 'documents', employeeId],
    queryFn: () => listEmployeeDocuments(employeeId),
  })

  const handleDownload = async (doc: EmployeeDocument) => {
    try {
      const { url } = await getEmployeeDocumentDownloadUrl(employeeId, doc.id)
      window.open(url, '_blank', 'noopener,noreferrer')
    } catch (e) {
      message.error(e instanceof ApiError ? e.message : 'Download failed.')
    }
  }

  if (error) return <ProfileError error={error} />

  return (
    <List
      loading={isLoading}
      dataSource={documents}
      locale={{ emptyText: 'No documents.' }}
      renderItem={(doc) => (
        <List.Item
          actions={[
            <Button key="download" size="small" onClick={() => handleDownload(doc)}>
              Download
            </Button>,
          ]}
        >
          <List.Item.Meta title={doc.file_name} description={doc.document_type} />
        </List.Item>
      )}
    />
  )
}
