import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './layout/AppLayout'
import { MinimalLayout } from './layout/MinimalLayout'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { DashboardPage } from './modules/dashboard/DashboardPage'
import { LoginPage } from './modules/auth/LoginPage'
import { PasswordResetPage } from './modules/auth/PasswordResetPage'
import { SecondFactorEnrollPage } from './modules/auth/SecondFactorEnrollPage'
import { SecondFactorRecoveryPage } from './modules/auth/SecondFactorRecoveryPage'
import { RoleGrantRequestsPage } from './modules/rbac/RoleGrantRequestsPage'
import { UserManagementPage } from './modules/rbac/UserManagementPage'
import { DepartmentsPage } from './modules/departments/DepartmentsPage'
import { EmployeesPage } from './modules/employees/EmployeesPage'
import { EmployeeDetailPage } from './modules/employees/EmployeeDetailPage'
import { MyProfilePage } from './modules/employees/MyProfilePage'
import { MyTeamPage } from './modules/employees/MyTeamPage'
import { RecruitmentPage } from './modules/recruitment/RecruitmentPage'
import { CandidateDetailPage } from './modules/recruitment/CandidateDetailPage'
import { OnboardingPage } from './modules/onboarding/OnboardingPage'
import { OnboardingChecklistPage } from './modules/onboarding/OnboardingChecklistPage'
import { NotificationsPage } from './modules/notifications/NotificationsPage'
import { LeavePage } from './modules/leave/LeavePage'
import { AuditLogPage } from './modules/audit/AuditLogPage'
import { ReportsPage } from './modules/reports/ReportsPage'
import { CompensationPage } from './modules/compensation/CompensationPage'
import { PayrollPage } from './modules/payroll/PayrollPage'
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
            element: <MinimalLayout />,
            children: [
              { path: '/second-factor/enroll', element: <SecondFactorEnrollPage /> },
              { path: '/second-factor/recovery', element: <SecondFactorRecoveryPage /> },
            ],
          },
          {
            element: <AppLayout />,
            children: [
              { path: '/', element: <DashboardPage /> },
              { path: '/notifications', element: <NotificationsPage /> },
              { path: '/leave', element: <LeavePage /> },
              { path: '/my-profile', element: <MyProfilePage /> },
              { path: '/my-team', element: <MyTeamPage /> },
              { path: '/role-grant-requests', element: <RoleGrantRequestsPage /> },
              {
                element: (
                  <ProtectedRoute
                    requireGroup={['HR Administrator', 'HR Officer', 'Recruiter', 'Payroll Officer']}
                  />
                ),
                children: [{ path: '/departments', element: <DepartmentsPage /> }],
              },
              {
                element: <ProtectedRoute requireGroup={['HR Administrator', 'HR Officer']} />,
                children: [
                  { path: '/employees', element: <EmployeesPage /> },
                  { path: '/employees/:id', element: <EmployeeDetailPage /> },
                ],
              },
              {
                element: <ProtectedRoute requireGroup={['Recruiter', 'HR Administrator', 'HR Officer']} />,
                children: [
                  { path: '/recruitment', element: <RecruitmentPage /> },
                  {
                    element: <ProtectedRoute requireGroup={['Recruiter', 'HR Officer']} />,
                    children: [{ path: '/recruitment/candidates/:id', element: <CandidateDetailPage /> }],
                  },
                ],
              },
              {
                element: <ProtectedRoute requireGroup={['HR Officer', 'HR Administrator', 'Recruiter']} />,
                children: [{ path: '/onboarding/:id', element: <OnboardingChecklistPage /> }],
              },
              {
                element: <ProtectedRoute requireGroup="HR Officer" />,
                children: [{ path: '/onboarding', element: <OnboardingPage /> }],
              },
              {
                element: <ProtectedRoute requireGroup="System Administrator" />,
                children: [
                  { path: '/users', element: <UserManagementPage /> },
                  { path: '/audit-log', element: <AuditLogPage /> },
                ],
              },
              {
                element: (
                  <ProtectedRoute
                    requireGroup={['HR Administrator', 'HR Officer', 'Payroll Officer', 'Executive']}
                    allowManager
                  />
                ),
                children: [{ path: '/reports', element: <ReportsPage /> }],
              },
              {
                element: <ProtectedRoute requireGroup={['HR Administrator', 'HR Officer', 'Payroll Officer']} />,
                children: [{ path: '/compensation', element: <CompensationPage /> }],
              },
              {
                element: <ProtectedRoute requireGroup={['Payroll Officer', 'HR Administrator']} />,
                children: [{ path: '/payroll', element: <PayrollPage /> }],
              },
            ],
          },
        ],
      },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
