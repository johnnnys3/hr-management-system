import { useQuery } from '@tanstack/react-query'
import { Alert, Button, DatePicker, Form, Input, List, Table, Tabs, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { ApiError } from '../../api/client'
import { getEmployeeDocumentDownloadUrl, listEmployeeDocuments, listEmploymentHistory } from '../../api/employees'
import { listLeaveBalances } from '../../api/leave'
import { getMyProfile } from '../../api/selfService'
import type { Employee, EmployeeDocument } from '../../api/types'
import { useAuth } from '../../auth/AuthContext'
import { useDepartments, useJobTitles } from '../departments/hooks'
import { NotificationPreferencesTab } from './NotificationPreferencesTab'

const HR_CONFIG_GROUPS = ['HR Administrator', 'HR Officer', 'Payroll Officer']

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
    { key: 'notifications', label: 'Notifications', children: <NotificationPreferencesTab /> },
  ]

  return (
    <div>
      <Typography.Title level={3}>My Profile</Typography.Title>
      <Tabs items={items} />
    </div>
  )
}

function ProfileTab({ employee }: { employee: Employee }) {
  const { me } = useAuth()
  const canSeeConfig = me?.groups.some((g) => HR_CONFIG_GROUPS.includes(g)) ?? false
  const { data: departments = [] } = useDepartments({ enabled: canSeeConfig })
  const { data: jobTitles = [] } = useJobTitles({ enabled: canSeeConfig })
  const { data: balances = [] } = useQuery({ queryKey: ['leave', 'balances'], queryFn: listLeaveBalances })

  const departmentName = departments.find((d) => d.id === employee.department)?.name ?? employee.department
  const jobTitleName = jobTitles.find((j) => j.id === employee.job_title)?.name ?? employee.job_title
  const totalEntitled = balances.reduce((sum, b) => sum + Number(b.entitled_days), 0)
  const totalUsed = balances.reduce((sum, b) => sum + Number(b.used_days), 0)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, maxWidth: 900 }}>
      <Form layout="vertical">
        <Form.Item label="Employee Number" htmlFor="employee_number">
          <Input id="employee_number" value={employee.employee_number} disabled />
        </Form.Item>
        <Form.Item label="First Name" htmlFor="first_name">
          <Input id="first_name" value={employee.first_name} disabled />
        </Form.Item>
        <Form.Item label="Last Name" htmlFor="last_name">
          <Input id="last_name" value={employee.last_name} disabled />
        </Form.Item>
        <Form.Item label="Date of Birth" htmlFor="date_of_birth">
          <DatePicker id="date_of_birth" style={{ width: '100%' }} value={dayjs(employee.date_of_birth)} disabled />
        </Form.Item>
        <Form.Item label="Employment Status" htmlFor="employment_status">
          <Input id="employment_status" value={employee.employment_status} disabled />
        </Form.Item>
        <Typography.Text type="secondary">
          To correct your name or date of birth, contact HR.
        </Typography.Text>
      </Form>
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#111', marginBottom: 12 }}>At a Glance</div>
        <div
          style={{
            padding: '12px 0',
            borderBottom: '1px solid #f2f2f2',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: 13,
          }}
        >
          <span style={{ color: 'rgba(0,0,0,0.45)' }}>Department</span>
          <span>{departmentName}</span>
        </div>
        <div
          style={{
            padding: '12px 0',
            borderBottom: '1px solid #f2f2f2',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: 13,
          }}
        >
          <span style={{ color: 'rgba(0,0,0,0.45)' }}>Job Title</span>
          <span>{jobTitleName}</span>
        </div>
        <div
          style={{
            padding: '12px 0',
            borderBottom: '1px solid #f2f2f2',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: 13,
          }}
        >
          <span style={{ color: 'rgba(0,0,0,0.45)' }}>Hire Date</span>
          <span>{employee.hire_date}</span>
        </div>
        <div style={{ padding: '12px 0', display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
          <span style={{ color: 'rgba(0,0,0,0.45)' }}>Leave Balance</span>
          <span>
            {totalUsed} / {totalEntitled} days
          </span>
        </div>
      </div>
    </div>
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
    // Open the tab synchronously from the click handler, before the await —
    // otherwise browsers can treat the post-await window.open as an
    // unsolicited popup and block it. noopener/noreferrer are omitted here
    // since they'd drop the window reference this needs to set .location on.
    const placeholder = window.open('', '_blank')
    if (!placeholder) {
      message.error('Download blocked by your browser’s pop-up blocker. Please allow pop-ups for this site and try again.')
      return
    }
    try {
      const { url } = await getEmployeeDocumentDownloadUrl(employeeId, doc.id)
      placeholder.location.href = url
    } catch (e) {
      placeholder.close()
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
