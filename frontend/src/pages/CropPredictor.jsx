import { useEffect, useState } from 'react'
import { Info, ShieldCheck } from 'lucide-react'
import { createPrediction, getFeatureStatistics, getApiError } from '../lib/api'
import PredictionForm from '../components/predictor/PredictionForm'
import CropResultCard from '../components/predictor/CropResultCard'
import SectionHeader from '../components/shared/SectionHeader'
import { ErrorState, LoadingState } from '../components/shared/States'

export default function CropPredictor() {
  const [statistics, setStatistics] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { getFeatureStatistics().then(({ data }) => setStatistics(data)).catch(() => {}) }, [])
  async function submit(payload) {
    setLoading(true); setError('')
    try { const { data } = await createPrediction(payload); setResult(data) } catch (err) { setError(getApiError(err, 'The recommendation service could not complete this prediction.')) } finally { setLoading(false) }
  }
  return <>
    <SectionHeader eyebrow="Decision support" title="Find a crop fit for your field" description="Use measured soil and environmental values. The saved Random Forest model returns a recommendation and up to three candidates." />
    <div className="predictor-layout"><section className="card predictor-card"><div className="card-heading"><div><span className="card-eyebrow">Field conditions</span><h2>Tell us about your plot</h2></div><ShieldCheck className="heading-icon" size={22} /></div><PredictionForm onSubmit={submit} loading={loading} /><div className="form-footnote"><Info size={15} /><span>Values outside the training dataset range are accepted within supported limits and clearly flagged in the result.</span></div></section><section className="result-panel"><CropResultCard result={result} statistics={statistics} />{loading && <LoadingState label="Running the saved model…" />}{error && <ErrorState message={error} />}</section></div>
  </>
}
