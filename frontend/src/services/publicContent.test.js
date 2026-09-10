import { afterEach, expect, test, vi } from 'vitest'

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

function jsonResponse(data) {
  return {
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => data,
  }
}

test('article services return collection and slug resources from public endpoints', async () => {
  const article = {
    id: 7,
    title: 'Lead story',
    slug: 'lead-story',
    body: 'Article body',
    status: 'published',
    author_id: 2,
    category_id: 3,
    featured_image_id: null,
    featured_image: null,
    tag_ids: [],
    created_at: '2026-09-09T08:00:00+00:00',
    updated_at: '2026-09-09T09:00:00+00:00',
    published_at: '2026-09-09T10:00:00+00:00',
  }
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(jsonResponse({ items: [article] }))
    .mockResolvedValueOnce(jsonResponse({ item: article }))
  vi.stubGlobal('fetch', fetchMock)
  localStorage.setItem('cms_access_token', 'stale-token')
  const { listPublishedArticles, getPublishedArticle } = await import('./articles')

  await expect(listPublishedArticles()).resolves.toEqual([article])
  await expect(getPublishedArticle('lead story')).resolves.toEqual(article)
  expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
    'http://localhost:5000/api/articles',
    'http://localhost:5000/api/articles/slug/lead%20story',
  ])
  expect(fetchMock.mock.calls.every(([, options]) => !options.headers.has('Authorization'))).toBe(true)
})

test('announcement service returns the public collection', async () => {
  const announcement = {
    id: 4,
    title: 'Maintenance',
    body: 'Tonight at 22:00.',
    status: 'published',
    author_id: 2,
    created_at: '2026-09-08T08:00:00+00:00',
    published_at: '2026-09-08T09:00:00+00:00',
    expires_at: null,
  }
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ items: [announcement] })))
  const { listPublishedAnnouncements } = await import('./announcements')

  await expect(listPublishedAnnouncements()).resolves.toEqual([announcement])
})

test('page service returns a published page by encoded slug', async () => {
  const page = {
    id: 5,
    title: 'About',
    slug: 'about us',
    body: 'About this publication.',
    status: 'published',
    author_id: 2,
    updated_at: '2026-09-07T09:00:00+00:00',
  }
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ item: page }))
  vi.stubGlobal('fetch', fetchMock)
  const { getPublishedPage } = await import('./pages')

  await expect(getPublishedPage('about us')).resolves.toEqual(page)
  expect(fetchMock.mock.calls[0][0]).toBe('http://localhost:5000/api/pages/slug/about%20us')
})

test('category service returns public taxonomy records', async () => {
  const categories = [{ id: 3, name: 'Community', slug: 'community' }]
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ items: categories })))
  const { listCategories } = await import('./categories')

  await expect(listCategories()).resolves.toEqual(categories)
})
