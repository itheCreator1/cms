import { apiRequest } from './api'

export const defaultSettings = {
  site_name: 'CMS', tagline: 'The daily edition',
  homepage_headline: 'Stories that keep us connected.',
  homepage_intro: 'News, notices, and voices from across the community.',
}

export const settingsService = {
  get: async () => (await apiRequest('/settings', { auth: false })).item,
  update: async (values) => (await apiRequest('/settings', { method: 'PUT', body: JSON.stringify(values) })).item,
}
