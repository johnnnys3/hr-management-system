import { Alert, Button, Space } from 'antd'
import { useReportExport } from './useReportExport'

export function ExportControl({ reportType, params }: { reportType: string; params: Record<string, unknown> }) {
  const { startExport, isStarting, job, reset } = useReportExport(reportType)

  if (job?.status === 'complete' && job.download_url) {
    return (
      <Space>
        <a href={job.download_url} target="_blank" rel="noreferrer">
          Download
        </a>
        <Button size="small" onClick={reset}>
          Export Again
        </Button>
      </Space>
    )
  }

  if (job?.status === 'failed') {
    return (
      <Space>
        <Alert type="error" showIcon message={job.failed_reason ?? 'Export failed.'} />
        <Button size="small" onClick={reset}>
          Retry
        </Button>
      </Space>
    )
  }

  return (
    <Button loading={isStarting || job?.status === 'pending'} onClick={() => startExport(params)}>
      Export
    </Button>
  )
}
