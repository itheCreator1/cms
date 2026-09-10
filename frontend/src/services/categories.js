import { apiRequest } from './api'

export async function listCategories() {
  const { items } = await apiRequest('/categories', { auth: false })
  return items
}

export const categoryService = Object.freeze({ listCategories })
