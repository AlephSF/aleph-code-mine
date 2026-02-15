---
title: "Component Testing Patterns with Testing Library"
category: "testing"
subcategory: "integration-testing"
tags: ["testing-library", "component-testing", "react", "user-events", "accessibility"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Component Testing Patterns with Testing Library

Component testing verifies React components behave correctly from a user's perspective by simulating interactions and asserting DOM state. Testing Library prioritizes testing components as users experience them rather than testing implementation details. Tests query elements by accessible roles, labels, and text content, ensuring components remain testable and accessible simultaneously. Three analyzed Next.js codebases (313+ components) have zero component tests. Source confidence: 0% (gap pattern).

## Query Prioritization with Testing Library

Testing Library query priority reflects real-world user interaction patterns. Users find elements by visible labels (getByRole, getByLabelText, getByText), not by CSS classes or test IDs. Queries prioritized by accessibility improve both test resilience and component quality.

```typescript
// Button.test.tsx - Good: Queries by accessible role
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

it('renders button with accessible label', () => {
  render(<Button>Submit Form</Button>)
  expect(screen.getByRole('button', { name: /submit form/i })).toBeInTheDocument()
})

// Bad: Queries by implementation detail (CSS class)
it('renders button with class name', () => {
  render(<Button>Submit Form</Button>)
  expect(screen.getByClassName('btn-primary')).toBeInTheDocument()  // Breaks on refactor
})
```

Prefer `getByRole` over `getByTestId` because role-based queries validate ARIA semantics. Button component refactored from `<button>` to `<a role="button">` passes role-based tests but breaks test-id-based tests. Query hierarchy: 1) getByRole, 2) getByLabelText, 3) getByPlaceholderText, 4) getByText, 5) getByDisplayValue, 6) getByAltText, 7) getByTitle, 8) getByTestId (last resort).

## User Event Simulation with userEvent API

Testing Library userEvent API simulates realistic browser interactions including focus, hover, keyboard navigation, and form submission. Legacy fireEvent dispatches synthetic events without browser-like behavior. Use userEvent for all interaction tests. Install: `npm install -D @testing-library/user-event`.

```typescript
import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/react'

it('calls onClick when button is clicked', async () => {
  const h = vi.fn(), u = userEvent.setup()
  render(<Button onClick={h}>Click Me</Button>)
  await u.click(screen.getByRole('button', { name: /click me/i }))
  expect(h).toHaveBeenCalledTimes(1)
})

it('increments counter on each click', async () => {
  const u = userEvent.setup()
  render(<Counter />)
  expect(screen.getByText(/count: 0/i)).toBeInTheDocument()
  await u.click(screen.getByRole('button', { name: /increment/i }))
  expect(screen.getByText(/count: 1/i)).toBeInTheDocument()
})
```

Setup userEvent with `userEvent.setup()` once per test. All userEvent methods return promises - use `await` for every interaction. Tests verify handler invocation (`toHaveBeenCalledTimes`) and UI state changes (`toBeInTheDocument`).

## Form Testing with Testing Library

Form components require testing keyboard input, validation, and submission. Testing Library userEvent.type() simulates realistic typing. Form tests verify validation errors appear, required fields prevent submission, and successful submissions call handlers with correct data.

```typescript
import userEvent from '@testing-library/user-event'
import { render, screen, waitFor } from '@testing-library/react'

it('validates required fields', async () => {
  const h = vi.fn(), u = userEvent.setup()
  render(<ContactForm onSubmit={h} />)
  await u.click(screen.getByRole('button', { name: /submit/i }))
  await waitFor(() => {
    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
  })
  expect(h).not.toHaveBeenCalled()
})

it('submits form with valid data', async () => {
  const h = vi.fn(), u = userEvent.setup()
  render(<ContactForm onSubmit={h} />)
  await u.type(screen.getByLabelText(/email/i), 'test@example.com')
  await u.type(screen.getByLabelText(/message/i), 'Hello')
  await u.click(screen.getByRole('button', { name: /submit/i }))
  await waitFor(() => expect(h).toHaveBeenCalledWith({ email: 'test@example.com', message: 'Hello' }))
})
```

Use `waitFor` for async validation and submission. waitFor retries assertions until they pass or timeout, handling React state updates and async validation. Type complete strings with `user.type()`. Verify both error states and success states.

## Testing Components with SCSS Modules

Components using SCSS Modules (100% adoption across analyzed codebases) apply dynamic class names. Testing Library toHaveClass matcher verifies CSS classes are applied. Test CSS classes sparingly - prefer testing visible behavior (is element visible? is button disabled?) over implementation details.

```typescript
import { render, screen } from '@testing-library/react'
import { Alert } from './Alert'

it('applies error class for error variant', () => {
  const { container } = render(<Alert variant="error">Error message</Alert>)
  expect(container.querySelector('[role="alert"]')).toHaveClass('alert', 'alert--error')
})

it('applies success class for success variant', () => {
  const { container } = render(<Alert variant="success">Success message</Alert>)
  expect(container.querySelector('[role="alert"]')).toHaveClass('alert', 'alert--success')
})

// Better: Test behavior, not classes
it('renders error alert with message', () => {
  render(<Alert variant="error">Error message</Alert>)
  const a = screen.getByRole('alert')
  expect(a).toBeInTheDocument()
  expect(a).toHaveTextContent('Error message')
})
```

Prefer `toBeInTheDocument()` and `toHaveTextContent()` over `toHaveClass()`. Class-based tests break when renaming CSS classes during refactoring. Behavior-based tests remain valid as long as component functionality is unchanged. Use `container.querySelector` for CSS-based queries only when role-based queries are impossible.

## Testing Next.js App Router Server Components

Next.js App Router async server components require special testing setup because they execute server-side. Testing Library renders components in jsdom (browser environment), so server components must be tested as client components with mocked data fetching. Alternatively, test server components via E2E tests with Playwright.

```typescript
// page.test.tsx
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import Page from './page'

vi.mock('@/lib/sanity/queries', () => ({
  getPageData: vi.fn().mockResolvedValue({ title: 'Test Page', content: 'Test content' })
}))

it('renders page with fetched data', async () => {
  const P = await Page({})
  render(P)
  expect(screen.getByRole('heading', { name: /test page/i })).toBeInTheDocument()
  expect(screen.getByText(/test content/i)).toBeInTheDocument()
})
```

Mock data fetching functions at module level with `vi.mock()`. Server components return promises - await component before rendering. Alternatively, convert server components to client components for testing by extracting logic into testable utilities and using client components as thin wrappers.

## Testing Component Props and Variants

Props testing verifies components render correctly with different prop combinations. Test all prop variants (optional, required, default) and prop types. Helix-dot-com-next has 188 components with Props interfaces - all untested. Source confidence: 0%.

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('Card - required', () => {
  it('renders with title', () => {
    render(<Card title="Test" content="Content" />)
    expect(screen.getByRole('heading', { name: /test/i })).toBeInTheDocument()
  })
})

describe('Card - optional', () => {
  it('renders without image when undefined', () => {
    render(<Card title="T" content="C" />)
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })

  it('renders with image when provided', () => {
    render(<Card title="T" content="C" imageUrl="/t.jpg" />)
    expect(screen.getByRole('img')).toHaveAttribute('src', '/t.jpg')
  })
})

describe('Card - functions', () => {
  it('calls onClick when clicked', async () => {
    const h = vi.fn(), u = userEvent.setup()
    render(<Card title="T" content="C" onClick={h} />)
    await u.click(screen.getByRole('article'))
    expect(h).toHaveBeenCalledTimes(1)
  })
})
```

Group related prop tests with `describe` blocks. Test default behavior, optional behavior, function props. Use `queryByRole` for asserting elements NOT in document.

## Snapshot Testing for Complex Components

Snapshot tests capture component output and fail when output changes unexpectedly. Snapshots detect unintended changes but create maintenance burden when components change frequently. Use snapshots sparingly for complex components with many props/states. Prefer explicit assertions over snapshots.

```typescript
import { render } from '@testing-library/react'
import { Card } from './Card'

it('matches snapshot with all props', () => {
  const { container } = render(
    <Card title="Test Title" content="Test content" imageUrl="/test.jpg"
      variant="primary" onClick={vi.fn()} />
  )
  expect(container.firstChild).toMatchSnapshot()
})
```

Vitest toMatchSnapshot() creates snapshot files in `__snapshots__` directory. First run creates snapshot, subsequent runs compare against saved snapshot. Update snapshots with `vitest -u` when changes are intentional. Snapshot tests complement (not replace) explicit behavior tests.

## Component Testing Coverage Goals

**High-priority components:** 80%+ coverage (forms, buttons, navigation)
**Medium-priority components:** 60-70% coverage (cards, lists, layout)
**Low-priority components:** 40-50% coverage (simple wrappers, presentational)

Three analyzed Next.js codebases contain 313+ untested components. Recommended initial targets: 50-80 component tests covering high-traffic pages and interactive components. Start with Button, Form, Navigation, and Card components - these are used across multiple pages.
