import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { isSecondFactorRequired } from '../../api/types'

interface LoginFormValues {
  email: string
  password: string
}

export function LoginPage() {
  const { refetch } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (values: LoginFormValues) => {
    setError(null)
    setSubmitting(true)
    try {
      const response = await login(values.email, values.password)
      if (isSecondFactorRequired(response)) {
        setError("Second-factor verification isn't available in this client yet — contact your administrator.")
        return
      }
      if (response.second_factor_enrollment_required) {
        setError("Second-factor setup isn't available in this client yet — contact your administrator.")
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
      <Card style={{ width: 360 }}>
        <Typography.Title level={3}>Log in</Typography.Title>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              Log in
            </Button>
          </Form.Item>
        </Form>
        <Link to="/password-reset">Forgot your password?</Link>
      </Card>
    </div>
  )
}
