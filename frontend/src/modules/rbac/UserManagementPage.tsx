import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Form, Input, Modal, Switch, Table, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import { createUser, listUsers, updateUser } from '../../api/rbac'
import { ApiError } from '../../api/client'
import type { UserAccount } from '../../api/types'

const USERS_QUERY_KEY = ['rbac', 'users']

export function UserManagementPage() {
  const queryClient = useQueryClient()
  const { data: users = [], isLoading } = useQuery({ queryKey: USERS_QUERY_KEY, queryFn: listUsers })
  const [modalUser, setModalUser] = useState<UserAccount | 'new' | null>(null)

  const invalidate = () => queryClient.invalidateQueries({ queryKey: USERS_QUERY_KEY })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3}>Users</Typography.Title>
        <Button type="primary" onClick={() => setModalUser('new')}>
          New User
        </Button>
      </div>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={users}
        pagination={{ pageSize: 25 }}
        onRow={(record) => ({ onClick: () => setModalUser(record) })}
        columns={[
          { title: 'Email', dataIndex: 'email' },
          {
            title: 'Active',
            dataIndex: 'is_active',
            render: (active: boolean) => (active ? <Tag color="green">Active</Tag> : <Tag>Inactive</Tag>),
          },
          {
            title: 'Roles',
            dataIndex: 'groups',
            render: (groups: string[]) => groups.map((g) => <Tag key={g}>{g}</Tag>),
          },
        ]}
      />
      {modalUser && (
        <UserFormModal
          user={modalUser === 'new' ? null : modalUser}
          onClose={() => setModalUser(null)}
          onSaved={() => {
            invalidate()
            setModalUser(null)
          }}
        />
      )}
    </div>
  )
}

interface UserFormValues {
  email: string
  password?: string
  is_active: boolean
}

function UserFormModal({
  user,
  onClose,
  onSaved,
}: {
  user: UserAccount | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form] = Form.useForm<UserFormValues>()

  const mutation = useMutation({
    mutationFn: (values: UserFormValues) =>
      user
        ? updateUser(user.id, values)
        : createUser({ email: values.email, password: values.password ?? '', is_active: values.is_active }),
    onSuccess: onSaved,
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Save failed.'),
  })

  return (
    <Modal
      open
      title={user ? 'Edit User' : 'New User'}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText={user ? 'Save' : 'Create'}
      confirmLoading={mutation.isPending}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ email: user?.email, is_active: user?.is_active ?? true }}
        onFinish={(values) => mutation.mutate(values)}
      >
        <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
          <Input disabled={!!user} />
        </Form.Item>
        <Form.Item label="Password" name="password" rules={[{ required: !user }]}>
          <Input.Password placeholder={user ? 'Leave blank to keep current password' : undefined} />
        </Form.Item>
        <Form.Item label="Active" name="is_active" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  )
}
