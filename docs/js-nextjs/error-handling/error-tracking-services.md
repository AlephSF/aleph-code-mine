---
title: "Error Tracking Services with Sentry for Next.js Production Monitoring"
category: "error-handling"
subcategory: "monitoring"
tags: ["error-tracking", "sentry", "rollbar", "monitoring", "observability"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

# Error Tracking Services with Sentry for Next.js Production Monitoring

Error tracking services (Sentry, Rollbar, Bugsnag) provide centralized error monitoring, stack trace aggregation, user context tracking, and alerting for production errors. Analyzed codebases show 0% adoption of error tracking services despite 313+ components, 33+ utility functions, and 10+ API routes with zero visibility into production errors. Error tracking enables proactive bug detection, release monitoring, and error trend analysis.

## Console Logging Limitations

Console.error logs vanish after execution (no persistence), lack user context (cannot correlate errors to specific users), and provide no alerting (developers unaware of production errors until users report issues). Current pattern across 0% of analyzed repos logs errors to console without persistence. Errors disappear after execution, no alerts notify developers, and no visibility exists into error frequency or affected users.

```typescript
// ❌ Current: Error logged to console, no persistence
catch (error) {
  console.error('Failed to fetch municipalities:', error)
}
// Error disappears after execution
// No alert sent to developers
// No visibility into frequency or affected users
```

## Sentry Error Tracking with Context

Error tracking services like Sentry persist exceptions, send alerts when thresholds exceed, and group similar errors with affected user counts. Metadata tags enable searching by section or operation. Errors persist in Sentry dashboard, alerts send to Slack/email when thresholds breach, and similar errors group with affected user counts.

```typescript
// ✅ Recommended: Error sent to Sentry with context
import * as Sentry from '@sentry/nextjs'

catch (error) {
  Sentry.captureException(error, {
    tags: {
      section: 'municipalities-api',
      operation: 'fetch',
    },
    extra: {
      municipalityId: params.slug,
      userId: session?.userId,
    },
  })
  throw error
}
// Error persisted in Sentry dashboard
// Alert sent to Slack/email if threshold exceeded
// Grouped with similar errors, shows affected user count
```

## Error Tracking Service Benefits

Sentry and similar services provide 6-12 months retention, duplicate error grouping with occurrence frequency, user context (ID, browser, OS, release, breadcrumbs), real-time Slack/email/PagerDuty notifications, error rate graphs with release comparisons, and full stack traces with source maps and variable values. Services aggregate errors across all environments, track trends over time, and alert teams before users report issues.

## Sentry Installation and Setup

Sentry provides Next.js SDK with automatic error instrumentation, source map uploading, release tracking, and performance monitoring. Sentry wizard automatically configures client, server, and edge runtime error tracking with single command.

```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

## Sentry Client, Server, and Edge Configuration

Wizard generates three config files for comprehensive error capture across all Next.js runtime environments. Client config enables session replay with privacy controls (mask text, block media). Server and edge configs use identical initialization with DSN and environment settings.

```typescript
// sentry.client.config.ts (Client-Side Errors)
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,  // 100% performance monitoring (reduce in production)
  replaysOnErrorSampleRate: 1.0,  // Session replay on errors
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
})

// sentry.server.config.ts (Server-Side Errors)
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})

// sentry.edge.config.ts (Edge Runtime Errors)
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})
```

## Sentry Environment Variables

Sentry requires DSN for error submission and auth token for source map uploads. Organization and project names enable release tracking and automatic issue assignment.

```bash
# .env.local
NEXT_PUBLIC_SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/7890123
SENTRY_AUTH_TOKEN=sntrys_your_auth_token_here  # For source map uploads
SENTRY_ORG=your-org
SENTRY_PROJECT=policy-node
```

## Sentry Next.js Config Integration

withSentryConfig wraps Next.js config to inject webpack source map uploading, hide production source maps, and suppress debug logs. Wizard automatically modifies next.config.js.

```javascript
// next.config.js (modified by wizard)
const { withSentryConfig } = require('@sentry/nextjs')

module.exports = withSentryConfig(
  {
    // Your Next.js config
  },
  {
    silent: true,  // Suppresses source map upload logs
    widenClientFileUpload: true,  // Upload larger set of source maps
    hideSourceMaps: true,  // Hides source maps from client bundle
    disableLogger: true,  // Removes Sentry debug logs from production
  }
)
```

## Automatic Client, Server, and API Error Capture

Sentry Next.js SDK automatically captures unhandled errors in Client Components, Server Components, API Routes, middleware, and edge functions without manual instrumentation. SDK intercepts unhandled promise rejections, render errors, and async exceptions across all runtime environments.

```typescript
// Client Component - Automatically captured
'use client'

export default function JobBoard() {
  const [jobs, setJobs] = useState([])

  useEffect(() => {
    // ✅ Unhandled promise rejection → Sentry captures automatically
    fetch('/api/jobs').then(res => res.json()).then(setJobs)
  }, [])

  // ✅ Render error → Sentry captures automatically
  return (
    <div>
      {jobs.map(job => (
        <div key={job.id}>{job.title.toUpperCase()}</div>  // Error if job.title is undefined
      ))}
    </div>
  )
}

// Server Component - Automatically captured
export default async function MunicipalityPage({ params }) {
  // ✅ Async error → Sentry captures automatically
  const municipality = await fetchMunicipality(params.slug)

  return <div>{municipality.name}</div>
}

// API Route - Automatically captured
export async function GET(request: NextRequest) {
  // ✅ Unhandled exception → Sentry captures automatically
  const data = await sanityClient.fetch(/* ... */)
  return NextResponse.json(data)
}
```

## Error Boundary Sentry Integration

App Router error.tsx files integrate with Sentry to capture component errors caught by React error boundaries. useEffect hook sends exception with tags and digest metadata for correlation with Next.js error logs.

```typescript
// app/error.tsx
'use client'

import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // ✅ Manually capture error from error boundary
    Sentry.captureException(error, {
      tags: { location: 'error-boundary' },
      extra: { digest: error.digest },
    })
  }, [error])

  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## Manual Error Capture with Tags

Sentry.captureException() provides manual error capture with custom tags, extra context, user information, and breadcrumbs for enhanced debugging. Manual capture enables re-throwing errors after logging while adding searchable metadata tags for filtering in Sentry UI.

```typescript
import * as Sentry from '@sentry/nextjs'

try {
  await fetchMunicipalities()
} catch (error) {
  Sentry.captureException(error)
  throw error
}
```

Tags enable filtering errors by section, operation, data source, or criticality level in Sentry dashboard.

```typescript
Sentry.captureException(error, {
  tags: {
    section: 'municipalities-api',
    operation: 'fetch',
    dataSource: 'sanity',
    critical: 'true',
  },
})

// Sentry UI: Filter by tag (e.g., show all errors with critical=true)
```

## Extra Context and User Tracking

Extra context provides non-searchable debugging metadata like IDs, retry counts, and request payloads. User context tracks affected user counts and correlates errors to specific sessions.

```typescript
Sentry.captureException(error, {
  extra: {
    municipalityId: params.slug,
    userId: session?.userId,
    s3Key: 'municipalities.csv',
    retryCount: 3,
    requestBody: JSON.stringify(request.body),
  },
})

// Sentry UI: Extra context shown in error details (not searchable)
```

Sentry.setUser() configures user context once at session start. All subsequent errors automatically include user metadata, enabling "N users affected" metrics.

```typescript
// Set user context at session start
Sentry.setUser({
  id: session.userId,
  email: session.email,
  username: session.username,
  role: session.role,
})

// All subsequent errors include user context
Sentry.captureException(error)

// Sentry UI: Shows "123 users affected" + user list
```

## Breadcrumbs for User Action Timeline

Sentry automatically captures navigation, console logs, and fetch calls. Manual breadcrumbs track custom events like filter selections or form submissions. Error timeline shows last 100 breadcrumbs before exception.

```typescript
// Sentry automatically captures navigation, console logs, fetch calls

// Manual breadcrumb for custom events
Sentry.addBreadcrumb({
  category: 'municipality',
  message: 'User selected municipality filter',
  level: 'info',
  data: {
    filter: 'population',
    value: '> 100k',
  },
})

// Breadcrumbs shown in error timeline (last 100 events before error)
```

## API Route Basic Error Tracking

Next.js API routes require manual error capture since automatic capture excludes request context like user ID, endpoint, and route params. Manual Sentry.captureException() in API route catch blocks adds endpoint tags and request metadata (URL, headers) before returning 500 responses. Re-throwing is not required since API routes terminate with NextResponse.json().

```typescript
// app/api/municipalities/route.ts
import * as Sentry from '@sentry/nextjs'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const municipalities = await fetchMunicipalities()
    return NextResponse.json(municipalities)
  } catch (error) {
    Sentry.captureException(error, {
      tags: {
        endpoint: '/api/municipalities',
        method: 'GET',
      },
      extra: {
        url: request.url,
        headers: Object.fromEntries(request.headers),
      },
    })

    return NextResponse.json(
      { error: 'Failed to fetch municipalities' },
      { status: 500 }
    )
  }
}
```

## API Route Request ID Correlation

Unique request IDs (crypto.randomUUID()) correlate logs, errors, and downstream API calls for distributed tracing. Sentry.captureMessage() tracks 404 warnings (not exceptions) with request ID for debugging.

```typescript
// app/api/municipalities/[slug]/route.ts
import * as Sentry from '@sentry/nextjs'

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  const requestId = crypto.randomUUID()

  try {
    const municipality = await fetchMunicipality(params.slug)

    if (!municipality) {
      // Track 404 errors (not exceptions, but still valuable)
      Sentry.captureMessage(`Municipality not found: ${params.slug}`, {
        level: 'warning',
        tags: { endpoint: '/api/municipalities/[slug]', statusCode: '404' },
        extra: { slug: params.slug, requestId },
      })

      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }

    return NextResponse.json(municipality)
  } catch (error) {
    Sentry.captureException(error, {
      tags: {
        endpoint: '/api/municipalities/[slug]',
        method: 'GET',
      },
      extra: {
        slug: params.slug,
        requestId,
      },
    })

    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

## API Route Custom Error Classes

Custom error classes with statusCode properties enable type guards for differentiating client errors (400-499, warning level) from server errors (500+, error level). Sentry.captureException() adjusts severity level based on status code.

```typescript
// lib/errors.ts
class MunicipalityError extends Error {
  readonly statusCode: number

  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalityError'
    this.statusCode = statusCode
  }
}

// app/api/municipalities/route.ts
try {
  if (!isValidSlug(params.slug)) {
    throw new MunicipalityError('Invalid slug format', 400)
  }

  const municipality = await fetchMunicipality(params.slug)

  if (!municipality) {
    throw new MunicipalityError('Municipality not found', 404)
  }

  return NextResponse.json(municipality)
} catch (error) {
  if (error instanceof MunicipalityError) {
    Sentry.captureException(error, {
      tags: { errorType: 'MunicipalityError', statusCode: error.statusCode },
      level: error.statusCode >= 500 ? 'error' : 'warning',
    })

    return NextResponse.json(
      { error: error.message },
      { status: error.statusCode }
    )
  }

  // Generic error
  Sentry.captureException(error)
  return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}
```

## Automatic Release Tracking with Source Maps

Sentry release tracking correlates errors with git commits, enabling error trend analysis per release, automatic issue assignment, and regression detection. withSentryConfig automatically uploads source maps during next build and associates errors with release versions. hideSourceMaps removes source maps from production client bundle while retaining them in Sentry for debugging.

```javascript
// next.config.js
const { withSentryConfig } = require('@sentry/nextjs')

module.exports = withSentryConfig(
  { /* Next.js config */ },
  {
    org: 'your-org',
    project: 'policy-node',
    authToken: process.env.SENTRY_AUTH_TOKEN,
    silent: true,
    widenClientFileUpload: true,  // Upload all source maps
    hideSourceMaps: true,  // Remove source maps from production bundle
  }
)
```

## Manual Release Creation and Deployment Tracking

sentry-cli enables manual release creation, source map uploading, commit association, and deployment notifications for CI/CD pipelines without withSentryConfig.

```bash
# Create release
npx sentry-cli releases new "$RELEASE_VERSION"

# Upload source maps
npx sentry-cli releases files "$RELEASE_VERSION" upload-sourcemaps ./out

# Finalize release
npx sentry-cli releases finalize "$RELEASE_VERSION"

# Associate commits (requires repository integration)
npx sentry-cli releases set-commits "$RELEASE_VERSION" --auto
```

Sentry UI compares releases to show new errors, regression errors (previously fixed, now reappearing), error-free rate (% sessions without errors), and crash-free rate (% sessions without crashes).

```bash
# Notify Sentry of deployment
npx sentry-cli releases deploys "$RELEASE_VERSION" new -e production
```

Source maps enable readable stack traces (original TypeScript/JSX line numbers), preserve variable names (no minification obfuscation), maintain file paths (original structure), and provide inline source code preview around error line.

## Automatic Page Load Performance Tracking

Sentry performance monitoring tracks API call duration, database query time, page load speed, and custom operation timing. browserTracingIntegration automatically tracks client-side page load performance. tracesSampleRate: 0.1 samples 10% of transactions to reduce Sentry quota consumption while maintaining statistical significance.

```typescript
// sentry.client.config.ts
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,  // 10% of transactions (reduce costs)
  integrations: [
    Sentry.browserTracingIntegration(),  // Automatic page load tracking
  ],
})
```

## Custom Transaction Performance Tracking

Sentry.startTransaction() measures custom operation duration like Sanity fetches or API calls. transaction.setTag() adds metadata (e.g., result count), and transaction.finish() records elapsed time.

```typescript
import * as Sentry from '@sentry/nextjs'

async function fetchMunicipalities() {
  const transaction = Sentry.startTransaction({
    op: 'fetch',
    name: 'Fetch Municipalities',
  })

  try {
    const municipalities = await sanityClient.fetch(/* ... */)
    transaction.setTag('municipalityCount', municipalities.length)
    transaction.finish()  // Records duration
    return municipalities
  } catch (error) {
    transaction.setStatus('internal_error')
    transaction.finish()
    throw error
  }
}
```

## Database Query Performance Spans

Spans nest within transactions to measure sub-operations like individual database queries. span.setData() records query-specific metadata (row counts, query params). Sentry UI enables setting alerts for transactions exceeding 500ms threshold. Slack notifications fire when thresholds breach. Performance trends display p50, p75, p95, p99 percentiles over time.

```typescript
async function fetchMunicipality(slug: string) {
  const transaction = Sentry.getCurrentHub().getScope()?.getTransaction()
  const span = transaction?.startChild({
    op: 'db.query',
    description: 'Fetch municipality by slug',
  })

  try {
    const municipality = await db.query(
      'SELECT * FROM municipalities WHERE slug = $1',
      [slug]
    )
    span?.setData('rowCount', municipality.rows.length)
    span?.finish()
    return municipality.rows[0]
  } catch (error) {
    span?.setStatus('internal_error')
    span?.finish()
    throw error
  }
}
```

## Session Replay on Errors

Sentry session replay records user interactions (clicks, scrolls, navigation) and replays session when error occurs, providing visual context for error debugging.

**Session Replay Configuration:**

```typescript
// sentry.client.config.ts
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  replaysOnErrorSampleRate: 1.0,  // 100% of error sessions
  replaysSessionSampleRate: 0.1,  // 10% of non-error sessions
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,  // Redact all text (PII protection)
      blockAllMedia: true,  // Block images/videos
      maskAllInputs: true,  // Redact input field values
    }),
  ],
})
```

**Privacy-Focused Replay Configuration:**

```typescript
Sentry.replayIntegration({
  // Mask PII
  maskAllText: true,
  maskAllInputs: true,
  blockAllMedia: true,

  // Unmask specific elements (non-sensitive UI)
  unblock: ['.public-header', '.navigation'],

  // Redact network request bodies
  networkDetailAllowUrls: [],
  networkCaptureBodies: false,
})
```

**Session Replay Features:**
- Visual playback of user actions before error
- Console logs shown in timeline
- Network requests shown in timeline
- DOM mutations recorded
- Privacy controls (mask text, inputs, media)

## Alerting and Notifications

Sentry alerts notify teams of new errors, error spikes, regression errors, and performance degradations via Slack, email, PagerDuty, or webhooks.

**Alert Types:**

1. **Issue Alerts:** Triggered when error occurs
   - First seen (new error type)
   - Error count exceeds threshold (10+ errors in 1 hour)
   - Users affected exceeds threshold (5+ users)
   - Error rate increase (2x spike compared to previous period)

2. **Metric Alerts:** Triggered by performance degradation
   - Transaction duration exceeds threshold (>500ms)
   - Error rate exceeds threshold (>1%)
   - Crash-free rate drops below threshold (<99%)

**Slack Integration:**

```yaml
# Sentry UI: Settings → Integrations → Slack
# Configure:
- Alert channel: #errors-production
- Alert conditions:
  - New error first seen
  - Error affects >5 users
  - Error count >10 in 1 hour
```

**Email Alerts:**

```yaml
# Sentry UI: Settings → Alerts → New Alert Rule
# Configure:
- Alert name: "High Error Rate - Production"
- Environment: production
- Condition: Error count >50 in 1 hour
- Notify: email → engineering@company.com
```

**PagerDuty Integration:**

```yaml
# Sentry UI: Settings → Integrations → PagerDuty
# Configure:
- Service: policy-node-production
- Alert conditions: Critical errors only (tagged critical=true)
```

## Codebase Patterns

**Current State (0% Adoption):**

```typescript
// Policy-node: 160 try/catch blocks, 116 console.error calls
catch (error) {
  console.error('Municipalities API error:', error)
}
// No error tracking, no alerting, no user context

// Helix: 1 try/catch block (commented-out logging)
catch (error) {
  // console.error(error)  ← Silent failure
}
// Zero visibility into production errors

// Kariusdx: 5 try/catch blocks, 0 console.error calls
catch (error) {
  // Silent catch (no logging, no tracking)
}
// Zero visibility into production errors
```

**Recommended Pattern:**

```typescript
import * as Sentry from '@sentry/nextjs'

try {
  await fetchMunicipalities()
} catch (error) {
  Sentry.captureException(error, {
    tags: {
      section: 'municipalities-api',
      operation: 'fetch',
      critical: 'true',
    },
    extra: {
      userId: session?.userId,
      municipalityId: params.slug,
    },
  })
  throw error  // Re-throw for error boundary to catch
}
```

**Adoption Summary:**
- Error tracking services: 0% (no Sentry, Rollbar, Bugsnag)
- Source map uploads: 0%
- Release tracking: 0%
- Performance monitoring: 0%
- Session replay: 0%
- Alerting: 0%

## Anti-Patterns

**1. Catching Errors Without Tracking:**
```typescript
// ❌ BAD: Catch error but don't track
catch (error) {
  console.error(error)
  return null
}
// Developers unaware of production errors
```

**2. Tracking Errors Without User Context:**
```typescript
// ❌ BAD: No user context
Sentry.captureException(error)

// ✅ GOOD: Include user context
Sentry.setUser({ id: session.userId, email: session.email })
Sentry.captureException(error)
```

**3. No Release Tracking:**
```typescript
// ❌ BAD: Errors not correlated with releases
// Cannot determine which deploy introduced error
```

**4. Excessive tracesSampleRate:**
```typescript
// ❌ BAD: 100% performance monitoring (expensive)
Sentry.init({ tracesSampleRate: 1.0 })

// ✅ GOOD: 10% sampling (sufficient for trends)
Sentry.init({ tracesSampleRate: 0.1 })
```

## Recommendations

**Priority 1: Install Sentry (All Repos)**
- Run `npx @sentry/wizard@latest -i nextjs`
- Configure SENTRY_DSN environment variable
- Add Sentry.setUser() at session initialization
- Integrate error.tsx with Sentry.captureException()

**Priority 2: Add User Context**
- Set user ID, email, role in Sentry.setUser()
- Track affected users per error
- Filter errors by user segment (admin, free, paid)

**Priority 3: Enable Release Tracking**
- Upload source maps automatically (withSentryConfig)
- Set release version from git commit SHA
- Track errors per release (regression detection)

**Priority 4: Configure Alerts**
- Slack alerts for new errors (first seen)
- Email alerts for high error rates (>10 errors/hour)
- PagerDuty for critical errors (tagged critical=true)

**Priority 5: Add Performance Monitoring**
- Set tracesSampleRate: 0.1 (10% sampling)
- Track slow API routes (>500ms)
- Monitor database query duration
