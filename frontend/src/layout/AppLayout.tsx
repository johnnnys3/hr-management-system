import { useQuery } from '@tanstack/react-query'
import { Layout } from 'antd'
import type { ReactNode } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { listNotifications } from '../api/notifications'
import { useAuth } from '../auth/AuthContext'

const { Header, Content } = Layout

function NavLink({ to, active, children }: { to: string; active: boolean; children: ReactNode }) {
  return (
    <Link
      to={to}
      style={{
        fontSize: 14,
        fontWeight: active ? 600 : 400,
        color: active ? '#111' : 'rgba(0,0,0,0.45)',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        whiteSpace: 'nowrap',
        flexShrink: 0,
        borderBottom: active ? '2px solid #2F6B4F' : '2px solid transparent',
      }}
    >
      {children}
    </Link>
  )
}

export function AppLayout() {
  const { me, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const { data: unreadNotificationsResponse } = useQuery({
    queryKey: ['notifications', 'list', 'unread-count'],
    queryFn: () => listNotifications({ read_at__isnull: true }),
    refetchInterval: 30000,
  })

  const items: { key: string; label: string; badge?: number }[] = [
    { key: '/', label: 'Dashboard' },
    { key: '/notifications', label: 'Notifications', badge: unreadNotificationsResponse?.count ?? 0 },
    { key: '/leave', label: 'Leave' },
    { key: '/my-profile', label: 'My Profile' },
    ...(me?.is_manager ? [{ key: '/my-team', label: 'My Team' }] : []),
    { key: '/role-grant-requests', label: 'Role Grant Requests' },
    ...(me?.groups.some((g) => ['HR Administrator', 'HR Officer', 'Recruiter', 'Payroll Officer'].includes(g))
      ? [{ key: '/departments', label: 'Departments' }]
      : []),
    ...(me?.groups.some((g) => ['HR Administrator', 'HR Officer'].includes(g))
      ? [{ key: '/employees', label: 'Employees' }]
      : []),
    ...(me?.groups.some((g) => ['Recruiter', 'HR Administrator', 'HR Officer'].includes(g))
      ? [{ key: '/recruitment', label: 'Recruitment' }]
      : []),
    ...(me?.groups.includes('HR Officer') ? [{ key: '/onboarding', label: 'Onboarding' }] : []),
    ...(me?.groups.includes('System Administrator')
      ? [
          { key: '/users', label: 'Users' },
          { key: '/audit-log', label: 'Audit Log' },
        ]
      : []),
    ...(me?.groups.some((g) => ['HR Administrator', 'Payroll Officer', 'Executive'].includes(g)) || me?.is_manager
      ? [{ key: '/reports', label: 'Reports' }]
      : []),
    ...(me?.groups.some((g) => ['HR Administrator', 'HR Officer', 'Payroll Officer'].includes(g))
      ? [{ key: '/compensation', label: 'Compensation' }]
      : []),
    ...(me?.groups.some((g) => ['Payroll Officer', 'HR Administrator'].includes(g))
      ? [{ key: '/payroll', label: 'Payroll' }]
      : []),
  ]

  const handleLogout = () => {
    void logout()
      .then(() => navigate('/login', { replace: true }))
      .catch(() => navigate('/login', { replace: true }))
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#fff' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          background: '#fff',
          borderBottom: '1px solid #ececec',
          padding: '0 40px',
          height: 64,
          lineHeight: 'normal',
          gap: 36,
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 700, color: '#111', flexShrink: 0 }}>HRMS</div>
        <div style={{ display: 'flex', gap: 28, alignItems: 'center', height: '100%', overflowX: 'auto', minWidth: 0 }}>
          {items.map((item) => (
            <NavLink key={item.key} to={item.key} active={location.pathname === item.key}>
              {item.label}
              {!!item.badge && item.badge > 0 && (
                <span
                  style={{
                    background: '#2F6B4F',
                    color: '#fff',
                    fontSize: 10,
                    lineHeight: 1,
                    padding: '2px 5px',
                    borderRadius: 999,
                  }}
                >
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </div>
        <div
          role="button"
          tabIndex={0}
          onClick={handleLogout}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              handleLogout()
            }
          }}
          style={{
            fontSize: 14,
            color: 'rgba(0,0,0,0.45)',
            marginLeft: 'auto',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            cursor: 'pointer',
          }}
        >
          Log out
        </div>
      </Header>
      <Content style={{ padding: '32px 40px' }}>
        <Outlet />
      </Content>
    </Layout>
  )
}
