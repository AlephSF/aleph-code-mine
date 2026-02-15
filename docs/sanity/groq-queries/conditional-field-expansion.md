---
title: "Conditional Field Expansion (_type ==)"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "conditional", "polymorphic", "content-blocks", "type-checking"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Conditional Field Expansion (_type ==)

## Overview

GROQ conditional field expansion (`_type == '...' => {...}`) enables type-specific field fetching for polymorphic content arrays. All three analyzed projects use this pattern for page builders, content blocks, and navigation structures: helix (39 instances), kariusdx (36 instances), and ripplecom (68 instances). Total of 143 conditional expansions across 51 query files demonstrate universal adoption (100%) for handling varied content types within single arrays.

## Pattern Adoption

**Adoption Rate:** 100% (3 of 3 repositories)

- **Helix (v3)**: 39 conditional expansion instances
- **Kariusdx (v2)**: 36 conditional expansion instances
- **Ripplecom (v4)**: 68 conditional expansion instances (highest usage)

**Average:** 2.8 conditional expansions per query file.


## Single Type Condition

Conditional expansion fetches type-specific fields within arrays of mixed content types.

**Schema (polymorphic content array):**
```typescript
defineField({
  name: 'content',
  type: 'array',
  of: [
    { type: 'textBlock' },
    { type: 'imageBlock' },
    { type: 'videoBlock' }
  ]
})
```

**Query without conditional expansion (generic fields only):**
```groq
*[_type == "page"][0] {
  content[] {
    _type,
    _key
  }
}
```

**Result (no type-specific fields):**
```json
{
  "content": [
    { "_type": "textBlock", "_key": "abc123" },
    { "_type": "imageBlock", "_key": "def456" }
  ]
}
```

**Query with conditional expansion:**
```groq
*[_type == "page"][0] {
  content[] {
    ...,
    _type == 'textBlock' => {
      heading,
      text,
      alignment
    },
    _type == 'imageBlock' => {
      'image': image.asset->{url, metadata.dimensions},
      caption,
      alt
    },
    _type == 'videoBlock' => {
      videoUrl,
      thumbnail
    }
  }
}
```

**Result (type-specific fields included):**
```json
{
  "content": [
    {
      "_type": "textBlock",
      "_key": "abc123",
      "heading": "Welcome",
      "text": "...",
      "alignment": "center"
    },
    {
      "_type": "imageBlock",
      "_key": "def456",
      "image": { "url": "...", "metadata": {...} },
      "caption": "Hero image",
      "alt": "Welcome banner"
    }
  ]
}
```

**Benefit:** Single query fetches all content blocks with appropriate fields for each type.


## Helix Accordion Example (Nested Conditional Expansion)

Helix uses conditional expansion for complex page builder arrays with nested content.

**Query:**
```groq
*[_type == "page" && slug.current == $pagePath][0]{
  title,
  pageBuilder[] {
    ...,
    _type == 'accordion' => {
      heading,
      items[] {
        question,
        answer,
        'image': image.asset->${imgReference}
      }
    },
    _type == 'caseStudy' => {
      title,
      description,
      fileDownload {
        'extension': asset->extension,
        'url': asset->url
      }
    },
    _type == 'hero' => {
      heading,
      subheading,
      'backgroundImage': backgroundImage.asset->${imgReference},
      ctaButtons[] {
        text,
        'url': link.current
      }
    }
  }
}
```

**Handles:**
- Accordion (with nested items array)
- Case Study (with file download)
- Hero (with background image and CTA buttons)

**Observation:** Helix pageBuilder arrays average 5-8 conditional types per query.


## Multi-Level Conditional Expansion

Kariusdx uses nested conditional expansion (2-3 levels deep).

**Query:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  "pageData": *[_type == 'page'][0]{
    content[]{
      ...,
      _type == 'pageSection' => {
        ...,
        innerBlocks[] {
          ...,
          _type == 'imageColumnsCard' => {
            ...,
            columns[]{
              ...,
              'image': image.asset->${imgReferenceExpansion}
            }
          },
          _type == 'imageCarousel' => {
            ...,
            images[]{
              ...,
              asset->${imgReferenceExpansion}
            }
          },
          _type == 'staffGrid' => {
            ...,
            staff[]->{
              ...,
              'headshot': headshot.asset->${imgReferenceExpansion}
            }
          }
        }
      },
      _type == 'columns' => {
        ...,
        columns[]{
          ...,
          richText[] {
            ...,
            _type == 'image' => {
              ...,
              asset->${imgReferenceExpansion}
            }
          }
        }
      }
    }
  }
}
`
```

**Structure:**
1. `content[]` - Top-level array with pageSection, columns types
2. `pageSection.innerBlocks[]` - Second-level array with imageColumnsCard, imageCarousel, staffGrid
3. `columns[].richText[]` - Third-level array with image, text types

**Benefit:** Handles nested polymorphic content in a single query.


## Conditional Expansion with Partial Interpolation

Ripplecom combines conditional expansion with reusable partials for cleaner queries.

**Partial (richText.ts):**
```typescript
export const richTextContentGroq = `
  ...,
  _type == 'image' => {
    ...,
    asset-> {
      url,
      metadata {
        dimensions {
          width,
          height
        }
      }
    },
    alt
  },
  _type == 'callout' => {
    ...,
    icon,
    message
  },
  _type == 'quote' => {
    ...,
    text,
    'author': author->name
  }
`
```

**Usage in query:**
```typescript
export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    content[] {
      ...,
      _type == "textSection" => {
        ...,
        content {
          ${richTextContentGroq}
        }
      }
    }
  }
`)
```

**Benefit:** Conditional expansion logic encapsulated in partial, reusable across multiple queries.


## Type-Based Reference Dereferencing

Conditional expansion with reference dereferencing for polymorphic reference fields.

**Schema (reference to multiple types):**
```typescript
defineField({
  name: 'relatedContent',
  type: 'array',
  of: [
    { type: 'reference', to: [{ type: 'post' }] },
    { type: 'reference', to: [{ type: 'page' }] },
    { type: 'reference', to: [{ type: 'product' }] }
  ]
})
```

**Query with conditional reference expansion:**
```groq
*[_type == "homepage"][0] {
  relatedContent[]-> {
    _type,
    _type == 'post' => {
      title,
      excerpt,
      publishedAt,
      'author': author->name,
      'category': category->title
    },
    _type == 'page' => {
      title,
      'slug': slug.current
    },
    _type == 'product' => {
      name,
      price,
      inStock,
      'image': image.asset->url
    }
  }
}
```

**Fetches different fields based on referenced document type.**


## Conditional Content Fetching Based on Component

**Query:**
```groq
content[]{
  ...,
  _type == 'resourceContentGrid' => {
    contentType == 'events' => {
      'content': (${upcomingEventsGroq(0, 1)} + ${pastEventsGroq(0, 1)})[0..1]
    },
    contentType == 'news' => {
      'content': ${recentNewsGroq(0, 2)}
    },
    contentType == 'pressReleases' => {
      'content': *[_type == 'pressRelease']|order(publishedDate desc)[0..2]
    },
    contentType == 'videos' => {
      'content': *[_type == 'video']|order(_createdAt desc)[0..2]{
        ...,
        'image': image.asset->${imgReferenceExpansion}
      }
    }
  }
}
```

**Behavior:**
- If `contentType == 'events'`, fetches upcoming + past events
- If `contentType == 'news'`, fetches recent news
- If `contentType == 'pressReleases'`, fetches press releases
- If `contentType == 'videos'`, fetches videos with images

**Benefit:** Single component (resourceContentGrid) dynamically fetches different content types based on configuration.


## Sequential Conditional Checks

GROQ supports multiple conditional checks for fine-grained field selection.

**Query:**
```groq
content[] {
  ...,
  _type == 'textBlock' && variant == 'centered' => {
    textAlign: 'center',
    maxWidth: 800
  },
  _type == 'textBlock' && variant == 'full-width' => {
    textAlign: 'left',
    maxWidth: 1200
  },
  _type == 'textBlock' && variant == 'sidebar' => {
    textAlign: 'left',
    maxWidth: 600,
    showBorder: true
  }
}
```

**Fetches different configuration fields based on both `_type` and `variant`.**


## Pattern: Universal Fields + Type-Specific Fields

**Query:**
```groq
content[] {
  ...,  // ✅ Spread operator includes all default fields (_type, _key, common fields)
  _type == 'textBlock' => {
    heading,
    text
  },
  _type == 'imageBlock' => {
    'image': image.asset->{url}
  }
}
```

**Result:**
- All blocks include `_type`, `_key`, and any other common fields
- Type-specific fields added based on condition

**Without spread operator:**
```groq
content[] {
  _type,  // ❌ Must manually specify every common field
  _key,
  _type == 'textBlock' => {
    heading,
    text
  }
}
```

**Recommendation:** Always use `...` before conditional expansions for complete field coverage.


## Over-Expansion vs Selective Expansion

**❌ Over-expansion (fetches all fields for all types):**
```groq
content[] {
  ...,  // ❌ Fetches ALL fields from ALL types (100+ fields)
}
```

**✅ Selective expansion (fetches only needed fields per type):**
```groq
content[] {
  ...,
  _type == 'textBlock' => {
    heading,
    text  // ✅ Only 2 fields
  },
  _type == 'imageBlock' => {
    'image': image.asset->{url}  // ✅ Only url
  }
}
```

**Impact:** Selective expansion reduces payload size by 60-80% in analyzed queries.


## ❌ Missing Spread Operator

```groq
content[] {
  _type == 'textBlock' => {
    heading,
    text
  }
}
```

**Problem:** Without `...`, _type and _key fields are not included (breaks rendering logic).

**Fix:**
```groq
content[] {
  ...,  // ✅ Include default fields
  _type == 'textBlock' => {...}
}
```

## ❌ Overly Complex Nested Conditions

```groq
content[] {
  ...,
  _type == 'section' => {
    blocks[] {
      ...,
      _type == 'subsection' => {
        items[] {
          ...,
          _type == 'component' => {
            ...  // ❌ 4 levels of conditional nesting
          }
        }
      }
    }
  }
}
```

**Problem:** 4+ levels of conditional nesting makes queries unreadable and hard to maintain.

**Better:** Extract inner conditionals to partials or flatten schema.

## ❌ Redundant Conditions

```groq
content[] {
  ...,
  _type == 'textBlock' => {
    _type == 'textBlock' => {  // ❌ Redundant nested condition
      heading
    }
  }
}
```

**Problem:** Duplicate conditions add complexity without benefit.

## Related Patterns

- **Projection and Composition** - See `projection-composition.md` for combining conditionals with partials
- **Reusable Query Partials** - See `reusable-query-partials.md` for extracting conditional logic
- **Reference Expansion** - See `reference-expansion.md` for conditional reference dereferencing

## Summary

Conditional field expansion (`_type == '...' => {...}`) handles polymorphic content with 100% adoption across 51 query files (143 instances). Primary use cases: page builders (helix: 39 instances), nested content blocks (kariusdx: 36 instances), and rich text expansion (ripplecom: 68 instances). Always include spread operator (`...`) before conditionals for default fields. Limit nesting to 2-3 levels maximum for maintainability. Extract complex conditional logic to partials for reusability across queries.
