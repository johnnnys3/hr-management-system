import { Alert, Button, Card, Typography } from 'antd'
import { useState } from 'react'
import { enrollSecondFactor } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'

export function SecondFactorEnrollPage() {
  const { refetch } = useAuth()
  const [provisioningUri, setProvisioningUri] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleEnroll = async () => {
    setError(null)
    setSubmitting(true)
    try {
      const { provisioning_uri } = await enrollSecondFactor()
      setProvisioningUri(provisioning_uri)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 96 }}>
      <Card style={{ width: 480 }}>
        <Typography.Title level={3}>Set up two-factor authentication</Typography.Title>
        <Typography.Paragraph type="secondary">
          Your role requires two-factor authentication. Set it up now to continue.
        </Typography.Paragraph>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        {provisioningUri ? (
          <>
            <Typography.Paragraph>
              Add this to your authenticator app (Google Authenticator, Authy, etc.) — most apps accept manual
              entry of the key below if you can't scan a code here:
            </Typography.Paragraph>
            <Typography.Text code copyable style={{ wordBreak: 'break-all' }}>
              {provisioningUri}
            </Typography.Text>
            <div style={{ marginTop: 24 }}>
              <Button type="primary" onClick={() => refetch()} block>
                I've added it — continue
              </Button>
            </div>
          </>
        ) : (
          <Button type="primary" loading={submitting} onClick={handleEnroll} block>
            Start setup
          </Button>
        )}
      </Card>
    </div>
  )
}
