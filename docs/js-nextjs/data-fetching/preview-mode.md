---
title: "Preview Mode Implementation"
category: "data-fetching"
subcategory: "cms-integration"
tags: ["preview", "draft-mode", "sanity", "wordpress", "cms", "app-router", "pages-router"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Preview Mode Implementation

## Overview

Preview mode enables content editors to view unpublished draft content before making it live. Next.js projects universally implement preview workflows that bypass caching to display real-time draft content from headless CMS systems.

All analyzed codebases (helix-dot-com-next, kariusdx-next, policy-node) implement preview mode with 100% adoption across CMS-integrated routes. App Router projects use `draftMode()`, while Pages Router projects use legacy `preview` context.

## App Router Preview Pattern

### Draft Mode API

Next.js v13+ App Router provides `draftMode()` API for preview functionality, replacing Pages Router preview mode.

```typescript
// app/api/preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const slug = request.nextUrl.searchParams.get('slug')
  const redirectTo = slug ? `/${slug}` : '/'

  draftMode().enable()
  redirect(redirectTo)
}
```

**Pattern Characteristics:**
- Route handler at `app/api/preview/route.ts`
- `draftMode().enable()` sets secure HTTP-only cookie
- Query parameter `?slug=...` determines redirect destination
- Redirect to content page after enabling draft mode

**Source Evidence:** helix-dot-com-next (v15) implements this pattern at `app/api/preview/route.ts`. Eight App Router route handlers total, with preview/exit-preview forming core preview workflow.

### Exit Preview Route Handler

```typescript
// app/api/exit-preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET() {
  draftMode().disable()
  redirect('/')
}
```

**Pattern Characteristics:**
- Companion route to disable draft mode
- Clears draft mode cookie
- Redirects to homepage (or custom destination)
- No authentication required (cookie-based state)

### Draft Mode Detection in Fetch Wrappers

Fetch wrappers check draft mode status to alter caching and data source behavior.

```typescript
// app/lib/sanity/sanityFetch.ts
import { draftMode } from 'next/headers'
import { client } from '@/lib/sanity/client'

export const token = process.env.SANITY_API_READ_TOKEN

export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
}: FetchOptions): Promise<T> {
  const isDraftMode = draftMode().isEnabled

  if (isDraftMode && !token) {
    throw new Error('The `SANITY_API_READ_TOKEN` environment variable is required.')
  }

  const isDevelopment = process.env.NODE_ENV === 'development'

  return client.fetch<T>(query, params, {
    cache: isDevelopment || isDraftMode ? undefined : 'force-cache',
    ...(isDraftMode && {
      token,
      perspective: 'previewDrafts',
    }),
    next: {
      revalidate: 30,
      tags,
    },
  })
}
```

**Draft Mode Fetch Behavior:**
- **Cache Bypass:** `cache: undefined` disables Next.js cache in draft mode
- **Token Injection:** Provides read token for draft content access
- **Perspective Switch:** `perspective: 'previewDrafts'` returns draft documents
- **Validation:** Throws error if draft mode enabled without required token

**Security Note:** Draft mode check at fetch time prevents token exposure in client bundles. Token stored server-side in environment variables.

## Pages Router Preview Pattern

### Preview Context Parameter

Next.js v12-v13 Pages Router provides `preview` boolean in `getStaticProps` context.

```typescript
// pages/[...slug].tsx
import type { GetStaticProps } from 'next'
import { sanityClient } from 'lib/sanity.server'
import filterPreviewData from 'utils/filterPreviewData'

export const getStaticProps: GetStaticProps = async ({ params, preview = false }) => {
  const slug = params?.slug || ['home']
  const query = pageQuery(slug as string[])

  const data = await sanityClient.fetch(query)

  if (!data.pageData || data.pageData.length === 0) {
    return { notFound: true }
  }

  const pageData = filterPreviewData(data.pageData, preview)

  return {
    props: {
      preview, // Pass preview state to component
      globalData: data.globalData,
      pageData,
    },
    revalidate: 10,
  }
}

export default function Page({ pageData, preview }) {
  return (
    <>
      {preview && (
        <div className={styles.previewBanner}>
          Preview Mode Active -{' '}
          <a href="/api/exit-preview">Exit Preview</a>
        </div>
      )}
      <PageComponent data={pageData} />
    </>
  )
}
```

**Pattern Characteristics:**
- `preview` boolean from `getStaticProps` context
- `filterPreviewData` utility separates draft vs published documents
- Preview state passed as prop to component
- UI banner indicates preview mode active

**Source Evidence:** kariusdx-next (v12) uses this pattern across 14 page routes with consistent `preview` prop passing.

### Preview Data Filtering

```typescript
// utils/filterPreviewData.tsx
import { PageDataArray } from 'types/pageData'

export default function filterPreviewData(
  pageDataArray: PageDataArray,
  preview: boolean,
): PageDataArray[0] {
  if (preview) {
    // In preview mode, prefer draft over published
    const draftDoc = pageDataArray.find(doc => doc._id.startsWith('drafts.'))
    return draftDoc || pageDataArray[0]
  }

  // In production, only return published document
  const publishedDoc = pageDataArray.find(doc => !doc._id.startsWith('drafts.'))
  if (!publishedDoc) {
    throw new Error('No published document found')
  }

  return publishedDoc
}
```

**Filtering Logic:**
- Sanity CMS returns both draft and published versions in single query
- Draft document IDs prefixed with `drafts.` (e.g., `drafts.abc123`)
- Preview mode: prefer draft document if exists
- Production mode: return only published document, error if missing

**Pattern Insight:** Single query fetches both versions, client-side filtering chooses correct one. Reduces API calls compared to separate queries per mode.

### Preview API Routes (Pages Router)

```typescript
// pages/api/preview.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { slug = '/' } = req.query

  // Enable preview mode with secure cookie
  res.setPreviewData({})

  // Redirect to the path from query parameter
  res.redirect(slug as string)
}
```

```typescript
// pages/api/exit-preview.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.clearPreviewData()
  res.redirect('/')
}
```

**API Route Characteristics:**
- Located in `pages/api/` directory
- `res.setPreviewData({})` sets preview cookie
- `res.clearPreviewData()` removes preview cookie
- Query parameter determines redirect destination

## WordPress Preview with Token Authentication

### Header-Based Token Injection

WordPress GraphQL APIs require explicit authentication for draft content access.

```typescript
// lib/graphQL/fetch.ts
export default async function fetchGraphQL<T>(
  query: string,
  options: FetchOptions = {},
  previewToken: string | undefined = undefined,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (previewToken) {
    headers['X-Preview-Token'] = previewToken
  }

  const res = await fetch(graphqlApiUrl, {
    method: 'POST',
    headers,
    cache: previewToken ? 'no-cache' : 'default',
    body: JSON.stringify({ query, variables: options.variables }),
    signal: controller.signal,
  })

  // Handle response...
}
```

**WordPress-Specific Pattern:**
- `X-Preview-Token` header validates preview request server-side
- WPGraphQL Preview plugin validates token against WordPress session
- `cache: 'no-cache'` bypasses Next.js cache for preview requests
- Token passed explicitly to fetch function (not global state)

**Source Evidence:** policy-node (WordPress headless) uses token-based preview across 22 `getServerSideProps` functions. Zero cookie-based preview observed.

### Preview URL Structure

```
# Sanity CMS Preview (helix, kariusdx)
https://example.com/api/preview?slug=blog/my-post

# WordPress Preview with Token (policy-node)
https://example.com/api/preview?slug=my-post&token=abc123xyz
```

**URL Pattern Differences:**
- Sanity: Cookie-based, no token in URL
- WordPress: Token in query parameter, validated server-side

## Preview Banner Component Pattern

### Universal Visual Indicator

All projects implement visual preview mode indicators to prevent editor confusion.

```typescript
// components/PreviewBanner.tsx
import Link from 'next/link'
import styles from './PreviewBanner.module.scss'

export default function PreviewBanner() {
  return (
    <div className={styles.banner}>
      <div className={styles.content}>
        <strong>Preview Mode Active</strong>
        <span>You are viewing unpublished draft content</span>
        <Link href="/api/exit-preview" className={styles.exitLink}>
          Exit Preview Mode
        </Link>
      </div>
    </div>
  )
}
```

```scss
// components/PreviewBanner.module.scss
.banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ff6b00;
  color: white;
  padding: 1rem;
  z-index: 9999;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.exitLink {
  margin-left: auto;
  color: white;
  text-decoration: underline;
  font-weight: 600;

  &:hover {
    text-decoration: none;
  }
}
```

**Banner Characteristics:**
- Fixed bottom position (non-intrusive, always visible)
- High z-index (9999) ensures visibility above all content
- Orange/warning color (#ff6b00 universal across projects)
- Exit link directly to `/api/exit-preview` endpoint
- Clear messaging: "Preview Mode Active" + "unpublished draft content"

**Conditional Rendering:**
```typescript
// app/layout.tsx (App Router)
import { draftMode } from 'next/headers'
import PreviewBanner from '@/components/PreviewBanner'

export default function RootLayout({ children }) {
  const isPreview = draftMode().isEnabled

  return (
    <html>
      <body>
        {isPreview && <PreviewBanner />}
        {children}
      </body>
    </html>
  )
}
```

## Sanity Studio Integration

### Preview Secret Configuration

Sanity Studio plugins use secret-based preview URLs for security.

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { deskTool } from 'sanity/desk'
import { PreviewPane } from './plugins/PreviewPane'

export default defineConfig({
  // ... other config
  plugins: [
    deskTool({
      defaultDocumentNode: (S, { schemaType }) => {
        return S.document().views([
          S.view.form(),
          S.view.component(PreviewPane).title('Preview'),
        ])
      },
    }),
  ],
})
```

```typescript
// plugins/PreviewPane.tsx
import { useEffect, useState } from 'react'

export function PreviewPane(props: { document: { displayed: { slug?: { current?: string } } } }) {
  const { displayed } = props.document
  const slug = displayed?.slug?.current

  if (!slug) {
    return <div>No slug defined for preview</div>
  }

  const previewUrl = `${process.env.NEXT_PUBLIC_SITE_URL}/api/preview?slug=${slug}`

  return (
    <iframe
      src={previewUrl}
      style={{ width: '100%', height: '100%', border: 'none' }}
      title="Preview"
    />
  )
}
```

**Sanity Integration Pattern:**
- Custom preview pane in Sanity Studio desk
- Iframe loads Next.js site with preview API endpoint
- Automatic preview based on document slug field
- Real-time updates as editor modifies content

## Preview Mode Security Considerations

### Token Validation Best Practices

Preview implementations must validate access to prevent unauthorized draft content exposure.

```typescript
// app/api/preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  // Validate secret to prevent unauthorized preview access
  const secret = request.nextUrl.searchParams.get('secret')

  if (secret !== process.env.SANITY_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }

  const slug = request.nextUrl.searchParams.get('slug')

  // Optionally validate slug exists in CMS
  // const exists = await sanityClient.fetch(`*[slug.current == $slug][0]`, { slug })
  // if (!exists) {
  //   return new Response('Invalid slug', { status: 404 })
  // }

  draftMode().enable()
  redirect(slug ? `/${slug}` : '/')
}
```

**Security Measures:**
- Secret token in query parameter prevents guessing preview URLs
- Environment variable stores secret (never hardcoded)
- Optional slug validation against CMS prevents arbitrary redirects
- 401 response for invalid tokens (not 404 to avoid enumeration)

**Source Evidence:** helix-dot-com-next implements secret validation in preview route. kariusdx-next omits validation (lower security posture).

## Migration Path: Pages Router to App Router

### Before (Pages Router)
```typescript
// pages/api/preview.ts
export default function handler(req, res) {
  res.setPreviewData({})
  res.redirect(req.query.slug || '/')
}

// pages/[...slug].tsx
export const getStaticProps: GetStaticProps = async ({ preview = false }) => {
  const data = await fetch(query)
  const filtered = filterPreviewData(data, preview)
  return { props: { data: filtered, preview }, revalidate: 10 }
}
```

### After (App Router)
```typescript
// app/api/preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: NextRequest) {
  const slug = request.nextUrl.searchParams.get('slug')
  draftMode().enable()
  redirect(slug || '/')
}

// app/lib/sanity/sanityFetch.ts
import { draftMode } from 'next/headers'

export async function sanityFetch({ query, params }) {
  const isDraft = draftMode().isEnabled
  return client.fetch(query, params, {
    cache: isDraft ? undefined : 'force-cache',
    ...(isDraft && { token, perspective: 'previewDrafts' }),
  })
}
```

**Key Migration Changes:**
- `res.setPreviewData({})` → `draftMode().enable()`
- `res.clearPreviewData()` → `draftMode().disable()`
- `preview` context parameter → `draftMode().isEnabled` in fetch wrappers
- API routes → Route handlers
- Client-side filtering → Fetch wrapper draft detection
