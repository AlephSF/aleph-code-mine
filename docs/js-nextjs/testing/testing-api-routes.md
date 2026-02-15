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

## API Testing Overview

API routes (Pages Router) and route handlers (App Router) execute server-side request/response logic including data transformations, external API calls, and database operations. Integration tests verify HTTP method handling, request parsing, response formatting, error handling, and status codes. Mock external dependencies (databases, third-party APIs) to ensure tests run fast and deterministically.

## Route Handlers vs API Routes

Next.js App Router route handlers use Web Standards (Request, Response) while Pages Router API routes use Node.js APIs (NextApiRequest, NextApiResponse). Route handlers export named functions (GET, POST, PUT, DELETE) while API routes export single default handler with method switching. Policy-node has 10+ API routes handling metrics and phrases transformations - all untested. Source confidence: 0% (no API testing infrastructure exists in analyzed codebases).

## Testing GET Route Handlers

Route handlers accept NextRequest and return Response. Test by importing handler, creating mock Request, calling handler, asserting Response properties.

```typescript
import { describe, it, expect, vi } from 'vitest'
import { GET } from './route'
import { NextRequest } from 'next/server'

vi.mock('@/lib/csvLoader', () => ({
  loadPhrases: vi.fn().mockResolvedValue([{id:'1',text:'Hello',locale:'en-US'},{id:'2',text:'World',locale:'en-US'}])
}))

describe('GET /api/phrases/[locale]', () => {
  it('returns phrases for valid locale', async () => {
    const req = new NextRequest('http://localhost:3000/api/phrases/en-US')
    const res = await GET(req, {params:{locale:'en-US'}})
    expect(res.status).toBe(200)
    const d = await res.json()
    expect(d).toEqual({phrases:[{id:'1',text:'Hello',locale:'en-US'},{id:'2',text:'World',locale:'en-US'}],locale:'en-US',count:2})
  })

  it('returns 404 for invalid locale', async () => {
    const {loadPhrases} = await import('@/lib/csvLoader')
    vi.mocked(loadPhrases).mockResolvedValueOnce([])
    const req = new NextRequest('http://localhost:3000/api/phrases/invalid')
    const res = await GET(req, {params:{locale:'invalid'}})
    expect(res.status).toBe(404)
    expect(await res.json()).toEqual({error:'No phrases found for locale: invalid'})
  })
})
```

Create NextRequest with full URL. Pass route parameters via `params`. Test success (200) and error (404). Mock external sources.

## Testing POST Route Handlers

POST handlers parse body (JSON, FormData) and perform mutations. Test by creating NextRequest with body, calling handler.

```typescript
import { describe, it, expect, vi } from 'vitest'
import { POST } from './route'
import { NextRequest } from 'next/server'

vi.mock('@/lib/database', () => ({
  saveMetric: vi.fn().mockResolvedValue({id:'123',status:'saved'})
}))

describe('POST /api/metrics', () => {
  it('saves metric with valid data', async () => {
    const b = JSON.stringify({name:'page_views',value:1234,timestamp:'2026-02-11T10:00:00Z'})
    const req = new NextRequest('http://localhost:3000/api/metrics', {method:'POST',body:b,headers:{'Content-Type':'application/json'}})
    const res = await POST(req)
    expect(res.status).toBe(201)
    expect(await res.json()).toMatchObject({id:'123',status:'saved'})
    const {saveMetric} = await import('@/lib/database')
    expect(saveMetric).toHaveBeenCalledWith({name:'page_views',value:1234,timestamp:'2026-02-11T10:00:00Z'})
  })

  it('returns 400 for invalid JSON', async () => {
    const req = new NextRequest('http://localhost:3000/api/metrics', {method:'POST',body:'invalid json',headers:{'Content-Type':'application/json'}})
    const res = await POST(req)
    expect(res.status).toBe(400)
    expect((await res.json()).error).toMatch(/invalid json/i)
  })
})
```

Stringify JSON body and set Content-Type. Verify handler parses body and passes to dependencies. Assert response status/body.

## Testing Pages Router API Routes

Pages Router API routes use Node.js request/response objects. Test by creating mock req/res objects, calling handler, and asserting response properties. Use helper library like `node-mocks-http` to create mock objects easily.

```typescript
// pages/api/health.test.ts
import { describe, it, expect } from 'vitest'
import { createMocks } from 'node-mocks-http'
import handler from './health'

describe('GET /api/health', () => {
  it('returns 200 with health status', async () => {
    const { req, res } = createMocks({ method: 'GET' })
    await handler(req, res)
    expect(res._getStatusCode()).toBe(200)
    expect(res._getJSONData()).toEqual({ status: 'ok', timestamp: expect.any(String) })
  })

  it('returns 405 for POST method', async () => {
    const { req, res } = createMocks({ method: 'POST' })
    await handler(req, res)
    expect(res._getStatusCode()).toBe(405)
    expect(res._getJSONData()).toEqual({ error: 'Method not allowed' })
  })
})
```

Install `node-mocks-http`: `npm install -D node-mocks-http @types/node-mocks-http`. `createMocks` generates req/res objects with method, headers, body, and query parameters. Access response with `_getStatusCode()` and `_getJSONData()`. Test all supported HTTP methods.

## Testing Data Transformations

Policy-node's API routes perform complex data transformations (metrics config, phrase localization, municipality data). Test transformations with diverse input data covering edge cases, boundary conditions, and error states.

```typescript
import { describe, it, expect } from 'vitest'
import { transformLocationData } from './transformLocationData'

describe('transformLocationData', () => {
  it('transforms raw CSV data to location objects', () => {
    const raw = [{muni_id:'1',name:'Toronto',population:'2930000',province:'ON'},{muni_id:'2',name:'Montreal',population:'1780000',province:'QC'}]
    const r = transformLocationData(raw)
    expect(r).toEqual([{id:'1',name:'Toronto',population:2930000,province:'ON'},{id:'2',name:'Montreal',population:1780000,province:'QC'}])
  })

  it('handles missing population gracefully', () => {
    const raw = [{muni_id:'1',name:'Test',population:'',province:'ON'}]
    const r = transformLocationData(raw)
    expect(r[0].population).toBe(0)
  })

  it('filters out invalid records', () => {
    const raw = [{muni_id:'',name:'Invalid',population:'1000',province:'ON'},{muni_id:'1',name:'Valid',population:'2000',province:'QC'}]
    const r = transformLocationData(raw)
    expect(r).toHaveLength(1)
    expect(r[0].id).toBe('1')
  })
})
```

Test transformation utilities separately from API routes for faster tests. Verify data type conversions, default values for missing fields, and filtering of invalid records.

## Mocking External APIs with MSW

Route handlers often call third-party APIs (Sanity, GraphQL, S3). Mock Service Worker intercepts HTTP requests during tests, returning predictable responses without real network calls. MSW works identically in Node.js tests and browser environments.

```typescript
// vitest.setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('https://api.sanity.io/v2023-08-01/data/query/*', () => {
    return HttpResponse.json({ result: [{ _id: '1', title: 'Test Page', slug: 'test' }] })
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

## Testing Error Handling

API routes must handle errors gracefully, returning appropriate HTTP status codes and error messages. Test error scenarios: invalid input (400), unauthorized access (401), missing resources (404), rate limiting (429), and server errors (500).

```typescript
describe('POST /api/metrics - error handling', () => {
  it('returns 400 for missing required fields', async () => {
    const b = JSON.stringify({ name: 'page_views' })
    const req = new NextRequest('http://localhost:3000/api/metrics', { method: 'POST', body: b })
    const res = await POST(req)
    expect(res.status).toBe(400)
    expect(await res.json()).toMatchObject({ error: 'Missing required field: value' })
  })

  it('returns 500 for database errors', async () => {
    const { saveMetric } = await import('@/lib/database')
    vi.mocked(saveMetric).mockRejectedValueOnce(new Error('DB connection failed'))
    const b = JSON.stringify({ name: 'test', value: 123 })
    const req = new NextRequest('http://localhost:3000/api/metrics', { method: 'POST', body: b })
    const res = await POST(req)
    expect(res.status).toBe(500)
    expect(await res.json()).toMatchObject({ error: 'Internal server error' })
  })
})
```

Test each error case explicitly. Mock dependencies to throw errors (`mockRejectedValueOnce`). Verify error responses contain helpful messages without leaking sensitive information. Never expose database errors or stack traces to clients.

## Testing Authentication

API routes requiring authentication need tests verifying token validation, session checking, and permission enforcement. Mock authentication middleware to test both authenticated and unauthenticated scenarios.

```typescript
describe('GET /api/admin/metrics - authentication', () => {
  it('returns 401 for missing authorization header', async () => {
    const req = new NextRequest('http://localhost:3000/api/admin/metrics')
    const res = await GET(req)
    expect(res.status).toBe(401)
    expect(await res.json()).toMatchObject({ error: 'Unauthorized' })
  })

  it('returns 403 for invalid token', async () => {
    const req = new NextRequest('http://localhost:3000/api/admin/metrics', {
      headers: { Authorization: 'Bearer invalid-token' },
    })
    const res = await GET(req)
    expect(res.status).toBe(403)
  })

  it('returns data for valid token', async () => {
    vi.mock('@/lib/auth', () => ({
      verifyToken: vi.fn().mockResolvedValue({ userId: '123', role: 'admin' }),
    }))
    const req = new NextRequest('http://localhost:3000/api/admin/metrics', {
      headers: { Authorization: 'Bearer valid-token' },
    })
    const res = await GET(req)
    expect(res.status).toBe(200)
  })
})
```

Test authentication failure (401), authorization failure (403), and success (200). Mock token verification to avoid real JWT signing during tests. Verify tokens are validated before executing business logic.

## API Testing Coverage Goals

**Critical API routes (payment, auth, data writes):** 90%+ coverage
**Standard API routes (data reads, transformations):** 70-80% coverage
**Simple API routes (health checks, status):** 50-60% coverage

Policy-node's 10+ API routes require estimated 20-30 integration tests. Start with high-risk routes handling data transformations (metrics, phrases) then expand to standard CRUD routes.
