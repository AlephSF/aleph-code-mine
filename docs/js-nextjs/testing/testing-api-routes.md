---
title: "Testing API Routes and Route Handlers in Next.js"
category: "testing"
subcategory: "api-testing"
tags: ["api-routes", "route-handlers", "integration-testing", "msw", "next-request"]
stack: "js-nextjs"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Testing API Routes and Route Handlers in Next.js

API routes (Pages Router) and route handlers (App Router) execute server-side request/response logic including data transformations, external API calls, and database operations. Integration tests verify HTTP method handling, request parsing, response formatting, error handling, and status codes. Mock external dependencies (databases, third-party APIs) to ensure tests run fast and deterministically.

### Route Handlers vs API Routes

Next.js App Router route handlers use Web Standards (Request, Response) while Pages Router API routes use Node.js APIs (NextApiRequest, NextApiResponse). Route handlers export named functions (GET, POST, PUT, DELETE) while API routes export single default handler with method switching. Policy-node has 10+ API routes handling metrics and phrases transformations - all untested. Source confidence: 0% (no API testing infrastructure exists in analyzed codebases).

### Testing Route Handlers (App Router)

Route handler functions accept NextRequest and return Response objects. Test by importing handler function, creating mock Request objects, calling handler, and asserting Response properties (status, headers, body). No HTTP server required - test handlers as pure functions.

#### Testing GET Route Handler

```typescript
// app/api/phrases/[locale]/route.test.ts
import { describe, it, expect, vi } from 'vitest'
import { GET } from './route'
import { NextRequest } from 'next/server'

// Mock data source
vi.mock('@/lib/csvLoader', () => ({
  loadPhrases: vi.fn().mockResolvedValue([
    { id: '1', text: 'Hello', locale: 'en-US' },
    { id: '2', text: 'World', locale: 'en-US' },
  ]),
}))

describe('GET /api/phrases/[locale]', () => {
  it('returns phrases for valid locale', async () => {
    const request = new NextRequest('http://localhost:3000/api/phrases/en-US')
    const response = await GET(request, { params: { locale: 'en-US' } })

    expect(response.status).toBe(200)

    const data = await response.json()
    expect(data).toEqual({
      phrases: [
        { id: '1', text: 'Hello', locale: 'en-US' },
        { id: '2', text: 'World', locale: 'en-US' },
      ],
      locale: 'en-US',
      count: 2,
    })
  })

  it('returns 404 for invalid locale', async () => {
    const { loadPhrases } = await import('@/lib/csvLoader')
    vi.mocked(loadPhrases).mockResolvedValueOnce([])

    const request = new NextRequest('http://localhost:3000/api/phrases/invalid')
    const response = await GET(request, { params: { locale: 'invalid' } })

    expect(response.status).toBe(404)

    const data = await response.json()
    expect(data).toEqual({ error: 'No phrases found for locale: invalid' })
  })
})
```

Create NextRequest with full URL (required by Web Standards). Pass route parameters via `params` object. Await response and parse JSON with `response.json()`. Test both success case (200) and error case (404). Mock external data sources (CSV loader, database) for predictable test data.

### Testing POST Route Handler with Request Body

POST handlers parse request body (JSON, FormData, text) and perform mutations. Test by creating NextRequest with body, calling handler, and verifying response data and side effects (database writes, external API calls).

#### Testing POST with JSON Body

```typescript
// app/api/metrics/route.test.ts
import { describe, it, expect, vi } from 'vitest'
import { POST } from './route'
import { NextRequest } from 'next/server'

vi.mock('@/lib/database', () => ({
  saveMetric: vi.fn().mockResolvedValue({ id: '123', status: 'saved' }),
}))

describe('POST /api/metrics', () => {
  it('saves metric with valid data', async () => {
    const body = JSON.stringify({
      name: 'page_views',
      value: 1234,
      timestamp: '2026-02-11T10:00:00Z',
    })

    const request = new NextRequest('http://localhost:3000/api/metrics', {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)

    expect(response.status).toBe(201)

    const data = await response.json()
    expect(data).toMatchObject({
      id: '123',
      status: 'saved',
    })

    const { saveMetric } = await import('@/lib/database')
    expect(saveMetric).toHaveBeenCalledWith({
      name: 'page_views',
      value: 1234,
      timestamp: '2026-02-11T10:00:00Z',
    })
  })

  it('returns 400 for invalid JSON', async () => {
    const request = new NextRequest('http://localhost:3000/api/metrics', {
      method: 'POST',
      body: 'invalid json',
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)

    expect(response.status).toBe(400)

    const data = await response.json()
    expect(data.error).toMatch(/invalid json/i)
  })
})
```

Stringify JSON body and set Content-Type header. Verify handler parses body correctly and passes data to dependencies. Assert both response status/body and mock function calls. Test validation errors (400), missing fields, and malformed JSON.

### Testing API Routes (Pages Router)

Pages Router API routes use Node.js request/response objects. Test by creating mock req/res objects, calling handler, and asserting response properties. Use helper library like `node-mocks-http` to create mock objects easily.

#### Testing Pages Router API Route

```typescript
// pages/api/health.test.ts
import { describe, it, expect } from 'vitest'
import { createMocks } from 'node-mocks-http'
import handler from './health'

describe('GET /api/health', () => {
  it('returns 200 with health status', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    })

    await handler(req, res)

    expect(res._getStatusCode()).toBe(200)
    expect(res._getJSONData()).toEqual({
      status: 'ok',
      timestamp: expect.any(String),
    })
  })

  it('returns 405 for POST method', async () => {
    const { req, res } = createMocks({
      method: 'POST',
    })

    await handler(req, res)

    expect(res._getStatusCode()).toBe(405)
    expect(res._getJSONData()).toEqual({
      error: 'Method not allowed',
    })
  })
})
```

Install `node-mocks-http`: `npm install -D node-mocks-http @types/node-mocks-http`. `createMocks` generates req/res objects with method, headers, body, and query parameters. Access response with `_getStatusCode()` and `_getJSONData()`. Test all supported HTTP methods.

### Testing Data Transformations in API Routes

Policy-node's API routes perform complex data transformations (metrics display config, phrase localization, municipality data). Test transformations with diverse input data covering edge cases, boundary conditions, and error states.

#### Testing Transformation Logic

```typescript
// app/api/phrases/utils/transformData.test.ts
import { describe, it, expect } from 'vitest'
import { transformLocationData } from './transformLocationData'

describe('transformLocationData', () => {
  it('transforms raw CSV data to location objects', () => {
    const rawData = [
      { muni_id: '1', name: 'Toronto', population: '2930000', province: 'ON' },
      { muni_id: '2', name: 'Montreal', population: '1780000', province: 'QC' },
    ]

    const result = transformLocationData(rawData)

    expect(result).toEqual([
      { id: '1', name: 'Toronto', population: 2930000, province: 'ON' },
      { id: '2', name: 'Montreal', population: 1780000, province: 'QC' },
    ])
  })

  it('handles missing population gracefully', () => {
    const rawData = [{ muni_id: '1', name: 'Test', population: '', province: 'ON' }]

    const result = transformLocationData(rawData)

    expect(result[0].population).toBe(0)  // Default value
  })

  it('filters out invalid records', () => {
    const rawData = [
      { muni_id: '', name: 'Invalid', population: '1000', province: 'ON' },
      { muni_id: '1', name: 'Valid', population: '2000', province: 'QC' },
    ]

    const result = transformLocationData(rawData)

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('1')
  })
})
```

Test transformation utilities separately from API routes for faster tests. Verify correct data type conversions (string to number), default values for missing fields, and filtering of invalid records. These tests prevent data corruption in production API responses.

### Mocking External APIs with MSW

Route handlers often call third-party APIs (Sanity, GraphQL, S3). Mock Service Worker intercepts HTTP requests during tests, returning predictable responses without real network calls. MSW works identically in Node.js tests and browser environments.

#### MSW Setup for API Testing

```typescript
// vitest.setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('https://api.sanity.io/v2023-08-01/data/query/*', () => {
    return HttpResponse.json({
      result: [
        { _id: '1', title: 'Test Page', slug: 'test' },
      ],
    })
  }),

  http.get('https://api.external.com/data', () => {
    return HttpResponse.json({ status: 'ok' })
  }),
]

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

MSW intercepts fetch/axios requests automatically. `onUnhandledRequest: 'error'` fails tests for unmocked requests, ensuring all external dependencies are mocked. `resetHandlers()` between tests prevents handler pollution. Use `server.use()` to override handlers per-test.

### Testing Error Handling and Status Codes

API routes must handle errors gracefully, returning appropriate HTTP status codes and error messages. Test error scenarios: invalid input (400), unauthorized access (401), missing resources (404), rate limiting (429), and server errors (500).

#### Comprehensive Error Testing

```typescript
describe('POST /api/metrics - error handling', () => {
  it('returns 400 for missing required fields', async () => {
    const body = JSON.stringify({ name: 'page_views' })  // Missing value

    const request = new NextRequest('http://localhost:3000/api/metrics', {
      method: 'POST',
      body,
    })

    const response = await POST(request)

    expect(response.status).toBe(400)
    expect(await response.json()).toMatchObject({
      error: 'Missing required field: value',
    })
  })

  it('returns 500 for database errors', async () => {
    const { saveMetric } = await import('@/lib/database')
    vi.mocked(saveMetric).mockRejectedValueOnce(new Error('DB connection failed'))

    const body = JSON.stringify({ name: 'test', value: 123 })
    const request = new NextRequest('http://localhost:3000/api/metrics', {
      method: 'POST',
      body,
    })

    const response = await POST(request)

    expect(response.status).toBe(500)
    expect(await response.json()).toMatchObject({
      error: 'Internal server error',
    })
  })
})
```

Test each error case explicitly. Mock dependencies to throw errors (`mockRejectedValueOnce`). Verify error responses contain helpful messages without leaking sensitive information. Never expose database errors or stack traces to clients.

### Testing Authentication and Authorization

API routes requiring authentication need tests verifying token validation, session checking, and permission enforcement. Mock authentication middleware to test both authenticated and unauthenticated scenarios.

#### Testing Protected Routes

```typescript
describe('GET /api/admin/metrics - authentication', () => {
  it('returns 401 for missing authorization header', async () => {
    const request = new NextRequest('http://localhost:3000/api/admin/metrics')

    const response = await GET(request)

    expect(response.status).toBe(401)
    expect(await response.json()).toMatchObject({
      error: 'Unauthorized',
    })
  })

  it('returns 403 for invalid token', async () => {
    const request = new NextRequest('http://localhost:3000/api/admin/metrics', {
      headers: { Authorization: 'Bearer invalid-token' },
    })

    const response = await GET(request)

    expect(response.status).toBe(403)
  })

  it('returns data for valid token', async () => {
    vi.mock('@/lib/auth', () => ({
      verifyToken: vi.fn().mockResolvedValue({ userId: '123', role: 'admin' }),
    }))

    const request = new NextRequest('http://localhost:3000/api/admin/metrics', {
      headers: { Authorization: 'Bearer valid-token' },
    })

    const response = await GET(request)

    expect(response.status).toBe(200)
  })
})
```

Test authentication failure (401), authorization failure (403), and success (200). Mock token verification to avoid real JWT signing during tests. Verify tokens are validated before executing business logic.

## API Testing Coverage Goals

**Critical API routes (payment, auth, data writes):** 90%+ coverage
**Standard API routes (data reads, transformations):** 70-80% coverage
**Simple API routes (health checks, status):** 50-60% coverage

Policy-node's 10+ API routes require estimated 20-30 integration tests. Start with high-risk routes handling data transformations (metrics, phrases) then expand to standard CRUD routes.
