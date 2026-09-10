import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import App from '../../App'

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

function response(data, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => data,
  }
}

function renderAt(path) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>)
}

const olderArticle = {
  id: 1,
  title: 'The neighbourhood archive opens',
  slug: 'archive-opens',
  body: 'Residents can explore the collection this weekend.',
  status: 'published',
  author_id: 2,
  category_id: 11,
  featured_image_id: null,
  featured_image: null,
  tag_ids: [],
  created_at: '2026-09-08T08:00:00+00:00',
  updated_at: '2026-09-08T09:00:00+00:00',
  published_at: '2026-09-08T10:00:00+00:00',
}

const leadArticle = {
  id: 2,
  title: 'A new chapter for the city garden',
  slug: 'city-garden',
  body: 'The gates reopen today.\n\nVolunteers planted two hundred native flowers.',
  status: 'published',
  author_id: 2,
  category_id: 12,
  featured_image_id: 9,
  featured_image: {
    id: 9,
    filename: 'garden.webp',
    url: '/api/media/files/garden.webp',
    uploaded_by: 3,
    uploaded_at: '2026-09-09T07:00:00+00:00',
    file_type: 'image/webp',
    source_type: 'upload',
    media_type: 'image',
    provider: 'local',
    alt_text: 'Purple flowers in the community garden',
  },
  tag_ids: [],
  created_at: '2026-09-09T08:00:00+00:00',
  updated_at: '2026-09-09T09:00:00+00:00',
  published_at: '2026-09-09T10:00:00+00:00',
}

const announcement = {
  id: 4,
  title: 'Street closure tonight',
  body: 'Oak Street closes at 22:00.',
  status: 'published',
  author_id: 2,
  created_at: '2026-09-09T11:00:00+00:00',
  published_at: '2026-09-09T12:00:00+00:00',
  expires_at: null,
}

test('home promotes the newest article and enriches it with category and media', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    if (url.endsWith('/articles')) return response({ items: [olderArticle, leadArticle] })
    if (url.endsWith('/announcements')) return response({ items: [announcement] })
    if (url.endsWith('/categories')) return response({ items: [
      { id: 11, name: 'Culture', slug: 'culture' },
      { id: 12, name: 'Community', slug: 'community' },
    ] })
    throw new Error(`Unexpected URL: ${url}`)
  }))

  renderAt('/')

  expect(await screen.findByRole('heading', { name: leadArticle.title })).toBeInTheDocument()
  const stories = screen.getByLabelText('Latest stories')
  expect(within(stories).getAllByRole('heading').map((heading) => heading.textContent)).toEqual([
    leadArticle.title,
    olderArticle.title,
  ])
  expect(screen.getByText('Community')).toBeInTheDocument()
  expect(screen.getByRole('img', { name: leadArticle.featured_image.alt_text })).toHaveAttribute(
    'src',
    'http://localhost:5000/api/media/files/garden.webp',
  )
  expect(screen.getByRole('heading', { name: announcement.title })).toBeInTheDocument()
})

test('home keeps articles readable when announcements and categories fail', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    if (url.endsWith('/articles')) return response({ items: [olderArticle] })
    throw new Error('offline')
  }))

  renderAt('/')

  expect(await screen.findByRole('heading', { name: olderArticle.title })).toBeInTheDocument()
  expect(screen.getByText('Announcements are unavailable.')).toBeInTheDocument()
  expect(screen.queryByText(String(olderArticle.category_id))).not.toBeInTheDocument()
})

test('home shows useful empty states when no public content exists', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    if (url.endsWith('/categories')) return response({ items: [] })
    return response({ items: [] })
  }))

  renderAt('/')

  expect(await screen.findByText('No stories have been published yet.')).toBeInTheDocument()
  expect(screen.getByText('There are no active announcements.')).toBeInTheDocument()
})

test('article route renders stored markup as text instead of executable HTML', async () => {
  const unsafeArticle = { ...leadArticle, body: 'First paragraph.\n\n<img src=x onerror=alert(1)>' }
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    if (url.includes('/articles/slug/')) return response({ item: unsafeArticle })
    if (url.endsWith('/categories')) return response({ items: [{ id: 12, name: 'Community', slug: 'community' }] })
    throw new Error(`Unexpected URL: ${url}`)
  }))

  const { container } = renderAt('/articles/city-garden')

  expect(await screen.findByRole('heading', { name: unsafeArticle.title })).toBeInTheDocument()
  expect(screen.getByText('<img src=x onerror=alert(1)>')).toBeInTheDocument()
  expect(container.querySelector('article .story-body img')).toBeNull()
  expect(screen.getByText('Community')).toBeInTheDocument()
})

test('article route renders an in-page not-found state', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    if (url.includes('/articles/slug/')) return response({ error: 'Not found' }, 404)
    if (url.endsWith('/categories')) return response({ items: [] })
    throw new Error(`Unexpected URL: ${url}`)
  }))

  renderAt('/articles/missing')

  expect(await screen.findByRole('heading', { name: 'Story not found' })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Return home' })).toHaveAttribute('href', '/')
})

test('announcements page orders current notices newest first', async () => {
  const newer = { ...announcement, id: 5, title: 'Library opens early', published_at: '2026-09-10T12:00:00+00:00' }
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ items: [announcement, newer] })))

  renderAt('/announcements')

  const list = await screen.findByLabelText('Published announcements')
  expect(within(list).getAllByRole('heading').map((heading) => heading.textContent)).toEqual([
    newer.title,
    announcement.title,
  ])
})

test('page route can retry a transient failure', async () => {
  const page = {
    id: 6,
    title: 'About the newsroom',
    slug: 'about',
    body: 'Independent local reporting.',
    status: 'published',
    author_id: 2,
    updated_at: '2026-09-10T09:00:00+00:00',
  }
  const fetchMock = vi.fn()
    .mockRejectedValueOnce(new Error('offline'))
    .mockResolvedValueOnce(response({ item: page }))
  vi.stubGlobal('fetch', fetchMock)

  renderAt('/pages/about')

  fireEvent.click(await screen.findByRole('button', { name: 'Try again' }))
  expect(await screen.findByRole('heading', { name: page.title })).toBeInTheDocument()
  expect(screen.getByText(page.body)).toBeInTheDocument()
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
})
