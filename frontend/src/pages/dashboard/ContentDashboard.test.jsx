import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import { AuthContext } from '../../context/AuthContext'
import { announcementService } from '../../services/announcements'
import { pageService } from '../../services/pages'
import AnnouncementEditor from './AnnouncementEditor'
import AnnouncementList from './AnnouncementList'
import PageEditor from './PageEditor'

vi.mock('../../services/announcements', () => ({ announcementService: { list: vi.fn(), get: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() } }))
vi.mock('../../services/pages', () => ({ pageService: { list: vi.fn(), get: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() } }))
vi.mock('../../services/media', () => ({ listMedia: vi.fn().mockResolvedValue([]), uploadImage: vi.fn() }))

afterEach(() => {
  vi.restoreAllMocks()
})

function withUser(component, user = { id: 1, role: 'publisher' }, path = '/') {
  return render(<AuthContext.Provider value={{ user }}><MemoryRouter initialEntries={[path]}>{component}</MemoryRouter></AuthContext.Provider>)
}

test('publisher announcement list shows only their items and filters by status', async () => {
  vi.spyOn(announcementService, 'list').mockResolvedValue([
    { id: 1, author_id: 1, title: 'Own draft', status: 'draft' },
    { id: 2, author_id: 1, title: 'Own submission', status: 'pending_review' },
    { id: 3, author_id: 2, title: 'Other draft', status: 'draft' },
  ])

  withUser(<AnnouncementList />)

  expect(await screen.findByText('Own draft')).toBeInTheDocument()
  expect(screen.queryByText('Other draft')).not.toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'pending_review' } })
  expect(screen.getByText('Own submission')).toBeInTheDocument()
  expect(screen.queryByText('Own draft')).not.toBeInTheDocument()
})

test('announcement deletion requires confirmation and refreshes the list', async () => {
  vi.spyOn(announcementService, 'list').mockResolvedValue([{ id: 1, author_id: 1, title: 'Old notice', status: 'draft' }])
  vi.spyOn(announcementService, 'delete').mockResolvedValue()
  vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true)

  withUser(<AnnouncementList />)
  const button = await screen.findByRole('button', { name: 'Delete Old notice' })
  fireEvent.click(button)
  expect(announcementService.delete).not.toHaveBeenCalled()
  fireEvent.click(button)
  await waitFor(() => expect(announcementService.delete).toHaveBeenCalledWith(1))
  await waitFor(() => expect(announcementService.list).toHaveBeenCalledTimes(2))
})

test('publisher saves announcement expiry and submits a saved draft for review', async () => {
  const draft = { id: 4, author_id: 1, title: 'Maintenance', status: 'draft', expires_at: null, body: 'Tonight', body_blocks: [{ type: 'text', text: 'Tonight' }] }
  vi.spyOn(announcementService, 'get').mockResolvedValue(draft)
  const update = vi.spyOn(announcementService, 'update').mockResolvedValue(draft)

  withUser(<Routes><Route path="/dashboard/announcements/:id/edit" element={<AnnouncementEditor />} /></Routes>, undefined, '/dashboard/announcements/4/edit')

  fireEvent.change(await screen.findByLabelText('Expires at'), { target: { value: '2026-09-30T18:00' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
  await waitFor(() => expect(update).toHaveBeenCalledWith('4', expect.objectContaining({
    status: 'draft',
    expires_at: new Date('2026-09-30T18:00').toISOString(),
    body_blocks: [{ type: 'text', text: 'Tonight' }],
  })))

  fireEvent.click(screen.getByRole('button', { name: 'Submit for review' }))
  await waitFor(() => expect(update).toHaveBeenLastCalledWith('4', expect.objectContaining({ status: 'pending_review' })))
})

test('admin page editor preserves blocks and publishes explicitly', async () => {
  const page = { id: 8, author_id: 2, title: 'About', slug: 'about', status: 'draft', body: 'About us', body_blocks: [{ type: 'text', text: 'About us' }] }
  vi.spyOn(pageService, 'get').mockResolvedValue(page)
  const update = vi.spyOn(pageService, 'update').mockResolvedValue({ ...page, status: 'published' })

  withUser(<Routes><Route path="/dashboard/pages/:id/edit" element={<PageEditor />} /></Routes>, { id: 3, role: 'admin' }, '/dashboard/pages/8/edit')

  fireEvent.click(await screen.findByRole('button', { name: 'Publish' }))
  await waitFor(() => expect(update).toHaveBeenCalledWith('8', {
    title: 'About', slug: 'about', status: 'published', body_blocks: [{ type: 'text', text: 'About us' }],
  }))
})

test('publisher sees a submitted announcement as read-only', async () => {
  vi.spyOn(announcementService, 'get').mockResolvedValue({ id: 5, author_id: 1, title: 'Submitted', status: 'pending_review', expires_at: null, body: 'Wait', body_blocks: [{ type: 'text', text: 'Wait' }] })

  withUser(<Routes><Route path="/dashboard/announcements/:id/edit" element={<AnnouncementEditor />} /></Routes>, undefined, '/dashboard/announcements/5/edit')

  expect(await screen.findByLabelText('Title')).toBeDisabled()
  expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument()
})
