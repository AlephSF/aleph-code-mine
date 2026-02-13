---
title: "Custom Error Classes with HTTP Status Codes"
category: "error-handling"
subcategory: "error-types"
tags: ["custom-errors", "http-status", "type-safety", "api-errors", "typescript"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

## Custom Error Classes with HTTP Status Codes

Custom error classes extending the built-in Error class provide type-safe error handling with domain-specific properties like HTTP status codes. Next.js API routes benefit from custom errors that store status codes (400, 404, 500) as readonly properties, enabling type guards to distinguish between error types and return appropriate HTTP responses. Policy-node implements this pattern across 3+ API routes with MunicipalityError, MunicipalitySearchError, and PhraseError classes.

## Why Custom Error Classes Over Generic Errors

Generic Error objects lack domain context and HTTP status codes. Custom error classes store status codes as properties, making error handling type-safe without string comparisons. Source confidence: 33% (policy-node only).

#### Generic Error Problems

```typescript
// BAD: Generic error requires string parsing
try {
  const data = await fetchData(id)
  if (!data) {
    throw new Error('Not found')  // What status code?
  }
} catch (error) {
  if (error.message.includes('Not found')) {  // String matching is fragile
    return NextResponse.json({ error: error.message }, { status: 404 })
  }
  return NextResponse.json({ error: 'Server error' }, { status: 500 })
}

// GOOD: Custom error with status code property
try {
  const data = await fetchData(id)
  if (!data) {
    throw new MunicipalityError('Municipality not found', 404)
  }
} catch (error) {
  if (error instanceof MunicipalityError) {  // Type-safe check
    return NextResponse.json(
      { error: error.message },
      { status: error.statusCode }  // Status code from property
    )
  }
  return NextResponse.json({ error: 'Server error' }, { status: 500 })
}
```

Custom errors enable instanceof type guards and direct status code access without brittle string matching.

## Custom Error Class Implementation Pattern

Policy-node's custom error classes follow consistent pattern: extend Error, store readonly statusCode property, set error name for debugging, and accept message + statusCode constructor parameters. Readonly statusCode prevents accidental mutation. Setting this.name enables stack traces to display custom error name instead of generic "Error".

#### Standard Custom Error Template

```typescript
// errors/MunicipalityError.ts
class MunicipalityError extends Error {
  readonly statusCode: number

  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalityError'
    this.statusCode = statusCode

    // Maintains proper stack trace (V8 engine only)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, MunicipalityError)
    }
  }
}

export { MunicipalityError }
```

Constructor accepts message (required) and statusCode (defaults to 500). Readonly statusCode enforces immutability. Error.captureStackTrace preserves stack trace pointing to throw site rather than constructor. this.name = 'MunicipalityError' ensures error.name property reflects custom class name in logs and debuggers.

## Using Custom Errors in API Routes

API routes throw custom errors with specific status codes. Catch blocks use instanceof type guards. Custom errors return error.statusCode, generic errors default to 500.

#### API Route Error Handling Pattern

```typescript
// app/api/municipalities/[slug]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { MunicipalityError } from '@/errors/MunicipalityError'

function validateSlug(slug: string): string {
  if (!/^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$/.test(slug)) {
    throw new MunicipalityError('Invalid slug format', 400)
  }
  return slug
}

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
): Promise<NextResponse> {
  try {
    const validSlug = validateSlug(params.slug)
    const municipality = await getMunicipalityBySlug(validSlug)

    if (!municipality) {
      throw new MunicipalityError('Municipality not found', 404)
    }

    return NextResponse.json({ municipality })
  } catch (error) {
    if (error instanceof MunicipalityError) {
      return NextResponse.json({ error: error.message }, { status: error.statusCode })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

validateSlug throws 400 for invalid format. Not-found check throws 404. Type guard enables specific error handling. Generic errors fall through to 500.

## Domain-Specific Error Classes

Create separate error classes per domain: MunicipalityError, PhraseError, MetricError. Domain-specific errors improve logs and enable domain-specific handling.

#### Multiple Error Classes

```typescript
// errors/MunicipalityError.ts
export class MunicipalityError extends Error {
  readonly statusCode: number
  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalityError'
    this.statusCode = statusCode
  }
}

// errors/PhraseError.ts
export class PhraseError extends Error {
  readonly statusCode: number
  readonly locale?: string  // Domain-specific property

  constructor(message: string, statusCode: number = 500, locale?: string) {
    super(message)
    this.name = 'PhraseError'
    this.statusCode = statusCode
    this.locale = locale
  }
}

// Usage in API route
try {
  const phrases = await getPhrases(locale)
  if (phrases.length === 0) {
    throw new PhraseError('No phrases found', 404, locale)
  }
} catch (error) {
  if (error instanceof PhraseError) {
    console.error(`Phrase error [${error.locale}]:`, error.message)
    return NextResponse.json(
      { error: error.message, locale: error.locale },
      { status: error.statusCode }
    )
  }
}
```

PhraseError stores locale property for debugging. Error logs include locale context. Domain-specific properties enable richer error responses. Tests can assert on domain properties: `expect(error.locale).toBe('fr-CA')`.

## Extracting Errors to Shared Module

Policy-node duplicates error classes across 3 files. Best practice: extract to shared `@/errors` directory, export from index file. DRY principle prevents inconsistent definitions.

#### Shared Errors Module Structure

```
src/errors/
  index.ts
  MunicipalityError.ts
  PhraseError.ts
  BaseApiError.ts
```

```typescript
// errors/BaseApiError.ts
export abstract class BaseApiError extends Error {
  readonly statusCode: number
  readonly context?: Record<string, unknown>

  constructor(message: string, statusCode: number, context?: Record<string, unknown>) {
    super(message)
    this.statusCode = statusCode
    this.context = context

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor)
    }
  }
}

// errors/MunicipalityError.ts
import { BaseApiError } from './BaseApiError'

export class MunicipalityError extends BaseApiError {
  constructor(message: string, statusCode: number = 500, context?: Record<string, unknown>) {
    super(message, statusCode, context)
    this.name = 'MunicipalityError'
  }
}

// errors/index.ts
export { BaseApiError } from './BaseApiError'
export { MunicipalityError } from './MunicipalityError'
export { PhraseError } from './PhraseError'

// Usage
import { MunicipalityError, PhraseError } from '@/errors'
```

BaseApiError defines shared properties. Subclasses inherit base behavior. Single import from '@/errors' imports all types.

## Custom Errors with Additional Metadata

Extend custom errors with metadata: timestamp, requestId, operation. Metadata aids debugging and integrates with error tracking services. Avoid sensitive data.

#### Errors with Metadata

```typescript
class ApiError extends Error {
  readonly statusCode: number
  readonly timestamp: string
  readonly requestId?: string
  readonly operation?: string

  constructor(
    message: string,
    statusCode: number,
    options?: {
      requestId?: string
      operation?: string
    }
  ) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.timestamp = new Date().toISOString()
    this.requestId = options?.requestId
    this.operation = options?.operation
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      timestamp: this.timestamp,
      requestId: this.requestId,
      operation: this.operation,
    }
  }
}

// Usage
throw new ApiError('Database connection failed', 500, {
  requestId: req.headers.get('x-request-id'),
  operation: 'fetchMunicipalities',
})

// Catch block
if (error instanceof ApiError) {
  console.error(error.toJSON())
  Sentry.captureException(error, { extra: { requestId: error.requestId } })
}
```

toJSON method serializes error for logging. requestId correlates errors across distributed systems. operation identifies failing code path. Structured logs enable log aggregation and querying.

## Best Practices

**Extract to shared module:** Define errors once in `@/errors`, reuse across application. Prevents inconsistent error definitions.

**Use readonly properties:** Prevent accidental mutation of error state. Errors should be immutable.

**Set error name:** Assign `this.name = 'CustomErrorName'` for accurate stack traces and logs.

**Default status codes:** Default to 500 (internal server error) when status code is not provided. Prevents accidentally returning 200 OK for errors.

**Type guards in catch blocks:** Use `error instanceof CustomError` to distinguish error types. Avoid string matching on error messages.

**Don't expose internal details:** Error messages returned to clients should not include database queries, file paths, or stack traces. Log details server-side only.

Policy-node's 3 custom error classes should be consolidated into shared errors module. Helix and kariusdx currently lack custom errors (0% adoption) and should implement this pattern for type-safe error handling.
