import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

const SECOND_FACTOR_ENROLL_PATH = '/second-factor/enroll'

export function ProtectedRoute({ requireGroup }: { requireGroup?: string }) {
  const { me, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return null
  }
  if (!me) {
    return <Navigate to="/login" replace />
  }
  if (me.second_factor_enrollment_pending && location.pathname !== SECOND_FACTOR_ENROLL_PATH) {
    return <Navigate to={SECOND_FACTOR_ENROLL_PATH} replace />
  }
  if (requireGroup && !me.groups.includes(requireGroup)) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
