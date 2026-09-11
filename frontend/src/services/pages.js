import { apiRequest } from './api'

export async function getPublishedPage(slug) {
  const { item } = await apiRequest(`/pages/slug/${encodeURIComponent(slug)}`, { auth: false })
  return item
}

export async function listPages() {
  const { items } = await apiRequest('/pages')
  return items
}

export async function getPage(id) {
  const { item } = await apiRequest(`/pages/${id}`)
  return item
}

export async function createPage(payload) {
  const { item } = await apiRequest('/pages', { method: 'POST', body: JSON.stringify(payload) })
  return item
}

export async function updatePage(id, payload) {
  const { item } = await apiRequest(`/pages/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  return item
}

export async function deletePage(id) {
  await apiRequest(`/pages/${id}`, { method: 'DELETE' })
}

export const pageService = Object.freeze({
  getPublished: getPublishedPage,
  list: listPages,
  get: getPage,
  create: createPage,
  update: updatePage,
  delete: deletePage,
})
