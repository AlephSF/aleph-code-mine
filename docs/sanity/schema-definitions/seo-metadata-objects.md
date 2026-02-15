---
title: "SEO Metadata Objects"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "seo", "metadata", "opengraph", "schema-org", "search-optimization"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# SEO Metadata Objects

## Overview

All analyzed Sanity repositories implement dedicated SEO metadata object schemas that encapsulate search engine optimization fields. SEO objects are reusable across document types (pages, blog posts, events) and consistently include title, description, Open Graph fields, and robots directives. This pattern has 100% adoption with 178 SEO/meta field references across 147 schemas.

## Pattern Adoption

**Adoption Rate:** 100% (all 3 repositories)

**SEO Field Density:**
- **Ripplecom (v4)**: 141 SEO/meta references (1.8 per schema)
- **Helix (v3)**: 15 SEO references (3.0 per schema)
- **Kariusdx (v2)**: 22 SEO references (0.34 per schema)

**Total:** 178 SEO/metadata field references


## Core SEO Fields Object

All projects define a reusable SEO object type with common search optimization fields.

```javascript
// helix-dot-com-sanity/schemas/objects/seo.js
export default {
  name: 'seoFields',
  type: 'object',
  title: 'SEO Fields',
  fields: [
    {
      name: 'focusKeyword',
      title: 'Focus Keyword',
      type: 'string',
      description: 'Set this word or phrase to get a good analysis of your content on the SEO pane.',
    },
    {
      name: 'seoTitle',
      title: 'SEO Title',
      type: 'string',
      description: 'Use this field to override the title of this content in search results.',
    },
    {
      name: 'seoDescription',
      title: 'SEO Description',
      type: 'text',
      description: 'Use this field to create a meta description for SEO.',
    },
    {
      name: 'canonicalUrl',
      title: 'Canonical URL',
      type: 'url',
      description: 'Use this field to use a different url for this content as the canonical source of truth.',
    },
    {
      name: 'noindex',
      title: 'noindex this content',
      type: 'boolean',
      description: 'Use this field to ask search engines NOT to index this content.',
    },
    {
      name: 'nofollow',
      title: 'nofollow this content',
      type: 'boolean',
      description: 'Use this field to set this content as "nofollow" for search engines.',
    },
  ],
}
```

## Usage in Document Schemas

SEO objects are embedded in document schemas via field reference.

```javascript
// helix-dot-com-sanity/schemas/documents/blogPost.js
export default {
  name: 'blogPost',
  type: 'document',
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
      name: 'seo',
      type: 'seoFields', // ← Reference to SEO object schema
      title: 'SEO Settings',
      group: 'pageSettings',
    },
  ],
}
```


## SEO Title Override

All projects provide a way to override the document title for search results.

**Field Names:**
- `seoTitle` (Helix, Kariusdx)
- `metaTitle` (Ripplecom)

```typescript
{
  name: 'seoTitle',
  type: 'string',
  title: 'SEO Title',
  validation: (Rule) => Rule.max(60),
  description: 'Optimal length: 50-60 characters for search results',
}
```

## Meta Description

All projects include a meta description field for search result snippets.

**Field Names:**
- `seoDescription` (Helix)
- `metaDescription` (Ripplecom)
- `description` (Kariusdx)

```typescript
{
  name: 'seoDescription',
  type: 'text',
  title: 'SEO Description',
  validation: (Rule) => Rule.max(160),
  description: 'Optimal length: 150-160 characters',
}
```

## Canonical URL

All projects support canonical URL specification to prevent duplicate content issues.

```typescript
{
  name: 'canonicalUrl',
  type: 'url',
  title: 'Canonical URL',
  description: 'Use this field to specify the canonical source of truth for this content.',
}
```

## Robots Directives (noindex/nofollow)

All projects provide boolean flags to control search engine crawling and indexing.

```javascript
{
  name: 'noindex',
  type: 'boolean',
  title: 'noindex this content',
  description: 'Ask search engines NOT to index this content.',
},
{
  name: 'nofollow',
  type: 'boolean',
  title: 'nofollow this content',
  description: 'Set this content as "nofollow" for search engines.',
}
```


## Open Graph Image

All projects include Open Graph image fields for social media sharing.

```javascript
// helix-dot-com-sanity/schemas/objects/seo.js
{
  name: 'ogImage',
  title: 'OpenGraph Image',
  type: 'image',
  description: 'Use this field to include an OpenGraph image for e.g. social media shares.',
}
```

## Open Graph Title and Description

Projects provide separate Open Graph fields to customize social media appearance.

```javascript
{
  name: 'openGraphUrl',
  title: 'OpenGraph URL',
  type: 'url',
  description: 'Use this field to use a different url for OpenGraph integrations such as social media shares.',
},
{
  name: 'ogDescription',
  title: 'OpenGraph Description',
  type: 'text',
  description: 'Use this field to create a different description than the meta description for social shares.',
}
```


## Separate SEO and Meta Objects

Ripplecom (v4) separates publishing metadata from SEO optimization into distinct object types.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/objects/metaFields.ts
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
      name: "updatedAt",
      title: "Last Updated",
      type: "datetime",
    }),
  ],
})
```

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/objects/seo.ts
export default defineType({
  name: "seo",
  title: "SEO",
  type: "object",
  fields: [
    defineField({
      name: "title",
      title: "SEO Title",
      type: "string",
      validation: (Rule) => Rule.max(60),
    }),
    defineField({
      name: "description",
      title: "Meta Description",
      type: "text",
      validation: (Rule) => Rule.max(160),
    }),
    defineField({
      name: "image",
      title: "Social Share Image",
      type: "image",
    }),
  ],
})
```

## Usage: Separate Tabs for Meta and SEO

Documents use separate field groups for publishing metadata and SEO optimization.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
export default defineType({
  name: "blogPost",
  groups: [
    { name: "content", title: "Content", default: true },
    { name: "meta", title: "Meta" },
    { name: "seo", title: "SEO" },
  ],
  fields: [
    defineField({
      name: "title",
      type: "string",
      group: "content",
    }),
    defineField({
      name: "meta",
      type: "metaFields", // ← Publishing information
      group: "meta",
    }),
    defineField({
      name: "seo",
      type: "seo", // ← Search optimization
      group: "seo",
    }),
  ],
})
```


## SEO Analysis Support

Helix includes focus keyword and synonym fields for SEO analysis tools.

```javascript
{
  name: 'focusKeyword',
  title: 'Focus Keyword',
  type: 'string',
  description: 'Set this word or phrase to get a good analysis of your content on the SEO pane.',
},
{
  name: 'focusSynonyms',
  title: 'Focus Synonyms',
  type: 'string',
  description: 'A comma delimited list of other focus keywords',
}
```

**Use Case:** Integration with SEO analysis tools (Yoast-like functionality) to score content based on keyword usage.


## Character Limits for SEO Fields

SEO fields should enforce character limits aligned with search engine guidelines.

```typescript
// SEO Title: 50-60 characters optimal
defineField({
  name: "seoTitle",
  type: "string",
  validation: (Rule) =>
    Rule.max(60).warning("Titles over 60 characters may be truncated in search results"),
  description: "Optimal: 50-60 characters",
})

// Meta Description: 150-160 characters optimal
defineField({
  name: "metaDescription",
  type: "text",
  validation: (Rule) =>
    Rule.max(160).warning("Descriptions over 160 characters may be truncated"),
  description: "Optimal: 150-160 characters",
})
```

## Required vs Optional SEO Fields

Most SEO fields are optional; only page-specific overrides should be required.

```typescript
// ❌ Bad: Required SEO title (forces override even when default title is good)
validation: (Rule) => Rule.required()

// ✅ Good: Optional SEO title (only override when needed)
validation: (Rule) => Rule.max(60)
```


## Frontend Fallback Pattern

SEO fields are typically optional; frontend code falls back to default values.

**Schema (Optional Fields):**
```typescript
{
  name: 'seo',
  type: 'object',
  fields: [
    { name: 'title', type: 'string' }, // Optional
    { name: 'description', type: 'text' }, // Optional
  ],
}
```

**Frontend (Fallback Logic):**
```typescript
// Next.js generateMetadata example
export async function generateMetadata({ params }) {
  const page = await getPageData(params.slug)

  return {
    title: page.seo?.title || page.title, // ← Fallback to page title
    description: page.seo?.description || page.excerpt, // ← Fallback to excerpt
    openGraph: {
      images: [page.seo?.ogImage || page.featuredImage],
    },
  }
}
```


## Minimal SEO Object

Essential fields only for basic search optimization.

```typescript
export default defineType({
  name: "seo",
  type: "object",
  fields: [
    defineField({
      name: "title",
      type: "string",
      validation: (Rule) => Rule.max(60),
    }),
    defineField({
      name: "description",
      type: "text",
      validation: (Rule) => Rule.max(160),
    }),
    defineField({
      name: "noindex",
      type: "boolean",
      initialValue: false,
    }),
  ],
})
```

## Comprehensive SEO Object

Full-featured SEO object with social media and advanced options.

```typescript
export default defineType({
  name: "seoComplete",
  type: "object",
  fields: [
    // Basic SEO
    defineField({ name: "title", type: "string", validation: (Rule) => Rule.max(60) }),
    defineField({ name: "description", type: "text", validation: (Rule) => Rule.max(160) }),
    defineField({ name: "keywords", type: "array", of: [{ type: "string" }] }),

    // Canonical & Robots
    defineField({ name: "canonicalUrl", type: "url" }),
    defineField({ name: "noindex", type: "boolean" }),
    defineField({ name: "nofollow", type: "boolean" }),

    // Open Graph
    defineField({ name: "ogTitle", type: "string" }),
    defineField({ name: "ogDescription", type: "text" }),
    defineField({ name: "ogImage", type: "image" }),
    defineField({ name: "ogUrl", type: "url" }),

    // Twitter Card
    defineField({ name: "twitterCard", type: "string", options: { list: ["summary", "summary_large_image"] } }),
    defineField({ name: "twitterCreator", type: "string" }),

    // Schema.org
    defineField({ name: "schemaType", type: "string" }),
  ],
})
```


## Duplicating SEO Fields Across Schemas

Don't copy SEO fields into every document schema; use a reusable object type.

**❌ Bad: Duplicated fields**
```typescript
// blogPost.ts
fields: [
  { name: "seoTitle", type: "string" },
  { name: "seoDescription", type: "text" },
  { name: "canonicalUrl", type: "url" },
]

// page.ts (duplicate definition)
fields: [
  { name: "seoTitle", type: "string" },
  { name: "seoDescription", type: "text" },
  { name: "canonicalUrl", type: "url" },
]
```

**✅ Good: Reusable object**
```typescript
// seo.ts (defined once)
export default defineType({ name: "seo", type: "object", fields: [/* ... */] })

// blogPost.ts (reference)
fields: [{ name: "seo", type: "seo" }]

// page.ts (reference)
fields: [{ name: "seo", type: "seo" }]
```

## Required SEO Fields Without Defaults

Don't require SEO overrides; use optional fields with frontend fallbacks.

**❌ Bad: Forces editors to duplicate content**
```typescript
{
  name: 'seo',
  type: 'object',
  fields: [
    { name: 'title', type: 'string', validation: (Rule) => Rule.required() },
    // ↑ Forces editors to enter SEO title even when page title is perfect
  ],
}
```

**✅ Good: Optional with fallback**
```typescript
{
  name: 'seo',
  type: 'object',
  fields: [
    { name: 'title', type: 'string', validation: (Rule) => Rule.max(60) },
    // ↑ Only override when page title is not ideal for SEO
  ],
}
```

## Missing Validation on Character Limits

Always validate SEO field lengths to prevent truncation in search results.

**❌ Bad: No validation**
```typescript
{ name: 'seoTitle', type: 'string' }
// ↑ Editors can enter 200+ character titles that get truncated
```

**✅ Good: Character limit validation**
```typescript
{
  name: 'seoTitle',
  type: 'string',
  validation: (Rule) => Rule.max(60).warning("May be truncated after 60 characters"),
  description: "Optimal: 50-60 characters",
}
```

## Implementation Checklist

- [ ] Create reusable SEO object schema (`seo.ts` or `seoFields.ts`)
- [ ] Include core fields: title, description, canonicalUrl, noindex, nofollow
- [ ] Add Open Graph fields: ogImage, ogTitle, ogDescription
- [ ] Set validation: max(60) for titles, max(160) for descriptions
- [ ] Make SEO fields optional (rely on frontend fallbacks)
- [ ] Add clear descriptions explaining when to override defaults
- [ ] Reference SEO object in document schemas (pages, posts, events)
- [ ] Group SEO fields in dedicated tab (e.g., "SEO" or "Page Settings")
- [ ] Test: Verify frontend falls back to default values when SEO fields are empty

## Related Patterns

- **Field Groups**: Group SEO fields in "SEO" or "Page Settings" tab
- **Validation Rules**: Use `.warning()` for length recommendations
- **Initial Values**: Set `initialValue: false` for noindex/nofollow booleans
- **Preview Configuration**: Show SEO title in preview if present

## References

- Helix (v3): 15 SEO references (seoFields object with focusKeyword)
- Kariusdx (v2): 22 SEO references (seo object)
- Ripplecom (v4): 141 references (separate meta and seo objects, 1.8 per schema)
- Google SEO Guidelines: https://developers.google.com/search/docs/appearance/title-link
- Open Graph Protocol: https://ogp.me/
