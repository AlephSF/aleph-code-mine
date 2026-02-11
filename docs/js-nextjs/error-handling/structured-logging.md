---
title: "Structured Logging with Pino for Next.js Production Debugging"
category: "error-handling"
subcategory: "logging"
tags: ["logging", "pino", "winston", "debugging", "observability"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

# Structured Logging with Pino for Next.js Production Debugging

Structured logging provides searchable, aggregatable, machine-readable log output using JSON formatting and contextual metadata. Analyzed codebases show 0% adoption of structured logging libraries (Winston, Pino, Bunyan), relying exclusively on console.error/console.log (policy-node: 116 console.error calls, helix: 1 call, kariusdx: 0 calls). Structured logging enables log aggregation (Datadog, New Relic, CloudWatch), error correlation, and production debugging.

## Why Structured Logging Matters

Console.error/console.log produce unstructured text output, limiting searchability, aggregation, and analysis. Structured logging outputs JSON objects with consistent fields (timestamp, level, context, error stack), enabling powerful querying and alerting in production.

**Current Pattern (Policy-Node - 116 console.error calls):**

```typescript
// ❌ Unstructured: No timestamps, no context, no searchability
catch (error) {
  console.error('Failed to fetch municipalities:', error)
}

// Production output (unstructured text):
// Failed to fetch municipalities: Error: Network timeout
```

**Structured Logging Pattern (Recommended):**

```typescript
// ✅ Structured: JSON output with timestamps, context, error details
import { logger } from '@/lib/logger'

catch (error) {
  logger.error({
    err: error,
    context: 'municipalities-api',
    operation: 'fetch',
    timestamp: new Date().toISOString(),
  }, 'Failed to fetch municipalities')
}

// Production output (structured JSON):
// {"level":"error","time":"2026-02-11T10:30:00.000Z","err":{"type":"Error","message":"Network timeout","stack":"..."},"context":"municipalities-api","operation":"fetch","msg":"Failed to fetch municipalities"}
```

**Benefits of Structured Logging:**
- Searchable: Query by error type, context, user ID, timestamp
- Aggregatable: Group errors by context, count occurrences over time
- Alertable: Trigger alerts when error count exceeds threshold
- Contextual: Include user ID, request ID, operation, data keys
- Correlatable: Link errors across services using trace IDs

## Pino: Fastest Node.js Logger

Pino provides production-grade structured logging with minimal performance overhead (5-10x faster than Winston). Outputs newline-delimited JSON (NDJSON) for streaming to log aggregation services.

**Installation:**

```bash
npm install pino pino-pretty
```

**Basic Configuration:**

```typescript
// lib/logger.ts
import { pino } from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => {
      return { level: label }
    },
  },
  browser: {
    disabled: true,  // Disable in browser (Next.js Client Components)
  },
})
```

**Development Configuration (Pretty Output):**

```typescript
// lib/logger.ts
import { pino } from 'pino'

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: isDevelopment
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'HH:MM:ss',
          ignore: 'pid,hostname',
        },
      }
    : undefined,  // Production: raw JSON output
})
```

**Production vs Development Output:**

```typescript
logger.info({ userId: '123', action: 'login' }, 'User logged in')

// Development (pino-pretty):
// [10:30:00] INFO: User logged in
//     userId: "123"
//     action: "login"

// Production (raw JSON):
// {"level":"info","time":1707649800000,"userId":"123","action":"login","msg":"User logged in"}
```

## Logging Levels and When to Use Them

Pino supports standard logging levels (fatal, error, warn, info, debug, trace), enabling log filtering by severity in production.

**Level Hierarchy (fatal > error > warn > info > debug > trace):**

```typescript
import { logger } from '@/lib/logger'

// FATAL: Application crashes, unrecoverable errors
logger.fatal({ err: error, context: 'db-connection' }, 'Database connection failed, shutting down')
process.exit(1)

// ERROR: Exceptions, API failures, data corruption
logger.error({ err: error, s3Key: 'data.csv', bucket: 'prod' }, 'Failed to download S3 file')

// WARN: Degraded functionality, retries, deprecated API usage
logger.warn({ retryCount: 3, endpoint: '/api/metrics' }, 'API request failed, retrying')

// INFO: Business events, user actions, state changes (default level)
logger.info({ userId: '123', municipalityId: 'oslo' }, 'User viewed municipality page')

// DEBUG: Detailed debugging (disabled in production by default)
logger.debug({ params: req.params, query: req.query }, 'Incoming API request')

// TRACE: Ultra-detailed tracing (rarely used)
logger.trace({ sqlQuery: query, duration: 45 }, 'Database query executed')
```

**Production LOG_LEVEL Configuration:**

```bash
# .env.production
LOG_LEVEL=info  # Only logs info, warn, error, fatal (filters out debug, trace)

# .env.development
LOG_LEVEL=debug  # Logs debug and above (filters out trace only)
```

**Environment-Based Level Control:**

```typescript
// lib/logger.ts
export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
})

// Dynamically change level at runtime
logger.level = 'debug'
```

## Error Logging Best Practices

Pino requires errors passed as err property to enable automatic serialization of stack traces, error types, and error messages.

**Correct Error Logging:**

```typescript
// ✅ CORRECT: Pass error as 'err' property
catch (error) {
  logger.error({ err: error, context: 's3-download' }, 'Failed to download S3 file')
}

// Output includes full error details:
// {"level":"error","err":{"type":"Error","message":"Network timeout","stack":"Error: Network timeout\n  at fetch (...)"},"context":"s3-download","msg":"Failed to download S3 file"}
```

**Incorrect Error Logging:**

```typescript
// ❌ INCORRECT: Error passed as different property
catch (error) {
  logger.error({ error: error }, 'Failed to download S3 file')
}
// Output loses error serialization (no stack trace)

// ❌ INCORRECT: Error in message string
catch (error) {
  logger.error(`Failed to download S3 file: ${error}`)
}
// Output loses structured error object
```

**Error with Additional Context:**

```typescript
// ✅ BEST: Error + context metadata
catch (error) {
  logger.error({
    err: error,
    context: 's3-download',
    s3Key: 'municipalities.csv',
    bucket: 'policy-node-data',
    attemptNumber: 3,
    userId: session?.userId,
  }, 'Failed to download S3 file after 3 retries')
}
```

## Child Loggers for Request Context

Pino child loggers inherit parent logger configuration while adding request-specific context (request ID, user ID, route), enabling error correlation across log entries.

**Request-Scoped Logger:**

```typescript
// middleware.ts
import { logger } from '@/lib/logger'
import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const requestId = crypto.randomUUID()
  const requestLogger = logger.child({
    requestId,
    path: request.nextUrl.pathname,
    method: request.method,
  })

  // Attach logger to request for use in route handlers
  ;(request as any).logger = requestLogger

  requestLogger.info('Incoming request')
  return NextResponse.next()
}
```

**Using Request Logger in API Route:**

```typescript
// app/api/municipalities/route.ts
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const logger = (request as any).logger

  logger.info({ operation: 'fetch-municipalities' }, 'Starting municipality fetch')

  try {
    const municipalities = await fetchMunicipalities()
    logger.info({ count: municipalities.length }, 'Successfully fetched municipalities')
    return NextResponse.json(municipalities)
  } catch (error) {
    logger.error({ err: error }, 'Failed to fetch municipalities')
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// All logs include requestId, path, method from child logger:
// {"level":"info","requestId":"abc-123","path":"/api/municipalities","method":"GET","msg":"Incoming request"}
// {"level":"info","requestId":"abc-123","path":"/api/municipalities","method":"GET","operation":"fetch-municipalities","msg":"Starting municipality fetch"}
// {"level":"error","requestId":"abc-123","path":"/api/municipalities","method":"GET","err":{...},"msg":"Failed to fetch municipalities"}
```

**User-Scoped Logger:**

```typescript
// lib/get-user-logger.ts
import { logger } from '@/lib/logger'
import { getSession } from '@/lib/session'

export async function getUserLogger() {
  const session = await getSession()

  return logger.child({
    userId: session?.userId,
    userEmail: session?.email,
    userRole: session?.role,
  })
}

// Usage in Server Component:
const userLogger = await getUserLogger()
userLogger.info({ action: 'view-municipality', municipalityId: 'oslo' }, 'User viewed municipality')

// Output includes user context:
// {"level":"info","userId":"user-123","userEmail":"user@example.com","userRole":"admin","action":"view-municipality","municipalityId":"oslo","msg":"User viewed municipality"}
```

## Performance Monitoring with Pino

Pino supports performance timing through child loggers with bindings, enabling measurement of operation duration, database query time, and API call latency.

**Operation Timing:**

```typescript
import { logger } from '@/lib/logger'

async function fetchMunicipalities() {
  const startTime = Date.now()

  try {
    const municipalities = await sanityClient.fetch(/* ... */)
    const duration = Date.now() - startTime

    logger.info({
      operation: 'fetch-municipalities',
      duration,
      count: municipalities.length,
    }, `Fetched municipalities in ${duration}ms`)

    return municipalities
  } catch (error) {
    const duration = Date.now() - startTime
    logger.error({
      err: error,
      operation: 'fetch-municipalities',
      duration,
    }, `Failed to fetch municipalities after ${duration}ms`)
    throw error
  }
}
```

**Database Query Timing:**

```typescript
async function queryDatabase(sql: string, params: any[]) {
  const queryLogger = logger.child({ context: 'database' })
  const startTime = Date.now()

  try {
    const result = await db.query(sql, params)
    const duration = Date.now() - startTime

    queryLogger.debug({
      sql,
      params,
      duration,
      rowCount: result.rows.length,
    }, 'Database query executed')

    return result
  } catch (error) {
    const duration = Date.now() - startTime
    queryLogger.error({
      err: error,
      sql,
      params,
      duration,
    }, 'Database query failed')
    throw error
  }
}
```

**Threshold-Based Logging:**

```typescript
// Only log slow queries (>100ms)
const duration = Date.now() - startTime

if (duration > 100) {
  logger.warn({
    operation: 'fetch-municipalities',
    duration,
    threshold: 100,
  }, 'Slow query detected')
}
```

## Log Sanitization: Removing Sensitive Data

Pino redaction removes sensitive data (passwords, API keys, tokens) from logs before serialization, preventing credential leaks in production logs.

**Automatic Redaction:**

```typescript
// lib/logger.ts
import { pino } from 'pino'

export const logger = pino({
  redact: {
    paths: [
      'password',
      'apiKey',
      'token',
      'authorization',
      'cookie',
      'sessionId',
      '*.password',
      '*.apiKey',
      'user.email',  // Redact PII if required
    ],
    censor: '[REDACTED]',
  },
})

// Usage:
logger.info({ username: 'john', password: 'secret123' }, 'User login')

// Output (password redacted):
// {"level":"info","username":"john","password":"[REDACTED]","msg":"User login"}
```

**Dynamic Redaction:**

```typescript
// Redact based on environment
export const logger = pino({
  redact: {
    paths: process.env.NODE_ENV === 'production'
      ? ['password', 'apiKey', 'token', 'user.email', 'user.phone']  // Full redaction in prod
      : ['password', 'apiKey', 'token'],  // Minimal redaction in dev
    censor: '[REDACTED]',
  },
})
```

**Nested Field Redaction:**

```typescript
// Redact nested fields
logger.info({
  user: {
    id: '123',
    email: 'user@example.com',  // Redacted
    password: 'secret',  // Redacted
  },
  apiKey: 'abc-123',  // Redacted
}, 'User data')

// Output:
// {"level":"info","user":{"id":"123","email":"[REDACTED]","password":"[REDACTED]"},"apiKey":"[REDACTED]","msg":"User data"}
```

## Integration with Error Tracking Services

Pino integrates with Sentry, Datadog, and other error tracking services through transport streams, enabling automatic error reporting from logs.

**Sentry Integration:**

```typescript
// lib/logger.ts
import { pino } from 'pino'
import * as Sentry from '@sentry/nextjs'

const sentryTransport = pino.transport({
  target: 'pino-sentry-transport',
  options: {
    sentry: Sentry,
    level: 'error',  // Only send error+ logs to Sentry
  },
})

export const logger = pino(sentryTransport)

// Usage:
logger.error({ err: error, userId: '123' }, 'Payment processing failed')
// Automatically sent to Sentry with context
```

**Datadog Integration:**

```typescript
// lib/logger.ts
import { pino } from 'pino'

export const logger = pino({
  formatters: {
    level: (label) => {
      return { level: label, service: 'policy-node', env: process.env.NODE_ENV }
    },
  },
})

// Logs automatically picked up by Datadog agent
// (configured to read stdout JSON logs)
```

## Codebase Patterns

**Policy-Node (116 console.error calls):**
```typescript
// Unstructured logging (repeated 116+ times)
catch (error) {
  console.error('Municipalities API error:', error)
  console.error('S3 download failed:', error)
  console.error('CSV parsing error:', error)
}
```

**Helix (1 console.error call):**
```typescript
// Single console.error (commented out in JobBoard)
catch (error) {
  // console.error(error)  ← Commented out, silent failure
}
```

**Kariusdx (0 console.error calls):**
- No error logging observed
- Silent failures (0 visibility into production errors)

**Adoption Summary:**
- Structured logging libraries: 0% (no Pino, Winston, Bunyan in package.json)
- console.error usage: 33% (policy-node only, 116 calls)
- console.log usage: Minimal (scattered, no standardization)
- Log aggregation: 0% (no Datadog, New Relic, CloudWatch integration)

## Anti-Patterns

**1. String Concatenation in Logs:**
```typescript
// ❌ BAD: String concatenation loses structure
logger.error(`Failed to fetch user ${userId}: ${error}`)

// ✅ GOOD: Structured fields
logger.error({ err: error, userId }, 'Failed to fetch user')
```

**2. Logging Sensitive Data:**
```typescript
// ❌ BAD: Logs password in plaintext
logger.info({ username, password }, 'User login attempt')

// ✅ GOOD: Redact sensitive fields
logger.info({ username }, 'User login attempt')
```

**3. Over-Logging in Production:**
```typescript
// ❌ BAD: Debug logs in production
logger.debug({ fullRequestBody: req.body }, 'API request received')
// Bloats logs, increases costs

// ✅ GOOD: Control level via environment
// LOG_LEVEL=info in production (filters out debug)
```

**4. Error as String:**
```typescript
// ❌ BAD: Error converted to string
logger.error({ error: error.message }, 'Failed to process')
// Loses stack trace

// ✅ GOOD: Error as 'err' object
logger.error({ err: error }, 'Failed to process')
```

## Migration from console.error

**Step 1: Install Pino:**
```bash
npm install pino pino-pretty
```

**Step 2: Create Logger Module:**
```typescript
// lib/logger.ts
import { pino } from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
})
```

**Step 3: Replace console.error:**
```typescript
// Before:
catch (error) {
  console.error('API error:', error)
}

// After:
import { logger } from '@/lib/logger'

catch (error) {
  logger.error({ err: error, context: 'api' }, 'API error occurred')
}
```

**Step 4: Add Request Context:**
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const requestLogger = logger.child({
    requestId: crypto.randomUUID(),
    path: request.nextUrl.pathname,
  })
  ;(request as any).logger = requestLogger
  return NextResponse.next()
}
```

## Recommendations

**Priority 1: Install Pino (Policy-Node, Helix, Kariusdx)**
- Replace 116 console.error calls with structured logging
- Add request ID correlation across API routes
- Enable log aggregation (stdout JSON → Datadog/CloudWatch)

**Priority 2: Add Error Context**
- Include operation name, user ID, resource ID in all error logs
- Use child loggers for request/user scope
- Redact sensitive fields (passwords, API keys, PII)

**Priority 3: Performance Monitoring**
- Log operation duration for slow operations (>100ms)
- Track database query times
- Monitor API call latency

**Priority 4: Integrate with Error Tracking**
- Forward error+ logs to Sentry via pino-sentry-transport
- Include log context in error tracking events
- Correlate errors across services using trace IDs
