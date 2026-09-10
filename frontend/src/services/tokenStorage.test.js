import { afterEach, expect, test } from 'vitest'

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from './tokenStorage'

afterEach(() => {
  localStorage.clear()
})

test('stores and reads the access token under the CMS key', () => {
  setAccessToken('token-value')

  expect(getAccessToken()).toBe('token-value')
  expect(localStorage.getItem('cms_access_token')).toBe('token-value')
})

test('clears the access token', () => {
  setAccessToken('token-value')

  clearAccessToken()

  expect(getAccessToken()).toBeNull()
})
