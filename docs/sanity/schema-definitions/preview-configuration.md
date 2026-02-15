---
title: "Preview Configuration for Schema Types"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "preview", "studio-ux", "document-list"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

# Preview Configuration for Schema Types

## Overview

Sanity preview configuration controls how documents appear in the Studio sidebar, document lists, and reference selectors. Previews customize the title, subtitle, description, and media (image) displayed for each document. Preview adoption is a de facto standard with 68% of schemas using custom configurations, though Helix relies entirely on default previews.

## Pattern Adoption

**Adoption Rate:** 67% (2 of 3 repositories)

**Preview Density:**
- **Ripplecom (v4)**: 84 preview configs (108% - 1.08 per schema)
- **Kariusdx (v2)**: 16 preview configs (25% of schemas)
- **Helix (v3)**: 0 preview configs (uses Sanity defaults)

**Total:** 100 preview configurations across 147 schemas = **68% adoption**


## Simple Title + Subtitle

The most common pattern shows document title and slug/identifier.

```javascript
// kariusdx-sanity/schemas/documents/page.js
export default {
  name: 'page',
  type: 'document',
  preview: {
    select: {
      title: 'title',
      subtitle: 'slug.current',
    },
  },
}
```

**Result in Studio:**
```
📄 About Us
   about-us
```

## Title + Media

Display document title with associated image.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
export default defineType({
  name: "blogPost",
  preview: {
    select: {
      title: "title",
      media: "featuredImage",
    },
  },
})
```

**Result in Studio:**
```
[Image] New Feature Launch
```


## Custom Subtitle Formatting

The `prepare()` function transforms selected data for display.

```typescript
export default defineType({
  name: "blogPost",
  preview: {
    select: {
      title: "title",
      media: "featuredImage",
      slug: "slug.current",
      author: "meta.author.name", // ← Dereferences author reference
    },
    prepare({ title, media, slug, author }) {
      return {
        title: title || "Untitled",
        subtitle: author ? `${author} | ${slug}` : slug,
        media,
      }
    },
  },
})
```

**Result in Studio:**
```
[Image] New Feature Launch
        John Doe | new-feature-launch
```

## Fallback for Missing Data

Use `prepare()` to provide defaults when fields are empty.

```typescript
preview: {
  select: {
    title: "title",
    slug: "slug.current",
    image: "featuredImage",
  },
  prepare({ title, slug, image }) {
    return {
      title: title || "Untitled",
      subtitle: slug || "No slug set",
      media: image, // Falls back to default document icon if undefined
    }
  },
}
```


## Dereferencing Author/Person

Preview can fetch data from referenced documents.

```typescript
preview: {
  select: {
    title: "title",
    authorName: "author.name", // ← Dereferences author reference
    authorImage: "author.image",
  },
  prepare({ title, authorName, authorImage }) {
    return {
      title: title || "Untitled",
      subtitle: authorName ? `By ${authorName}` : "No author",
      media: authorImage, // Shows author's image if no featured image
    }
  },
}
```

## Dereferencing Categories

Display category names in preview subtitle.

```typescript
preview: {
  select: {
    title: "title",
    category0: "categories.0.title", // First category
    category1: "categories.1.title", // Second category
  },
  prepare({ title, category0, category1 }) {
    const categories = [category0, category1].filter(Boolean).join(", ")

    return {
      title: title || "Untitled",
      subtitle: categories || "Uncategorized",
    }
  },
}
```


## Publishing Status Indicators

Show draft vs published status in previews.

```typescript
preview: {
  select: {
    title: "title",
    publishedAt: "publishedAt",
    draft: "_id",
  },
  prepare({ title, publishedAt, draft }) {
    const isDraft = draft.startsWith("drafts.")
    const status = publishedAt
      ? `Published ${new Date(publishedAt).toLocaleDateString()}`
      : isDraft
      ? "Draft"
      : "Unpublished"

    return {
      title: title || "Untitled",
      subtitle: status,
    }
  },
}
```

**Result in Studio:**
```
About Us
Draft

Feature Launch
Published 2/11/2026
```

## Content Statistics

Display content metrics like word count or item counts.

```typescript
preview: {
  select: {
    title: "title",
    content: "content",
    images: "gallery",
  },
  prepare({ title, content, images }) {
    const blockCount = content?.length || 0
    const imageCount = images?.length || 0

    return {
      title: title || "Untitled",
      subtitle: `${blockCount} blocks, ${imageCount} images`,
    }
  },
}
```


## Component/Block Previews

Object types (components, builder blocks) benefit from clear preview labels.

```typescript
// Button component preview
export default defineType({
  name: "button",
  type: "object",
  preview: {
    select: {
      label: "label",
      url: "url",
      variant: "variant",
    },
    prepare({ label, url, variant }) {
      return {
        title: label || "Button",
        subtitle: `${variant || "primary"} → ${url || "(no link)"}`,
      }
    },
  },
})
```

**Result in Page Builder:**
```
Learn More
primary → /about-us

Contact Us
secondary → /contact
```

## SEO Object Preview

Show SEO field status in object previews.

```typescript
export default defineType({
  name: "seo",
  type: "object",
  preview: {
    select: {
      title: "title",
      description: "description",
      noindex: "noindex",
    },
    prepare({ title, description, noindex }) {
      const parts = []

      if (title) parts.push(`Title: "${title.slice(0, 30)}..."`)
      if (description) parts.push(`Desc: "${description.slice(0, 30)}..."`)
      if (noindex) parts.push("⚠️ No-Index")

      return {
        title: parts.length > 0 ? "SEO Configured" : "No SEO Overrides",
        subtitle: parts.join(" | "),
      }
    },
  },
})
```


## Multi-Language Content

Show language indicator in previews for localized content.

```typescript
preview: {
  select: {
    title: "title",
    language: "language",
    slug: "slug.current",
  },
  prepare({ title, language, slug }) {
    const langLabel = {
      en: "🇺🇸 EN",
      es: "🇪🇸 ES",
      fr: "🇫🇷 FR",
    }[language] || language

    return {
      title: title || "Untitled",
      subtitle: `${langLabel} | ${slug}`,
    }
  },
}
```

**Result in Studio:**
```
About Us
🇺🇸 EN | about-us

Acerca de Nosotros
🇪🇸 ES | acerca-de-nosotros
```


## Priority-Based Media Selection

Fall back through multiple image fields to find preview media.

```typescript
preview: {
  select: {
    title: "title",
    heroImage: "heroImage",
    featuredImage: "featuredImage",
    ogImage: "seo.ogImage",
  },
  prepare({ title, heroImage, featuredImage, ogImage }) {
    // Use first available image
    const media = heroImage || featuredImage || ogImage

    return {
      title: title || "Untitled",
      media,
    }
  },
}
```

## Array Image (First Item)

Select the first image from an array.

```typescript
preview: {
  select: {
    title: "title",
    firstImage: "gallery.0", // ← First item in gallery array
  },
  prepare({ title, firstImage }) {
    return {
      title: title || "Untitled",
      media: firstImage,
    }
  },
}
```


## Computed Titles

Generate preview titles from multiple fields when title doesn't exist.

```typescript
// Event preview: "2026 Conference - San Francisco"
preview: {
  select: {
    eventName: "name",
    location: "location",
    date: "startDate",
  },
  prepare({ eventName, location, date }) {
    const year = date ? new Date(date).getFullYear() : ""

    return {
      title: `${year} ${eventName} - ${location}`,
      subtitle: date ? new Date(date).toLocaleDateString() : "No date set",
    }
  },
}
```

## Person Name Formatting

Format person names from firstName/lastName fields.

```typescript
preview: {
  select: {
    firstName: "firstName",
    lastName: "lastName",
    title: "jobTitle",
    image: "image",
  },
  prepare({ firstName, lastName, title, image }) {
    const name = [firstName, lastName].filter(Boolean).join(" ")

    return {
      title: name || "Unnamed Person",
      subtitle: title || "No title",
      media: image,
    }
  },
}
```


## Limiting Selected Fields

Only select fields actually needed for display to improve query performance.

**❌ Bad: Selects unnecessary data**
```typescript
preview: {
  select: {
    title: "title",
    slug: "slug.current",
    content: "content", // ← Not used in preview
    seo: "seo", // ← Not used in preview
  },
  prepare({ title, slug }) { /* ... */ }
}
```

**✅ Good: Only necessary fields**
```typescript
preview: {
  select: {
    title: "title",
    slug: "slug.current",
  },
}
```

## Avoiding Heavy Computations

Keep `prepare()` functions lightweight; avoid expensive transformations.

**❌ Bad: Heavy computation**
```typescript
prepare({ content }) {
  // Parses all content blocks on every render
  const wordCount = content
    ?.map(block => block.children?.map(c => c.text).join(' '))
    .join(' ')
    .split(/\s+/)
    .length

  return { title: `Document (${wordCount} words)` }
}
```

**✅ Good: Simple property access**
```typescript
prepare({ title, status }) {
  return {
    title: title || "Untitled",
    subtitle: status,
  }
}
```


## When preview is Omitted

Sanity uses sensible defaults when no preview config is provided.

**Default Behavior:**
- **Title**: First string field (usually `title` or `name`)
- **Subtitle**: Second string field or slug
- **Media**: First image field

```typescript
// No preview config - Sanity auto-detects
export default defineType({
  name: "page",
  fields: [
    defineField({ name: "title", type: "string" }), // ← Auto-used for preview
    defineField({ name: "slug", type: "slug" }), // ← Auto-used for subtitle
    defineField({ name: "image", type: "image" }), // ← Auto-used for media
  ],
})
```

**When to Skip Preview Config:**
- Schema has standard `title` + `slug` + `image` fields
- No custom formatting needed
- No referenced data to display


## Overly Complex Preview Logic

Keep preview logic simple; complex computations slow down Studio UI.

**❌ Bad: Complex string manipulation**
```typescript
prepare({ title, content }) {
  // Heavy processing on every render
  const summary = content
    ?.filter(block => block._type === 'block')
    .map(block => block.children.map(child => child.text).join(''))
    .join(' ')
    .slice(0, 100)
    .replace(/\s\w+$/, '...')

  return { title, subtitle: summary }
}
```

**✅ Good: Simple field access**
```typescript
prepare({ title, excerpt }) {
  return {
    title: title || "Untitled",
    subtitle: excerpt || "No excerpt",
  }
}
```

## Selecting Too Many Fields

Selecting 10+ fields for preview slows down document lists.

**❌ Bad: Excessive selection**
```typescript
select: {
  title: "title",
  slug: "slug.current",
  content: "content",
  seo: "seo",
  meta: "meta",
  author: "author",
  categories: "categories",
  tags: "tags",
  images: "images",
  // Only using title and slug!
}
```

**✅ Good: Minimal selection**
```typescript
select: {
  title: "title",
  slug: "slug.current",
}
```

## Missing Fallbacks

Always provide fallbacks for undefined values.

**❌ Bad: No fallbacks**
```typescript
prepare({ title, author }) {
  return {
    title, // ← Undefined if missing
    subtitle: author.name, // ← Error if author is null
  }
}
```

**✅ Good: Safe fallbacks**
```typescript
prepare({ title, author }) {
  return {
    title: title || "Untitled",
    subtitle: author?.name || "No author",
  }
}
```

## Implementation Checklist

- [ ] Add preview config to all document types (page, blogPost, event, person)
- [ ] Add preview to frequently-used object types (components, builder blocks)
- [ ] Select only fields needed for display (avoid over-fetching)
- [ ] Use `prepare()` for custom formatting and fallbacks
- [ ] Dereference author/category names for richer previews
- [ ] Provide fallback values for missing data (`title || "Untitled"`)
- [ ] Test preview rendering in document lists and reference selectors
- [ ] Verify preview performance (no slow renders on large document lists)

## Related Patterns

- **Icon Customization**: Icons appear alongside preview title/media
- **Reference Fields**: Preview can dereference and display referenced data
- **Validation Rules**: Validation doesn't affect preview display
- **Field Groups**: Preview selects from any group (not just default tab)

## References

- Ripplecom (v4): 84 preview configs (1.08 per schema, extensive usage)
- Kariusdx (v2): 16 preview configs (document types only)
- Helix (v3): 0 preview configs (relies on Sanity defaults)
- Sanity Preview Documentation: https://www.sanity.io/docs/previews-list-views
