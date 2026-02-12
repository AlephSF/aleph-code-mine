---
title: "Reusable Query Partials"
category: "sanity"
subcategory: "groq-queries"
tags: ["sanity", "groq", "partials", "reusability", "dry", "image-reference"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Reusable Query Partials

## Overview

GROQ query partials are reusable fragments that represent common content structures. All three analyzed Sanity projects (helix v3, kariusdx v2, ripplecom v4) use partials to avoid repetition and maintain consistency across queries. The pattern shows 100% adoption with 13 partials across 51 query files. Image reference partials appear in all projects, followed by SEO metadata (67%) and rich text content (67%).

## Pattern Adoption

**Adoption Rate:** 100% (3 of 3 repositories)

- **Helix (v3)**: 3 partials (imgReference, link, teaser)
- **Kariusdx (v2)**: 4 partials (imgReferenceExpansion, seoData, navigation, globalData)
- **Ripplecom (v4)**: 6 partials (image, link, richText, seo, video, quote)

**Total:** 13 partials representing common patterns across 51 query files.

## Image Reference Partial Pattern

### Universal Adoption (100%)

All three projects maintain dedicated image reference partials for dereferencing Sanity image assets with metadata.

**Helix imgReference.ts:**
```typescript
const imgReference = `
{
  url,
  altText,
  title,
  description,
  'height': metadata.dimensions.height,
  'width': metadata.dimensions.width,
  'aspectRatio': metadata.dimensions.aspectRatio,
  'blurHash': metadata.blurHash,
}
`
export default imgReference
```

**Kariusdx imgReferenceExpansion.ts:**
```typescript
const imgReferenceExpansion = `
{
  ...,
  'height': metadata.dimensions.height,
  'width': metadata.dimensions.width,
  'aspectRatio': metadata.dimensions.aspectRatio,
  'blurHash': metadata.blurHash,
}
`
export default imgReferenceExpansion
```

**Ripplecom image.ts:**
```typescript
const imageGroq = `
  _id,
  url,
  title,
  altText,
  "width": metadata.dimensions.width,
  "height": metadata.dimensions.height,
  description,
  "contentType": mimeType
`

export const imageFieldGroq = `
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
`
export default imageGroq
```

### Common Image Fields (100% Adoption)

All projects include:
- `metadata.dimensions.width` - Required for Next.js Image component
- `metadata.dimensions.height` - Required for Next.js Image component
- `metadata.dimensions.aspectRatio` - For responsive sizing (67% - helix + kariusdx)
- `metadata.blurHash` - For progressive loading (67% - helix + kariusdx)
- `altText` or `alt` - Accessibility requirement (100%)

### Using Image Partials in Queries

**Pattern: Reference expansion with partial interpolation**

```typescript
import { groq } from 'next-sanity'
import imgReference from './partials/imgReference'

const pageQuery = groq`
  *[_type == "page" && slug.current == $slug][0] {
    title,
    'heroImage': heroImage.asset->${imgReference},
    'thumbnail': thumbnail.asset->${imgReference},
    content[] {
      ...,
      _type == 'imageBlock' => {
        'image': image.asset->${imgReference}
      }
    }
  }
`
```

**Benefits:**
- Single source of truth for image expansion
- Consistent metadata fetching (width/height for Next.js Image)
- Easy to add fields globally (add blurHash to 20 queries by editing one partial)

## SEO Metadata Partial Pattern

### Adoption: 67% (Kariusdx + Ripplecom)

SEO partials centralize Open Graph, meta descriptions, and structured data queries.

**Kariusdx seoData.ts:**
```typescript
const seoData = `
  'seo': {
    'metaTitle': coalesce(seo.metaTitle, title),
    'metaDescription': seo.metaDescription,
    'ogImage': seo.ogImage.asset->url,
    'keywords': seo.keywords[]
  }
`
export default seoData
```

**Ripplecom seo.ts:**
```typescript
const seoGroq = `
  metaTitle,
  metaDescription,
  ogTitle,
  ogDescription,
  ogImage {
    asset-> {
      url,
      metadata {
        dimensions {
          width,
          height
        }
      }
    }
  },
  noIndex,
  noFollow
`
export default seoGroq
```

**Usage in queries:**
```typescript
export const getPageByPathQuery = defineQuery(`
  *[_type == "page" && path.current == $path][0] {
    _id,
    title,
    seo {
      ${seoGroq}
    }
  }
`)
```

**Common SEO fields:**
- metaTitle, metaDescription
- ogTitle, ogDescription, ogImage
- noIndex, noFollow flags (robots meta tags)
- keywords array (deprecated but still used)

## Rich Text / Portable Text Partial

### Adoption: 67% (Kariusdx + Ripplecom)

Rich text partials handle Portable Text expansion with custom block types.

**Ripplecom richText.ts:**
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
    icon
  }
`
```

**Usage in content arrays:**
```typescript
const pageQuery = groq`
  *[_type == "page"][0] {
    content[] {
      ${richTextContentGroq}
    }
  }
`
```

**Handles:**
- Standard Portable Text blocks (paragraph, heading, list)
- Custom blocks (image, video, callout, quote)
- Conditional expansion based on _type
- Asset dereferencing for embedded media

## Navigation Partial Pattern

### Adoption: 33% (Kariusdx Only)

Navigation partials extract site-wide navigation structures for headers/footers.

**Kariusdx navigation.ts:**
```typescript
const navigation = `
  'navigation': *[_type == 'navigation'][0]{
    mainNav[]{
      ...,
      'slug': page->slug.current,
      'title': coalesce(navLabel, page->title),
      subNav[]{
        'slug': page->slug.current,
        'title': coalesce(navLabel, page->title)
      }
    }
  }
`
export default navigation
```

**Usage:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  ${navigation},
  "pageData": *[_type == 'page' && path == "${slug}"][0]{...}
}
`
```

**Benefits:**
- Navigation fetched alongside page data
- Single query for header/footer data
- Consistent navigation structure across all pages

## Global Data Partial Pattern

### Adoption: 33% (Kariusdx Only)

Global data partials fetch site-wide settings (contact info, social links, footer content).

**Kariusdx globalData.ts:**
```typescript
const globalData = `
  'globalData': *[_type == 'siteSettings'][0]{
    siteName,
    siteUrl,
    contactEmail,
    socialLinks[]{
      platform,
      url
    },
    footer{
      copyrightText,
      links[]{
        text,
        url
      }
    }
  }
`
export default globalData
```

**Usage:**
```typescript
const pageQuery = (slug: string[]) => groq`
{
  ${globalData},
  ${navigation},
  "pageData": ...
}
`
```

## Link Partial Pattern

### Adoption: 67% (Helix + Ripplecom)

Link partials handle internal/external link objects with conditional logic.

**Ripplecom link.ts:**
```typescript
const linkGroq = `
  text,
  linkType,
  linkType == 'internal' => {
    'url': internalLink->path.current
  },
  linkType == 'external' => {
    'url': externalUrl
  },
  openInNewTab
`
export default linkGroq
```

**Usage in CTA buttons:**
```typescript
const heroQuery = groq`
  *[_type == "hero"][0] {
    heading,
    primaryCta {
      ${linkGroq}
    },
    secondaryCta {
      ${linkGroq}
    }
  }
`
```

## Video Partial Pattern

### Adoption: 33% (Ripplecom Only)

Video partials handle video embeds (YouTube, Vimeo) or uploaded video files.

**Ripplecom video.ts:**
```typescript
const videoGroq = `
  videoType,
  videoType == 'youtube' => {
    youtubeId,
    'embedUrl': 'https://www.youtube.com/embed/' + youtubeId
  },
  videoType == 'vimeo' => {
    vimeoId,
    'embedUrl': 'https://player.vimeo.com/video/' + vimeoId
  },
  videoType == 'file' => {
    'url': videoFile.asset->url
  },
  thumbnail {
    asset-> {
      url
    }
  }
`
export default videoGroq
```

## When to Create a Partial

Create a partial when a GROQ fragment meets any of these criteria:

### 1. Repetition (Used in 2+ Queries)

**Without partial (repetitive):**
```typescript
const blogQuery = groq`{ 'image': image.asset->{url, metadata.dimensions.width} }`
const pageQuery = groq`{ 'heroImage': heroImage.asset->{url, metadata.dimensions.width} }`
const authorQuery = groq`{ 'avatar': avatar.asset->{url, metadata.dimensions.width} }`
```

**With partial (DRY):**
```typescript
const imgRef = `{url, 'width': metadata.dimensions.width}`
const blogQuery = groq`{ 'image': image.asset->${imgRef} }`
const pageQuery = groq`{ 'heroImage': heroImage.asset->${imgRef} }`
const authorQuery = groq`{ 'avatar': avatar.asset->${imgRef} }`
```

### 2. Complex Structures (>5 Fields)

**Without partial (unreadable):**
```typescript
const query = groq`
  seo {
    metaTitle,
    metaDescription,
    ogTitle,
    ogDescription,
    ogImage{ asset->{url, metadata.dimensions.width, metadata.dimensions.height} },
    twitterCard,
    twitterSite,
    noIndex,
    noFollow,
    canonicalUrl
  }
`
```

**With partial (readable):**
```typescript
// partials/seoData.ts
const seoData = `metaTitle, metaDescription, ogTitle, ogDescription, ...`

// query.ts
const query = groq`seo { ${seoData} }`
```

### 3. Conditional Logic

**Without partial (complex):**
```typescript
const query = groq`
  link {
    linkType,
    linkType == 'internal' => { 'url': internalLink->slug.current },
    linkType == 'external' => { 'url': externalUrl },
    linkType == 'file' => { 'url': file.asset->url }
  }
`
```

**With partial (encapsulated):**
```typescript
// partials/link.ts
const linkData = `linkType, linkType == 'internal' => {...}, ...`

// query.ts
const query = groq`link { ${linkData} }`
```

## Partial Naming Conventions

**Observed patterns:**

| Project | Naming Convention | Examples |
|---------|------------------|----------|
| Helix | camelCase descriptive | imgReference, link, teaser |
| Kariusdx | camelCase + "Data" suffix | seoData, globalData, navigation |
| Ripplecom | camelCase + "Groq" suffix | imageGroq, seoGroq, videoGroq |

**Recommendation:** Use camelCase with descriptive names. Add "Groq" or "Data" suffix if helpful for clarity in larger projects.

## Anti-Patterns to Avoid

### ❌ Over-Abstraction

```typescript
// TOO GENERIC - Not reusable
const fields = `_id, title, slug`  // Every document type has different fields
```

**Better:** Create specific partials for content structures that repeat.

### ❌ Hardcoded Values in Partials

```typescript
// BAD - Hardcoded filter in partial
const posts = `*[_type == "post"][0..10]`
```

**Better:** Partials should be fragments, not full queries. Keep filters in main queries.

### ❌ Not Exporting as Default

```typescript
// INCONSISTENT - Mix of named and default exports
export const imgRef = `...`  // Named
const seoData = `...`
export default seoData  // Default
```

**Better:** Choose one convention (default export recommended for partials).

## Related Patterns

- **Query File Organization** - See `query-file-organization.md` for directory structure
- **Reference Expansion Operator** - See `reference-expansion.md` for dereferencing
- **Projection and Composition** - See `projection-composition.md` for interpolation

## Summary

Reusable query partials eliminate repetition and ensure consistency across 51 query files in analyzed projects. Image reference partials appear universally (100%) with metadata fields for Next.js Image components. SEO and rich text partials follow (67%). Create partials when fragments repeat 2+ times, exceed 5 fields, or contain complex conditional logic. Store partials in dedicated `/partials` subdirectory and export as default for consistency.
