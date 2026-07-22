import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Form, Input, Modal, Switch, Table, Tabs, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import {
  createDepartment,
  createJobTitle,
  listDepartments,
  listJobTitles,
  updateDepartment,
  updateJobTitle,
} from '../../api/departments'
import { ApiError } from '../../api/client'
import type { Department, JobTitle } from '../../api/types'
import { StatStrip } from '../../components/StatStrip'

type NamedRecord = Department | JobTitle
type FormValues = { name: string; is_active: boolean }

export function DepartmentsPage() {
  const { data: departments = [] } = useQuery({ queryKey: ['departments', 'departments'], queryFn: listDepartments })
  const [activeKey, setActiveKey] = useState('departments')

  return (
    <div>
      <Typography.Title level={3}>Departments</Typography.Title>
      <Tabs
        activeKey={activeKey}
        onChange={setActiveKey}
        items={[
          { key: 'departments', label: 'Departments' },
          { key: 'job-titles', label: 'Job Titles' },
        ]}
      />
      <StatStrip
        stats={[
          { label: 'Total Departments', value: departments.length },
          { label: 'Active', value: departments.filter((d) => d.is_active).length },
          { label: 'Retired', value: departments.filter((d) => !d.is_active).length },
        ]}
      />
      {activeKey === 'departments' ? (
        <ConfigTable
          title="Department"
          queryKey={['departments', 'departments']}
          listFn={listDepartments}
          createFn={createDepartment}
          updateFn={updateDepartment}
        />
      ) : (
        <ConfigTable
          title="Job Title"
          queryKey={['departments', 'job-titles']}
          listFn={listJobTitles}
          createFn={createJobTitle}
          updateFn={updateJobTitle}
        />
      )}
    </div>
  )
}

function ConfigTable({
  title,
  queryKey,
  listFn,
  createFn,
  updateFn,
}: {
  title: string
  queryKey: string[]
  listFn: () => Promise<NamedRecord[]>
  createFn: (data: FormValues) => Promise<NamedRecord>
  updateFn: (id: number, data: Partial<FormValues>) => Promise<NamedRecord>
}) {
  const queryClient = useQueryClient()
  const { data: records = [], isLoading, error } = useQuery({ queryKey, queryFn: listFn })
  const [modalRecord, setModalRecord] = useState<NamedRecord | 'new' | null>(null)

  const invalidate = () => queryClient.invalidateQueries({ queryKey })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load data"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading the list.'}
      />
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setModalRecord('new')}>
          New {title}
        </Button>
      </div>
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<NamedRecord>
          rowKey="id"
          loading={isLoading}
          dataSource={records}
          pagination={{ pageSize: 25 }}
          onRow={(record) => ({ onClick: () => setModalRecord(record), style: { cursor: 'pointer' } })}
          columns={[
            { title: 'Name', dataIndex: 'name' },
            {
              title: 'Status',
              dataIndex: 'is_active',
              render: (active: boolean) => (active ? <Tag color="green">Active</Tag> : <Tag>Retired</Tag>),
            },
          ]}
        />
      </div>
      {modalRecord && (
        <RecordFormModal
          title={title}
          record={modalRecord === 'new' ? null : modalRecord}
          createFn={createFn}
          updateFn={updateFn}
          onClose={() => setModalRecord(null)}
          onSaved={() => {
            invalidate()
            setModalRecord(null)
          }}
        />
      )}
    </div>
  )
}

function RecordFormModal({
  title,
  record,
  createFn,
  updateFn,
  onClose,
  onSaved,
}: {
  title: string
  record: NamedRecord | null
  createFn: (data: FormValues) => Promise<NamedRecord>
  updateFn: (id: number, data: Partial<FormValues>) => Promise<NamedRecord>
  onClose: () => void
  onSaved: () => void
}) {
  const [form] = Form.useForm<FormValues>()

  const mutation = useMutation({
    mutationFn: (values: FormValues) => {
      if (record) {
        // Build PATCH payload from only changed fields
        const changes: Partial<FormValues> = {}
        if (values.name !== record.name) {
          changes.name = values.name
        }
        if (values.is_active !== record.is_active) {
          changes.is_active = values.is_active
        }
        return updateFn(record.id, changes)
      }
      return createFn(values)
    },
    onSuccess: onSaved,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
  })

  return (
    <Modal
      open
      title={record ? `Edit ${title}` : `New ${title}`}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText={record ? 'Save' : 'Create'}
      confirmLoading={mutation.isPending}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ name: record?.name, is_active: record?.is_active ?? true }}
        onFinish={(values) => mutation.mutate(values)}
      >
        <Form.Item label="Name" name="name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Active" name="is_active" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  )
}
