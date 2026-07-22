import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Alert,
  Button,
  DatePicker,
  Form,
  Input,
  List,
  Modal,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
  Upload,
  message,
} from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { ApiError } from '../../api/client'
import { changeManager, listDirectReports, listReportingRelationships } from '../../api/reporting'
import { useDepartments, useJobTitles } from '../departments/hooks'
import { STATUS_COLORS } from './constants'
import {
  createEmergencyContact,
  getEmployee,
  getEmployeeDocumentDownloadUrl,
  listEmergencyContacts,
  listEmployeeDocuments,
  listEmployees,
  listEmploymentHistory,
  updateEmergencyContact,
  updateEmployee,
  uploadEmployeeDocument,
} from '../../api/employees'
import type { EmergencyContact, Employee, EmployeeDocument, EmploymentStatus } from '../../api/types'

export function EmployeeDetailPage() {
  const params = useParams<{ id: string }>()
  const employeeId = Number(params.id)

  const { data: employee, isLoading, error } = useQuery({
    queryKey: ['employees', 'detail', employeeId],
    queryFn: () => getEmployee(employeeId),
  })

  if (isLoading) return null
  if (error || !employee) {
    return (
      <Alert
        type="error"
        message="Failed to load employee"
        description={error instanceof ApiError ? error.message : 'Employee not found.'}
      />
    )
  }

  return (
    <div>
      <Typography.Title level={3}>
        {employee.first_name} {employee.last_name}
      </Typography.Title>
      <Tabs
        items={[
          { key: 'profile', label: 'Profile', children: <ProfileTab employee={employee} /> },
          { key: 'reporting', label: 'Reporting', children: <ReportingTab employeeId={employeeId} /> },
          { key: 'history', label: 'Employment History', children: <HistoryTab employeeId={employeeId} /> },
          { key: 'documents', label: 'Documents', children: <DocumentsTab employeeId={employeeId} /> },
          { key: 'contacts', label: 'Emergency Contacts', children: <EmergencyContactsTab employeeId={employeeId} /> },
        ]}
      />
    </div>
  )
}

interface ProfileFormValues {
  first_name: string
  last_name: string
  date_of_birth: dayjs.Dayjs
  hire_date: dayjs.Dayjs
  department: number
  job_title: number
  employment_status: EmploymentStatus
}

function ProfileTab({ employee }: { employee: Employee }) {
  const queryClient = useQueryClient()
  const [form] = Form.useForm<ProfileFormValues>()
  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()

  const mutation = useMutation({
    mutationFn: (values: ProfileFormValues) =>
      updateEmployee(employee.id, {
        ...values,
        date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
        hire_date: values.hire_date.format('YYYY-MM-DD'),
      }),
    onSuccess: () => {
      message.success('Saved.')
      queryClient.invalidateQueries({ queryKey: ['employees', 'detail', employee.id] })
      queryClient.invalidateQueries({ queryKey: ['employees', 'history', employee.id] })
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
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
        hire_date: dayjs(employee.hire_date),
        department: employee.department,
        job_title: employee.job_title,
        employment_status: employee.employment_status,
      }}
      onFinish={(values) => mutation.mutate(values)}
    >
      <Form.Item label="Employee Number">
        <Input value={employee.employee_number} disabled />
      </Form.Item>
      <Form.Item label="First Name" name="first_name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="Last Name" name="last_name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="Date of Birth" name="date_of_birth" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="Hire Date" name="hire_date" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="Department" name="department" rules={[{ required: true }]}>
        <Select options={departments.map((d) => ({ label: d.name, value: d.id }))} />
      </Form.Item>
      <Form.Item label="Job Title" name="job_title" rules={[{ required: true }]}>
        <Select options={jobTitles.map((j) => ({ label: j.name, value: j.id }))} />
      </Form.Item>
      <Form.Item label="Employment Status" name="employment_status" rules={[{ required: true }]}>
        <Select
          options={Object.keys(STATUS_COLORS).map((s) => ({ label: s.replace('_', ' '), value: s }))}
        />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={mutation.isPending}>
        Save
      </Button>
    </Form>
  )
}

function ReportingTab({ employeeId }: { employeeId: number }) {
  const { me } = useAuth()
  const queryClient = useQueryClient()
  const [changeOpen, setChangeOpen] = useState(false)
  const canChangeManager = me?.groups.includes('HR Officer') ?? false

  const { data: relationships = [] } = useQuery({
    queryKey: ['reporting', 'relationships'],
    queryFn: () => listReportingRelationships(),
  })
  const managerId = relationships.find((r) => r.employee === employeeId)?.manager_employee

  const { data: manager } = useQuery({
    queryKey: ['employees', 'detail', managerId],
    queryFn: () => getEmployee(managerId as number),
    enabled: managerId !== undefined,
  })

  const { data: directReports = [], isLoading: reportsLoading } = useQuery({
    queryKey: ['reporting', 'direct-reports', employeeId],
    queryFn: () => listDirectReports(employeeId),
  })

  return (
    <div>
      <Typography.Title level={5}>Manager</Typography.Title>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <Typography.Text>
          {manager ? `${manager.first_name} ${manager.last_name} (${manager.employee_number})` : 'None'}
        </Typography.Text>
        {canChangeManager && (
          <Button size="small" onClick={() => setChangeOpen(true)}>
            Change Manager
          </Button>
        )}
      </div>
      <Typography.Title level={5}>Direct Reports</Typography.Title>
      <Table<Employee>
        rowKey="id"
        loading={reportsLoading}
        dataSource={directReports}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Employee #', dataIndex: 'employee_number' },
          { title: 'First Name', dataIndex: 'first_name' },
          { title: 'Last Name', dataIndex: 'last_name' },
        ]}
      />
      {changeOpen && (
        <ChangeManagerModal
          employeeId={employeeId}
          onClose={() => setChangeOpen(false)}
          onSaved={() => {
            queryClient.invalidateQueries({ queryKey: ['reporting', 'relationships'] })
            queryClient.invalidateQueries({ queryKey: ['employees', 'history', employeeId] })
            setChangeOpen(false)
          }}
        />
      )}
    </div>
  )
}

function ChangeManagerModal({
  employeeId,
  onClose,
  onSaved,
}: {
  employeeId: number
  onClose: () => void
  onSaved: () => void
}) {
  const { data: employees = [] } = useQuery({ queryKey: ['employees', 'list', {}], queryFn: () => listEmployees() })
  const [managerEmployeeId, setManagerEmployeeId] = useState<number | undefined>()

  const mutation = useMutation({
    mutationFn: () => changeManager(employeeId, managerEmployeeId as number),
    onSuccess: onSaved,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
  })

  return (
    <Modal
      open
      title="Change Manager"
      onCancel={onClose}
      onOk={() => mutation.mutate()}
      okText="Save"
      okButtonProps={{ disabled: managerEmployeeId === undefined }}
      confirmLoading={mutation.isPending}
    >
      <Select
        style={{ width: '100%' }}
        showSearch
        placeholder="Select a manager"
        optionFilterProp="label"
        value={managerEmployeeId}
        onChange={setManagerEmployeeId}
        options={employees
          .filter((e) => e.id !== employeeId)
          .map((e) => ({ label: `${e.first_name} ${e.last_name} (${e.employee_number})`, value: e.id }))}
      />
    </Modal>
  )
}

function HistoryTab({ employeeId }: { employeeId: number }) {
  const { data: history = [], isLoading } = useQuery({
    queryKey: ['employees', 'history', employeeId],
    queryFn: () => listEmploymentHistory(employeeId),
  })

  return (
    <Table
      rowKey="id"
      loading={isLoading}
      dataSource={history}
      pagination={{ pageSize: 25 }}
      columns={[
        { title: 'Event', dataIndex: 'event_type', render: (v: string) => v.replaceAll('_', ' ') },
        { title: 'Effective Date', dataIndex: 'effective_date' },
        { title: 'Previous', dataIndex: 'previous_value', render: (v: unknown) => (v ? JSON.stringify(v) : '—') },
        { title: 'New', dataIndex: 'new_value', render: (v: unknown) => JSON.stringify(v) },
      ]}
    />
  )
}

function DocumentsTab({ employeeId }: { employeeId: number }) {
  const queryClient = useQueryClient()
  const [documentType, setDocumentType] = useState('')
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['employees', 'documents', employeeId],
    queryFn: () => listEmployeeDocuments(employeeId),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadEmployeeDocument(employeeId, documentType, file),
    onSuccess: () => {
      message.success('Uploaded.')
      setDocumentType('')
      queryClient.invalidateQueries({ queryKey: ['employees', 'documents', employeeId] })
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Upload failed.'),
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

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="Document type"
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          style={{ width: 200 }}
        />
        <Upload
          showUploadList={false}
          disabled={!documentType || uploadMutation.isPending}
          beforeUpload={(file) => {
            uploadMutation.mutate(file)
            return false
          }}
        >
          <Button disabled={!documentType} loading={uploadMutation.isPending}>
            Upload
          </Button>
        </Upload>
      </Space>
      <Table<EmployeeDocument>
        rowKey="id"
        loading={isLoading}
        dataSource={documents}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Type', dataIndex: 'document_type' },
          { title: 'File Name', dataIndex: 'file_name' },
          { title: 'Uploaded', dataIndex: 'created_at' },
          {
            title: 'Actions',
            render: (_: unknown, doc: EmployeeDocument) => (
              <Button size="small" onClick={() => handleDownload(doc)}>
                Download
              </Button>
            ),
          },
        ]}
      />
    </div>
  )
}

interface ContactFormValues {
  name: string
  relationship: string
  phone: string
  email?: string
  is_primary: boolean
}

function EmergencyContactsTab({ employeeId }: { employeeId: number }) {
  const queryClient = useQueryClient()
  const [modalContact, setModalContact] = useState<EmergencyContact | 'new' | null>(null)
  const { data: contacts = [], isLoading } = useQuery({
    queryKey: ['employees', 'contacts', employeeId],
    queryFn: () => listEmergencyContacts(employeeId),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['employees', 'contacts', employeeId] })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setModalContact('new')}>
          New Contact
        </Button>
      </div>
      <List
        loading={isLoading}
        dataSource={contacts}
        rowKey="id"
        renderItem={(contact) => (
          <List.Item
            onClick={() => setModalContact(contact)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setModalContact(contact)
              }
            }}
            tabIndex={0}
            style={{ cursor: 'pointer' }}
            actions={[contact.is_primary ? <Tag color="blue" key="primary">Primary</Tag> : null]}
          >
            <List.Item.Meta title={contact.name} description={`${contact.relationship} · ${contact.phone}`} />
          </List.Item>
        )}
      />
      {modalContact && (
        <ContactFormModal
          employeeId={employeeId}
          contact={modalContact === 'new' ? null : modalContact}
          onClose={() => setModalContact(null)}
          onSaved={() => {
            invalidate()
            setModalContact(null)
          }}
        />
      )}
    </div>
  )
}

function ContactFormModal({
  employeeId,
  contact,
  onClose,
  onSaved,
}: {
  employeeId: number
  contact: EmergencyContact | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form] = Form.useForm<ContactFormValues>()

  const mutation = useMutation({
    mutationFn: (values: ContactFormValues) =>
      contact ? updateEmergencyContact(employeeId, contact.id, values) : createEmergencyContact(employeeId, values),
    onSuccess: onSaved,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
  })

  return (
    <Modal
      open
      title={contact ? 'Edit Contact' : 'New Contact'}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText={contact ? 'Save' : 'Create'}
      confirmLoading={mutation.isPending}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          name: contact?.name,
          relationship: contact?.relationship,
          phone: contact?.phone,
          email: contact?.email ?? undefined,
          is_primary: contact?.is_primary ?? false,
        }}
        onFinish={(values) => mutation.mutate(values)}
      >
        <Form.Item label="Name" name="name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Relationship" name="relationship" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Phone" name="phone" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Email" name="email" rules={[{ type: 'email' }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Primary" name="is_primary" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  )
}
