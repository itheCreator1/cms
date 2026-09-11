import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'
import ArticleEditor from './ArticleEditor'
import { articleService } from '../../services/articles'
import * as categories from '../../services/categories'

vi.mock('../../services/articles', () => ({ articleService: { get: vi.fn(), update: vi.fn() } }))

afterEach(() => vi.restoreAllMocks())

function openEditor() {
  render(<MemoryRouter initialEntries={['/dashboard/articles/1/edit']}><Routes><Route path="/dashboard/articles/:id/edit" element={<ArticleEditor />} /></Routes></MemoryRouter>)
}

test('saving metadata preserves published status and picture blocks without sending response fields', async () => {
  const item = { id: 1, title: 'Story', slug: 'story', category_id: 1, status: 'published', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }, { type: 'image', media_id: 7, media: { id: 7 } }] }
  vi.spyOn(articleService, 'get').mockResolvedValue(item)
  vi.spyOn(categories, 'listCategories').mockResolvedValue([{ id: 1, name: 'News' }])
  const update = vi.spyOn(articleService, 'update').mockResolvedValue(item)
  openEditor()
  fireEvent.change(await screen.findByLabelText('Title'), { target: { value: 'Revised' } })
  fireEvent.submit(screen.getByLabelText('Title').closest('form'))
  await waitFor(() => expect(update).toHaveBeenCalledWith('1', { title: 'Revised', slug: 'story', category_id: 1, status: 'published', body_blocks: [{ type: 'text', text: 'Text' }, { type: 'image', media_id: 7 }] }))
})

test('failed article load displays a retry instead of endless loading', async () => {
  vi.spyOn(articleService, 'get').mockRejectedValue(new Error('Unavailable'))
  vi.spyOn(categories, 'listCategories').mockResolvedValue([])
  openEditor()
  expect(await screen.findByRole('alert')).toHaveTextContent('The editor is unavailable.')
})
