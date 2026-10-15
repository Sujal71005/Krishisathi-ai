import { Fragment, useEffect, useState } from 'react'
import { Activity, Info, Target } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getConfusionMatrix, getFeatureImportance, getModelMetrics } from '../lib/api'
import { number, percent } from '../lib/format'
import { ChartCard, MetricPill } from '../components/shared/Cards'
import SectionHeader from '../components/shared/SectionHeader'
import { ErrorState, LoadingState } from '../components/shared/States'

export default function ModelPerformance() {
  const [data, setData] = useState(null)
  const [activeClass, setActiveClass] = useState('')
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([getModelMetrics(), getConfusionMatrix(), getFeatureImportance()]).then(([metrics, matrix, importance]) => setData({ metrics: metrics.data, matrix: matrix.data, importance: importance.data })).catch((err) => setError(err?.response?.data?.detail || 'Model analytics could not be loaded.')) }, [])
  if (error) return <><SectionHeader eyebrow="Evaluation lab" title="Model performance" /><ErrorState message={error} /></>
  if (!data) return <LoadingState label="Loading verified evaluation results…" />
  const { metrics, matrix, importance } = data
  const test = metrics.held_out_test
  const comparison = metrics.comparison.map((item) => ({ ...item, label: item.model_name.replace('K-Nearest Neighbors', 'KNN').replace(' Classifier', ''), score: item.cv_macro_f1_mean }))
  const selectedIndex = activeClass ? matrix.labels.indexOf(activeClass) : -1
  return <>
    <SectionHeader eyebrow="Evaluation lab" title="Model performance" description="Everything on this page comes from the saved Phase 2 evaluation metadata. The held-out test set was not used for selection." />
    <div className="metric-strip"><MetricPill label="Selected model" value={metrics.model_name} /><MetricPill label="Accuracy" value={test.accuracy} /><MetricPill label="Macro precision" value={test.macro_precision} /><MetricPill label="Macro recall" value={test.macro_recall} /><MetricPill label="Macro F1" value={test.macro_f1} /></div>
    <div className="content-grid content-grid-main"><ChartCard title="Cross-validation comparison" eyebrow="Mean macro F1"><div className="chart-wrap chart-wrap-medium"><ResponsiveContainer width="100%" height="100%"><BarChart data={comparison} layout="vertical" margin={{ top: 4, right: 18, left: 20, bottom: 4 }}><CartesianGrid horizontal={false} stroke="#e4e9df" /><XAxis type="number" domain={[0.9, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} tick={{ fontSize: 11, fill: '#718074' }} /><YAxis type="category" dataKey="label" width={120} tick={{ fontSize: 11, fill: '#3c5142' }} /><Tooltip formatter={(value) => percent(value)} contentStyle={{ border: '1px solid #dce5d8', borderRadius: 10 }} /><Bar dataKey="score" radius={[0, 6, 6, 0]}>{comparison.map((entry) => <Cell key={entry.model_name} fill={entry.model_name === metrics.model_name ? '#174D35' : '#86A98A'} />)}</Bar></BarChart></ResponsiveContainer></div><div className="selection-note"><Target size={16} /><span>Selected by highest mean macro F1 across {metrics.cross_validation.splits}-fold stratified cross-validation.</span></div></ChartCard><ChartCard title="Feature importance" eyebrow="Selected estimator"><div className="chart-wrap chart-wrap-medium"><ResponsiveContainer width="100%" height="100%"><BarChart data={importance.items} margin={{ top: 8, right: 12, left: -20, bottom: 18 }}><CartesianGrid vertical={false} stroke="#e4e9df" /><XAxis dataKey="feature" tick={{ fontSize: 11, fill: '#718074' }} /><YAxis tick={{ fontSize: 11, fill: '#718074' }} /><Tooltip formatter={(value) => number(value, 4)} contentStyle={{ border: '1px solid #dce5d8', borderRadius: 10 }} /><Bar dataKey="importance" fill="#6b9b76" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div><div className="selection-note"><Info size={16} /><span>Feature importance is provided by the persisted Random Forest estimator and is not causal evidence.</span></div></ChartCard></div>
    <ChartCard title="Confusion matrix" eyebrow="Held-out test set" action={<select className="compact-select" value={activeClass} onChange={(event) => setActiveClass(event.target.value)}><option value="">All classes</option>{matrix.labels.map((label) => <option key={label} value={label}>{label}</option>)}</select>}>
      <div className="matrix-note">Rows are actual classes. Columns are predicted classes. Values come from the saved test evaluation.</div><div className={`matrix-wrap ${activeClass ? 'matrix-focused' : ''}`}><div className="matrix-grid" style={{ '--matrix-size': matrix.labels.length + 1 }}>{['Actual / Predicted', ...matrix.labels].map((label, index) => <span className={`matrix-label ${index === 0 ? 'matrix-corner' : ''}`} key={`h-${label}`}>{index === 0 ? label : label}</span>)}{matrix.matrix.map((row, rowIndex) => <Fragment key={`row-${matrix.labels[rowIndex]}`}><span className={`matrix-label ${selectedIndex === rowIndex ? 'matrix-selected-label' : ''}`}>{matrix.labels[rowIndex]}</span>{row.map((value, colIndex) => <span key={`${rowIndex}-${colIndex}`} className={`matrix-cell ${rowIndex === colIndex ? 'matrix-diagonal' : ''} ${selectedIndex >= 0 && rowIndex !== selectedIndex && colIndex !== selectedIndex ? 'matrix-muted' : ''}`} title={`${matrix.labels[rowIndex]} → ${matrix.labels[colIndex]}: ${value}`}>{value || ''}</span>)}</Fragment>)}</div></div>
    </ChartCard>
  </>
}
