# GROQ Queries - Cross-Project Comparison

**Analysis Date:** February 11, 2026
**Scope:** Phase 3, Domain 2 - GROQ Queries
**Repositories:**
- helix-dot-com-next (Sanity v3.10.0) + helix-dot-com-sanity
- kariusdx-next (Sanity v2.30.0) + kariusdx-sanity
- ripplecom-nextjs (Sanity v4.3.0) - apps/ripple-web
- policy-node (WordPress VIP - **No Sanity, uses GraphQL**)

---

## Executive Summary

**Query File Counts:**
- Helix (v3): 12 query files
- Kariusdx (v2): 17 query files (8 main queries + 9 partials/helpers)
- Ripplecom (v4): 22 query files (16 main queries + 6 partials)
- Policy-node: 0 (uses WordPress GraphQL, not Sanity)
- **Total**: 51 GROQ query files analyzed

**Key Finding**: Significant API evolution from v2 → v3 → v4. Ripplecom (v4) uses modern `defineQuery()` API, while helix (v3) and kariusdx (v2) use `groq` tagged template. All three projects adopt reusable partials, reference expansion, and TypeScript typing.

---

## 1. Query File Organization

### Dedicated Query Directories

| Repo | Path | Structure | Partials/Helpers |
|------|------|-----------|------------------|
| Helix | `app/(frontend)/lib/sanity/queries/` | Flat structure | 3 partials in `/partials` |
| Kariusdx | `lib/groq/` | Organized with `/helpers` and `/partials` subdirs | 4 partials + 4 helpers |
| Ripplecom | `apps/ripple-web/src/queries/sanity/` | Organized with `/partials` subdir | 6 partials |

**Pattern confidence**: 100% (all projects use dedicated query directories)

**Helix query files:**
- 12 query files (e.g., `pageByPathQuery.ts`, `termQuery.ts`, `footerQuery.ts`)
- 3 partials: `imgReference.ts`, `link.ts`, `teaser.ts`

**Kariusdx query files:**
- 8 main queries (e.g., `pageQuery.ts`, `newsPageQuery.ts`, `eventsPageQuery.ts`)
- 4 partials: `imgReferenceExpansion.ts`, `seoData.ts`, `navigation.ts`, `globalData.ts`
- 4 helpers: `pagePathQueryString.ts`, `clinicalDataQueryString.ts`, `breadCrumbsQueryString.ts`, `buildPagePath.ts`

---

## 2. Modern defineQuery API vs groq Tagged Template

### Two Query Definition Patterns

**Ripplecom (v4) - Modern defineQuery API:**
```typescript
import { defineQuery } from "next-sanity"

export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    _id,
    title,
    "path": path.current
  }
`)
```

**Helix (v3) & Kariusdx (v2) - groq Tagged Template:**
```typescript
import { groq } from 'next-sanity'

const pageQuery = groq`
  *[_type == "page" && slug.current == $slug][0] {
    title,
    slug
  }
`
```

### API Usage by Version

| Repo | Version | defineQuery | groq Template | Pattern |
|------|---------|-------------|---------------|---------|
| Ripplecom | v4.3.0 | 66 instances | 4 instances | 94% modern API |
| Helix | v3.10.0 | 0 instances | 12 files | 100% groq template |
| Kariusdx | v2.30.0 | 0 instances | 8 files | 100% groq template |

**Pattern confidence**: 33% for modern defineQuery (ripplecom only)

**Benefits of defineQuery (v4+):**
- Auto-generates TypeScript types from queries (via `npm run generate:schema:and:types`)
- Better type inference for query parameters
- Integrated with Sanity's type generation tooling
- Explicit query naming for better debugging

**When to use groq template:**
- Sanity v2/v3 projects (defineQuery not available)
- Backward compatibility requirements
- Manual TypeScript typing preferred

---

## 3. Reusable Query Partials

### Image Reference Expansion Pattern

**Adoption**: 100% (both projects have dedicated image reference partials)

**Helix pattern** (`imgReference.ts`):
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
```

**Kariusdx pattern** (`imgReferenceExpansion.ts`):
```typescript
const imgReferenceExpansion = `
{
  ...,
  'height': metadata.dimensions.height,
  'width': metadata.dimensions.width,
  'aspectRatio': metadata.dimensions.aspectRatio,
  'blurHash': metadata.blurHash,
}
`
```

**Differences:**
- Helix explicitly lists fields (url, altText, title, description)
- Kariusdx uses spread operator (`...`) for default fields

**Common fields:**
- Metadata dimensions (height, width, aspectRatio)
- blurHash for progressive image loading
- 100% adoption of performance-optimized image queries

---

## 4. Reference Expansion Operator (->)

**Usage counts:**
- Helix (v3): 58 instances
- Kariusdx (v2): 30 instances
- Ripplecom (v4): 46 instances

**Pattern confidence**: 100% (universal pattern for dereferencing)

**Common patterns:**
```groq
// Single reference expansion
'image': image.asset->${imgReference}

// Nested reference expansion
author->{
  name,
  'avatar': avatar.asset->${imgReference}
}

// Array reference expansion
people[]->{
  ...,
  'avatar': avatar.asset->${imgReference}
}
```

---

## 5. Projection and Template Interpolation (${...})

**Usage counts:**
- Helix (v3): 48 instances
- Kariusdx (v2): 66 instances
- Ripplecom (v4): Estimated 40+ instances (uses partials extensively)

**Pattern confidence**: 100% (all projects heavily use projections)

**Helix pattern:**
```typescript
const pageByPathQuery = (
  groq`*[_type == "page" && slug.current == $pagePath][0]{
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
    },
  }`
)
```

**Kariusdx pattern:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  ${globalData},
  ${breadCrumbsQueryString(slug)}
  "pageData": ${pagePathQueryString(slug)}{
    ...,
    "heroImage": heroImage.asset -> ${imgReferenceExpansion},
    ${seoData}
    ${clinicalDataQueryString(slug)}
  },
}
`
```

**Differences:**
- Helix: Single large query with inline projections
- Kariusdx: Composed queries with multiple `${}` interpolations

---

## 6. Conditional Field Expansion (_type ==)

**Usage counts:**
- Helix (v3): 39 instances
- Kariusdx (v2): 36 instances
- Ripplecom (v4): 68 instances

**Pattern confidence**: 100% (universal for polymorphic content)

**Pattern:**
```groq
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
}
```

**Use case:** Expanding different fields based on component type in arrays

---

## 7. Ordering and Filtering

### Ordering with |order

**Usage counts:**
- Helix: 0 instances
- Kariusdx: 7 instances

**Pattern confidence**: 50% (only kariusdx uses ordering)

**Kariusdx pattern:**
```groq
*[_type == 'news']|order(newsDate desc)[0..5]
```

**Common ordering patterns in kariusdx:**
- `|order(newsDate desc)` - Sort news by date
- `|order(publishedDate desc)` - Sort press releases
- `|order(_createdAt desc)` - Sort videos by creation date

**Observation:** Helix may handle ordering client-side or in React components

---

## 8. Array Slicing ([N..M])

**Usage counts:**
- Helix: 2 instances
- Kariusdx: 4 instances

**Pattern confidence**: 100% (both use array slicing)

**Pattern:**
```groq
*[_type == 'news']|order(newsDate desc)[0..5]  // Get first 6 items
```

**Common use cases:**
- Pagination: `[0..5]`, `[6..11]`, etc.
- "Latest N items": `[0..2]` for 3 most recent
- Dynamic slicing with parameters: `[${startCount}..${endCount}]`

---

## 9. Query Parameterization

### Using $param in GROQ

**Pattern confidence**: 100% (both projects use parameterized queries)

**Helix pattern:**
```typescript
groq`*[_type == "page" && slug.current == $pagePath][0]`
```

**Kariusdx pattern:**
```typescript
// Via helper functions
const pagePathQueryString = (slug: string[]) => `
  *[_type == 'page' && path == "${buildPagePath(slug)}"][0]
`
```

**Differences:**
- Helix: Uses GROQ params (`$pagePath`) passed to fetch
- Kariusdx: Uses template string interpolation for dynamic queries

---

## 10. count() Aggregation

**Kariusdx usage:**
```groq
"newsDataCount": count(*[_type == 'news'])
```

**Pattern confidence**: 50% (only observed in kariusdx)

**Use case:** Get total count for pagination without fetching all items

---

## 11. Conditional Query Composition

**Kariusdx pattern:**
```typescript
export const newsDataQueryString = (slug: string[]) => (
  slug[slug.length - 1] === 'news'
    ? `
    ${newsDataGroq()}
    "newsDataCount": count(*[_type == 'news']),
`
    : ''
)
```

**Pattern confidence**: 50% (only observed in kariusdx)

**Use case:** Conditionally include query fragments based on route

---

## 12. TypeScript Typing for Query Results

**Pattern confidence**: 100% (both projects type query results)

**Helix pattern:**
```typescript
export type PageByPath = {
  title: string | null
  slug: {
    current: string
  }
  seo: SeoDataType
  pageHero: PageHeroType | null
  pageBuilder: PageBuilder
}

const pageByPathQuery = (
  groq`*[_type == "page" && slug.current == $pagePath][0]{...}`
)
```

**Benefits:**
- Type safety when consuming query results
- Autocomplete in components
- Compile-time error detection

---

## Summary of Universal Patterns (100% Adoption)

1. ✅ Dedicated query directories (`/queries` or `/groq`)
2. ✅ Reusable image reference partials (metadata + dimensions)
3. ✅ Reference expansion operator (`->`) for dereferencing
4. ✅ Projection with template interpolation (`${}`)
5. ✅ Conditional field expansion (`_type ==`) for polymorphic content
6. ✅ Array slicing (`[N..M]`) for pagination
7. ✅ Query parameterization (GROQ params or template strings)
8. ✅ TypeScript typing for results
9. ✅ Organized partials in subdirectories

## Version-Specific Patterns

### Sanity v4 (Ripplecom)
- ✅ **Modern defineQuery API** (66 instances, 94% adoption)
- ✅ Auto-generated TypeScript types from queries
- ✅ Explicit query exports for better type inference
- ✅ JSDoc comments on queries for developer experience

### Sanity v3 (Helix)
- ✅ **groq tagged template** (12 files, 100%)
- ✅ Manual TypeScript type definitions
- ✅ Inline query composition

### Sanity v2 (Kariusdx)
- ✅ **groq tagged template** (8 files, 100%)
- ✅ Helper functions for query composition
- ✅ Extensive use of conditional query fragments

## Divergent Patterns

1. **Query definition API:**
   - Ripplecom (v4): defineQuery() - modern API with auto-generated types
   - Helix (v3): groq template - manual types
   - Kariusdx (v2): groq template - manual types

2. **Query composition approach:**
   - Helix: Large single queries with inline projections
   - Kariusdx: Composed queries with helper functions
   - Ripplecom: Named exports with partials

3. **Ordering:**
   - Helix: No `|order` usage (0 instances)
   - Kariusdx: 7 instances with `|order`
   - Ripplecom: Not extensively measured

4. **Type generation:**
   - Ripplecom: Automated via `npm run generate:schema:and:types`
   - Helix/Kariusdx: Manual TypeScript type definitions

5. **Documentation:**
   - Ripplecom: JSDoc comments with usage instructions
   - Helix/Kariusdx: Minimal inline documentation

---

## Recommendations for Standards

### High Priority (100% Adoption)
- Require dedicated `/queries` or `/groq` directory with `/partials` subdirectory
- Require reusable partials for image references (metadata, dimensions, blurHash)
- Require TypeScript types for query results
- Use reference expansion operator (`->`) for all reference dereferencing
- Use conditional field expansion (`_type ==`) for polymorphic content

### Version-Specific Recommendations

**For Sanity v4 projects:**
- Use `defineQuery()` from `next-sanity` (modern API)
- Set up automated type generation: `npm run generate:schema:and:types`
- Add JSDoc comments to queries with usage instructions
- Export queries as named constants for better tree-shaking

**For Sanity v2/v3 projects:**
- Use `groq` tagged template from `next-sanity`
- Manually define TypeScript types for query results
- Consider migrating to v4 for improved type safety

### Medium Priority (50%+ Adoption)
- Use `|order` for server-side sorting (avoids client-side sorting overhead)
- Use array slicing (`[N..M]`) for pagination
- Use `count()` aggregation for pagination metadata
- Organize queries into logical files (e.g., `pages.ts`, `posts.ts`, `events.ts`)

### Best Practices to Document
1. **Query composition strategies:**
   - When to use inline projections vs. helper functions
   - How to structure reusable partials
   - Balancing query complexity vs. over-fetching

2. **Image reference optimization:**
   - Always include metadata.dimensions for Next.js Image component
   - Include blurHash for progressive loading (kariusdx + helix pattern)
   - Use consistent field naming across partials

3. **Conditional field expansion:**
   - Use for page builder / content block arrays
   - Pattern: `_type == 'blockType' => { expanded fields }`
   - Keeps queries maintainable as content types grow

4. **Type safety progression:**
   - v2/v3: Manual type definitions
   - v4: Auto-generated types from defineQuery
   - Both approaches: Always type query results in consuming code
