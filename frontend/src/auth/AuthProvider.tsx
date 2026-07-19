import { useQuery, useQueryClient } from '@tanstack/react-query'
import { type ReactNode, useEffect } from 'react'
import { bootstrapCsrf, fetchMe, logout as apiLogout } from '../api/auth'
import { AuthContext } from './AuthContext'

const ME_QUERY_KEY = ['auth', 'me']

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  useEffect(() => {
    void bootstrapCsrf()
  }, [])

  const { data: me, isLoading, refetch } = useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: fetchMe,
    retry: false,
  })

  const logout = async () => {
    await apiLogout()
    queryClient.setQueryData(ME_QUERY_KEY, null)
    queryClient.clear()
  }

  return (
    <AuthContext.Provider value={{ me: me ?? null, isLoading, refetch, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
