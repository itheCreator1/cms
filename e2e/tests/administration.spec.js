import { randomUUID } from 'node:crypto'
import { expect, test } from '@playwright/test'

const api = 'http://backend:5000/api'
const accounts = {
  publisher: ['publisher.e2e@example.test', 'publisher e2e test password'],
  admin: ['admin.e2e@example.test', 'admin e2e test password'],
  superadmin: ['superadmin.e2e@example.test', 'superadmin e2e test password'],
}

async function login(page, role) {
  await page.goto(role === 'superadmin' ? '/system-access' : '/login')
  await page.getByLabel('Email', { exact: true }).fill(accounts[role][0])
  await page.getByLabel('Password', { exact: true }).fill(accounts[role][1])
  await page.getByRole('button', { name: role === 'superadmin' ? 'Enter system' : 'Log in' }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  return page.evaluate(() => localStorage.getItem('cms_access_token'))
}

test('Admin manages taxonomy, media, and Publisher users', async ({ page, request }) => {
  const suffix = randomUUID().slice(0, 8)
  const token = await login(page, 'admin')
  await page.goto('/dashboard/categories')
  await expect(page.getByRole('heading', { name: 'Categories' })).toBeVisible()
  await page.getByLabel('Name').fill(`News ${suffix}`)
  await page.getByLabel('Slug').fill(`news-${suffix}`)
  await page.getByRole('button', { name: 'Create category' }).click()
  await expect(page.getByRole('button', { name: `Edit News ${suffix}` })).toBeVisible()
  await page.getByRole('button', { name: `Edit News ${suffix}` }).click()
  await page.getByLabel('Name').fill(`Updated ${suffix}`)
  await page.getByRole('button', { name: 'Save category' }).click()
  await expect(page.getByRole('button', { name: `Edit Updated ${suffix}` })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete Updated ${suffix}` }).click()
  await expect(page.getByRole('button', { name: `Edit Updated ${suffix}` })).toHaveCount(0)
  await page.goto('/dashboard/tags')
  await page.getByLabel('Name').fill(`Tag ${suffix}`)
  await page.getByLabel('Slug').fill(`tag-${suffix}`)
  await page.getByRole('button', { name: 'Create tag' }).click()
  await expect(page.getByRole('button', { name: `Edit Tag ${suffix}` })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete Tag ${suffix}` }).click()
  await expect(page.getByRole('button', { name: `Edit Tag ${suffix}` })).toHaveCount(0)
  await page.goto('/dashboard/media')
  await page.getByLabel('HTTPS URL').fill(`https://media-${suffix}.example.com/`)
  await page.getByRole('button', { name: 'Add link' }).click()
  await expect(page.getByRole('button', { name: `Edit media-${suffix}.example.com` })).toBeVisible()
  await page.getByRole('button', { name: `Edit media-${suffix}.example.com` }).click()
  await page.getByLabel('Alt text').fill(`Media ${suffix}`)
  await page.getByRole('button', { name: 'Save media' }).click()
  await expect(page.getByText(`Media ${suffix}`)).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete media-${suffix}.example.com` }).click()
  await expect(page.getByRole('button', { name: `Edit media-${suffix}.example.com` })).toHaveCount(0)
  await page.locator('input[type="file"]').setInputFiles({
    name: `image-${suffix}.png`, mimeType: 'image/png',
    buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=', 'base64'),
  })
  await page.locator('button', { hasText: 'Upload image' }).click()
  await expect(page.getByRole('button', { name: `Edit image-${suffix}.png` })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete image-${suffix}.png` }).click()
  await page.goto('/dashboard/users')
  await page.getByLabel('Email').fill(`user-${suffix}@example.test`)
  await page.getByLabel('Password').fill('publisher test password')
  await page.getByRole('button', { name: 'Create user' }).click()
  await expect(page.getByRole('button', { name: `Edit user-${suffix}@example.test` })).toBeVisible()
  await page.getByRole('button', { name: `Edit user-${suffix}@example.test` }).click()
  await page.getByLabel('Email').fill(`revised-${suffix}@example.test`)
  await page.getByRole('button', { name: 'Save user' }).click()
  await expect(page.getByRole('button', { name: `Edit revised-${suffix}@example.test` })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete revised-${suffix}@example.test` }).click()
  await expect(page.getByRole('button', { name: `Edit revised-${suffix}@example.test` })).toHaveCount(0)
  expect(await request.post(`${api}/users`, { headers: { Authorization: `Bearer ${token}` }, data: { email: `admin-${suffix}@example.test`, password: 'admin test password', role: 'admin' } }).then((response) => response.status())).toBe(403)
})

test('Publisher cannot open administration routes; Superadmin settings reach public site', async ({ page, browser, request }) => {
  const suffix = randomUUID().slice(0, 8)
  const publisherToken = await login(page, 'publisher')
  await page.goto('/dashboard/users')
  await expect(page).toHaveURL('http://frontend:5173/')
  expect((await request.put(`${api}/settings`, { headers: { Authorization: `Bearer ${publisherToken}` }, data: { site_name: 'Denied' } })).status()).toBe(403)
  await page.getByRole('button', { name: 'Log out' }).click()
  await login(page, 'superadmin')
  await page.goto('/dashboard/users')
  await expect(page.getByRole('option', { name: 'Admin', exact: true })).toBeAttached()
  await page.getByLabel('Email').fill(`new-admin-${suffix}@example.test`)
  await page.getByLabel('Password').fill('admin test password')
  await page.getByLabel('Role').selectOption('admin')
  await page.getByRole('button', { name: 'Create user' }).click()
  await expect(page.getByRole('button', { name: `Edit new-admin-${suffix}@example.test` })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: `Delete new-admin-${suffix}@example.test` }).click()
  await page.goto('/dashboard/settings')
  const name = `Journal ${suffix}`
  await page.getByLabel('Site name').fill(name)
  await page.getByLabel('Homepage headline').fill(`Headlines ${suffix}`)
  await page.getByRole('button', { name: 'Save settings' }).click()
  const visitor = await browser.newPage()
  try {
    await visitor.goto('http://frontend:5173/')
    await expect(visitor.getByRole('heading', { name: `Headlines ${suffix}` })).toBeVisible()
    await expect(visitor.getByRole('link', { name: `${name} home` })).toBeVisible()
  } finally {
    await visitor.close()
    await page.getByLabel('Site name').fill('CMS')
    await page.getByLabel('Homepage headline').fill('Stories that keep us connected.')
    await page.getByRole('button', { name: 'Save settings' }).click()
  }
})
