# Data Fetching Patterns - Cross-Project Comparison

**Analysis Date:** February 11, 2026
**Repos Analyzed:** helix-dot-com-next, kariusdx-next, policy-node

## Quantitative Summary

| Pattern | helix | kariusdx | policy-node | Total | Adoption |
|---------|-------|----------|-------------|-------|----------|
| **Pages Router** |
| getServerSideProps | 17 | 12 | 22 | 51 | 100% |
| getStaticProps | 18 | 14 | 19 | 51 | 100% |
| getStaticPaths | 17 | 11 | 20 | 48 | 100% |
| **App Router** |
| await fetch | 48 | 1 | 70 | 119 | 67% |
| route.ts handlers | 8 | 0 | 14 | 22 | 67% |
| Server actions ('use server') | 0 | 0 | 0 | 0 | 0% |
| **ISR & Caching** |
| revalidate configs | 116 | 23 | 162 | 301 | 100% |
| cache: configurations | 7 | 0 | 0 | 7 | 33% |
| **Client-Side** |
| useSWR | 0 | 0 | 0 | 0 | 0% |
| React Query | 185 (imports only, minimal actual usage) |
| **Error Handling** |
| try/catch blocks | ~4060 total | High |

## Next.js Version Analysis

- **helix-dot-com-next:** v15 (App Router primary, Pages Router legacy)
- **kariusdx-next:** v12/v13 (Pages Router only)
- **policy-node:** v14 (Hybrid: App Router + Pages Router)

## Key Patterns Identified

### 1. ISR is Universal (100% adoption)
All three projects heavily use Incremental Static Regeneration with revalidation.

**Pages Router (kariusdx):**
```typescript
export const getStaticProps: GetStaticProps = async () => {
  // fetch data
  return {
    props: { data },
    revalidate: 10, // seconds
  }
}
```

**App Router (helix, policy-node):**
```typescript
export const revalidate = 10 // seconds (segment-level)
```

**Revalidation Values:**
- **10 seconds:** Most common (helix, kariusdx)
- **30 seconds:** sanityFetch default (helix)
- **60 seconds:** WordPress content (policy-node)

### 2. Custom Fetch Wrappers (100% adoption)

All projects wrap their data fetching logic for consistency.

#### helix: sanityFetch
- **Purpose:** Sanity CMS data fetching
- **Features:**
  - Draft mode detection
  - Automatic cache control (force-cache vs no-cache)
  - Token injection for preview
  - Default 30s revalidation
  - Tag-based revalidation support

#### policy-node: fetchGraphQL + fetchGraphQLOptimized
- **Purpose:** WordPress GraphQL API
- **Features:**
  - Timeout management (30s prod, 10s dev)
  - Automatic retries (3x default) with exponential backoff
  - Network error detection and retry
  - Query name extraction for error logging
  - Preview token support
  - **Advanced:** GraphQL request batching (fetchOptimized)
  - Detailed logging and error tracking

#### kariusdx: getStaticPropsWithPreview
- **Purpose:** Reusable getStaticProps wrapper
- **Features:**
  - Preview mode support
  - notFound handling
  - Automatic ISR (revalidate: 10)
  - Preview data filtering

### 3. No Server Actions (0% adoption)
Zero usage of 'use server' directive across all repos.
- All server-side data fetching uses traditional patterns
- Route handlers for mutations/API endpoints

### 4. Minimal Client-Side Fetching (0% SWR, minimal React Query)
- No SWR usage despite it being Next.js recommended
- React Query detected (185 mentions) but analysis shows most are import statements, minimal actual usage
- Heavy preference for server-side rendering

### 5. Error Handling Patterns

#### policy-node (Most Robust)
- **Timeout detection:** AbortController with configurable timeouts
- **Retry logic:** Exponential backoff (retryDelay * 2^attempt)
- **Network error detection:** ETIMEDOUT, ECONNREFUSED, ENOTFOUND, ConnectTimeoutError
- **Detailed logging:** Query name, duration, attempt number, endpoint
- **GraphQL error parsing:** Extract and log error messages

#### helix
- **Basic try/catch:** Present but less sophisticated
- **Draft mode validation:** Throws if token missing

#### kariusdx
- **notFound handling:** Returns { notFound: true } for missing data
- **Preview data filtering:** Handles draft vs published content

### 6. App Router Adoption

**helix (v15):**
- Primary App Router usage
- 48 fetch calls in server components
- 8 route handlers (api/preview, api/exit-preview, etc.)
- generateStaticParams + generateMetadata pattern

**policy-node (v14):**
- Hybrid approach (most complex)
- 70 fetch calls
- 14 route handlers
- Extensive use of catch-all routes ([...slug])

**kariusdx (v12/v13):**
- Pages Router only
- 1 fetch call (minimal App Router)
- 0 route handlers

## Architecture Patterns

### Pattern A: Sanity CMS (helix)
```typescript
// page.tsx
export const revalidate = 10

export async function generateMetadata(): Promise<Metadata> {
  const pageData = await sanityFetch<PageByPath>({
    query: pageByPathQuery,
    params: { pagePath: 'resources' },
  })
  return buildMetaData({ /* ... */ })
}

export default async function Page() {
  const pageData = await sanityFetch<PageByPath>({
    query: pageByPathQuery,
    params: { pagePath: 'resources' },
  })
  return <Component data={pageData} />
}
```

**Characteristics:**
- Duplicate queries (metadata + page) - relies on React cache deduplication
- GROQ queries for Sanity
- Tag-based revalidation support

### Pattern B: WordPress GraphQL (policy-node)
```typescript
// page.tsx
export const revalidate = 60

export async function generateStaticParams() {
  // Recursive pagination to fetch ALL paths
  const fetchAllPosts = async (cursor?: string, allPosts = []) => {
    const { posts, pageInfo } = await getPageSlugs({ after: cursor })
    const updatedPosts = [...allPosts, ...posts]
    if (pageInfo.hasNextPage) {
      return fetchAllPosts(pageInfo.endCursor, updatedPosts)
    }
    return updatedPosts
  }
  const allPosts = await fetchAllPosts()
  return allPosts.map(post => ({ slug: post.uri.split('/') }))
}

export default async function Page({ params }) {
  const pageData = await getPageByUri(params.slug)
  if (!pageData) notFound()
  return <Component data={pageData} />
}
```

**Characteristics:**
- Recursive pagination in generateStaticParams (handles large datasets)
- Separate queries for paths vs content
- WordPress-specific: language slug denormalization
- GraphQL with cursor-based pagination

### Pattern C: Pages Router + Preview (kariusdx)
```typescript
// pages/[...slug].tsx
import getStaticPropsWithPreview from 'utils/getStaticPropsWithPreview'

export const getStaticProps = getStaticPropsWithPreview

export async function getStaticPaths() {
  // Define paths to pre-render
  return {
    paths: [{ params: { slug: ['home'] } }],
    fallback: 'blocking',
  }
}

export default function Page({ pageData }) {
  return <Component data={pageData} />
}
```

**Characteristics:**
- Reusable wrapper pattern
- fallback: 'blocking' for ISR
- Centralized preview logic

## De Facto Standards (>80% adoption)

1. ✅ **ISR with revalidation** (100% - universal pattern)
2. ✅ **Custom fetch wrappers** (100% - always abstracted)
3. ✅ **Preview mode support** (100% - all have preview)
4. ✅ **Error handling with try/catch** (100% - extensive usage)
5. ✅ **Server-side rendering preference** (100% - minimal client fetching)

## Divergent Patterns

1. **Revalidation timing:**
   - 10s (kariusdx, helix default)
   - 30s (helix sanityFetch)
   - 60s (policy-node WordPress)

2. **Error handling sophistication:**
   - Basic (helix, kariusdx)
   - Advanced with retries (policy-node)

3. **Optimization strategies:**
   - React cache deduplication (helix)
   - GraphQL batching (policy-node)
   - Wrapper functions (kariusdx)

## Recommendations for Documentation

### High Priority Docs
1. ISR revalidation patterns (100% confidence)
2. Custom fetch wrapper patterns (100% confidence)
3. Preview mode implementation (100% confidence)
4. Error handling strategies (100% confidence, varying sophistication)
5. App Router data fetching (generateStaticParams + revalidate)
6. Pages Router data fetching (getStaticProps + ISR)

### Medium Priority
7. Route handlers (67% adoption)
8. GraphQL batching (33% adoption, but valuable pattern)
9. Recursive pagination in generateStaticParams

### Low Priority / Anti-Patterns
10. Server actions - document the gap (0% adoption, not yet adopted)
11. Client-side fetching libraries - document the gap (0% SWR, minimal React Query)

## Semgrep Rule Opportunities

1. ✅ Enforce revalidate export in pages/routes
2. ✅ Require try/catch in fetch wrappers
3. ✅ Enforce timeout in custom fetch functions
4. ⚠️ Warn on missing error handling in data fetching
5. ⚠️ Warn on duplicate queries without React cache
6. ⚠️ Detect missing preview mode support in data fetchers
