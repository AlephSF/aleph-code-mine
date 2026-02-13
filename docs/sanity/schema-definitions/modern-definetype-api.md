---
title: "Modern defineType API for Schema Definitions"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "typescript", "definetype", "definefield", "v3", "v4"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

# Modern defineType API for Schema Definitions

## Overview

Sanity v3+ introduced the modern `defineType()` and `defineField()` helper functions to replace object-literal schema definitions. These helpers provide enhanced TypeScript type inference, better autocomplete, and clearer code structure. Only ripplecom (v4.3.0) has fully adopted this pattern with 651 instances across 78 schema files.

## Pattern Adoption

**Adoption Rate:** 33% (1 of 3 repositories)

- **Ripplecom (v4.3.0)**: 651 instances (100% modern API)
- **Helix (v3.10.0)**: 0 instances (uses legacy object-literal pattern)
- **Kariusdx (v2.30.0)**: 0 instances (v2 doesn't support modern API)

**Observation:** Despite Helix running v3.10.0 (which supports the modern API), it continues using the v2-compatible object-literal pattern for backward compatibility.

## Modern API Pattern (v3+)

## Document Schema with defineType

Sanity v3+ provides `defineType()` for type-safe schema definitions with full TypeScript autocomplete support.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
import { DocumentTextIcon } from "@sanity/icons"
import { defineType, defineField } from "sanity"

export default defineType({
  name: "blogPost",
  title: "Blog Post",
  type: "document",
  icon: DocumentTextIcon,
  groups: [
    {
      name: "content",
      title: "Content",
      default: true,
    },
    {
      name: "meta",
      title: "Meta",
    },
    {
      name: "seo",
      title: "SEO",
    },
  ],
  fields: [
    defineField({
      name: "title",
      title: "Post Title",
      type: "string",
      validation: (Rule) => Rule.required().max(180),
      group: "content",
    }),
    defineField({
      name: "slug",
      title: "Slug",
      type: "contentSlug",
      group: "meta",
    }),
    defineField({
      name: "content",
      title: "Post Content",
      type: "richText",
      validation: (Rule) => Rule.required(),
      group: "content",
    }),
  ],
})
```

## Object Schema with defineType

Object types (embedded data structures) use the same `defineType()` pattern with `type: "object"`.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/objects/metaFields.ts
import { defineType, defineField } from "sanity"

export default defineType({
  name: "metaFields",
  title: "Meta Information",
  type: "object",
  fields: [
    defineField({
      name: "author",
      title: "Author",
      type: "reference",
      to: [{ type: "person" }],
    }),
    defineField({
      name: "publishedAt",
      title: "Published At",
      type: "datetime",
      initialValue: () => new Date().toISOString(),
    }),
    defineField({
      name: "categories",
      title: "Categories",
      type: "array",
      of: [{ type: "reference", to: [{ type: "category" }] }],
    }),
  ],
})
```

## Legacy Object-Literal Pattern (v2-Compatible)

## Document Schema (Legacy)

Helix v3.10.0 continues using the object-literal pattern for v2 compatibility despite supporting the modern API.

```javascript
// helix-dot-com-sanity/schemas/documents/blogPost.js
export default {
  name: 'blogPost',
  type: 'document',
  title: 'Blog Post',
  groups: [
    {
      name: 'mainContent',
      title: 'Main Content',
      default: true,
    },
    {
      name: 'pageSettings',
      title: 'SEO + Page Settings',
    },
  ],
  fields: [
    {
      name: 'name',
      type: 'string',
      title: 'Title',
      group: 'mainContent',
    },
    {
      name: 'docSlug',
      type: 'slug',
      title: 'Slug',
      group: 'pageSettings',
      options: {
        source: 'title',
        maxLength: 200,
      },
    },
  ],
}
```

## Sanity v2 createSchema Pattern

Kariusdx (v2.30.0) uses the legacy `createSchema()` function to register all schema types.

```javascript
// kariusdx-sanity/schemas/schema.js
import createSchema from 'part:@sanity/base/schema-creator'
import schemaTypes from 'all:part:@sanity/base/schema-type'

import page from './documents/page'
import blogPost from './documents/blogPost'
import seo from './objects/seo'

export default createSchema({
  name: 'default',
  types: schemaTypes.concat([
    page,
    blogPost,
    seo,
  ]),
})
```

## Benefits of Modern API

## Enhanced TypeScript Support

The `defineType()` and `defineField()` helpers provide superior type inference compared to object literals.

**Modern API (Full Autocomplete):**
```typescript
defineField({
  name: "publishedAt",
  type: "datetime", // ← TypeScript knows all valid Sanity types
  initialValue: () => new Date().toISOString(),
  validation: (Rule) => Rule.required(), // ← Rule methods autocomplete
})
```

**Legacy API (Limited Autocomplete):**
```javascript
{
  name: "publishedAt",
  type: "datetime", // ← No type validation
  initialValue: () => new Date().toISOString(),
  validation: (Rule) => Rule.required(), // ← No autocomplete
}
```

## Better Error Detection

The modern API catches configuration errors at development time rather than runtime.

```typescript
// TypeScript error: 'invalidType' is not a valid Sanity type
defineField({
  name: "title",
  type: "invalidType", // ← Error caught at build time
})

// Object literal: No error until Sanity Studio loads
{
  name: "title",
  type: "invalidType", // ← Error only at runtime
}
```

## Clearer Code Structure

The `defineField()` function makes field definitions visually distinct from configuration objects.

```typescript
// Modern: Clear field boundary
fields: [
  defineField({
    name: "title",
    type: "string",
  }),
  defineField({
    name: "content",
    type: "text",
  }),
]

// Legacy: Fields blend with config objects
fields: [
  {
    name: "title",
    type: "string",
  },
  {
    name: "content",
    type: "text",
  },
]
```

## Migration Path

## Incremental Migration Strategy

Sanity v3+ supports both patterns simultaneously, allowing gradual migration.

**Step 1: Install defineType/defineField**
```typescript
import { defineType, defineField } from "sanity"
```

**Step 2: Wrap Existing Schema**
```typescript
// Before
export default {
  name: "page",
  type: "document",
  fields: [/* ... */],
}

// After (minimal change)
export default defineType({
  name: "page",
  type: "document",
  fields: [/* ... */],
})
```

**Step 3: Migrate Fields Individually**
```typescript
export default defineType({
  name: "page",
  type: "document",
  fields: [
    defineField({ name: "title", type: "string" }), // ← Migrated
    { name: "slug", type: "slug" }, // ← Not yet migrated
  ],
})
```

## File Extension Consideration

The modern API works best with TypeScript (`.ts`/`.tsx`) for full type inference benefits.

**Optimal Setup:**
```typescript
// schemas/documents/page.ts (TypeScript)
import { defineType, defineField } from "sanity"
// Full autocomplete and type checking
```

**Partial Benefits:**
```javascript
// schemas/documents/page.js (JavaScript)
import { defineType, defineField } from "sanity"
// Runtime validation but no autocomplete
```

## Anti-Patterns

## Mixing Patterns Inconsistently

**❌ Bad: Mixed patterns within same schema**
```typescript
export default defineType({
  name: "page",
  fields: [
    defineField({ name: "title", type: "string" }),
    { name: "slug", type: "slug" }, // ← Inconsistent
  ],
})
```

**✅ Good: Consistent pattern**
```typescript
export default defineType({
  name: "page",
  fields: [
    defineField({ name: "title", type: "string" }),
    defineField({ name: "slug", type: "slug" }),
  ],
})
```

## Using Modern API Without TypeScript

The modern API provides limited benefits in plain JavaScript files.

**❌ Bad: Modern API in .js file**
```javascript
// page.js (no TypeScript benefits)
export default defineType({ /* ... */ })
```

**✅ Good: Modern API in .ts file**
```typescript
// page.ts (full TypeScript benefits)
export default defineType({ /* ... */ })
```

## Implementation Checklist

- [ ] Verify Sanity version ≥3.0.0
- [ ] Use TypeScript (`.ts`) for schema files to leverage type inference
- [ ] Import `defineType` and `defineField` from "sanity"
- [ ] Wrap document/object schemas with `defineType()`
- [ ] Wrap individual fields with `defineField()`
- [ ] Test schema validation in Sanity Studio
- [ ] Enable strict TypeScript mode for maximum type safety

## Related Patterns

- **Validation Rules**: Modern API improves validation rule autocomplete
- **Field Groups**: `defineField()` provides better group assignment autocomplete
- **Preview Configuration**: TypeScript infers preview select fields from schema
- **Icon Customization**: `@sanity/icons` package recommended for v3+

## Version Compatibility

| Sanity Version | defineType Support | Recommendation |
|----------------|-------------------|----------------|
| v2.x | ❌ Not available | Use object literals |
| v3.x | ✅ Available | Migrate incrementally |
| v4.x | ✅ Recommended | Use exclusively |

## References

- Ripplecom (v4.3.0): 651 instances across 78 schema files
- Sanity v3 Migration Guide: https://www.sanity.io/docs/migrating-from-v2
- TypeScript Schema Guide: https://www.sanity.io/docs/schema-types
