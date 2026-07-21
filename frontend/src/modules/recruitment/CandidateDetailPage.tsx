import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, DatePicker, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { listEmployees } from '../../api/employees'
import {
  createCandidateApplication,
  createInterview,
  createOffer,
  decideOffer,
  getCandidate,
  listCandidateApplications,
  listInterviews,
  listJobPostings,
  listOffers,
} from '../../api/recruitment'
import type { CandidateApplication, Interview } from '../../api/types'

const STAGE_COLORS: Record<string, string> = {
  applied: 'default',
  screening: 'gold',
  interview: 'blue',
  offer: 'purple',
  hired: 'green',
  rejected: 'red',
}

export function CandidateDetailPage() {
  const params = useParams<{ id: string }>()
  const candidateId = Number(params.id)
  const [applyOpen, setApplyOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: candidate, isLoading, error } = useQuery({
    queryKey: ['recruitment', 'candidate', candidateId],
    queryFn: () => getCandidate(candidateId),
  })
  const { data: applications = [] } = useQuery({
    queryKey: ['recruitment', 'applications', candidateId],
    queryFn: () => listCandidateApplications(candidateId),
  })
  const { data: postings = [] } = useQuery({ queryKey: ['recruitment', 'postings'], queryFn: () => listJobPostings() })

  if (isLoading) return null
  if (error || !candidate) {
    return (
      <Alert
        type="error"
        message="Failed to load candidate"
        description={error instanceof ApiError ? error.message : 'Candidate not found.'}
      />
    )
  }

  return (
    <div>
      <Typography.Title level={3}>
        {candidate.first_name} {candidate.last_name}
      </Typography.Title>
      <Typography.Text type="secondary">{candidate.email}</Typography.Text>
      <div style={{ marginTop: 24, marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Typography.Title level={5} style={{ margin: 0 }}>
          Applications
        </Typography.Title>
        <Button type="primary" onClick={() => setApplyOpen(true)}>
          New Application
        </Button>
      </div>
      <Table<CandidateApplication>
        rowKey="id"
        dataSource={applications}
        pagination={false}
        columns={[
          {
            title: 'Posting',
            dataIndex: 'posting',
            render: (id: number) => postings.find((p) => p.id === id)?.title ?? id,
          },
          {
            title: 'Stage',
            dataIndex: 'stage',
            render: (s: string) => <Tag color={STAGE_COLORS[s]}>{s}</Tag>,
          },
        ]}
        expandable={{ expandedRowRender: (application) => <ApplicationDetail application={application} /> }}
      />
      {applyOpen && (
        <NewApplicationModal
          candidateId={candidateId}
          postings={postings}
          onClose={() => setApplyOpen(false)}
          onCreated={() => {
            queryClient.invalidateQueries({ queryKey: ['recruitment', 'applications', candidateId] })
            setApplyOpen(false)
          }}
        />
      )}
    </div>
  )
}

function NewApplicationModal({
  candidateId,
  postings,
  onClose,
  onCreated,
}: {
  candidateId: number
  postings: { id: number; title: string }[]
  onClose: () => void
  onCreated: () => void
}) {
  const [postingId, setPostingId] = useState<number | undefined>()

  const mutation = useMutation({
    mutationFn: () => createCandidateApplication(candidateId, postingId as number),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="New Application"
      onCancel={onClose}
      onOk={() => mutation.mutate()}
      okText="Create"
      okButtonProps={{ disabled: postingId === undefined }}
      confirmLoading={mutation.isPending}
    >
      <Select
        style={{ width: '100%' }}
        placeholder="Select a posting"
        value={postingId}
        onChange={setPostingId}
        options={postings.map((p) => ({ label: p.title, value: p.id }))}
      />
    </Modal>
  )
}

function ApplicationDetail({ application }: { application: CandidateApplication }) {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <InterviewsPanel applicationId={application.id} />
      <OfferPanel applicationId={application.id} />
    </Space>
  )
}

function InterviewsPanel({ applicationId }: { applicationId: number }) {
  const queryClient = useQueryClient()
  const [scheduleOpen, setScheduleOpen] = useState(false)
  const { data: interviews = [], isLoading } = useQuery({
    queryKey: ['recruitment', 'interviews', applicationId],
    queryFn: () => listInterviews(applicationId),
  })
  const { data: employees = [] } = useQuery({ queryKey: ['employees', 'list', {}], queryFn: () => listEmployees() })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <Typography.Text strong>Interviews</Typography.Text>
        <Button size="small" onClick={() => setScheduleOpen(true)}>
          Schedule Interview
        </Button>
      </div>
      <Table<Interview>
        rowKey="id"
        size="small"
        loading={isLoading}
        dataSource={interviews}
        pagination={false}
        columns={[
          {
            title: 'Interviewer',
            dataIndex: 'interviewer_employee',
            render: (id: number | null) => {
              const employee = employees.find((e) => e.id === id)
              return employee ? `${employee.first_name} ${employee.last_name}` : '—'
            },
          },
          { title: 'Scheduled At', dataIndex: 'scheduled_at' },
          { title: 'Status', dataIndex: 'status' },
        ]}
      />
      {scheduleOpen && (
        <ScheduleInterviewModal
          applicationId={applicationId}
          employees={employees}
          onClose={() => setScheduleOpen(false)}
          onCreated={() => {
            queryClient.invalidateQueries({ queryKey: ['recruitment', 'interviews', applicationId] })
            setScheduleOpen(false)
          }}
        />
      )}
    </div>
  )
}

interface ScheduleFormValues {
  interviewer_employee?: number
  scheduled_at: dayjs.Dayjs
}

function ScheduleInterviewModal({
  applicationId,
  employees,
  onClose,
  onCreated,
}: {
  applicationId: number
  employees: { id: number; first_name: string; last_name: string }[]
  onClose: () => void
  onCreated: () => void
}) {
  const [form] = Form.useForm<ScheduleFormValues>()

  const mutation = useMutation({
    mutationFn: (values: ScheduleFormValues) =>
      createInterview(applicationId, {
        interviewer_employee: values.interviewer_employee,
        scheduled_at: values.scheduled_at.toISOString(),
      }),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Schedule failed.'),
  })

  return (
    <Modal
      open
      title="Schedule Interview"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Schedule"
      confirmLoading={mutation.isPending}
    >
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="Interviewer" name="interviewer_employee">
          <Select
            allowClear
            options={employees.map((e) => ({ label: `${e.first_name} ${e.last_name}`, value: e.id }))}
          />
        </Form.Item>
        <Form.Item label="Scheduled At" name="scheduled_at" rules={[{ required: true }]}>
          <DatePicker showTime style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  )
}

function OfferPanel({ applicationId }: { applicationId: number }) {
  const queryClient = useQueryClient()
  const [issueOpen, setIssueOpen] = useState(false)
  const [inFlightOfferIds, setInFlightOfferIds] = useState<Set<number>>(new Set())
  const { data: offers = [], isLoading } = useQuery({
    queryKey: ['recruitment', 'offers', applicationId],
    queryFn: () => listOffers(applicationId),
  })
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['recruitment', 'offers', applicationId] })

  const decisionMutation = useMutation({
    mutationFn: ({ id, decision }: { id: number; decision: 'accepted' | 'rejected' | 'withdrawn' }) =>
      decideOffer(id, decision),
    onMutate: ({ id }) => {
      setInFlightOfferIds((prev) => new Set(prev).add(id))
    },
    onSettled: (_, __, { id }) => {
      setInFlightOfferIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    },
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Action failed.'),
  })

  const currentOffer = offers[0]
  const canIssueOffer = !isLoading && (!currentOffer || currentOffer.status === 'rejected' || currentOffer.status === 'withdrawn')

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <Typography.Text strong>Offer</Typography.Text>
        {canIssueOffer && (
          <Button size="small" onClick={() => setIssueOpen(true)}>
            Issue Offer
          </Button>
        )}
      </div>
      {currentOffer && (
        <Space>
          <Typography.Text>Salary: {currentOffer.offered_salary}</Typography.Text>
          <Tag>{currentOffer.status}</Tag>
          {currentOffer.status === 'pending' && (
            <Space>
              <Button
                size="small"
                loading={inFlightOfferIds.has(currentOffer.id)}
                onClick={() => decisionMutation.mutate({ id: currentOffer.id, decision: 'accepted' })}
              >
                Accept
              </Button>
              <Button
                size="small"
                danger
                loading={inFlightOfferIds.has(currentOffer.id)}
                onClick={() => decisionMutation.mutate({ id: currentOffer.id, decision: 'rejected' })}
              >
                Reject
              </Button>
              <Button size="small" loading={inFlightOfferIds.has(currentOffer.id)} onClick={() => decisionMutation.mutate({ id: currentOffer.id, decision: 'withdrawn' })}>
                Withdraw
              </Button>
            </Space>
          )}
        </Space>
      )}
      {issueOpen && (
        <IssueOfferModal
          applicationId={applicationId}
          onClose={() => setIssueOpen(false)}
          onCreated={() => {
            invalidate()
            setIssueOpen(false)
          }}
        />
      )}
    </div>
  )
}

function IssueOfferModal({
  applicationId,
  onClose,
  onCreated,
}: {
  applicationId: number
  onClose: () => void
  onCreated: () => void
}) {
  const [offeredSalary, setOfferedSalary] = useState('')

  const mutation = useMutation({
    mutationFn: () => createOffer(applicationId, offeredSalary),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Issue failed.'),
  })

  return (
    <Modal
      open
      title="Issue Offer"
      onCancel={onClose}
      onOk={() => mutation.mutate()}
      okText="Issue"
      okButtonProps={{ disabled: !offeredSalary }}
      confirmLoading={mutation.isPending}
    >
      <Input
        placeholder="Offered salary"
        value={offeredSalary}
        onChange={(e) => setOfferedSalary(e.target.value)}
      />
    </Modal>
  )
}
