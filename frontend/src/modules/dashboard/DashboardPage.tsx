import { useQuery } from '@tanstack/react-query'
import { Alert, Progress, Typography } from 'antd'
import { ApiError } from '../../api/client'
import { getDashboard } from '../../api/dashboard'
import { useAuth } from '../../auth/AuthContext'

const GREEN = '#2F6B4F'

function HeadlineStat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div style={{ fontSize: 11, color: 'rgba(0,0,0,0.4)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: '#111' }}>{value}</div>
    </div>
  )
}

function StripStat({ label, value, accent, last }: { label: string; value: string; accent?: boolean; last?: boolean }) {
  return (
    <div style={{ flex: 1, padding: '18px 24px', borderRight: last ? 'none' : '1px solid #ececec' }}>
      <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.4)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: accent ? GREEN : '#111' }}>{value}</div>
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

  const headlineStats = data.aggregates
    ? [
        { label: 'Headcount', value: data.aggregates.headcount.total },
        { label: 'Hires', value: data.aggregates.turnover.hires },
        { label: 'Terminations', value: data.aggregates.turnover.terminations },
      ]
    : data.team
      ? [{ label: 'Team Pending Leave Requests', value: data.team.pending_leave_requests }]
      : []

  const leaveUtilization = data.aggregates?.leave_utilization
  const leaveUtilizationPercent = leaveUtilization
    ? leaveUtilization.entitled_days > 0
      ? Math.round((leaveUtilization.used_days / leaveUtilization.entitled_days) * 100)
      : 0
    : null

  const stripStats = data.aggregates
    ? [
        ...(leaveUtilizationPercent !== null
          ? [{ label: 'Leave Utilization', value: `${leaveUtilizationPercent}%`, accent: true }]
          : []),
        { label: 'Payroll Gross Pay', value: String(data.aggregates.payroll_cost.gross_pay) },
        { label: 'Payroll Net Pay', value: String(data.aggregates.payroll_cost.net_pay) },
        { label: 'Finalized Payslips', value: String(data.aggregates.payroll_summary.payslip_count) },
      ]
    : []

  const hasBottomSection = Boolean(data.leave_balance?.length || data.pending_tasks?.length)

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: 20,
          borderBottom: '1px solid #ececec',
          marginBottom: 24,
        }}
      >
        <div>
          <Typography.Title level={3} style={{ margin: 0, lineHeight: 1.3 }}>
            {getGreeting()}{me ? `, ${me.email.split('@')[0]}` : ''}
          </Typography.Title>
          <div style={{ fontSize: 13, color: 'rgba(0,0,0,0.4)' }}>Here's what's happening today.</div>
        </div>
        {headlineStats.length > 0 && (
          <div style={{ display: 'flex', gap: 36 }}>
            {headlineStats.map((stat) => (
              <HeadlineStat key={stat.label} label={stat.label} value={stat.value} />
            ))}
          </div>
        )}
      </div>

      {stripStats.length > 0 && (
        <div
          style={{
            display: 'flex',
            borderTop: '1px solid #ececec',
            borderBottom: '1px solid #ececec',
            marginBottom: 24,
          }}
        >
          {stripStats.map((stat, i) => (
            <StripStat key={stat.label} {...stat} last={i === stripStats.length - 1} />
          ))}
        </div>
      )}

      {hasBottomSection && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 40 }}>
          {data.leave_balance && data.leave_balance.length > 0 && (
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#111', marginBottom: 12 }}>My Leave Balance</div>
              {data.leave_balance.map((balance, i) => {
                const entitled = Number(balance.entitled_days)
                const used = Number(balance.used_days)
                const percent = entitled > 0 ? Math.round((used / entitled) * 100) : 0
                return (
                  <div
                    key={`${balance.period_start}-${balance.period_end}`}
                    style={{
                      padding: '14px 0',
                      borderBottom: i === data.leave_balance!.length - 1 ? 'none' : '1px solid #f2f2f2',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 13,
                        color: 'rgba(0,0,0,0.6)',
                        marginBottom: 6,
                      }}
                    >
                      <span>
                        {balance.period_start} – {balance.period_end}
                      </span>
                      <span>
                        {balance.used_days} / {balance.entitled_days} days used
                      </span>
                    </div>
                    <Progress percent={percent} showInfo={false} strokeColor={GREEN} size="small" />
                  </div>
                )
              })}
            </div>
          )}
          {data.pending_tasks && data.pending_tasks.length > 0 && (
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#111', marginBottom: 12 }}>Pending Tasks</div>
              {data.pending_tasks.map((task, i) => (
                <div
                  key={task.id}
                  style={{
                    fontSize: 13,
                    color: 'rgba(0,0,0,0.6)',
                    padding: '10px 0',
                    borderBottom: i === data.pending_tasks!.length - 1 ? 'none' : '1px solid #f2f2f2',
                  }}
                >
                  {task.subject}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
