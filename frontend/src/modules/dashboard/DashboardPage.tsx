import { useQuery } from '@tanstack/react-query'
import {
  ArrowUpOutlined,
  BankOutlined,
  CalendarOutlined,
  DollarOutlined,
  FileDoneOutlined,
  TeamOutlined,
  UserAddOutlined,
  UserDeleteOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Alert, Avatar, Card, Col, List, Progress, Row, Statistic, Typography } from 'antd'
import { ApiError } from '../../api/client'
import { getDashboard } from '../../api/dashboard'
import { useAuth } from '../../auth/AuthContext'

// Card background cycles through this palette, matching the mockup's
// mint/yellow/cream tile treatment. ponytail: fixed 3-color cycle, not a
// theming system -- extend the array if more colors are ever wanted.
const TILE_COLORS = ['#E7F0E4', '#FBF3D5', '#FFFFFF']
const ICON_COLORS = ['#3C8C5B', '#B8952E', '#3C6E9C']

function tileStyle(index: number) {
  return {
    background: TILE_COLORS[index % TILE_COLORS.length],
    border: 'none',
    boxShadow: '0 4px 16px rgba(30, 20, 0, 0.06)',
  }
}

const STAT_ICONS: Record<string, typeof TeamOutlined> = {
  Headcount: TeamOutlined,
  Hires: UserAddOutlined,
  Terminations: UserDeleteOutlined,
  'Leave Days Entitled': CalendarOutlined,
  'Leave Days Used': CalendarOutlined,
  'Payroll Gross Pay': DollarOutlined,
  'Payroll Net Pay': DollarOutlined,
  'Finalized Payslips': FileDoneOutlined,
  'Finalized Payroll Gross Pay': BankOutlined,
  'Finalized Payroll Net Pay': BankOutlined,
  'Team Pending Leave Requests': CalendarOutlined,
}

function HeadlineStat({ label, value }: { label: string; value: number }) {
  const Icon = STAT_ICONS[label] ?? ArrowUpOutlined
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <Avatar size={36} icon={<Icon />} style={{ background: '#111', flexShrink: 0 }} />
      <div>
        <Typography.Text strong style={{ fontSize: 28, lineHeight: 1, display: 'block' }}>
          {value}
        </Typography.Text>
        <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 13 }}>{label}</div>
      </div>
    </div>
  )
}

export function DashboardPage() {
  const { me } = useAuth()
  const { data, isLoading, error } = useQuery({ queryKey: ['dashboard'], queryFn: getDashboard })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load dashboard"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading the dashboard.'}
      />
    )
  }

  if (isLoading || !data) {
    return null
  }

  // Header-strip headline numbers, mockup style -- only real figures we
  // actually have, up to three, no fabricated placeholders.
  const headlineStats = data.aggregates
    ? [
        { label: 'Headcount', value: data.aggregates.headcount.total },
        { label: 'Hires', value: data.aggregates.turnover.hires },
        { label: 'Terminations', value: data.aggregates.turnover.terminations },
      ]
    : data.team
      ? [{ label: 'Team Pending Leave Requests', value: data.team.pending_leave_requests }]
      : []

  const remainingStats = data.aggregates
    ? [
        { title: 'Payroll Gross Pay', value: data.aggregates.payroll_cost.gross_pay },
        { title: 'Payroll Net Pay', value: data.aggregates.payroll_cost.net_pay },
        { title: 'Finalized Payslips', value: data.aggregates.payroll_summary.payslip_count },
        { title: 'Finalized Payroll Gross Pay', value: data.aggregates.payroll_summary.gross_pay },
        { title: 'Finalized Payroll Net Pay', value: data.aggregates.payroll_summary.net_pay },
      ]
    : []

  const leaveUtilization = data.aggregates?.leave_utilization
  const leaveUtilizationPercent = leaveUtilization
    ? leaveUtilization.entitled_days > 0
      ? Math.round((leaveUtilization.used_days / leaveUtilization.entitled_days) * 100)
      : 0
    : null

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <Avatar size={48} icon={<UserOutlined />} style={{ background: '#111' }} />
          <div>
            <Typography.Title level={3} style={{ margin: 0, lineHeight: 1.2 }}>
              Good morning{me ? `, ${me.email.split('@')[0]}` : ''}
            </Typography.Title>
            <Typography.Text type="secondary">Here's what's happening today.</Typography.Text>
          </div>
        </div>
        {headlineStats.length > 0 && (
          <div style={{ display: 'flex', gap: 32 }}>
            {headlineStats.map((stat) => (
              <HeadlineStat key={stat.label} label={stat.label} value={stat.value} />
            ))}
          </div>
        )}
      </div>

      <Row gutter={[16, 16]}>
        <Col span={16}>
          {leaveUtilizationPercent !== null && leaveUtilization && (
            <Card style={{ ...tileStyle(0), marginBottom: 16 }} styles={{ body: { padding: 20 } }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                <Progress
                  type="circle"
                  percent={leaveUtilizationPercent}
                  size={88}
                  strokeColor="#3C8C5B"
                />
                <div>
                  <Typography.Text strong style={{ fontSize: 16, display: 'block' }}>
                    Leave Utilization
                  </Typography.Text>
                  <Typography.Text type="secondary">
                    {leaveUtilization.used_days} of {leaveUtilization.entitled_days} entitled days used
                  </Typography.Text>
                </div>
              </div>
            </Card>
          )}
          {remainingStats.length > 0 && (
            <Row gutter={[16, 16]}>
              {remainingStats.map((stat, i) => {
                const Icon = STAT_ICONS[stat.title] ?? ArrowUpOutlined
                return (
                  <Col span={12} key={stat.title}>
                    <Card style={tileStyle(i)} styles={{ body: { padding: 20 } }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <Avatar
                          size={40}
                          icon={<Icon />}
                          style={{ background: ICON_COLORS[i % ICON_COLORS.length] }}
                        />
                        <Statistic title={stat.title} value={stat.value} />
                      </div>
                    </Card>
                  </Col>
                )
              })}
            </Row>
          )}
          {data.leave_balance && (
            <Card
              title="My Leave Balance"
              style={{ marginTop: remainingStats.length > 0 ? 16 : 0, boxShadow: '0 4px 16px rgba(30, 20, 0, 0.06)' }}
            >
              <List
                dataSource={data.leave_balance}
                locale={{ emptyText: 'No leave balance records.' }}
                renderItem={(balance) => {
                  const entitled = Number(balance.entitled_days)
                  const used = Number(balance.used_days)
                  const percent = entitled > 0 ? Math.round((used / entitled) * 100) : 0
                  return (
                    <List.Item>
                      <div style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <span>
                            {balance.period_start} – {balance.period_end}
                          </span>
                          <span>
                            {balance.used_days} / {balance.entitled_days} days used
                          </span>
                        </div>
                        <Progress percent={percent} showInfo={false} strokeColor="#3C8C5B" />
                      </div>
                    </List.Item>
                  )
                }}
              />
            </Card>
          )}
        </Col>
        <Col span={8}>
          {data.pending_tasks && (
            <Card title="Pending Tasks" style={tileStyle(2)}>
              <List
                dataSource={data.pending_tasks}
                locale={{ emptyText: 'No pending tasks.' }}
                renderItem={(task) => <List.Item>{task.subject}</List.Item>}
              />
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}
