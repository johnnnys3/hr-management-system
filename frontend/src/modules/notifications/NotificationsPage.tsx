import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, List, Segmented, Tag, Typography } from 'antd'
import { useState } from 'react'
import { listNotifications, markNotificationRead } from '../../api/notifications'
import type { Notification } from '../../api/types'

const CATEGORY_LABELS: Record<string, string> = {
  pending_task: 'Pending task',
  request_update: 'Request update',
}

const NOTIFICATIONS_QUERY_KEY = ['notifications', 'list']

export function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread'>('unread')
  const queryClient = useQueryClient()
  const { data: notifications = [], isLoading } = useQuery({
    queryKey: [...NOTIFICATIONS_QUERY_KEY, filter],
    queryFn: () => listNotifications(filter === 'unread' ? { read_at__isnull: true } : {}),
  })

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY }),
  })

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
