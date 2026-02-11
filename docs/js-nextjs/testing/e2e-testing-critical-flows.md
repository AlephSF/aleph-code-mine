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

### Why Playwright Over Cypress

Playwright provides better Next.js App Router support, multi-browser testing (Chromium, Firefox, WebKit), auto-waiting without manual timeouts, parallel test execution, and network mocking without third-party libraries. Next.js documentation officially recommends Playwright for App Router applications. Cypress requires workarounds for server components and struggles with streaming/Suspense patterns. Analyzed Next.js codebases (helix, kariusdx, policy-node) have zero E2E tests. Source confidence: 0% (gap pattern - no E2E infrastructure exists).

### Critical Flows Requiring E2E Tests

Identify high-value user journeys that combine multiple features and pages. Critical flows for analyzed codebases include: preview mode workflow (Sanity CMS integration), ISR revalidation verification, i18n language switching (policy-node), search functionality, form submissions, authentication flows (if present), and navigation across nested layouts. Each critical flow represents a potential regression point when changing routing, data fetching, or component architecture.

### Playwright Installation and Configuration

Install Playwright test runner and browsers with: `npm install -D @playwright/test && npx playwright install chromium firefox`. Playwright configuration defines test directory, parallelization, retry logic, browser projects, and Next.js dev server integration. Configuration file: `playwright.config.ts`.

#### Playwright Configuration for Next.js

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
```

Configuration starts Next.js dev server automatically via `webServer`. Tests run in parallel (`fullyParallel: true`) for speed. Retries (`retries: 2`) handle flaky tests in CI. Traces and screenshots captured only on failures minimize storage. Multiple browser projects ensure cross-browser compatibility.

### Testing Preview Mode Workflow

Sanity-based Next.js applications (helix, policy-node) implement preview mode for content editors to preview unpublished changes. Preview mode workflow spans multiple steps: navigate to preview API route, set preview cookies, redirect to content page, verify draft content renders, exit preview mode. E2E test verifies complete workflow end-to-end.

#### Preview Mode E2E Test

```typescript
// e2e/preview-mode.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Preview Mode', () => {
  test('enables preview mode and shows draft content', async ({ page, context }) => {
    // Start on homepage
    await page.goto('/')
    await expect(page.getByRole('heading', { name: /welcome/i })).toBeVisible()

    // Navigate to preview API route with secret and slug
    await page.goto('/api/preview?secret=test-secret&slug=draft-page')

    // Verify preview cookies are set
    const cookies = await context.cookies()
    const previewCookie = cookies.find(c => c.name === '__previewData')
    expect(previewCookie).toBeDefined()

    // Verify redirect to content page
    await expect(page).toHaveURL('/draft-page')

    // Verify draft content renders (content not visible in production)
    await expect(page.getByText(/draft content - not published/i)).toBeVisible()

    // Verify preview mode banner appears
    await expect(page.getByRole('banner', { name: /preview mode/i })).toBeVisible()
  })

  test('exits preview mode and hides draft content', async ({ page, context }) => {
    // Enable preview mode first
    await page.goto('/api/preview?secret=test-secret&slug=test-page')
    await page.waitForURL('/test-page')

    // Click "Exit Preview" button
    await page.getByRole('button', { name: /exit preview/i }).click()

    // Verify preview cookies are cleared
    await page.waitForURL('/test-page')
    const cookies = await context.cookies()
    const previewCookie = cookies.find(c => c.name === '__previewData')
    expect(previewCookie).toBeUndefined()

    // Verify draft content is hidden
    await expect(page.getByText(/draft content/i)).not.toBeVisible()
  })
})
```

Test navigates through API routes, verifies cookies, and checks redirects. `page.waitForURL()` waits for navigation to complete. `context.cookies()` accesses browser cookies for verification. Test both enabling and disabling preview mode to ensure toggle works correctly.

### Testing ISR Revalidation

Incremental Static Regeneration generates static pages with revalidation intervals. E2E test verifies page is statically generated at build time, content updates after revalidation period, and stale content is replaced with fresh data. ISR is adopted 100% across analyzed codebases with various revalidation periods (60s, 3600s, 43200s).

#### ISR Revalidation E2E Test

```typescript
// e2e/isr-revalidation.spec.ts
import { test, expect } from '@playwright/test'

test.describe('ISR Revalidation', () => {
  test('serves static page with ISR revalidation', async ({ page }) => {
    // Navigate to ISR page
    await page.goto('/blog/test-post')

    // Verify page renders with static data
    await expect(page.getByRole('heading')).toBeVisible()

    // Check response headers for cache status
    const response = await page.goto('/blog/test-post')
    const cacheStatus = response?.headers()['x-nextjs-cache']
    expect(cacheStatus).toBe('HIT')  // Served from cache
  })

  test('revalidates page on demand via API route', async ({ page, request }) => {
    // Trigger on-demand revalidation
    const revalidateResponse = await request.post('/api/revalidate', {
      data: { secret: 'test-secret', path: '/blog/test-post' },
    })
    expect(revalidateResponse.ok()).toBeTruthy()

    // Navigate to revalidated page
    const response = await page.goto('/blog/test-post')

    // First request after revalidation generates fresh page
    const cacheStatus = response?.headers()['x-nextjs-cache']
    expect(cacheStatus).toBe('MISS')  // Cache miss, regenerated

    // Second request serves from cache
    const response2 = await page.goto('/blog/test-post')
    const cacheStatus2 = response2?.headers()['x-nextjs-cache']
    expect(cacheStatus2).toBe('HIT')
  })
})
```

Test checks Next.js cache headers (`x-nextjs-cache`) to verify ISR behavior. `request.post()` triggers on-demand revalidation API. First request after revalidation shows MISS (regenerated), subsequent requests show HIT (cached). Tests prevent ISR misconfiguration breaking caching strategy.

### Testing i18n Language Switching

Policy-node implements i18n with [lang] route parameter and middleware. E2E test verifies language switcher updates URL, content language changes, and language preference persists across navigation. i18n patterns are adoption 33% across analyzed codebases (policy-node only).

#### i18n Language Switching E2E Test

```typescript
// e2e/i18n.spec.ts
import { test, expect } from '@playwright/test'

test.describe('i18n Language Switching', () => {
  test('switches language and updates content', async ({ page }) => {
    // Start on English version
    await page.goto('/en-US')
    await expect(page.getByRole('heading', { name: /welcome/i })).toBeVisible()

    // Open language switcher
    await page.getByRole('button', { name: /language/i }).click()

    // Select French
    await page.getByRole('menuitem', { name: /français/i }).click()

    // Verify URL updated to French
    await expect(page).toHaveURL('/fr')

    // Verify content changed to French
    await expect(page.getByRole('heading', { name: /bienvenue/i })).toBeVisible()
  })

  test('persists language preference across navigation', async ({ page }) => {
    // Select Spanish
    await page.goto('/es')
    await expect(page.getByRole('heading', { name: /bienvenida/i })).toBeVisible()

    // Navigate to different page
    await page.getByRole('link', { name: /acerca de/i }).click()

    // Verify still on Spanish version
    await expect(page).toHaveURL(/^\/es\//)
    await expect(page.getByRole('heading', { name: /acerca de/i })).toBeVisible()
  })

  test('uses Accept-Language header for initial locale', async ({ page, context }) => {
    // Set Accept-Language header
    await context.setExtraHTTPHeaders({
      'Accept-Language': 'it,en;q=0.9',
    })

    // Navigate to root (no locale in URL)
    await page.goto('/')

    // Verify redirected to Italian version
    await expect(page).toHaveURL(/^\/it\//)
    await expect(page.getByRole('heading', { name: /benvenuto/i })).toBeVisible()
  })
})
```

Test language switcher UI interaction with `getByRole('menuitem')`. Verify URL changes match selected language. Test Accept-Language header detection for automatic locale selection. Ensure language preference persists across page navigation.

### Testing Search Functionality

Search features span multiple components: search input, autocomplete suggestions, results page, filters, pagination. E2E test verifies complete search workflow from query input to results display including debouncing, filtering, and result accuracy.

#### Search Flow E2E Test

```typescript
// e2e/search.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Search Functionality', () => {
  test('searches content and displays results', async ({ page }) => {
    await page.goto('/')

    // Enter search query
    const searchInput = page.getByRole('searchbox', { name: /search/i })
    await searchInput.fill('React')

    // Wait for autocomplete suggestions (debounced)
    await expect(page.getByRole('option', { name: /react hooks/i })).toBeVisible({ timeout: 1000 })

    // Submit search
    await searchInput.press('Enter')

    // Verify redirected to search results page
    await expect(page).toHaveURL(/\/search\?q=React/)

    // Verify results rendered
    const results = page.getByRole('article')
    await expect(results).toHaveCount(10)  // First page shows 10 results

    // Verify search query displayed
    await expect(page.getByText(/results for "React"/i)).toBeVisible()
  })

  test('filters search results by category', async ({ page }) => {
    await page.goto('/search?q=JavaScript')

    // Verify initial results count
    await expect(page.getByRole('article')).toHaveCount(10)

    // Apply filter
    await page.getByRole('checkbox', { name: /tutorials/i }).check()

    // Wait for filtered results
    await page.waitForURL(/category=tutorials/)

    // Verify results updated
    const filteredResults = page.getByRole('article')
    await expect(filteredResults.first()).toContainText('Tutorial')
  })
})
```

Test debounced autocomplete with `toBeVisible({ timeout: 1000 })`. Submit search via Enter key or button click. Verify URL query parameters updated correctly. Test filters and pagination to ensure search state management works correctly.

### Testing Form Submissions

Forms require E2E tests for validation, submission, error handling, and success feedback. Test both client-side validation (immediate feedback) and server-side validation (API errors).

#### Form Submission E2E Test

```typescript
// e2e/contact-form.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Contact Form', () => {
  test('validates required fields before submission', async ({ page }) => {
    await page.goto('/contact')

    // Submit empty form
    await page.getByRole('button', { name: /submit/i }).click()

    // Verify validation errors appear
    await expect(page.getByText(/email is required/i)).toBeVisible()
    await expect(page.getByText(/message is required/i)).toBeVisible()
  })

  test('submits form successfully with valid data', async ({ page }) => {
    await page.goto('/contact')

    // Fill form
    await page.getByLabel(/name/i).fill('John Doe')
    await page.getByLabel(/email/i).fill('john@example.com')
    await page.getByLabel(/message/i).fill('Test message content')

    // Intercept form submission API call
    await page.route('/api/contact', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, id: '123' }),
      })
    })

    // Submit form
    await page.getByRole('button', { name: /submit/i }).click()

    // Verify success message
    await expect(page.getByText(/message sent successfully/i)).toBeVisible()

    // Verify form cleared
    await expect(page.getByLabel(/name/i)).toHaveValue('')
  })

  test('displays server error on submission failure', async ({ page }) => {
    await page.goto('/contact')

    await page.getByLabel(/email/i).fill('test@example.com')
    await page.getByLabel(/message/i).fill('Test')

    // Mock server error
    await page.route('/api/contact', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error' }),
      })
    })

    await page.getByRole('button', { name: /submit/i }).click()

    // Verify error message displayed
    await expect(page.getByText(/failed to send message/i)).toBeVisible()
  })
})
```

Use `page.route()` to mock API responses without backend. Test both success (200) and error (500) responses. Verify UI updates correctly for validation errors, loading states, success messages, and server errors.

### Testing Navigation and Nested Layouts

App Router's nested layouts require E2E tests verifying layout persistence across navigation, parallel routes, and intercepting routes. Helix-dot-com-next uses nested layouts with (frontend)/(studio) route groups.

#### Navigation E2E Test

```typescript
// e2e/navigation.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('preserves header layout across page navigation', async ({ page }) => {
    await page.goto('/')

    // Verify header exists
    const header = page.getByRole('banner')
    await expect(header).toBeVisible()

    // Navigate to different page
    await page.getByRole('link', { name: /about/i }).click()
    await expect(page).toHaveURL('/about')

    // Verify header still exists (not re-rendered)
    await expect(header).toBeVisible()
  })

  test('updates active navigation link on page change', async ({ page }) => {
    await page.goto('/')

    // Home link is active
    await expect(page.getByRole('link', { name: /home/i })).toHaveAttribute('aria-current', 'page')

    // Navigate to About
    await page.getByRole('link', { name: /about/i }).click()

    // About link is now active
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
