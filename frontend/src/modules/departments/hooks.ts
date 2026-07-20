import { useQuery } from '@tanstack/react-query'
import { listDepartments, listJobTitles } from '../../api/departments'

export function useDepartments() {
  return useQuery({ queryKey: ['departments', 'departments'], queryFn: listDepartments })
}

export function useJobTitles() {
  return useQuery({ queryKey: ['departments', 'job-titles'], queryFn: listJobTitles })
}
