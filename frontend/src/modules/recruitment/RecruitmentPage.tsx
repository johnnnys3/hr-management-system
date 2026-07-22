import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Form, Input, Modal, Select, Space, Table, Tabs, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { StatStrip } from '../../components/StatStrip'
import { useDepartments, useJobTitles } from '../departments/hooks'
import {
  approveJobRequisition,
  createCandidate,
  createJobPosting,
  createJobRequisition,
  listCandidates,
  listJobPostings,
  listJobRequisitions,
  publishJobPosting,
  rejectJobRequisition,
} from '../../api/recruitment'
import type { Candidate, JobPosting, JobRequisition } from '../../api/types'

const REQUISITION_STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  pending_approval: 'gold',
  approved: 'green',
  rejected: 'red',
  closed: 'default',
}

export function RecruitmentPage() {
  const { me } = useAuth()
  const isRecruiter = me?.groups.includes('Recruiter') ?? false
  const isHrAdministrator = me?.groups.includes('HR Administrator') ?? false
  const isHrOfficer = me?.groups.includes('HR Officer') ?? false

  const { data: requisitions = [] } = useQuery({
    queryKey: ['recruitment', 'requisitions', 'all'],
    queryFn: () => listJobRequisitions(),
    enabled: isRecruiter || isHrAdministrator,
  })
  const { data: candidates = [] } = useQuery({
    queryKey: ['recruitment', 'candidates', undefined],
    queryFn: () => listCandidates(),
    enabled: isRecruiter || isHrOfficer,
  })

  const items = [
    ...(isRecruiter || isHrAdministrator
      ? [{ key: 'requisitions', label: 'Requisitions', content: <RequisitionsTab /> }]
      : []),
    ...(isRecruiter ? [{ key: 'postings', label: 'Postings', content: <PostingsTab /> }] : []),
    ...(isRecruiter || isHrOfficer
      ? [{ key: 'candidates', label: 'Candidates', content: <CandidatesTab /> }]
      : []),
  ]
  const [activeKey, setActiveKey] = useState(items[0]?.key)

  return (
    <div>
      <Typography.Title level={3}>Recruitment</Typography.Title>
      <Tabs activeKey={activeKey} onChange={setActiveKey} items={items.map(({ key, label }) => ({ key, label }))} />
      <StatStrip
        stats={[
          {
            label: 'Open Requisitions',
            value: requisitions.filter((r) => r.status !== 'closed' && r.status !== 'rejected').length,
          },
          { label: 'Candidates', value: candidates.length },
        ]}
      />
      {items.find((item) => item.key === activeKey)?.content}
    </div>
  )
}

function RequisitionsTab() {
  const { me } = useAuth()
  const queryClient = useQueryClient()
  const isRecruiter = me?.groups.includes('Recruiter') ?? false
  const isHrAdministrator = me?.groups.includes('HR Administrator') ?? false
  const [createOpen, setCreateOpen] = useState(false)
  const [inFlightRequisitionIds, setInFlightRequisitionIds] = useState<Set<number>>(new Set())

  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()
  const { data: requisitions = [], isLoading } = useQuery({
    queryKey: ['recruitment', 'requisitions', 'all'],
    queryFn: () => listJobRequisitions(),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['recruitment', 'requisitions'] })

  const decisionMutation = useMutation({
    mutationFn: ({ id, decision }: { id: number; decision: 'approve' | 'reject' }) =>
      decision === 'approve' ? approveJobRequisition(id) : rejectJobRequisition(id),
    onMutate: ({ id }) => {
      setInFlightRequisitionIds((prev) => new Set(prev).add(id))
    },
    onSettled: (_, __, { id }) => {
      setInFlightRequisitionIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    },
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Action failed.'),
  })

  const departmentName = (id: number) => departments.find((d) => d.id === id)?.name ?? id
  const jobTitleName = (id: number) => jobTitles.find((j) => j.id === id)?.name ?? id

  return (
    <div>
      {isRecruiter && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
          <Button type="primary" onClick={() => setCreateOpen(true)}>
            New Requisition
          </Button>
        </div>
      )}
      <Table<JobRequisition>
        rowKey="id"
        loading={isLoading}
        dataSource={requisitions}
        pagination={{ pageSize: 25 }}
        columns={[
          { title: 'Department', dataIndex: 'department', render: departmentName },
          { title: 'Job Title', dataIndex: 'job_title', render: jobTitleName },
          {
            title: 'Status',
            dataIndex: 'status',
            render: (s: string) => <Tag color={REQUISITION_STATUS_COLORS[s]}>{s.replace('_', ' ')}</Tag>,
          },
          ...(isHrAdministrator
            ? [
                {
                  title: 'Actions',
                  render: (_: unknown, record: JobRequisition) =>
                    record.status === 'draft' || record.status === 'pending_approval' ? (
                      <Space>
                        <Button
                          size="small"
                          loading={inFlightRequisitionIds.has(record.id)}
                          onClick={() => decisionMutation.mutate({ id: record.id, decision: 'approve' })}
                        >
                          Approve
                        </Button>
                        <Button
                          size="small"
                          danger
                          loading={inFlightRequisitionIds.has(record.id)}
                          onClick={() => decisionMutation.mutate({ id: record.id, decision: 'reject' })}
                        >
                          Reject
                        </Button>
                      </Space>
                    ) : null,
                },
              ]
            : []),
        ]}
      />
      {createOpen && (
        <NewRequisitionModal
          departments={departments}
          jobTitles={jobTitles}
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

function NewRequisitionModal({
  departments,
  jobTitles,
  onClose,
  onCreated,
}: {
  departments: { id: number; name: string }[]
  jobTitles: { id: number; name: string }[]
  onClose: () => void
  onCreated: () => void
}) {
  const [form] = Form.useForm<{ department: number; job_title: number }>()

  const mutation = useMutation({
    mutationFn: (values: { department: number; job_title: number }) => createJobRequisition(values),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="New Requisition"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Create"
      confirmLoading={mutation.isPending}
    >
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
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

function PostingsTab() {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [inFlightPostingIds, setInFlightPostingIds] = useState<Set<number>>(new Set())
  const { data: postings = [], isLoading } = useQuery({
    queryKey: ['recruitment', 'postings'],
    queryFn: () => listJobPostings(),
  })
  const { data: requisitions = [] } = useQuery({
    queryKey: ['recruitment', 'requisitions', 'approved'],
    queryFn: () => listJobRequisitions('approved'),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['recruitment', 'postings'] })

  const publishMutation = useMutation({
    mutationFn: (id: number) => publishJobPosting(id),
    onMutate: (id) => {
      setInFlightPostingIds((prev) => new Set(prev).add(id))
    },
    onSettled: (_, __, id) => {
      setInFlightPostingIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    },
    onSuccess: invalidate,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Publish failed.'),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          New Posting
        </Button>
      </div>
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<JobPosting>
          rowKey="id"
          loading={isLoading}
          dataSource={postings}
          pagination={{ pageSize: 25 }}
          columns={[
            { title: 'Title', dataIndex: 'title' },
            { title: 'Channel', dataIndex: 'channel' },
            {
              title: 'Status',
              render: (_: unknown, record: JobPosting) =>
                record.published_at ? <Tag color="green">Published</Tag> : <Tag>Draft</Tag>,
            },
            {
              title: 'Actions',
              render: (_: unknown, record: JobPosting) =>
                !record.published_at ? (
                  <Button
                    size="small"
                    loading={inFlightPostingIds.has(record.id)}
                    onClick={() => publishMutation.mutate(record.id)}
                  >
                    Publish
                  </Button>
                ) : null,
            },
          ]}
        />
      </div>
      {createOpen && (
        <NewPostingModal
          requisitions={requisitions}
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

interface PostingFormValues {
  requisition: number
  title: string
  description: string
  channel: 'internal' | 'external'
}

function NewPostingModal({
  requisitions,
  onClose,
  onCreated,
}: {
  requisitions: JobRequisition[]
  onClose: () => void
  onCreated: () => void
}) {
  const [form] = Form.useForm<PostingFormValues>()

  const mutation = useMutation({
    mutationFn: (values: PostingFormValues) => createJobPosting(values),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="New Posting"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Create"
      confirmLoading={mutation.isPending}
    >
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="Approved Requisition" name="requisition" rules={[{ required: true }]}>
          <Select options={requisitions.map((r) => ({ label: `Requisition #${r.id}`, value: r.id }))} />
        </Form.Item>
        <Form.Item label="Title" name="title" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Description" name="description" rules={[{ required: true }]}>
          <Input.TextArea rows={4} />
        </Form.Item>
        <Form.Item label="Channel" name="channel" rules={[{ required: true }]}>
          <Select
            options={[
              { label: 'Internal', value: 'internal' },
              { label: 'External', value: 'external' },
            ]}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

function CandidatesTab() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { me } = useAuth()
  const isRecruiter = me?.groups.includes('Recruiter') ?? false
  const [createOpen, setCreateOpen] = useState(false)
  const [search, setSearch] = useState('')
  const { data: candidates = [], isLoading } = useQuery({
    queryKey: ['recruitment', 'candidates', search],
    queryFn: () => listCandidates(search || undefined),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Input.Search
          placeholder="Search by email"
          allowClear
          style={{ width: 260 }}
          onSearch={setSearch}
        />
        {isRecruiter && (
          <Button type="primary" onClick={() => setCreateOpen(true)}>
            New Candidate
          </Button>
        )}
      </div>
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<Candidate>
          rowKey="id"
          loading={isLoading}
          dataSource={candidates}
          pagination={{ pageSize: 25 }}
          onRow={(record) => ({ onClick: () => navigate(`/recruitment/candidates/${record.id}`), style: { cursor: 'pointer' } })}
          columns={[
            { title: 'First Name', dataIndex: 'first_name' },
            { title: 'Last Name', dataIndex: 'last_name' },
            { title: 'Email', dataIndex: 'email' },
            { title: 'Phone', dataIndex: 'phone', render: (p: string | null) => p ?? '—' },
          ]}
        />
      </div>
      {createOpen && (
        <NewCandidateModal
          onClose={() => setCreateOpen(false)}
          onCreated={(candidate) => {
            queryClient.invalidateQueries({ queryKey: ['recruitment', 'candidates'] })
            setCreateOpen(false)
            navigate(`/recruitment/candidates/${candidate.id}`)
          }}
        />
      )}
    </div>
  )
}

interface CandidateFormValues {
  first_name: string
  last_name: string
  email: string
  phone?: string
}

function NewCandidateModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (candidate: Candidate) => void
}) {
  const [form] = Form.useForm<CandidateFormValues>()
  const [resume, setResume] = useState<File | undefined>()

  const mutation = useMutation({
    mutationFn: (values: CandidateFormValues) => createCandidate({ ...values, resume }),
    onSuccess: onCreated,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Create failed.'),
  })

  return (
    <Modal
      open
      title="New Candidate"
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Create"
      confirmLoading={mutation.isPending}
    >
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="First Name" name="first_name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Last Name" name="last_name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Phone" name="phone">
          <Input />
        </Form.Item>
        <Form.Item label="Resume">
          <input type="file" onChange={(e) => setResume(e.target.files?.[0])} />
        </Form.Item>
      </Form>
    </Modal>
  )
}
