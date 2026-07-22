import { Outlet } from 'react-router-dom'

export function MinimalLayout() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#fff' }}>
      <div style={{ display: 'flex', alignItems: 'center', padding: '0 40px', height: 64, borderBottom: '1px solid #ececec' }}>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#111' }}>HRMS</div>
      </div>
      <Outlet />
    </div>
  )
}
