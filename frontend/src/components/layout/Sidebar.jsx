import { NavLink } from 'react-router-dom'
import { BarChart3, ChevronLeft, ChevronRight, CircleGauge, History, Leaf, LineChart, Sprout, X } from 'lucide-react'

const links = [
  { to: '/', label: 'Overview', icon: CircleGauge },
  { to: '/predictor', label: 'Crop Predictor', icon: Sprout },
  { to: '/model-performance', label: 'Model Performance', icon: BarChart3 },
  { to: '/insights', label: 'Soil & Climate', icon: LineChart },
  { to: '/history', label: 'History & SDG 2', icon: History },
]

export default function Sidebar({ collapsed, mobileOpen, onToggle, onClose }) {
  return (
    <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''} ${mobileOpen ? 'sidebar-mobile-open' : ''}`}>
      <div className="brand-block">
        <div className="brand-mark"><Leaf size={21} strokeWidth={2.4} /></div>
        <div className="brand-copy"><strong>KrishiSathi</strong><span>AI</span><small>Smart farming intelligence</small></div>
        <button className="icon-button sidebar-close" onClick={onClose} aria-label="Close navigation"><X size={18} /></button>
      </div>
      <div className="sidebar-divider" />
      <nav className="sidebar-nav" aria-label="Primary navigation">
        <p className="nav-label">Workspace</p>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`} title={collapsed ? label : undefined}>
            <Icon size={19} /><span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="sdg-badge"><span>SDG</span><strong>2</strong><small>Zero Hunger</small></div>
        {!collapsed && <p>Smarter crop decisions.<br />More sustainable farming.</p>}
      </div>
      <button className="collapse-button" onClick={onToggle} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
        {collapsed ? <ChevronRight size={18} /> : <><ChevronLeft size={18} /><span>Collapse menu</span></>}
      </button>
    </aside>
  )
}
