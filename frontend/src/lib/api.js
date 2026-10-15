import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

export const getHealth = () => api.get('/health')
export const getMetadata = () => api.get('/metadata')
export const getSummary = () => api.get('/dashboard/summary')
export const getCropDistribution = () => api.get('/dashboard/crop-distribution')
export const getFeatureStatistics = () => api.get('/dashboard/feature-statistics')
export const getModelMetrics = () => api.get('/dashboard/model-metrics')
export const getConfusionMatrix = () => api.get('/dashboard/confusion-matrix')
export const getFeatureImportance = () => api.get('/dashboard/feature-importance')
export const createPrediction = (payload) => api.post('/predict', payload)
export const getHistory = (params = {}) => api.get('/history', { params })
export const getPrediction = (id) => api.get(`/history/${id}`)
export const deletePrediction = (id) => api.delete(`/history/${id}`)
export const exportHistory = () => api.get('/history/export', { responseType: 'blob' })

export function getApiError(error, fallback = 'Something went wrong. Please try again.') {
  return error?.response?.data?.detail || error?.message || fallback
}

export default api
