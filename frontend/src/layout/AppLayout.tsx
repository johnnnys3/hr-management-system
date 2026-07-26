import {
  ApartmentOutlined,
  BarChartOutlined,
  BellOutlined,
  CalendarOutlined,
  DashboardOutlined,
  DollarOutlined,
  FileSearchOutlined,
  IdcardOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RocketOutlined,
  SafetyCertificateOutlined,
  SolutionOutlined,
  TeamOutlined,
  UserOutlined,
  UsergroupAddOutlined,
  WalletOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { Badge, Dropdown, Layout, Menu } from 'antd'
import type { MenuProps } from 'antd'
import type { ReactNode } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { listNotifications } from '../api/notifications'
import { useAuth } from '../auth/AuthContext'
import { buildNavGroups } from './navGroups'
import { useSidebarCollapse } from './useSidebarCollapse'

const { Header, Sider, Content } = Layout

const ICONS: Record<string, ReactNode> = {
  DashboardOutlined: <DashboardOutlined />,
  BellOutlined: <BellOutlined />,
  CalendarOutlined: <CalendarOutlined />,
  UserOutlined: <UserOutlined />,
  TeamOutlined: <TeamOutlined />,
  ApartmentOutlined: <ApartmentOutlined />,
  IdcardOutlined: <IdcardOutlined />,
  SolutionOutlined: <SolutionOutlined />,
  RocketOutlined: <RocketOutlined />,
  DollarOutlined: <DollarOutlined />,
  WalletOutlined: <WalletOutlined />,
  BarChartOutlined: <BarChartOutlined />,
  UsergroupAddOutlined: <UsergroupAddOutlined />,
  FileSearchOutlined: <FileSearchOutlined />,
  SafetyCertificateOutlined: <SafetyCertificateOutlined />,
}

export function AppLayout() {
  const { me, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const { collapsed, setCollapsed } = useSidebarCollapse()

  const { data: unreadNotificationsResponse } = useQuery({
    queryKey: ['notifications', 'list', 'unread-count'],
    queryFn: () => listNotifications({ read_at__isnull: true }),
    refetchInterval: 30000,
  })

  const navGroups = buildNavGroups(me, unreadNotificationsResponse?.count ?? 0)

  const menuItems: MenuProps['items'] = navGroups.map((group) => ({
    key: group.label,
    label: group.label,
    type: 'group',
    children: group.items.map((item) => ({
      key: item.key,
      icon: ICONS[item.icon],
      label: (
        <Link to={item.key}>
          {item.label}
          {!!item.badge && item.badge > 0 && <Badge count={item.badge} size="small" style={{ marginLeft: 8 }} />}
        </Link>
      ),
    })),
  }))

  const handleLogout = () => {
    void logout()
      .then(() => navigate('/login', { replace: true }))
      .catch(() => navigate('/login', { replace: true }))
  }

  const userMenuItems: MenuProps['items'] = [{ key: 'logout', label: 'Log out', onClick: handleLogout }]

  return (
    <Layout style={{ minHeight: '100vh', background: '#fff' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          background: '#fff',
          borderBottom: '1px solid #ececec',
          padding: '0 24px',
          height: 56,
          lineHeight: 'normal',
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 700, color: '#111' }}>HRMS</div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 20 }}>
          <Link to="/notifications" style={{ color: 'rgba(0,0,0,0.65)', display: 'flex', alignItems: 'center' }}>
            <Badge count={unreadNotificationsResponse?.count ?? 0} size="small">
              <BellOutlined style={{ fontSize: 18 }} />
            </Badge>
          </Link>
          <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
            <button
              type="button"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                cursor: 'pointer',
                border: 'none',
                background: 'none',
                padding: 0,
                font: 'inherit',
              }}
            >
              <UserOutlined />
              <span style={{ fontSize: 14 }}>{me?.email}</span>
            </button>
          </Dropdown>
        </div>
      </Header>
      <Layout>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          trigger={null}
          theme="light"
          width={220}
          style={{ borderRight: '1px solid #ececec', position: 'relative' }}
        >
          <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} style={{ borderRight: 'none' }} />
          <button
            type="button"
            aria-label="collapse sidebar"
            onClick={() => setCollapsed(!collapsed)}
            style={{
              position: 'absolute',
              bottom: 12,
              left: collapsed ? 20 : 190,
              border: '1px solid #ececec',
              borderRadius: 6,
              background: '#fff',
              width: 28,
              height: 28,
              cursor: 'pointer',
            }}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </button>
        </Sider>
        <Content style={{ padding: '32px 40px' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
