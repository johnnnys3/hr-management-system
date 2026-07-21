import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { createReportExport, getReportExport } from '../../api/reports'

export function useReportExport(reportType: string) {
  const queryClient = useQueryClient()
  const [jobId, setJobId] = useState<number | null>(null)

  const createMutation = useMutation({
    mutationFn: (params: Record<string, unknown>) => createReportExport(reportType, params),
    onSuccess: (record) => setJobId(record.id),
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Failed to start export.'),
  })

  const { data: job } = useQuery({
    queryKey: ['reports', 'export', jobId],
    queryFn: () => getReportExport(jobId as number),
    enabled: jobId !== null,
    refetchInterval: (query) => (query.state.data?.status === 'pending' ? 2000 : false),
  })

  const reset = () => {
    queryClient.removeQueries({ queryKey: ['reports', 'export', jobId] })
    setJobId(null)
  }

  return { startExport: createMutation.mutate, isStarting: createMutation.isPending, job, reset }
}
