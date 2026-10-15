import { ArrowUpRight, BarChart3, Database, Leaf, Target, Zap } from 'lucide-react'
import { percent } from '../../lib/format'

const icons = { records: Database, crops: Leaf, accuracy: Target, f1: Zap }

export function StatCard({ label, value, detail, type = 'records', accent = false }) {
  const Icon = icons[type] || BarChart3
  return <div className={`stat-card ${accent ? 'stat-card-accent' : ''}`}><div className="stat-icon"><Icon size={19} /></div><div className="stat-label">{label}</div><div className="stat-value">{value}</div>{detail && <div className="stat-detail">{detail}</div>}<ArrowUpRight className="stat-arrow" size={17} /></div>
}

export function ChartCard({ title, eyebrow, action, children, className = '' }) {
  return <section className={`card chart-card ${className}`}><div className="card-heading"><div><span className="card-eyebrow">{eyebrow}</span><h2>{title}</h2></div>{action}</div>{children}</section>
}

export function MetricPill({ label, value }) {
  return <div className="metric-pill"><span>{label}</span><strong>{typeof value === 'number' && value <= 1 ? percent(value) : value}</strong></div>
}
