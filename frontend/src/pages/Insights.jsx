import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getCropDistribution, getFeatureStatistics } from '../lib/api'
import { number, titleCase } from '../lib/format'
import { ChartCard } from '../components/shared/Cards'
import SectionHeader from '../components/shared/SectionHeader'
import { ErrorState, LoadingState } from '../components/shared/States'

const colors = { N: '#174D35', P: '#397453', K: '#6b9b76', temperature: '#d8955d', humidity: '#5f96ad', ph: '#9872a8', rainfall: '#5b83b0' }

export default function Insights() {
  const [data, setData] = useState(null)
  const [selectedCrop, setSelectedCrop] = useState('All crops')
  const [error, setError] = useState('')
  useEffect(() => {
    let cancelled = false

    async function fetchData() {
      try {
        const [stats, crops] = await Promise.all([getFeatureStatistics(), getCropDistribution()])
        if (!cancelled) {
          setData({ stats: stats.data, crops: crops.data })
        }
      } catch {
        if (!cancelled) {
          setError('Could not load live feature insights.')
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, [])
  if (error) return <><SectionHeader eyebrow="Field intelligence" title="Soil & climate insights" /><ErrorState message={error} /></>
  if (!data) return <LoadingState label="Loading feature distributions…" />
  const selected = selectedCrop === 'All crops' ? data.crops.items : data.crops.items.filter((item) => item.crop === selectedCrop)
  return <>
    <SectionHeader eyebrow="Field intelligence" title="Soil & climate insights" description="A transparent view of the real inputs represented in the training dataset. Use these ranges as context, not universal agronomic limits." action={<select className="filter-select" value={selectedCrop} onChange={(event) => setSelectedCrop(event.target.value)}><option>All crops</option>{data.crops.items.map((crop) => <option key={crop.crop}>{crop.crop}</option>)}</select>} />
    <div className="insight-banner"><div className="banner-mark">{selectedCrop === 'All crops' ? data.crops.items.length : selected.length}</div><div><strong>{selectedCrop === 'All crops' ? 'Balanced crop coverage' : `${titleCase(selectedCrop)} selected`}</strong><p>{selectedCrop === 'All crops' ? 'The benchmark contains 100 records for each of its 22 crop classes.' : 'The backend currently exposes overall feature statistics; crop-specific feature distributions are not available.'}</p></div></div>
    <div className="insight-chart-grid">{data.stats.items.map((item) => <ChartCard key={item.feature} title={item.feature} eyebrow="Distribution summary"><div className="feature-range"><div><span>Mean</span><strong>{number(item.mean)}</strong></div><div><span>Median</span><strong>{number(item.median)}</strong></div><div><span>Range</span><strong>{number(item.min)} — {number(item.max)}</strong></div></div><div className="range-track"><i style={{ left: '0%', width: '100%', background: colors[item.feature] || '#174D35' }} /></div><div className="range-labels"><span>Min {number(item.min)}</span><span>Max {number(item.max)}</span></div></ChartCard>)}</div>
    <ChartCard title="Feature means at a glance" eyebrow="Seven model inputs"><div className="chart-wrap chart-wrap-medium"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.stats.items} margin={{ top: 8, right: 8, left: -16, bottom: 8 }}><CartesianGrid vertical={false} stroke="#e4e9df" /><XAxis dataKey="feature" tick={{ fontSize: 11, fill: '#718074' }} /><YAxis tick={{ fontSize: 11, fill: '#718074' }} /><Tooltip formatter={(value) => number(value)} contentStyle={{ border: '1px solid #dce5d8', borderRadius: 10 }} /><Bar dataKey="mean" radius={[5, 5, 0, 0]}>{data.stats.items.map((item) => <Cell key={item.feature} fill={colors[item.feature] || '#174D35'} />)}</Bar></BarChart></ResponsiveContainer></div></ChartCard>
    <div className="two-column-note"><ChartCard title="Data-quality notes" eyebrow="What the audit confirms"><ul className="clean-list"><li><strong>2,200</strong> complete records are available.</li><li>There are no missing values or duplicate rows.</li><li>All 22 crop classes are equally represented.</li><li>Observed ranges support transparent input warnings in the predictor.</li></ul></ChartCard><ChartCard title="Correlation view" eyebrow="Backend capability"><div className="unavailable-panel"><span>Not exposed by the current backend</span><p>No correlation endpoint exists yet, so no correlation values are invented here.</p></div></ChartCard></div>
  </>
}
