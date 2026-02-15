---
title: "Projection and Query Composition"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "projection", "composition", "template-interpolation", "modular-queries"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Projection and Query Composition

## Overview

GROQ template interpolation (`${}`) enables modular query composition by injecting reusable partials and helper fragments into queries. All three analyzed projects use this pattern extensively: helix (48 instances), kariusdx (66 instances), and ripplecom (40+ estimated instances). Total of 150+ interpolations across 51 query files demonstrate universal adoption (100%) for composing complex queries from smaller, maintainable pieces.

## Pattern Adoption

**Adoption Rate:** 100% (3 of 3 repositories)

- **Helix (v3)**: 48 projection instances
- **Kariusdx (v2)**: 66 projection instances (highest usage)
- **Ripplecom (v4)**: Estimated 40+ instances (uses partials extensively)

**Average:** 3 projections per query file for modular composition.


## Simple Partial Interpolation

Template interpolation injects partial query fragments into larger queries.

**Partial definition:**
```typescript
// partials/imgReference.ts
const imgReference = `
{
  url,
  'width': metadata.dimensions.width,
  'height': metadata.dimensions.height
}
`
export default imgReference
```

**Query with interpolation:**
```typescript
import { groq } from 'next-sanity'
import imgReference from './partials/imgReference'

const pageQuery = groq`
  *[_type == "page"][0] {
    title,
    'heroImage': heroImage.asset->${imgReference}
  }
`
```

**Compiled GROQ (what Sanity receives):**
```groq
*[_type == "page"][0] {
  title,
  'heroImage': heroImage.asset->{
    url,
    'width': metadata.dimensions.width,
    'height': metadata.dimensions.height
  }
}
```

**Benefits:**
- Reusable across queries
- Single source of truth for image expansion
- Easy to update globally (modify partial, all queries updated)


## Kariusdx Pattern (Composed Query with Multiple Partials)

Kariusdx composes queries from multiple partials for maximum reusability.

**Partials:**
```typescript
// partials/globalData.ts
const globalData = `'globalData': *[_type == 'siteSettings'][0]{...}`

// partials/seoData.ts
const seoData = `'seo': {metaTitle, metaDescription, ...}`

// partials/breadcrumbs.ts
const breadcrumbsQueryString = (slug: string[]) => `'breadcrumbs': [...]`

// partials/imgReferenceExpansion.ts
const imgReferenceExpansion = `{..., 'width': metadata.dimensions.width, ...}`
```

**Composed query:**
```typescript
import { groq } from 'next-sanity'
import globalData from './partials/globalData'
import seoData from './partials/seoData'
import breadCrumbsQueryString from './helpers/breadCrumbsQueryString'
import imgReferenceExpansion from './partials/imgReferenceExpansion'

const pageQuery = (slug: string[]) => groq`
{
  ${globalData},
  ${breadCrumbsQueryString(slug)},
  "pageData": *[_type == 'page' && path == "${slug}"][0]{
    ...,
    "heroImage": heroImage.asset->${imgReferenceExpansion},
    ${seoData}
  },
}
`
export default pageQuery
```

**Result:** Single query fetches global data, breadcrumbs, page content, hero image, and SEO metadata - all composed from reusable partials.

**Observation:** Kariusdx averages 4 partial interpolations per query (highest of all projects).


## Dynamic Query Fragments Based on Route

Kariusdx uses helper functions to conditionally include query fragments based on route parameters.

**Helper with conditional logic:**
```typescript
// helpers/clinicalDataQueryString.ts
export const clinicalDataQueryString = (slug: string[]) => (
  slug.includes('clinical-data')
    ? `"clinicalData": *[_type == 'clinicalData'][0]{
        trials[]{title, status, enrolling},
        publications[]{title, journal, year}
      }`
    : ''
)
```

**Usage in composed query:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  "pageData": *[_type == 'page'][0]{
    title,
    ${clinicalDataQueryString(slug)}
  }
}
`
```

**Behavior:**
- If slug includes `'clinical-data'`, fetches clinical trials and publications
- Otherwise, empty string (omitted from query)

**Result:** Route-specific data fetching without separate query files.


## Ripplecom Pattern (Content Array with Nested Projections)

Ripplecom uses partials within content array expansions for polymorphic content blocks.

**Partials:**
```typescript
// partials/richText.ts
export const richTextContentGroq = `
  ...,
  _type == 'image' => {
    asset-> {url, metadata.dimensions},
    alt
  },
  _type == 'callout' => {
    icon,
    message
  }
`

// partials/seo.ts
const seoGroq = `metaTitle, metaDescription, ogImage{...}`
```

**Composed query with nested projections:**
```typescript
import { defineQuery } from "next-sanity"
import { richTextContentGroq } from "./partials/richText"
import seoGroq from "./partials/seo"

export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    _id,
    title,
    content[] {
      ...,
      _type == "textSection" => {
        ...,
        content {
          ${richTextContentGroq}
        }
      },
      _type == "heroSection" => {
        ...,
        'backgroundImage': image.asset->{url}
      }
    },
    seo {
      ${seoGroq}
    }
  }
`)
```

**Benefit:** Handles polymorphic content blocks (textSection, heroSection) with partial interpolation for repeated patterns (richText, seo).


## Dynamic Partial with Parameters

Kariusdx uses parameterized helpers for flexible query fragments.

**Parameterized helper:**
```typescript
// helpers/recentNewsGroq.ts
export const recentNewsGroq = (startCount = 0, endCount = 5) => `
  *[_type == 'news']|order(newsDate desc)[${startCount}..${endCount}]{
    ...,
    "featuredImage": featuredImage.image.asset->${imgReferenceExpansion}
  }
`
```

**Usage with different parameters:**
```typescript
const homepageQuery = groq`
{
  "latestNews": ${recentNewsGroq(0, 3)},
  "archive": ${recentNewsGroq(3, 10)}
}
`
```

**Result:**
- `latestNews`: First 3 news items
- `archive`: Next 7 news items

**Benefit:** Single helper function with parameters for flexible pagination.


## Site-Wide Data Composition

Kariusdx pattern for including global site data in every query.

**Global data partial:**
```typescript
// partials/globalData.ts
const globalData = `
  'globalData': *[_type == 'siteSettings'][0]{
    siteName,
    siteUrl,
    contactEmail,
    socialLinks[]{platform, url},
    footer{copyrightText, links[]{text, url}}
  }
`
export default globalData
```

**Included in all page queries:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  ${globalData},
  "pageData": *[_type == 'page'][0]{...}
}
`
```

**Benefit:** Every query fetches site settings (header, footer, contact info) without repetition.

**Observation:** Global data projection appears in 100% of kariusdx queries (17 files).


## Helix Pattern (Inline Projections)

Helix uses fewer partials (3 vs 4-6 in other projects) and more inline projections.

**Helix query (inline-heavy):**
```typescript
const pageByPathQuery = groq`
  *[_type == "page" && slug.current == $pagePath][0]{
    title,
    slug,
    'seo': seo {
      ...,
      'ogImage': ogImage.asset->${imgReference},
    },
    pageBuilder[] {
      ...,
      _type == 'accordion' => {
        ...,
        items[] {
          ...,
          'image': image.asset->${imgReference},
        }
      },
      _type == 'caseStudy' => {
        ...,
        fileDownload {
          'extension': asset->extension,
          'url': asset->url,
        },
      },
    },
  }
`
```

**Characteristics:**
- Large single queries (100-200 lines)
- Inline field expansions for content blocks
- Only common patterns extracted to partials (image, link, teaser)

**Trade-offs:**
- **Pros:** Entire query visible in one file, easier to debug single queries
- **Cons:** Less reusable, harder to maintain across multiple queries

## Kariusdx Pattern (Partial-Heavy)

Kariusdx extracts more patterns into partials/helpers (8 total).

**Characteristics:**
- Smaller query files (30-50 lines)
- Heavy use of composition (`${}`)
- Conditional fragments via helper functions

**Trade-offs:**
- **Pros:** Highly reusable, easier to maintain across 17 query files
- **Cons:** Query logic spread across multiple files, requires jumping between files

**Recommendation:** Use partials for patterns repeated 2+ times. Use inline projections for query-specific logic.


## Filtered Projections in Content Arrays

**Pattern: Filter content blocks by type within projection**

```typescript
const pageQuery = groq`
  *[_type == "page"][0] {
    'publishedBlocks': content[published == true]{
      ...,
      _type == 'textBlock' => {
        ${richTextExpansion}
      }
    }
  }
`
```

**Filters content array to only published blocks before expansion.**


## ❌ Over-Interpolation (Too Many Partials)

```typescript
// TOO GRANULAR
const title = `title`
const slug = `'slug': slug.current`
const id = `_id`

const query = groq`
  *[_type == "page"][0] {
    ${id},
    ${title},
    ${slug}
  }
`
```

**Problem:** Partials for single fields add complexity without benefit.

**Better:** Only extract repeated multi-field patterns.

## ❌ Circular Dependencies

```typescript
// partial1.ts
import partial2 from './partial2'
const partial1 = `{${partial2}}`

// partial2.ts
import partial1 from './partial1'  // ❌ Circular dependency
const partial2 = `{${partial1}}`
```

**Problem:** Circular imports break query composition.

**Better:** Use one-way dependency flow (partials → queries, not partials → partials).

## ❌ Mixing String Concatenation and Template Interpolation

```typescript
// INCONSISTENT
const query = groq`
  {
    ${globalData},
    "page": *[_type == 'page'][0]{` + pageFields + `}
  }
`
```

**Problem:** Mix of `${}` and string concatenation makes queries hard to read.

**Better:** Use consistent `${}` interpolation throughout.


## Projection Overhead

**Minimal:** Template interpolation is compile-time (no runtime cost).

**Example:**
```typescript
const query = groq`{ ${partial1}, ${partial2} }`
```

**Compiled before execution:**
```groq
{ ...partial1 content..., ...partial2 content... }
```

**No runtime interpolation - Sanity receives fully composed GROQ string.**

## Related Patterns

- **Reusable Query Partials** - See `reusable-query-partials.md` for partial creation patterns
- **Conditional Field Expansion** - See `conditional-field-expansion.md` for type-based projections
- **Query File Organization** - See `query-file-organization.md` for partial directory structure

## Summary

Template interpolation (`${}`) enables modular query composition with 100% adoption across 51 query files (150+ instances). Helix uses inline-heavy queries (48 interpolations, 12 files), while kariusdx uses partial-heavy composition (66 interpolations, 17 files). Extract patterns repeated 2+ times into partials. Use helpers for conditional query fragments based on route or parameters. Balance between inline clarity (helix) and reusable composition (kariusdx) based on project size and query complexity.
