import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, DatePicker, Form, Input, InputNumber, Modal, Select, Table, Tabs, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { createPayGrade, createSalaryStructure } from '../../api/compensation'
import type { PayGrade, SalaryStructure } from '../../api/types'
import { StatStrip } from '../../components/StatStrip'
import { usePayGrades, useSalaryStructures } from './hooks'

// Modules 15's own client interface — plain SalaryStructure/PayGrade CRUD
// for HR Administrator, per docs/07-iam-rbac.md §4.2. Assigning an
// employee to a pay grade (HR Officer's own action, HRMS-FR-057/058) lives
// on EmployeeDetailPage's Compensation tab instead, next to the employee
// record it applies to, matching Reporting/Emergency Contacts' own
// per-employee-tab precedent rather than a second standalone page.
export function CompensationPage() {
  const [activeKey, setActiveKey] = useState('structures')
  const { data: structures = [] } = useSalaryStructures()
  const { data: payGrades = [] } = usePayGrades()

  return (
    <div>
      <Typography.Title level={3}>Compensation</Typography.Title>
      <Tabs
        activeKey={activeKey}
        onChange={setActiveKey}
        items={[
          { key: 'structures', label: 'Salary Structures' },
          { key: 'grades', label: 'Pay Grades' },
        ]}
      />
      <StatStrip
        stats={[
          { label: 'Salary Structures', value: structures.length },
          { label: 'Pay Grades', value: payGrades.length },
        ]}
      />
      {activeKey === 'structures' ? <SalaryStructuresTab structures={structures} /> : <PayGradesTab payGrades={payGrades} structures={structures} />}
    </div>
  )
}

function SalaryStructuresTab({ structures }: { structures: SalaryStructure[] }) {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm<{ name: string; description?: string; effective_from: dayjs.Dayjs }>()

  const mutation = useMutation({
    mutationFn: (values: { name: string; description?: string; effective_from: dayjs.Dayjs }) =>
      createSalaryStructure({ ...values, effective_from: values.effective_from.format('YYYY-MM-DD') }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compensation', 'salary-structures'] })
      setCreateOpen(false)
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Salary Structure
        </Button>
      </div>
      <Table<SalaryStructure>
        rowKey="id"
        dataSource={structures}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Description', dataIndex: 'description', render: (d: string | null) => d ?? '—' },
          { title: 'Effective From', dataIndex: 'effective_from' },
        ]}
      />
      {createOpen && (
        <Modal
          open
          title="New Salary Structure"
          onCancel={() => setCreateOpen(false)}
          onOk={() => form.submit()}
          okText="Create"
          confirmLoading={mutation.isPending}
        >
          <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
            <Form.Item label="Name" name="name" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Description" name="description">
              <Input.TextArea rows={3} />
            </Form.Item>
            <Form.Item label="Effective From" name="effective_from" rules={[{ required: true }]}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Form>
        </Modal>
      )}
    </div>
  )
}

function PayGradesTab({ payGrades, structures }: { payGrades: PayGrade[]; structures: SalaryStructure[] }) {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm<{ salary_structure: number; name: string; min_salary: number; max_salary: number }>()

  const structureName = (id: number) => structures.find((s) => s.id === id)?.name ?? id

  const mutation = useMutation({
    mutationFn: (values: { salary_structure: number; name: string; min_salary: number; max_salary: number }) =>
      createPayGrade({
        salary_structure: values.salary_structure,
        name: values.name,
        min_salary: String(values.min_salary),
        max_salary: String(values.max_salary),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compensation', 'pay-grades'] })
      setCreateOpen(false)
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Pay Grade
        </Button>
      </div>
      <Table<PayGrade>
        rowKey="id"
        dataSource={payGrades}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Salary Structure', dataIndex: 'salary_structure', render: structureName },
          { title: 'Min Salary', dataIndex: 'min_salary' },
          { title: 'Max Salary', dataIndex: 'max_salary' },
        ]}
      />
      {createOpen && (
        <Modal
          open
          title="New Pay Grade"
          onCancel={() => setCreateOpen(false)}
          onOk={() => form.submit()}
          okText="Create"
          confirmLoading={mutation.isPending}
        >
          <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
            <Form.Item label="Salary Structure" name="salary_structure" rules={[{ required: true }]}>
              <Select options={structures.map((s) => ({ label: s.name, value: s.id }))} />
            </Form.Item>
            <Form.Item label="Name" name="name" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Min Salary" name="min_salary" rules={[{ required: true }]}>
              <InputNumber style={{ width: '100%' }} min={0} />
            </Form.Item>
            <Form.Item label="Max Salary" name="max_salary" rules={[{ required: true }]}>
              <InputNumber style={{ width: '100%' }} min={0} />
            </Form.Item>
          </Form>
        </Modal>
      )}
    </div>
  )
}
