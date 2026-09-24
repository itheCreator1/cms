import { apiRequest } from './api'

export async function listCategories() {
  const { items } = await apiRequest('/categories', { auth: false })
  return items
}

export const categoryService = {
  list: listCategories,
  create: async (values) => (await apiRequest('/categories', { method: 'POST', body: JSON.stringify(values) })).item,
  update: async (id, values) => (await apiRequest(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(values) })).item,
  delete: async (id) => { await apiRequest(`/categories/${id}`, { method: 'DELETE' }) },
  listCategories,
}
