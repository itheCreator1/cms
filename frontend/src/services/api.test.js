import { afterEach, expect, test, vi } from 'vitest'

import { apiRequest } from './api'
import { getHealth } from './health'

afterEach(() => {
  vi.restoreAllMocks()
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
