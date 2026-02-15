---
title: "E2E Testing Critical Flows with Playwright"
category: "testing"
subcategory: "e2e-testing"
tags: ["playwright", "e2e", "end-to-end", "critical-flows", "regression-testing"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## E2E Testing Critical Flows with Playwright

End-to-end tests verify complete user workflows across the full application stack from browser UI to backend services. Playwright executes tests in real browsers (Chromium, Firefox, WebKit) with automatic waiting, network interception, and visual regression testing. E2E tests catch integration bugs that unit and component tests miss including routing, data fetching, SSR/CSR boundaries, and cross-page workflows.

Playwright provides better Next.js App Router support, multi-browser testing, auto-waiting without manual timeouts, parallel test execution, and network mocking without third-party libraries. Next.js documentation officially recommends Playwright for App Router applications. Cypress requires workarounds for server components and struggles with streaming/Suspense patterns. Analyzed Next.js codebases (helix, kariusdx, policy-node) have zero E2E tests. Source confidence: 0% (gap pattern).

Critical flows for analyzed codebases include: preview mode workflow (Sanity CMS integration), ISR revalidation verification, i18n language switching (policy-node), search functionality, form submissions, authentication flows, and navigation across nested layouts. Each critical flow represents a potential regression point when changing routing, data fetching, or component architecture.

## Playwright Installation and Next.js Configuration

Install Playwright test runner and browsers: `npm install -D @playwright/test && npx playwright install chromium firefox`. Playwright configuration defines test directory, parallelization, retry logic, browser projects, and Next.js dev server integration.

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e', fullyParallel: true, forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0, workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: { baseURL: 'http://localhost:3000', trace: 'on-first-retry', screenshot: 'only-on-failure' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ],
  webServer: {
    command: 'npm run dev', url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI, timeout: 120000
  }
})
```

Configuration starts Next.js dev server automatically via `webServer`. Tests run in parallel (`fullyParallel: true`). Retries (`retries: 2`) handle flaky tests in CI. Traces and screenshots captured only on failures minimize storage. Multiple browser projects ensure cross-browser compatibility.

## Testing Preview Mode Workflow with Playwright

Sanity-based Next.js applications (helix, policy-node) implement preview mode for content editors to preview unpublished changes. Preview mode workflow: navigate to preview API route, set preview cookies, redirect to content page, verify draft content, exit preview mode.

```typescript
import { test, expect } from '@playwright/test'

test.describe('Preview Mode', () => {
  test('enables preview mode', async ({ page, context }) => {
    await page.goto('/api/preview?secret=test-secret&slug=draft-page')
    const c = await context.cookies()
    expect(c.find(x => x.name === '__previewData')).toBeDefined()
    await expect(page).toHaveURL('/draft-page')
    await expect(page.getByText(/draft content/i)).toBeVisible()
  })

  test('exits preview mode', async ({ page, context }) => {
    await page.goto('/api/preview?secret=test-secret&slug=test-page')
    await page.waitForURL('/test-page')
    await page.getByRole('button', { name: /exit/i }).click()
    const c = await context.cookies()
    expect(c.find(x => x.name === '__previewData')).toBeUndefined()
    await expect(page.getByText(/draft/i)).not.toBeVisible()
  })
})
```

Test navigates through API routes, verifies cookies, and checks redirects. `page.waitForURL()` waits for navigation. `context.cookies()` accesses browser cookies. Test both enabling and disabling preview mode.

## Testing ISR Revalidation with Playwright

Incremental Static Regeneration generates static pages with revalidation intervals. E2E test verifies page is statically generated, content updates after revalidation, and stale content is replaced. ISR adoption: 100% across analyzed codebases (60s, 3600s, 43200s periods).

```typescript
import { test, expect } from '@playwright/test'

test.describe('ISR', () => {
  test('serves static page with ISR', async ({ page }) => {
    await page.goto('/blog/test-post')
    const r = await page.goto('/blog/test-post')
    expect(r?.headers()['x-nextjs-cache']).toBe('HIT')
  })

  test('revalidates on demand', async ({ page, request }) => {
    const r = await request.post('/api/revalidate', { data: { secret: 'x', path: '/blog/test-post' } })
    expect(r.ok()).toBeTruthy()
    const r1 = await page.goto('/blog/test-post')
    expect(r1?.headers()['x-nextjs-cache']).toBe('MISS')
    const r2 = await page.goto('/blog/test-post')
    expect(r2?.headers()['x-nextjs-cache']).toBe('HIT')
  })
})
```

Test checks Next.js cache headers (`x-nextjs-cache`) to verify ISR behavior. `request.post()` triggers on-demand revalidation. First request after revalidation shows MISS (regenerated), subsequent show HIT (cached).

## Testing i18n Language Switching with Playwright

Policy-node implements i18n with [lang] route parameter and middleware. E2E test verifies language switcher updates URL, content language changes, and language preference persists across navigation. i18n adoption: 33% (policy-node only).

```typescript
import { test, expect } from '@playwright/test'

test.describe('i18n', () => {
  test('switches language', async ({ page }) => {
    await page.goto('/en-US')
    await page.getByRole('button', { name: /language/i }).click()
    await page.getByRole('menuitem', { name: /français/i }).click()
    await expect(page).toHaveURL('/fr')
    await expect(page.getByRole('heading', { name: /bienvenue/i })).toBeVisible()
  })

  test('persists language across navigation', async ({ page }) => {
    await page.goto('/es')
    await page.getByRole('link', { name: /acerca/i }).click()
    await expect(page).toHaveURL(/^\/es\//)
  })

  test('uses Accept-Language header', async ({ page, context }) => {
    await context.setExtraHTTPHeaders({ 'Accept-Language': 'it,en;q=0.9' })
    await page.goto('/')
    await expect(page).toHaveURL(/^\/it\//)
  })
})
```

Test language switcher UI with `getByRole('menuitem')`. Verify URL changes match selected language. Test Accept-Language header detection for automatic locale selection. Ensure language preference persists across navigation.

## Testing Search Functionality with Playwright

Search features span multiple components: search input, autocomplete, results page, filters, pagination. E2E test verifies complete search workflow from query input to results display including debouncing, filtering, and result accuracy.

```typescript
import { test, expect } from '@playwright/test'

test.describe('Search', () => {
  test('searches and displays results', async ({ page }) => {
    await page.goto('/')
    const s = page.getByRole('searchbox', { name: /search/i })
    await s.fill('React')
    await expect(page.getByRole('option', { name: /react/i })).toBeVisible({ timeout: 1000 })
    await s.press('Enter')
    await expect(page).toHaveURL(/\/search\?q=React/)
    await expect(page.getByRole('article')).toHaveCount(10)
  })

  test('filters by category', async ({ page }) => {
    await page.goto('/search?q=JS')
    await page.getByRole('checkbox', { name: /tutorials/i }).check()
    await page.waitForURL(/category=tutorials/)
    await expect(page.getByRole('article').first()).toContainText('Tutorial')
  })
})
```

Test debounced autocomplete with `toBeVisible({ timeout: 1000 })`. Submit search via Enter key. Verify URL query parameters updated correctly. Test filters to ensure search state management works.

## Testing Form Submissions with Playwright

Forms require E2E tests for validation, submission, error handling, and success feedback. Test both client-side and server-side validation.

```typescript
import { test, expect } from '@playwright/test'

test.describe('Form', () => {
  test('validates fields', async ({ page }) => {
    await page.goto('/contact')
    await page.getByRole('button', { name: /submit/i }).click()
    await expect(page.getByText(/required/i)).toBeVisible()
  })

  test('submits successfully', async ({ page }) => {
    await page.goto('/contact')
    await page.getByLabel(/name/i).fill('J')
    await page.getByLabel(/email/i).fill('j@x.com')
    await page.getByLabel(/message/i).fill('T')
    await page.route('/api/contact', r => r.fulfill({ status: 200, body: JSON.stringify({ ok: true }) }))
    await page.getByRole('button', { name: /submit/i }).click()
    await expect(page.getByText(/success/i)).toBeVisible()
  })

  test('displays error', async ({ page }) => {
    await page.goto('/contact')
    await page.getByLabel(/email/i).fill('t@x.com')
    await page.route('/api/contact', r => r.fulfill({ status: 500, body: JSON.stringify({ error: 'E' }) }))
    await page.getByRole('button', { name: /submit/i }).click()
    await expect(page.getByText(/failed/i)).toBeVisible()
  })
})
```

Use `page.route()` to mock API responses. Test both success (200) and error (500) responses. Verify UI updates for validation errors, success messages, and server errors.

## Testing Navigation and Nested Layouts with Playwright

App Router nested layouts require E2E tests verifying layout persistence across navigation, parallel routes, and intercepting routes. Helix-dot-com-next uses nested layouts with (frontend)/(studio) route groups.

```typescript
// e2e/navigation.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('preserves header layout across page navigation', async ({ page }) => {
    await page.goto('/')
    const h = page.getByRole('banner')
    await expect(h).toBeVisible()
    await page.getByRole('link', { name: /about/i }).click()
    await expect(page).toHaveURL('/about')
    await expect(h).toBeVisible()
  })

  test('updates active navigation link on page change', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('link', { name: /home/i })).toHaveAttribute('aria-current', 'page')
    await page.getByRole('link', { name: /about/i }).click()
    await expect(page.getByRole('link', { name: /about/i })).toHaveAttribute('aria-current', 'page')
    await expect(page.getByRole('link', { name: /home/i })).not.toHaveAttribute('aria-current')
  })
})
```

Test verifies shared layout components (header, footer, sidebar) persist across navigation. Check `aria-current` attribute for active navigation state. Ensure client-side navigation doesn't full-page refresh.

## E2E Testing Best Practices

**Isolate tests:** Each test should be independent and runnable in any order. Use `test.beforeEach` to set up clean state.

**Use data-testid sparingly:** Prefer accessible queries (`getByRole`, `getByLabel`) over test IDs. Test IDs couple tests to implementation.

**Mock external APIs:** Use `page.route()` to mock third-party APIs (Sanity, Stripe, analytics) for consistent test data.

**Test in multiple browsers:** Playwright's multi-project configuration runs tests in Chromium, Firefox, and WebKit automatically.

**Debug with UI mode:** Run `npx playwright test --ui` for interactive debugging with time-travel and network inspection.

## E2E Testing Coverage Goals

**Critical flows (authentication, checkout, preview mode):** 100% coverage
**High-traffic pages (homepage, landing pages):** 80% coverage
**Secondary flows (search, filtering, pagination):** 60% coverage

Analyzed codebases require estimated 10-15 E2E tests covering preview mode (helix, policy-node), ISR revalidation (all 3 repos), i18n switching (policy-node), navigation (all 3 repos), and search/filter flows. Start with highest-risk user journeys and expand coverage incrementally.
