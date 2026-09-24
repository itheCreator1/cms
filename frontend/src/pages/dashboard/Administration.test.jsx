import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import { AuthContext } from '../../context/AuthContext'
import { categoryService } from '../../services/categories'
import { userService } from '../../services/users'
import { settingsService } from '../../services/settings'
import TaxonomyManager from './TaxonomyManager'
import ManageUsers from './ManageUsers'
import ManageSettings from './ManageSettings'
import MediaLibrary from './MediaLibrary'
import { mediaService } from '../../services/media'

afterEach(() => vi.restoreAllMocks())

function withRole(view, role = 'admin') {
  return render(<AuthContext.Provider value={{ user: { id: 1, role } }}><MemoryRouter>{view}</MemoryRouter></AuthContext.Provider>)
}

test('category screen creates, edits, and reports API conflicts', async () => {
  vi.spyOn(categoryService, 'list').mockResolvedValue([{ id: 2, name: 'News', slug: 'news' }])
  vi.spyOn(categoryService, 'create').mockResolvedValue({ id: 3, name: 'Culture', slug: 'culture' })
  vi.spyOn(categoryService, 'update').mockRejectedValue(new Error('Name or slug is already in use'))
  withRole(<TaxonomyManager kind="category" service={categoryService} />)
  expect(await screen.findByRole('button', { name: 'Edit News' })).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Culture' } })
  fireEvent.change(screen.getByLabelText('Slug'), { target: { value: 'culture' } })
  fireEvent.click(screen.getByRole('button', { name: 'Create category' }))
  await waitFor(() => expect(categoryService.create).toHaveBeenCalledWith({ name: 'Culture', slug: 'culture' }))
  fireEvent.click(screen.getByRole('button', { name: 'Edit News' }))
  fireEvent.click(screen.getByRole('button', { name: 'Save category' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Name or slug is already in use')
})

test('taxonomy screen retries a failed load and reports delete conflicts', async () => {
  vi.spyOn(categoryService, 'list').mockRejectedValueOnce(new Error('Temporarily unavailable')).mockResolvedValue([{ id: 7, name: 'Used', slug: 'used' }])
  vi.spyOn(categoryService, 'delete').mockRejectedValue(new Error('Resource is in use'))
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  withRole(<TaxonomyManager kind="category" service={categoryService} />)
  expect(await screen.findByRole('alert')).toHaveTextContent('Temporarily unavailable')
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
  fireEvent.click(await screen.findByRole('button', { name: 'Delete Used' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Resource is in use')
})

test('admin user screen offers Publisher role only', async () => {
  vi.spyOn(userService, 'list').mockResolvedValue([])
  withRole(<ManageUsers />)
  expect(await screen.findByRole('heading', { name: 'Users' })).toBeInTheDocument()
  expect(screen.getByRole('option', { name: 'Publisher' })).toBeInTheDocument()
  expect(screen.queryByRole('option', { name: 'Admin' })).not.toBeInTheDocument()
})

test('settings screen saves changes and shows API errors', async () => {
  vi.spyOn(settingsService, 'get').mockResolvedValue({ site_name: 'CMS', tagline: 'Daily', homepage_headline: 'Stories', homepage_intro: 'Intro' })
  vi.spyOn(settingsService, 'update').mockRejectedValue(new Error('Invalid settings data'))
  withRole(<ManageSettings />, 'superadmin')
  fireEvent.change(await screen.findByLabelText('Site name'), { target: { value: '' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save settings' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid settings data')
})

test('media library creates HTTPS links and edits metadata', async () => {
  vi.spyOn(mediaService, 'list').mockResolvedValue([{ id: 4, filename: 'example.com', url: 'https://example.com/a', source_type: 'external', alt_text: 'Old' }])
  vi.spyOn(mediaService, 'createLink').mockResolvedValue({ id: 5 })
  vi.spyOn(mediaService, 'update').mockResolvedValue({ id: 4 })
  withRole(<MediaLibrary />)
  expect(await screen.findByRole('button', { name: 'Edit example.com' })).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('HTTPS URL'), { target: { value: 'https://example.com/b' } })
  fireEvent.click(screen.getByRole('button', { name: 'Add link' }))
  await waitFor(() => expect(mediaService.createLink).toHaveBeenCalledWith(expect.objectContaining({ url: 'https://example.com/b' })))
  fireEvent.click(screen.getByRole('button', { name: 'Edit example.com' }))
  fireEvent.change(screen.getByLabelText('Alt text'), { target: { value: 'New' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save media' }))
  await waitFor(() => expect(mediaService.update).toHaveBeenCalledWith(4, expect.objectContaining({ alt_text: 'New' })))
})
