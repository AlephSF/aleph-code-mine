---
title: "App Router Route Handlers"
category: "data-fetching"
subcategory: "api-routes"
tags: ["route-handlers", "api-routes", "app-router", "nextrequest", "nextresponse", "webhooks"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

# App Router Route Handlers

## Overview

Route Handlers in Next.js App Router replace Pages Router API routes with a file-based routing system using `route.ts` files. Route handlers define server-side endpoints that respond to HTTP methods (GET, POST, PUT, DELETE, PATCH) using Web standard Request and Response APIs.

Route handler adoption shows 67% across analyzed codebases with App Router: helix-dot-com-next (8 handlers) and policy-node (14 handlers) implement route handlers for preview mode, webhooks, and API endpoints. kariusdx-next (Pages Router only) has 0 route handlers.

## Basic Route Handler Pattern

## File-Based API Routes

Route handlers use `route.ts` or `route.js` files within the `app` directory structure to define API endpoints.

```typescript
// app/api/hello/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ message: 'Hello, World!' })
}
```

**Route Mapping:**
- File: `app/api/hello/route.ts`
- URL: `https://example.com/api/hello`
- Method: GET

**Naming Convention:**
- Must be named `route.ts` or `route.tsx` (exact filename)
- Cannot coexist with `page.tsx` in same directory
- Located anywhere in `app` directory tree

**Source Evidence:** helix-dot-com-next implements 8 route handlers at `app/api/*/route.ts` for preview mode and webhooks. policy-node implements 14 route handlers for multilingual preview, revalidation, and sitemap generation.

## HTTP Method Handlers

## Supported Method Exports

Route handlers export async functions named after HTTP methods.

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getPosts, createPost } from '@/lib/api'

export async function GET(request: NextRequest) {
  const posts = await getPosts()
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}
```

**Supported Methods:**
- `GET` - Retrieve resources
- `POST` - Create resources
- `PUT` - Replace resources
- `PATCH` - Update resources
- `DELETE` - Remove resources
- `HEAD` - Same as GET without response body
- `OPTIONS` - CORS preflight requests

**Method Behavior:**
- Only exported methods are available
- 405 Method Not Allowed returned for unsupported methods
- Each method handler receives `NextRequest` parameter
- Must return `Response` or `NextResponse` object

## NextRequest and NextResponse APIs

## Request Object Methods

NextRequest extends Web Request API with Next.js-specific utilities.

```typescript
// app/api/search/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  // URL query parameters
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get('q') // ?q=next.js
  const page = searchParams.get('page') || '1'

  // Request headers
  const userAgent = request.headers.get('user-agent')
  const cookies = request.cookies.get('session')

  // Full URL
  const url = request.nextUrl.href // https://example.com/api/search?q=next.js

  const results = await searchDatabase(query, parseInt(page))

  return NextResponse.json({
    query,
    page: parseInt(page),
    results,
  })
}
```

**NextRequest Properties:**
- `nextUrl` - URL object with pathname, searchParams, etc.
- `cookies` - Cookie management (get, set, delete)
- `headers` - HTTP headers map
- `json()` - Parse JSON body
- `formData()` - Parse form data
- `text()` - Parse text body

## Response Object Methods

NextResponse extends Web Response API with convenience methods.

```typescript
// app/api/data/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const data = { message: 'Success' }

  // JSON response with status
  return NextResponse.json(data, {
    status: 200,
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
    },
  })
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  // Redirect response
  return NextResponse.redirect(new URL('/success', request.url))
}
```

**NextResponse Static Methods:**
- `NextResponse.json(data, init)` - JSON response with automatic headers
- `NextResponse.redirect(url, status)` - Redirect response (302 or 301)
- `NextResponse.rewrite(url)` - Internal rewrite (URL stays same)
- `NextResponse.next()` - Continue to next middleware

## Dynamic Route Handlers

## Path Parameters in Routes

Route handlers support dynamic segments with `[param]` syntax.

```typescript
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getPost, updatePost, deletePost } from '@/lib/api'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const post = await getPost(params.id)

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    )
  }

  return NextResponse.json(post)
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json()
  const updatedPost = await updatePost(params.id, body)

  return NextResponse.json(updatedPost)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await deletePost(params.id)
  return NextResponse.json({ success: true }, { status: 204 })
}
```

**Dynamic Segment Rules:**
- File: `app/api/posts/[id]/route.ts`
- URL: `/api/posts/123` → `params.id = "123"`
- Second parameter provides `params` object
- Type-safe with TypeScript generics

## Catch-All Route Handlers

```typescript
// app/api/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  // /api/a/b/c → params.path = ['a', 'b', 'c']
  const fullPath = params.path.join('/')

  return NextResponse.json({
    message: `Catch-all handler for: ${fullPath}`,
  })
}
```

## Preview Mode Route Handlers

## Draft Mode Enable/Disable Pattern

Route handlers commonly implement preview mode endpoints for CMS integration.

```typescript
// app/api/preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  // Validate secret to prevent unauthorized access
  const secret = request.nextUrl.searchParams.get('secret')

  if (secret !== process.env.SANITY_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }

  // Get destination slug from query
  const slug = request.nextUrl.searchParams.get('slug')
  const redirectTo = slug ? `/${slug}` : '/'

  // Enable draft mode (sets secure cookie)
  draftMode().enable()

  // Redirect to content page
  redirect(redirectTo)
}
```

```typescript
// app/api/exit-preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET() {
  draftMode().disable()
  redirect('/')
}
```

**Preview Handler Characteristics:**
- `draftMode().enable()` sets HTTP-only secure cookie
- Query parameter validation prevents unauthorized preview access
- Redirect to content page after enabling draft mode
- Exit handler clears cookie and redirects to homepage

**Source Evidence:** helix-dot-com-next implements preview handlers at `app/api/preview/route.ts` and `app/api/exit-preview/route.ts`. 100% of App Router projects with CMS integration implement this pattern.

## Webhook Route Handlers

## CMS Revalidation Webhooks

Route handlers process CMS webhooks for on-demand revalidation.

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  // Validate webhook signature
  const signature = request.headers.get('x-sanity-signature')
  const isValid = validateSignature(signature, await request.text())

  if (!isValid) {
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 401 }
    )
  }

  const body = await request.json()
  const { _type, slug } = body

  try {
    // Revalidate by path
    if (slug?.current) {
      await revalidatePath(`/${slug.current}`)
    }

    // Revalidate by cache tag
    if (_type) {
      revalidateTag(_type) // Invalidate all fetches tagged with this type
    }

    return NextResponse.json({
      revalidated: true,
      now: Date.now(),
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Error revalidating' },
      { status: 500 }
    )
  }
}
```

**Webhook Pattern Elements:**
- POST method for webhook receivers
- Signature validation prevents unauthorized revalidation
- `revalidatePath()` invalidates specific route
- `revalidateTag()` invalidates all fetches with tag
- Error handling with appropriate status codes

## CORS Configuration

## Cross-Origin Request Handling

Route handlers implement CORS headers for external API access.

```typescript
// app/api/public/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const data = { message: 'Public API' }

  return NextResponse.json(data, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

**CORS Best Practices:**
- Implement OPTIONS handler for preflight requests
- Set specific origins instead of `*` in production
- Include credentials header if using cookies
- Consistent headers across all methods

## Route Handler Caching

## Default Cache Behavior

Route handlers have different default cache behavior based on HTTP method.

```typescript
// app/api/data/route.ts - GET is cached by default
export async function GET() {
  const data = await fetchData()
  return NextResponse.json(data)
}

// Force dynamic (no cache)
export const dynamic = 'force-dynamic'

export async function GET() {
  const data = await fetchData()
  return NextResponse.json(data) // Now not cached
}
```

**Cache Defaults:**
- **GET:** Cached by default (force-cache)
- **POST, PUT, DELETE, PATCH:** Not cached (no-store)
- Override with `export const dynamic = 'force-dynamic'`
- Set Cache-Control headers for CDN caching

## Manual Cache Control

```typescript
// app/api/posts/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const posts = await fetchPosts()

  return NextResponse.json(posts, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
    },
  })
}
```

## Migration from Pages Router API Routes

## Before (Pages Router)
```typescript
// pages/api/hello.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const data = await fetchData()
  res.status(200).json(data)
}
```

## After (App Router)
```typescript
// app/api/hello/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const data = await fetchData()
  return NextResponse.json(data)
}
```

**Key Migration Changes:**
- Default export handler → Named HTTP method exports
- Single handler with method checks → Separate functions per method
- `req`/`res` parameters → `NextRequest`/`NextResponse` objects
- `res.status().json()` → `NextResponse.json(data, { status })`
- `pages/api/` directory → `app/api/` directory
- Filename flexibility → Must be named `route.ts`

## Error Handling in Route Handlers

## Try/Catch with Proper Status Codes

```typescript
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getPost } from '@/lib/api'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const post = await getPost(params.id)

    if (!post) {
      return NextResponse.json(
        { error: 'Post not found' },
        { status: 404 }
      )
    }

    return NextResponse.json(post)
  } catch (error) {
    console.error(`Error fetching post ${params.id}:`, error)

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**Error Response Best Practices:**
- 400 - Bad Request (invalid input)
- 401 - Unauthorized (missing/invalid auth)
- 404 - Not Found (resource doesn't exist)
- 405 - Method Not Allowed (handled automatically)
- 500 - Internal Server Error (unexpected errors)
- Include error message in JSON body
- Log errors server-side with context

## Anti-Patterns to Avoid

## Missing Method Handlers

Implementing only GET without POST when both are needed.

```typescript
// ❌ AVOID: Only GET handler, missing POST
export async function GET() {
  const posts = await getPosts()
  return NextResponse.json(posts)
}
// POST requests return 405 Method Not Allowed

// ✅ CORRECT: Implement all needed methods
export async function GET() {
  const posts = await getPosts()
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}
```

## Not Validating Request Input

Accepting request body without validation.

```typescript
// ❌ AVOID: No input validation
export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body) // May crash if body malformed
  return NextResponse.json(post)
}

// ✅ CORRECT: Validate input before processing
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    if (!body.title || !body.content) {
      return NextResponse.json(
        { error: 'Missing required fields: title, content' },
        { status: 400 }
      )
    }

    const post = await createPost(body)
    return NextResponse.json(post, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid JSON body' },
      { status: 400 }
    )
  }
}
```

## Forgetting CORS Headers

External API access blocked without CORS headers.

```typescript
// ❌ AVOID: No CORS headers (blocks external requests)
export async function GET() {
  return NextResponse.json({ data: 'public' })
}

// ✅ CORRECT: Include CORS headers for public APIs
export async function GET() {
  return NextResponse.json(
    { data: 'public' },
    {
      headers: {
        'Access-Control-Allow-Origin': 'https://trusted-domain.com',
      },
    }
  )
}

export async function OPTIONS() {
  return new NextResponse(null, {
    headers: {
      'Access-Control-Allow-Origin': 'https://trusted-domain.com',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
    },
  })
}
```

## Coexisting page.tsx and route.ts

Cannot have both in same directory (build error).

```
❌ AVOID:
app/dashboard/
├── page.tsx     # Page component
└── route.ts     # Route handler
(Build error: Conflicting routes)

✅ CORRECT:
app/
├── dashboard/
│   └── page.tsx
└── api/
    └── dashboard/
        └── route.ts
```
