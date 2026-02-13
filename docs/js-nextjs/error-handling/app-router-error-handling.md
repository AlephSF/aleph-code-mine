---
title: "Next.js App Router Error Handling with error.tsx and notFound()"
category: "error-handling"
subcategory: "app-router"
tags: ["error-handling", "app-router", "error-boundaries", "notfound", "nextjs"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-11"
---

# Next.js App Router Error Handling with error.tsx and notFound()

Next.js App Router provides file-based error handling through error.tsx, not-found.tsx, and global-error.tsx files, plus the notFound() function for programmatic 404 responses. Analyzed codebases show 50% adoption of error.tsx (policy-node only), 67% notFound() usage (helix: 6 calls, policy-node: 19 calls), and 0% adoption of not-found.tsx and global-error.tsx despite 25 notFound() calls requiring custom 404 pages.

## error.tsx: Route-Specific Error Boundaries

Next.js error.tsx files automatically wrap route segments in React error boundaries, catching rendering errors, data fetching errors, and component lifecycle errors. Error boundaries must be client components ('use client' directive) and receive error and reset props.

**Policy-Node Implementation (50% App Router Adoption):**

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

**Observed Pattern:**
- Policy-node: 1 error.tsx file
- Helix: 0 error.tsx files (gap - uses notFound() but no error handling)
- Placement: Root app/ directory (catches errors in all routes)
- Scope: Catches errors in nested route segments but NOT layout.tsx errors

**When error.tsx Triggers:**
- Component throws error during rendering
- Server Component encounters error during data fetching
- Event handler throws uncaught error (bubbled to nearest boundary)
- Async function in useEffect throws unhandled error

**When error.tsx Does NOT Trigger:**
- Errors in layout.tsx (requires global-error.tsx)
- Errors in root layout
- Server-side errors in middleware
- API route errors (handled separately)

## notFound() Function: Programmatic 404 Responses

Next.js notFound() function programmatically triggers 404 responses, rendering the nearest not-found.tsx file. Used in Server Components to handle missing resources (CMS content, database records, dynamic route segments).

**Helix Pattern (6 Calls):**

```typescript
// app/[slug]/page.tsx
import { notFound } from 'next/navigation'

async function getPageData(slug: string) {
  const page = await sanityClient.fetch(/* ... */)

  if (!page) {
    notFound()  // Renders not-found.tsx (but file doesn't exist!)
  }

  return page
}
```

**Policy-Node Pattern (19 Calls):**

```typescript
// app/[lang]/municipality/[slug]/page.tsx
import { notFound } from 'next/navigation'

const municipality = await fetchMunicipality(params.slug)

if (!municipality) {
  notFound()  // Returns 404 status code
}
```

**Adoption Metrics:**
- Helix: 6 notFound() calls (no not-found.tsx - uses Next.js default)
- Policy-node: 19 notFound() calls (no not-found.tsx - uses Next.js default)
- Kariusdx: 0 notFound() calls (Pages Router, uses getStaticProps fallback)

**Best Practices:**
- Call notFound() before rendering to avoid partial page renders
- Use in generateStaticParams when pre-rendering unknown routes
- Return notFound() in catch blocks for missing CMS content
- Avoid notFound() in Client Components (use conditional rendering instead)

## not-found.tsx: Custom 404 Pages

Next.js not-found.tsx files provide custom 404 error pages for missing routes and notFound() calls. Placed at any route level, inherits parent layout.tsx styling.

**Missing Pattern (0% Adoption):**

```typescript
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className={styles.notFound}>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist or has been moved.</p>
      <Link href="/">Return to Homepage</Link>
    </div>
  )
}
```

**Gap:** 25 notFound() calls, 0 custom not-found.tsx files. Users see unstyled Next.js default instead of branded 404.

**Recommended Structure:**

```typescript
// app/not-found.tsx (Root-level 404)
export default function NotFound() {
  return (
    <>
      <h1>404</h1>
      <p>We couldn't find that page.</p>
      <Link href="/">Home</Link>
    </>
  )
}

// app/blog/not-found.tsx (Nested 404 for blog routes)
export default function BlogNotFound() {
  return (
    <>
      <h2>Blog Post Not Found</h2>
      <Link href="/blog">View All Posts</Link>
    </>
  )
}
```

**Inheritance Behavior:**
- not-found.tsx inherits layout.tsx (includes navigation, footer)
- Root not-found.tsx catches all 404s without nested not-found.tsx
- Nested not-found.tsx provides context-specific 404 messages

## global-error.tsx: Root Layout Error Handling

Next.js global-error.tsx handles errors in root layout.tsx. Must define <html> and <body> tags since root layout is not rendered during activation. Critical gap: 0% adoption across App Router projects. Root layout errors crash entire application with blank white screen.

```typescript
// app/global-error.tsx
'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div>
          <h2>Application Error</h2>
          <p>Something went wrong at the root level.</p>
          <button onClick={() => reset()}>Reload Application</button>
        </div>
      </body>
    </html>
  )
}
```

Triggers when: error thrown in app/layout.tsx, error in root Server Component, or unhandled error not caught by nested error.tsx.

## global-error.tsx with Error Tracking

Sentry integration in global-error.tsx provides last-chance error tracking before application crashes. useEffect captures exception with location tag and digest metadata.

```typescript
// app/global-error.tsx
'use client'

import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error, {
      tags: { location: 'global-error' },
      extra: { digest: error.digest },
    })
  }, [error])

  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  )
}
```

## Error Handling Hierarchy

Next.js error handling follows a hierarchical fallback pattern, starting with the nearest error.tsx and escalating to global-error.tsx.

**Error Resolution Order:**
1. Component-level try/catch (handled inline, no UI fallback)
2. Nearest error.tsx in route segment (catches route + nested errors)
3. Parent error.tsx (if current segment has no error.tsx)
4. Root error.tsx (catches errors in all routes except layout)
5. global-error.tsx (catches root layout errors only)
6. Next.js default error page (if no custom error handling exists)

**Observed Gaps:**
- Policy-node: Has root error.tsx but no global-error.tsx (layout errors crash app)
- Helix: No error.tsx or global-error.tsx (all errors use Next.js default)
- No nested error.tsx for route-specific error handling
- No error tracking integration in any error boundary

**Recommended Hierarchy:**

```
app/
├── global-error.tsx          (handles root layout errors)
├── error.tsx                 (handles all route errors)
├── not-found.tsx             (handles all 404s)
├── [lang]/
│   ├── error.tsx            (handles i18n-specific errors)
│   └── not-found.tsx        (handles i18n-specific 404s)
└── blog/
    ├── error.tsx            (handles blog-specific errors)
    └── not-found.tsx        (handles blog-specific 404s)
```

## Error Digest for Production Debugging

Next.js error digest provides production-safe error identifiers, hiding sensitive stack trace details from users while enabling developer debugging.

**Error Digest Usage:**

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
}: {
  error: Error & { digest?: string }
}) {
  return (
    <div>
      <h2>An error occurred</h2>
      {error.digest && (
        <p>Error ID: {error.digest}</p>
      )}
    </div>
  )
}
```

**Production Error Logging:**

```typescript
// app/error.tsx
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
}: {
  error: Error & { digest?: string }
}) {
  useEffect(() => {
    // Log to error tracking service
    console.error('Error digest:', error.digest)
    console.error('Error message:', error.message)
  }, [error])

  return (
    <div>
      <h2>Something went wrong</h2>
      <p>Reference ID: {error.digest}</p>
    </div>
  )
}
```

**Gap Analysis:**
- 0% usage of error.digest across analyzed codebases
- No error tracking service integration (no Sentry, Rollbar)
- Production errors have no reference IDs for user support tickets
- Developers cannot correlate user-reported errors with logs

## reset() Function: Error Recovery

Next.js error boundaries provide reset() function to re-render error route segment, enabling recovery from transient errors without full page reload.

**Basic reset() Pattern:**

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Error loading content</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>
        Try again
      </button>
    </div>
  )
}
```

**Advanced reset() with Retry Limit:**

```typescript
// app/error.tsx
'use client'

import { useState } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 3

  const handleReset = () => {
    if (retryCount < maxRetries) {
      setRetryCount(retryCount + 1)
      reset()
    }
  }

  return (
    <div>
      <h2>Error loading content</h2>
      {retryCount < maxRetries ? (
        <button onClick={handleReset}>
          Retry ({retryCount}/{maxRetries})
        </button>
      ) : (
        <p>Max retries reached. Please refresh the page.</p>
      )}
    </div>
  )
}
```

Works for: transient network errors, race conditions, stale data. Does NOT work for: syntax errors, missing env vars, invalid schema, DB failures.

## Codebase Patterns

**Policy-Node (v14 - Partial Adoption):**
- 1 error.tsx file (root level)
- 19 notFound() calls
- 0 not-found.tsx (uses Next.js default)
- 0 global-error.tsx (root layout errors crash app)

**Helix (v15 - Minimal Adoption):**
- 0 error.tsx files
- 6 notFound() calls
- 0 not-found.tsx (uses Next.js default)
- 0 global-error.tsx
- Gap: Uses Next.js defaults despite custom brand requirements

**Kariusdx (v12 - Pages Router):**
- N/A (Pages Router uses different error handling: _error.tsx, 404.tsx)
- 0 notFound() calls (uses getStaticProps fallback: blocking)

**Adoption Summary:**
- error.tsx: 50% App Router projects (1/2)
- notFound(): 67% App Router projects (2/2, but helix + policy-node only)
- not-found.tsx: 0% despite 25 notFound() calls
- global-error.tsx: 0% (critical gap)

## Anti-Patterns

**1. notFound() Without not-found.tsx:**
```typescript
// ❌ BAD: Calls notFound() but no custom not-found.tsx exists
if (!page) {
  notFound()  // Users see Next.js default unstyled 404
}
```

**2. Client Component notFound():**
```typescript
// ❌ BAD: notFound() in Client Component
'use client'

export default function BlogPost({ slug }: Props) {
  const [post, setPost] = useState(null)

  useEffect(() => {
    if (!post) {
      notFound()  // Error: notFound() only works in Server Components
    }
  }, [post])
}
```

**3. No global-error.tsx:**
```typescript
// ❌ BAD: Root layout has no error handling
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
// If layout.tsx throws, entire app crashes with white screen
```

**4. No Error Tracking in error.tsx:**
```typescript
// ❌ BAD: Catches error but doesn't log or track
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
// No visibility into production errors
```

## Migration from Pages Router

**Pages Router Error Handling:**
```typescript
// pages/_error.tsx (Pages Router)
function Error({ statusCode }) {
  return (
    <p>
      {statusCode
        ? `An error ${statusCode} occurred on server`
        : 'An error occurred on client'}
    </p>
  )
}

Error.getInitialProps = ({ res, err }) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404
  return { statusCode }
}
```

**App Router Equivalent:**
```typescript
// app/error.tsx (App Router)
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <p>An error occurred: {error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}

// app/global-error.tsx (Replaces _error.tsx root-level handling)
'use client'

export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  )
}
```

**Migration Steps:**
1. Create app/global-error.tsx (replaces _error.tsx)
2. Create app/error.tsx for route-level errors
3. Create app/not-found.tsx (replaces pages/404.tsx)
4. Replace notFound() calls from getStaticProps with Server Component notFound()
5. Remove pages/_error.tsx and pages/404.tsx

## Recommendations

**Priority 1: Add not-found.tsx (Helix, Policy-Node)**
- Create branded 404 pages for 25 existing notFound() calls
- Add tracking/analytics to 404 page
- Provide helpful navigation (search, popular pages, sitemap)

**Priority 2: Add global-error.tsx (Helix, Policy-Node)**
- Prevent white screen crashes on root layout errors
- Integrate error tracking service (Sentry)
- Provide user-friendly recovery options

**Priority 3: Expand error.tsx Coverage (Helix)**
- Add root-level error.tsx
- Add nested error.tsx for critical sections (checkout, dashboard)
- Include error tracking in all error boundaries

**Priority 4: Track Error Digests**
- Display error.digest in user-facing error messages
- Log error.digest to error tracking service
- Use digest as reference ID for support tickets
