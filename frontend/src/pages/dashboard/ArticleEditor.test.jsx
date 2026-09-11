import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'
import ArticleEditor from './ArticleEditor'
import { articleService } from '../../services/articles'
import * as categories from '../../services/categories'
import * as media from '../../services/media'
import { AuthContext } from '../../context/AuthContext'

vi.mock('../../services/articles', () => ({ articleService: { get: vi.fn(), create: vi.fn(), update: vi.fn() } }))

afterEach(() => vi.restoreAllMocks())

function openEditor(user = { id: 1, role: 'publisher' }) {
  render(<AuthContext.Provider value={{ user }}><MemoryRouter initialEntries={['/dashboard/articles/1/edit']}><Routes><Route path="/dashboard/articles/:id/edit" element={<ArticleEditor />} /></Routes></MemoryRouter></AuthContext.Provider>)
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

test('publisher sees a submitted article as read-only', async () => {
  vi.spyOn(articleService, 'get').mockResolvedValue({ id: 1, title: 'Submitted story', slug: 'submitted-story', category_id: 1, status: 'pending_review', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }] })
  vi.spyOn(categories, 'listCategories').mockResolvedValue([{ id: 1, name: 'News' }])

  openEditor()

  expect(await screen.findByLabelText('Title')).toBeDisabled()
  expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Submit for review' })).not.toBeInTheDocument()
})

test('admin can publish a submitted article', async () => {
  vi.spyOn(articleService, 'get').mockResolvedValue({ id: 1, title: 'Submitted story', slug: 'submitted-story', category_id: 1, status: 'pending_review', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }] })
  vi.spyOn(categories, 'listCategories').mockResolvedValue([{ id: 1, name: 'News' }])
  const update = vi.spyOn(articleService, 'update').mockResolvedValue({ id: 1, title: 'Submitted story', slug: 'submitted-story', category_id: 1, status: 'published', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }] })

  openEditor({ id: 2, role: 'admin' })
  fireEvent.click(await screen.findByRole('button', { name: 'Publish' }))

  await waitFor(() => expect(update).toHaveBeenCalledWith('1', { title: 'Submitted story', slug: 'submitted-story', category_id: 1, status: 'published', body_blocks: [{ type: 'text', text: 'Text' }] }))
})

test('publisher cannot open another author’s article from a dashboard route', async () => {
  vi.spyOn(articleService, 'get').mockResolvedValue({ id: 1, author_id: 2, title: 'Other story', slug: 'other-story', category_id: 1, status: 'published', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }] })
  vi.spyOn(categories, 'listCategories').mockResolvedValue([{ id: 1, name: 'News' }])

  openEditor({ id: 1, role: 'publisher' })

  expect(await screen.findByRole('alert')).toHaveTextContent('This article is unavailable.')
  expect(screen.queryByLabelText('Title')).not.toBeInTheDocument()
})

test('editor adds an uploaded picture as an ordered body block', async () => {
  const item = { id: 1, title: 'Draft story', slug: 'draft-story', category_id: 1, status: 'draft', body: 'Text', body_blocks: [{ type: 'text', text: 'Text' }] }
  vi.spyOn(articleService, 'get').mockResolvedValue(item)
  vi.spyOn(categories, 'listCategories').mockResolvedValue([{ id: 1, name: 'News' }])
  vi.spyOn(media, 'listMedia').mockResolvedValue([])
  vi.spyOn(media, 'uploadImage').mockResolvedValue({ id: 8, url: '/api/media/files/garden.webp', alt_text: 'Garden' })

  openEditor()
  fireEvent.click(await screen.findByRole('button', { name: 'Add picture' }))
  fireEvent.change(screen.getByLabelText('Upload picture'), { target: { files: [new File(['image'], 'garden.webp', { type: 'image/webp' })] } })

  expect(await screen.findByText('Attached picture Garden')).toBeInTheDocument()
  fireEvent.submit(screen.getByLabelText('Title').closest('form'))
  await waitFor(() => expect(articleService.update).toHaveBeenCalledWith('1', expect.objectContaining({
    body_blocks: [{ type: 'text', text: 'Text' }, { type: 'image', media_id: 8 }],
  })))
})
