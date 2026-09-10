import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, test, vi } from 'vitest'

import App from './App'
import { AuthContext } from './context/AuthContext'

afterEach(() => {
  vi.restoreAllMocks()
})

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('home health status', () => {
  test('renders Backend connected after a successful health response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ status: 'ok' }),
    }))

    renderAt('/')

    expect(await screen.findByText('Backend connected')).toBeInTheDocument()
  })

  test('renders Backend unavailable when the health request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))

    renderAt('/')

    expect(await screen.findByText('Backend unavailable')).toBeInTheDocument()
  })
})

test('regular login renders a working login form', () => {
  renderAt('/login')

  expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument()
  expect(screen.getByLabelText('Email')).toBeInTheDocument()
  expect(screen.getByLabelText('Password')).toBeInTheDocument()
})

test('system access is a distinct working login page', () => {
  renderAt('/system-access')

  expect(screen.getByRole('heading', { name: 'System access' })).toBeInTheDocument()
  expect(screen.getByLabelText('Email')).toBeInTheDocument()
  expect(screen.getByLabelText('Password')).toBeInTheDocument()
  expect(screen.queryByRole('heading', { name: 'Login' })).not.toBeInTheDocument()
})

test.each(['/dashboard', '/dashboard/articles/new', '/dashboard/anything/nested'])(
  '%s redirects to login',
  async (path) => {
    renderAt(path)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument()
    })
  },
)

test('dashboard is available to an authenticated publisher', () => {
  render(
    <AuthContext.Provider value={{ isRestoring: false, token: 'token', user: { role: 'publisher' } }}>
      <MemoryRouter initialEntries={['/dashboard']}><App /></MemoryRouter>
    </AuthContext.Provider>,
  )

  expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
})
