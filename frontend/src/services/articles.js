import { apiRequest } from './api'

export async function listPublishedArticles() {
  const { items } = await apiRequest('/articles', { auth: false })
  return items
}

export async function getPublishedArticle(slug) {
  const { item } = await apiRequest(`/articles/slug/${encodeURIComponent(slug)}`, { auth: false })
  return item
}

export const articleService = Object.freeze({ listPublishedArticles, getPublishedArticle })
