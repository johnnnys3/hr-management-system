import { Alert, Button, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { isSecondFactorRequired } from '../../api/types'

interface LoginFormValues {
  email: string
  password: string
  totpCode?: string
}

export function LoginPage() {
  const { refetch } = useAuth()
  const navigate = useNavigate()
  const [form] = Form.useForm<LoginFormValues>()
  const [needsTotp, setNeedsTotp] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: LoginFormValues) => {
    setError(null)
    setSubmitting(true)
    try {
      const response = await login(values.email, values.password, values.totpCode)
      if (isSecondFactorRequired(response)) {
        setNeedsTotp(true)
        setError('Enter the 6-digit code from your authenticator app.')
        return
      }
      if (response.second_factor_enrollment_required) {
        await refetch()
        navigate('/second-factor/enroll', { replace: true })
        return
      }
      await refetch()
      navigate('/', { replace: true })
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <div style={{ width: 360 }}>
        <div style={{ fontSize: 20, fontWeight: 700, color: '#111', marginBottom: 24 }}>HRMS</div>
        <Typography.Title level={3} style={{ marginTop: 0 }}>
          Log in
        </Typography.Title>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
            <Input autoComplete="username" disabled={needsTotp} />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" disabled={needsTotp} />
          </Form.Item>
          {needsTotp && (
            <Form.Item label="Authenticator code" name="totpCode" rules={[{ required: true }]}>
              <Input autoComplete="one-time-code" maxLength={6} />
            </Form.Item>
          )}
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              {needsTotp ? 'Verify' : 'Log in'}
            </Button>
          </Form.Item>
        </Form>
        <Link to="/password-reset">Forgot your password?</Link>
      </div>
    </div>
  )
}
