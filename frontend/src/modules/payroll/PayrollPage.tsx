import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, DatePicker, Form, Modal, Space, Table, Tag, Typography, message } from 'antd'
import type { Dayjs } from 'dayjs'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import {
  approvePayrollRun,
  calculatePayrollRun,
  createPayrollRun,
  finalizePayrollRun,
  getPayrollRun,
  listPayrollRuns,
  submitPayrollRunForApproval,
} from '../../api/payroll'
import type { PayrollRun } from '../../api/types'
import { StatStrip } from '../../components/StatStrip'
import { useAuth } from '../../auth/AuthContext'

const STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  calculated: 'blue',
  pending_approval: 'gold',
  approved: 'cyan',
  finalized: 'green',
  failed: 'red',
}

// Module 16's own client interface. calculate/ and finalize/ are async
// (202, docs/06-api-contracts.md §4.14) — this page polls GET
// .../{id}/ every 2s while a run sits in a transitional status, the same
// pattern already established by reports/useReportExport.ts, rather than
// assuming synchronous completion.
export function PayrollPage() {
  const queryClient = useQueryClient()
  const { me } = useAuth()
  const [createOpen, setCreateOpen] = useState(false)
  const [pollingIds, setPollingIds] = useState<Set<number>>(new Set())

  const { data: runs = [], isLoading } = useQuery({
    queryKey: ['payroll', 'runs'],
    queryFn: listPayrollRuns,
    refetchInterval: pollingIds.size > 0 ? 2000 : false,
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['payroll', 'runs'] })

  // `fromStatus` is the status the run held *before* the async action was
  // requested (e.g. 'draft' before calculate/, 'approved' before
  // finalize/) — the task is done once status has moved away from that,
  // not once it matches any known status, since the starting status can
  // itself be one of the "terminal-looking" ones (finalize/'s own
  // precondition is already 'approved').
  const pollUntilSettled = async (id: number, fromStatus: string) => {
    setPollingIds((prev) => new Set(prev).add(id))
    const poll = async () => {
      const run = await getPayrollRun(id)
      if (run.status !== fromStatus) {
        setPollingIds((prev) => {
          const next = new Set(prev)
          next.delete(id)
          return next
        })
        invalidate()
        return
      }
      setTimeout(poll, 2000)
    }
    void poll()
  }

  const calculateMutation = useMutation({
    mutationFn: ({ id }: { id: number; fromStatus: string }) => calculatePayrollRun(id),
    onSuccess: (_, { id, fromStatus }) => {
      invalidate()
      void pollUntilSettled(id, fromStatus)
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Calculate failed.'),
  })

  const submitMutation = useMutation({
    mutationFn: (id: number) => submitPayrollRunForApproval(id),
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Submit failed.'),
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => approvePayrollRun(id),
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Approve failed.'),
  })

  const finalizeMutation = useMutation({
    mutationFn: ({ id }: { id: number; fromStatus: string }) => finalizePayrollRun(id),
    onSuccess: (_, { id, fromStatus }) => {
      invalidate()
      void pollUntilSettled(id, fromStatus)
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Finalize failed.'),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3}>Payroll</Typography.Title>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Payroll Run
        </Button>
      </div>
      <StatStrip
        stats={[
          { label: 'Total Runs', value: runs.length },
          { label: 'Pending Approval', value: runs.filter((r) => r.status === 'pending_approval').length },
          { label: 'Finalized', value: runs.filter((r) => r.status === 'finalized').length },
        ]}
      />
      <Table<PayrollRun>
        rowKey="id"
        loading={isLoading}
        dataSource={runs}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Period Start', dataIndex: 'period_start' },
          { title: 'Period End', dataIndex: 'period_end' },
          {
            title: 'Status',
            dataIndex: 'status',
            render: (s: string) => <Tag color={STATUS_COLORS[s]}>{s.replace('_', ' ')}</Tag>,
          },
          {
            title: 'Actions',
            render: (_: unknown, record: PayrollRun) => {
              const isInitiator = record.initiated_by === me?.id
              const busy = pollingIds.has(record.id)
              return (
                <Space>
                  {(record.status === 'draft' || record.status === 'failed') && (
                    <Button size="small" loading={busy || calculateMutation.isPending} onClick={() => calculateMutation.mutate({ id: record.id, fromStatus: record.status })}>
                      Calculate
                    </Button>
                  )}
                  {record.status === 'calculated' && (
                    <Button size="small" loading={submitMutation.isPending} onClick={() => submitMutation.mutate(record.id)}>
                      Submit for Approval
                    </Button>
                  )}
                  {record.status === 'pending_approval' && !isInitiator && (
                    <Button size="small" loading={approveMutation.isPending} onClick={() => approveMutation.mutate(record.id)}>
                      Approve
                    </Button>
                  )}
                  {record.status === 'approved' && !isInitiator && (
                    <Button size="small" loading={busy || finalizeMutation.isPending} onClick={() => finalizeMutation.mutate({ id: record.id, fromStatus: record.status })}>
                      Finalize
                    </Button>
                  )}
                </Space>
              )
            },
          },
        ]}
      />
      {createOpen && (
        <NewPayrollRunModal
          onClose={() => setCreateOpen(false)}
          onCreated={() => {
            invalidate()
            setCreateOpen(false)
          }}
        />
      )}
    </div>
  )
}

function NewPayrollRunModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form] = Form.useForm<{ dates: [Dayjs, Dayjs] }>()

  const mutation = useMutation({
    mutationFn: (values: { dates: [Dayjs, Dayjs] }) =>
      createPayrollRun({
        period_start: values.dates[0].format('YYYY-MM-DD'),
        period_end: values.dates[1].format('YYYY-MM-DD'),
      }),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal open title="New Payroll Run" onCancel={onClose} onOk={() => form.submit()} okText="Create" confirmLoading={mutation.isPending}>
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="Period" name="dates" rules={[{ required: true }]}>
          <DatePicker.RangePicker style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  )
}
