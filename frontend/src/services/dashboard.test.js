import { afterEach, expect, test, vi } from 'vitest'

import { articleService } from './articles'

afterEach(() => {
  vi.restoreAllMocks()
})

test('article management service sends authenticated content requests', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ item: { id: 12, title: 'Draft' } }),
  })
  vi.stubGlobal('fetch', fetchMock)

  await expect(articleService.create({ title: 'Draft' })).resolves.toEqual({ id: 12, title: 'Draft' })

  expect(fetchMock).toHaveBeenCalledWith(
    'http://localhost:5000/api/articles',
    expect.objectContaining({ method: 'POST', body: JSON.stringify({ title: 'Draft' }) }),
  )
})
