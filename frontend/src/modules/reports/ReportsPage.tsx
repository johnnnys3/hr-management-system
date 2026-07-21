import { useQuery } from '@tanstack/react-query'
import { Alert, DatePicker, Select, Space, Statistic, Table, Tabs, Typography } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import {
  getHeadcountReport,
  getLeaveUtilizationReport,
  getPayrollCostReport,
  getPayrollSummaryReport,
  getTurnoverReport,
} from '../../api/reports'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { useDepartments } from '../departments/hooks'
import { ExportControl } from './ExportControl'

function ReportError({ error }: { error: unknown }) {
  return (
    <Alert
      type="error"
      message="Failed to load report"
      description={error instanceof ApiError ? error.message : 'An error occurred while loading the report.'}
    />
  )
}

function HeadcountTab() {
  const { data: departments = [] } = useDepartments()
  const [departmentId, setDepartmentId] = useState<number>()
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'headcount', departmentId],
    queryFn: () => getHeadcountReport({ department_id: departmentId }),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Filter by department"
          style={{ width: 220 }}
          value={departmentId}
          onChange={setDepartmentId}
          options={departments.map((d) => ({ value: d.id, label: d.name }))}
        />
        <ExportControl reportType="headcount" params={{ department_id: departmentId }} />
      </Space>
      <Statistic title="Total Headcount" value={data?.aggregate.total} loading={isLoading} />
      {data?.breakdown && (
        <Table
          style={{ marginTop: 16 }}
          rowKey="department_id"
          dataSource={data.breakdown}
          pagination={false}
          columns={[
            { title: 'Department', dataIndex: 'department__name' },
            { title: 'Count', dataIndex: 'count' },
          ]}
        />
      )}
    </div>
  )
}

function LeaveUtilizationTab() {
  const { data: departments = [] } = useDepartments()
  const [departmentId, setDepartmentId] = useState<number>()
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'leave-utilization', departmentId],
    queryFn: () => getLeaveUtilizationReport({ department_id: departmentId }),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Filter by department"
          style={{ width: 220 }}
          value={departmentId}
          onChange={setDepartmentId}
          options={departments.map((d) => ({ value: d.id, label: d.name }))}
        />
        <ExportControl reportType="leave_utilization" params={{ department_id: departmentId }} />
      </Space>
      <Space size="large">
        <Statistic title="Entitled Days" value={data?.aggregate.entitled_days} loading={isLoading} />
        <Statistic title="Used Days" value={data?.aggregate.used_days} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <Table
          style={{ marginTop: 16 }}
          rowKey="leave_type_id"
          dataSource={data.breakdown}
          pagination={false}
          columns={[
            { title: 'Leave Type', dataIndex: 'leave_type__name' },
            { title: 'Entitled Days', dataIndex: 'entitled_days' },
            { title: 'Used Days', dataIndex: 'used_days' },
          ]}
        />
      )}
    </div>
  )
}

function TurnoverTab() {
  const { data: departments = [] } = useDepartments()
  const [departmentId, setDepartmentId] = useState<number>()
  const [range, setRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().subtract(365, 'day'), dayjs()])
  const periodStart = range[0].format('YYYY-MM-DD')
  const periodEnd = range[1].format('YYYY-MM-DD')

  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'turnover', departmentId, periodStart, periodEnd],
    queryFn: () => getTurnoverReport({ department_id: departmentId, period_start: periodStart, period_end: periodEnd }),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Filter by department"
          style={{ width: 220 }}
          value={departmentId}
          onChange={setDepartmentId}
          options={departments.map((d) => ({ value: d.id, label: d.name }))}
        />
        <DatePicker.RangePicker
          value={range}
          onChange={(values) => {
            if (values?.[0] && values[1]) setRange([values[0], values[1]])
          }}
        />
        <ExportControl
          reportType="turnover"
          params={{ department_id: departmentId, period_start: periodStart, period_end: periodEnd }}
        />
      </Space>
      <Space size="large">
        <Statistic title="Hires" value={data?.aggregate.hires} loading={isLoading} />
        <Statistic title="Terminations" value={data?.aggregate.terminations} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <Space align="start" size="large" style={{ marginTop: 16 }}>
          <Table
            rowKey="department_id"
            dataSource={data.breakdown.hires_by_department}
            pagination={false}
            title={() => 'Hires by Department'}
            columns={[
              { title: 'Department', dataIndex: 'department__name' },
              { title: 'Count', dataIndex: 'count' },
            ]}
          />
          <Table
            rowKey="employee__department_id"
            dataSource={data.breakdown.terminations_by_department}
            pagination={false}
            title={() => 'Terminations by Department'}
            columns={[
              { title: 'Department', dataIndex: 'employee__department__name' },
              { title: 'Count', dataIndex: 'count' },
            ]}
          />
        </Space>
      )}
    </div>
  )
}

function PayrollCostTab() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'payroll-cost'],
    queryFn: () => getPayrollCostReport({}),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <ExportControl reportType="payroll_cost" params={{}} />
      </Space>
      <Space size="large">
        <Statistic title="Gross Pay" value={data?.aggregate.gross_pay} loading={isLoading} />
        <Statistic title="Net Pay" value={data?.aggregate.net_pay} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <Table
          style={{ marginTop: 16 }}
          rowKey="employee__department_id"
          dataSource={data.breakdown}
          pagination={false}
          columns={[
            { title: 'Department', dataIndex: 'employee__department__name' },
            { title: 'Gross Pay', dataIndex: 'gross_pay' },
            { title: 'Net Pay', dataIndex: 'net_pay' },
          ]}
        />
      )}
    </div>
  )
}

function PayrollSummaryTab() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'payroll-summary'],
    queryFn: () => getPayrollSummaryReport({}),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <ExportControl reportType="payroll_summary" params={{}} />
      </Space>
      <Space size="large">
        <Statistic title="Gross Pay" value={data?.aggregate.gross_pay} loading={isLoading} />
        <Statistic title="Net Pay" value={data?.aggregate.net_pay} loading={isLoading} />
        <Statistic title="Finalized Payslips" value={data?.aggregate.payslip_count} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <Table
          style={{ marginTop: 16 }}
          rowKey="id"
          dataSource={data.breakdown}
          pagination={false}
          columns={[
            { title: 'Period Start', dataIndex: 'period_start' },
            { title: 'Period End', dataIndex: 'period_end' },
            { title: 'Gross Pay', dataIndex: 'gross_pay' },
            { title: 'Net Pay', dataIndex: 'net_pay' },
          ]}
        />
      )}
    </div>
  )
}

export function ReportsPage() {
  const { me } = useAuth()
  const isHr = me?.groups.some((g) => ['HR Administrator', 'HR Officer'].includes(g)) ?? false
  const isPayrollOfficer = me?.groups.includes('Payroll Officer') ?? false
  const isExecutive = me?.groups.includes('Executive') ?? false
  const isManager = me?.is_manager ?? false

  const items = [
    ...(isHr || isExecutive || isManager
      ? [
          { key: 'headcount', label: 'Headcount', children: <HeadcountTab /> },
          { key: 'leave-utilization', label: 'Leave Utilization', children: <LeaveUtilizationTab /> },
          { key: 'turnover', label: 'Turnover', children: <TurnoverTab /> },
        ]
      : []),
    ...(isPayrollOfficer || isExecutive
      ? [
          { key: 'payroll-cost', label: 'Payroll Cost', children: <PayrollCostTab /> },
          { key: 'payroll-summary', label: 'Payroll Summary', children: <PayrollSummaryTab /> },
        ]
      : []),
  ]

  return (
    <div>
      <Typography.Title level={3}>Reports</Typography.Title>
      <Tabs items={items} />
    </div>
  )
}
