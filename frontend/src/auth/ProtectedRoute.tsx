import { Result } from 'antd'
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
    return <Result status="403" title="403" subTitle="You are not authorized to access this page." />
  }
  return <Outlet />
}
