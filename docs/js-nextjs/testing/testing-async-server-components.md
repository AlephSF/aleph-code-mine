---
title: "Testing Async Server Components in Next.js App Router"
category: "testing"
subcategory: "app-router"
tags: ["app-router", "server-components", "async", "vitest", "next15"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Testing Overview

Next.js App Router async server components fetch data during server-side rendering and return JSX asynchronously. Traditional component testing libraries execute in jsdom browser environments and cannot test server-only code directly. Two testing strategies exist: unit test server components as async functions with mocked data sources, or integration test via end-to-end tests with Playwright.

## Server Components Testing Challenge

Async server components execute exclusively on the server and cannot access browser APIs (window, document, localStorage). Testing Library's `render()` runs in jsdom (browser simulation) and cannot execute server-only imports like `next/headers` or database clients. Helix-dot-com-next (Next.js 15) has 20 async server component pages - all untested. Policy-node (Next.js 14) has hybrid App Router + Pages Router - async pages untested. Source confidence: 0% (no server component tests exist in analyzed codebases).

## Unit Testing with Mocked Data

Server components are async functions returning JSX. Unit tests await component function, mock data fetching dependencies at module level, render resolved JSX with Testing Library. Tests component logic and rendering but not real data fetching.

```typescript
import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import Page from './page'

vi.mock('@/lib/sanity/queries', () => ({
  getPageData: vi.fn().mockResolvedValue({title:'Test Page',slug:'test-page',content:[{_type:'block',children:[{text:'Test content'}]}]})
}))

describe('Page - async server component', () => {
  it('renders page with fetched Sanity data', async () => {
    const P = await Page({params:{slug:'test-page'}})
    render(P)
    expect(screen.getByRole('heading',{name:/test page/i})).toBeInTheDocument()
    expect(screen.getByText(/test content/i)).toBeInTheDocument()
  })

  it('handles error state when data fetch fails', async () => {
    const {getPageData} = await import('@/lib/sanity/queries')
    vi.mocked(getPageData).mockResolvedValueOnce(null)
    const P = await Page({params:{slug:'missing'}})
    render(P)
    expect(screen.getByText(/page not found/i)).toBeInTheDocument()
  })
})
```

Mock Sanity queries with `vi.mock()` before importing page. Await page component to resolve async data. Render resolved JSX with Testing Library. Test success (data exists) and error (data null) states.

## Mocking Next.js Server APIs

Server components use Next.js APIs like `cookies()`, `headers()`, `notFound()` which are server-only. Vitest cannot execute these in jsdom. Mock these functions at module level to prevent runtime errors.

```typescript
import { vi } from 'vitest'

vi.mock('next/headers', () => ({
  cookies: vi.fn(() => ({get: vi.fn((name: string) => ({name, value: 'mock-value'}))})),
  headers: vi.fn(() => ({get: vi.fn((name: string) => 'mock-header-value')})),
}))

vi.mock('next/navigation', () => ({
  notFound: vi.fn(() => {throw new Error('notFound() called')}),
  redirect: vi.fn((url: string) => {throw new Error(`redirect() called with ${url}`)}),
}))

describe('Page with server APIs', () => {
  it('reads cookies during render', async () => {
    const P = await Page({params:{}})
    render(P)
    const {cookies} = await import('next/headers')
    expect(cookies).toHaveBeenCalled()
  })

  it('throws notFound for missing resources', async () => {
    const {getPageData} = await import('@/lib/sanity/queries')
    vi.mocked(getPageData).mockResolvedValueOnce(null)
    await expect(Page({params:{slug:'missing'}})).rejects.toThrow('notFound() called')
  })
})
```

Mock `next/headers` and `next/navigation` before imports. `notFound()` and `redirect()` throw errors - tests catch with `rejects.toThrow()`. Mocked `cookies()` returns objects matching Next.js API shape.

## Testing generateStaticParams

App Router's `generateStaticParams` exports list of route parameters for static generation at build time. Testing verifies correct slug generation for all content items. Policy-node uses `generateStaticParams` for 800+ pages - untested. Source confidence: 0%.

```typescript
import { vi, describe, it, expect } from 'vitest'
import { generateStaticParams } from './page'

vi.mock('@/lib/sanity/queries', () => ({
  getAllPageSlugs: vi.fn().mockResolvedValue([{slug:'about'},{slug:'contact'},{slug:'services'}])
}))

describe('generateStaticParams', () => {
  it('returns array of slug objects', async () => {
    const p = await generateStaticParams()
    expect(p).toEqual([{slug:'about'},{slug:'contact'},{slug:'services'}])
  })

  it('fetches all slugs from Sanity', async () => {
    const {getAllPageSlugs} = await import('@/lib/sanity/queries')
    await generateStaticParams()
    expect(getAllPageSlugs).toHaveBeenCalledTimes(1)
  })

  it('handles empty result gracefully', async () => {
    const {getAllPageSlugs} = await import('@/lib/sanity/queries')
    vi.mocked(getAllPageSlugs).mockResolvedValueOnce([])
    const p = await generateStaticParams()
    expect(p).toEqual([])
  })
})
```

Mock data source to return predictable slugs. Verify `generateStaticParams` returns array with expected shape. Test edge case: empty array when no content exists.

## Testing generateMetadata

App Router's `generateMetadata` exports dynamic metadata for each page. Testing ensures correct title, description, OpenGraph tags, and robots directives. All App Router pages in analyzed codebases use `generateMetadata` - none tested. Source confidence: 0%.

```typescript
import { vi, describe, it, expect } from 'vitest'
import { generateMetadata } from './page'

vi.mock('@/lib/sanity/queries', () => ({
  getPageMetadata: vi.fn().mockResolvedValue({title:'Test Page',description:'Test description for SEO',ogImage:'/og-test.jpg'})
}))

describe('generateMetadata', () => {
  it('returns metadata object with title and description', async () => {
    const m = await generateMetadata({params:{slug:'test'}})
    expect(m).toMatchObject({
      title:'Test Page',
      description:'Test description for SEO',
      openGraph:{title:'Test Page',description:'Test description for SEO',images:[{url:'/og-test.jpg'}]},
    })
  })

  it('falls back to default title when no metadata', async () => {
    const {getPageMetadata} = await import('@/lib/sanity/queries')
    vi.mocked(getPageMetadata).mockResolvedValueOnce(null)
    const m = await generateMetadata({params:{slug:'missing'}})
    expect(m.title).toBe('Default Site Title')
  })
})
```

Test metadata object shape matches Next.js Metadata type. Verify OpenGraph, Twitter, robots metadata are correctly populated. Test fallback when data source returns null.

## E2E Testing with Playwright

Playwright tests run in real browsers with actual Next.js server rendering. E2E tests verify server components, data fetching, streaming, user interactions end-to-end. E2E tests are slower (seconds) than unit tests (milliseconds) but provide highest confidence.

```typescript
import { test, expect } from '@playwright/test'

test('homepage renders with server-fetched data', async ({page}) => {
  await page.goto('/')
  await expect(page.getByRole('heading',{name:/welcome/i})).toBeVisible()
  await expect(page.getByText(/latest news/i)).toBeVisible()
  const articles = page.getByRole('article')
  await expect(articles).toHaveCount(10)
})

test('dynamic page uses generateStaticParams', async ({page}) => {
  await page.goto('/blog/test-slug')
  await expect(page.getByRole('heading')).toBeVisible()
  await expect(page.locator('time')).toBeVisible()
})
```

Playwright's `toBeVisible()` waits for server rendering to complete. No mocking required - tests hit real Sanity API or test database. E2E tests verify complete rendering pipeline including async components, Suspense, streaming.

## Testing Suspense Boundaries

Server components wrapped in Suspense show fallback content during async data fetching. Testing Library cannot test Suspense in jsdom. Use Playwright E2E tests to verify Suspense fallbacks appear and resolve correctly.

```typescript
import { test, expect } from '@playwright/test'

test('shows loading state during data fetch', async ({page}) => {
  await page.goto('/products')
  await expect(page.getByText(/loading products/i)).toBeVisible()
  await expect(page.getByText(/loading products/i)).not.toBeVisible({timeout:3000})
  await expect(page.getByRole('article')).toHaveCount(20)
})
```

Playwright's timeout options wait for async operations. `not.toBeVisible({timeout:3000})` waits up to 3 seconds for element to disappear. Test both loading state appearance and content state after loading completes.

## Testing Error Boundaries

Server components can throw errors during data fetching or rendering. Error boundaries catch errors and display fallback UI. Test error boundaries with intentionally failing data fetching or by mocking error conditions.

```typescript
vi.mock('@/lib/sanity/queries', () => ({
  getPageData: vi.fn().mockRejectedValue(new Error('Network error')),
}))

describe('Page - error handling', () => {
  it('shows error boundary when data fetch fails', async () => {
    await expect(Page({params:{slug:'test'}})).rejects.toThrow('Network error')
  })
})

// E2E test
test('shows error UI when page data fails', async ({page}) => {
  await page.goto('/error-test-page')
  await expect(page.getByText(/something went wrong/i)).toBeVisible()
  await expect(page.getByRole('button',{name:/try again/i})).toBeVisible()
})
```

Unit tests verify error is thrown. E2E tests verify error boundary UI renders correctly. Both approaches complement each other - unit tests are fast, E2E tests provide visual confirmation.

## Testing Strategy Recommendations

**Unit test** async server components for:
- Data fetching logic
- Conditional rendering based on data
- generateStaticParams and generateMetadata
- Error handling and null states

**E2E test** async server components for:
- Complete page rendering with real data
- Suspense fallback behavior
- Error boundary UI
- Streaming and progressive rendering

Combined approach provides fast feedback (unit tests) and high confidence (E2E tests). Helix-dot-com-next's 20 async pages require ~30 unit tests + ~10 E2E tests for comprehensive coverage.
