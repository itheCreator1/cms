import { apiRequest } from './api'

export async function listPublishedAnnouncements() {
  const { items } = await apiRequest('/announcements', { auth: false })
  return items
}

export const announcementService = Object.freeze({ listPublishedAnnouncements })
