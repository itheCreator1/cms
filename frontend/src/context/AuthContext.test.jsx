import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'

import { AuthContext, AuthProvider, useAuth } from './AuthContext'

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

function Probe() {
  const { isRestoring, user, logout } = useAuth()
  return (
    <div>
      <span data-testid="state">{isRestoring ? 'restoring' : user?.email || 'anonymous'}</span>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

test('restores a stored session from the current-user endpoint', async () => {
  localStorage.setItem('cms_access_token', 'stored-token')
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({
      user: { id: 3, email: 'publisher@example.test', role: 'publisher' },
    }),
  }))

  render(<AuthProvider><Probe /></AuthProvider>)

  expect(await screen.findByTestId('state')).toHaveTextContent('publisher@example.test')
})

test('clears an invalid stored session', async () => {
  localStorage.setItem('cms_access_token', 'expired-token')
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: false,
    status: 401,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ error: 'Authentication required' }),
  }))

  render(<AuthProvider><Probe /></AuthProvider>)

  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('anonymous'))
  expect(localStorage.getItem('cms_access_token')).toBeNull()
})

test('logout clears the active token and user', async () => {
  localStorage.setItem('cms_access_token', 'stored-token')
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ user: { id: 3, email: 'user@example.test', role: 'publisher' } }),
  }))

  render(<AuthProvider><Probe /></AuthProvider>)
  await screen.findByText('user@example.test')

  screen.getByRole('button', { name: 'Logout' }).click()

  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('anonymous'))
  expect(localStorage.getItem('cms_access_token')).toBeNull()
})

test('the auth context starts without a session when storage is empty', () => {
  render(<AuthContext.Consumer>{value => <span>{value.user?.email || 'anonymous'}</span>}</AuthContext.Consumer>)

  expect(screen.getByText('anonymous')).toBeInTheDocument()
})
