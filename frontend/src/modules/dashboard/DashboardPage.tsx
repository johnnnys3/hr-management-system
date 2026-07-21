import { useQuery } from '@tanstack/react-query'
import { Alert, Card, Col, List, Row, Statistic, Typography } from 'antd'
import { ApiError } from '../../api/client'
import { getDashboard } from '../../api/dashboard'
import { useAuth } from '../../auth/AuthContext'

// Card background cycles through this palette, matching the mockup's
// mint/yellow/cream tile treatment. ponytail: fixed 3-color cycle, not a
// theming system -- extend the array if more colors are ever wanted.
const TILE_COLORS = ['#E7F0E4', '#FBF3D5', '#FFFFFF']

function tileStyle(index: number) {
  return { background: TILE_COLORS[index % TILE_COLORS.length], border: 'none' }
}

function HeadlineStat({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ textAlign: 'right' }}>
      <Typography.Text strong style={{ fontSize: 28, lineHeight: 1 }}>
        {value}
      </Typography.Text>
      <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 13 }}>{label}</div>
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
        { title: 'Leave Days Entitled', value: data.aggregates.leave_utilization.entitled_days },
        { title: 'Leave Days Used', value: data.aggregates.leave_utilization.used_days },
        { title: 'Payroll Gross Pay', value: data.aggregates.payroll_cost.gross_pay },
        { title: 'Payroll Net Pay', value: data.aggregates.payroll_cost.net_pay },
        { title: 'Finalized Payslips', value: data.aggregates.payroll_summary.payslip_count },
        { title: 'Finalized Payroll Gross Pay', value: data.aggregates.payroll_summary.gross_pay },
        { title: 'Finalized Payroll Net Pay', value: data.aggregates.payroll_summary.net_pay },
      ]
    : []

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <Typography.Title level={2} style={{ margin: 0 }}>
          Good morning{me ? `, ${me.email.split('@')[0]}` : ''}
        </Typography.Title>
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
          {remainingStats.length > 0 && (
            <Row gutter={[16, 16]}>
              {remainingStats.map((stat, i) => (
                <Col span={12} key={stat.title}>
                  <Card style={tileStyle(i)}>
                    <Statistic title={stat.title} value={stat.value} />
                  </Card>
                </Col>
              ))}
            </Row>
          )}
          {data.leave_balance && (
            <Card title="My Leave Balance" style={{ marginTop: remainingStats.length > 0 ? 16 : 0 }}>
              <List
                dataSource={data.leave_balance}
                locale={{ emptyText: 'No leave balance records.' }}
                renderItem={(balance) => (
                  <List.Item>
                    {balance.period_start} – {balance.period_end}: {balance.used_days} / {balance.entitled_days} days
                    used
                  </List.Item>
                )}
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
