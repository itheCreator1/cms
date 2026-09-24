import { apiRequest } from './api'

export async function listTags() {
  const { items } = await apiRequest('/tags')
  return items
}

export const tagService = {
  list: listTags,
  create: async (values) => (await apiRequest('/tags', { method: 'POST', body: JSON.stringify(values) })).item,
  update: async (id, values) => (await apiRequest(`/tags/${id}`, { method: 'PUT', body: JSON.stringify(values) })).item,
  delete: async (id) => { await apiRequest(`/tags/${id}`, { method: 'DELETE' }) },
}
