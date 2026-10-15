import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  useEffect(() => setMobileOpen(false), [location.pathname])

  return (
    <div className="app-shell">
      <Sidebar collapsed={collapsed} mobileOpen={mobileOpen} onToggle={() => setCollapsed((value) => !value)} onClose={() => setMobileOpen(false)} />
      <div className={`main-shell ${collapsed ? 'main-shell-collapsed' : ''}`}>
        <Topbar onMenu={() => setMobileOpen(true)} />
        <main className="page-container"><Outlet /></main>
      </div>
    </div>
  )
}
