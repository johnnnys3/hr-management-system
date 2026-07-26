import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Form, Input, Switch, Typography, message } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import {
  confirmPhoneVerification,
  getNotificationPreference,
  requestPhoneVerification,
  updateNotificationPreference,
} from '../../api/notificationPreferences'
import { useAuth } from '../../auth/AuthContext'

export function NotificationPreferencesTab() {
  const queryClient = useQueryClient()
  const { me } = useAuth()
  const [codeSent, setCodeSent] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [code, setCode] = useState('')

  const { data: preference, error } = useQuery({
    queryKey: ['notification-preferences', 'me'],
    queryFn: getNotificationPreference,
  })

  const updateMutation = useMutation({
    mutationFn: updateNotificationPreference,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notification-preferences', 'me'] }),
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to update preference.'),
  })

  const requestCodeMutation = useMutation({
    mutationFn: requestPhoneVerification,
    onSuccess: () => setCodeSent(true),
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to send code.'),
  })

  const confirmCodeMutation = useMutation({
    mutationFn: confirmPhoneVerification,
    onSuccess: () => {
      message.success('Phone number verified.')
      setCodeSent(false)
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
    },
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Invalid or expired code.'),
  })

  if (error) return <Alert type="error" message="Failed to load notification preferences" />
  if (!preference) return null

  const phoneVerified = !!me?.phone_verified_at

  return (
    <div>
      <Typography.Title level={4}>Notifications</Typography.Title>

      <Form.Item label="Email notifications">
        <Switch
          aria-label="Email notifications"
          checked={preference.email_enabled}
          onChange={(checked) => updateMutation.mutate({ email_enabled: checked })}
        />
      </Form.Item>

      <Form.Item label="SMS notifications">
        <Switch
          aria-label="SMS notifications"
          checked={preference.sms_enabled}
          disabled={!phoneVerified}
          onChange={(checked) => updateMutation.mutate({ sms_enabled: checked })}
        />
      </Form.Item>

      {!phoneVerified && (
        <div>
          <Typography.Text type="secondary">Verify your phone number to enable SMS notifications.</Typography.Text>
          <Form.Item label="Phone number">
            <Input
              aria-label="Phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+15551234567"
            />
          </Form.Item>
          <Button onClick={() => requestCodeMutation.mutate(phoneNumber)}>Send code</Button>

          {codeSent && (
            <>
              <Form.Item label="Verification code">
                <Input aria-label="Verification code" value={code} onChange={(e) => setCode(e.target.value)} />
              </Form.Item>
              <Button onClick={() => confirmCodeMutation.mutate(code)}>Confirm</Button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
