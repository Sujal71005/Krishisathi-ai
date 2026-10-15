import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import Overview from './pages/Overview'
import CropPredictor from './pages/CropPredictor'
import ModelPerformance from './pages/ModelPerformance'
import Insights from './pages/Insights'
import HistoryImpact from './pages/HistoryImpact'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/predictor" element={<CropPredictor />} />
        <Route path="/model-performance" element={<ModelPerformance />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/history" element={<HistoryImpact />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
