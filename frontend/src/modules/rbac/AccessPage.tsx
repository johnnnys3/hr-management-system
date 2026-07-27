import { Typography } from 'antd'
import { useAuth } from '../../auth/AuthContext'
import { AccessApprovalsQueue } from './AccessApprovalsQueue'
import { GrantAccessForm } from './GrantAccessForm'

export function AccessPage() {
  const { me } = useAuth()
  const canGrantAccess = me?.groups.includes('System Administrator') ?? false
  const canApproveAccess = me?.groups.includes('HR Administrator') ?? false

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      <Typography.Title level={3}>Access</Typography.Title>
      {canGrantAccess && <GrantAccessForm />}
      {canGrantAccess && canApproveAccess && <div style={{ borderTop: '1px solid #ececec' }} />}
      {canApproveAccess && <AccessApprovalsQueue />}
    </div>
  )
}
