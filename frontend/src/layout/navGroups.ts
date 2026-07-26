import type { Me } from '../api/types'

export interface NavItem {
  key: string
  label: string
  icon: string
  badge?: number
}

export interface NavGroup {
  label: string
  items: NavItem[]
}

function hasAnyGroup(me: Me, allowed: string[]): boolean {
  return me.groups.some((g) => allowed.includes(g))
}

export function buildNavGroups(me: Me | null, unreadNotifications = 0): NavGroup[] {
  if (!me) return []

  const myWork: NavItem[] = [
    { key: '/', label: 'Dashboard', icon: 'DashboardOutlined' },
    { key: '/notifications', label: 'Notifications', icon: 'BellOutlined', badge: unreadNotifications },
    { key: '/leave', label: 'Leave', icon: 'CalendarOutlined' },
    { key: '/my-profile', label: 'My Profile', icon: 'UserOutlined' },
  ]

  const people: NavItem[] = [
    ...(me.is_manager ? [{ key: '/my-team', label: 'My Team', icon: 'TeamOutlined' }] : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer', 'Recruiter', 'Payroll Officer'])
      ? [{ key: '/departments', label: 'Departments', icon: 'ApartmentOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer'])
      ? [{ key: '/employees', label: 'Employees', icon: 'IdcardOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['Recruiter', 'HR Administrator', 'HR Officer'])
      ? [{ key: '/recruitment', label: 'Recruitment', icon: 'SolutionOutlined' }]
      : []),
    ...(me.groups.includes('HR Officer') ? [{ key: '/onboarding', label: 'Onboarding', icon: 'RocketOutlined' }] : []),
  ]

  const payrollAndCompensation: NavItem[] = [
    ...(hasAnyGroup(me, ['HR Administrator', 'HR Officer', 'Payroll Officer'])
      ? [{ key: '/compensation', label: 'Compensation', icon: 'DollarOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['Payroll Officer', 'HR Administrator'])
      ? [{ key: '/payroll', label: 'Payroll', icon: 'WalletOutlined' }]
      : []),
    ...(hasAnyGroup(me, ['HR Administrator', 'Payroll Officer', 'Executive']) || me.is_manager
      ? [{ key: '/reports', label: 'Reports', icon: 'BarChartOutlined' }]
      : []),
  ]

  const canGrantAccess = me.groups.includes('System Administrator')
  // Proxy for the `iam.approve_role_grant` permission, which the frontend
  // has no general mechanism to query directly — correct given the
  // migration in backend/iam/migrations/0003_... defaults that permission
  // to this group. Revisit if a deployment ever assigns the permission
  // elsewhere (docs/07-iam-rbac.md §8).
  const canApproveAccess = me.groups.includes('HR Administrator')

  let accessLabel: string | null = null
  if (canGrantAccess && canApproveAccess) {
    accessLabel = 'Access'
  } else if (canGrantAccess) {
    accessLabel = 'Grant Access'
  } else if (canApproveAccess) {
    accessLabel = 'Access Approvals'
  }

  const admin: NavItem[] = [
    ...(accessLabel ? [{ key: '/access', label: accessLabel, icon: 'SafetyCertificateOutlined' }] : []),
    ...(me.groups.includes('System Administrator')
      ? [
          { key: '/users', label: 'Users', icon: 'UsergroupAddOutlined' },
          { key: '/audit-log', label: 'Audit Log', icon: 'FileSearchOutlined' },
        ]
      : []),
  ]

  const groups: NavGroup[] = [
    { label: 'My Work', items: myWork },
    { label: 'People', items: people },
    { label: 'Payroll & Compensation', items: payrollAndCompensation },
    { label: 'Admin', items: admin },
  ]

  return groups.filter((g) => g.items.length > 0)
}
