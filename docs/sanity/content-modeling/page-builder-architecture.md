---
title: "Page Builder Architecture Patterns"
category: "content-modeling"
subcategory: "page-composition"
tags: ["sanity", "page-builder", "content-blocks", "modular-content"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

# Page Builder Architecture Patterns

## Overview

Sanity CMS supports modular page composition through array-based page builders. Two dominant patterns emerge from production codebases: flat content arrays (modern approach) and nested section wrappers (legacy approach). This architecture enables content editors to compose pages from reusable blocks without developer intervention.

**Adoption**: 67% of analyzed projects (kariusdx v2 + ripplecom v4) use page builder architecture. Helix v3 uses simple field-based content structure.

## Flat Content Array Pattern (Modern)

Ripplecom (Sanity v4) implements a flat array structure where each section type is self-contained and added directly to the page's `content` field.

**Structure**:
- Single `content` array field on page document
- Each section is an object type (not nested)
- 15+ section types available
- No wrapper objects required

**Benefits**:
- Simpler content structure
- Easier to query with GROQ
- Better performance (fewer nested objects)
- Cleaner Studio UI

## Implementation Example

```typescript
// schemaTypes/documents/page.ts
import { defineType, defineField } from "sanity"

export default defineType({
  name: "page",
  title: "Page",
  type: "document",
  fields: [
    defineField({
      name: "content",
      title: "Page Content",
      type: "array",
      of: [
        { type: "heroSection" },
        { type: "textSection" },
        { type: "imageSection" },
        { type: "video" },
        { type: "cardGrid" },
        { type: "quote" },
        { type: "ctaSection" },
        { type: "spacer" },
      ],
      group: "content",
    }),
  ],
})
```

## Section Component Structure

```typescript
// schemaTypes/components/heroSection.ts
export default defineType({
  name: "heroSection",
  title: "Hero Section",
  type: "object",
  fields: [
    defineField({
      name: "headline",
      title: "Headline",
      type: "string",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "subheadline",
      title: "Subheadline",
      type: "text",
      rows: 2,
    }),
    defineField({
      name: "backgroundImage",
      title: "Background Image",
      type: "image",
    }),
    defineField({
      name: "primaryCta",
      title: "Primary CTA",
      type: "object",
      fields: [
        { name: "text", title: "Button Text", type: "string" },
        { name: "link", title: "Link", type: "link" },
      ],
    }),
  ],
})
```

## Nested Section Wrapper Pattern (Legacy)

Kariusdx (Sanity v2) implements a nested structure where a `pageSection` wrapper provides layout controls and contains an `innerBlocks` array for content.

**Structure**:
- Top-level `pageBuilder` array field
- `pageSection` wrapper object with:
  - Layout controls (background color, padding)
  - `innerBlocks` array (nested content)
- 20+ builder block types

**Benefits**:
- Consistent section styling
- Visual grouping in Studio
- Layout flexibility per section

**Tradeoffs**:
- Deeply nested data structure
- More complex GROQ queries
- Potential performance impact

## Implementation Example

```javascript
// schemas/fields/pageBuilder.js
export default {
  name: 'pageBuilder',
  type: 'array',
  title: 'Page sections',
  description: 'Add, edit, and reorder sections',
  of: [
    { type: 'pageSection' },
    { type: 'pathogenList' },
    { type: 'wistiaEmbed' },
    { type: 'jobPostings' },
  ]
}
```

## Section Wrapper Implementation

See "Nested Section Wrapper Code Example" subsection below for full implementation.

## Nested Section Wrapper Code Example

```javascript
// schemas/builderBlocks/pageSection.js
export default {
  name: 'pageSection',
  type: 'object',
  title: 'Page Section',
  fields: [
    {
      name: 'sectionTitle',
      type: 'string',
      description: 'Display the following text as section title',
    },
    {
      name: 'backgroundcolor',
      type: 'string',
      options: {
        list: [
          {value: 'none', title: 'None'},
          {value: 'gray', title: 'Gray'},
          {value: 'darkBlue', title: 'Dark Blue'},
        ],
      },
      initialValue: 'none',
    },
    {
      name: 'innerBlocks',
      type: 'array',
      of: [
        { type: 'button' },
        { type: 'richText' },
        { type: 'imageCarousel' },
        { type: 'cardContent' },
        { type: 'hubspotForm' },
        // ... 15 more block types
      ],
      validation: Rule => Rule.required()
    },
  ],
  preview: {
    select: {
      title: 'sectionTitle',
      block0: 'innerBlocks.0._type',
      block1: 'innerBlocks.1._type',
    },
  }
}
```


## Flat Structure Query (Ripplecom)

GROQ queries for flat content arrays are straightforward with direct array expansion:

```groq
*[_type == "page" && path.current == $path][0] {
  title,
  content[] {
    _type,
    _type == "heroSection" => {
      headline,
      subheadline,
      backgroundImage {
        asset->
      }
    },
    _type == "textSection" => {
      heading,
      text[] {
        ...,
        _type == "image" => {
          asset->
        }
      }
    }
  }
}
```

## Nested Structure Query (Kariusdx)

Nested structures require multiple levels of array expansion:

```groq
*[_type == "page" && slug.current == $slug][0] {
  title,
  pageBuilder[] {
    _type,
    _type == "pageSection" => {
      sectionTitle,
      backgroundcolor,
      innerBlocks[] {
        _type,
        _type == "richText" => {
          content[]
        },
        _type == "cardContent" => {
          cards[] {
            title,
            description
          }
        }
      }
    }
  }
}
```


## Choose Flat Content Array When:

- Building new Sanity v3+ projects
- Performance is critical (fewer nested objects)
- Content structure is straightforward
- Developers prefer simpler GROQ queries

**Source Confidence**: 33% (ripplecom v4 only)

## Choose Nested Section Wrapper When:

- Consistent section styling is required (background colors, padding)
- Visual grouping improves editor experience
- Migrating from existing nested architecture
- Layout flexibility per section is valuable

**Source Confidence**: 33% (kariusdx v2 only)

## Skip Page Builder When:

- Content structure is simple (blog posts, basic pages)
- Team size is small (< 3 content editors)
- Build time is constrained

**Source Confidence**: 33% (helix v3 uses simple fields)


## React Component Mapping (Flat Structure)

```typescript
// components/PageBuilder.tsx
const componentMap = {
  heroSection: HeroSection,
  textSection: TextSection,
  imageSection: ImageSection,
  cardGrid: CardGrid,
}

export function PageBuilder({ content }: { content: ContentBlock[] }) {
  return (
    <>
      {content.map((block) => {
        const Component = componentMap[block._type]
        if (!Component) return null
        return <Component key={block._key} {...block} />
      })}
    </>
  )
}
```

## React Component Mapping (Nested Structure)

```typescript
// components/PageBuilder.tsx
const blockMap = {
  richText: RichTextBlock,
  imageCarousel: ImageCarousel,
  cardContent: CardContent,
}

export function PageBuilder({ pageBuilder }: { pageBuilder: PageSection[] }) {
  return (
    <>
      {pageBuilder.map((section) => {
        if (section._type === 'pageSection') {
          return (
            <Section
              key={section._key}
              background={section.backgroundcolor}
            >
              {section.innerBlocks.map((block) => {
                const Component = blockMap[block._type]
                if (!Component) return null
                return <Component key={block._key} {...block} />
              })}
            </Section>
          )
        }
        return null
      })}
    </>
  )
}
```


## Nested Array Issues

**Problem**: Sanity's array input renderer can experience TypeErrors with deeply nested arrays (`array` containing `array`).

**Solution**: Wrap inner content arrays in an `object` type:

```typescript
// ❌ Problematic: array within array
{
  name: "richText",
  type: "array", // Problem if used in pageBuilder array
  of: [{ type: "block" }],
}

// ✅ Correct: object wrapper
{
  name: "richText",
  type: "object", // Wrapper to prevent nesting issues
  fields: [
    {
      name: "content",
      type: "array",
      of: [{ type: "block" }],
    },
  ],
}
```

**Source**: Ripplecom v4 codebase comments document this pattern explicitly.

## Excessive Block Types

**Problem**: 30+ block types overwhelm content editors.

**Solution**: Group related blocks into categories using `groups` field:

```typescript
of: [
  { type: "heroSection", group: "hero" },
  { type: "textSection", group: "content" },
  { type: "cardGrid", group: "content" },
  { type: "ctaSection", group: "cta" },
]
```

## Missing Preview Configuration

**Problem**: Content editors cannot distinguish between similar blocks without preview.

**Solution**: Implement custom previews for all block types:

```typescript
preview: {
  select: {
    title: "headline",
    media: "backgroundImage",
  },
  prepare({ title, media }) {
    return {
      title: title || "Hero Section",
      subtitle: "Hero",
      media,
    }
  },
}
```


## From Simple Fields to Page Builder

**Phase 1**: Create parallel `content` array field alongside existing fields

**Phase 2**: Migrate content programmatically or manually

**Phase 3**: Deprecate old fields once migration is complete

**Phase 4**: Remove deprecated fields after validation

## From Nested to Flat Structure

**Phase 1**: Create new section types that match old innerBlocks

**Phase 2**: Write migration script to flatten nested structure

**Phase 3**: Update frontend rendering logic

**Phase 4**: Archive legacy `pageSection` wrapper

**Source**: Ripplecom v4 demonstrates this pattern with `legacy/sections/` folder containing 16 deprecated section types.

## Related Patterns

- **Content Block Organization**: Folder structure for components vs builderBlocks
- **Rich Text Configuration**: Portable text patterns within page builders
- **Global Documents**: Site-wide content that doesn't use page builder

## See Also

- [Content Block Naming Conventions](./content-block-naming-conventions.md)
- [Reusable Content Objects](./reusable-content-objects.md)
- [Rich Text Configuration](./rich-text-configuration.md)
