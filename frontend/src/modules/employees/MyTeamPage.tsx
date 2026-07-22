import { useQuery } from '@tanstack/react-query'
import { Alert, Table, Typography } from 'antd'
import { ApiError } from '../../api/client'
import { listDirectReports } from '../../api/reporting'
import { getMyProfile } from '../../api/selfService'
import type { Employee } from '../../api/types'
import { StatStrip } from '../../components/StatStrip'

export function MyTeamPage() {
  const { data: me, isLoading: isMeLoading, error: meError } = useQuery({ queryKey: ['self-service', 'me'], queryFn: getMyProfile })

  const { data: reports = [], isLoading: isReportsLoading, error: reportsError } = useQuery({
    queryKey: ['reporting', 'direct-reports', me?.id],
    queryFn: () => listDirectReports(me?.id as number),
    enabled: me !== undefined,
  })

  const error = meError ?? reportsError
  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load your team"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading your team.'}
      />
    )
  }

  return (
    <div>
      <Typography.Title level={3}>My Team</Typography.Title>
      <StatStrip
        stats={[
          { label: 'Team Size', value: reports.length },
          { label: 'Active', value: reports.filter((r) => r.employment_status === 'active').length },
          { label: 'On Leave', value: reports.filter((r) => r.employment_status === 'on_leave').length },
        ]}
      />
      <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden' }}>
        <Table<Employee>
          rowKey="id"
          loading={isMeLoading || isReportsLoading}
          dataSource={reports}
          pagination={{ pageSize: 25 }}
          locale={{ emptyText: 'You have no direct reports.' }}
          columns={[
            { title: 'Employee #', dataIndex: 'employee_number' },
            { title: 'First Name', dataIndex: 'first_name' },
            { title: 'Last Name', dataIndex: 'last_name' },
            { title: 'Employment Status', dataIndex: 'employment_status' },
          ]}
        />
      </div>
    </div>
  )
}
