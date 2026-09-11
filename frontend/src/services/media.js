import { apiRequest } from './api'

export async function listMedia() {
  const { items } = await apiRequest('/media')
  return items
}

export async function uploadImage(file, altText = '') {
  const body = new FormData()
  body.append('file', file)
  if (altText) body.append('alt_text', altText)
  const { item } = await apiRequest('/media/uploads', { method: 'POST', body })
  return item
}
