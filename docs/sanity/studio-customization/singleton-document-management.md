---
title: "Singleton Document Management"
category: "studio-customization"
subcategory: "content-modeling"
tags: ["sanity", "singleton", "templates", "settings", "global"]
stack: "sanity"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

## Overview

Singleton documents in Sanity Studio represent global settings, site configuration, and unique content that should only exist once (homepage, navigation, SEO defaults). Singleton management prevents content editors from creating duplicate settings documents. 67% of analyzed Sanity projects use singleton patterns (ripplecom with 6 singletons, kariusdx with 2 singletons).

## Template Filtering Pattern (Modern v3+)

Sanity v3+ removes singleton document types from the "Create" menu by filtering the schema templates array. This prevents accidental creation of duplicate singleton documents.

### Template Filter Implementation

Sanity config templates filter hides singleton types from the global "+ Create" menu:

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'

const singletonTypes = new Set([
  'defaultSeo',
  'footerNavigation',
  'globalOptions',
  'homepage',
  'regions',
  'rlusdBalance',
])

export default defineConfig({
  // ... projectId, dataset, plugins
  schema: {
    types: schemaTypes,
    templates: (prev) =>
      prev.filter((template) => !singletonTypes.has(template.id)),
  },
})
```

Ripplecom uses this pattern to hide 6 singleton types from the "Create" menu. Singletons remain visible in custom desk structure but cannot be created via the global "+ Create" button.

## Singleton Document Types

Common singleton document types across analyzed projects:

| Document Type | Purpose | Projects Using |
|---------------|---------|----------------|
| `homepage` | Homepage-specific content | Ripplecom |
| `defaultSeo` | Site-wide SEO fallbacks | Ripplecom |
| `siteSettings` | General site configuration | Kariusdx |
| `navigation` | Main navigation menu(s) | Kariusdx, Ripplecom |
| `footerNavigation` | Footer navigation links | Ripplecom |
| `regions` | Global region/country data | Ripplecom |
| `rlusdBalance` | Real-time balance display | Ripplecom |

Ripplecom has the most singletons (6), focusing on global configuration and navigation. Kariusdx has 2 singletons (siteSettings, navigation).

## Singleton Schema Definition

Singleton documents use identical schema definitions as regular documents. The "singleton" behavior comes from template filtering and desk structure configuration, not schema fields.

### Homepage Singleton Schema Example

Sanity singleton schemas define standard document structure without special singleton indicators:

```typescript
// schemaTypes/globals/homepage.ts
import { defineType } from 'sanity'
import { HomeIcon } from '@sanity/icons'

export default defineType({
  name: 'homepage',
  title: 'Homepage Setting',
  type: 'document',
  icon: HomeIcon,
  fields: [
    {
      name: 'title',
      title: 'Page Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'heroSection',
      title: 'Hero Section',
      type: 'reference',
      to: [{ type: 'heroSection' }],
    },
    {
      name: 'featuredContent',
      title: 'Featured Content',
      type: 'array',
      of: [
        { type: 'reference', to: [{ type: 'blogPost' }] },
        { type: 'reference', to: [{ type: 'caseStudy' }] },
      ],
    },
  ],
})
```

Ripplecom defines homepage as a regular document type. Schema does not indicate singleton status—configuration in `sanity.config.ts` and `structure/index.ts` enforces singleton behavior.

## Desk Structure Integration

Singletons appear in a dedicated "Global Options" section. Use `.documentId()` to link directly to singleton documents.

### Global Options Grouping

Structure Builder groups singletons with direct document links via hardcoded IDs:

```typescript
// structure/index.ts
import { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      S.divider(),
      S.listItem()
        .title('Global Options')
        .child(
          S.list()
            .title('Global Options')
            .items([
              S.listItem()
                .title('Homepage Setting')
                .child(S.document().schemaType('homepage').documentId('homepage')),
              S.listItem()
                .title('Default SEO')
                .child(S.document().schemaType('defaultSeo').documentId('defaultSeo')),
              // ... other singletons
            ]),
        ),
    ])
```

Each singleton uses `.documentId()` with hardcoded ID matching schema type name, bypassing document list view.

## Singleton Document IDs

Singleton documents must have predictable, hardcoded document IDs. Convention is to use the schema type name as the document ID.

**Examples:**

- Schema type: `homepage` → Document ID: `homepage`
- Schema type: `defaultSeo` → Document ID: `defaultSeo`
- Schema type: `siteSettings` → Document ID: `siteSettings`

Predictable IDs enable:

1. Direct linking in desk structure (`.documentId('homepage')`)
2. Querying from frontend (`*[_type == "homepage"][0]`)
3. Initial value templates for first-time setup

## Initial Value Templates

Sanity automatically creates singleton documents the first time a content editor navigates to them in the desk structure. No manual initialization required.

**Automatic Creation:**

When a content editor clicks "Homepage Setting" in the desk structure, Sanity:

1. Checks if document with ID `homepage` exists
2. If not, creates new document with `_id: "homepage"` and `_type: "homepage"`
3. Opens the document in the form view

Content editors see an empty form on first access. Save once to persist the singleton document.

## Preventing Multiple Singletons

Template filtering prevents creating duplicates via the "+ Create" button, but editors can still create duplicates via direct GROQ mutations or API access. Enforce singleton behavior with:

**1. Template Filtering (Required):**

```typescript
schema: {
  templates: (prev) =>
    prev.filter((template) => !singletonTypes.has(template.id)),
}
```

**2. Desk Structure Exclusion (Required):**

```typescript
...S.documentTypeListItems().filter(
  (item) => !['homepage', 'defaultSeo', 'navigation'].includes(item.getId() ?? ''),
)
```

### Custom Document Actions (Optional)

Kariusdx v2 custom actions prevent unpublishing singletons via action filtering:

```javascript
// schemas/documentActions.js (v2 API)
export default function resolveDocumentActions(props) {
  if (['siteSettings', 'navigation'].includes(props.type)) {
    // Remove unpublish action for singletons
    return defaultResolve(props).filter(
      (Action) => Action !== UnpublishAction
    )
  }
  return defaultResolve(props)
}
```

This pattern is advanced and optional for most projects.

## Querying Singletons from Frontend

Singleton documents use `[0]` array accessor to select the first (only) document of that type.

### Homepage Singleton GROQ Query

defineQuery with [0] accessor returns single object instead of array:

```typescript
// queries/homepage.ts
import { defineQuery } from 'next-sanity'

export const homepageQuery = defineQuery(`
  *[_type == "homepage"][0] {
    _id,
    title,
    heroSection->{
      _id,
      title,
      backgroundImage
    },
    featuredContent[]->{
      _id,
      _type,
      title,
      slug
    }
  }
`)
```

### Next.js Server Component Integration

Next.js async server components fetch singleton data with null checks:

```typescript
// app/page.tsx
import { sanityFetch } from '@/lib/sanity'
import { homepageQuery } from '@/queries/homepage'

export default async function HomePage() {
  const homepage = await sanityFetch({ query: homepageQuery })

  if (!homepage) {
    return <div>Homepage not configured</div>
  }

  return (
    <main>
      <h1>{homepage.title}</h1>
      {/* ... */}
    </main>
  )
}
```

Always check for `null` result. Singleton may not exist if content editor hasn't saved it yet.

## Multi-Singleton Desk Structure

Some singleton types allow multiple instances with different purposes. Ripplecom uses this for `navigation` (multiple menus: header, footer, mobile).

### List View Pattern

Multi-singleton desk structure shows filtered document list instead of single document:

```typescript
// Desk structure shows a filtered list, not a single document
S.listItem()
  .title('Navigation Menus')
  .icon(MenuIcon)
  .child(
    S.documentTypeList('navigation')
      .title('Navigation Menus')
      .filter('_type == "navigation"'),
  ),
```

## Multi-Singleton Schema Definition

Multi-singleton schemas include internal title field for differentiating instances.

### Navigation Schema Pattern

Navigation schema uses required title field as internal identifier:

```typescript
export default defineType({
  name: 'navigation',
  title: 'Navigation Menu',
  type: 'document',
  fields: [
    {
      name: 'title',
      title: 'Menu Title',
      type: 'string',
      description: 'Internal label (e.g., "Header Menu", "Footer Menu")',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'items',
      title: 'Menu Items',
      type: 'array',
      of: [{ type: 'navigationItem' }],
    },
  ],
})
```

## Multi-Singleton Query Pattern

Frontend queries specific navigation menus by internal title parameter.

### Title-Based Navigation Query

defineQuery filters navigation documents by title string parameter:

```typescript
// Query specific navigation by title
export const navigationQuery = defineQuery(`
  *[_type == "navigation" && title == $title][0] {
    _id,
    title,
    items[] {
      label,
      href,
      external
    }
  }
`)

// Usage
const headerNav = await sanityFetch({
  query: navigationQuery,
  params: { title: 'Header Menu' },
})
```

Multi-singleton pattern is semi-singleton: not truly global, but limited to 3-5 instances per type.

## When to Use Singletons

**Use singletons for:**

- Site settings (site name, logo, social links)
- SEO defaults (fallback title, description, OG image)
- Navigation menus (1-3 menus: header, footer, mobile)
- Homepage configuration
- Global announcements or banners
- Footer content

**Don't use singletons for:**

- Content that may have multiple instances (pages, posts, case studies)
- User-generated content
- Time-series data (events, releases)
- Content with slug-based routing

Helix (v3) has no singletons despite having a homepage. Homepage content is embedded in the `page` document type with a specific slug.

## Migration Path (v2 to v3+)

Kariusdx (v2) uses the "parts" system for singleton actions. Migrating to v3+ requires removing custom actions and using template filtering instead.

**v2 (sanity.json):**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/document-actions/resolver",
      "path": "./schemas/documentActions.js"
    }
  ]
}
```

**v3+ (sanity.config.ts):**

```typescript
schema: {
  templates: (prev) =>
    prev.filter((template) => !singletonTypes.has(template.id)),
}
```

Template filtering is simpler and more maintainable than custom document actions for singleton enforcement.

## Anti-Patterns

**Anti-Pattern 1: No template filtering**

```typescript
// ❌ BAD: Singletons appear in "+ Create" menu
export default defineConfig({
  schema: {
    types: schemaTypes,
    // Missing templates filter
  },
})
```

Content editors can create duplicate `homepage` or `siteSettings` documents, causing frontend ambiguity.

**Anti-Pattern 2: Using array queries without [0]**

```typescript
// ❌ BAD: Returns array with one item
const homepage = await sanityFetch({ query: `*[_type == "homepage"]` })
// homepage = [{...}] instead of {...}

// ✅ GOOD: Returns single object
const homepage = await sanityFetch({ query: `*[_type == "homepage"][0]` })
// homepage = {...}
```

**Anti-Pattern 3: Dynamic singleton IDs**

```typescript
// ❌ BAD: Unpredictable IDs
.documentId(uuidv4()) // Different ID each time

// ✅ GOOD: Hardcoded, predictable IDs
.documentId('homepage')
```

Use schema type name as document ID for consistency.

## Related Patterns

- **desk-structure-customization.md** - Grouping singletons in desk structure
- **seo-metadata-objects.md** - Default SEO singleton usage
- **custom-document-actions.md** - Preventing unpublish on singletons

## References

- Ripplecom: `apps/sanity-studio/sanity.config.ts` (template filtering with 6 singletons)
- Ripplecom: `apps/sanity-studio/structure/index.ts` (singleton grouping in desk structure)
- Kariusdx: `sanity.json` (v2 singleton actions, deprecated pattern)
