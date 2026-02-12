---
title: "Field Groups for Content Organization"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "field-groups", "content-organization", "tabs", "ux"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "12%"
last_updated: "2026-02-11"
---

# Field Groups for Content Organization

## Overview

Sanity field groups organize schema fields into tabs within the Studio editor, improving the content editing experience for schemas with many fields. Analyzed repositories show low overall adoption (12%) despite the pattern improving editor usability significantly. When groups are used, naming conventions are highly consistent across all projects.

## Pattern Adoption

**Adoption Rate:** 12% (18 of 147 schemas)

- **Helix (v3)**: 1 instance (20% of schemas)
- **Kariusdx (v2)**: 4 instances (6% of schemas)
- **Ripplecom (v4)**: 13 instances (17% of schemas)

**Observation:** Low adoption suggests field groups are underutilized despite providing clear UX benefits for content-heavy schemas.

## Standard Pattern: Content + Meta/SEO Separation

### Two-Group Pattern (Most Common)

The most common field group pattern separates main content from administrative/SEO fields.

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
      default: true, // ← Opens this tab by default
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
      group: 'mainContent', // ← Assign field to group
    },
    {
      name: 'content',
      type: 'array',
      title: 'Content',
      group: 'mainContent',
      of: [{ type: 'block' }],
    },
    {
      name: 'seo',
      type: 'seoFields',
      title: 'SEO Settings',
      group: 'pageSettings',
    },
  ],
}
```

### Three-Group Pattern (Ripplecom Standard)

Ripplecom separates content, metadata, and SEO into distinct tabs for clearer organization.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
import { defineType, defineField } from "sanity"

export default defineType({
  name: "blogPost",
  title: "Blog Post",
  type: "document",
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
      group: "content",
    }),
    defineField({
      name: "featuredImage",
      title: "Featured Image",
      type: "image",
      group: "content",
    }),
    defineField({
      name: "slug",
      title: "Slug",
      type: "contentSlug",
      group: "meta", // ← Publishing/taxonomy fields
    }),
    defineField({
      name: "categories",
      title: "Categories",
      type: "array",
      of: [{ type: "reference", to: [{ type: "category" }] }],
      group: "meta",
    }),
    defineField({
      name: "seoTitle",
      title: "SEO Title",
      type: "string",
      group: "seo", // ← Search engine optimization
    }),
  ],
})
```

## Group Naming Conventions

### Standard Group Names (100% Consistency)

Across all projects using field groups, naming follows these consistent patterns:

**Content Groups:**
- `mainContent` / `content` — Primary editorial content
- `pageSettings` / `settings` — Configuration and administrative fields
- `seo` / `meta` — SEO metadata and publishing information

**Multi-Tab Examples:**

```typescript
// Pattern 1: Content + Settings
groups: [
  { name: "mainContent", title: "Main Content", default: true },
  { name: "pageSettings", title: "SEO + Page Settings" },
]

// Pattern 2: Content + Meta + SEO
groups: [
  { name: "content", title: "Content", default: true },
  { name: "meta", title: "Meta" },
  { name: "seo", title: "SEO" },
]
```

### Default Tab Configuration

The `default: true` property sets which tab opens when editors create or edit a document.

```javascript
groups: [
  {
    name: 'mainContent',
    title: 'Main Content',
    default: true, // ← This tab opens first
  },
  {
    name: 'pageSettings',
    title: 'SEO + Page Settings',
    // default not set, opens when clicked
  },
]
```

## Field Assignment to Groups

### Explicit Group Assignment

Fields must explicitly declare their group via the `group` property.

```typescript
fields: [
  defineField({
    name: "title",
    type: "string",
    group: "content", // ← Explicit assignment required
  }),
  defineField({
    name: "slug",
    type: "slug",
    group: "meta", // ← Different tab
  }),
]
```

### Fields Without Group Assignment

Fields without a `group` property appear in a default "Ungrouped" tab.

```typescript
// ❌ Bad: Ungrouped field creates extra tab
fields: [
  defineField({
    name: "title",
    type: "string",
    group: "content",
  }),
  defineField({
    name: "publishedAt",
    type: "datetime",
    // Missing group assignment → appears in "Ungrouped" tab
  }),
]
```

## When to Use Field Groups

### Schemas That Benefit from Groups

Field groups provide the most value for schemas with 5+ fields or distinct conceptual sections.

**Ideal Candidates:**
- **Page/Blog Post**: Content, SEO, publishing metadata (5-15 fields)
- **Person/Staff**: Bio, contact info, social links, photo (8-12 fields)
- **Event**: Details, location, registration, sponsors (10-20 fields)
- **Product**: Description, pricing, inventory, shipping (8-15 fields)

### Schemas That Don't Need Groups

Simple schemas with 3-4 fields rarely benefit from tabs.

**Skip Groups For:**
- **Category**: Name, slug, description (3 fields)
- **Tag**: Name, slug (2 fields)
- **Settings**: Single-purpose configuration objects (2-4 fields)

## Complex Example: Kariusdx Page Schema

### Multi-Section Document with Conditional Fields

Kariusdx page schema demonstrates groups with extensive conditional field visibility.

```javascript
// kariusdx-sanity/schemas/documents/page.js
export default {
  name: 'page',
  type: 'document',
  title: 'Page',
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
    // Main Content Group
    {
      name: 'title',
      type: 'string',
      title: 'Title',
      group: 'mainContent',
    },
    {
      name: 'heroImage',
      type: 'image',
      title: 'Hero Image',
      group: 'mainContent',
      hidden: ({document}) => document?.slug?.current == 'mobile-app',
    },
    {
      name: 'pageBuilder',
      type: 'pageBuilder',
      title: 'Page Builder',
      group: 'mainContent',
    },

    // Page Settings Group
    {
      name: 'slug',
      type: 'slug',
      title: 'Slug',
      group: 'pageSettings',
      options: {
        source: 'title',
        maxLength: 200,
      },
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'seo',
      type: 'seo',
      title: 'SEO',
      group: 'pageSettings',
    },
  ],
}
```

## Benefits of Field Groups

### Reduced Cognitive Load

Editors see 5-7 fields per tab instead of 15-20 fields in one scrolling list.

**Without Groups (Overwhelming):**
```
[ Title ]
[ Subheader ]
[ Hero Image ]
[ Content ]
[ Featured Image ]
[ Slug ]
[ Published At ]
[ Author ]
[ Categories ]
[ Tags ]
[ SEO Title ]
[ SEO Description ]
[ OG Image ]
[ Canonical URL ]
[ No-Index Checkbox ]
```

**With Groups (Organized):**
```
Tab: Content               Tab: Meta              Tab: SEO
[ Title ]                  [ Slug ]               [ SEO Title ]
[ Subheader ]              [ Published At ]       [ SEO Description ]
[ Hero Image ]             [ Author ]             [ OG Image ]
[ Content ]                [ Categories ]         [ Canonical URL ]
[ Featured Image ]         [ Tags ]               [ No-Index ]
```

### Workflow Optimization

Content editors can focus on editorial fields without distraction from technical SEO settings.

```typescript
// Typical editor workflow:
// 1. Open "Content" tab (default) → Write content
// 2. Switch to "Meta" tab → Set categories, publish date
// 3. Switch to "SEO" tab → Optimize for search (optional)
```

### Logical Grouping by Responsibility

Different team members can focus on their domain without navigating irrelevant fields.

- **Content Editors**: Work in "Content" tab only
- **Publishers**: Set metadata in "Meta" tab
- **SEO Specialists**: Optimize in "SEO" tab

## Anti-Patterns

### Too Many Groups

More than 4-5 groups creates excessive tab switching.

**❌ Bad: Over-segmented**
```typescript
groups: [
  { name: "title", title: "Title" },
  { name: "body", title: "Body" },
  { name: "image", title: "Image" },
  { name: "slug", title: "Slug" },
  { name: "categories", title: "Categories" },
  { name: "seo", title: "SEO" },
]
// 6 tabs for 6 fields = excessive clicking
```

**✅ Good: Balanced grouping**
```typescript
groups: [
  { name: "content", title: "Content" }, // title, body, image
  { name: "meta", title: "Meta" }, // slug, categories
  { name: "seo", title: "SEO" }, // seo fields
]
// 3 tabs for 6 fields = logical organization
```

### Inconsistent Naming

Different group names for the same concept confuses editors across schemas.

**❌ Bad: Inconsistent names**
```typescript
// blogPost.ts
groups: [{ name: "content", title: "Content" }]

// page.ts
groups: [{ name: "mainContent", title: "Main Content" }]

// event.ts
groups: [{ name: "details", title: "Details" }]
```

**✅ Good: Consistent naming**
```typescript
// All document types use same group names
groups: [
  { name: "content", title: "Content" },
  { name: "meta", title: "Meta" },
  { name: "seo", title: "SEO" },
]
```

### Forgetting Default Tab

Without `default: true`, the Studio opens the first alphabetically-sorted tab, not necessarily the logical starting point.

**❌ Bad: No default specified**
```typescript
groups: [
  { name: "seo", title: "SEO" }, // Opens first alphabetically
  { name: "content", title: "Content" },
]
```

**✅ Good: Explicit default**
```typescript
groups: [
  { name: "content", title: "Content", default: true }, // Opens first
  { name: "seo", title: "SEO" },
]
```

## Implementation Checklist

- [ ] Identify schemas with 5+ fields that would benefit from grouping
- [ ] Use consistent group names across all schemas (`content`, `meta`, `seo`)
- [ ] Set `default: true` on the primary content group
- [ ] Assign all fields to a group (avoid "Ungrouped" tab)
- [ ] Keep group count to 2-4 tabs maximum
- [ ] Test editor workflow: Can editors complete tasks within 1-2 tab switches?

## Related Patterns

- **Conditional Field Visibility**: `hidden` property works independently of groups
- **Validation Rules**: Validation applies regardless of group assignment
- **Preview Configuration**: Preview can select fields from any group

## Gap Analysis

**Current Adoption:** 12% (18 of 147 schemas)

**Recommendation:** Increase adoption to 40-50% by adding groups to content-heavy schemas (pages, posts, events, people) that currently have 5+ ungrouped fields.

**Impact:** Improved editor experience and reduced cognitive load for content teams.

## References

- Helix (v3): 1 instance (blogPost.js)
- Kariusdx (v2): 4 instances (page.js, pathogen.js, pressRelease.js, staff.js)
- Ripplecom (v4): 13 instances across document schemas
- Sanity Field Groups Documentation: https://www.sanity.io/docs/field-groups
