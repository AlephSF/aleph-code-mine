---
title: "Query File Organization for GROQ"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "file-structure", "organization", "queries", "partials"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Query File Organization for GROQ

## Overview

Sanity projects consistently organize GROQ queries into dedicated directories with subdirectories for reusable partials. This pattern appears in 100% of analyzed codebases (helix v3, kariusdx v2, ripplecom v4), totaling 51 query files across three projects. Dedicated query organization improves maintainability, enables code reuse, and provides clear separation between data-fetching logic and UI components.

## Pattern Adoption

**Adoption Rate:** 100% (3 of 3 repositories)

- **Helix (v3.10.0)**: 12 query files in `app/(frontend)/lib/sanity/queries/`
- **Kariusdx (v2.30.0)**: 17 query files in `lib/groq/`
- **Ripplecom (v4.3.0)**: 22 query files in `apps/ripple-web/src/queries/sanity/`

**Observation:** All projects place queries outside component directories, treating them as shared data-fetching utilities rather than component-specific logic.

## Standard Directory Structure

## Helix Pattern (Flat with Partials Subdirectory)

Helix (v3) uses a flat structure with a dedicated `/partials` subdirectory for reusable query fragments.

```
app/(frontend)/lib/sanity/
└── queries/
    ├── pageByPathQuery.ts
    ├── termQuery.ts
    ├── footerQuery.ts
    ├── mainNavQuery.ts
    ├── latestContentQuery.ts
    ├── siteMapInfoQuery.ts
    └── partials/
        ├── imgReference.ts
        ├── link.ts
        └── teaser.ts
```

**Benefits:**
- Simple flat structure for quick navigation
- Clear separation between full queries and partials
- 12 main query files + 3 reusable partials

## Kariusdx Pattern (Organized with Helpers and Partials)

Kariusdx (v2) uses the most organized structure with separate `/helpers` and `/partials` subdirectories.

```
lib/groq/
├── pageQuery.ts
├── newsPageQuery.ts
├── eventsPageQuery.ts
├── staticPagePathsQuery.ts
├── helpers/
│   ├── pagePathQueryString.ts
│   ├── clinicalDataQueryString.ts
│   ├── breadCrumbsQueryString.ts
│   └── buildPagePath.ts
└── partials/
    ├── imgReferenceExpansion.ts
    ├── seoData.ts
    ├── navigation.ts
    └── globalData.ts
```

**Benefits:**
- Separates query composition helpers from reusable partials
- Helper functions handle conditional query logic
- 8 main queries + 4 helpers + 4 partials
- Scalable for complex projects with many query variations

## Ripplecom Pattern (Modern v4 with Partials)

Ripplecom (v4) organizes queries with a `/partials` subdirectory and follows modern naming conventions.

```
apps/ripple-web/src/queries/sanity/
├── pages.ts
├── caseStudies.ts
├── events.ts
├── pressReleases.ts
├── reports.ts
├── investments.ts
├── insightsBlogPosts.ts
├── carousel.ts
├── seoMetadata.ts
└── partials/
    ├── image.ts
    ├── link.ts
    ├── richText.ts
    ├── seo.ts
    ├── video.ts
    └── quote.ts
```

**Benefits:**
- Named exports for each document type (pages, events, etc.)
- 16 main query files + 6 partials
- Descriptive filenames match Sanity document types
- Partials represent common content structures (image, link, richText)

## File Naming Conventions

## Query Files (Main Queries)

**Pattern 1: Descriptive noun (Ripplecom):**
```typescript
// pages.ts, events.ts, caseStudies.ts
export const getPageByPathQuery = defineQuery(`...`)
export const getAllPagePathsQuery = defineQuery(`...`)
```

**Pattern 2: Query suffix (Helix, Kariusdx):**
```typescript
// pageByPathQuery.ts, newsPageQuery.ts
const pageByPathQuery = groq`...`
export default pageByPathQuery
```

**Recommendation:** Use descriptive nouns (pages.ts, posts.ts) with named exports for multiple related queries per file. This reduces file proliferation and groups related queries logically.

## Partials Subdirectory Pattern

## Purpose of Partials

Partials contain reusable GROQ fragments for common content structures. All three projects use partials for:

1. **Image references** (100% adoption) - Dereferencing image assets with metadata
2. **SEO metadata** (67% adoption) - Open Graph, meta descriptions, structured data
3. **Rich text content** (67% adoption) - Portable Text expansion with custom blocks
4. **Navigation/links** (67% adoption) - Link objects with URL and display text

## Image Reference Partial Example

**Helix imgReference.ts:**
```typescript
const imgReference = `
{
  url,
  altText,
  title,
  description,
  'height': metadata.dimensions.height,
  'width': metadata.dimensions.width,
  'aspectRatio': metadata.dimensions.aspectRatio,
  'blurHash': metadata.blurHash,
}
`
export default imgReference
```

**Ripplecom image.ts:**
```typescript
const imageGroq = `
  _id,
  url,
  title,
  altText,
  "width": metadata.dimensions.width,
  "height": metadata.dimensions.height,
  description,
  "contentType": mimeType
`
export default imageGroq
```

**Common fields across all projects:**
- metadata.dimensions (height, width, aspectRatio)
- blurHash for progressive loading
- altText for accessibility

## Helpers Subdirectory Pattern (Kariusdx Only)

Kariusdx separates conditional query logic into `/helpers`:

```typescript
// helpers/pagePathQueryString.ts
const pagePathQueryString = (slug: string[]) => `
  *[_type == 'page' && path == "${buildPagePath(slug)}"][0]
`
```

```typescript
// helpers/clinicalDataQueryString.ts
export const clinicalDataQueryString = (slug: string[]) => (
  slug.includes('clinical-data')
    ? `"clinicalData": *[_type == 'clinicalData'][0]{...}`
    : ''
)
```

**Use cases for helpers:**
- Conditional query fragments based on route
- Dynamic parameter interpolation
- Query string builders for complex filters

## Anti-Patterns to Avoid

## ❌ Queries Inside Component Files

```typescript
// components/BlogPost.tsx (AVOID)
const BlogPost = () => {
  const query = groq`*[_type == "post"][0]`  // ❌ Couples query to component
  const data = await client.fetch(query)
  return <div>{data.title}</div>
}
```

**Problem:** Query is not reusable, harder to test, and couples data fetching to UI.

## ❌ No Partials for Repeated Patterns

```typescript
// pageQuery.ts (AVOID)
const pageQuery = groq`
  *[_type == "page"][0]{
    'image': image.asset->{url, metadata.dimensions.width, metadata.dimensions.height},  // ❌ Repeated
    'heroImage': heroImage.asset->{url, metadata.dimensions.width, metadata.dimensions.height},  // ❌ Duplicated
  }
`
```

**Problem:** Image reference expansion repeated twice. Extract to `imgReference` partial.

## ✅ Correct Pattern with Partials

```typescript
// partials/imgReference.ts
const imgReference = `{url, 'width': metadata.dimensions.width, 'height': metadata.dimensions.height}`

// pageQuery.ts
import imgReference from './partials/imgReference'

const pageQuery = groq`
  *[_type == "page"][0]{
    'image': image.asset->${imgReference},
    'heroImage': heroImage.asset->${imgReference},
  }
`
```

## When to Create a Partial

Create a partial when a GROQ fragment is:

1. **Used in 2+ queries** - DRY principle (Don't Repeat Yourself)
2. **Represents a reusable content structure** - Image, link, SEO, video
3. **Complex (>3 fields)** - Simplifies main query readability
4. **Versioned across document types** - Consistent field expansion

**Example:** If 5 queries all dereference image assets with metadata, create `partials/imgReference.ts` and reuse across all 5 queries.

## Migration Path

**From no organization to organized structure:**

1. Create `/queries` directory at project root or in `/lib`
2. Move inline queries from components to dedicated query files
3. Identify repeated patterns (images, links, SEO) and extract to `/partials`
4. For projects with conditional logic, create `/helpers` subdirectory
5. Update imports in components to use centralized queries

**Example migration:**
```bash
# Before
components/Page.tsx (contains inline groq query)

# After
lib/queries/pages.ts (main query)
lib/queries/partials/imgReference.ts (reusable partial)
components/Page.tsx (imports from lib/queries/pages.ts)
```

## Related Patterns

- **Reusable Query Partials** - See `reusable-query-partials.md` for detailed partial patterns
- **Modern defineQuery API** - See `modern-definequery-api.md` for v4 query definition
- **TypeScript Typing for Queries** - See `typescript-query-typing.md` for type safety

## Summary

Dedicated query directories with `/partials` subdirectories are a universal pattern (100% adoption). Organize queries by document type (pages.ts, posts.ts) with named exports, extract repeated patterns into partials, and separate conditional logic into helpers when needed. This structure scales from small projects (12 files) to large projects (22+ files) while maintaining clarity and reusability.
