import { Button, Result } from 'antd'
import { useNavigate, useRouteError } from 'react-router-dom'

export function RouteErrorBoundary() {
  const error = useRouteError()
  const navigate = useNavigate()
  console.error(error)

  return (
    <Result
      status="500"
      title="Something went wrong"
      subTitle="An unexpected error occurred. You can try going back to the home page."
      extra={
        <Button type="primary" onClick={() => navigate('/', { replace: true })}>
          Back to Home
        </Button>
      }
    />
  )
}
