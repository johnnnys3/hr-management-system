import { useQuery } from '@tanstack/react-query'
import { listDepartments, listJobTitles } from '../../api/departments'

export function useDepartments(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['departments', 'departments'],
    queryFn: listDepartments,
    enabled: options?.enabled ?? true,
  })
}

export function useJobTitles() {
  return useQuery({ queryKey: ['departments', 'job-titles'], queryFn: listJobTitles })
}
