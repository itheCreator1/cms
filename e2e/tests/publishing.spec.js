import { randomUUID } from 'node:crypto'
import { expect, test } from '@playwright/test'

const users = {
  publisher: { email: 'publisher.e2e@example.test', password: 'publisher e2e test password' },
  admin: { email: 'admin.e2e@example.test', password: 'admin e2e test password' },
  superadmin: { email: 'superadmin.e2e@example.test', password: 'superadmin e2e test password' },
}
const api = 'http://backend:5000/api'

async function login(page, role, heading = 'Dashboard') {
  await page.goto(role === 'superadmin' ? '/system-access' : '/login')
  await page.getByLabel('Email', { exact: true }).fill(users[role].email)
  await page.getByLabel('Password', { exact: true }).fill(users[role].password)
  const response = page.waitForResponse((item) => item.url().endsWith(role === 'superadmin' ? '/api/superadmin-login' : '/api/login') && item.request().method() === 'POST')
  await page.getByRole('button', { name: role === 'superadmin' ? 'Enter system' : 'Log in', exact: true }).click()
  const result = await response
  expect(result.status(), `${role} login: ${JSON.stringify(await result.json())}`).toBe(200)
  await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible()
}

function watchStartup(page) {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('requestfailed', (request) => {
    if (request.resourceType() === 'script') errors.push(`Module failed: ${request.url()}`)
  })
  page.on('response', (response) => {
    if (response.request().resourceType() === 'script' && response.status() >= 400) {
      errors.push(`Module HTTP ${response.status()}: ${response.url()}`)
    }
  })
  return errors
}

async function loadedImage(page, description) {
  const image = page.getByRole('img', { name: description, exact: true })
  await expect(image).toBeVisible()
  await expect.poll(() => image.evaluate((element) => element.complete && element.naturalWidth > 0)).toBe(true)
}

test('public startup and both real login flows work without failed modules', async ({ page }) => {
  const errors = watchStartup(page)
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Stories that keep us connected.' })).toBeVisible()
  await expect(page.getByText('Loading', { exact: false })).toHaveCount(0)
  await page.goto('/dashboard/articles')
  await expect(page).toHaveURL(/\/login$/)
  await login(page, 'publisher', /^(Dashboard|Articles)$/)
  await page.reload()
  await expect(page.getByRole('heading', { name: /^(Dashboard|Articles)$/ })).toBeVisible()
  await page.getByRole('button', { name: 'Log out', exact: true }).click()
  await login(page, 'superadmin')
  expect(errors).toEqual([])
})

test('publisher picture becomes public only after review and publication, then private on unpublish', async ({ browser, page, request }) => {
  const slug = `journey-${randomUUID()}`
  const title = `Publishing journey ${slug}`
  const description = 'A blue test picture'
  const errors = watchStartup(page)
  const adminContext = await browser.newContext()
  const visitorContext = await browser.newContext()
  const admin = await adminContext.newPage()
  const visitor = await visitorContext.newPage()
  const adminErrors = watchStartup(admin)
  const visitorErrors = watchStartup(visitor)
  try {
    await login(page, 'publisher')
    await page.goto('/dashboard/articles/new')
    await page.getByLabel('Title', { exact: true }).fill(title)
    await page.getByLabel('Slug', { exact: true }).fill(slug)
    await page.locator('#article-category').selectOption({ label: 'E2E News' }, { timeout: 5000 })
    await page.getByLabel('Body', { exact: true }).fill('Opening paragraph from the publisher.')
    await page.getByLabel('Picture description', { exact: true }).fill(description)
    const upload = page.waitForResponse((response) => response.url().endsWith('/api/media/uploads') && response.request().method() === 'POST', { timeout: 10000 })
    await page.locator('#article-picture').setInputFiles({
      name: 'picture.png',
      mimeType: 'image/png',
      buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=', 'base64'),
    }, { timeout: 5000 })
    const uploaded = await upload
    expect(uploaded.status()).toBe(201)
    const picture = (await uploaded.json()).item
    const imageUrl = new URL(picture.url, api).href
    await loadedImage(page, description)
    expect((await request.get(imageUrl)).status()).toBe(404)
    await page.getByRole('button', { name: 'Add section', exact: true }).click()
    await page.getByLabel('Text section 3', { exact: true }).fill('Closing paragraph after the picture.')
    await page.getByRole('button', { name: 'Save draft', exact: true }).click()
    await expect(page).toHaveURL(/\/dashboard\/articles\/\d+\/edit$/)
    const editPath = new URL(page.url()).pathname
    expect((await request.get(`${api}/articles/slug/${slug}`)).status()).toBe(404)
    await page.getByRole('button', { name: 'Submit for review', exact: true }).click()
    await expect(page.getByLabel('Title', { exact: true })).toBeDisabled()
    expect((await request.get(imageUrl)).status()).toBe(404)

    await login(admin, 'admin')
    await admin.goto(`http://frontend:5173${editPath}`)
    await loadedImage(admin, description)
    await admin.getByRole('button', { name: 'Publish', exact: true }).click()
    await expect(admin.getByRole('button', { name: 'Unpublish', exact: true })).toBeVisible()

    await visitor.goto('http://frontend:5173/')
    await visitor.getByRole('link', { name: title, exact: true }).click()
    await expect(visitor.getByRole('heading', { name: title, exact: true })).toBeVisible()
    await expect(visitor.getByText('Opening paragraph from the publisher.', { exact: true })).toBeVisible()
    await expect(visitor.getByText('Closing paragraph after the picture.', { exact: true })).toBeVisible()
    await loadedImage(visitor, description)
    const publicImage = await request.get(imageUrl)
    expect(publicImage.status()).toBe(200)
    expect(publicImage.headers()['content-type']).toContain('image/png')
    const published = await request.get(`${api}/articles/slug/${slug}`)
    expect(published.status()).toBe(200)
    expect((await published.json()).item.body_blocks.map((block) => block.type)).toEqual(['text', 'image', 'text'])

    await admin.getByRole('button', { name: 'Unpublish', exact: true }).click()
    await expect(admin.getByRole('button', { name: 'Publish', exact: true })).toBeVisible()
    expect((await request.get(imageUrl)).status()).toBe(404)
    expect((await request.get(`${api}/articles/slug/${slug}`)).status()).toBe(404)
    await visitor.reload()
    await expect(visitor.getByRole('heading', { name: 'Story not found', exact: true })).toBeVisible()
    await visitor.goto('http://frontend:5173/')
    await expect(visitor.getByText('Loading', { exact: false })).toHaveCount(0)
    await expect(visitor.getByRole('link', { name: title, exact: true })).toHaveCount(0)
    await page.reload()
    await loadedImage(page, description)
    expect([...errors, ...adminErrors, ...visitorErrors]).toEqual([])
  } finally {
    await adminContext.close()
    await visitorContext.close()
  }
})

test('an admin publishes a page that renders through PageView on direct navigation', async ({ page, browser }) => {
  const slug = `page-${randomUUID()}`
  const errors = watchStartup(page)
  await login(page, 'admin')
  await page.goto('/dashboard/pages/new')
  await page.getByLabel('Title', { exact: true }).fill('E2E published page')
  await page.getByLabel('Slug', { exact: true }).fill(slug)
  await page.getByLabel('Text section 1', { exact: true }).fill('A real published page body.')
  await page.getByRole('button', { name: 'Save draft', exact: true }).click()
  await expect(page).toHaveURL(/\/dashboard\/pages\/\d+\/edit$/)
  await page.getByRole('button', { name: 'Publish', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Unpublish', exact: true })).toBeVisible()
  const visitorContext = await browser.newContext()
  try {
    const visitor = await visitorContext.newPage()
    const visitorErrors = watchStartup(visitor)
    await visitor.goto(`http://frontend:5173/pages/${slug}`)
    await expect(visitor.getByRole('heading', { name: 'E2E published page', exact: true })).toBeVisible()
    await expect(visitor.getByText('A real published page body.', { exact: true })).toBeVisible()
    expect([...errors, ...visitorErrors]).toEqual([])
  } finally {
    await visitorContext.close()
  }
})
