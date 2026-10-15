import { AlertTriangle, LoaderCircle, SearchX } from 'lucide-react'

export function LoadingState({ label = 'Loading live data…' }) {
  return <div className="state-panel"><LoaderCircle className="spin" size={22} /><span>{label}</span></div>
}

export function ErrorState({ message = 'The backend is unavailable.' }) {
  return <div className="state-panel state-error"><AlertTriangle size={21} /><span>{message}</span></div>
}

export function EmptyState({ message = 'No records to display yet.' }) {
  return <div className="state-panel"><SearchX size={21} /><span>{message}</span></div>
}
