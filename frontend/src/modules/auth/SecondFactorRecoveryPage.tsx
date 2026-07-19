import { Alert, Button, Card, InputNumber, Space, Typography } from 'antd'
import { useState } from 'react'
import { decideSecondFactorRecovery, requestSecondFactorRecovery } from '../../api/auth'
import { ApiError } from '../../api/client'

export function SecondFactorRecoveryPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <RequestRecoveryForm />
      <DecideRecoveryForm />
    </Space>
  )
}

function RequestRecoveryForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    setError(null)
    setSubmitting(true)
    try {
      const created = await requestSecondFactorRecovery()
      setResult(`Recovery request #${created.id} submitted.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card title="Lost your second factor?">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Typography.Paragraph type="secondary">
        Request a reset. A deployment-designated approver must approve it before you can re-enroll.
      </Typography.Paragraph>
      <Button type="primary" loading={submitting} onClick={handleSubmit}>
        Request second-factor reset
      </Button>
    </Card>
  )
}

function DecideRecoveryForm() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submittingAction, setSubmittingAction] = useState<'approved' | 'denied' | null>(null)
  const [requestId, setRequestId] = useState<number | null>(null)

  const decide = async (decision: 'approved' | 'denied') => {
    if (requestId == null) return
    setError(null)
    setSubmittingAction(decision)
    try {
      const decided = await decideSecondFactorRecovery(requestId, decision)
      setResult(`Recovery request #${decided.id} ${decided.status}.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmittingAction(null)
    }
  }

  const isDisabled = requestId === null
  const isSubmitting = submittingAction !== null

  return (
    <Card title="Decide a second-factor recovery request">
      {result && <Alert type="success" message={result} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Space>
        <label htmlFor="decide-recovery-id">Request ID</label>
        <InputNumber
          id="decide-recovery-id"
          onChange={(value) => setRequestId(typeof value === 'number' ? value : null)}
        />
        <Button
          loading={submittingAction === 'approved'}
          disabled={isDisabled || isSubmitting}
          onClick={() => decide('approved')}
        >
          Approve
        </Button>
        <Button
          loading={submittingAction === 'denied'}
          disabled={isDisabled || isSubmitting}
          danger
          onClick={() => decide('denied')}
        >
          Deny
        </Button>
      </Space>
    </Card>
  )
}
