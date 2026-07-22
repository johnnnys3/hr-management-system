import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Checkbox, Form, Input, Modal, Table, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { getEmployee } from '../../api/employees'
import {
  createOnboardingTask,
  getOnboardingChecklist,
  listOnboardingTasks,
  updateOnboardingTaskStatus,
} from '../../api/onboarding'
import type { OnboardingTask, OnboardingTaskStatus } from '../../api/types'
import { useAuth } from '../../auth/AuthContext'
import { StatStrip } from '../../components/StatStrip'
import { TASK_STATUS_COLORS } from './constants'

const NEXT_STATUS: Record<OnboardingTaskStatus, { label: string; status: OnboardingTaskStatus }[]> = {
  pending: [
    { label: 'Start', status: 'in_progress' },
    { label: 'Complete', status: 'completed' },
    { label: 'Skip', status: 'skipped' },
  ],
  in_progress: [
    { label: 'Complete', status: 'completed' },
    { label: 'Skip', status: 'skipped' },
  ],
  completed: [],
  skipped: [{ label: 'Reopen', status: 'pending' }],
}

export function OnboardingChecklistPage() {
  const params = useParams<{ id: string }>()
  const checklistId = Number(params.id)
  const { me } = useAuth()
  const isHrOfficer = me?.groups.includes('HR Officer') ?? false
  const [addTaskOpen, setAddTaskOpen] = useState(false)
  const [inFlightTaskIds, setInFlightTaskIds] = useState<Set<number>>(new Set())
  const queryClient = useQueryClient()

  const { data: checklist, isLoading, error } = useQuery({
    queryKey: ['onboarding', 'checklist', checklistId],
    queryFn: () => getOnboardingChecklist(checklistId),
  })
  const { data: employee } = useQuery({
    queryKey: ['employees', 'detail', checklist?.employee],
    queryFn: () => getEmployee(checklist!.employee),
    enabled: !!checklist,
  })
  const { data: tasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['onboarding', 'tasks', checklistId],
    queryFn: () => listOnboardingTasks(checklistId),
  })
  const invalidateTasks = () => queryClient.invalidateQueries({ queryKey: ['onboarding', 'tasks', checklistId] })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: OnboardingTaskStatus }) =>
      updateOnboardingTaskStatus(checklistId, id, status),
    onMutate: ({ id }) => setInFlightTaskIds((prev) => new Set(prev).add(id)),
    onSettled: (_, __, { id }) =>
      setInFlightTaskIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      }),
    onSuccess: invalidateTasks,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Update failed.'),
  })

  if (isLoading) return null
  if (error || !checklist) {
    return (
      <Alert
        type="error"
        message="Failed to load onboarding checklist"
        description={error instanceof ApiError ? error.message : 'Checklist not found.'}
      />
    )
  }

  return (
    <div>
      <Typography.Title level={3}>
        Onboarding — {employee ? `${employee.first_name} ${employee.last_name}` : `Employee #${checklist.employee}`}
      </Typography.Title>
      <Typography.Text type="secondary">
        Started {new Date(checklist.started_at).toLocaleString()}
        {checklist.completed_at && ` · Completed ${new Date(checklist.completed_at).toLocaleString()}`}
      </Typography.Text>
      <div style={{ marginTop: 24 }}>
        <StatStrip
          stats={[
            { label: 'Completed', value: tasks.filter((t) => t.status === 'completed').length },
            { label: 'In Progress', value: tasks.filter((t) => t.status === 'in_progress').length },
            { label: 'Pending', value: tasks.filter((t) => t.status === 'pending').length },
          ]}
        />
      </div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Typography.Title level={5} style={{ margin: 0 }}>
          Tasks
        </Typography.Title>
        {isHrOfficer && (
          <Button type="primary" onClick={() => setAddTaskOpen(true)}>
            Add Task
          </Button>
        )}
      </div>
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<OnboardingTask>
          rowKey="id"
          loading={tasksLoading}
          dataSource={tasks}
          pagination={false}
          columns={[
            { title: 'Name', dataIndex: 'name' },
            { title: 'Required', dataIndex: 'is_required', render: (v: boolean) => (v ? 'Yes' : 'No') },
            {
              title: 'Status',
              dataIndex: 'status',
              render: (s: OnboardingTaskStatus) => <Tag color={TASK_STATUS_COLORS[s]}>{s.replace('_', ' ')}</Tag>,
            },
            ...(isHrOfficer
              ? [
                  {
                    title: 'Actions',
                    key: 'actions',
                    render: (_: unknown, task: OnboardingTask) => (
                      <>
                        {NEXT_STATUS[task.status].map(({ label, status }) => (
                          <Button
                            key={status}
                            size="small"
                            style={{ marginRight: 8 }}
                            loading={inFlightTaskIds.has(task.id)}
                            onClick={() => statusMutation.mutate({ id: task.id, status })}
                          >
                            {label}
                          </Button>
                        ))}
                      </>
                    ),
                  },
                ]
              : []),
          ]}
        />
      </div>
      {addTaskOpen && (
        <AddTaskModal
          checklistId={checklistId}
          onClose={() => setAddTaskOpen(false)}
          onCreated={() => {
            invalidateTasks()
            setAddTaskOpen(false)
          }}
        />
      )}
    </div>
  )
}

interface TaskFormValues {
  name: string
  is_required: boolean
}

function AddTaskModal({
  checklistId,
  onClose,
  onCreated,
}: {
  checklistId: number
  onClose: () => void
  onCreated: () => void
}) {
  const [form] = Form.useForm<TaskFormValues>()

  const mutation = useMutation({
    mutationFn: (values: TaskFormValues) => createOnboardingTask(checklistId, values),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="Add Task"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Add"
      confirmLoading={mutation.isPending}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ is_required: true }}
        onFinish={(values) => mutation.mutate(values)}
      >
        <Form.Item label="Name" name="name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="is_required" valuePropName="checked">
          <Checkbox>Required</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  )
}
