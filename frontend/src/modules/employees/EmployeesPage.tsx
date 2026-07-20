import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, DatePicker, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { createEmployee, listEmployees, type EmployeeListParams } from '../../api/employees'
import type { Employee } from '../../api/types'
import { useDepartments, useJobTitles } from '../departments/hooks'
import { STATUS_COLORS } from './constants'

const EMPLOYEES_QUERY_KEY = ['employees', 'list']

export function EmployeesPage() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<EmployeeListParams>({})
  const [createOpen, setCreateOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()
  const {
    data: employees = [],
    isLoading,
    error,
  } = useQuery({ queryKey: [...EMPLOYEES_QUERY_KEY, filters], queryFn: () => listEmployees(filters) })

  const departmentName = (id: number) => departments.find((d) => d.id === id)?.name ?? id
  const jobTitleName = (id: number) => jobTitles.find((j) => j.id === id)?.name ?? id

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3}>Employees</Typography.Title>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Employee
        </Button>
      </div>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search
          placeholder="Search name or employee number"
          allowClear
          style={{ width: 260 }}
          onSearch={(value) => setFilters((f) => ({ ...f, search: value || undefined }))}
        />
        <Select
          placeholder="Department"
          allowClear
          style={{ width: 180 }}
          options={departments.map((d) => ({ label: d.name, value: d.id }))}
          onChange={(value) => setFilters((f) => ({ ...f, department_id: value }))}
        />
        <Select
          placeholder="Job title"
          allowClear
          style={{ width: 180 }}
          options={jobTitles.map((j) => ({ label: j.name, value: j.id }))}
          onChange={(value) => setFilters((f) => ({ ...f, job_title_id: value }))}
        />
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 160 }}
          options={Object.keys(STATUS_COLORS).map((s) => ({ label: s.replace('_', ' '), value: s }))}
          onChange={(value) => setFilters((f) => ({ ...f, employment_status: value }))}
        />
      </Space>
      {error ? (
        <Alert
          type="error"
          message="Failed to load employees"
          description={error instanceof ApiError ? error.message : 'An error occurred while loading the list.'}
        />
      ) : (
        <Table<Employee>
          rowKey="id"
          loading={isLoading}
          dataSource={employees}
          pagination={{ pageSize: 25 }}
          onRow={(record) => ({
            onClick: () => navigate(`/employees/${record.id}`),
            onKeyDown: (e) => {
              if (e.key === 'Enter') {
                navigate(`/employees/${record.id}`)
              }
            },
            tabIndex: 0,
            style: { cursor: 'pointer' },
          })}
          columns={[
            { title: 'Employee #', dataIndex: 'employee_number' },
            { title: 'First Name', dataIndex: 'first_name' },
            { title: 'Last Name', dataIndex: 'last_name' },
            { title: 'Department', dataIndex: 'department', render: departmentName },
            { title: 'Job Title', dataIndex: 'job_title', render: jobTitleName },
            {
              title: 'Status',
              dataIndex: 'employment_status',
              render: (statusValue: string) => (
                <Tag color={STATUS_COLORS[statusValue]}>{statusValue.replace('_', ' ')}</Tag>
              ),
            },
          ]}
        />
      )}
      {createOpen && (
        <CreateEmployeeModal
          departments={departments}
          jobTitles={jobTitles}
          onClose={() => setCreateOpen(false)}
          onCreated={(employee) => {
            queryClient.invalidateQueries({ queryKey: EMPLOYEES_QUERY_KEY })
            setCreateOpen(false)
            navigate(`/employees/${employee.id}`)
          }}
        />
      )}
    </div>
  )
}

interface CreateFormValues {
  employee_number: string
  first_name: string
  last_name: string
  date_of_birth: dayjs.Dayjs
  hire_date: dayjs.Dayjs
  department: number
  job_title: number
}

function CreateEmployeeModal({
  departments,
  jobTitles,
  onClose,
  onCreated,
}: {
  departments: { id: number; name: string }[]
  jobTitles: { id: number; name: string }[]
  onClose: () => void
  onCreated: (employee: Employee) => void
}) {
  const [form] = Form.useForm<CreateFormValues>()

  const mutation = useMutation({
    mutationFn: (values: CreateFormValues) =>
      createEmployee({
        employee_number: values.employee_number,
        first_name: values.first_name,
        last_name: values.last_name,
        date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
        hire_date: values.hire_date.format('YYYY-MM-DD'),
        department: values.department,
        job_title: values.job_title,
      }),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="New Employee"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Create"
      confirmLoading={mutation.isPending}
    >
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="Employee Number" name="employee_number" rules={[{ required: true }]}>
          <Input />
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
      </Form>
    </Modal>
  )
}
