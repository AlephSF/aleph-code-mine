---
title: "Modern defineQuery API (Sanity v4+)"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "definequery", "typescript", "v4", "type-generation"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

# Modern defineQuery API (Sanity v4+)

## Overview

Sanity v4 introduced the `defineQuery()` helper function to replace the legacy `groq` tagged template literal. The modern API enables auto-generated TypeScript types from queries, better type inference for query parameters, and explicit query naming for improved debugging. Ripplecom (v4.3.0) has fully adopted this pattern with 66 instances (94% of queries), while helix (v3) and kariusdx (v2) continue using the legacy `groq` template.

## Pattern Adoption

**Adoption Rate:** 33% (1 of 3 repositories)

- **Ripplecom (v4.3.0)**: 66 defineQuery instances (94% modern API)
- **Helix (v3.10.0)**: 0 defineQuery instances (100% groq template)
- **Kariusdx (v2.30.0)**: 0 defineQuery instances (100% groq template)

**Version Availability:**
- Sanity v4.0+: `defineQuery()` available
- Sanity v3: `groq` template only (defineQuery not available)
- Sanity v2: `groq` template only


## Basic Query with defineQuery

Sanity v4 projects use `defineQuery()` from `next-sanity` for type-safe query definitions with auto-generated TypeScript types.

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
      ...
    }
  }
`)
```

**Key differences from groq template:**
- Import from `"next-sanity"` (not `"@sanity/client"`)
- Exported as named const (not default export)
- No template tag needed (function call syntax)
- Enables type generation tooling

## Query with Multiple Exports

Ripplecom organizes related queries in single files with multiple named exports.

```typescript
// apps/ripple-web/src/queries/sanity/pages.ts
import { defineQuery } from "next-sanity"
import { richTextContentGroq } from "@/queries/sanity/partials/richText"
import seoGroq from "@/queries/sanity/partials/seo"

/**
 * Query to fetch a page by its path/slug
 * Returns full page data including layout type, content blocks, and SEO metadata
 */
export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    _id,
    title,
    "path": path.current,
    seo {
      ${seoGroq}
    }
  }
`)

/**
 * Query to fetch all page paths for static generation
 * Returns minimal data needed for Next.js generateStaticParams
 */
export const getAllPagePathsQuery = defineQuery(`
  *[_type == "page"] {
    "path": path.current
  }
`)

/**
 * Query to check if a page exists at a given path
 * Lightweight query for existence checks
 */
export const pageExistsQuery = defineQuery(`
  count(*[_type == "page" && path.current == $path]) > 0
`)
```

**Benefits:**
- Single file for related queries (getByPath, getAll, exists)
- JSDoc comments provide usage context
- Named exports improve tree-shaking
- Auto-generated types for all three queries

## Using Queries with Auto-Generated Types

After defining queries, run type generation to create TypeScript types:

```bash
npm run generate:schema:and:types
```

**Generated types (sanity.types.ts):**
```typescript
// Auto-generated - do not edit manually
export type GetPageByPathQueryResult = {
  _id: string
  title: string
  path: string
  seo: {
    metaTitle: string
    metaDescription: string
    ogImage: { url: string }
  }
} | null

export type GetAllPagePathsQueryResult = Array<{
  path: string
}>
```

**Using generated types in components:**
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


## Basic Query with groq Template

Helix (v3) and kariusdx (v2) use the `groq` tagged template literal with manual TypeScript types.

```typescript
// lib/groq/pageQuery.ts (Kariusdx v2)
import { groq } from 'next-sanity'
import imgReferenceExpansion from './partials/imgReferenceExpansion'

const pageQuery = (slug: string[]) => groq`
{
  "pageData": *[_type == 'page' && path == "${buildPagePath(slug)}"][0]{
    ...,
    "heroImage": heroImage.asset -> ${imgReferenceExpansion},
  },
}
`
export default pageQuery
```

**Characteristics:**
- Tagged template literal syntax (groq\`...\`)
- Function wrapper for parameterization
- Default export (not named export)
- Requires manual TypeScript type definitions

## Manual TypeScript Typing (Legacy Pattern)

With `groq` template, types must be defined manually:

```typescript
// types/page.ts (Manual types for v2/v3)
export type PageQueryResult = {
  pageData: {
    title: string
    slug: { current: string }
    heroImage: {
      url: string
      width: number
      height: number
      blurHash: string
    }
  }
}
```

```typescript
// components/Page.tsx
import pageQuery from '@/lib/groq/pageQuery'
import { PageQueryResult } from '@/types/page'

const data: PageQueryResult = await client.fetch(pageQuery(slug))
```

**Drawbacks:**
- Manual type definitions can drift from actual query
- No compile-time validation of query structure
- Types must be updated when query changes
- More boilerplate code


## Side-by-Side Comparison

**defineQuery (v4):**
```typescript
import { defineQuery } from "next-sanity"

export const getPostsQuery = defineQuery(`
  *[_type == "post"] | order(publishedAt desc) [0..10] {
    _id,
    title,
    slug
  }
`)

// Auto-generated type:
// GetPostsQueryResult = Array<{ _id: string; title: string; slug: { current: string } }>
```

**groq template (v2/v3):**
```typescript
import { groq } from 'next-sanity'

const getPostsQuery = groq`
  *[_type == "post"] | order(publishedAt desc) [0..10] {
    _id,
    title,
    slug
  }
`
export default getPostsQuery

// Manual type definition required:
export type Post = { _id: string; title: string; slug: { current: string } }
export type GetPostsResult = Post[]
```

## Feature Matrix

| Feature | defineQuery (v4+) | groq Template (v2/v3) |
|---------|-------------------|----------------------|
| Type generation | ✅ Auto-generated | ❌ Manual types required |
| Type inference | ✅ Full inference | ⚠️ Limited inference |
| Named exports | ✅ Recommended | ⚠️ Mix of default/named |
| JSDoc support | ✅ Integrated | ⚠️ Manual comments |
| Debugging | ✅ Named queries | ⚠️ Anonymous templates |
| Version support | v4.0+ only | v2, v3, v4 |

## When to Use defineQuery

**Use defineQuery when:**
- ✅ Running Sanity v4.0 or later
- ✅ Want auto-generated TypeScript types
- ✅ Need strict type safety for query parameters
- ✅ Building new projects with modern Sanity versions
- ✅ Can integrate `npm run generate:schema:and:types` into CI/CD

**Stick with groq template when:**
- ⚠️ Running Sanity v2 or v3 (defineQuery unavailable)
- ⚠️ Prefer manual control over types
- ⚠️ Maintaining legacy codebases with established patterns
- ⚠️ Cannot run type generation in build pipeline


## Step 1: Upgrade to Sanity v4

```bash
npm install sanity@^4.0.0 next-sanity@^7.0.0
```

## Step 2: Convert Query Files

**Before (groq template):**
```typescript
import { groq } from 'next-sanity'

const pageQuery = groq`*[_type == "page"][0]{ title, slug }`
export default pageQuery
```

**After (defineQuery):**
```typescript
import { defineQuery } from "next-sanity"

export const getPageQuery = defineQuery(`
  *[_type == "page"][0] {
    title,
    slug
  }
`)
```

## Step 3: Set Up Type Generation

Add script to `package.json`:

```json
{
  "scripts": {
    "generate:schema:and:types": "sanity schema extract && sanity typegen generate"
  }
}
```

## Step 4: Run Type Generation

```bash
npm run generate:schema:and:types
```

**Generated output:**
- `schema.json` - Extracted Sanity schema
- `sanity.types.ts` - TypeScript types for all queries

## Step 5: Update Component Imports

**Before:**
```typescript
import pageQuery from '@/lib/groq/pageQuery'
import type { PageResult } from '@/types/page'  // Manual type
```

**After:**
```typescript
import { getPageQuery } from '@/queries/sanity/pages'
import type { GetPageQueryResult } from '../../sanity.types'  // Auto-generated
```


## 1. Use Named Exports

```typescript
// ✅ Good - Named exports for clarity
export const getPostBySlugQuery = defineQuery(`...`)
export const getAllPostsQuery = defineQuery(`...`)

// ❌ Avoid - Default exports harder to track
const query = defineQuery(`...`)
export default query
```

## 2. Add JSDoc Comments

```typescript
/**
 * Query to fetch a single post by its slug
 * Used in: app/(frontend)/blog/[slug]/page.tsx
 *
 * @param $slug - The post slug from URL params
 * @returns Post data with author, content, and related posts
 */
export const getPostBySlugQuery = defineQuery(`...`)
```

## 3. Run Type Generation in CI/CD

```yaml
# .github/workflows/ci.yml
- name: Generate Sanity types
  run: npm run generate:schema:and:types

- name: Type check
  run: npm run type-check
```

## 4. Gitignore Generated Files (Optional)

```gitignore
# Option 1: Gitignore (regenerate in CI)
sanity.types.ts
schema.json

# Option 2: Commit (faster local dev)
# (commit sanity.types.ts for offline type checking)
```

## Related Patterns

- **Query File Organization** - See `query-file-organization.md` for directory structure
- **TypeScript Query Typing** - See `typescript-query-typing.md` for type patterns
- **Reusable Query Partials** - See `reusable-query-partials.md` for partial composition

## Summary

The modern `defineQuery()` API (v4+) provides auto-generated TypeScript types, better debugging with named queries, and stricter type safety. Ripplecom demonstrates full adoption (94%) with 66 instances across 22 query files. Legacy `groq` template remains necessary for v2/v3 projects. When migrating to v4, adopt defineQuery for new queries while maintaining backward compatibility for existing queries during gradual migration.
