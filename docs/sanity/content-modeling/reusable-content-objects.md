---
title: "Reusable Content Objects Pattern"
category: "content-modeling"
subcategory: "data-structures"
tags: ["sanity", "objects", "reusable-components", "data-modeling", "dry"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Reusable Content Objects Pattern

## Overview

Sanity object types enable reusable data structures across multiple document types and content blocks. All analyzed projects (100%) implement reusable objects for common patterns like SEO metadata, links, images, and navigation items.

**Adoption**: 100% of projects use reusable objects. Common patterns: SEO objects (100%), link objects (67%), image objects (67%), navigation items (67%).


## Object Type Characteristics

- **Not standalone**: Cannot be created/edited directly in Studio
- **Embedded**: Used within document or other object fields
- **Reusable**: Referenced in multiple schemas
- **No unique _id**: Part of parent document's data
- **Type**: `type: 'object'`

**Example**:
```typescript
export default defineType({
  name: "seo",
  type: "object",  // Not a document
  // ...
})
```

## Document Type Characteristics

- **Standalone**: Can be created/edited in Studio
- **Top-level**: Appears in document lists
- **Unique _id**: Has own document identity
- **Referenceable**: Other documents can reference it
- **Type**: `type: 'document'`

**Example**:
```typescript
export default defineType({
  name: "blogPost",
  type: "document",  // Standalone document
  // ...
})
```


## Universal Pattern (100% Adoption)

All analyzed projects implement dedicated SEO object for OpenGraph, meta tags, and search engine controls. The SEO object provides fields for meta title, meta description, OpenGraph images, canonical URLs, and indexing controls. Each document type can include the SEO object as a field for customizable search engine optimization.

**Common SEO Fields**:
- Meta title (50-60 chars) with validation
- Meta description (150-160 chars) with validation
- OpenGraph image (1200x630px recommended)
- Canonical URL override
- Indexing controls (noindex, nofollow)

**Source Confidence**: 100% (all projects implement SEO objects)

## SEO Object Implementation

```typescript
// schemaTypes/objects/seo.ts
import { SearchIcon } from '@sanity/icons'
import { defineType, defineField } from 'sanity'

export default defineType({
  name: "seo",
  type: "object",
  title: "SEO",
  icon: SearchIcon,
  fields: [
    defineField({
      name: "metaTitle",
      title: "Meta Title",
      type: "string",
      validation: (Rule) => Rule.max(60).warning("Should be 50-60 characters"),
    }),
    defineField({
      name: "metaDescription",
      title: "Meta Description",
      type: "text",
      rows: 3,
      validation: (Rule) => Rule.max(160).warning("Should be 150-160 characters"),
    }),
    defineField({
      name: "openGraphImage",
      title: "Open Graph Image",
      type: "image",
    }),
    defineField({
      name: "canonicalUrl",
      title: "Canonical URL",
      type: "url",
    }),
    defineField({
      name: "noindex",
      title: "No Index",
      type: "boolean",
      initialValue: false,
    }),
    defineField({
      name: "nofollow",
      title: "No Follow",
      type: "boolean",
      initialValue: false,
    }),
  ],
  preview: {
    select: { title: "metaTitle" },
    prepare({ title }) {
      return { title: title || "SEO Settings", subtitle: "SEO Metadata" }
    },
  },
})
```

## SEO Object Usage

```typescript
// schemaTypes/documents/page.ts
fields: [
  defineField({
    name: "seo",
    title: "SEO",
    type: "seo",  // Reference to reusable object
    group: "seo",
  }),
]
```


## Enhanced Link Object (Ripplecom Pattern)

Link objects with internal/external routing and opening behavior support both reference-based internal links and URL-based external links. The pattern uses conditional field visibility and validation to ensure appropriate data entry based on link type.

**Key Features**:
- Radio selection for internal vs external links
- Conditional field visibility (hide unused fields)
- Type-specific validation (required based on selection)
- Reference-based internal linking (prevents 404s)
- Support for multiple URL schemes (http, https, mailto, tel)
- New window control for external links

**Source Confidence**: 67% (kariusdx v2 + ripplecom v4)

## Enhanced Link Object Implementation

```typescript
// schemaTypes/objects/link.ts
import { defineType, defineField } from 'sanity'

export default defineType({
  name: "link",
  type: "object",
  title: "Link",
  fields: [
    defineField({
      name: "linkType",
      type: "string",
      options: {
        list: [
          { title: "Internal", value: "internal" },
          { title: "External", value: "external" },
        ],
        layout: "radio",
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "internalLink",
      type: "reference",
      to: [{ type: "page" }],
      hidden: ({ parent }) => parent?.linkType !== "internal",
    }),
    defineField({
      name: "externalUrl",
      type: "url",
      hidden: ({ parent }) => parent?.linkType !== "external",
    }),
    defineField({
      name: "newWindow",
      type: "boolean",
      initialValue: false,
    }),
  ],
})
```

## Simple Link Object (Minimal Pattern)

```javascript
// schemas/objects/link.js
export default {
  name: 'link',
  type: 'object',
  title: 'Link',
  fields: [
    {
      name: 'text',
      type: 'string',
      title: 'Link Text',
    },
    {
      name: 'url',
      type: 'url',
      title: 'URL',
    },
  ],
}
```

**Source Confidence**: 33% (helix v3 has no link objects)


## Featured Image Object

```javascript
// schemas/objects/featuredImage.js
export default {
  name: 'featuredImage',
  type: 'object',
  title: 'Featured Image',
  fields: [
    {
      name: 'image',
      type: 'image',
      title: 'Image',
      options: {
        hotspot: true, // Enable focal point selection
      },
    },
    {
      name: 'alt',
      type: 'string',
      title: 'Alt Text',
      description: 'Describe image for screen readers and SEO',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'caption',
      type: 'string',
      title: 'Caption',
      description: 'Optional caption displayed below image',
    },
  ],
}
```

**Usage**:
```javascript
fields: [
  {
    name: 'featuredImage',
    type: 'featuredImage',
    title: 'Featured Image',
  },
]
```

**Benefits**:
- Enforces alt text (accessibility)
- Consistent caption pattern
- Hotspot support for responsive images

**Source Confidence**: 100% (helix v3 + kariusdx v2)


## Simple Navigation Item

```typescript
// schemaTypes/objects/navigationItem.ts
export default defineType({
  name: "navigationItem",
  type: "object",
  title: "Navigation Item",
  fields: [
    defineField({
      name: "label",
      title: "Label",
      type: "string",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "link",
      title: "Link",
      type: "link",  // Reuses link object
    }),
  ],
})
```

## Navigation Dropdown Object

```typescript
// schemaTypes/objects/navigationDropdown.ts
export default defineType({
  name: "navigationDropdown",
  type: "object",
  title: "Navigation Dropdown",
  fields: [
    defineField({
      name: "label",
      title: "Label",
      type: "string",
    }),
    defineField({
      name: "columns",
      title: "Columns",
      type: "array",
      of: [
        {
          type: "object",
          fields: [
            { name: "heading", type: "string" },
            {
              name: "links",
              type: "array",
              of: [{ type: "navigationItem" }],
            },
          ],
        },
      ],
    }),
  ],
})
```

**Usage in Global Navigation**:
```typescript
// schemaTypes/globals/navigation.ts
fields: [
  defineField({
    name: "items",
    type: "array",
    of: [
      { type: "navigationItem" },    // Simple link
      { type: "navigationDropdown" }, // Mega menu
    ],
  }),
]
```

**Source Confidence**: 67% (kariusdx v2 + ripplecom v4)


## Publishing Metadata Object

```typescript
// schemaTypes/objects/metaFields.ts
export default defineType({
  name: "metaFields",
  type: "object",
  title: "Metadata",
  fields: [
    defineField({
      name: "publishedAt",
      title: "Published Date",
      type: "datetime",
      initialValue: () => new Date().toISOString(),
    }),
    defineField({
      name: "lastModified",
      title: "Last Modified",
      type: "datetime",
      readOnly: true, // Auto-updated
    }),
    defineField({
      name: "author",
      title: "Author",
      type: "reference",
      to: [{ type: "person" }],
    }),
    defineField({
      name: "featured",
      title: "Featured Content",
      type: "boolean",
      description: "Highlight on homepage",
      initialValue: false,
    }),
  ],
})
```

**Usage**:
```typescript
fields: [
  defineField({
    name: "meta",
    type: "metaFields",
    group: "meta",
  }),
]
```

**Benefits**:
- Consistent metadata across document types
- Publishing workflow support
- Author attribution

**Source Confidence**: 33% (ripplecom v4 only)


## Statistics Display Object

```typescript
// schemaTypes/objects/stat.ts
export default defineType({
  name: "stat",
  type: "object",
  title: "Statistic",
  fields: [
    defineField({
      name: "value",
      title: "Value",
      type: "string",
      description: "e.g., '50M+', '99%', '$10B'",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "label",
      title: "Label",
      type: "string",
      description: "What the statistic represents",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "suffix",
      title: "Suffix",
      type: "string",
      description: "Optional unit (e.g., 'users', 'countries')",
    }),
  ],
  preview: {
    select: {
      value: "value",
      label: "label",
    },
    prepare({ value, label }) {
      return {
        title: `${value} ${label}`,
        subtitle: "Statistic",
      }
    },
  },
})
```

**Usage in Stats Grid**:
```typescript
// schemaTypes/components/statsGrid.ts
fields: [
  defineField({
    name: "stats",
    type: "array",
    of: [{ type: "stat" }],
    validation: (Rule) => Rule.min(2).max(4),
  }),
]
```

**Source Confidence**: 33% (kariusdx v2 only)


## Contact Information Object

```typescript
// schemaTypes/objects/contactInfo.ts
export default defineType({
  name: "contactInfo",
  type: "object",
  title: "Contact Information",
  fields: [
    defineField({
      name: "email",
      type: "email",
      validation: (Rule) => Rule.email(),
    }),
    defineField({
      name: "phone",
      type: "string",
      validation: (Rule) => Rule.regex(/^\+?[0-9\s\-\(\)]+$/, {
        name: "phone",
        invert: false,
      }).error("Must be a valid phone number"),
    }),
    defineField({
      name: "address",
      type: "object",
      fields: [
        { name: "street", type: "string" },
        { name: "city", type: "string" },
        { name: "state", type: "string" },
        { name: "zip", type: "string" },
        { name: "country", type: "string" },
      ],
    }),
  ],
})
```

**Source Confidence**: 33% (ripplecom v4 only)


## Create Reusable Object When:

- Data structure used in 3+ places
- Consistent validation across uses
- Related fields form logical group
- No need for standalone document identity

**Examples**: SEO metadata, links, addresses, stats

## Create Document When:

- Content needs unique URL/identity
- Should appear in Studio document lists
- Other documents will reference it
- Content editors manage independently

**Examples**: Pages, blog posts, authors, categories

## Inline Fields When:

- Used only once
- No reuse expected
- Very simple structure (1-2 fields)

**Example**: One-off boolean or string field


## Document When Should Be Object

**Problem**: Creating `seo` as document type instead of object

**Solution**: SEO metadata should be object embedded in pages, not standalone documents

## Object When Should Be Document

**Problem**: Creating `author` as object instead of document

**Solution**: Authors should be documents so multiple posts can reference same author

## No Validation

**Problem**: Reusable objects without validation

**Solution**: Add validation to ensure data quality across all uses

```typescript
validation: (Rule) => Rule.required().max(60)
```

## Overly Generic Names

**Problem**: Objects named `data`, `info`, `content`

**Solution**: Use specific names: `seoMetadata`, `contactInfo`, `publishingMeta`


## Rendering Objects

```typescript
// components/SeoHead.tsx
import Head from 'next/head'

interface SeoProps {
  seo: {
    metaTitle?: string
    metaDescription?: string
    openGraphImage?: {
      asset: {
        url: string
      }
    }
    noindex?: boolean
  }
  fallbackTitle: string
}

export function SeoHead({ seo, fallbackTitle }: SeoProps) {
  return (
    <Head>
      <title>{seo.metaTitle || fallbackTitle}</title>
      {seo.metaDescription && (
        <meta name="description" content={seo.metaDescription} />
      )}
      {seo.openGraphImage && (
        <meta property="og:image" content={seo.openGraphImage.asset.url} />
      )}
      {seo.noindex && <meta name="robots" content="noindex,nofollow" />}
    </Head>
  )
}
```

## Querying Objects

```groq
*[_type == "page" && slug.current == $slug][0] {
  title,
  seo {
    metaTitle,
    metaDescription,
    openGraphImage {
      asset-> {
        url
      }
    },
    noindex,
    nofollow
  }
}
```

## Object Composition

Objects can contain other objects:

```typescript
// Navigation column contains navigation items
export default defineType({
  name: "navigationColumn",
  type: "object",
  fields: [
    { name: "heading", type: "string" },
    {
      name: "items",
      type: "array",
      of: [{ type: "navigationItem" }],  // Nested object
    },
  ],
})
```

**Benefit**: Build complex structures from simple, reusable objects

## Related Patterns

- **Content Block Organization**: Where to store object schemas
- **Schema Definitions**: Object type syntax and validation
- **Global Documents**: Documents vs objects for site-wide content

## See Also

- [Content Block Organization](./content-block-organization.md)
- [Global Singleton Documents](./global-singleton-documents.md)
