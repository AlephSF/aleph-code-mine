---
title: "Content Block Organization Strategies"
category: "content-modeling"
subcategory: "code-organization"
tags: ["sanity", "folder-structure", "components", "builder-blocks", "schema-organization"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

# Content Block Organization Strategies

## Overview

Sanity projects with page builders accumulate 15-35 reusable content block schemas. Consistent folder organization improves developer experience, enables faster schema discovery, and maintains codebase clarity as projects scale.

**Adoption**: 67% of analyzed projects (kariusdx v2 + ripplecom v4) use dedicated folders for content blocks. Helix v3 uses minimal `objects/` folder for SEO and image metadata only.

## Folder Structure Patterns

## Modern Components Pattern (Sanity v3+)

Ripplecom (v4) organizes reusable content blocks in a `components/` folder, distinguishing them from document types and objects:

```
schemaTypes/
├── index.ts              # Schema registry
├── documents/            # Document types (page, blogPost, etc.)
│   ├── page.ts
│   ├── blogPost.ts
│   └── event.ts
├── components/           # Reusable page builder blocks
│   ├── heroSection.ts
│   ├── textSection.ts
│   ├── cardGrid.ts
│   ├── quote.ts
│   ├── button.ts
│   └── ctaSection.ts
├── fields/               # Custom field types
│   ├── richText.ts
│   ├── link.tsx
│   └── path.ts
├── objects/              # Reusable data objects
│   ├── seo.ts
│   ├── navigationItem.ts
│   └── metaFields.ts
├── globals/              # Singleton documents
│   ├── navigation.ts
│   ├── homepage.ts
│   └── seoMetadata.ts
└── legacy/               # Deprecated schemas
    └── sections/
        ├── faqSection.ts
        └── videoList.ts
```

**Characteristics**:
- **15 component files** in `components/` folder
- Each component is an `object` type (not `document`)
- Used in page builder `content` arrays
- Modern naming: `heroSection`, `textSection`, `ctaSection`

## Legacy Builder Blocks Pattern (Sanity v2)

Kariusdx (v2) uses `builderBlocks/` folder for page composition elements:

```
schemas/
├── schema.js             # Schema registry
├── documents/            # Document types
│   ├── page.js
│   ├── news.js
│   └── staff.js
├── builderBlocks/        # Page builder content blocks
│   ├── pageSection.js
│   ├── richText.js
│   ├── cardContent.js
│   ├── imageCarousel.js
│   ├── hubspotForm.js
│   └── pathogenList.js
├── fields/               # Custom field types
│   ├── pageBuilder.js
│   ├── richTextCustom.js
│   └── slug.js
├── objects/              # Reusable data objects
│   ├── seo.js
│   ├── link.js
│   ├── stat.js
│   └── navItem.js
└── actions/              # Custom document actions
    └── setSlugAndPublish.js
```

**Characteristics**:
- **20 builder block files** in `builderBlocks/` folder
- Mix of layout, content, and integration blocks
- Domain-specific blocks: `pathogenList`, `diagnosisComparison`
- Integration blocks: `hubspotForm`, `wistiaEmbed`

## Minimal Objects Pattern (Sanity v3)

Helix (v3) has no page builder, using simple `objects/` folder for shared data:

```
schemas/
├── index.ts              # Schema registry
├── documents/            # Document types only
│   ├── page.js
│   └── blogPost.js
└── objects/              # Shared metadata objects
    ├── featuredImage.js
    └── seo.js
```

**Characteristics**:
- **2 object files** only
- No page builder components
- Focus on hierarchical pages over modular content

## Naming Conventions

## Components Folder (Modern)

**Pattern**: Descriptive, purpose-driven names

**Examples**:
- `heroSection.ts` - Hero banner with CTA
- `textSection.ts` - Text content block
- `imageSection.ts` - Image display
- `ctaSection.ts` - Call-to-action block
- `cardGrid.ts` - Card layout
- `quote.ts` - Quote block
- `spacer.ts` - Spacing utility

**Philosophy**: Names describe what the component renders, not its technical type

## Builder Blocks Folder (Legacy)

**Pattern**: Mix of descriptive and technical names

**Examples**:
- `pageSection.js` - Section wrapper with layout controls
- `richText.js` - Rich text editor
- `cardContent.js` - Card display
- `imageCarousel.js` - Image carousel
- `hubspotForm.js` - Form integration
- `wistiaEmbed.js` - Video embed
- `pathogenList.js` - Domain-specific list

**Philosophy**: Names describe component function, often including technical details

## Schema Registry Organization

## Modern Index Pattern (TypeScript)

```typescript
// schemaTypes/index.ts
import { SchemaTypeDefinition } from 'sanity'

// Documents
import page from './documents/page'
import blogPost from './documents/blogPost'
import event from './documents/event'

// Components
import heroSection from './components/heroSection'
import textSection from './components/textSection'
import cardGrid from './components/cardGrid'

// Fields
import richText from './fields/richText'
import link from './fields/link'

// Objects
import seo from './objects/seo'
import metaFields from './objects/metaFields'

// Globals
import navigation from './globals/navigation'
import homepage from './globals/homepage'

export const schemaTypes: SchemaTypeDefinition[] = [
  // Documents
  page,
  blogPost,
  event,

  // Components (order matters for Studio UI)
  heroSection,
  textSection,
  cardGrid,

  // Fields
  richText,
  link,

  // Objects
  seo,
  metaFields,

  // Globals
  navigation,
  homepage,
]
```

**Benefits**:
- Clear section comments
- Grouped by type
- Import order controls Studio UI order

## Legacy Schema Pattern (JavaScript)

```javascript
// schemas/schema.js
import createSchema from 'part:@sanity/base/schema-creator'
import schemaTypes from 'all:part:@sanity/base/schema-type'

// Documents
import page from './documents/page'
import news from './documents/news'

// Builder Blocks
import pageSection from './builderBlocks/pageSection'
import richText from './builderBlocks/richText'
import cardContent from './builderBlocks/cardContent'

// Objects
import seo from './objects/seo'
import link from './objects/link'

// Fields
import pageBuilder from './fields/pageBuilder'

export default createSchema({
  name: 'default',
  types: schemaTypes.concat([
    // Documents
    page,
    news,

    // Builder Blocks
    pageSection,
    richText,
    cardContent,

    // Objects
    seo,
    link,

    // Fields
    pageBuilder,
  ]),
})
```

## Folder Guidelines by Project Size

## Small Projects (< 10 Content Blocks)

**Structure**:
```
schemas/
├── documents/
├── objects/    # Contains both metadata and content blocks
└── index.ts
```

**Rationale**: Single `objects/` folder sufficient for small block counts

## Medium Projects (10-25 Content Blocks)

**Structure**:
```
schemaTypes/
├── documents/
├── components/     # or builderBlocks/
├── objects/        # Metadata only
├── fields/
└── index.ts
```

**Rationale**: Separate content blocks from data objects

## Large Projects (25+ Content Blocks)

**Structure**:
```
schemaTypes/
├── documents/
├── components/
│   ├── hero/
│   ├── content/
│   └── layout/
├── objects/
├── fields/
├── globals/
├── legacy/
└── index.ts
```

**Rationale**: Group components by category for easier navigation

## Component Categorization Strategies

## By Purpose (Recommended)

```
components/
├── hero/
│   ├── heroSection.ts
│   └── heroBanner.ts
├── content/
│   ├── textSection.ts
│   ├── richTextBlock.ts
│   └── quote.ts
├── media/
│   ├── imageSection.ts
│   ├── videoPlayer.ts
│   └── imageGallery.ts
├── layout/
│   ├── cardGrid.ts
│   ├── columns.ts
│   └── spacer.ts
└── cta/
    ├── ctaSection.ts
    └── button.ts
```

**Benefits**:
- Intuitive organization
- Mirrors frontend component structure
- Easy to locate specific blocks

## By Complexity

```
components/
├── simple/
│   ├── spacer.ts
│   ├── divider.ts
│   └── quote.ts
├── standard/
│   ├── textSection.ts
│   ├── imageSection.ts
│   └── button.ts
└── complex/
    ├── cardGrid.ts
    ├── heroSection.ts
    └── navigationMenu.ts
```

**Benefits**:
- Highlights maintenance burden
- Useful for large teams

**Tradeoffs**:
- Subjective complexity assessment
- Less intuitive navigation

## Flat Structure (No Subcategories)

```
components/
├── heroSection.ts
├── textSection.ts
├── imageSection.ts
├── cardGrid.ts
├── quote.ts
├── ctaSection.ts
└── spacer.ts
```

**Benefits**:
- Simplest structure
- Fastest to implement

**Appropriate for**: Projects with < 20 components

## Legacy Content Migration

## Migration Folder Pattern

Ripplecom v4 maintains deprecated schemas in `legacy/` folder:

```
schemaTypes/
├── components/          # Modern components
└── legacy/
    ├── index.ts
    └── sections/
        ├── faqSection.ts
        ├── videoList.ts
        ├── bioModalList.ts
        └── collapsibleSectionList.ts
```

**Strategy**:
- **16 legacy section files** preserved for backward compatibility
- New content uses modern `components/` sections
- Frontend supports both modern and legacy rendering
- Gradual migration as content is updated

**Benefits**:
- Zero content breakage during migration
- Clear separation of old vs new
- Safe deprecation path

## Pattern Selection Guidelines

## Use components/ Folder When:

- Sanity v3+ project
- 10+ reusable content blocks
- Modern naming conventions preferred

**Source Confidence**: 33% (ripplecom v4 only)

## Use builderBlocks/ Folder When:

- Sanity v2 project
- Page builder with section wrappers
- Domain-specific blocks (medical, e-commerce)

**Source Confidence**: 33% (kariusdx v2 only)

## Use objects/ Folder When:

- < 5 reusable blocks
- Focus on data objects (SEO, links, metadata)
- No page builder architecture

**Source Confidence**: 33% (helix v3 uses minimal objects)

## Common Pitfalls

## Mixing Data Objects with Content Blocks

**Problem**: `objects/` folder contains both metadata (SEO, links) and content blocks (heroSection, cardGrid)

**Solution**: Separate content blocks into `components/` or `builderBlocks/` folder

## Inconsistent Naming

**Problem**: Mix of `heroSection.ts`, `Hero.ts`, `hero-section.ts`

**Solution**: Enforce naming convention: `camelCase` with descriptive suffixes (`Section`, `Block`, `Card`)

## No Legacy Folder

**Problem**: Deprecated schemas mixed with active ones

**Solution**: Move deprecated schemas to `legacy/` folder, document migration path

## Frontend Mapping Patterns

## Component Map from Folder Structure

```typescript
// lib/componentMap.ts
import HeroSection from '@/components/sanity/HeroSection'
import TextSection from '@/components/sanity/TextSection'
import CardGrid from '@/components/sanity/CardGrid'

export const componentMap: Record<string, React.ComponentType<any>> = {
  heroSection: HeroSection,
  textSection: TextSection,
  cardGrid: CardGrid,
}

// Usage
export function renderComponent(block: SanityBlock) {
  const Component = componentMap[block._type]
  if (!Component) {
    console.warn(`No component found for type: ${block._type}`)
    return null
  }
  return <Component {...block} />
}
```

## Related Patterns

- **Page Builder Architecture**: How content blocks are composed
- **Content Block Naming Conventions**: Naming standards for blocks
- **Reusable Content Objects**: When to use objects vs components

## See Also

- [Page Builder Architecture](./page-builder-architecture.md)
- [Content Block Naming Conventions](./content-block-naming-conventions.md)
