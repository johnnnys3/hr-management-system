import { Card, Tag, Typography } from 'antd'
import { useAuth } from '../../auth/AuthContext'

export function HomePage() {
  const { me } = useAuth()
  if (!me) return null

  return (
    <Card>
      <Typography.Title level={3}>Welcome, {me.email}</Typography.Title>
      <Typography.Paragraph type="secondary">
        This is a placeholder landing page. The Executive Dashboard (module 14) has its own screen, built
        later in the frontend batch.
      </Typography.Paragraph>
      <Typography.Text strong>Your roles: </Typography.Text>
      {me.groups.length === 0 ? (
        <Typography.Text type="secondary">none assigned</Typography.Text>
      ) : (
        me.groups.map((group) => <Tag key={group}>{group}</Tag>)
      )}
    </Card>
  )
}
