import { useQuery } from '@tanstack/react-query'
import { Badge, Layout, Menu, Typography } from 'antd'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { listNotifications } from '../api/notifications'
import { useAuth } from '../auth/AuthContext'

const { Header, Content } = Layout

export function AppLayout() {
  const { me, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const { data: unreadNotifications = [] } = useQuery({
    queryKey: ['notifications', 'list', 'unread-count'],
    queryFn: () => listNotifications({ read_at__isnull: true }),
    refetchInterval: 30000,
  })

  const items = [
    { key: '/', label: <Link to="/">Dashboard</Link> },
    {
      key: '/notifications',
      label: (
        <Link to="/notifications">
          <Badge count={unreadNotifications.length} size="small" offset={[8, 0]}>
            <span style={{ color: 'inherit' }}>Notifications</span>
          </Badge>
        </Link>
      ),
    },
    { key: '/leave', label: <Link to="/leave">Leave</Link> },
    { key: '/role-grant-requests', label: <Link to="/role-grant-requests">Role Grant Requests</Link> },
    ...(me?.groups.some((g) => ['HR Administrator', 'HR Officer', 'Recruiter', 'Payroll Officer'].includes(g))
      ? [{ key: '/departments', label: <Link to="/departments">Departments</Link> }]
      : []),
    ...(me?.groups.some((g) => ['HR Administrator', 'HR Officer'].includes(g))
      ? [{ key: '/employees', label: <Link to="/employees">Employees</Link> }]
      : []),
    ...(me?.groups.some((g) => ['Recruiter', 'HR Administrator', 'HR Officer'].includes(g))
      ? [{ key: '/recruitment', label: <Link to="/recruitment">Recruitment</Link> }]
      : []),
    ...(me?.groups.includes('HR Officer')
      ? [{ key: '/onboarding', label: <Link to="/onboarding">Onboarding</Link> }]
      : []),
    { key: '/second-factor/recovery', label: <Link to="/second-factor/recovery">2FA Recovery</Link> },
    ...(me?.groups.includes('System Administrator')
      ? [{ key: '/users', label: <Link to="/users">Users</Link> }]
      : []),
    { key: 'logout', label: 'Log out' },
  ]

  const handleClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      void logout()
        .then(() => navigate('/login', { replace: true }))
        .catch(() => navigate('/login', { replace: true }))
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <Typography.Title level={4} style={{ color: 'white', margin: '0 24px 0 0' }}>
          HRMS
        </Typography.Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={items}
          onClick={handleClick}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: 24 }}>
        <Outlet />
      </Content>
    </Layout>
  )
}
