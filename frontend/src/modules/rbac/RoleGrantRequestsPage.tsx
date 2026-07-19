import { Alert, Button, Card, Form, InputNumber, Space, Typography } from 'antd'
import { useState } from 'react'
import { createRoleGrantRequest, decideRoleGrantRequest } from '../../api/rbac'
import { ApiError } from '../../api/client'

export function RoleGrantRequestsPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Typography.Paragraph type="secondary">
        There is currently no list view for pending requests (backend gap — tracked separately). Use these
        forms with a request ID from a notification.
      </Typography.Paragraph>
      <RaiseRequestForm />
      <DecideRequestForm />
    </Space>
  )
}

function RaiseRequestForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { subjectUserId: number; roleId: number }) => {
    setError(null)
    setSubmitting(true)
    try {
      const created = await createRoleGrantRequest(values.subjectUserId, values.roleId)
      setResult(`Request #${created.id} submitted.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Raise a role grant request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Form layout="inline" onFinish={handleSubmit}>
        <Form.Item label="Subject user ID" name="subjectUserId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item label="Role ID" name="roleId" rules={[{ required: true }]}>
          <InputNumber />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting}>
            Submit request
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

function DecideRequestForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [requestId, setRequestId] = useState<number | null>(null)

  const decide = async (decision: 'approved' | 'refused') => {
    if (requestId == null) return
    setError(null)
    setSubmitting(true)
    try {
      const decided = await decideRoleGrantRequest(requestId, decision)
      setResult(`Request #${decided.id} ${decided.status}.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Decide a role grant request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Space>
        <label htmlFor="decide-request-id">Request ID</label>
        <InputNumber
          id="decide-request-id"
          onChange={(value) => setRequestId(typeof value === 'number' ? value : null)}
        />
        <Button loading={submitting} onClick={() => decide('approved')}>
          Approve
        </Button>
        <Button loading={submitting} danger onClick={() => decide('refused')}>
          Refuse
        </Button>
      </Space>
    </Card>
  )
}
