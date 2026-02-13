---
title: "Error Context Wrapping: Preserving Stack Traces with Contextual Information"
category: "error-handling"
subcategory: "error-wrapping"
tags: ["error-handling", "error-wrapping", "stack-traces", "debugging", "context"]
stack: "js-nextjs"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Error Context Wrapping: Preserving Stack Traces with Contextual Information

Error context wrapping catches errors, adds contextual information (operation name, file path, data keys), and re-throws enriched errors while preserving original stack traces. Analyzed codebases show 33% adoption (policy-node: 80% of utility functions wrap errors with context), enabling production debugging by correlating errors with specific operations, files, and data inputs.

## Why Error Context Wrapping Matters

Generic error messages lack context. Error wrapping transforms "Network timeout" into "Failed to download S3 file from bucket 'data-bucket', key 'municipalities.csv': Network timeout".

**Generic Error (Bad):**

```typescript
// ❌ BAD: Generic error message (which S3 file failed?)
async function downloadS3File(s3Key: string, bucket: string) {
  const response = await s3Client.send(
    new GetObjectCommand({ Bucket: bucket, Key: s3Key })
  )
  return response.Body
  // If error occurs, stack trace shows:
  // Error: Network timeout
  //   at AWS.S3.getObject (...)
}
```

**Wrapped Error (Good):**

```typescript
// ✅ GOOD: Error wrapped with context (shows bucket, key, operation)
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
// Error message now includes:
// Error: Failed to download S3 file from bucket "data-bucket", key "municipalities.csv": Network timeout
```

Benefits: contextual debugging, data identification, stack trace preservation, production debugging without source code access.

## Policy-Node Pattern: String Concatenation Wrapping

Policy-node wraps errors with context using string concatenation, preserving original error message while adding operation/file/data context.

**S3 Download Error Wrapping:**

```typescript
// lib/s3-loader.ts
async function downloadS3File(s3Key: string, bucket: string) {
  try {
    const response = await s3Client.send(new GetObjectCommand({ Bucket: bucket, Key: s3Key }))
    return response.Body
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to download S3 file from bucket "${bucket}", key "${s3Key}": ${error.message}`)
    }
    throw error
  }
}
```

**CSV Parsing Error Wrapping:**

```typescript
async function parseStreamToCsv(stream: Readable) {
  try {
    return await parseStream(stream)
  } catch (error) {
    if (error instanceof Error) throw new Error(`CSV parsing failed: ${error.message}`)
    throw error
  }
}
```

**Adoption:** Policy-node: 80% of utility functions wrap errors. Helix: 0%, Kariusdx: 0%.

## Multi-Level Error Context Chaining

Error wrapping at multiple abstraction levels builds context chain from low-level (S3 download) through high-level (data loading pipeline).

```typescript
async function loadMunicipalitiesFromS3(s3Key: string) {
  try {
    const fileStream = await downloadS3File(s3Key, 'data-bucket')
    const csvData = await parseStreamToCsv(fileStream)
    return csvData
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load municipalities from S3 key "${s3Key}": ${error.message}`)
    }
    throw error
  }
}
```

Error message includes full context chain: "Failed to load municipalities from S3 key 'municipalities.csv': CSV parsing failed: Failed to download S3 file from bucket 'data-bucket', key 'municipalities.csv': Network timeout"

## Preserving Stack Traces

Error wrapping preserves original error stack trace by creating new Error with wrapped message but maintaining original error's stack trace location.

**Stack Trace Preservation:**

```typescript
async function fetchData() {
  try {
    const response = await fetch('/api/data')
    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      const wrappedError = new Error(`Data fetch failed: ${error.message}`)
      wrappedError.stack = error.stack  // Preserve original stack trace
      throw wrappedError
    }
    throw error
  }
}

// Stack trace still points to original error location:
// Error: Data fetch failed: Network timeout
//   at fetch (node:internal/fetch:123)  ← Original error location preserved
//   at fetchData (lib/data.ts:45)
```

**Automatic Stack Trace Preservation (Error Constructor):**

```typescript
// New Error inherits stack trace from throw location by default
try {
  await fetch('/api/data')
} catch (error) {
  if (error instanceof Error) {
    throw new Error(`Data fetch failed: ${error.message}`)
    // Stack trace automatically includes original error location
  }
  throw error
}
```

## Error Cause Property (ES2022)

Modern JavaScript Error constructor supports cause property (ES2022), preserving full original error object (not just message).

```typescript
async function downloadS3File(s3Key: string, bucket: string) {
  try {
    const response = await s3Client.send(new GetObjectCommand({ Bucket: bucket, Key: s3Key }))
    return response.Body
  } catch (error) {
    throw new Error(
      `Failed to download S3 file from bucket "${bucket}", key "${s3Key}"`,
      { cause: error }
    )
  }
}

catch (error) {
  console.error('Wrapped:', error.message)
  console.error('Original:', error.cause)
}
```

Benefits: preserves full error object, enables chaining, TypeScript-friendly, ES2022 standard.

## Custom Error Classes with Cause and Context

Custom error classes extend Error with cause property and context metadata for structured error handling.

```typescript
class S3Error extends Error {
  readonly cause: Error | undefined
  readonly context: Record<string, any>
  constructor(message: string, cause?: Error, context?: Record<string, any>) {
    super(message)
    this.name = 'S3Error'
    this.cause = cause
    this.context = context || {}
  }
}

try {
  await s3Client.send(command)
} catch (error) {
  throw new S3Error('Failed to download S3 file', error instanceof Error ? error : undefined, { bucket, s3Key, operation: 'download' })
}

catch (error) {
  if (error instanceof S3Error) {
    console.error('Operation:', error.context.operation, 'Root cause:', error.cause?.message)
  }
}
```

## Contextual Metadata in Error Objects

Error objects store metadata (user ID, request ID, operation name) as properties for structured logging.

```typescript
class ContextualError extends Error {
  readonly context: Record<string, any>
  readonly timestamp: string
  readonly operation: string
  constructor(message: string, operation: string, context?: Record<string, any>) {
    super(message)
    this.name = 'ContextualError'
    this.operation = operation
    this.context = context || {}
    this.timestamp = new Date().toISOString()
  }
}

try {
  await fetchMunicipality(slug)
} catch (error) {
  throw new ContextualError('Failed to fetch municipality', 'fetch-municipality', { slug, userId: session?.userId, requestId: crypto.randomUUID(), dataSource: 'sanity' })
}

catch (error) {
  if (error instanceof ContextualError) {
    logger.error({ err: error, operation: error.operation, timestamp: error.timestamp, ...error.context }, error.message)
  }
}
```

Log output: `{"level":"error","operation":"fetch-municipality","timestamp":"2026-02-11T10:30:00Z","slug":"oslo","userId":"user-123","requestId":"abc-def-456","dataSource":"sanity"}`

**Adoption:** Custom error classes with metadata: 33% (policy-node statusCode only). Full context objects: 0%.

## Basic Error Wrapping Patterns

**Pattern 1: Operation Name Prefix:**

```typescript
catch (error) {
  if (error instanceof Error) throw new Error(`CSV parsing failed: ${error.message}`)
  throw error
}
```

**Pattern 2: File Path Context:**

```typescript
catch (error) {
  if (error instanceof Error) throw new Error(`Failed to read file "${filePath}": ${error.message}`)
  throw error
}
```

**Pattern 3: Data Key Context:**

```typescript
catch (error) {
  if (error instanceof Error) throw new Error(`S3 download failed for bucket "${bucket}", key "${s3Key}": ${error.message}`)
  throw error
}
```

## Advanced Error Wrapping: Transformation and Chaining

**Error Transformation (External Library → Domain Errors):**

```typescript
catch (error) {
  if (error.code === 'NoSuchKey') throw new NotFoundError(`S3 file not found: ${s3Key}`)
  if (error.code === 'AccessDenied') throw new UnauthorizedError(`Access denied to S3 bucket: ${bucket}`)
  throw new S3Error(`S3 operation failed: ${error.message}`, error, { bucket, s3Key })
}
```

**Multi-Level Context Chain:**

```typescript
async function loadData() {
  try {
    const stream = await downloadS3File(s3Key, bucket)
    const csvData = await parseStreamToCsv(stream)
    return await validateData(csvData)
  } catch (error) {
    if (error instanceof Error) throw new Error(`Data loading pipeline failed for S3 key "${s3Key}": ${error.message}`)
    throw error
  }
}
```

Error chain: "Data loading pipeline failed for S3 key 'municipalities.csv': Data validation failed: CSV parsing failed: S3 download failed for bucket 'data-bucket', key 'municipalities.csv': Network timeout"

## When to Wrap Errors

**Wrap Errors When:**
- Crossing abstraction boundaries (utility function → API route)
- Data processing pipelines (download → parse → validate → transform)
- External API calls (add endpoint, operation name)
- File operations (add file path, operation type)
- Database queries (add table name, query type, record ID)

**Do NOT Wrap When:**
- Error already has sufficient context
- Wrapping adds no new information (redundant wrapping)
- Inside tight loops (performance impact)
- Error will be caught and transformed immediately

**Example: When to Wrap:**

```typescript
// ✅ WRAP: Utility function (add context for callers)
export async function downloadS3File(s3Key: string, bucket: string) {
  try {
    return await s3Client.send(command)
  } catch (error) {
    throw new Error(`S3 download failed for bucket "${bucket}", key "${s3Key}": ${error.message}`)
  }
}

// ✅ WRAP: API route (add request context)
export async function GET(request: NextRequest) {
  try {
    const data = await fetchData()
    return NextResponse.json(data)
  } catch (error) {
    throw new Error(`API request failed for ${request.url}: ${error.message}`)
  }
}

// ❌ DO NOT WRAP: Error already has context
catch (error) {
  if (error instanceof S3Error) {
    throw error  // Already wrapped, don't re-wrap
  }
}

// ❌ DO NOT WRAP: Adds no new information
catch (error) {
  throw new Error(`Error occurred: ${error.message}`)  // Redundant
}
```

## Error Wrapping vs Error Logging

Error wrapping adds context for callers, error logging records errors for developers. Use both together.

**Error Wrapping (For Callers):**

```typescript
async function downloadS3File(s3Key: string) {
  try {
    return await s3Client.send(command)
  } catch (error) {
    throw new Error(`S3 download failed for key "${s3Key}": ${error.message}`)
  }
}
```

**Error Logging (For Developers):**

```typescript
async function downloadS3File(s3Key: string) {
  try {
    return await s3Client.send(command)
  } catch (error) {
    logger.error({ err: error, context: 's3-download', s3Key, bucket: 'data-bucket' }, 'S3 download failed')
    throw error
  }
}
```

**Combined (Best Practice):**

```typescript
async function downloadS3File(s3Key: string, bucket: string) {
  try {
    return await s3Client.send(command)
  } catch (error) {
    logger.error({ err: error, context: 's3-download', s3Key, bucket }, 'S3 download failed')
    throw new Error(`S3 download failed for bucket "${bucket}", key "${s3Key}": ${error.message}`, { cause: error })
  }
}
```

## Type Guards for Wrapped Errors

Type guards (instanceof checks) enable distinct handling per error type, allowing specific recovery strategies, status codes, and user messages per error class.

**Type Guard Pattern:**

```typescript
try {
  await loadData()
} catch (error) {
  if (error instanceof S3Error) {
    // S3-specific error handling
    logger.error({ err: error, s3Key: error.context.s3Key }, 'S3 error')
    return { error: 'Failed to load data from storage' }
  }

  if (error instanceof ValidationError) {
    // Validation-specific error handling
    logger.warn({ err: error, fields: error.fields }, 'Validation error')
    return { error: 'Invalid data format', fields: error.fields }
  }

  if (error instanceof NetworkError) {
    // Network-specific error handling (retryable)
    logger.warn({ err: error }, 'Network error (retryable)')
    return { error: 'Network error, please retry' }
  }

  // Generic error fallback
  logger.error({ err: error }, 'Unexpected error')
  return { error: 'Internal server error' }
}
```

## Codebase Patterns

**Policy-Node (80% Error Wrapping in Utilities):**

```typescript
// S3 download error wrapping
catch (error) {
  if (error instanceof Error) {
    throw new Error(`Failed to download and cache S3 data: ${error.message}`)
  }
  throw error
}

// CSV parsing error wrapping
catch (error) {
  if (error instanceof Error) {
    throw new Error(`CSV parsing failed: ${error.message}`)
  }
  throw error
}

// Municipality API error wrapping
catch (error) {
  if (error instanceof MunicipalityError) {
    console.error(`Municipalities API ${error.statusCode}:`, error.message)
    return NextResponse.json({ error: error.message }, { status: error.statusCode })
  }
  throw error
}
```

**Helix (0% Error Wrapping):**
- 1 try/catch block (commented-out logging)
- No error wrapping observed

**Kariusdx (0% Error Wrapping):**
- 5 try/catch blocks (no logging)
- No error wrapping observed

**Adoption Summary:**
- Error wrapping with context: 33% (policy-node only)
- Custom error classes with cause: 0%
- Error metadata objects: 0% (policy-node uses string concatenation)
- Multi-level context chaining: 33% (policy-node only)

## Error Wrapping Anti-Patterns

**1. Wrapping Without Adding Context:**

```typescript
// ❌ BAD: No new information
catch (error) {
  throw new Error(`Error: ${error.message}`)
}

// ✅ GOOD: Adds operation/data context
catch (error) {
  throw new Error(`S3 download failed for key "${s3Key}": ${error.message}`)
}
```

**2. Losing Original Error:**

```typescript
// ❌ BAD: Loses original stack trace
catch (error) {
  throw new Error('S3 download failed')
}

// ✅ GOOD: Preserves original error
catch (error) {
  throw new Error(`S3 download failed: ${error.message}`, { cause: error })
}
```

## Over-Wrapping and Type Safety Anti-Patterns

**3. Over-Wrapping (Redundant Context):**

```typescript
// ❌ BAD: Same context at every level
async function downloadFile() {
  try {
    await s3Client.send(command)
  } catch (error) {
    throw new Error(`Download failed: ${error.message}`)
  }
}
async function loadData() {
  try {
    await downloadFile()
  } catch (error) {
    throw new Error(`Download failed: ${error.message}`)  // Redundant
  }
}

// ✅ GOOD: Different context at each level
async function downloadFile(s3Key) {
  try {
    await s3Client.send(command)
  } catch (error) {
    throw new Error(`S3 download failed for key "${s3Key}": ${error.message}`)
  }
}
async function loadData() {
  try {
    await downloadFile('municipalities.csv')
  } catch (error) {
    throw new Error(`Data loading pipeline failed: ${error.message}`)
  }
}
```

**4. Wrapping Non-Error Objects:**

```typescript
// ❌ BAD: No instanceof check
catch (error) {
  throw new Error(`Failed: ${error.message}`)  // TypeError if error is string
}

// ✅ GOOD: Check instanceof before accessing .message
catch (error) {
  if (error instanceof Error) throw new Error(`Failed: ${error.message}`)
  throw error
}
```

## Recommendations

**Priority 1: Extract Error Classes to Shared Module (Policy-Node)**
- Create lib/errors.ts with S3Error, ValidationError, ApiError
- Add cause property to preserve original errors
- Add context property for metadata (s3Key, bucket, userId, etc.)

**Priority 2: Add Error Wrapping to Utilities (Helix, Kariusdx)**
- Wrap errors in all utility functions with operation context
- Add file paths, S3 keys, database IDs to error messages
- Preserve original error stack traces with cause property

**Priority 3: Standardize Error Wrapping Pattern (All Repos)**
- Use Error constructor with cause property (ES2022)
- Always check instanceof Error before wrapping
- Add context at each abstraction boundary (utility → service → API route)

**Priority 4: Integrate with Structured Logging (All Repos)**
- Log wrapped errors with full context (operation, data keys, user ID)
- Use logger.error({ err, ...context }) for structured logs
- Send wrapped errors to error tracking service (Sentry)
