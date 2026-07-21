import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import { router } from './routes'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ConfigProvider
          theme={{
            token: {
              colorPrimary: '#111111',
              colorBgLayout: '#F7F3EC',
              borderRadius: 14,
              fontFamily: 'inherit',
            },
          }}
        >
          <RouterProvider router={router} />
        </ConfigProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
