import { apiRequest } from './api'

export const userService = {
  list: async () => (await apiRequest('/users')).items,
  create: async (values) => (await apiRequest('/users', { method: 'POST', body: JSON.stringify(values) })).item,
  update: async (id, values) => (await apiRequest(`/users/${id}`, { method: 'PUT', body: JSON.stringify(values) })).item,
  delete: async (id) => { await apiRequest(`/users/${id}`, { method: 'DELETE' }) },
}
