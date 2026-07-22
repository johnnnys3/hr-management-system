const GREEN = '#2F6B4F'

export interface Stat {
  label: string
  value: string | number
  accent?: boolean
}

export function StatStrip({ stats }: { stats: Stat[] }) {
  if (stats.length === 0) return null
  return (
    <div style={{ display: 'flex', borderTop: '1px solid #ececec', borderBottom: '1px solid #ececec', marginBottom: 24 }}>
      {stats.map((stat, i) => (
        <div
          key={stat.label}
          style={{ flex: 1, padding: '18px 24px', borderRight: i === stats.length - 1 ? 'none' : '1px solid #ececec' }}
        >
          <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.4)', marginBottom: 4 }}>{stat.label}</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: stat.accent ? GREEN : '#111' }}>{stat.value}</div>
        </div>
      ))}
    </div>
  )
}
