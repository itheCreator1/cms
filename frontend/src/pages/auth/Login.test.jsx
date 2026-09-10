import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import Login from './Login'
import SystemAccess from './SystemAccess'
import { AuthContext } from '../../context/AuthContext'

afterEach(() => vi.restoreAllMocks())

function renderWithAuth(element, value) {
  return render(
    <AuthContext.Provider value={{ isRestoring: false, user: null, token: null, ...value }}>
      <MemoryRouter>{element}</MemoryRouter>
    </AuthContext.Provider>,
  )
}

function fillForm(email = 'user@example.test', password = 'a secure password') {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: password } })
}

test('regular login submits through the regular login action', async () => {
  const login = vi.fn().mockResolvedValue({ role: 'publisher' })
  renderWithAuth(<Login />, { login })
  fillForm()

  fireEvent.click(screen.getByRole('button', { name: 'Log in' }))

  await waitFor(() => expect(login).toHaveBeenCalledWith('user@example.test', 'a secure password'))
})

test('regular login shows a generic failure message', async () => {
  const login = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
  renderWithAuth(<Login />, { login })
  fillForm()

  fireEvent.click(screen.getByRole('button', { name: 'Log in' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid credentials')
})

test('system access submits through the isolated Superadmin login action', async () => {
  const superadminLogin = vi.fn().mockResolvedValue({ role: 'superadmin' })
  renderWithAuth(<SystemAccess />, { superadminLogin })
  fillForm('root@example.test', 'a secure password')

  fireEvent.click(screen.getByRole('button', { name: 'Enter system' }))

  await waitFor(() => expect(superadminLogin).toHaveBeenCalledWith('root@example.test', 'a secure password'))
})
