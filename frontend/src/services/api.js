import { getAccessToken } from './tokenStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export async function apiRequest(path, options = {}) {
  const { auth = true, ...fetchOptions } = options
  const headers = new Headers(fetchOptions.headers)
  const token = getAccessToken()
  if (auth && token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  if (fetchOptions.body && !(fetchOptions.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(
    `${API_BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`,
    { ...fetchOptions, headers },
  )
  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : null

  if (!response.ok) {
    const error = new Error(data?.error || `Request failed with status ${response.status}`)
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}

export async function fetchAuthenticatedBlob(path) {
  const headers = new Headers()
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(resolveApiUrl(path), { headers })
  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`)
    error.status = response.status
    throw error
  }
  return response.blob()
}

export function resolveApiUrl(url) {
  if (!url || /^https?:\/\//i.test(url)) return url

  const base = new URL(API_BASE_URL, window.location.origin)
  if (url.startsWith('/api/')) return new URL(url, base.origin).toString()
  return new URL(url.replace(/^\//, ''), `${base.href.replace(/\/$/, '')}/`).toString()
}
