import { useEffect, useMemo, useState } from 'react'
import { Download, Eye, Filter, HeartHandshake, Search, Trash2 } from 'lucide-react'
import { deletePrediction, exportHistory, getApiError, getHistory, getPrediction } from '../lib/api'
import { dateTime, number, titleCase } from '../lib/format'
import Badge from '../components/shared/Badge'
import SectionHeader from '../components/shared/SectionHeader'
import { ChartCard } from '../components/shared/Cards'
import { EmptyState, ErrorState, LoadingState } from '../components/shared/States'

export default function HistoryImpact() {
  const [items, setItems] = useState([])
  const [search, setSearch] = useState('')
  const [crop, setCrop] = useState('All crops')
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  async function load() { setLoading(true); try { const { data } = await getHistory({ limit: 200 }); setItems(data.items) } catch (err) { setError(getApiError(err, 'Prediction history is unavailable.')) } finally { setLoading(false) } }
  useEffect(() => { load() }, [])
  const crops = useMemo(() => ['All crops', ...new Set(items.map((item) => item.result?.crop).filter(Boolean))], [items])
  const filtered = items.filter((item) => { const matchesSearch = `${item.result?.crop} ${item.prediction_id} ${JSON.stringify(item.input_features)}`.toLowerCase().includes(search.toLowerCase()); return matchesSearch && (crop === 'All crops' || item.result?.crop === crop) })
  async function showDetails(id) { try { const { data } = await getPrediction(id); setSelected(data) } catch (err) { setError(getApiError(err, 'Could not load prediction details.')) } }
  async function remove(id) { if (!window.confirm('Delete this prediction from local history?')) return; try { await deletePrediction(id); setItems((current) => current.filter((item) => item.prediction_id !== id)); if (selected?.prediction_id === id) setSelected(null) } catch (err) { setError(getApiError(err, 'Could not delete this prediction.')) } }
  async function download() { try { const response = await exportHistory(); const url = URL.createObjectURL(response.data); const link = document.createElement('a'); link.href = url; link.download = 'krishisathi-history.csv'; link.click(); URL.revokeObjectURL(url) } catch (err) { setError(getApiError(err, 'Could not export prediction history.')) } }
  return <>
    <SectionHeader eyebrow="Local history & impact" title="Prediction history and SDG 2" description="Review model-backed recommendations, keep your local history tidy, and connect the work to Zero Hunger." action={<button className="button button-secondary" onClick={download}><Download size={16} /> Export CSV</button>} />
    <div className="sdg-impact"><div className="sdg-impact-mark">2</div><div><span className="card-eyebrow">UN Sustainable Development Goal</span><h2>Zero Hunger</h2><p>KrishiSathi AI supports more informed crop planning by connecting soil and environmental conditions with transparent decision support. These are project indicators, not claims of food-security impact.</p></div><HeartHandshake className="impact-icon" size={42} /></div>
    {error && <ErrorState message={error} />}
    <ChartCard title="Saved recommendations" eyebrow={`${filtered.length} visible records`} action={<div className="history-tools"><div className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search crop or ID" aria-label="Search prediction history" /></div><div className="filter-box"><Filter size={15} /><select value={crop} onChange={(event) => setCrop(event.target.value)} aria-label="Filter by crop">{crops.map((item) => <option key={item}>{item}</option>)}</select></div></div>}>
      {loading ? <LoadingState label="Loading SQLite history…" /> : filtered.length ? <div className="table-scroll"><table className="history-table"><thead><tr><th>ID</th><th>Recommendation</th><th>Created</th><th>Inputs</th><th>Score</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{filtered.map((item) => <tr key={item.prediction_id}><td className="muted-cell">#{item.prediction_id}</td><td><div className="table-crop"><span className="crop-avatar">{item.result.crop?.slice(0, 1).toUpperCase()}</span><strong>{titleCase(item.result.crop)}</strong></div></td><td>{dateTime(item.timestamp)}</td><td><div className="input-summary">{Object.entries(item.input_features).slice(0, 3).map(([key, value]) => <span key={key}>{key}: {number(value)}</span>)}<small>+4 fields</small></div></td><td><Badge>{Math.round((item.result.candidates?.[0]?.score || 0) * 100)}%</Badge></td><td><div className="table-actions"><button className="icon-button small" onClick={() => showDetails(item.prediction_id)} aria-label={`View prediction ${item.prediction_id}`}><Eye size={16} /></button><button className="icon-button small danger-icon" onClick={() => remove(item.prediction_id)} aria-label={`Delete prediction ${item.prediction_id}`}><Trash2 size={16} /></button></div></td></tr>)}</tbody></table></div> : <EmptyState message="No saved predictions match these filters." />}
    </ChartCard>
    {selected && <div className="detail-drawer"><div><span className="card-eyebrow">Prediction #{selected.prediction_id}</span><h2>{titleCase(selected.result?.crop)}</h2><p>{dateTime(selected.timestamp)} · {selected.model_name} v{selected.model_version}</p></div><div className="detail-grid">{Object.entries(selected.input_features || {}).map(([key, value]) => <div key={key}><span>{key}</span><strong>{number(value)}</strong></div>)}</div><button className="button button-ghost" onClick={() => setSelected(null)}>Close details</button></div>}
  </>
}
