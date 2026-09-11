import { afterEach, expect, test, vi } from 'vitest'

import { listMedia, uploadImage } from './media'
import { apiRequest } from './api'

vi.mock('./api', () => ({ apiRequest: vi.fn() }))

afterEach(() => vi.restoreAllMocks())

test('uploadImage sends the selected file and optional description as multipart form data', async () => {
  apiRequest.mockResolvedValue({ item: { id: 4 } })
  const file = new File(['image'], 'garden.webp', { type: 'image/webp' })

  await expect(uploadImage(file, 'Garden flowers')).resolves.toEqual({ id: 4 })
  expect(apiRequest).toHaveBeenCalledWith('/media/uploads', expect.objectContaining({ method: 'POST' }))
  const body = apiRequest.mock.calls[0][1].body
  expect(body).toBeInstanceOf(FormData)
  expect(body.get('file')).toBe(file)
  expect(body.get('alt_text')).toBe('Garden flowers')
})

test('listMedia returns the available image records', async () => {
  apiRequest.mockResolvedValue({ items: [{ id: 4 }] })
  await expect(listMedia()).resolves.toEqual([{ id: 4 }])
})
