import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CloudRain, Droplets, ExternalLink, Thermometer, Wind } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getCropDistribution, getFeatureStatistics, getHistory, getModelMetrics, getSummary } from '../lib/api'
import { dateTime, number, percent, titleCase } from '../lib/format'
import { ChartCard, StatCard } from '../components/shared/Cards'
import Badge from '../components/shared/Badge'
import SectionHeader from '../components/shared/SectionHeader'
import { EmptyState, ErrorState, LoadingState } from '../components/shared/States'

const chartColors = ['#174D35', '#397453', '#6b9b76', '#86A98A', '#abc49d', '#C8E66B']

export default function Overview() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    Promise.all([getSummary(), getCropDistribution(), getFeatureStatistics(), getModelMetrics(), getHistory({ limit: 5 })])
      .then(([summary, distribution, statistics, metrics, history]) => setData({ summary: summary.data, distribution: distribution.data, statistics: statistics.data, metrics: metrics.data, history: history.data }))
      .catch((err) => setError(err?.response?.data?.detail || 'Could not connect to the live backend. Start FastAPI to load the workspace.'))
  }, [])

  if (error) return <><SectionHeader eyebrow="Workspace overview" title="Welcome to your field intelligence" description="The dashboard is connected to real dataset and model endpoints." /><ErrorState message={error} /></>
  if (!data) return <LoadingState label="Gathering dataset, model and history insights…" />

  const { summary, distribution, statistics, metrics, history } = data
  const featureMap = Object.fromEntries(statistics.items.map((item) => [item.feature, item]))
  const insightCards = [
    { label: 'Temperature', value: `${number(featureMap.temperature?.mean)}°C`, icon: Thermometer, note: 'dataset mean' },
    { label: 'Humidity', value: `${number(featureMap.humidity?.mean)}%`, icon: Droplets, note: 'dataset mean' },
    { label: 'Rainfall', value: `${number(featureMap.rainfall?.mean)} mm`, icon: CloudRain, note: 'dataset mean' },
    { label: 'Soil pH', value: number(featureMap.ph?.mean), icon: Wind, note: 'dataset mean' },
  ]
  return <>
    <SectionHeader eyebrow="Live workspace" title="Welcome to your field intelligence" description="A compact view of the data, model and recommendations supporting smarter crop decisions." action={<Link className="button button-secondary" to="/predictor">New recommendation <ArrowRight size={16} /></Link>} />
    <div className="stat-grid stat-grid-four">
      <StatCard label="Dataset records" value={summary.dataset_rows.toLocaleString()} detail="verified training rows" type="records" />
      <StatCard label="Crop classes" value={summary.crop_class_count} detail="balanced labels" type="crops" />
      <StatCard label="Model accuracy" value={percent(metrics.held_out_test.accuracy)} detail="held-out test set" type="accuracy" accent />
      <StatCard label="Macro F1 score" value={percent(metrics.held_out_test.macro_f1)} detail="held-out test set" type="f1" />
    </div>
    <div className="content-grid content-grid-main">
      <ChartCard title="Crop distribution" eyebrow="Training dataset" action={<Link className="text-link" to="/insights">Explore insights <ExternalLink size={14} /></Link>}>
        <div className="chart-wrap chart-wrap-distribution"><ResponsiveContainer width="100%" height="100%"><BarChart data={distribution.items} margin={{ top: 8, right: 8, left: -18, bottom: 42 }}><CartesianGrid vertical={false} stroke="#e4e9df" /><XAxis dataKey="crop" angle={-42} textAnchor="end" interval={0} tick={{ fontSize: 10, fill: '#718074' }} height={70} /><YAxis tick={{ fontSize: 11, fill: '#718074' }} /><Tooltip cursor={{ fill: '#f0f4eb' }} contentStyle={{ border: '1px solid #dce5d8', borderRadius: 10, boxShadow: '0 8px 24px #174d3514' }} /><Bar dataKey="count" radius={[5, 5, 0, 0]}>{distribution.items.map((entry, index) => <Cell key={entry.crop} fill={chartColors[index % chartColors.length]} />)}</Bar></BarChart></ResponsiveContainer></div>
      </ChartCard>
      <ChartCard title="Environmental snapshot" eyebrow="Dataset averages" action={<Link className="text-link" to="/insights">View all <ArrowRight size={14} /></Link>}>
        <div className="insight-list">{insightCards.map(({ label, value, icon: Icon, note }) => <div className="insight-row" key={label}><span className="insight-icon"><Icon size={17} /></span><div><strong>{label}</strong><small>{note}</small></div><b>{value}</b></div>)}</div>
        <div className="callout callout-soft"><span className="callout-dot" /><div><strong>Balanced benchmark</strong><p>Every crop class contributes 100 rows to the dataset.</p></div></div>
      </ChartCard>
    </div>
    <div className="content-grid content-grid-bottom">
      <ChartCard title="Feature statistics" eyebrow="Seven model inputs"><div className="mini-stat-grid">{statistics.items.map((item) => <div className="mini-stat" key={item.feature}><span>{item.feature}</span><strong>{number(item.mean)}</strong><small>{number(item.min)} — {number(item.max)}</small></div>)}</div></ChartCard>
      <ChartCard title="Recent predictions" eyebrow="SQLite history" action={<Link className="text-link" to="/history">View history <ArrowRight size={14} /></Link>}>
        {history.items.length ? <div className="recent-list">{history.items.map((item) => <div className="recent-row" key={item.prediction_id}><div className="recent-crop"><span className="crop-avatar">{item.result.crop?.slice(0, 1).toUpperCase()}</span><div><strong>{titleCase(item.result.crop)}</strong><small>{dateTime(item.timestamp)}</small></div></div><Badge>{percent(item.result.candidates?.[0]?.score || 0)} score</Badge></div>)}</div> : <EmptyState message="Predictions will appear here after your first recommendation." />}
      </ChartCard>
    </div>
  </>
}
