import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { expect, test, vi } from 'vitest'

import { settingsService } from '../services/settings'
import Home from '../pages/public/Home'
import SiteShell from './SiteShell'

test('saved settings appear in site chrome and homepage intro', async () => {
  vi.spyOn(settingsService, 'get').mockResolvedValue({
    site_name: 'Local Journal', tagline: 'Every day',
    homepage_headline: 'Your stories', homepage_intro: 'Shared locally.',
  })
  render(<MemoryRouter><Routes><Route element={<SiteShell navigationItems={[]} />}><Route index element={<Home />} /></Route></Routes></MemoryRouter>)
  expect(await screen.findByRole('heading', { name: 'Your stories' })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Local Journal home' })).toBeInTheDocument()
  expect(screen.getByText('Shared locally.')).toBeInTheDocument()
  expect(screen.getAllByText('Every day')).toHaveLength(2)
})
