import { afterEach, expect, test, vi } from 'vitest'

import { apiRequest, fetchAuthenticatedBlob, resolveApiUrl } from './api'
import { getHealth } from './health'

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

test('apiRequest joins the base URL and parses JSON', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ value: 42 }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await expect(apiRequest('/example')).resolves.toEqual({ value: 42 })
  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/example',
    expect.objectContaining({ headers: expect.any(Headers) }),
  )
})

test('apiRequest throws an error with parsed API details for non-success responses', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: false,
    status: 404,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ error: 'Not found' }),
  }))

  await expect(apiRequest('/missing')).rejects.toMatchObject({
    message: 'Not found',
    status: 404,
  })
})

test('getHealth requests the health path', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ status: 'ok' }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await expect(getHealth()).resolves.toEqual({ status: 'ok' })
  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/health',
    expect.any(Object),
  )
})

test('apiRequest attaches the stored bearer token', async () => {
  localStorage.setItem('cms_access_token', 'access-token')
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ ok: true }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await apiRequest('/protected')

  expect(fetchMock.mock.calls[0][1].headers.get('Authorization')).toBe(
    'Bearer access-token',
  )
})

test('apiRequest preserves an explicitly supplied authorization header', async () => {
  localStorage.setItem('cms_access_token', 'stored-token')
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ ok: true }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await apiRequest('/protected', {
    headers: { Authorization: 'Bearer explicit-token' },
  })

  expect(fetchMock.mock.calls[0][1].headers.get('Authorization')).toBe(
    'Bearer explicit-token',
  )
})

test('apiRequest omits a stored bearer token for an anonymous request', async () => {
  localStorage.setItem('cms_access_token', 'stale-token')
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ items: [] }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await apiRequest('/articles', { auth: false })

  expect(fetchMock.mock.calls[0][1].headers.has('Authorization')).toBe(false)
  expect(fetchMock.mock.calls[0][1]).not.toHaveProperty('auth')
})

test('apiRequest keeps the browser multipart content type boundary', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ item: {} }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await apiRequest('/media/uploads', { method: 'POST', body: new FormData() })

  expect(fetchMock.mock.calls[0][1].headers.has('Content-Type')).toBe(false)
})

test('fetchAuthenticatedBlob uses the bearer header without exposing it in a URL', async () => {
  localStorage.setItem('cms_access_token', 'private-token')
  const blob = new Blob(['image'])
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, blob: async () => blob })
  vi.stubGlobal('fetch', fetchMock)

  await expect(fetchAuthenticatedBlob('/media/files/private.webp')).resolves.toBe(blob)
  expect(fetchMock).toHaveBeenCalledWith('http://localhost:5000/api/media/files/private.webp', expect.any(Object))
  expect(fetchMock.mock.calls[0][1].headers.get('Authorization')).toBe('Bearer private-token')
})

test.each([
  ['/api/media/files/image.webp', 'http://localhost:5000/api/media/files/image.webp'],
  ['https://cdn.example/image.webp', 'https://cdn.example/image.webp'],
  [null, null],
])('resolveApiUrl maps %s to %s', (url, expected) => {
  expect(resolveApiUrl(url)).toBe(expected)
})
