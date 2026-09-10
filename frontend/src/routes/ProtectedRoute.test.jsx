import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { expect, test } from 'vitest'

import { AuthContext } from '../context/AuthContext'
import ProtectedRoute from './ProtectedRoute'

function renderRoute(value, minimumRole = 'publisher') {
  return render(
    <AuthContext.Provider value={value}>
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route element={<ProtectedRoute minimumRole={minimumRole} />}>
            <Route path="/dashboard" element={<p>Dashboard content</p>} />
          </Route>
          <Route path="/login" element={<p>Login page</p>} />
          <Route path="/" element={<p>Public home</p>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

test('redirects anonymous users to login', () => {
  renderRoute({ isRestoring: false, user: null, token: null })

  expect(screen.getByText('Login page')).toBeInTheDocument()
})

test('allows a role at or above the minimum', () => {
  renderRoute({
    isRestoring: false,
    token: 'token',
    user: { role: 'admin' },
  })

  expect(screen.getByText('Dashboard content')).toBeInTheDocument()
})

test('redirects authenticated users below the minimum to the public home', () => {
  renderRoute({
    isRestoring: false,
    token: 'token',
    user: { role: 'visitor' },
  })

  expect(screen.getByText('Public home')).toBeInTheDocument()
})

test('redirects users with an unknown role to the public home', () => {
  renderRoute({
    isRestoring: false,
    token: 'token',
    user: { role: 'unknown' },
  })

  expect(screen.getByText('Public home')).toBeInTheDocument()
})
