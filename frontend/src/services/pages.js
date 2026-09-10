import { apiRequest } from './api'

export async function getPublishedPage(slug) {
  const { item } = await apiRequest(`/pages/slug/${encodeURIComponent(slug)}`, { auth: false })
  return item
}

export const pageService = Object.freeze({ getPublishedPage })
