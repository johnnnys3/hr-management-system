import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, DatePicker, Form, Input, Modal, Select, Space, Table, Tabs, Tag, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import {
  approveLeaveRequest,
  cancelLeaveRequest,
  correctLeaveRequest,
  createLeaveRequest,
  getLeaveCalendar,
  listLeaveBalances,
  listLeaveRequests,
  listLeaveTypes,
  rejectLeaveRequest,
} from '../../api/leave'
import type { LeaveRequest } from '../../api/types'
import { useAuth } from '../../auth/AuthContext'
import { StatStrip } from '../../components/StatStrip'
import { LEAVE_REQUEST_STATUS_COLORS } from './constants'

export function LeavePage() {
  const { me } = useAuth()
  const isHrOfficer = me?.groups.includes('HR Officer') ?? false
  const isHrAdministrator = me?.groups.includes('HR Administrator') ?? false
  const isHr = isHrOfficer || isHrAdministrator
  const isManager = me?.is_manager ?? false

  const { data: requests = [] } = useQuery({ queryKey: ['leave', 'requests'], queryFn: () => listLeaveRequests() })
  const { data: balances = [] } = useQuery({ queryKey: ['leave', 'balances'], queryFn: listLeaveBalances })
  const [activeKey, setActiveKey] = useState('requests')

  const items = [
    { key: 'requests', label: 'Requests', content: <RequestsTab /> },
    { key: 'balances', label: 'Balances', content: <BalancesTab /> },
    ...(isHr ? [{ key: 'types', label: 'Leave Types', content: <LeaveTypesTab /> }] : []),
    ...(isHr || isManager ? [{ key: 'calendar', label: 'Calendar', content: <CalendarTab /> }] : []),
  ]

  return (
    <div>
      <Typography.Title level={3}>Leave</Typography.Title>
      <Tabs
        activeKey={activeKey}
        onChange={setActiveKey}
        items={items.map(({ key, label }) => ({ key, label }))}
      />
      <StatStrip
        stats={[
          { label: 'Pending', value: requests.filter((r) => r.status === 'pending').length },
          { label: 'Approved', value: requests.filter((r) => r.status === 'approved').length },
          { label: 'Rejected', value: requests.filter((r) => r.status === 'rejected').length },
          {
            label: 'Days Used YTD',
            value: balances.reduce((sum, b) => sum + Number(b.used_days), 0),
          },
        ]}
      />
      {items.find((item) => item.key === activeKey)?.content}
    </div>
  )
}

function useLeaveTypeLookup() {
  const { data: leaveTypes = [] } = useQuery({ queryKey: ['leave', 'types'], queryFn: listLeaveTypes })
  return (id: number) => leaveTypes.find((t) => t.id === id)?.name ?? id
}

function RequestsTab() {
  const { me } = useAuth()
  const isHrOfficer = me?.groups.includes('HR Officer') ?? false
  const isHrAdministrator = me?.groups.includes('HR Administrator') ?? false
  const isHr = isHrOfficer || isHrAdministrator
  const queryClient = useQueryClient()
  const leaveTypeName = useLeaveTypeLookup()
  const { data: leaveTypes = [] } = useQuery({ queryKey: ['leave', 'types'], queryFn: listLeaveTypes })
  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<LeaveRequest | null>(null)
  const [inFlightIds, setInFlightIds] = useState<Set<number>>(new Set())
  const [form] = Form.useForm()
  const [editForm] = Form.useForm()

  const { data: requests = [], isLoading, error } = useQuery({
    queryKey: ['leave', 'requests'],
    queryFn: () => listLeaveRequests(),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['leave', 'requests'] })

  const createMutation = useMutation({
    mutationFn: createLeaveRequest,
    onSuccess: () => {
      message.success('Leave request submitted.')
      setCreateOpen(false)
      form.resetFields()
      invalidate()
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to submit leave request.'),
  })

  const decisionMutation = useMutation({
    mutationFn: ({ id, action }: { id: number; action: 'approve' | 'reject' | 'cancel' }) => {
      if (action === 'approve') return approveLeaveRequest(id)
      if (action === 'reject') return rejectLeaveRequest(id)
      return cancelLeaveRequest(id)
    },
    onMutate: ({ id }) => setInFlightIds((prev) => new Set(prev).add(id)),
    onSettled: (_, __, { id }) =>
      setInFlightIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      }),
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Action failed.'),
  })

  const correctionMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof correctLeaveRequest>[1] }) =>
      correctLeaveRequest(id, data),
    onSuccess: () => {
      message.success('Leave request updated.')
      setEditing(null)
      invalidate()
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to update leave request.'),
  })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load leave requests"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading leave requests.'}
      />
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Request
        </Button>
      </div>
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<LeaveRequest>
          rowKey="id"
          loading={isLoading}
          dataSource={requests}
          pagination={{ pageSize: 25 }}
          columns={[
            { title: 'Leave Type', dataIndex: 'leave_type', render: leaveTypeName },
            { title: 'Start', dataIndex: 'start_date' },
            { title: 'End', dataIndex: 'end_date' },
            { title: 'Reason', dataIndex: 'reason' },
            {
              title: 'Status',
              dataIndex: 'status',
              render: (s: string) => <Tag color={LEAVE_REQUEST_STATUS_COLORS[s]}>{s}</Tag>,
            },
            {
              title: 'Actions',
              render: (_: unknown, record: LeaveRequest) => {
                if (record.status !== 'pending') return null
                if (isHrOfficer) {
                  return (
                    <Space>
                      <Button size="small" onClick={() => { editForm.resetFields(); setEditing(record); }}>
                        Correct
                      </Button>
                      <Button
                        size="small"
                        danger
                        loading={inFlightIds.has(record.id)}
                        onClick={() => decisionMutation.mutate({ id: record.id, action: 'cancel' })}
                      >
                        Cancel
                      </Button>
                    </Space>
                  )
                }
                if (isHr) return null
                return (
                  <Space>
                    <Button
                      size="small"
                      loading={inFlightIds.has(record.id)}
                      onClick={() => decisionMutation.mutate({ id: record.id, action: 'approve' })}
                    >
                      Approve
                    </Button>
                    <Button
                      size="small"
                      danger
                      loading={inFlightIds.has(record.id)}
                      onClick={() => decisionMutation.mutate({ id: record.id, action: 'reject' })}
                    >
                      Reject
                    </Button>
                    <Button
                      size="small"
                      loading={inFlightIds.has(record.id)}
                      onClick={() => decisionMutation.mutate({ id: record.id, action: 'cancel' })}
                    >
                      Cancel
                    </Button>
                  </Space>
                )
              },
            },
          ]}
        />
      </div>

      <Modal
        open={createOpen}
        title="New Leave Request"
        onCancel={() => setCreateOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) =>
            createMutation.mutate({
              leave_type: values.leave_type,
              start_date: values.dates[0].format('YYYY-MM-DD'),
              end_date: values.dates[1].format('YYYY-MM-DD'),
              reason: values.reason,
            })
          }
        >
          <Form.Item name="leave_type" label="Leave Type" rules={[{ required: true }]}>
            <Select options={leaveTypes.map((t) => ({ label: t.name, value: t.id }))} />
          </Form.Item>
          <Form.Item name="dates" label="Dates" rules={[{ required: true }]}>
            <DatePicker.RangePicker />
          </Form.Item>
          <Form.Item name="reason" label="Reason">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={!!editing}
        title="Correct Leave Request"
        onCancel={() => setEditing(null)}
        onOk={() => editForm.submit()}
        confirmLoading={correctionMutation.isPending}
      >
        {editing && (
          <Form
            form={editForm}
            layout="vertical"
            initialValues={{
              leave_type: editing.leave_type,
              dates: [dayjs(editing.start_date), dayjs(editing.end_date)],
              reason: editing.reason ?? undefined,
            }}
            onFinish={(values) =>
              correctionMutation.mutate({
                id: editing.id,
                data: {
                  leave_type: values.leave_type,
                  start_date: values.dates[0].format('YYYY-MM-DD'),
                  end_date: values.dates[1].format('YYYY-MM-DD'),
                  reason: values.reason,
                },
              })
            }
          >
            <Form.Item name="leave_type" label="Leave Type" rules={[{ required: true }]}>
              <Select options={leaveTypes.map((t) => ({ label: t.name, value: t.id }))} />
            </Form.Item>
            <Form.Item name="dates" label="Dates" rules={[{ required: true }]}>
              <DatePicker.RangePicker />
            </Form.Item>
            <Form.Item name="reason" label="Reason">
              <Input.TextArea rows={3} />
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  )
}

function BalancesTab() {
  const leaveTypeName = useLeaveTypeLookup()
  const { data: balances = [], isLoading, error } = useQuery({
    queryKey: ['leave', 'balances'],
    queryFn: listLeaveBalances,
  })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load leave balances"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading leave balances.'}
      />
    )
  }

  return (
    <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={balances}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Leave Type', dataIndex: 'leave_type', render: leaveTypeName },
          { title: 'Period Start', dataIndex: 'period_start' },
          { title: 'Period End', dataIndex: 'period_end' },
          { title: 'Entitled Days', dataIndex: 'entitled_days' },
          { title: 'Used Days', dataIndex: 'used_days' },
        ]}
      />
    </div>
  )
}

function LeaveTypesTab() {
  const { data: leaveTypes = [], isLoading, error } = useQuery({ queryKey: ['leave', 'types'], queryFn: listLeaveTypes })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load leave types"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading leave types.'}
      />
    )
  }

  return (
    <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={leaveTypes}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Requires Approval', dataIndex: 'requires_approval', render: (v: boolean) => (v ? 'Yes' : 'No') },
          { title: 'Active', dataIndex: 'is_active', render: (v: boolean) => (v ? 'Yes' : 'No') },
        ]}
      />
    </div>
  )
}

function CalendarTab() {
  const leaveTypeName = useLeaveTypeLookup()
  const { data: entries = [], isLoading, error } = useQuery({
    queryKey: ['leave', 'calendar'],
    queryFn: getLeaveCalendar,
  })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load the leave calendar"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading the leave calendar.'}
      />
    )
  }

  return (
    <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={entries}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Leave Type', dataIndex: 'leave_type', render: leaveTypeName },
          { title: 'Start', dataIndex: 'start_date' },
          { title: 'End', dataIndex: 'end_date' },
        ]}
      />
    </div>
  )
}
