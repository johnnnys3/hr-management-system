import { useEffect, useState } from 'react'

function App() {
  const [health, setHealth] = useState<string>('checking...')

  useEffect(() => {
    fetch('/api/health/')
      .then((res) => res.json())
      .then((data) => setHealth(data.status ?? 'unknown'))
      .catch(() => setHealth('unreachable'))
  }, [])

  return (
    <main>
      <h1>HRMS</h1>
      <p>Environment Setup placeholder. This page exists only to prove the deployment composition.</p>
      <p>
        API health via same-origin <code>/api/health/</code>: <strong>{health}</strong>
      </p>
    </main>
  )
}

export default App
