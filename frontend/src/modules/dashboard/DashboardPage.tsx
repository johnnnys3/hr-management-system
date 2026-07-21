import { useQuery } from '@tanstack/react-query'
import { Alert, Card, Col, List, Row, Statistic, Typography } from 'antd'
import { ApiError } from '../../api/client'
import { getDashboard } from '../../api/dashboard'

export function DashboardPage() {
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

  return (
    <div>
      <Typography.Title level={3}>Dashboard</Typography.Title>

      {data.aggregates && (
        <Row gutter={16}>
          <Col span={8}>
            <Card>
              <Statistic title="Headcount" value={data.aggregates.headcount.total} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Leave Days Entitled" value={data.aggregates.leave_utilization.entitled_days} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Leave Days Used" value={data.aggregates.leave_utilization.used_days} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Hires (last 365 days)" value={data.aggregates.turnover.hires} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Terminations (last 365 days)" value={data.aggregates.turnover.terminations} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Payroll Gross Pay" value={data.aggregates.payroll_cost.gross_pay} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Payroll Net Pay" value={data.aggregates.payroll_cost.net_pay} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="Finalized Payslips" value={data.aggregates.payroll_summary.payslip_count} />
            </Card>
          </Col>
        </Row>
      )}

      {data.team && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Card>
              <Statistic title="Team Pending Leave Requests" value={data.team.pending_leave_requests} />
            </Card>
          </Col>
        </Row>
      )}

      {(data.leave_balance || data.pending_tasks) && (
        <Row gutter={16}>
          {data.leave_balance && (
            <Col span={12}>
              <Card title="My Leave Balance">
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
            </Col>
          )}
          {data.pending_tasks && (
            <Col span={12}>
              <Card title="Pending Tasks">
                <List
                  dataSource={data.pending_tasks}
                  locale={{ emptyText: 'No pending tasks.' }}
                  renderItem={(task) => <List.Item>{task.subject}</List.Item>}
                />
              </Card>
            </Col>
          )}
        </Row>
      )}
    </div>
  )
}
