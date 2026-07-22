import { useQuery } from '@tanstack/react-query'
import { Alert, DatePicker, Select, Space, Statistic, Table, Tabs, Typography } from 'antd'
import dayjs from 'dayjs'
import { useState, type ReactNode } from 'react'
import {
  getHeadcountReport,
  getLeaveUtilizationReport,
  getPayrollCostReport,
  getPayrollSummaryReport,
  getTurnoverReport,
} from '../../api/reports'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { StatStrip } from '../../components/StatStrip'
import { useDepartments } from '../departments/hooks'
import { ExportControl } from './ExportControl'

function ReportTableCard({ children }: { children: ReactNode }) {
  return (
    <div style={{ border: '1px solid #ececec', borderRadius: 10, overflow: 'hidden', marginTop: 16 }}>
      {children}
    </div>
  )
}

function ReportError({ error }: { error: unknown }) {
  return (
    <Alert
      type="error"
      message="Failed to load report"
      description={error instanceof ApiError ? error.message : 'An error occurred while loading the report.'}
    />
  )
}

function HeadcountTab({ isHr }: { isHr: boolean }) {
  const { data: departments = [] } = useDepartments({ enabled: isHr })
  const [departmentId, setDepartmentId] = useState<number>()
  // Only an HR viewer's own selection is ever sent downstream — if isHr
  // flips false while this stays mounted (a live role change), a stale
  // departmentId from before must not keep riding along in the query or export.
  const effectiveDepartmentId = isHr ? departmentId : undefined
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'headcount', effectiveDepartmentId],
    queryFn: () => getHeadcountReport({ department_id: effectiveDepartmentId }),
  })

  if (error) return <ReportError error={error} />

  // The API breaks down by (department, employment_status) pairs, not by
  // department alone — aggregate to per-department totals for display.
  const byDepartment = new Map<number, { department_id: number; department__name: string; count: number }>()
  for (const row of data?.breakdown ?? []) {
    const existing = byDepartment.get(row.department_id)
    if (existing) {
      existing.count += row.count
    } else {
      byDepartment.set(row.department_id, { ...row })
    }
  }
  const departmentBreakdown = [...byDepartment.values()]
  const maxCount = Math.max(1, ...departmentBreakdown.map((row) => row.count))

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {isHr && (
          <Select
            allowClear
            placeholder="Filter by department"
            style={{ width: 220 }}
            value={departmentId}
            onChange={setDepartmentId}
            options={departments.map((d) => ({ value: d.id, label: d.name }))}
          />
        )}
        <ExportControl reportType="headcount" params={{ department_id: effectiveDepartmentId }} />
      </Space>
      <StatStrip
        stats={[
          { label: 'Total Headcount', value: isLoading ? '—' : (data?.aggregate.total ?? 0) },
          ...(isHr ? [{ label: 'Departments', value: departments.length }] : []),
        ]}
      />
      {departmentBreakdown.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 48 }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#111', marginBottom: 16 }}>
              Headcount by Department
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {departmentBreakdown.map((row) => (
                <div key={row.department_id}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                    <span>{row.department__name}</span>
                    <span style={{ color: '#111', fontWeight: 600 }}>{row.count}</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 4, background: '#f2f2f2', overflow: 'hidden' }}>
                    <div
                      style={{ height: '100%', width: `${(row.count / maxCount) * 100}%`, background: '#2F6B4F' }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#111', marginBottom: 16 }}>Department Table</div>
            <ReportTableCard>
              <Table
                rowKey="department_id"
                dataSource={departmentBreakdown}
                pagination={false}
                showHeader
                columns={[
                  { title: 'Department', dataIndex: 'department__name' },
                  { title: 'Count', dataIndex: 'count' },
                ]}
              />
            </ReportTableCard>
          </div>
        </div>
      )}
    </div>
  )
}

function LeaveUtilizationTab({ isHr }: { isHr: boolean }) {
  const { data: departments = [] } = useDepartments({ enabled: isHr })
  const [departmentId, setDepartmentId] = useState<number>()
  const effectiveDepartmentId = isHr ? departmentId : undefined
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'leave-utilization', effectiveDepartmentId],
    queryFn: () => getLeaveUtilizationReport({ department_id: effectiveDepartmentId }),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {isHr && (
          <Select
            allowClear
            placeholder="Filter by department"
            style={{ width: 220 }}
            value={departmentId}
            onChange={setDepartmentId}
            options={departments.map((d) => ({ value: d.id, label: d.name }))}
          />
        )}
        <ExportControl reportType="leave_utilization" params={{ department_id: effectiveDepartmentId }} />
      </Space>
      <Space size="large">
        <Statistic title="Entitled Days" value={data?.aggregate.entitled_days} loading={isLoading} />
        <Statistic title="Used Days" value={data?.aggregate.used_days} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <ReportTableCard>
          <Table
            rowKey="leave_type_id"
            dataSource={data.breakdown}
            pagination={false}
            columns={[
              { title: 'Leave Type', dataIndex: 'leave_type__name' },
              { title: 'Entitled Days', dataIndex: 'entitled_days' },
              { title: 'Used Days', dataIndex: 'used_days' },
            ]}
          />
        </ReportTableCard>
      )}
    </div>
  )
}

function TurnoverTab({ isHr }: { isHr: boolean }) {
  const { data: departments = [] } = useDepartments({ enabled: isHr })
  const [departmentId, setDepartmentId] = useState<number>()
  const [range, setRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().subtract(365, 'day'), dayjs()])
  const periodStart = range[0].format('YYYY-MM-DD')
  const periodEnd = range[1].format('YYYY-MM-DD')
  const effectiveDepartmentId = isHr ? departmentId : undefined

  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', 'turnover', effectiveDepartmentId, periodStart, periodEnd],
    queryFn: () =>
      getTurnoverReport({ department_id: effectiveDepartmentId, period_start: periodStart, period_end: periodEnd }),
  })

  if (error) return <ReportError error={error} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {isHr && (
          <Select
            allowClear
            placeholder="Filter by department"
            style={{ width: 220 }}
            value={departmentId}
            onChange={setDepartmentId}
            options={departments.map((d) => ({ value: d.id, label: d.name }))}
          />
        )}
        <DatePicker.RangePicker
          value={range}
          onChange={(values) => {
            if (values?.[0] && values[1]) setRange([values[0], values[1]])
          }}
        />
        <ExportControl
          reportType="turnover"
          params={{ department_id: effectiveDepartmentId, period_start: periodStart, period_end: periodEnd }}
        />
      </Space>
      <Space size="large">
        <Statistic title="Hires" value={data?.aggregate.hires} loading={isLoading} />
        <Statistic title="Terminations" value={data?.aggregate.terminations} loading={isLoading} />
      </Space>
      {data?.breakdown && (
        <Space align="start" size="large" style={{ marginTop: 16 }}>
          <ReportTableCard>
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
          </ReportTableCard>
          <ReportTableCard>
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
          </ReportTableCard>
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
        <ReportTableCard>
          <Table
            rowKey="employee__department_id"
            dataSource={data.breakdown}
            pagination={false}
            columns={[
              { title: 'Department', dataIndex: 'employee__department__name' },
              { title: 'Gross Pay', dataIndex: 'gross_pay' },
              { title: 'Net Pay', dataIndex: 'net_pay' },
            ]}
          />
        </ReportTableCard>
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
        <ReportTableCard>
          <Table
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
        </ReportTableCard>
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
          { key: 'headcount', label: 'Headcount', children: <HeadcountTab isHr={isHr} /> },
          { key: 'leave-utilization', label: 'Leave Utilization', children: <LeaveUtilizationTab isHr={isHr} /> },
          { key: 'turnover', label: 'Turnover', children: <TurnoverTab isHr={isHr} /> },
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
