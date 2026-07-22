import { Alert, Button, Form, Input, Typography } from 'antd'
import { useState, type ReactNode } from 'react'
import { useSearchParams } from 'react-router-dom'
import { confirmPasswordReset, requestPasswordReset } from '../../api/auth'
import { ApiError } from '../../api/client'

function AuthCard({ children }: { children: ReactNode }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <div style={{ width: 360 }}>
        <div style={{ fontSize: 20, fontWeight: 700, color: '#111', marginBottom: 24 }}>HRMS</div>
        {children}
      </div>
    </div>
  )
}

export function PasswordResetPage() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid')
  const token = searchParams.get('token')

  if (uid && token) {
    return <ConfirmForm uid={uid} token={token} />
  }
  return <RequestForm />
}

function RequestForm() {
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { email: string }) => {
    setError(null)
    setSubmitting(true)
    try {
      await requestPasswordReset(values.email)
      setDone(true)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthCard>
      <Typography.Title level={3} style={{ marginTop: 0 }}>
        Reset your password
      </Typography.Title>
      {done ? (
        <Alert type="info" message="If an account exists for that email, a reset link has been sent." />
      ) : (
        <>
          {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
          <Form layout="vertical" onFinish={handleSubmit}>
            <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
              <Input autoComplete="username" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={submitting} block>
                Send reset link
              </Button>
            </Form.Item>
          </Form>
        </>
      )}
    </AuthCard>
  )
}

function ConfirmForm({ uid, token }: { uid: string; token: string }) {
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: { password: string }) => {
    setError(null)
    setSubmitting(true)
    try {
      await confirmPasswordReset(uid, token, values.password)
      setDone(true)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthCard>
      <Typography.Title level={3} style={{ marginTop: 0 }}>
        Set a new password
      </Typography.Title>
      {done ? (
        <Alert type="success" message="Your password has been reset. You may now log in." />
      ) : (
        <>
          {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
          <Form layout="vertical" onFinish={handleSubmit}>
            <Form.Item label="New password" name="password" rules={[{ required: true }]}>
              <Input.Password autoComplete="new-password" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={submitting} block>
                Set new password
              </Button>
            </Form.Item>
          </Form>
        </>
      )}
    </AuthCard>
  )
}
