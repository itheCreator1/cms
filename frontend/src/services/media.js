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

export const mediaService = {
  list: listMedia,
  upload: uploadImage,
  createLink: async (values) => (await apiRequest('/media/links', { method: 'POST', body: JSON.stringify(values) })).item,
  update: async (id, values) => (await apiRequest(`/media/${id}`, { method: 'PUT', body: JSON.stringify(values) })).item,
  delete: async (id) => { await apiRequest(`/media/${id}`, { method: 'DELETE' }) },
}
