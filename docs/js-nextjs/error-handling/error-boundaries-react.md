---
title: "React Error Boundaries for Graceful Failure Handling"
category: "error-handling"
subcategory: "react-patterns"
tags: ["error-boundaries", "react", "componentDidCatch", "graceful-degradation", "error-recovery"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## React Error Boundaries for Graceful Failure Handling

React Error Boundaries catch JavaScript errors anywhere in component tree, log errors, and display fallback UI instead of crashing entire application with white screen. Error boundaries use componentDidCatch lifecycle method and getDerivedStateFromError static method to intercept errors during rendering, in lifecycle methods, and in constructors. Next.js applications without error boundaries risk catastrophic user experience when single component error crashes entire page. Analysis of three Next.js codebases (helix, kariusdx, policy-node) reveals zero error boundary implementations.

## Why Error Boundaries Are Critical

Uncaught errors in React components unmount entire component tree, displaying blank white screen to users. Users cannot recover, navigate, or complete tasks. Error boundaries prevent cascading failures by catching errors at boundary level, preserving surrounding UI, and displaying helpful fallback message. Source confidence: 0% (gap pattern - no error boundaries exist in analyzed codebases despite 313+ components).

#### Without Error Boundary

```typescript
// Component with error
function UserProfile({ userId }: { userId: string }) {
  const user = useUser(userId)

  // Runtime error: user is null, accessing user.name throws
  return <h1>{user.name}</h1>  // 💥 Entire app crashes, white screen
}

// App structure
export default function Page() {
  return (
    <Layout>
      <Header />
      <UserProfile userId="123" />
      <Footer />
    </Layout>
  )
}
// If UserProfile crashes, Header and Footer also unmount - entire page blank
```

Error in UserProfile unmounts Layout, Header, and Footer. Users see blank page with no recovery option. Navigation broken. Console shows error but UI provides no feedback.

#### With Error Boundary

```typescript
function UserProfile({ userId }: { userId: string }) {
  const user = useUser(userId)
  return <h1>{user.name}</h1>  // Error occurs here
}

export default function Page() {
  return (
    <Layout>
      <Header />
      <ErrorBoundary fallback={<ErrorFallback />}>
        <UserProfile userId="123" />  // Wrapped in boundary
      </ErrorBoundary>
      <Footer />
    </Layout>
  )
}
// If UserProfile crashes, Header and Footer remain visible
// ErrorFallback displays instead of UserProfile only
```

Error contained to UserProfile section. Header and Footer remain functional. Users can navigate elsewhere. ErrorFallback explains problem and offers recovery actions.

## Error Boundary Class Component Implementation

Error boundaries must be class components because getDerivedStateFromError and componentDidCatch are not available as hooks. Functional components cannot implement error boundaries directly. Error boundary stores hasError state, implements both lifecycle methods, and renders fallback UI when hasError is true.

#### Basic Error Boundary

```typescript
// components/ErrorBoundary/ErrorBoundary.tsx
import React, { Component, ReactNode, ErrorInfo } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so next render shows fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to error reporting service
    console.error('Caught by Error Boundary:', error, errorInfo)

    // Call optional error callback
    this.props.onError?.(error, errorInfo)

    // Send to Sentry/Rollbar
    // Sentry.captureException(error, { extra: errorInfo })
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return this.props.fallback || (
        <div>
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

getDerivedStateFromError updates state during render phase (pure function, no side effects). componentDidCatch called during commit phase for side effects (logging, analytics). Props.fallback provides custom error UI. Props.onError enables parent components to handle errors.

## Error Boundary with Reset Functionality

Production error boundaries should provide reset button allowing users to recover without page refresh. Reset clears error state and re-renders children. Useful for transient errors (network failures, race conditions) that may resolve on retry.

#### Error Boundary with Reset

```typescript
interface Props {
  children: ReactNode
  fallback?: (error: Error, reset: () => void) => ReactNode
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error Boundary caught:', error, errorInfo)
  }

  reset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback?.(this.state.error, this.reset) || (
        <div>
          <h2>Something went wrong</h2>
          <p>{this.state.error.message}</p>
          <button onClick={this.reset}>Try again</button>
        </div>
      )
    }

    return this.props.children
  }
}

// Usage with custom fallback
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <h2>Failed to load user profile</h2>
      <p>Error: {error.message}</p>
      <button onClick={reset}>Reload profile</button>
    </div>
  )}
>
  <UserProfile userId="123" />
</ErrorBoundary>
```

reset method clears error state, triggering re-render of children. Fallback function receives error and reset callback. Users can retry without full page reload. Reset button labeled descriptively ("Reload profile" not generic "Try again").

## Granular Error Boundaries for Isolated Failures

Wrap independent sections in separate error boundaries to prevent single component failure from affecting unrelated UI sections. Dashboard with multiple widgets should wrap each widget in error boundary. One failing widget doesn't crash entire dashboard.

#### Multiple Error Boundaries

```typescript
export default function Dashboard() {
  return (
    <div>
      <Header />
      <ErrorBoundary fallback={<WidgetError name="User Stats" />}>
        <UserStatsWidget />
      </ErrorBoundary>
      <ErrorBoundary fallback={<WidgetError name="Activity Feed" />}>
        <ActivityFeedWidget />
      </ErrorBoundary>
      <ErrorBoundary fallback={<WidgetError name="Recent Orders" />}>
        <RecentOrdersWidget />
      </ErrorBoundary>
      <Footer />
    </div>
  )
}

function WidgetError({ name }: { name: string }) {
  return (
    <div className="widget-error">
      <p>Failed to load {name}</p>
      <button onClick={() => window.location.reload()}>Refresh page</button>
    </div>
  )
}
```

Each widget isolated by boundary. UserStatsWidget error doesn't affect ActivityFeedWidget. Users see partial dashboard with working widgets. Failed widgets display helpful error messages. Granular boundaries enable precise error reporting per component.

## Error Boundaries Cannot Catch These Errors

Error boundaries have limitations: event handlers, asynchronous code (setTimeout, fetch), server-side rendering errors, and errors thrown in error boundary itself. Event handler errors require try/catch. Async errors caught in promise catch blocks or try/catch with async/await. SSR errors handled by Next.js error.tsx files.

#### Errors Outside Error Boundary Scope

```typescript
function Component() {
  // ❌ Error boundary CANNOT catch this (event handler)
  const handleClick = () => {
    throw new Error('Click handler error')
  }

  // ❌ Error boundary CANNOT catch this (async error)
  useEffect(() => {
    fetchData().catch((error) => {
      // Must handle here, error boundary won't catch
      console.error(error)
    })
  }, [])

  // ✅ Error boundary CAN catch this (render error)
  return <div>{data.map(item => item.value)}</div>  // If data is null
}

// Event handler requires try/catch
const handleClick = () => {
  try {
    processData()
  } catch (error) {
    console.error(error)
    showErrorToast(error.message)
  }
}

// Async code requires try/catch or .catch()
useEffect(() => {
  const loadData = async () => {
    try {
      const data = await fetchData()
      setData(data)
    } catch (error) {
      console.error(error)
      setError(error)
    }
  }
  loadData()
}, [])
```

Event handlers must use try/catch internally. Async operations need explicit error handling. Error boundaries complement (not replace) traditional error handling.

## Integration with Error Tracking Services

Error boundaries integrate with Sentry, Rollbar, or Bugsnag to report production errors. componentDidCatch sends errors to tracking service with user context, component stack, and custom metadata. Enables monitoring production error rates and prioritizing fixes.

#### Sentry Integration

```typescript
import * as Sentry from '@sentry/nextjs'

class ErrorBoundary extends Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
      tags: {
        errorBoundary: 'true',
      },
      level: 'error',
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h2>Something went wrong</h2>
          <button onClick={() => Sentry.showReportDialog()}>
            Report feedback
          </button>
          <button onClick={this.reset}>Try again</button>
        </div>
      )
    }

    return this.props.children
  }
}
```

Sentry.captureException sends error with component stack. Sentry.showReportDialog lets users provide feedback. Tags identify errors caught by boundary. Contexts attach React-specific information.

## Root-Level Error Boundary

Wrap entire Next.js application in root-level error boundary to catch unhandled errors in any component. Place in root layout (App Router) or _app.tsx (Pages Router). Provides last-resort error handling preventing complete application crash.

#### Root Layout with Error Boundary (App Router)

```typescript
// app/layout.tsx
import ErrorBoundary from '@/components/ErrorBoundary'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary
          fallback={(error, reset) => (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <h1>Application Error</h1>
              <p>We're sorry, something went wrong.</p>
              <button onClick={reset}>Reload application</button>
            </div>
          )}
        >
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}
```

Root boundary catches all unhandled component errors. Fallback provides minimal UI for recovery. Users can reload application without browser refresh. Combine with Next.js error.tsx for complete error handling coverage.

## Error Boundaries vs Next.js error.tsx

Next.js App Router error.tsx files handle errors during server rendering and in server components. Error boundaries handle errors in client components during browser rendering. Both are needed: error.tsx for SSR failures, error boundaries for CSR failures. error.tsx is client component, Error Boundary is class component.

#### Combined Error Handling Strategy

```typescript
// app/error.tsx (Next.js error handler)
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
      <h2>Page Error</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}

// components/ErrorBoundary.tsx (React error boundary)
class ErrorBoundary extends Component {
  // ... implementation
}

// app/layout.tsx (both strategies)
export default function Layout({ children }) {
  return (
    <ErrorBoundary>  {/* Client component errors */}
      {children}     {/* Server component errors → error.tsx */}
    </ErrorBoundary>
  )
}
```

error.tsx catches server-side errors (data fetching failures, async server component errors). ErrorBoundary catches client-side errors (event handlers, useEffect errors, render errors). Layered approach provides comprehensive error coverage.

## Implementation Priority

**Immediate (Week 1):** Add root-level ErrorBoundary to all 3 Next.js repositories. Prevents white screen crashes from unhandled component errors.

**Short-term (Week 2):** Add granular boundaries around complex/risky components (data-heavy widgets, third-party integrations, experimental features).

**Medium-term (Week 3-4):** Integrate with Sentry/Rollbar for production error tracking. Add custom fallback UI with reset functionality and user feedback forms.

Zero error boundaries across 313+ components in analyzed codebases represents critical gap. Single component error currently crashes entire application. Priority 1 fix for production-ready Next.js applications.
