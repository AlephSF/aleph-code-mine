---
title: "Recommended Testing Stack for Next.js 14/15"
category: "testing"
subcategory: "tooling"
tags: ["vitest", "testing-library", "playwright", "msw", "testing-stack"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Recommended Testing Stack for Next.js 14/15

Next.js applications require three testing layers: unit tests for utilities and hooks, integration tests for components and API routes, and end-to-end tests for user flows. The recommended stack combines Vitest for speed, Testing Library for DOM testing, and Playwright for E2E automation. Modern alternatives like Vitest provide better Next.js App Router support than Jest while maintaining familiar APIs.

### Unit & Integration Testing: Vitest

Vitest serves as the primary test runner for unit and integration tests in Next.js applications. Vitest provides 5-10x faster test execution than Jest due to ESM-native architecture and Vite's transformer. Next.js 15 App Router patterns (async server components, route handlers) work seamlessly with Vitest's native ESM support. Configuration integrates with existing `tsconfig.json` path aliases via `vite-tsconfig-paths`. Install with: `npm install -D vitest @vitejs/plugin-react`. Source confidence: 0% (none of the analyzed codebases use Vitest or Jest).

#### Vitest Configuration for Next.js

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', '**/*.d.ts', '**/*.config.ts'],
    },
  },
})
```

Vitest configuration requires `environment: 'jsdom'` for React component testing, `globals: true` to avoid importing `describe`/`it` in every file, and `setupFiles` for global test setup. Path alias resolution via `tsconfigPaths()` ensures `@/components` imports work identically to the application. Coverage thresholds enforce minimum quality standards in CI/CD pipelines.

### Component Testing: @testing-library/react

Testing Library provides user-centric component testing focused on behavior rather than implementation details. Queries like `getByRole`, `getByLabelText`, and `getByText` encourage accessible component design and resilient tests. Install with: `npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event`. The `userEvent` API simulates realistic user interactions (clicks, typing, form submissions) rather than synthetic events. Source confidence: 0% (no component testing exists in analyzed codebases).

#### Testing Library Best Practices

```typescript
// Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('calls onClick handler when clicked', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    await userEvent.click(screen.getByRole('button', { name: /click me/i }))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

Testing Library emphasizes semantic queries (`getByRole`, `getByLabelText`) over implementation-dependent queries (`getByTestId`, `getByClassName`). Tests using `getByRole('button')` remain valid when Button implementation changes from `<button>` to `<a role="button">`. Async `userEvent` API (not `fireEvent`) simulates real browser interactions including focus, hover, and keyboard navigation.

### API Mocking: Mock Service Worker (MSW)

Mock Service Worker intercepts HTTP requests at the network level, enabling realistic API testing without modifying application code. MSW works in both Node.js tests (Vitest) and browser environments (development, Storybook). Install with: `npm install -D msw`. MSW mocks replicate production API behavior including response delays, error states, and pagination. Source confidence: 0% (no API mocking infrastructure exists).

#### MSW Configuration for API Route Testing

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/phrases/:locale', ({ params }) => {
    return HttpResponse.json({
      phrases: [{ id: '1', text: 'Test phrase' }],
      locale: params.locale,
    })
  }),

  http.post('/api/metrics', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ success: true, data: body })
  }),
]
```

MSW handlers define request matching patterns and response generation logic. Path parameters (`/api/phrases/:locale`) and request bodies are accessible for response customization. MSW setup file (`vitest.setup.ts`) initializes handlers before all tests: `beforeAll(() => server.listen())`, `afterEach(() => server.resetHandlers())`, `afterAll(() => server.close())`. This ensures test isolation and predictable API state.

### E2E Testing: Playwright

Playwright provides cross-browser end-to-end testing for Next.js applications with excellent App Router support. Playwright runs tests in real browsers (Chromium, Firefox, WebKit) and simulates user interactions at the application level. Install with: `npm install -D @playwright/test`. Playwright's auto-waiting mechanism reduces flaky tests compared to Selenium or Cypress. Next.js documentation officially recommends Playwright over Cypress for App Router applications. Source confidence: 0% (no E2E testing infrastructure exists).

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
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

Playwright configuration defines test directory (`./e2e`), parallelization strategy, retry logic for CI environments, and automatic Next.js dev server startup via `webServer`. Tests run in multiple browsers (`chromium`, `firefox`) to catch browser-specific bugs. Traces captured on first retry provide debugging artifacts for flaky tests.

### Type-Safe Matchers: @testing-library/jest-dom

Testing Library's `jest-dom` matchers extend Vitest's assertion API with DOM-specific matchers. Matchers like `toBeInTheDocument()`, `toHaveAttribute()`, `toBeVisible()`, and `toBeDisabled()` improve test readability. Install with: `npm install -D @testing-library/jest-dom`. Import in setup file: `import '@testing-library/jest-dom'`. TypeScript types are automatically recognized in Vitest environments. Source confidence: 0% (no DOM testing utilities exist).

### Coverage Tooling: Vitest's V8 Provider

Vitest's built-in coverage tool (V8 provider) generates code coverage reports without additional configuration. Run with: `vitest --coverage`. Reports show line coverage, branch coverage, function coverage, and statement coverage. HTML reports visualize untested lines with red highlighting. Coverage thresholds in `vitest.config.ts` enforce minimum quality: `coverage: { lines: 80, branches: 75, functions: 80 }`. CI/CD pipelines fail builds when coverage drops below thresholds.

### Alternative Stack: Jest + Testing Library + Cypress

Jest (traditional test runner) + Testing Library + Cypress (E2E framework) represents the legacy testing stack for Next.js. Jest has larger ecosystem (more plugins, wider adoption) but slower performance than Vitest. Cypress has better debugging UI than Playwright but weaker multi-browser support. Choose Jest + Cypress when maintaining existing test suites or prioritizing ecosystem size over performance. Choose Vitest + Playwright for new projects prioritizing speed and App Router compatibility.

## Installation Script

```bash
# Unit & Integration Testing
npm install -D vitest @vitejs/plugin-react vite-tsconfig-paths
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @vitest/ui  # Optional: Web UI for test results

# API Mocking
npm install -D msw

# E2E Testing
npm install -D @playwright/test
npx playwright install chromium firefox

# Coverage
npm install -D @vitest/coverage-v8
```

Add scripts to `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

## Recommended Testing Distribution

- **Unit Tests (50-60%):** Pure functions, utilities, data transformations
- **Integration Tests (30-40%):** Components, hooks, API routes
- **E2E Tests (10-20%):** Critical user flows, preview mode, ISR

Total test count recommendation: 100-150 tests for medium-sized Next.js application (30K LOC). Policy-node's 33 utility files require 40-60 unit tests. 313 components across three codebases require 50-80 integration tests. Critical flows (preview mode, ISR, i18n) require 10-15 E2E tests.
