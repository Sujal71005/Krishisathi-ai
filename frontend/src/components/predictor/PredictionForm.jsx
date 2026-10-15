import { useState } from 'react'
import { RotateCcw, Sparkles } from 'lucide-react'

export const defaultValues = { N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: '' }
const fields = [
  ['N', 'Nitrogen', 'Soil nutrient value', '0–1000'], ['P', 'Phosphorus', 'Soil nutrient value', '0–1000'], ['K', 'Potassium', 'Soil nutrient value', '0–1000'],
  ['temperature', 'Temperature', 'Degrees Celsius', '−50–70 °C'], ['humidity', 'Humidity', 'Relative humidity', '0–100 %'], ['ph', 'Soil pH', 'Acidity / alkalinity', '0–14'], ['rainfall', 'Rainfall', 'Observed rainfall', '0–10000'],
]

export default function PredictionForm({ onSubmit, loading }) {
  const [values, setValues] = useState(defaultValues)
  const [error, setError] = useState('')
  function update(name, value) { setValues((current) => ({ ...current, [name]: value })); setError('') }
  function submit(event) {
    event.preventDefault()
    if (Object.values(values).some((value) => value === '' || !Number.isFinite(Number(value)))) { setError('Complete all seven fields with finite numeric values.'); return }
    onSubmit(Object.fromEntries(Object.entries(values).map(([key, value]) => [key, Number(value)])))
  }
  function reset() { setValues(defaultValues); setError('') }
  return <form onSubmit={submit} className="predictor-form"><div className="form-grid">{fields.map(([name, label, hint, range]) => <label className="form-field" key={name}><span className="form-label"><b>{label}</b><code>{name}</code></span><span className="form-hint">{hint}</span><input type="number" step="any" value={values[name]} onChange={(event) => update(name, event.target.value)} placeholder="Enter value" required aria-label={label} /><small>Supported: {range}</small></label>)}</div>{error && <p className="form-error">{error}</p>}<div className="form-actions"><button type="button" className="button button-ghost" onClick={reset}><RotateCcw size={16} /> Reset</button><button type="submit" className="button button-primary" disabled={loading}><Sparkles size={17} /> {loading ? 'Analysing field…' : 'Recommend crops'}</button></div></form>
}
