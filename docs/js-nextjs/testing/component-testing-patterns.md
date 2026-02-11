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

Component testing verifies React components behave correctly from a user's perspective by simulating interactions and asserting DOM state. Testing Library prioritizes testing components as users experience them rather than testing implementation details. Tests query elements by accessible roles, labels, and text content, ensuring components remain testable and accessible simultaneously.

### Query Prioritization: Accessibility-First

Testing Library's query priority reflects real-world user interaction patterns. Users find elements by visible labels (getByRole, getByLabelText, getByText), not by CSS classes or test IDs. Queries prioritized by accessibility improve both test resilience and component quality. Three analyzed Next.js codebases (313+ components) have zero component tests. Source confidence: 0% (gap pattern - no component testing infrastructure exists).

#### Query Priority Hierarchy

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

### User Event Simulation: userEvent Over fireEvent

Testing Library's `userEvent` API simulates realistic browser interactions including focus, hover, keyboard navigation, and form submission. Legacy `fireEvent` dispatches synthetic events without browser-like behavior (no focus, no hover). Use `userEvent` for all interaction tests to match production behavior. Install with: `npm install -D @testing-library/user-event`.

#### Realistic Click Interactions

```typescript
import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

it('calls onClick when button is clicked', async () => {
  const handleClick = vi.fn()
  const user = userEvent.setup()
  render(<Button onClick={handleClick}>Click Me</Button>)

  await user.click(screen.getByRole('button', { name: /click me/i }))

  expect(handleClick).toHaveBeenCalledTimes(1)
})

it('increments counter on each click', async () => {
  const user = userEvent.setup()
  render(<Counter />)

  expect(screen.getByText(/count: 0/i)).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: /increment/i }))
  expect(screen.getByText(/count: 1/i)).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: /increment/i }))
  expect(screen.getByText(/count: 2/i)).toBeInTheDocument()
})
```

Setup `userEvent` with `userEvent.setup()` once per test for optimal performance. All `userEvent` methods return promises - use `await` for every interaction. Tests verify both handler invocation (`toHaveBeenCalledTimes`) and UI state changes (`toBeInTheDocument`). Multiple clicks in sequence simulate real user behavior.

### Form Testing with Type and Submit

Form components require testing keyboard input, validation, and submission. Testing Library's `userEvent.type()` simulates realistic typing with individual keypress events. Form tests verify validation errors appear, required fields prevent submission, and successful submissions call handlers with correct data.

#### Complete Form Interaction Test

```typescript
import userEvent from '@testing-library/user-event'
import { render, screen, waitFor } from '@testing-library/react'
import { ContactForm } from './ContactForm'

it('validates required fields before submission', async () => {
  const handleSubmit = vi.fn()
  const user = userEvent.setup()
  render(<ContactForm onSubmit={handleSubmit} />)

  // Submit empty form
  await user.click(screen.getByRole('button', { name: /submit/i }))

  // Validation errors appear
  await waitFor(() => {
    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    expect(screen.getByText(/message is required/i)).toBeInTheDocument()
  })
  expect(handleSubmit).not.toHaveBeenCalled()
})

it('submits form with valid data', async () => {
  const handleSubmit = vi.fn()
  const user = userEvent.setup()
  render(<ContactForm onSubmit={handleSubmit} />)

  // Fill form fields
  await user.type(screen.getByLabelText(/email/i), 'test@example.com')
  await user.type(screen.getByLabelText(/message/i), 'Hello world')
  await user.click(screen.getByRole('button', { name: /submit/i }))

  // Handler called with correct data
  await waitFor(() => {
    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      message: 'Hello world',
    })
  })
})
```

Use `waitFor` for async validation and submission. `waitFor` retries assertions until they pass or timeout, handling React state updates and async validation. Type complete strings with `user.type()` - do not type character-by-character unless testing autocomplete. Verify both error states and success states.

### Testing Components with SCSS Modules

Components using SCSS Modules (100% adoption across analyzed codebases) apply dynamic class names. Testing Library's `toHaveClass` matcher verifies CSS classes are applied. Test CSS classes sparingly - prefer testing visible behavior (is element visible? is button disabled?) over implementation details.

#### Testing Conditional Classes

```typescript
import { render } from '@testing-library/react'
import { Alert } from './Alert'

it('applies error class for error variant', () => {
  const { container } = render(<Alert variant="error">Error message</Alert>)
  const alert = container.querySelector('[role="alert"]')

  expect(alert).toHaveClass('alert', 'alert--error')
})

it('applies success class for success variant', () => {
  const { container } = render(<Alert variant="success">Success message</Alert>)
  const alert = container.querySelector('[role="alert"]')

  expect(alert).toHaveClass('alert', 'alert--success')
})

// Better: Test behavior, not classes
it('renders error alert with red styling', () => {
  render(<Alert variant="error">Error message</Alert>)
  const alert = screen.getByRole('alert')

  expect(alert).toBeInTheDocument()
  expect(alert).toHaveTextContent('Error message')
})
```

Prefer `toBeInTheDocument()` and `toHaveTextContent()` over `toHaveClass()`. Class-based tests break when renaming CSS classes during refactoring. Behavior-based tests remain valid as long as component functionality is unchanged. Use `container.querySelector` for CSS-based queries only when role-based queries are impossible.

### Testing Server Components (Next.js App Router)

Next.js App Router async server components require special testing setup because they execute server-side. Testing Library renders components in jsdom (browser environment), so server components must be tested as client components with mocked data fetching. Alternatively, test server components via E2E tests with Playwright.

#### Testing Server Components as Client Components

```typescript
// page.test.tsx
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import Page from './page'

// Mock data fetching
vi.mock('@/lib/sanity/queries', () => ({
  getPageData: vi.fn().mockResolvedValue({
    title: 'Test Page',
    content: 'Test content',
  }),
}))

it('renders page with fetched data', async () => {
  const PageResolved = await Page({})  // Await async server component

  render(PageResolved)

  expect(screen.getByRole('heading', { name: /test page/i })).toBeInTheDocument()
  expect(screen.getByText(/test content/i)).toBeInTheDocument()
})
```

Mock data fetching functions at the module level with `vi.mock()`. Server components return promises - await the component before rendering. Alternatively, convert server components to client components for testing by extracting logic into testable utilities and using client components as thin wrappers.

### Testing Components with Props

Props testing verifies components render correctly with different prop combinations. Test all prop variants (optional props, required props, default props) and prop types (strings, numbers, booleans, objects, functions). Helix-dot-com-next has 188 components with Props interfaces - all untested. Source confidence: 0%.

#### Props Testing Pattern

```typescript
import { render, screen } from '@testing-library/react'
import { Card } from './Card'

describe('Card - required props', () => {
  it('renders with title and content', () => {
    render(<Card title="Test Title" content="Test content" />)

    expect(screen.getByRole('heading', { name: /test title/i })).toBeInTheDocument()
    expect(screen.getByText(/test content/i)).toBeInTheDocument()
  })
})

describe('Card - optional props', () => {
  it('renders without image when imageUrl is undefined', () => {
    render(<Card title="Title" content="Content" />)

    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })

  it('renders with image when imageUrl is provided', () => {
    render(<Card title="Title" content="Content" imageUrl="/test.jpg" />)

    expect(screen.getByRole('img')).toHaveAttribute('src', '/test.jpg')
  })
})

describe('Card - function props', () => {
  it('calls onClick when card is clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    render(<Card title="Title" content="Content" onClick={handleClick} />)

    await user.click(screen.getByRole('article'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

Group related prop tests with `describe` blocks. Test default behavior (no optional props), optional behavior (with optional props), and function props (handlers, callbacks). Use `queryByRole` for asserting elements are NOT in the document (returns null instead of throwing).

### Snapshot Testing for Complex Components

Snapshot tests capture component output and fail when output changes unexpectedly. Snapshots detect unintended changes but create maintenance burden when components change frequently. Use snapshots sparingly for complex components with many props/states. Prefer explicit assertions over snapshots.

#### Snapshot Testing Example

```typescript
import { render } from '@testing-library/react'
import { Card } from './Card'

it('matches snapshot with all props', () => {
  const { container } = render(
    <Card
      title="Test Title"
      content="Test content"
      imageUrl="/test.jpg"
      variant="primary"
      onClick={vi.fn()}
    />
  )

  expect(container.firstChild).toMatchSnapshot()
})
```

Vitest's `toMatchSnapshot()` creates snapshot files in `__snapshots__` directory. First run creates snapshot, subsequent runs compare against saved snapshot. Update snapshots with `vitest -u` when changes are intentional. Snapshot tests complement (not replace) explicit behavior tests.

## Component Testing Coverage Goals

**High-priority components:** 80%+ coverage (forms, buttons, navigation)
**Medium-priority components:** 60-70% coverage (cards, lists, layout)
**Low-priority components:** 40-50% coverage (simple wrappers, presentational)

Three analyzed Next.js codebases contain 313+ untested components. Recommended initial targets: 50-80 component tests covering high-traffic pages and interactive components. Start with Button, Form, Navigation, and Card components - these are used across multiple pages.
