import { apiRequest } from './api'

export async function listTags() {
  const { items } = await apiRequest('/tags')
  return items
}

export const tagService = Object.freeze({ list: listTags })
