---
title: "Silent Failure Antipatterns: Catching Errors Without User Feedback"
category: "error-handling"
subcategory: "antipatterns"
tags: ["antipatterns", "silent-failure", "error-handling", "user-experience", "debugging"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Silent Failure Antipatterns: Catching Errors Without User Feedback

Silent failures occur when catch blocks suppress errors without logging, user feedback, or error state management, causing features to fail invisibly. Analyzed codebases show 33% silent failure patterns (helix JobBoard component: commented-out error logging, returns undefined on error, no user feedback), resulting in users unable to distinguish between "no data available" and "data fetch failed".

## The Silent Failure Antipattern

Silent failures catch errors but provide no visibility to developers (no logging) or users (no error UI), causing features to appear functional while failing invisibly in production.

**Helix JobBoard Component (Production Antipattern):**

```typescript
// app/components/JobBoard/JobBoard.tsx
const fetchGreenhouseData = async () => {
  let response
  try {
    const axios = (await import('axios')).default
    response = await axios.get('https://boards-api.greenhouse.io/v1/boards/helix/departments')
  } catch (error) {
    // console.error(error)  ← COMMENTED OUT: No developer visibility
  }
  return response  // Returns undefined on error
}

useEffect(() => {
  (async () => {
    const greenhouseData: GreenhouseDepartmentsData | undefined = await fetchGreenhouseData()
    const jobsByDept = greenhouseData?.data.departments.filter((dept) => dept.jobs.length > 0)
    // ⚠️ SILENT FAILURE: If fetch fails, greenhouseData is undefined
    // Optional chaining prevents runtime error but provides NO user feedback
    setDepts(jobsByDept)  // Sets undefined, UI shows empty state
  })()
}, [])

return (
  <div>
    {depts && depts.length > 0 ? (
      depts.map((dept) => <JobDepartment key={dept.id} {...dept} />)
    ) : (
      <p>No jobs available</p>  // Shown for both "no jobs" AND "API failed"
    )}
  </div>
)
```

**Problems:**
1. **No Developer Visibility:** Error logging commented out (developers unaware of production failures)
2. **No User Feedback:** Users see "No jobs available" for both legitimate empty state and API failures
3. **Indistinguishable States:** Cannot differentiate between "no jobs exist" vs "API request failed"
4. **Lost Context:** Error details lost (network timeout, 404, 500, rate limit?)
5. **No Retry Mechanism:** Users cannot retry failed request
6. **No Error Tracking:** Error not sent to monitoring service (Sentry)

**User Impact:**
- Users assume no jobs are available (false negative)
- Users cannot report error (no error message shown)
- Support team cannot diagnose issue without error logs

## Correct Error Handling with Error States

Error states store error information in component state, enabling conditional rendering of error UI, retry buttons, and error logging.

**Corrected JobBoard Component:**

```typescript
'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

export default function JobBoard() {
  const [depts, setDepts] = useState<Department[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchGreenhouseData = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.get(
        'https://boards-api.greenhouse.io/v1/boards/helix/departments',
        { timeout: 10000 }  // 10 second timeout
      )
      return response.data
    } catch (error) {
      console.error('Failed to fetch Greenhouse jobs:', error)
      throw error  // Re-throw for caller to handle
    }
  }

  useEffect(() => {
    const loadJobs = async () => {
      try {
        const data = await fetchGreenhouseData()
        const jobsByDept = data.departments.filter((dept) => dept.jobs.length > 0)
        setDepts(jobsByDept)
      } catch (error) {
        setError(error instanceof Error ? error : new Error('Failed to load jobs'))
      } finally {
        setLoading(false)
      }
    }

    loadJobs()
  }, [])

  // Loading state
  if (loading) {
    return <div>Loading jobs...</div>
  }

  // Error state
  if (error) {
    return (
      <div className={styles.error}>
        <h3>Unable to load jobs</h3>
        <p>We're having trouble connecting to our jobs board. Please try again later.</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    )
  }

  // Empty state (legitimate no jobs)
  if (!depts || depts.length === 0) {
    return <p>No jobs available at this time. Check back soon!</p>
  }

  // Success state
  return (
    <div>
      {depts.map((dept) => <JobDepartment key={dept.id} {...dept} />)}
    </div>
  )
}
```

**Improvements:**
1. ✅ Error state stored in component state
2. ✅ Error logged to console (developer visibility)
3. ✅ Error UI shown to users (clear feedback)
4. ✅ Retry mechanism provided (user can reload)
5. ✅ Distinct UI for loading, error, empty, success states
6. ✅ Error re-thrown for potential error boundary to catch

## Empty State vs Error State Distinction

Empty states represent legitimate no-data scenarios (no jobs available), while error states represent failures (API down, network timeout, 404). Users must distinguish between these states.

**Indistinguishable States (Bad):**

```typescript
// ❌ BAD: Same UI for empty and error states
const [jobs, setJobs] = useState<Job[] | undefined>()

useEffect(() => {
  fetchJobs().then(setJobs).catch(() => setJobs(undefined))
}, [])

return jobs && jobs.length > 0 ? (
  <JobList jobs={jobs} />
) : (
  <p>No jobs available</p>  // Shown for both empty AND error
)
```

**Distinguishable States (Good):**

```typescript
// ✅ GOOD: Separate UI for empty and error states
const [jobs, setJobs] = useState<Job[] | null>(null)
const [error, setError] = useState<Error | null>(null)
const [loading, setLoading] = useState(true)

useEffect(() => {
  fetchJobs()
    .then(setJobs)
    .catch(setError)
    .finally(() => setLoading(false))
}, [])

if (loading) return <Spinner />
if (error) return <ErrorMessage error={error} onRetry={fetchJobs} />
if (!jobs || jobs.length === 0) return <EmptyState message="No jobs available" />
return <JobList jobs={jobs} />
```

**State Matrix:**

| Loading | Error | Jobs | UI Shown |
|---------|-------|------|----------|
| true | null | null | Loading spinner |
| false | Error | null | Error message + retry button |
| false | null | [] | Empty state (no jobs) |
| false | null | [Job, ...] | Job list |

## Logging Errors for Developer Visibility

Commented-out console.error calls eliminate developer visibility into production errors. Errors must be logged with context (operation name, timestamp, user ID) for debugging.

**Bad: Commented-Out Logging:**

```typescript
// ❌ BAD: Error logging commented out
catch (error) {
  // console.error(error)  ← Developers cannot debug production failures
}
```

**Good: Structured Error Logging:**

```typescript
// ✅ GOOD: Log with context
import { logger } from '@/lib/logger'

catch (error) {
  logger.error({
    err: error,
    context: 'greenhouse-api',
    operation: 'fetch-jobs',
    endpoint: 'https://boards-api.greenhouse.io/v1/boards/helix/departments',
    timestamp: new Date().toISOString(),
  }, 'Failed to fetch Greenhouse jobs')
  setError(error instanceof Error ? error : new Error('Failed to load jobs'))
}
```

**With Error Tracking Service:**

```typescript
// ✅ BEST: Log + send to error tracking service
import * as Sentry from '@sentry/nextjs'

catch (error) {
  console.error('Failed to fetch Greenhouse jobs:', error)

  Sentry.captureException(error, {
    tags: {
      section: 'job-board',
      api: 'greenhouse',
    },
    extra: {
      endpoint: 'https://boards-api.greenhouse.io/v1/boards/helix/departments',
      userAgent: navigator.userAgent,
    },
  })

  setError(error instanceof Error ? error : new Error('Failed to load jobs'))
}
```

## Returning Undefined vs Throwing Errors

Returning undefined on error suppresses failures, forcing callers to handle undefined (easy to forget). Throwing errors propagates failures, enabling error boundaries to catch and display error UI.

**Bad: Returns undefined on Error:**

```typescript
// ❌ BAD: Returns undefined, caller must handle
async function fetchJobs(): Promise<Job[] | undefined> {
  try {
    const response = await fetch('/api/jobs')
    return await response.json()
  } catch (error) {
    // console.error(error)  ← Commented out
    return undefined  // Silent failure
  }
}

// Caller must remember to check for undefined
const jobs = await fetchJobs()
if (jobs) {
  setJobs(jobs)
} else {
  // Easy to forget this check → silent failure
}
```

**Good: Throws Errors:**

```typescript
// ✅ GOOD: Throws error, caller catches or error boundary catches
async function fetchJobs(): Promise<Job[]> {
  try {
    const response = await fetch('/api/jobs')

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Failed to fetch jobs:', error)
    throw error  // Re-throw for caller or error boundary
  }
}

// Caller must catch or let error boundary handle
try {
  const jobs = await fetchJobs()
  setJobs(jobs)
} catch (error) {
  setError(error instanceof Error ? error : new Error('Failed to load jobs'))
}
```

**Error Boundary Integration:**

```typescript
// Wrap component in error boundary
<ErrorBoundary fallback={<ErrorFallback />}>
  <JobBoard />
</ErrorBoundary>

// JobBoard component throws on error
async function loadJobs() {
  const jobs = await fetchJobs()  // Throws on error
  setJobs(jobs)
}

// Error boundary catches thrown errors automatically
```

## Optional Chaining Masking Errors

Optional chaining (?.) prevents runtime errors but masks underlying failures, converting errors into undefined without alerting developers or users.

**Helix JobBoard Pattern (Antipattern):**

```typescript
// ❌ BAD: Optional chaining masks API failure
const greenhouseData: GreenhouseDepartmentsData | undefined = await fetchGreenhouseData()
const jobsByDept = greenhouseData?.data.departments.filter((dept) => dept.jobs.length > 0)
// If fetchGreenhouseData() returns undefined (error), jobsByDept is undefined
// No runtime error, no user feedback, silent failure
```

**Correct Pattern with Error Handling:**

```typescript
// ✅ GOOD: Explicitly handle undefined
const greenhouseData = await fetchGreenhouseData()

if (!greenhouseData) {
  setError(new Error('Failed to fetch jobs'))
  return
}

const jobsByDept = greenhouseData.data.departments.filter(
  (dept) => dept.jobs.length > 0
)
setDepts(jobsByDept)
```

**When Optional Chaining is Appropriate:**

```typescript
// ✅ GOOD: Optional chaining for truly optional data
const userName = user?.profile?.name || 'Anonymous'

// ❌ BAD: Optional chaining for required data
const jobs = response?.data?.jobs  // If response is undefined, jobs is undefined silently
```

## User-Facing Error Messages

User-facing error messages should be actionable (tell users what to do), non-technical (no stack traces), and empathetic (acknowledge frustration).

**Bad: Technical Error Messages:**

```typescript
// ❌ BAD: Technical error message exposed to users
<p>Error: Network timeout after 10000ms at axios.get:234</p>
```

**Good: User-Friendly Error Messages:**

```typescript
// ✅ GOOD: User-friendly, actionable error message
<div className={styles.error}>
  <h3>Unable to load jobs</h3>
  <p>We're having trouble connecting to our jobs board. Please check your internet connection and try again.</p>
  <button onClick={handleRetry}>Retry</button>
  <a href="/contact">Contact support if this persists</a>
</div>
```

**Error Message Guidelines:**
- **What happened:** "Unable to load jobs"
- **Why it happened (optional):** "We're having trouble connecting"
- **What to do:** "Please check your internet connection and try again"
- **Escape hatch:** "Contact support if this persists"
- **Retry mechanism:** Retry button or reload link

**Error-Specific Messages:**

```typescript
function getErrorMessage(error: Error): string {
  if (error.message.includes('timeout')) {
    return 'The request is taking longer than expected. Please check your internet connection and try again.'
  }

  if (error.message.includes('404')) {
    return 'We couldn't find the jobs board. Please contact support.'
  }

  if (error.message.includes('429')) {
    return 'Too many requests. Please wait a moment and try again.'
  }

  if (error.message.includes('500')) {
    return 'Our server is experiencing issues. Please try again later.'
  }

  return 'Something went wrong. Please try again or contact support.'
}
```

## Retry Mechanisms for Transient Failures

Transient failures (network timeout, rate limit, server restart) succeed on retry. Retry mechanisms enable users to recover from transient failures without page reload.

**Manual Retry (User-Triggered):**

```typescript
const [retryCount, setRetryCount] = useState(0)

const handleRetry = async () => {
  setError(null)
  setLoading(true)
  setRetryCount(retryCount + 1)

  try {
    const jobs = await fetchJobs()
    setJobs(jobs)
  } catch (error) {
    setError(error instanceof Error ? error : new Error('Failed to load jobs'))
  } finally {
    setLoading(false)
  }
}

return error ? (
  <div>
    <p>Failed to load jobs</p>
    <button onClick={handleRetry}>Retry</button>
  </div>
) : (
  <JobList jobs={jobs} />
)
```

**Automatic Retry with Exponential Backoff:**

```typescript
async function fetchWithRetry<T>(
  fetchFn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fetchFn()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Fetch failed')
      console.warn(`Attempt ${attempt + 1} failed:`, lastError.message)

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt)
        console.log(`Retrying in ${delay}ms...`)
        await new Promise((resolve) => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError!
}

// Usage:
const jobs = await fetchWithRetry(() => fetchJobs(), 3, 1000)
// Attempts: 0ms, 1000ms delay, 2000ms delay, 4000ms delay
```

**Smart Retry (Retry Only on Transient Errors):**

```typescript
function isRetryableError(error: Error): boolean {
  const retryableStatusCodes = [408, 429, 500, 502, 503, 504]
  const retryableMessages = ['timeout', 'network error', 'ECONNRESET']

  // Check HTTP status code
  if ('statusCode' in error && typeof error.statusCode === 'number') {
    return retryableStatusCodes.includes(error.statusCode)
  }

  // Check error message
  return retryableMessages.some((msg) =>
    error.message.toLowerCase().includes(msg)
  )
}

async function fetchWithSmartRetry<T>(fetchFn: () => Promise<T>): Promise<T> {
  try {
    return await fetchFn()
  } catch (error) {
    if (isRetryableError(error as Error)) {
      console.log('Retryable error detected, retrying once...')
      return await fetchFn()
    }
    throw error  // Non-retryable error (404, 401, etc.)
  }
}
```

## Codebase Patterns

**Helix (Silent Failure Observed):**

```typescript
// JobBoard.tsx (ANTIPATTERN)
const fetchGreenhouseData = async () => {
  let response
  try {
    const axios = (await import('axios')).default
    response = await axios.get('https://boards-api.greenhouse.io/v1/boards/helix/departments')
  } catch (error) {
    // console.error(error)  ← COMMENTED OUT
  }
  return response  // Returns undefined on error
}

// No error state, no user feedback, no retry mechanism
```

**Policy-Node (No Silent Failures Observed):**
- 160 try/catch blocks, 116 console.error calls
- All errors logged (no commented-out logging)
- API routes return proper error responses

**Kariusdx (Potential Silent Failures):**
- 5 try/catch blocks, 0 console.error calls
- No error logging observed (likely silent failures)

**Adoption Summary:**
- Silent failures (commented-out logging): 33% (helix JobBoard)
- Error states in components: 0% (no error state management observed)
- User-facing error messages: 0%
- Retry mechanisms: 0%

## Anti-Patterns Summary

**1. Commented-Out Error Logging:**
```typescript
// ❌ catch (error) { /* console.error(error) */ }
// ✅ catch (error) { console.error('Context:', error) }
```

**2. Returning undefined on Error:**
```typescript
// ❌ catch (error) { return undefined }
// ✅ catch (error) { throw error }
```

**3. No Error State in Components:**
```typescript
// ❌ const [data, setData] = useState()
// ✅ const [data, setData] = useState(); const [error, setError] = useState()
```

**4. Same UI for Empty and Error:**
```typescript
// ❌ {!data && <p>No data</p>}
// ✅ {error ? <Error /> : !data ? <Empty /> : <Data />}
```

**5. No Retry Mechanism:**
```typescript
// ❌ {error && <p>Error occurred</p>}
// ✅ {error && <><p>Error</p><button onClick={retry}>Retry</button></>}
```

## Recommendations

**Priority 1: Fix Helix JobBoard Silent Failure**
- Add error state to component
- Uncomment error logging (or use structured logging)
- Display error UI with retry button
- Send errors to Sentry for monitoring

**Priority 2: Add Error States to All Components**
- useState for error state in all data-fetching components
- Conditional rendering for loading, error, empty, success states
- User-friendly error messages (no stack traces)

**Priority 3: Add Error Logging**
- Uncomment all console.error calls
- Replace console.error with structured logging (Pino)
- Add context to all error logs (operation, timestamp, user ID)

**Priority 4: Distinguish Empty vs Error States**
- Separate UI for "no data available" vs "failed to load data"
- Provide retry button for error states
- Provide helpful messaging for empty states ("Check back soon!")

**Priority 5: Integrate Error Tracking**
- Send all client-side errors to Sentry
- Track affected users per error
- Set up alerts for high error rates
