---
title: "Ordering, Filtering, and Pagination"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "ordering", "filtering", "pagination", "array-slicing", "sorting"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

# Ordering, Filtering, and Pagination

## Overview

GROQ provides `|order` for server-side sorting and array slicing (`[N..M]`) for pagination. Adoption varies: kariusdx uses ordering extensively (7 instances), while helix handles sorting client-side (0 instances). Array slicing appears in both projects (helix: 2, kariusdx: 4, ripplecom: minimal observed). The `count()` aggregation for pagination metadata appears in 50% of projects (kariusdx only).

## Pattern Adoption

**Ordering (`|order`):**
- **Helix (v3)**: 0 instances (client-side sorting)
- **Kariusdx (v2)**: 7 instances (server-side sorting)
- **Ripplecom (v4)**: Not extensively measured

**Array Slicing (`[N..M]`):**
- **Helix (v3)**: 2 instances
- **Kariusdx (v2)**: 4 instances
- **Ripplecom (v4)**: Not extensively measured

**Source Confidence:** 67% (helix + kariusdx)


## Basic Ordering Pattern

Kariusdx uses `|order` pipe operator for server-side sorting before fetching results.

**Query with ordering:**
```groq
*[_type == 'news']|order(newsDate desc)[0..5]{
  title,
  excerpt,
  newsDate,
  'featuredImage': featuredImage.image.asset->{url}
}
```

**Result:** 6 most recent news items, sorted by `newsDate` descending (newest first).

**Syntax:**
- `|order(field asc)` - Ascending order (A-Z, 0-9, oldest-newest)
- `|order(field desc)` - Descending order (Z-A, 9-0, newest-oldest)

## Ordering by Date Fields

**Kariusdx common pattern (date-based content):**

```typescript
// Recent news (newest first)
export const recentNewsGroq = (startCount = 0, endCount = 5) => `
  *[_type == 'news']|order(newsDate desc)[${startCount}..${endCount}]{
    ...,
    "featuredImage": featuredImage.image.asset->${imgReferenceExpansion}
  }
`

// Press releases (newest first)
const pressReleasesQuery = groq`
  *[_type == 'pressRelease']|order(publishedDate desc)[0..5]
`

// Videos (newest first)
const videosQuery = groq`
  *[_type == 'video']|order(_createdAt desc)[0..2]{
    ...,
    'image': image.asset->${imgReferenceExpansion}
  }
`
```

**Common date fields for ordering:**
- `publishedDate` - Custom date field
- `newsDate` - Custom date field for news items
- `_createdAt` - Sanity built-in creation timestamp
- `_updatedAt` - Sanity built-in update timestamp

## Multiple Order Criteria

**Query with fallback ordering:**
```groq
*[_type == 'post']|order(publishedDate desc, _createdAt desc)[0..10]{
  title,
  slug
}
```

**Behavior:**
- Primary sort: `publishedDate desc` (newest published first)
- Secondary sort: `_createdAt desc` (if publishedDate is null or tied)

**Use case:** Posts with optional publishedDate field - falls back to creation date.


## Basic Array Slicing

GROQ array slicing (`[start..end]`) extracts subsets of query results for pagination.

**Syntax:**
- `[0..5]` - First 6 items (indices 0-5 inclusive)
- `[6..11]` - Next 6 items (indices 6-11)
- `[0..N]` - First N+1 items

**Query with slicing:**
```groq
*[_type == 'post']|order(publishedAt desc)[0..9]{
  title,
  slug,
  publishedAt
}
```

**Result:** First 10 posts, sorted by publishedAt.

## Parameterized Pagination

**Kariusdx pattern (dynamic pagination):**

```typescript
export const recentNewsGroq = (startCount = 0, endCount = 5) => `
  *[_type == 'news']|order(newsDate desc)[${startCount}..${endCount}]{
    ...,
    "featuredImage": featuredImage.image.asset->${imgReferenceExpansion}
  }
`

// Usage
const page1 = recentNewsGroq(0, 9)   // Items 0-9 (10 items)
const page2 = recentNewsGroq(10, 19) // Items 10-19 (10 items)
const page3 = recentNewsGroq(20, 29) // Items 20-29 (10 items)
```

**Benefits:**
- Single helper function for all pages
- Server-side pagination (reduces client payload)
- Type-safe with TypeScript parameters

## count() for Total Items

**Kariusdx pattern (pagination metadata):**

```typescript
export const newsDataQueryString = (slug: string[]) => (
  slug[slug.length - 1] === 'news'
    ? `
    ${newsDataGroq()},
    "newsDataCount": count(*[_type == 'news']),
`
    : ''
)
```

**Result:**
```json
{
  "newsData": [...],  // Current page items
  "newsDataCount": 42  // Total items for pagination UI
}
```

**Use case:** Display "Page 1 of 5" or "Showing 1-10 of 42" in pagination UI.

**Observation:** Only kariusdx uses `count()` (50% adoption). Helix may handle totals client-side or skip pagination.


## Combined Filter and Order

**Query pattern:**
```groq
*[_type == 'post' && category == $category]|order(publishedAt desc)[0..9]{
  title,
  excerpt,
  publishedAt
}
```

**Execution order:**
1. Filter: `*[_type == 'post' && category == $category]`
2. Order: `|order(publishedAt desc)`
3. Slice: `[0..9]`

**Result:** First 10 posts in specified category, sorted by date.

## Published Content Filter

**Common pattern (only published content):**
```groq
*[_type == 'post' && published == true]|order(publishedAt desc)[0..10]
```

**Use case:** Hide draft/unpublished content from public-facing queries.

## Date Range Filtering with Ordering

**Query pattern:**
```groq
*[
  _type == 'event' &&
  startDate >= $startDate &&
  startDate <= $endDate
]|order(startDate asc)[0..20]{
  title,
  startDate,
  location
}
```

**Result:** Upcoming events within date range, sorted chronologically.


## Helix Pattern (Client-Side Sorting)

Helix fetches unordered results and sorts in React components.

**Query (no ordering):**
```typescript
const latestContentQuery = groq`
  *[_type in ['post', 'page']][0..20]{
    title,
    _type,
    _createdAt
  }
`
```

**Component (client-side sort):**
```typescript
const LatestContent = async () => {
  const content = await client.fetch(latestContentQuery)
  const sorted = content.sort((a, b) =>
    new Date(b._createdAt) - new Date(a._createdAt)
  )
  return <div>{sorted.map(...)}</div>
}
```

**Trade-offs:**
- **Pros:** Flexible sorting in UI (user can change sort order without re-fetching)
- **Cons:** Must fetch all items (no server-side pagination), higher payload size

## Kariusdx Pattern (Server-Side Sorting)

Kariusdx sorts on server with `|order`, reducing payload.

**Query (server-side ordering):**
```typescript
const latestNewsQuery = groq`
  *[_type == 'news']|order(newsDate desc)[0..10]{
    title,
    newsDate
  }
`
```

**Component (already sorted):**
```typescript
const LatestNews = async () => {
  const news = await client.fetch(latestNewsQuery)
  return <div>{news.map(...)}</div>  // ✅ Already sorted
}
```

**Trade-offs:**
- **Pros:** Smaller payload (only needed items), server does sorting work
- **Cons:** Less flexible (changing sort requires new query)

**Recommendation:** Use server-side ordering for pagination and large datasets. Use client-side sorting for small datasets (<50 items) with user-controlled sorting.


## Priority-Based Ordering

**Query with custom priority field:**
```groq
*[_type == 'announcement']|order(priority asc, publishedDate desc)[0..5]{
  title,
  priority,
  publishedDate
}
```

**Schema (priority field):**
```typescript
defineField({
  name: 'priority',
  type: 'number',
  validation: (Rule) => Rule.min(1).max(5),
  description: '1 = Highest priority, 5 = Lowest priority'
})
```

**Result:** Announcements sorted by priority (1 first), then by date within each priority level.


## Offset Pagination (Kariusdx)

**Pattern:**
```typescript
const getNewsPage = (page: number, perPage: number = 10) => {
  const start = (page - 1) * perPage
  const end = start + perPage - 1
  return groq`
    {
      "items": *[_type == 'news']|order(newsDate desc)[${start}..${end}],
      "total": count(*[_type == 'news'])
    }
  `
}

// Usage
const page1 = getNewsPage(1, 10)  // [0..9]
const page2 = getNewsPage(2, 10)  // [10..19]
```

**Benefit:** Standard offset pagination with page numbers (1, 2, 3, ...).

## Cursor Pagination (Not Observed)

**Not used in analyzed projects, but GROQ supports:**
```groq
*[_type == 'post' && _createdAt < $cursor]|order(_createdAt desc)[0..9]
```

**Use case:** Infinite scroll, "Load More" buttons.


## Cannot Order by Reference Fields Directly

**❌ Does not work:**
```groq
*[_type == 'post']|order(author->name desc)  // ❌ Cannot order by referenced field
```

**✅ Workaround (flatten first):**
```groq
*[_type == 'post']{
  ...,
  'authorName': author->name
}|order(authorName desc)
```

**Or fetch and sort client-side.**

## Cannot Order by Computed Fields

**❌ Does not work:**
```groq
*[_type == 'post']|order(count(tags[]) desc)  // ❌ Cannot order by aggregation
```

**✅ Workaround:**
```groq
*[_type == 'post']{
  ...,
  'tagCount': count(tags[])
}|order(tagCount desc)
```


## Ordering vs Client-Side Sorting

**Server-side ordering (|order):**
- ✅ Efficient for large datasets (sorts before fetching)
- ✅ Enables server-side pagination
- ✅ Reduces client payload size
- ❌ Less flexible for user-controlled sorting

**Client-side sorting:**
- ✅ Flexible (users can re-sort without re-fetching)
- ✅ Good for small datasets (<50 items)
- ❌ Must fetch all items (higher payload)
- ❌ Sorting work done on client

**Recommendation:** Use `|order` for pagination and large datasets. Use client-side sort for small, user-controlled datasets.

## Related Patterns

- **Query Parameterization** - See `typescript-query-typing.md` for parameterized pagination queries
- **Projection and Composition** - See `projection-composition.md` for composing pagination helpers
- **Array Slicing** - See GROQ documentation for advanced slicing syntax

## Summary

Server-side ordering (`|order`) appears in 50% of projects (kariusdx only, 7 instances). Array slicing (`[N..M]`) for pagination appears in 100% of projects with 6 total instances. The `count()` aggregation for pagination metadata appears in kariusdx only. Helix handles sorting client-side. Best practices: use server-side ordering for large datasets and pagination, use client-side sorting for small datasets with user-controlled sorting, combine filtering → ordering → slicing for efficient queries.
