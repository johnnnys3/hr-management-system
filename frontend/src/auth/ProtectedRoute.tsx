import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function ProtectedRoute({ requireGroup }: { requireGroup?: string }) {
  const { me, isLoading } = useAuth()

  if (isLoading) {
    return null
  }
  if (!me) {
    return <Navigate to="/login" replace />
  }
  if (requireGroup && !me.groups.includes(requireGroup)) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
