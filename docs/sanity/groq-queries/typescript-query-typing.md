---
title: "TypeScript Typing for GROQ Queries"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "typescript", "type-safety", "auto-generation", "sanity-codegen"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# TypeScript Typing for GROQ Queries

## Overview

TypeScript typing for GROQ query results ensures type safety when consuming Sanity data in components. All three analyzed projects type their query results: ripplecom uses auto-generated types (v4 with defineQuery), while helix and kariusdx use manual type definitions (v2/v3 with groq template). Total of 51 query files with 100% TypeScript adoption demonstrate universal commitment to type safety.

## Pattern Adoption

**Adoption Rate:** 100% (3 of 3 repositories)

**Type Generation Approaches:**
- **Ripplecom (v4)**: Auto-generated types from `defineQuery()` (modern approach)
- **Helix (v3)**: Manual type definitions for query results (legacy approach)
- **Kariusdx (v2)**: Manual type definitions with helper types (legacy approach)

**Source Confidence:** 100% (all projects type query results)


## Modern Pattern with Type Generation

Ripplecom (v4) uses `defineQuery()` with automated type generation. The `@sanity/codegen` CLI generates TypeScript types from GROQ queries, ensuring types always match query shape.

**Query definition:**
```typescript
// apps/ripple-web/src/queries/sanity/pages.ts
import { defineQuery } from "next-sanity"

export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    _id,
    title,
    "path": path.current,
    layout,
    content[] {
      ...,
      _type == "textSection" => { ... }
    },
    seo { ... }
  }
`)
```

**Type generation:**
```bash
npm run generate:schema:and:types
```

**Benefits:**
- Zero manual type definitions
- Types always match queries (no drift)
- Compile-time errors if query changes break code
- Full IDE autocomplete for query results

## Type Generation Output

Generated types match the exact shape of GROQ query results:

```typescript
// Auto-generated - DO NOT EDIT
export type GetPageByPathQueryResult = {
  _id: string
  title: string
  path: string
  layout: 'standard' | 'wide' | 'full-width'
  content: Array<{
    _type: string
    _key: string
  }>
  seo: {
    metaTitle: string
    metaDescription: string
  } | null
} | null
```

## Type-Safe Component Usage

```typescript
import { sanityFetch } from "@/lib/sanity/client"
import { getPageByPathQuery } from "@/queries/sanity/pages"
import type { GetPageByPathQueryResult } from "../../sanity.types"

async function Page({ params }: { params: { path: string } }) {
  const page: GetPageByPathQueryResult = await sanityFetch({
    query: getPageByPathQuery,
    params: { path: params.path }
  })

  if (!page) return notFound()

  return <h1>{page.title}</h1>  // ✅ Full type inference
}
```

## Setting Up Type Generation (v4)

**1. Install dependencies:**
```bash
npm install -D sanity@^4.0.0 @sanity/codegen
```

**2. Add generation script to package.json:**
```json
{
  "scripts": {
    "generate:schema:and:types": "sanity schema extract && sanity typegen generate"
  }
}
```

**3. Create sanity-typegen.json config:**
```json
{
  "generates": {
    "./sanity.types.ts": {
      "schema": "schema.json"
    }
  }
}
```

**4. Run type generation:**
```bash
npm run generate:schema:and:types
```

**Output files:**
- `schema.json` - Extracted Sanity schema
- `sanity.types.ts` - Generated TypeScript types for all queries

**5. Add to .gitignore (optional):**
```gitignore
# Option 1: Gitignore (regenerate in CI)
sanity.types.ts
schema.json

# Option 2: Commit (faster local development)
# (Keep sanity.types.ts for offline type checking)
```

**6. Integrate into CI/CD:**
```yaml
# .github/workflows/ci.yml
- name: Generate Sanity types
  run: npm run generate:schema:and:types

- name: Type check
  run: npm run type-check
```


## Helix Pattern (Manual Types with Inference)

Helix (v3) manually defines TypeScript types for GROQ query results without automated generation.

**Query:**
```typescript
// lib/sanity/queries/pageByPathQuery.ts
const pageByPathQuery = (path: string) => groq`
  *[_type == "page" && slug.current == $path][0]{
    title,
    slug,
    seo { metaTitle, metaDescription },
    pageBuilder[] { ..., _type == 'accordion' => { ... } }
  }
`
```

**Manual type definition:**
```typescript
// types/page.ts
export type SeoData = {
  metaTitle: string | null
  metaDescription: string | null
}

export type PageByPath = {
  title: string | null
  slug: { current: string }
  seo: SeoData | null
  pageBuilder: Array<{ _type: string, _key: string }>
} | null
```

**Usage:**
```typescript
import type { PageByPath } from '@/types/page'

const page: PageByPath = await client.fetch(pageByPathQuery(path))
```

**Challenges:**
- Manual types can drift from queries
- Must update types when query changes
- No compile-time validation of query structure

## Kariusdx Pattern (Manual Types with Utility Types)

Kariusdx uses manual types with TypeScript utility types for reusability.

**Reusable image type:**
```typescript
// types/sanity.ts
export type SanityImageWithMetadata = {
  url: string
  width: number
  height: number
  aspectRatio: number
  blurHash: string
}

export type SanityReference<T = any> = {
  _ref: string
  _type: 'reference'
}
```

**Query result type:**
```typescript
// types/page.ts
import type { SanityImageWithMetadata } from './sanity'

export type PageQueryResult = {
  globalData: {
    siteName: string
    contactEmail: string
    socialLinks: Array<{
      platform: string
      url: string
    }>
  }
  pageData: {
    title: string
    path: string
    heroImage: SanityImageWithMetadata | null
    content: Array<{
      _type: string
      _key: string
      // ... content block types
    }>
  } | null
}
```

**Usage:**
```typescript
import pageQuery from '@/lib/groq/pageQuery'
import type { PageQueryResult } from '@/types/page'

const data: PageQueryResult = await client.fetch(pageQuery(slug))
```


## Using Sanity Codegen for v2/v3 Projects

Even v2/v3 projects can generate base types from schema, then extend manually.

**1. Generate schema types:**
```bash
npx sanity schema extract
npx @sanity/codegen
```

**2. Use generated schema types:**
```typescript
// Auto-generated from schema
import type { Page, SeoMetadata } from './sanity.schema'

// Manual query result type (uses generated types)
export type PageQueryResult = Pick<Page, 'title' | 'slug'> & {
  seo: SeoMetadata | null
  heroImage: {
    url: string
    width: number
    height: number
  } | null
}
```

**Benefits:**
- Schema types auto-generated (field names, document types)
- Query result types manually crafted (projected fields, computed fields)
- Partial automation reduces manual work


## Typed Query Parameters

**v4 defineQuery (auto-inferred params):**
```typescript
export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    title
  }
`)

// TypeScript infers $path parameter
await sanityFetch({
  query: getPageByPathQuery,
  params: { path: '/about' }  // ✅ Type-checked
})
```

**v2/v3 groq template (manual param types):**
```typescript
const pageByPathQuery = (pagePath: string) => groq`
  *[_type == "page" && slug.current == $pagePath][0]
`

// Parameter type enforced by function signature
await client.fetch(pageByPathQuery('/about'))  // ✅ Type-checked
```


## Discriminated Union Types

**Manual typing for polymorphic content arrays:**

```typescript
// types/contentBlocks.ts
type TextBlock = {
  _type: 'textBlock'
  _key: string
  heading: string
  text: string
  alignment: 'left' | 'center' | 'right'
}

type ImageBlock = {
  _type: 'imageBlock'
  _key: string
  image: {
    url: string
    alt: string
  }
  caption: string | null
}

type VideoBlock = {
  _type: 'videoBlock'
  _key: string
  videoUrl: string
  thumbnail: { url: string }
}

export type ContentBlock = TextBlock | ImageBlock | VideoBlock
```

**Type-safe rendering:**
```typescript
const renderBlock = (block: ContentBlock) => {
  switch (block._type) {
    case 'textBlock':
      return <div>{block.heading}</div>  // ✅ TypeScript knows block has heading

    case 'imageBlock':
      return <img src={block.image.url} alt={block.image.alt} />  // ✅ Type-safe

    case 'videoBlock':
      return <video src={block.videoUrl} />  // ✅ Type-safe

    default:
      const _exhaustive: never = block  // ✅ Compile error if case missing
      return null
  }
}
```

**Benefits:**
- Exhaustiveness checking (compile error if block type not handled)
- Type narrowing in switch statements
- Autocomplete for type-specific fields


## Handling Nullable Query Results

GROQ queries can return `null` if no document matches.

**Query result type (nullable):**
```typescript
export type PageByPath = {
  title: string
  slug: { current: string }
} | null
```

**Component with null check:**
```typescript
async function Page({ params }: { params: { path: string } }) {
  const page = await client.fetch(pageByPathQuery(params.path))

  if (!page) return notFound()  // ✅ Type guard

  return <h1>{page.title}</h1>  // ✅ TypeScript knows page is not null
}
```

## Optional vs Nullable Fields

**Pattern: Distinguish optional from nullable:**

```typescript
type PageData = {
  title: string           // Required field
  subtitle?: string       // Optional field (may be omitted from query)
  excerpt: string | null  // Nullable field (explicitly null in Sanity)
}
```

**Usage:**
```typescript
<h1>{page.title}</h1>
{page.subtitle && <h2>{page.subtitle}</h2>}  // Optional check
{page.excerpt !== null && <p>{page.excerpt}</p>}  // Null check
```


## Typing Reusable Partials

**Partial with type export:**
```typescript
// partials/imgReference.ts
export type ImageReference = {
  url: string
  altText: string | null
  width: number
  height: number
  aspectRatio: number
  blurHash: string
}

const imgReference = `
{
  url,
  altText,
  'width': metadata.dimensions.width,
  'height': metadata.dimensions.height,
  'aspectRatio': metadata.dimensions.aspectRatio,
  'blurHash': metadata.blurHash
}
`
export default imgReference
```

**Using partial type in query result:**
```typescript
import imgReference, { type ImageReference } from './partials/imgReference'

export type PageResult = {
  title: string
  heroImage: ImageReference | null  // ✅ Reuse partial type
  thumbnail: ImageReference | null
}
```

**Benefit:** Single source of truth for both GROQ partial and TypeScript type.


## 1. Always Type Query Results

```typescript
// ❌ Avoid - No typing
const page = await client.fetch(pageQuery(slug))
console.log(page.title)  // ❌ No autocomplete, runtime error if field missing

// ✅ Good - Explicit typing
const page: PageResult = await client.fetch(pageQuery(slug))
console.log(page.title)  // ✅ Autocomplete, compile-time safety
```

## 2. Use Discriminated Unions for Polymorphic Content

```typescript
// ✅ Good - Discriminated union
type ContentBlock =
  | { _type: 'textBlock'; heading: string }
  | { _type: 'imageBlock'; image: { url: string } }

// ❌ Avoid - Loose typing
type ContentBlock = {
  _type: string
  heading?: string
  image?: { url: string }
}
```

## 3. Keep Types Close to Queries

```typescript
// ✅ Good - Co-located
// queries/pages.ts
export const getPageQuery = defineQuery(`...`)
export type PageResult = {...}

// ❌ Avoid - Separate type files
// types/page.ts (far from query)
export type PageResult = {...}
```

## 4. Prefer Auto-Generation Over Manual Types

**For v4 projects:** Always use `defineQuery()` + type generation.

**For v2/v3 projects:** Consider upgrading to v4 for type safety benefits.

## Migration Strategy

**From manual types to auto-generated types:**

1. Upgrade to Sanity v4 and next-sanity v7+
2. Convert queries from `groq` to `defineQuery`
3. Set up type generation tooling
4. Run `npm run generate:schema:and:types`
5. Replace manual type imports with generated types
6. Remove manual type definition files

**Example migration:**
```typescript
// Before (v3 with manual types)
import { groq } from 'next-sanity'
import type { PageResult } from '@/types/page'  // Manual

const pageQuery = groq`...`
const page: PageResult = await client.fetch(pageQuery)

// After (v4 with auto-generated types)
import { defineQuery } from 'next-sanity'
import type { GetPageQueryResult } from '../../sanity.types'  // Auto-generated

export const getPageQuery = defineQuery(`...`)
const page: GetPageQueryResult = await sanityFetch({ query: getPageQuery })
```

## Related Patterns

- **Modern defineQuery API** - See `modern-definequery-api.md` for v4 query definition
- **Query File Organization** - See `query-file-organization.md` for co-locating types with queries
- **Reusable Query Partials** - See `reusable-query-partials.md` for typing partial patterns

## Summary

TypeScript typing for GROQ queries shows 100% adoption across 51 query files. Ripplecom (v4) uses auto-generated types via `defineQuery()` + sanity-codegen, eliminating manual type definitions. Helix and kariusdx (v2/v3) manually define types for each query result. Auto-generation provides compile-time query validation, prevents type drift, and enables full IDE autocomplete. For v4 projects, always use type generation. For v2/v3 projects, consider manual types with utility types for reusability, or upgrade to v4 for automated type safety.
