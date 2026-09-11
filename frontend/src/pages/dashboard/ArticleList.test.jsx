import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test, vi } from 'vitest'

import { AuthContext } from '../../context/AuthContext'
import { articleService } from '../../services/articles'
import ArticleList from './ArticleList'

vi.mock('../../services/articles', () => ({ articleService: { list: vi.fn() } }))

test('publisher filters their articles by status', async () => {
  vi.spyOn(articleService, 'list').mockResolvedValue([
    { id: 1, author_id: 1, title: 'Draft article', status: 'draft' },
    { id: 2, author_id: 1, title: 'Submitted article', status: 'pending_review' },
    { id: 3, author_id: 2, title: 'Another author article', status: 'draft' },
  ])

  render(<AuthContext.Provider value={{ user: { id: 1, role: 'publisher' } }}><MemoryRouter><ArticleList /></MemoryRouter></AuthContext.Provider>)

  expect(await screen.findByText('Draft article')).toBeInTheDocument()
  expect(screen.queryByText('Another author article')).not.toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'pending_review' } })
  expect(screen.getByText('Submitted article')).toBeInTheDocument()
  expect(screen.queryByText('Draft article')).not.toBeInTheDocument()
})
