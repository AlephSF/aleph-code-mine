---
title: "App Router vs Pages Router: Architecture Comparison"
category: "project-structure"
subcategory: "routing"
tags: ["app-router", "pages-router", "next.js", "migration", "architecture"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

# App Router vs Pages Router: Architecture Comparison

## Overview

Next.js offers two routing architectures: modern App Router (Next.js 13+) and legacy Pages Router (Next.js 12 and earlier). Helix (v15) and policy-node (v14) migrated to App Router (67% adoption), while kariusdx remains on Pages Router (v12). App Router introduces file-based conventions, server components by default, streaming, and built-in metadata management.

**Key Difference:** Pages Router uses arbitrary file names in `pages/` directory for routes. App Router uses special file names (`page.tsx`, `layout.tsx`, `error.tsx`) in `app/` directory with explicit routing semantics.

**Migration Status:** 67% App Router adoption indicates industry shift toward modern architecture. Pages Router remains supported but receives no new features.

## Directory Structure Comparison

### App Router (helix, policy-node)

```
app/
├── layout.tsx          ← Root layout (replaces _app.tsx)
├── page.tsx            ← Homepage / route
├── not-found.tsx       ← 404 page (replaces 404.tsx)
├── error.tsx           ← Error boundary (new feature)
├── loading.tsx         ← Loading UI (new feature)
├── api/
│   └── cache/
│       └── route.ts    ← API route (replaces pages/api/)
└── resources/
    ├── page.tsx        ← /resources route
    └── [slug]/
        └── page.tsx    ← /resources/[slug] route
```

**Pattern:** Special file names (`page.tsx`, `layout.tsx`) define routing behavior. Folder structure maps directly to URL structure.

### Pages Router (kariusdx)

```
pages/
├── _app.tsx            ← Global app wrapper
├── _document.js        ← HTML document customization
├── 404.tsx             ← 404 page
├── index.tsx           ← Homepage (/)
├── [...slug].tsx       ← Catch-all route
└── api/
    └── endpoint.ts     ← API route
```

**Pattern:** File names directly become routes. `index.tsx` → `/`, `about.tsx` → `/about`, `[slug].tsx` → `/[slug]`.

**Comparison:** Pages Router simpler mental model (file = route). App Router more explicit semantics (page.tsx = route, layout.tsx = shared UI).

## App Router File Naming

App Router reserves specific file names for routing behavior. All other files are non-routable.

| File Name | Purpose | Example |
|-----------|---------|---------|
| `page.tsx` | Route page | `app/about/page.tsx` → `/about` |
| `layout.tsx` | Shared UI wrapper | Root/nested layouts |
| `not-found.tsx` | 404 page | Custom 404 |
| `error.tsx` | Error boundary | Error handling |
| `loading.tsx` | Loading UI | Streaming fallback |
| `route.ts` | API handler | API endpoints |

**Rule:** Only `page.tsx` creates routes. Folder structure defines URL paths.

**Example:**

```
app/blog/
├── page.tsx        ← /blog
├── BlogList.tsx    ← Component (not route)
└── [slug]/page.tsx ← /blog/[slug]
```

**Benefit:** Clear separation. No accidental routes.

## Pages Router File Naming

Pages Router treats every `.tsx` file in `pages/` as a route (except `_` prefix).

| File Name | Route | Notes |
|-----------|-------|-------|
| `index.tsx` | `/` | Homepage |
| `about.tsx` | `/about` | Direct mapping |
| `[slug].tsx` | `/[slug]` | Dynamic route |
| `_app.tsx` | N/A | Global wrapper |
| `_document.tsx` | N/A | HTML customization |

**Rule:** All non-underscore files become routes. File name = URL path.

**Limitation:** Components cannot live in `pages/` without becoming routes. Must use separate `components/` directory.

## App Router Data Fetching

App Router uses async React Server Components. No special export functions required.

```tsx
// app/blog/page.tsx
import {sanityFetch} from '@/lib/sanity'
export default async function BlogPage(){
  const posts=await sanityFetch({query:postsQuery})
  return <BlogList posts={posts}/>
}
```

**Pattern:** Pages are async functions. Data fetched in component body.

**Static generation with generateStaticParams:**

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams(){
  const s=await client.fetch(allSlugsQuery)
  return s.map(({slug})=>({slug}))
}
export default async function Post({params}){
  const p=await sanityFetch({query:postBySlugQuery,params:{slug:params.slug}})
  if(!p)notFound()
  return <PostContent post={p}/>
}
```

**Benefit:** Collocates data fetching with component logic.

**Adoption:** 20 async page components (helix: 9, policy-node: 11). 6 generateStaticParams implementations.

## Pages Router Data Fetching

Pages Router requires special export functions for data fetching. Data passed as props.

```tsx
// pages/index.tsx
import {GetStaticProps} from 'next'
export default function HomePage({pageData}){
  return <PageContent data={pageData}/>
}
export const getStaticProps:GetStaticProps=async()=>{
  const pageData=await fetchPageData()
  return {props:{pageData},revalidate:60}
}
```

**Pattern:** Separate data fetching function exports props. Component receives at runtime.

**Adoption:** 8 instances of getStaticProps/getServerSideProps in kariusdx.

## Data Fetching Comparison

| Feature | App Router | Pages Router |
|---------|-----------|--------------|
| **Syntax** | Async function | Export special function |
| **Collocation** | Data + component together | Separated |
| **Type safety** | Automatic | Manual prop types |
| **Streaming** | Supported (Suspense) | Not supported |

## App Router Nested Layouts

App Router supports nested layouts that wrap child routes automatically. Layouts persist across route changes (no re-render).

```tsx
// app/layout.tsx
export default function RootLayout({children}){
  return(
    <html lang="en">
      <body>
        <SiteHeader/>
        {children}
        <SiteFooter/>
      </body>
    </html>
  )
}
// app/resources/[slug]/layout.tsx
export default function ResourceLayout({children}){
  return(
    <div className="resource-wrapper">
      <ResourceSidebar/>
      {children}
    </div>
  )
}
```

**Pattern:** Each layout wraps children. Layouts compose automatically based on route hierarchy.

**Benefit:** Shared UI doesn't re-render when navigating between sibling routes.

**Adoption:** 100% of App Router projects use nested layouts (helix: 3, policy-node: 2).

## Pages Router Global Layout

Pages Router has single global `_app.tsx` for layouts. Per-route layouts require manual composition.

```tsx
// pages/_app.tsx
import Layout from 'components/Layout'
export default function MyApp({Component,pageProps}){
  return(
    <Layout globalData={pageProps.globalData}>
      <Component {...pageProps}/>
    </Layout>
  )
}
```

**Pattern:** Single `<Layout>` component wraps all pages. No automatic nesting.

**Limitation:** Per-route layouts require conditional logic or HOC composition:

```tsx
export default function BlogPage(props){
  return(
    <BlogLayout>
      <BlogContent {...props}/>
    </BlogLayout>
  )
}
```

**Comparison:** App Router layouts persist and compose automatically. Pages Router requires manual management.

## App Router Metadata API

App Router provides type-safe Metadata API for SEO, social sharing, and document head management.

```tsx
// app/layout.tsx
import type {Metadata} from 'next'
export const metadata:Metadata={
  title:{template:'%s | Helix',default:'Helix'},
  description:'...',
  metadataBase:new URL('https://helix.com'),
}
```

**Dynamic metadata with generateMetadata:**

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata({params}):Promise<Metadata>{
  const p=await sanityFetch({query,params})
  return{title:p.title,description:p.excerpt,openGraph:{images:[p.coverImage]}}
}
```

**Pattern:** Static metadata in `layout.tsx`, dynamic in `page.tsx` via async function.

**Benefit:** Type-safe, no runtime overhead, automatic deduplication, streaming support.

**Adoption:** 100% of App Router projects (helix: 1 static, policy-node: 1 dynamic).

## Pages Router SEO Libraries

Pages Router requires external library (next-seo) for metadata management.

```tsx
// pages/_app.tsx
import {DefaultSeo} from 'next-seo'
<DefaultSeo title="Site Title" description="..." openGraph={{...}}/>

// pages/index.tsx
import {NextSeo} from 'next-seo'
<NextSeo title="Page Title" description="..."/>
```

**Pattern:** Component-based SEO requires rendering `<NextSeo>` in every page. Adds runtime overhead.

**Adoption:** 100% of Pages Router projects use next-seo library.

**Comparison:** App Router metadata is build-time static exports. Pages Router SEO is runtime components with larger bundle.

## API Routes

### App Router: Route Handlers

App Router API routes use `route.ts` files with named HTTP method exports.

```tsx
// app/api/cache/route.ts (helix pattern)
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const cacheKey = searchParams.get('key')

  return Response.json({ status: 'ok', key: cacheKey })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  return Response.json({ received: body })
}
```

**Pattern:** File named `route.ts` exports HTTP method functions (GET, POST, PUT, DELETE). Uses standard Request/Response APIs.

**Adoption:** 9 API route handlers (helix: 2, policy-node: 7).

### Pages Router: API Routes

Pages Router API routes export handler function in `pages/api/` directory.

```tsx
// pages/api/endpoint.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'GET') {
    res.status(200).json({ name: 'John' })
  }
}
```

**Pattern:** Single default export handler. Manual method checking via `req.method`.

**Comparison:** App Router uses named exports per method (clearer separation). Pages Router uses conditional logic.

## File-Based Conventions Summary

**App Router special files:**
- `layout.tsx` - Shared UI for route segment
- `page.tsx` - Route page (required for public route)
- `loading.tsx` - Loading UI (Suspense boundary)
- `error.tsx` - Error boundary
- `not-found.tsx` - 404 page
- `route.ts` - API route handler

**Pages Router special files:**
- `_app.tsx` - Global app wrapper
- `_document.tsx` - HTML document customization
- `404.tsx` - Custom 404 page
- `500.tsx` - Custom error page
- Any other `.tsx` file = route

**Naming comparison:**

| Purpose | App Router | Pages Router |
|---------|-----------|--------------|
| Homepage | `app/page.tsx` | `pages/index.tsx` |
| About page | `app/about/page.tsx` | `pages/about.tsx` |
| Dynamic route | `app/blog/[slug]/page.tsx` | `pages/blog/[slug].tsx` |
| API route | `app/api/users/route.ts` | `pages/api/users.ts` |
| Global layout | `app/layout.tsx` | `pages/_app.tsx` |
| 404 page | `app/not-found.tsx` | `pages/404.tsx` |

## When to Use Each Router

### Use App Router When:
- Starting new Next.js project (v13+)
- Need nested layouts and route groups
- Want streaming and Suspense
- Prefer async server components
- Need built-in metadata management

### Use Pages Router When:
- Maintaining legacy project (v12 or earlier)
- Team not ready for architecture migration
- Relying on Pages Router-specific libraries
- Simpler routing model preferred

**Recommendation:** Migrate to App Router for new features and long-term support. Pages Router enters maintenance mode.

## Adoption Statistics

**Cross-project adoption:**

| Project | Next.js Version | Router Type | Status |
|---------|----------------|-------------|--------|
| helix-dot-com-next | 15.0.3 | App Router | ✅ Fully migrated |
| policy-node | 14.0.0 | App Router | ✅ Fully migrated |
| kariusdx-next | 12.3.4 | Pages Router | ⚠️ Needs migration |

**Overall adoption:** 67% App Router, 33% Pages Router.

**Recommendation:** Migrate kariusdx to App Router for modern features and continued Next.js support.

## Related Patterns

- **Route Groups:** See `route-groups-organization.md` for App Router organization patterns
- **Nested Layouts:** See `nested-layouts-pattern.md` for layout composition details
- **Metadata API:** See `metadata-api-usage.md` for SEO and metadata patterns
- **Migration Guide:** See `migration-pages-to-app-router.md` for migration steps
