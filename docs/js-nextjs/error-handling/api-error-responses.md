---
title: "Next.js API Route Error Responses with NextResponse and Custom Errors"
category: "error-handling"
subcategory: "api-routes"
tags: ["api-routes", "error-handling", "nextresponse", "http-status", "error-classes"]
stack: "js-nextjs"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Next.js API Route Error Responses with NextResponse and Custom Errors

Next.js API routes return errors via NextResponse.json() with HTTP status codes, error messages, and optional error metadata. Analyzed codebases show 33% adoption of custom error classes with status codes (policy-node only: MunicipalityError, PhraseError, MunicipalitySearchError), 67% notFound() usage for 404 responses, and inconsistent error response formats across 10+ API routes.

## NextResponse Error Patterns

Next.js App Router API routes use NextResponse.json() to return error responses with status codes, replacing Pages Router's res.status().json() pattern.

**Basic Error Response:**

```typescript
// app/api/municipalities/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const municipalities = await fetchMunicipalities()
    return NextResponse.json(municipalities)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch municipalities' },
      { status: 500 }
    )
  }
}
```

**Error Response with Details:**

```typescript
// app/api/municipalities/[slug]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  try {
    const municipality = await fetchMunicipality(params.slug)

    if (!municipality) {
      return NextResponse.json(
        {
          error: 'Municipality not found',
          code: 'MUNICIPALITY_NOT_FOUND',
          slug: params.slug,
        },
        { status: 404 }
      )
    }

    return NextResponse.json(municipality)
  } catch (error) {
    return NextResponse.json(
      {
        error: 'Internal server error',
        code: 'INTERNAL_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    )
  }
}
```

**Observed Patterns:**
- Policy-node: 10+ API routes with structured error responses
- Helix: Minimal API error handling (reliance on automatic Next.js error handling)
- Kariusdx: Pages Router (uses res.status().json() instead of NextResponse)

## Custom Error Classes with HTTP Status Codes

Custom error classes extend Error with statusCode property, enabling type-safe error handling and automatic status code mapping in API routes.

**Policy-Node Pattern (100% of API Routes):**

```typescript
// lib/errors.ts (or inline in API route - duplication observed)
class MunicipalityError extends Error {
  readonly statusCode: number

  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalityError'
    this.statusCode = statusCode
  }
}

class MunicipalitySearchError extends Error {
  readonly statusCode: number

  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalitySearchError'
    this.statusCode = statusCode
  }
}
```

**Usage in API Route:**

```typescript
// app/api/municipalities/[slug]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  try {
    // Validation errors (400 Bad Request)
    if (!/^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$/.test(params.slug)) {
      throw new MunicipalityError('Invalid slug format', 400)
    }

    const municipality = await fetchMunicipality(params.slug)

    // Not found errors (404 Not Found)
    if (!municipality) {
      throw new MunicipalityError('Municipality not found', 404)
    }

    return NextResponse.json(municipality)
  } catch (error) {
    if (error instanceof MunicipalityError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      )
    }

    // Generic errors (500 Internal Server Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**Benefits:**
- Type-safe error handling (TypeScript knows error.statusCode exists)
- Automatic status code mapping (no manual if/else for status codes)
- Consistent error response format across API routes
- Error type identification via instanceof checks

**Adoption:**
- Policy-node: 100% of API routes use custom error classes (3 classes: MunicipalityError, PhraseError, MunicipalitySearchError)
- Helix: 0% (no API routes observed)
- Kariusdx: 0% (Pages Router, no custom error classes)

**Gap:** Error classes duplicated across 3+ API route files (should be extracted to shared @/lib/errors module)

## Type Guards for Error Handling

Type guards (instanceof checks) enable distinct error handling per error type, allowing specific error messages, status codes, and logging per error class.

**Policy-Node Pattern (100% of API Routes with Custom Errors):**

```typescript
// app/api/municipalities/search/route.ts
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    if (!body.query) {
      throw new MunicipalitySearchError('Search query is required', 400)
    }

    const results = await searchMunicipalities(body.query)
    return NextResponse.json(results)
  } catch (error) {
    // Type guard for MunicipalitySearchError
    if (error instanceof MunicipalitySearchError) {
      console.error(`Municipality search error ${error.statusCode}:`, error.message)
      return NextResponse.json(
        {
          error: error.message,
          code: 'SEARCH_ERROR',
        },
        { status: error.statusCode }
      )
    }

    // Type guard for MunicipalityError
    if (error instanceof MunicipalityError) {
      console.error(`Municipality error ${error.statusCode}:`, error.message)
      return NextResponse.json(
        {
          error: error.message,
          code: 'MUNICIPALITY_ERROR',
        },
        { status: error.statusCode }
      )
    }

    // Generic error fallback
    console.error('Unexpected error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**Multi-Level Error Handling:**

```typescript
// Specific error handling per error type
try {
  const municipality = await fetchMunicipality(params.slug)
} catch (error) {
  if (error instanceof ValidationError) {
    return NextResponse.json({ error: error.message }, { status: 400 })
  }

  if (error instanceof NotFoundError) {
    return NextResponse.json({ error: error.message }, { status: 404 })
  }

  if (error instanceof UnauthorizedError) {
    return NextResponse.json({ error: error.message }, { status: 401 })
  }

  if (error instanceof RateLimitError) {
    return NextResponse.json(
      { error: error.message, retryAfter: error.retryAfter },
      { status: 429 }
    )
  }

  // Fallback for unknown errors
  return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}
```

## Validation Errors with Fail-Fast Principle

Validation errors throw immediately with 400 Bad Request status, preventing invalid data from reaching business logic or database queries.

**Policy-Node Pattern (100% of Validated API Routes):**

```typescript
// app/api/municipalities/[slug]/route.ts
function validateSlug(slug: string): string {
  if (!slug) {
    throw new MunicipalityError('Slug is required', 400)
  }

  if (!/^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$/.test(slug)) {
    throw new MunicipalityError(
      'Slug must contain only letters, numbers, and hyphens',
      400
    )
  }

  if (slug.length > 100) {
    throw new MunicipalityError('Slug must be 100 characters or less', 400)
  }

  return slug
}

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  try {
    const validatedSlug = validateSlug(params.slug)  // Throws on invalid input
    const municipality = await fetchMunicipality(validatedSlug)

    if (!municipality) {
      throw new MunicipalityError('Municipality not found', 404)
    }

    return NextResponse.json(municipality)
  } catch (error) {
    if (error instanceof MunicipalityError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      )
    }

    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

**Request Body Validation:**

```typescript
// app/api/municipalities/route.ts
import { z } from 'zod'

const municipalitySchema = z.object({
  name: z.string().min(1).max(100),
  population: z.number().int().positive(),
  slug: z.string().regex(/^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$/),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate with Zod (throws ZodError on invalid data)
    const validatedData = municipalitySchema.parse(body)

    const municipality = await createMunicipality(validatedData)
    return NextResponse.json(municipality, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          errors: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
          })),
        },
        { status: 400 }
      )
    }

    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

**Adoption:**
- Policy-node: 100% of API routes with user input perform validation
- Helix: No API routes observed (no validation patterns)
- Kariusdx: Minimal validation (Pages Router getStaticProps validates at build time)

## Error Response Format Standardization

Consistent error response format (error field, optional code field, optional details field) enables predictable client-side error handling and debugging.

**Recommended Format:**

```typescript
// Standard error response structure
interface ErrorResponse {
  error: string              // User-facing error message
  code?: string             // Machine-readable error code (e.g., "VALIDATION_ERROR")
  details?: Record<string, any>  // Additional error context (field errors, retry info)
  requestId?: string        // Request ID for debugging
}

// Example responses:
// 400 Bad Request
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "fields": {
      "slug": "Slug must contain only letters, numbers, and hyphens",
      "population": "Population must be a positive integer"
    }
  }
}

// 404 Not Found
{
  "error": "Municipality not found",
  "code": "NOT_FOUND",
  "details": {
    "slug": "oslo-2",
    "availableSlugs": ["oslo", "bergen", "trondheim"]
  }
}

// 500 Internal Server Error
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "requestId": "abc-123-def-456"
}
```

**Implementation:**

```typescript
// lib/api-error.ts
export function createErrorResponse(
  error: string,
  code?: string,
  details?: Record<string, any>,
  requestId?: string
): ErrorResponse {
  return {
    error,
    ...(code && { code }),
    ...(details && { details }),
    ...(requestId && { requestId }),
  }
}

// Usage in API route:
return NextResponse.json(
  createErrorResponse(
    'Municipality not found',
    'NOT_FOUND',
    { slug: params.slug },
    requestId
  ),
  { status: 404 }
)
```

**Gap Analysis:**
- Policy-node: Inconsistent format (some responses have code, some don't)
- Helix: No API routes (no format to analyze)
- Kariusdx: Pages Router (different error format)

## Error Context Wrapping

Error context wrapping preserves original error stack trace while adding contextual information (operation name, file path, data keys), improving production debugging.

**Policy-Node Pattern (80% of Utilities):**

```typescript
// lib/s3-loader.ts
async function downloadS3File(s3Key: string, bucket: string) {
  try {
    const response = await s3Client.send(
      new GetObjectCommand({ Bucket: bucket, Key: s3Key })
    )
    return response.Body
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(
        `Failed to download S3 file from bucket "${bucket}", key "${s3Key}": ${error.message}`
      )
    }
    throw error
  }
}
```

**Nested Error Context:**

```typescript
// lib/csv-parser.ts
async function parseCsvFromS3(s3Key: string) {
  try {
    const fileStream = await downloadS3File(s3Key, 'data-bucket')
    const csvData = await parseStreamToCsv(fileStream)
    return csvData
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`CSV parsing failed for S3 key "${s3Key}": ${error.message}`)
    }
    throw error
  }
}

// Error stack preserves full context:
// Error: CSV parsing failed for S3 key "municipalities.csv": Failed to download S3 file from bucket "data-bucket", key "municipalities.csv": Network timeout
```

**Custom Error Wrapping:**

```typescript
// lib/errors.ts
class WrappedError extends Error {
  readonly cause: Error
  readonly context: Record<string, any>

  constructor(message: string, cause: Error, context?: Record<string, any>) {
    super(message)
    this.name = 'WrappedError'
    this.cause = cause
    this.context = context || {}
  }
}

// Usage:
try {
  await downloadS3File(s3Key, bucket)
} catch (error) {
  throw new WrappedError(
    'Failed to download S3 file',
    error as Error,
    { s3Key, bucket, operation: 'download' }
  )
}
```

**Adoption:**
- Policy-node: 80% of utility functions wrap errors with context
- Helix: 0% (minimal error handling, no wrapping)
- Kariusdx: 0% (minimal error handling, no wrapping)

## HTTP Status Code Best Practices

HTTP status codes communicate error type to clients, enabling appropriate client-side handling (retry on 5xx, show error message on 4xx, redirect on 401).

**Common Status Codes in API Routes:**

```typescript
// 400 Bad Request - Client sent invalid data
if (!isValidSlug(params.slug)) {
  return NextResponse.json({ error: 'Invalid slug format' }, { status: 400 })
}

// 401 Unauthorized - Missing or invalid authentication
const session = await getSession(request)
if (!session) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
}

// 403 Forbidden - Authenticated but insufficient permissions
if (session.role !== 'admin') {
  return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
}

// 404 Not Found - Resource does not exist
const municipality = await fetchMunicipality(params.slug)
if (!municipality) {
  return NextResponse.json({ error: 'Municipality not found' }, { status: 404 })
}

// 409 Conflict - Resource already exists
const existing = await findMunicipalityBySlug(body.slug)
if (existing) {
  return NextResponse.json(
    { error: 'Municipality with this slug already exists' },
    { status: 409 }
  )
}

// 422 Unprocessable Entity - Valid syntax but semantic errors
const validation = await validateMunicipality(body)
if (!validation.valid) {
  return NextResponse.json(
    { error: 'Validation failed', errors: validation.errors },
    { status: 422 }
  )
}

// 429 Too Many Requests - Rate limit exceeded
if (isRateLimited(request)) {
  return NextResponse.json(
    { error: 'Rate limit exceeded', retryAfter: 60 },
    { status: 429, headers: { 'Retry-After': '60' } }
  )
}

// 500 Internal Server Error - Unexpected server error
catch (error) {
  console.error('Unexpected error:', error)
  return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}

// 503 Service Unavailable - Temporary service outage
if (!isDatabaseConnected()) {
  return NextResponse.json(
    { error: 'Service unavailable', retryAfter: 30 },
    { status: 503 }
  )
}
```

**Status Code Selection:**
- 4xx: Client error (client can fix by changing request)
- 5xx: Server error (client cannot fix, retry may succeed)

## Logging API Errors

API route errors should log error details (stack trace, request context, user ID) for debugging while returning sanitized error messages to clients (no stack traces, no sensitive data).

**Recommended Pattern:**

```typescript
export async function GET(request: NextRequest) {
  try {
    const municipalities = await fetchMunicipalities()
    return NextResponse.json(municipalities)
  } catch (error) {
    // Log full error details (server-side only)
    console.error('API error:', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      path: request.nextUrl.pathname,
      method: request.method,
      timestamp: new Date().toISOString(),
    })

    // Return sanitized error to client (no stack trace)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**With Structured Logging:**

```typescript
import { logger } from '@/lib/logger'

export async function GET(request: NextRequest) {
  try {
    const municipalities = await fetchMunicipalities()
    return NextResponse.json(municipalities)
  } catch (error) {
    logger.error({
      err: error,
      context: 'municipalities-api',
      path: request.nextUrl.pathname,
      method: request.method,
    }, 'API request failed')

    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

## Codebase Patterns

**Policy-Node (100% Custom Error Classes):**
```typescript
// Repeated in 3+ API routes (duplication)
class MunicipalityError extends Error {
  readonly statusCode: number
  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.name = 'MunicipalityError'
    this.statusCode = statusCode
  }
}

catch (error) {
  if (error instanceof MunicipalityError) {
    return NextResponse.json({ error: error.message }, { status: error.statusCode })
  }
  return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}
```

**Helix (No API Routes Observed):**
- No App Router API routes
- Relies on external APIs (Sanity, Greenhouse)

**Kariusdx (Pages Router):**
```typescript
// pages/api/preview.ts (Pages Router pattern)
export default async function handler(req, res) {
  try {
    // ...
    res.json({ success: true })
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' })
  }
}
```

**Adoption Summary:**
- Custom error classes: 33% (policy-node only)
- Type guards (instanceof): 33% (policy-node only)
- Validation with fail-fast: 33% (policy-node only)
- Error context wrapping: 33% (policy-node only)
- Structured error responses: Inconsistent (no standard format)

## Anti-Patterns

**1. Returning Generic Error Messages:**
```typescript
// ❌ BAD: Generic error message (no context for debugging)
catch (error) {
  return NextResponse.json({ error: 'Error' }, { status: 500 })
}

// ✅ GOOD: Specific error message
catch (error) {
  return NextResponse.json(
    { error: 'Failed to fetch municipalities', code: 'FETCH_ERROR' },
    { status: 500 }
  )
}
```

**2. Exposing Stack Traces to Clients:**
```typescript
// ❌ BAD: Exposes internal error details to clients
catch (error) {
  return NextResponse.json({ error: error.stack }, { status: 500 })
}
```

**3. Wrong Status Codes:**
```typescript
// ❌ BAD: Returns 500 for validation errors (should be 400)
if (!isValidSlug(params.slug)) {
  return NextResponse.json({ error: 'Invalid slug' }, { status: 500 })
}

// ✅ GOOD: Returns 400 for client errors
if (!isValidSlug(params.slug)) {
  return NextResponse.json({ error: 'Invalid slug' }, { status: 400 })
}
```

**4. Duplicating Error Classes:**
```typescript
// ❌ BAD: MunicipalityError defined in 3+ files
// app/api/municipalities/route.ts
class MunicipalityError extends Error { /* ... */ }

// app/api/municipalities/[slug]/route.ts
class MunicipalityError extends Error { /* ... */ }

// ✅ GOOD: Extract to shared module
// lib/errors.ts
export class MunicipalityError extends Error { /* ... */ }
```

## Recommendations

**Priority 1: Extract Custom Error Classes (Policy-Node)**
- Create lib/errors.ts with MunicipalityError, PhraseError, MunicipalitySearchError
- Import from shared module in all API routes
- Add additional error classes (ValidationError, UnauthorizedError, NotFoundError)

**Priority 2: Standardize Error Response Format (All Repos)**
- Define ErrorResponse interface
- Create createErrorResponse() helper function
- Ensure all API routes return consistent format

**Priority 3: Add Validation to API Routes (Helix, Kariusdx)**
- Install Zod or Yup for request validation
- Validate all user input with fail-fast principle
- Return 400 Bad Request with field-level errors

**Priority 4: Integrate Error Logging (All Repos)**
- Log all 5xx errors with full context (stack trace, request path, user ID)
- Use structured logging (Pino) for searchable logs
- Integrate error tracking service (Sentry) for alerting
