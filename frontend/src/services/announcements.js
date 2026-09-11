import { apiRequest } from './api'

export async function listPublishedAnnouncements() {
  const { items } = await apiRequest('/announcements', { auth: false })
  return items
}

export async function listAnnouncements() {
  const { items } = await apiRequest('/announcements')
  return items
}

export async function getAnnouncement(id) {
  const { item } = await apiRequest(`/announcements/${id}`)
  return item
}

export async function createAnnouncement(payload) {
  const { item } = await apiRequest('/announcements', { method: 'POST', body: JSON.stringify(payload) })
  return item
}

export async function updateAnnouncement(id, payload) {
  const { item } = await apiRequest(`/announcements/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  return item
}

export async function deleteAnnouncement(id) {
  await apiRequest(`/announcements/${id}`, { method: 'DELETE' })
}

export const announcementService = Object.freeze({
  listPublished: listPublishedAnnouncements,
  list: listAnnouncements,
  get: getAnnouncement,
  create: createAnnouncement,
  update: updateAnnouncement,
  delete: deleteAnnouncement,
})
