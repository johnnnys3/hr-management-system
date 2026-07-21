import { useQuery } from '@tanstack/react-query'
import { Alert, Select, Table, Tag, Typography } from 'antd'
import { useState } from 'react'
import { listAuditLog } from '../../api/audit'
import { ApiError } from '../../api/client'
import type { AuditLogEntry } from '../../api/types'
import { AUDIT_LOG_CATEGORY_LABELS } from './constants'

export function AuditLogPage() {
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [page, setPage] = useState(1)

  const { data, isLoading, error } = useQuery({
    queryKey: ['audit', 'log', category, page],
    queryFn: () => listAuditLog({ category, page }),
  })

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load the audit log"
        description={error instanceof ApiError ? error.message : 'An error occurred while loading the audit log.'}
      />
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Audit Log
        </Typography.Title>
        <Select
          allowClear
          placeholder="Filter by category"
          style={{ width: 220 }}
          value={category}
          onChange={(value) => {
            setCategory(value)
            setPage(1)
          }}
          options={Object.entries(AUDIT_LOG_CATEGORY_LABELS).map(([value, label]) => ({ value, label }))}
        />
      </div>
      <Table<AuditLogEntry>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.results ?? []}
        pagination={{
          current: page,
          pageSize: 50,
          total: data?.count ?? 0,
          onChange: setPage,
        }}
        columns={[
          { title: 'Occurred At', dataIndex: 'occurred_at', render: (v: string) => new Date(v).toLocaleString() },
          {
            title: 'Category',
            dataIndex: 'category',
            render: (c: string) => <Tag>{AUDIT_LOG_CATEGORY_LABELS[c] ?? c}</Tag>,
          },
          { title: 'Action', dataIndex: 'action' },
          {
            title: 'Target',
            render: (_: unknown, record: AuditLogEntry) =>
              record.target_type
                ? `${record.target_type}${record.target_id == null ? '' : ` #${record.target_id}`}`
                : '—',
          },
          { title: 'Actor', dataIndex: 'actor', render: (v: number | null) => v ?? '—' },
        ]}
        expandable={{
          rowExpandable: (record) => !!record.detail,
          expandedRowRender: (record) => <pre>{JSON.stringify(record.detail, null, 2)}</pre>,
        }}
      />
    </div>
  )
}
