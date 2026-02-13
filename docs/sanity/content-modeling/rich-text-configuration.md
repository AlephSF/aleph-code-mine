---
title: "Rich Text Configuration Patterns"
category: "content-modeling"
subcategory: "content-editing"
tags: ["sanity", "portable-text", "rich-text", "block-content", "wysiwyg"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Rich Text Configuration Patterns

## Overview

Sanity Portable Text (formerly Block Content) provides structured rich text editing with customizable styles, marks, and inline objects. All analyzed projects (100%) implement Portable Text for rich content, with patterns ranging from simple text to complex multimedia blocks.

**Adoption**: 100% use Portable Text / block content for rich editing. Configuration complexity varies: minimal (helix), standard (kariusdx), extensive (ripplecom).

## Portable Text Architecture

Portable Text stores content as structured JSON rather than HTML, enabling:

- **Structured Data**: Content is queryable with GROQ
- **Frontend Flexibility**: Same content renders differently per platform
- **Version Control**: JSON diffs are meaningful
- **Validation**: Schema-level content validation
- **Customization**: Custom marks, styles, and inline objects

## Rich Text as Object Wrapper Pattern

Ripplecom (v4) wraps Portable Text in an `object` type to prevent nested array issues when used in page builders:

**Problem**: Sanity's array input renderer experiences TypeErrors with nested arrays (`array` containing `array`).

**Solution**: Wrap block content in object with `content` field.

## Implementation Example

```typescript
// schemaTypes/fields/richText.ts
import { defineType, defineField, defineArrayMember } from "sanity"

export default defineType({
  name: "richText",
  type: "object",
  title: "Rich Text",
  fields: [
    defineField({
      name: "content",
      title: "Content",
      type: "array",
      of: [
        defineArrayMember({
          type: "block",
          styles: [
            { title: "Normal", value: "normal" },
            { title: "Heading 2", value: "h2" },
            { title: "Heading 3", value: "h3" },
            { title: "Quote", value: "blockquote" },
          ],
          lists: [
            { title: "Bullet", value: "bullet" },
            { title: "Numbered", value: "number" },
          ],
          marks: {
            decorators: [
              { title: "Bold", value: "strong" },
              { title: "Italic", value: "em" },
              { title: "Code", value: "code" },
            ],
            annotations: [defineField({ name: "link", type: "link" })],
          },
        }),
        defineArrayMember({ type: "image", name: "inlineImage" }),
        defineArrayMember({ type: "video", name: "inlineVideo" }),
      ],
    }),
  ],
})
```

## Rich Text Data Structure

Sanity Portable Text stores content as structured JSON with block-level and inline elements:

```json
{
  "_type": "richText",
  "content": [
    {
      "_type": "block",
      "style": "normal",
      "children": [
        { "_type": "span", "text": "Hello ", "marks": [] },
        { "_type": "span", "text": "world", "marks": ["strong"] }
      ]
    }
  ]
}
```

## Direct Array Pattern

Kariusdx (v2) and Helix (v3) use Portable Text as direct array fields:

## Standard Configuration Example

```javascript
// schemas/fields/richTextCustom.js
export default {
  name: 'richTextCustom',
  type: 'array',
  title: 'Rich Text',
  of: [
    {
      type: 'block',
      styles: [
        { title: 'Normal', value: 'normal' },
        { title: 'H2', value: 'h2' },
        { title: 'H3', value: 'h3' },
      ],
      lists: [
        { title: 'Bullet', value: 'bullet' },
      ],
      marks: {
        decorators: [
          { title: 'Strong', value: 'strong' },
          { title: 'Emphasis', value: 'em' },
        ],
        annotations: [
          {
            name: 'link',
            type: 'object',
            title: 'Link',
            fields: [
              {
                name: 'href',
                type: 'url',
                title: 'URL',
              },
            ],
          },
        ],
      },
    },
  ],
}
```

**Usage**: Directly in document fields or as custom field type

```javascript
{
  name: 'body',
  type: 'richTextCustom',
  title: 'Body Content',
}
```

## Custom Styles Configuration

## Heading Hierarchy

**Best Practice**: Limit heading levels to match frontend design system

```typescript
styles: [
  { title: "Normal", value: "normal" },
  { title: "Heading 2", value: "h2" },     // Skip H1 (page title)
  { title: "Heading 3", value: "h3" },
  { title: "Heading 4", value: "h4" },
  { title: "Blockquote", value: "blockquote" },
]
```

**Rationale**:
- H1 reserved for page titles (SEO best practice)
- Match frontend design system constraints
- Prevent content structure issues

## Custom Style Example

```typescript
styles: [
  { title: "Normal", value: "normal" },
  { title: "Large Text", value: "large" },
  { title: "Small Text", value: "small" },
  { title: "Caption", value: "caption" },
]
```

**Frontend Rendering**:
```typescript
const components = {
  block: {
    normal: ({ children }) => <p className="text-base">{children}</p>,
    large: ({ children }) => <p className="text-xl">{children}</p>,
    small: ({ children }) => <p className="text-sm">{children}</p>,
    caption: ({ children }) => <p className="text-xs text-gray-600">{children}</p>,
  },
}
```

## Custom Marks (Decorators)

## Standard Decorators

**100% adoption pattern**:
```typescript
marks: {
  decorators: [
    { title: "Bold", value: "strong" },
    { title: "Italic", value: "em" },
  ],
}
```

## Extended Decorators (Ripplecom Pattern)

```typescript
marks: {
  decorators: [
    { title: "Bold", value: "strong", icon: BoldIcon },
    { title: "Italic", value: "em", icon: ItalicIcon },
    { title: "Underline", value: "underline", icon: UnderlineIcon },
    { title: "Strike", value: "strike-through", icon: StrikethroughIcon },
    { title: "Code", value: "code" },
  ],
}
```

**Benefits**:
- Visual icons in Studio editor
- More formatting options
- Matches common WYSIWYG editors

## Custom Decorator Example

```typescript
marks: {
  decorators: [
    { title: "Highlight", value: "highlight" },
    { title: "Superscript", value: "sup" },
    { title: "Subscript", value: "sub" },
  ],
}
```

**Frontend Rendering**:
```typescript
const components = {
  marks: {
    highlight: ({ children }) => <mark className="bg-yellow-200">{children}</mark>,
    sup: ({ children }) => <sup>{children}</sup>,
    sub: ({ children }) => <sub>{children}</sub>,
  },
}
```

## Link Annotations

## Simple Link Pattern

```typescript
annotations: [
  {
    name: "link",
    type: "object",
    title: "URL",
    fields: [
      {
        name: "href",
        type: "url",
        title: "URL",
      },
    ],
  },
]
```

## Enhanced Link Pattern

```typescript
// schemas/objects/link.ts
export default {
  name: "link",
  type: "object",
  title: "Link",
  fields: [
    {
      name: "linkType",
      type: "string",
      options: {
        list: [
          { title: "Internal Page", value: "internal" },
          { title: "External URL", value: "external" },
        ],
      },
      initialValue: "internal",
    },
    {
      name: "internalLink",
      type: "reference",
      to: [{ type: "page" }],
      hidden: ({ parent }) => parent?.linkType !== "internal",
    },
    {
      name: "externalUrl",
      type: "url",
      hidden: ({ parent }) => parent?.linkType !== "external",
    },
    {
      name: "newWindow",
      type: "boolean",
      title: "Open in new window",
      initialValue: false,
    },
  ],
}
```

**Benefits**:
- Internal link validation
- Prevents broken links when pages move
- Opening behavior control

## Inline Objects

Ripplecom (v4) embeds complex objects within Portable Text:

## Inline Object Types

```typescript
of: [
  defineArrayMember({ type: "block" }), // Standard blocks
  defineArrayMember({ type: "image" }),  // Images
  defineArrayMember({ type: "video" }),  // Videos
  defineArrayMember({ type: "quote" }),  // Pull quotes
  defineArrayMember({ type: "button" }), // CTAs
  defineArrayMember({ type: "codeSnippet" }),      // Code
  defineArrayMember({ type: "tableBlock" }),       // Tables
  defineArrayMember({ type: "newsletterSignup" }), // Forms
]
```

## Inline Image Configuration

```typescript
defineArrayMember({
  type: "image",
  name: "inlineImage",
  fields: [
    {
      name: "alt",
      type: "string",
      title: "Alt Text",
      validation: (Rule) => Rule.required(),
    },
    {
      name: "caption",
      type: "string",
      title: "Caption",
    },
    {
      name: "alignment",
      type: "string",
      options: {
        list: ["left", "center", "right", "full"],
      },
      initialValue: "center",
    },
  ],
})
```

## Press Release Rich Text Pattern

Ripplecom implements domain-specific rich text for press releases:

```typescript
// schemaTypes/fields/pressReleaseRichText.ts
export default defineType({
  name: "pressReleaseRichText",
  type: "object",
  fields: [
    defineField({
      name: "content",
      type: "array",
      of: [
        defineArrayMember({
          type: "block",
          styles: [
            { title: "Normal", value: "normal" },
            // No custom headings for press releases
          ],
          marks: {
            decorators: [
              { title: "Bold", value: "strong" },
              { title: "Italic", value: "em" },
            ],
            annotations: [
              { name: "link", type: "link" },
              {
                name: "companyMention",
                type: "object",
                fields: [
                  {
                    name: "company",
                    type: "reference",
                    to: [{ type: "company" }],
                  },
                ],
              },
            ],
          },
        }),
        defineArrayMember({ type: "quote" }),
      ],
    }),
  ],
})
```

**Benefits**:
- Domain-specific annotations (company mentions)
- Restricted styles for consistency
- Enhanced semantics for SEO

## Frontend Rendering

## Next.js Portable Text

The `@portabletext/react` library renders Sanity Portable Text in Next.js with custom component mappings for blocks, lists, marks, and types.

```typescript
// lib/portableTextComponents.tsx
import { PortableText, PortableTextComponents } from '@portabletext/react'
import Image from 'next/image'

const components: PortableTextComponents = {
  block: {
    normal: ({ children }) => <p className="mb-4">{children}</p>,
    h2: ({ children }) => <h2 className="text-3xl font-bold mb-4">{children}</h2>,
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic">
        {children}
      </blockquote>
    ),
  },
  list: {
    bullet: ({ children }) => <ul className="list-disc ml-6">{children}</ul>,
    number: ({ children }) => <ol className="list-decimal ml-6">{children}</ol>,
  },
  marks: {
    strong: ({ children }) => <strong className="font-bold">{children}</strong>,
    link: ({ value, children }) => (
      <a href={value?.href || '#'} className="text-blue-600 underline">
        {children}
      </a>
    ),
  },
  types: {
    image: ({ value }) => (
      <Image
        src={value.asset.url}
        alt={value.alt || ''}
        width={value.asset.metadata.dimensions.width}
        height={value.asset.metadata.dimensions.height}
      />
    ),
  },
}

export function RichTextRenderer({ content }) {
  return <PortableText value={content} components={components} />
}
```

## Pattern Selection Guidelines

## Use Object Wrapper When:

- Rich text used in page builder arrays
- Nested array issues encountered
- Sanity v3+ project

**Source Confidence**: 33% (ripplecom v4 only)

## Use Direct Array When:

- Rich text in simple document fields
- No page builder architecture
- Sanity v2 project

**Source Confidence**: 67% (kariusdx v2 + helix v3)

## Limit Styles When:

- Frontend design system is constrained
- Content consistency is priority
- Non-technical editors

**Source Confidence**: 67% (kariusdx + ripplecom limit to H2-H4)

## Include Inline Objects When:

- Complex content requirements (multimedia, forms)
- Blog or news content
- High editor expectations

**Source Confidence**: 33% (ripplecom v4 only)

## Common Pitfalls

## Allowing H1 in Rich Text

**Problem**: Multiple H1 tags hurt SEO, break heading hierarchy

**Solution**: Start styles at H2, reserve H1 for page titles

## No Link Validation

**Problem**: External links break, internal links point to deleted pages

**Solution**: Use internal/external link pattern with references

## Excessive Inline Objects

**Problem**: Editor overwhelmed with 10+ inline object types

**Solution**: Limit to 3-5 most common objects (image, video, button)

## Related Patterns

- **Page Builder Architecture**: Using rich text in modular content
- **Content Block Organization**: Where to define rich text schemas
- **Reusable Content Objects**: Link and image object patterns

## See Also

- [Page Builder Architecture](./page-builder-architecture.md)
- [Content Block Organization](./content-block-organization.md)
