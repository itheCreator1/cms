import { apiRequest } from './api'

export function getHealth() {
  return apiRequest('/health')
}
