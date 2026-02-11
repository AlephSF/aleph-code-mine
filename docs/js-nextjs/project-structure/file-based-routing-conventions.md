---
title: "File-Based Routing Conventions: Special Files Quick Reference"
category: "project-structure"
subcategory: "routing"
tags: ["routing", "file-conventions", "app-router", "pages-router"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# File-Based Routing Conventions: Special Files Quick Reference

## Overview

Next.js uses file-based routing where file names and folder structure determine URL paths and routing behavior. App Router (Next.js 13+) uses special file names (`page.tsx`, `layout.tsx`) for specific routing features. Pages Router (Next.js 12) treats any file in `pages/` as a route except those prefixed with underscore.

**Key Difference:** App Router requires `page.tsx` to create public route. Pages Router treats all files as routes by default.

**Adoption:** 67% App Router (helix, policy-node), 33% Pages Router (kariusdx).

## App Router Special Files

App Router reserves specific file names for routing behavior. All other file names ignored for routing.

| File Name | Purpose | Required | Example |
|-----------|---------|----------|---------|
| `page.tsx` | Route page (makes folder publicly accessible) | Yes for routes | `app/about/page.tsx` → `/about` |
| `layout.tsx` | Shared UI that wraps child routes | No | Root layout, nested layouts |
| `not-found.tsx` | 404 page for route segment | No | Custom 404 UI |
| `error.tsx` | Error boundary for route segment | No | Error handling |
| `loading.tsx` | Loading UI with Suspense | No | Streaming fallback |
| `route.ts` | API route handler | Yes for APIs | HTTP method exports |
| `template.tsx` | Re-rendered layout (vs persistent layout) | No | Animation layouts |
| `default.tsx` | Fallback for parallel routes | No | Parallel route defaults |

**Rule:** Only `page.tsx` or `route.ts` makes folder publicly accessible. Other files provide routing features.

## Pages Router Special Files

Pages Router treats files starting without underscore as routes. Files starting with `_` are special.

| File Name | Purpose | Route |
|-----------|---------|-------|
| `index.tsx` | Homepage | `/` |
| `about.tsx` | About page | `/about` |
| `[slug].tsx` | Dynamic route | `/[slug]` |
| `[...slug].tsx` | Catch-all route | `/path/to/anything` |
| `_app.tsx` | Global app wrapper | N/A (special) |
| `_document.tsx` | HTML document customization | N/A (special) |
| `404.tsx` | Custom 404 page | Fallback |
| `500.tsx` | Custom error page | Fallback |

**Rule:** Any `.tsx` file without leading underscore becomes route. File name determines URL.

## Dynamic Routes

Both routers support dynamic route segments using square brackets.

### Single Dynamic Segment

```
# App Router
app/blog/[slug]/page.tsx  → /blog/[slug]

# Pages Router
pages/blog/[slug].tsx     → /blog/[slug]
```

**Usage:**
```tsx
// App Router
export default async function Page({ params }) {
  const { slug } = params  // Type-safe params
}

// Pages Router
export default function Page({ slug }) {  // From getStaticProps
}
```

### Catch-All Routes

```
# App Router
app/docs/[...slug]/page.tsx   → /docs/a, /docs/a/b, /docs/a/b/c

# Pages Router
pages/docs/[...slug].tsx      → /docs/a, /docs/a/b, /docs/a/b/c
```

**Pattern:** Three dots `...` before parameter name enables catch-all matching.

### Optional Catch-All Routes

```
# App Router only
app/shop/[[...slug]]/page.tsx  → /shop, /shop/a, /shop/a/b

# Not available in Pages Router
```

**Pattern:** Double brackets `[[...slug]]` makes catch-all optional. Matches parent route too.

## URL to File Mapping

### App Router Mapping

| File Path | URL | Notes |
|-----------|-----|-------|
| `app/page.tsx` | `/` | Homepage |
| `app/about/page.tsx` | `/about` | Static route |
| `app/blog/[slug]/page.tsx` | `/blog/[slug]` | Dynamic route |
| `app/[[...slug]]/page.tsx` | Any path | Optional catch-all |
| `app/api/users/route.ts` | `/api/users` | API route |
| `app/(group)/page.tsx` | `/` | Route group (no URL segment) |

**Rule:** Only folders with `page.tsx` create routes. Folder structure = URL structure (except route groups).

### Pages Router Mapping

| File Path | URL | Notes |
|-----------|-----|-------|
| `pages/index.tsx` | `/` | Homepage |
| `pages/about.tsx` | `/about` | File name = URL |
| `pages/blog/[slug].tsx` | `/blog/[slug]` | Dynamic route |
| `pages/[...slug].tsx` | Any path | Catch-all |
| `pages/api/users.ts` | `/api/users` | API route |

**Rule:** File name (minus extension) becomes URL segment. No `index` in URL for `index.tsx`.

## Route Priority

When multiple routes could match URL, Next.js uses priority order:

1. **Static routes** (highest priority)
2. **Dynamic routes with single segment** `[slug]`
3. **Catch-all routes** `[...slug]` or `[[...slug]]` (lowest priority)

**Example:**
```
app/blog/post/page.tsx       → /blog/post (matches first - static)
app/blog/[slug]/page.tsx     → /blog/[slug] (matches if not /blog/post)
app/blog/[...slug]/page.tsx  → /blog/anything/else (matches last)
```

**Recommendation:** Use specific static routes when possible. Catch-all routes should be last resort.

## API Routes

Both routers support API routes with different conventions.

### App Router API Routes

```
app/api/users/route.ts
```

**Pattern:** File named `route.ts` exports HTTP method functions.

```tsx
export async function GET(request: Request) {
  return Response.json({ users: [] })
}

export async function POST(request: Request) {
  const body = await request.json()
  return Response.json({ created: body })
}
```

**Methods:** GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.

### Pages Router API Routes

```
pages/api/users.ts
```

**Pattern:** Default export handler function with method checking.

```tsx
export default function handler(req, res) {
  if (req.method === 'GET') {
    res.status(200).json({ users: [] })
  }
}
```

**Comparison:** App Router uses named exports per method. Pages Router uses conditional logic.

## Nested Routes

App Router supports nested routing with automatic layout composition.

```
app/
└── dashboard/
    ├── layout.tsx           ← Dashboard layout
    ├── page.tsx             ← /dashboard
    └── settings/
        └── page.tsx         ← /dashboard/settings (inherits layout)
```

**Pattern:** Layouts nest automatically. Child routes wrapped by parent layouts.

Pages Router requires manual layout composition or HOCs for nested layouts.

## Parallel Routes (App Router Only)

App Router supports parallel routes using `@folder` syntax for simultaneous page rendering.

```
app/
└── dashboard/
    ├── @analytics/
    │   └── page.tsx         ← Renders in {analytics} slot
    ├── @team/
    │   └── page.tsx         ← Renders in {team} slot
    └── layout.tsx           ← Defines {analytics} and {team} slots
```

**Pattern:** Folders prefixed with `@` are parallel routes, not URL segments.

**Adoption:** 0% in analyzed projects. Advanced pattern for split views, modals.

## Intercepting Routes (App Router Only)

App Router supports route interception using `(..)folder` syntax for modals and overlays.

```
app/
└── photos/
    ├── [id]/
    │   └── page.tsx         ← /photos/[id] (full page)
    └── (..)photos/
        └── [id]/
            └── page.tsx     ← Intercepts /photos/[id] (modal)
```

**Pattern:** Parentheses with dots `(..)` intercept routes for modal overlay.

**Adoption:** 0% in analyzed projects. Advanced pattern for modal overlays.

## Route Metadata Files

App Router supports static metadata files for icons, sitemaps, robots.

| File Name | Purpose | Auto-served |
|-----------|---------|-------------|
| `favicon.ico` | Favicon | `/favicon.ico` |
| `icon.png` | App icon | `/icon.png` |
| `apple-icon.png` | Apple touch icon | `/apple-icon.png` |
| `opengraph-image.png` | OG image | `/opengraph-image.png` |
| `robots.txt` | Robots file | `/robots.txt` |
| `sitemap.xml` | Sitemap | `/sitemap.xml` |

**Pattern:** Place in `app/` directory. Next.js serves automatically at root path.

**Adoption:** 100% of App Router projects use static metadata files (helix has favicon, icon, apple-icon in app/).

## File Convention Quick Reference

**App Router must-know files:**
- `page.tsx` - Route page (required for public route)
- `layout.tsx` - Shared UI wrapper
- `route.ts` - API route handler

**Pages Router must-know files:**
- `index.tsx` - Homepage
- `_app.tsx` - Global wrapper
- `[param].tsx` - Dynamic route

**Dynamic routing:**
- `[slug]` - Single segment
- `[...slug]` - Catch-all
- `[[...slug]]` - Optional catch-all (App Router only)

**Adoption statistics:**

| Pattern | helix | policy-node | kariusdx | Overall |
|---------|-------|-------------|----------|---------|
| App Router special files | ✅ 9 pages, 3 layouts | ✅ 11 pages, 2 layouts | ❌ N/A | 67% |
| Pages Router files | ❌ N/A | ❌ N/A | ✅ 7 pages, _app, _document | 33% |
| Dynamic routes | ✅ [[...slug]] | ✅ [lang], [...slug] | ✅ [...slug] | 100% |
| API routes | ✅ 2 route.ts | ✅ 7 route.ts | ❌ 0 | 67% |

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for router comparison
- **Route Groups:** See `route-groups-organization.md` for (groupName) syntax
- **Dynamic Routes:** See Next.js docs for advanced dynamic routing patterns
