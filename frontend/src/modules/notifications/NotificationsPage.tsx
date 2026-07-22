import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, List, Segmented, Tag, Typography } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { listNotifications, markNotificationRead } from '../../api/notifications'
import type { Notification } from '../../api/types'
import { StatStrip } from '../../components/StatStrip'

const CATEGORY_LABELS: Record<string, string> = {
  pending_task: 'Pending task',
  request_update: 'Request update',
}

const NOTIFICATIONS_QUERY_KEY = ['notifications', 'list']

export function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread'>('unread')
  const queryClient = useQueryClient()
  const { data: notifications = [], isLoading, error } = useQuery({
    queryKey: [...NOTIFICATIONS_QUERY_KEY, filter],
    queryFn: () => listNotifications(filter === 'unread' ? { read_at__isnull: true } : {}),
  })

  const { data: unread = [] } = useQuery({
    queryKey: [...NOTIFICATIONS_QUERY_KEY, 'unread'],
    queryFn: () => listNotifications({ read_at__isnull: true }),
  })

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY }),
  })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load notifications"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading notifications.'}
      />
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Notifications
        </Typography.Title>
        <Segmented
          value={filter}
          onChange={(value) => setFilter(value as 'all' | 'unread')}
          options={[
            { label: 'Unread', value: 'unread' },
            { label: 'All', value: 'all' },
          ]}
        />
      </div>
      <StatStrip
        stats={[
          { label: 'Unread', value: unread.length },
          { label: 'Pending Tasks', value: unread.filter((n) => n.category === 'pending_task').length },
          { label: 'Request Updates', value: unread.filter((n) => n.category === 'request_update').length },
        ]}
      />
      <List<Notification>
        loading={isLoading}
        dataSource={notifications}
        locale={{ emptyText: filter === 'unread' ? 'No unread notifications.' : 'No notifications.' }}
        renderItem={(notification) => (
          <List.Item
            actions={
              notification.read_at
                ? []
                : [
                    <Button
                      key="mark-read"
                      size="small"
                      loading={markReadMutation.isPending && markReadMutation.variables === notification.id}
                      onClick={() => markReadMutation.mutate(notification.id)}
                    >
                      Mark read
                    </Button>,
                  ]
            }
          >
            <List.Item.Meta
              title={
                <>
                  {notification.subject} <Tag>{CATEGORY_LABELS[notification.category]}</Tag>
                </>
              }
              description={notification.body}
            />
            <Typography.Text type="secondary">{new Date(notification.created_at).toLocaleString()}</Typography.Text>
          </List.Item>
        )}
      />
    </div>
  )
}
