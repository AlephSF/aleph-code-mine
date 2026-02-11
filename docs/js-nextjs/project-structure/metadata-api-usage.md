---
title: "Metadata API for SEO and Document Head Management"
category: "project-structure"
subcategory: "seo"
tags: ["metadata", "seo", "app-router", "head", "opengraph"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Metadata API for SEO and Document Head Management

## Overview

Next.js App Router provides built-in Metadata API for managing document head content (title, meta tags, Open Graph, Twitter cards). Helix uses static metadata export in root layout and dynamic `generateMetadata()` in pages (100% App Router adoption). Pages Router projects use external next-seo library instead.

**Benefits:** Type-safe metadata, automatic deduplication, streaming support, no runtime overhead, automatic Open Graph image generation.

**Pattern:** Static metadata in `layout.tsx`, dynamic metadata via `generateMetadata()` async function in `page.tsx`.

## Static Metadata in Layouts

Root layout defines site-wide default metadata using `metadata` export.

```tsx
// app/layout.tsx (helix pattern)
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    template: '%s | Helix',  // Page titles use this template
    default: 'Helix',        // Fallback when no page title
  },
  description: 'Helix is a population genomics company...',
  metadataBase: new URL('https://helix.com'),
  manifest: '/site.webmanifest',
  themeColor: '#ffffff',
}
```

**Pattern:** Static export named `metadata` of type `Metadata`. Defines sitewide defaults.

**Template:** `template` string uses `%s` placeholder replaced by page-specific title. `default` used when page doesn't provide title.

**Adoption:** 100% of App Router projects export metadata in root layout (helix: 1 static export).

## Dynamic Metadata with generateMetadata

Pages generate dynamic metadata by exporting async `generateMetadata()` function.

```tsx
// app/blog/[slug]/page.tsx (helix pattern)
import type { Metadata } from 'next'

export async function generateMetadata({ params }): Promise<Metadata> {
  const { slug } = params
  const post = await sanityFetch({
    query: postBySlugQuery,
    params: { slug },
  })

  if (!post) return {}  // Fallback to layout metadata

  return {
    title: post.title,                    // Replaces %s in template
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage?.url],
      type: 'article',
      publishedTime: post.publishedAt,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage?.url],
    },
  }
}

export default async function Page({ params }) {
  // Page component
}
```

**Pattern:** Async function receives route params, fetches data, returns metadata object.

**Type Safety:** Return type `Promise<Metadata>` provides autocomplete and validation.

**Fallback:** Return empty object `{}` to use parent layout metadata.

**Adoption:** 100% of App Router projects with dynamic routes use generateMetadata (helix: 1 implementation, policy-node: 1 implementation).

## Metadata Fields Reference

**Core fields:**
- `title` - Page title (string or `{ template, default, absolute }`)
- `description` - Meta description
- `keywords` - SEO keywords array
- `authors` - Author information
- `creator` - Content creator
- `publisher` - Publisher name

**Open Graph fields:**
- `openGraph.title` - OG title
- `openGraph.description` - OG description
- `openGraph.images` - OG image array
- `openGraph.type` - Content type (website, article, etc.)
- `openGraph.url` - Canonical URL
- `openGraph.siteName` - Site name

**Twitter fields:**
- `twitter.card` - Card type (summary, summary_large_image, etc.)
- `twitter.site` - @username for website
- `twitter.creator` - @username for content creator
- `twitter.images` - Twitter card images

**Technical fields:**
- `metadataBase` - Base URL for relative paths
- `manifest` - Web app manifest path
- `themeColor` - Theme color for browser UI
- `viewport` - Viewport configuration
- `robots` - Robot directives
- `alternates` - Alternate URLs (i18n, canonical)

## Metadata Base URL

`metadataBase` defines base URL for all relative metadata URLs.

```tsx
export const metadata: Metadata = {
  metadataBase: new URL('https://helix.com'),
  openGraph: {
    images: '/og-image.png',  // Resolves to https://helix.com/og-image.png
  },
}
```

**Pattern:** Set once in root layout. All child metadata inherits base URL.

**Benefit:** Relative URLs in metadata resolve correctly without manual concatenation.

## Title Templates

Title template allows consistent page title formatting across site.

```tsx
// app/layout.tsx
export const metadata = {
  title: {
    template: '%s | Helix',
    default: 'Helix',
  },
}

// app/about/page.tsx
export const metadata = {
  title: 'About Us',  // Renders as "About Us | Helix"
}

// app/contact/page.tsx
export const metadata = {
  title: 'Contact',  // Renders as "Contact | Helix"
}
```

**Pattern:** Template in layout, title strings in pages. `%s` replaced by page title.

**Absolute titles:** Use `title: { absolute: 'Full Title' }` to bypass template.

## Metadata Inheritance and Merging

Metadata cascades from root layout to page with automatic merging.

**Layout hierarchy:**
```tsx
// app/layout.tsx (root)
export const metadata = {
  title: { template: '%s | Site', default: 'Site' },
  description: 'Default description',
}

// app/blog/layout.tsx (nested)
export const metadata = {
  openGraph: { type: 'website' },
}

// app/blog/[slug]/page.tsx
export const metadata = {
  title: 'Post Title',  // Uses root template
  openGraph: { type: 'article' },  // Overrides nested layout
}
```

**Result:** Final metadata merges all layers. Child metadata overrides parent where conflicts exist.

## Metadata for API Routes

API routes can export metadata for API documentation or RSS feeds.

```tsx
// app/api/feed/route.ts
export const metadata = {
  title: 'RSS Feed',
  alternates: {
    types: {
      'application/rss+xml': '/feed.xml',
    },
  },
}
```

**Pattern:** Same `metadata` export syntax. Useful for discoverable APIs.

**Adoption:** 0% in analyzed projects (API routes don't use metadata export).

## Robots and Indexing

Control search engine indexing via `robots` metadata field.

```tsx
export const metadata = {
  robots: {
    index: true,
    follow: true,
    nocache: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}
```

**Pattern:** Granular control per bot. Renders appropriate meta tags.

**Common patterns:**
- Production: `index: true, follow: true`
- Staging: `index: false, follow: false`
- Private pages: `index: false, follow: false`

## App Router vs Pages Router Metadata

### App Router: Built-in Metadata API

```tsx
export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Description',
}
```

**Benefits:** Type-safe, build-time, no dependencies, automatic deduplication.

### Pages Router: next-seo Library

```tsx
import { NextSeo } from 'next-seo'

<NextSeo
  title="Page Title"
  description="Description"
  openGraph={{ title: 'Page Title' }}
/>
```

**Limitations:** Runtime component, requires npm package, larger bundle, manual deduplication.

**Recommendation:** Migrate to Metadata API when adopting App Router. Remove next-seo dependency.

## Adoption Statistics

**Metadata patterns:**

| Project | Router | Metadata Method | Static | Dynamic |
|---------|--------|----------------|---------|---------|
| **helix** | App Router | Metadata API | ✅ Root layout | ✅ generateMetadata |
| **policy-node** | App Router | Metadata API | ❌ No static | ✅ generateMetadata |
| **kariusdx** | Pages Router | next-seo | ✅ DefaultSeo | ✅ NextSeo per page |

**App Router metadata adoption:** 100% use Metadata API.

**Pages Router SEO adoption:** 100% use next-seo library.

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for router comparison
- **generateMetadata:** See Next.js docs for advanced metadata patterns
- **Open Graph:** See OG spec for social sharing metadata
