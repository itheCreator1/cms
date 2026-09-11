import { apiRequest } from './api'

export async function listPublishedArticles() {
  const { items } = await apiRequest('/articles', { auth: false })
  return items
}

export async function getPublishedArticle(slug) {
  const { item } = await apiRequest(`/articles/slug/${encodeURIComponent(slug)}`, { auth: false })
  return item
}

export async function listArticles() {
  const { items } = await apiRequest('/articles')
  return items
}

export async function getArticle(id) {
  const { item } = await apiRequest(`/articles/${id}`)
  return item
}

export async function createArticle(payload) {
  const { item } = await apiRequest('/articles', { method: 'POST', body: JSON.stringify(payload) })
  return item
}

export async function updateArticle(id, payload) {
  const { item } = await apiRequest(`/articles/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  return item
}

export async function deleteArticle(id) {
  await apiRequest(`/articles/${id}`, { method: 'DELETE' })
}

export const articleService = Object.freeze({
  listPublished: listPublishedArticles,
  getPublished: getPublishedArticle,
  list: listArticles,
  get: getArticle,
  create: createArticle,
  update: updateArticle,
  delete: deleteArticle,
})
