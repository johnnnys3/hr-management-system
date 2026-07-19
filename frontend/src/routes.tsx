import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './layout/AppLayout'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { HomePage } from './modules/auth/HomePage'
import { LoginPage } from './modules/auth/LoginPage'
import { PasswordResetPage } from './modules/auth/PasswordResetPage'
import { SecondFactorEnrollPage } from './modules/auth/SecondFactorEnrollPage'
import { SecondFactorRecoveryPage } from './modules/auth/SecondFactorRecoveryPage'
import { RoleGrantRequestsPage } from './modules/rbac/RoleGrantRequestsPage'
import { UserManagementPage } from './modules/rbac/UserManagementPage'
import { RouteErrorBoundary } from './routes/RouteErrorBoundary'

export const router = createBrowserRouter([
  {
    errorElement: <RouteErrorBoundary />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/password-reset', element: <PasswordResetPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          {
            element: <AppLayout />,
            children: [
              { path: '/', element: <HomePage /> },
              { path: '/role-grant-requests', element: <RoleGrantRequestsPage /> },
              { path: '/second-factor/enroll', element: <SecondFactorEnrollPage /> },
              { path: '/second-factor/recovery', element: <SecondFactorRecoveryPage /> },
              {
                element: <ProtectedRoute requireGroup="System Administrator" />,
                children: [{ path: '/users', element: <UserManagementPage /> }],
              },
            ],
          },
        ],
      },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
