import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

const SECOND_FACTOR_ENROLL_PATH = '/second-factor/enroll'

export function ProtectedRoute({ requireGroup }: { requireGroup?: string | string[] }) {
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
  const requiredGroups = requireGroup ? (Array.isArray(requireGroup) ? requireGroup : [requireGroup]) : null
  if (requiredGroups && !requiredGroups.some((group) => me.groups.includes(group))) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
