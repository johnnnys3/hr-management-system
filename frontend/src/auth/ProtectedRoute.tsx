import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

const SECOND_FACTOR_ENROLL_PATH = '/second-factor/enroll'

export function ProtectedRoute({
  requireGroup,
  allowManager,
}: {
  requireGroup?: string | string[]
  /** Also admit a caller where `me.is_manager` is true, alongside `requireGroup` —
   * Manager is a derived role (`docs/07-iam-rbac.md` §3), never a Django group, so
   * it can't be expressed through `requireGroup` alone. */
  allowManager?: boolean
}) {
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
  const inRequiredGroup = requiredGroups ? requiredGroups.some((group) => me.groups.includes(group)) : true
  if (requiredGroups && !inRequiredGroup && !(allowManager && me.is_manager)) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
