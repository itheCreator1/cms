import { afterEach, expect, test, vi } from 'vitest'

import { login, superadminLogin } from './auth'

afterEach(() => vi.restoreAllMocks())

function response(payload) {
  return {
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => payload,
  }
}

test('login posts credentials to the regular endpoint', async () => {
  const fetchMock = vi.fn().mockResolvedValue(response({ access_token: 'token' }))
  vi.stubGlobal('fetch', fetchMock)

  await login('user@example.test', 'secure password')

  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/login',
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ email: 'user@example.test', password: 'secure password' }),
    }),
  )
})

test('superadminLogin posts credentials to the isolated endpoint', async () => {
  const fetchMock = vi.fn().mockResolvedValue(response({ access_token: 'token' }))
  vi.stubGlobal('fetch', fetchMock)

  await superadminLogin('root@example.test', 'secure password')

  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/superadmin-login',
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ email: 'root@example.test', password: 'secure password' }),
    }),
  )
})
