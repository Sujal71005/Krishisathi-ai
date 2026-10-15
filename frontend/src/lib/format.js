export function percent(value, digits = 2) {
  return Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(digits)}%` : '—'
}

export function number(value, digits = 2) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : '—'
}

export function dateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

export function titleCase(value = '') {
  return value.replace(/[-_]/g, ' ').replace(/\b\w/g, (character) => character.toUpperCase())
}
