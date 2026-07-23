import { useQuery } from '@tanstack/react-query'
import { listPayGrades, listSalaryStructures } from '../../api/compensation'

export function useSalaryStructures(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['compensation', 'salary-structures'],
    queryFn: listSalaryStructures,
    enabled: options?.enabled ?? true,
  })
}

export function usePayGrades(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['compensation', 'pay-grades'],
    queryFn: listPayGrades,
    enabled: options?.enabled ?? true,
  })
}
