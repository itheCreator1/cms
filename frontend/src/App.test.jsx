import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

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

test('visitor navigation omits the Publisher dashboard link', () => {
  render(
    <AuthContext.Provider value={{ isRestoring: false, token: 'token', user: { role: 'visitor' } }}>
      <MemoryRouter><App /></MemoryRouter>
    </AuthContext.Provider>,
  )

  expect(screen.queryByRole('link', { name: 'Dashboard' })).not.toBeInTheDocument()
})
