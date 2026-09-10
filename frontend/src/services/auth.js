import { apiRequest } from './api'

export function login(email, password) {
  return apiRequest('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function superadminLogin(email, password) {
  return apiRequest('/superadmin-login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function getCurrentUser() {
  return apiRequest('/me')
}

export const authService = Object.freeze({ login, superadminLogin, getCurrentUser })
