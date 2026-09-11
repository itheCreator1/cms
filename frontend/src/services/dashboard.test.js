import { afterEach, expect, test, vi } from 'vitest'

import { articleService } from './articles'
import { announcementService } from './announcements'
import { pageService } from './pages'

afterEach(() => {
  vi.restoreAllMocks()
})

test('article management service sends authenticated content requests', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ item: { id: 12, title: 'Draft' } }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await expect(articleService.create({ title: 'Draft' })).resolves.toEqual({ id: 12, title: 'Draft' })

  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/articles',
    expect.objectContaining({ method: 'POST', body: JSON.stringify({ title: 'Draft' }) }),
  )
})

test.each([
  ['announcement', announcementService, '/announcements'],
  ['page', pageService, '/pages'],
])('%s management service exposes authenticated CRUD requests', async (_name, service, path) => {
  expect(service).toEqual(expect.objectContaining({
    list: expect.any(Function),
    get: expect.any(Function),
    create: expect.any(Function),
    update: expect.any(Function),
    delete: expect.any(Function),
  }))

  const fetchMock = vi.fn()
    .mockResolvedValueOnce({ ok: true, headers: new Headers({ 'content-type': 'application/json' }), json: async () => ({ items: [{ id: 1 }] }) })
    .mockResolvedValueOnce({ ok: true, headers: new Headers({ 'content-type': 'application/json' }), json: async () => ({ item: { id: 1 } }) })
    .mockResolvedValueOnce({ ok: true, headers: new Headers({ 'content-type': 'application/json' }), json: async () => ({ item: { id: 2 } }) })
    .mockResolvedValueOnce({ ok: true, headers: new Headers({ 'content-type': 'application/json' }), json: async () => ({ item: { id: 1, title: 'Revised' } }) })
    .mockResolvedValueOnce({ ok: true, headers: new Headers(), json: async () => null })
  vi.stubGlobal('fetch', fetchMock)

  await expect(service.list()).resolves.toEqual([{ id: 1 }])
  await expect(service.get(1)).resolves.toEqual({ id: 1 })
  await expect(service.create({ title: 'Draft' })).resolves.toEqual({ id: 2 })
  await expect(service.update(1, { title: 'Revised' })).resolves.toEqual({ id: 1, title: 'Revised' })
  await expect(service.delete(1)).resolves.toBeUndefined()

  expect(fetchMock).toHaveBeenNthCalledWith(1, `http://localhost:5000/api${path}`, expect.objectContaining({ headers: expect.any(Headers) }))
  expect(fetchMock).toHaveBeenNthCalledWith(2, `http://localhost:5000/api${path}/1`, expect.objectContaining({ headers: expect.any(Headers) }))
  expect(fetchMock).toHaveBeenNthCalledWith(3, `http://localhost:5000/api${path}`, expect.objectContaining({ method: 'POST', body: JSON.stringify({ title: 'Draft' }) }))
  expect(fetchMock).toHaveBeenNthCalledWith(4, `http://localhost:5000/api${path}/1`, expect.objectContaining({ method: 'PUT', body: JSON.stringify({ title: 'Revised' }) }))
  expect(fetchMock).toHaveBeenNthCalledWith(5, `http://localhost:5000/api${path}/1`, expect.objectContaining({ method: 'DELETE' }))
})
