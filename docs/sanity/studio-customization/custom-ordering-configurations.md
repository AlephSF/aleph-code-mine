---
title: "Custom Ordering Configurations"
category: "studio-customization"
subcategory: "organization"
tags: ["sanity", "ordering", "sorting", "desk", "usability"]
stack: "sanity"
priority: "low"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

## Overview

Custom ordering configurations in Sanity Studio define sort options for document lists in desk structure. Ordering configurations enable content editors to switch between alphabetical, date-based, and custom sorting without writing GROQ queries. Only 33% of analyzed projects use custom orderings (ripplecom v4 only).

## Orderings Schema Configuration

Orderings are defined in document schema `orderings` array. Each ordering has `title`, `name`, and `by` fields.

**Basic Ordering:**

```typescript
// schemaTypes/documents/blogPost.ts
import { defineType } from 'sanity'

export default defineType({
  name: 'blogPost',
  title: 'Blog Post',
  type: 'document',
  orderings: [
    {
      title: 'Publication Date (Newest First)',
      name: 'publishedAtDesc',
      by: [{ field: 'publishedAt', direction: 'desc' }],
    },
    {
      title: 'Publication Date (Oldest First)',
      name: 'publishedAtAsc',
      by: [{ field: 'publishedAt', direction: 'asc' }],
    },
    {
      title: 'Title (A-Z)',
      name: 'titleAsc',
      by: [{ field: 'title', direction: 'asc' }],
    },
  ],
  fields: [
    {
      name: 'title',
      type: 'string',
    },
    {
      name: 'publishedAt',
      type: 'datetime',
    },
  ],
})
```

Ripplecom defines 3 orderings for blog posts. Content editors see dropdown menu in desk structure with "Publication Date (Newest First)", "Publication Date (Oldest First)", and "Title (A-Z)" options.

**Ordering Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `title` | string | Yes | Display name in dropdown |
| `name` | string | Yes | Unique identifier (camelCase) |
| `by` | array | Yes | Sort criteria (field + direction) |

## Multi-Field Sorting

Orderings support multiple sort fields for tiebreaker logic.

**Multi-Field Pattern:**

```typescript
orderings: [
  {
    title: 'Category, then Title (A-Z)',
    name: 'categoryTitleAsc',
    by: [
      { field: 'category->title', direction: 'asc' },
      { field: 'title', direction: 'asc' },
    ],
  },
]
```

Sorts by category title first, then by document title for documents with same category. Uses `->` syntax to dereference category reference field.

**Use Cases:**

- **Events:** Sort by date, then time
- **Products:** Sort by category, then price
- **Team members:** Sort by department, then last name
- **Blog posts:** Sort by category, then publication date

## Sorting by Reference Fields

Reference field sorting uses `->` syntax to access referenced document fields.

**Reference Sorting:**

```typescript
// schemaTypes/documents/event.ts
export default defineType({
  name: 'event',
  orderings: [
    {
      title: 'Venue Name (A-Z)',
      name: 'venueAsc',
      by: [{ field: 'venue->name', direction: 'asc' }],
    },
  ],
  fields: [
    {
      name: 'title',
      type: 'string',
    },
    {
      name: 'venue',
      type: 'reference',
      to: [{ type: 'venue' }],
    },
  ],
})
```

Sorts events by referenced venue's `name` field. Useful when primary sort field exists in related document.

**Multi-Level References:**

```typescript
orderings: [
  {
    title: 'Author Country (A-Z)',
    name: 'authorCountryAsc',
    by: [{ field: 'author->country->name', direction: 'asc' }],
  },
]
```

Chain `->` operators for nested reference traversal: `document → author → country → name`.

## Common Ordering Patterns

Ripplecom uses 13 orderings across 7 document types. Common patterns:

## Date-Based Orderings (Most Common)

```typescript
// Blog posts, press releases, events
orderings: [
  {
    title: 'Publication Date (Newest First)',
    name: 'publishedAtDesc',
    by: [{ field: 'publishedAt', direction: 'desc' }],
  },
  {
    title: 'Publication Date (Oldest First)',
    name: 'publishedAtAsc',
    by: [{ field: 'publishedAt', direction: 'asc' }],
  },
]
```

Descending order (newest first) as default for time-series content.

## Alphabetical Orderings

```typescript
// People, categories, tags
orderings: [
  {
    title: 'Name (A-Z)',
    name: 'nameAsc',
    by: [{ field: 'name', direction: 'asc' }],
  },
  {
    title: 'Name (Z-A)',
    name: 'nameDesc',
    by: [{ field: 'name', direction: 'desc' }],
  },
]
```

Bidirectional alphabetical sort for taxonomy and reference documents.

## Priority Orderings

```typescript
// Featured content, pinned posts
orderings: [
  {
    title: 'Priority (High to Low)',
    name: 'priorityDesc',
    by: [
      { field: 'priority', direction: 'desc' },
      { field: 'publishedAt', direction: 'desc' },
    ],
  },
]
```

Sort by priority field first, then by date for same-priority documents.

## Default Ordering

First ordering in `orderings` array becomes default sort order. Order matters.

**Example:**

```typescript
orderings: [
  { title: 'Newest First', name: 'publishedAtDesc', ... }, // Default
  { title: 'Oldest First', name: 'publishedAtAsc', ... },
  { title: 'Title (A-Z)', name: 'titleAsc', ... },
]
```

Content editors see "Newest First" when opening document list. Dropdown allows switching to other orderings.

**Strategic Default Ordering:**

- **Blog posts:** Newest first (editors focus on recent content)
- **Pages:** Alphabetical (editors search by title)
- **Products:** Category then price (logical browsing)
- **Team members:** Department then last name (organizational structure)

## Ordering UX in Studio

Orderings appear as dropdown menu above document list.

**UI Behavior:**

1. **Initial load** - Shows documents sorted by first ordering
2. **Dropdown click** - Reveals all ordering options
3. **Selection** - Re-sorts documents without page reload
4. **Persistence** - Selection persists in browser session

**No Orderings:**

If `orderings` array missing or empty, Sanity uses default sort (usually `_createdAt desc`). Content editors cannot change sort order.

## When to Define Orderings

**Define orderings when:**

- Document type has time-based fields (publishedAt, eventDate, createdAt)
- Content editors need multiple view modes (newest first vs alphabetical)
- Documents have priority/featured flags
- Reference fields require sorting (venue name, category name)
- Document list regularly exceeds 20 items

**Skip orderings when:**

- Document type has <10 documents total
- Single sort order suffices (e.g., pages always alphabetical)
- Content editors rarely browse full document list
- All documents have same created date (bulk import)

Helix and kariusdx define no custom orderings, relying on default sort. Ripplecom defines orderings for 7 document types with 100+ documents each.

## Ordering Performance

Custom orderings query all documents of type to perform sort. Large document sets (1000+ documents) may load slowly.

**Optimization:**

1. **Index sort fields** - Ensure `publishedAt`, `title`, etc. indexed by Sanity
2. **Limit document list** - Use pagination (default 50 documents per page)
3. **Avoid reference sorting** - Direct field sorting faster than `author->name`

Ripplecom's largest document type (blogPost) has 200+ documents. Orderings load in <1 second with default Sanity indexing.

## Orderings in Custom Desk Structure

Custom desk structure can override schema orderings with `defaultOrdering` option.

**Desk Structure Override:**

```typescript
// structure/index.ts
import { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      S.listItem()
        .title('Blog Posts')
        .child(
          S.documentTypeList('blogPost')
            .title('Blog Posts')
            .defaultOrdering([
              { field: 'publishedAt', direction: 'desc' },
            ]),
        ),
    ])
```

Override forces specific ordering for desk structure list, ignoring schema orderings. Use when desk structure requires different default than schema default.

## Anti-Patterns

**Anti-Pattern 1: Too many orderings**

```typescript
// ❌ BAD: 10 ordering options overwhelms editors
orderings: [
  { title: 'Title A-Z', ... },
  { title: 'Title Z-A', ... },
  { title: 'Date Newest', ... },
  { title: 'Date Oldest', ... },
  { title: 'Author A-Z', ... },
  { title: 'Author Z-A', ... },
  { title: 'Category A-Z', ... },
  { title: 'Category Z-A', ... },
  { title: 'Priority High-Low', ... },
  { title: 'Priority Low-High', ... },
]

// ✅ GOOD: 3-4 most useful orderings
orderings: [
  { title: 'Newest First', ... },
  { title: 'Title (A-Z)', ... },
  { title: 'Category, then Date', ... },
]
```

Limit to 3-4 orderings. More options cause decision paralysis.

**Anti-Pattern 2: Vague ordering titles**

```typescript
// ❌ BAD: Unclear what "Default" means
{ title: 'Default', name: 'default', ... }

// ❌ BAD: Technical jargon
{ title: 'publishedAt DESC', name: 'publishedAtDesc', ... }

// ✅ GOOD: Clear, user-friendly
{ title: 'Publication Date (Newest First)', name: 'publishedAtDesc', ... }
```

**Anti-Pattern 3: Orderings for immutable fields**

```typescript
// ❌ BAD: _id is random, sorting useless
{ title: 'Document ID', name: 'idAsc', by: [{ field: '_id', direction: 'asc' }] }

// ❌ BAD: _createdAt is default, redundant
{ title: 'Created Date', name: 'createdAsc', by: [{ field: '_createdAt', direction: 'asc' }] }
```

Avoid orderings on fields that don't provide useful categorization.

## Related Patterns

- **desk-structure-customization.md** - Custom desk structure with ordering overrides
- **groq-queries/ordering-filtering-pagination.md** - Ordering in GROQ queries
- **schema-definitions/modern-definetype-api.md** - Schema definition patterns

## References

- Ripplecom: `apps/sanity-studio/schemaTypes/documents/blogPost.ts` (3 orderings)
- Ripplecom: `apps/sanity-studio/schemaTypes/documents/person.ts` (1 ordering)
- Ripplecom: `apps/sanity-studio/schemaTypes/documents/event.ts` (2 orderings)
- Sanity Docs: Orderings
