import { Menu, Search, Sprout } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const titles = {
  '/': ['Overview', 'A clear view of your farming intelligence.'],
  '/predictor': ['Crop Predictor', 'Turn field conditions into a thoughtful crop recommendation.'],
  '/model-performance': ['Model Performance', 'Understand how the recommendation engine performs.'],
  '/insights': ['Soil & Climate Insights', 'Explore the conditions represented in the training dataset.'],
  '/history': ['History & SDG 2', 'Track recommendations and the impact behind the project.'],
}

export default function Topbar({ onMenu }) {
  const location = useLocation()
  const [title, subtitle] = titles[location.pathname] || titles['/']
  return (
    <header className="topbar">
      <button className="icon-button mobile-menu" onClick={onMenu} aria-label="Open navigation"><Menu size={21} /></button>
      <div className="topbar-heading"><span className="eyebrow">KrishiSathi AI / {title}</span><h1>{title}</h1><p>{subtitle}</p></div>
      <div className="topbar-actions"><button className="icon-button" aria-label="Search"><Search size={19} /></button><div className="user-chip"><span className="avatar"><Sprout size={16} /></span><span className="user-name">Field workspace</span></div></div>
    </header>
  )
}
