---
title: "Legacy Content Migration Patterns"
category: "content-modeling"
subcategory: "schema-evolution"
tags: ["sanity", "migration", "legacy-content", "deprecation", "schema-versioning"]
stack: "sanity"
priority: "low"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

# Legacy Content Migration Patterns

## Overview

Sanity projects evolve over time, requiring schema changes and content migrations. Legacy content migration patterns enable gradual transitions from old schemas to new patterns without breaking existing content or requiring big-bang migrations.

**Adoption**: 33% of analyzed projects (ripplecom v4 only) implement explicit legacy content management. Kariusdx v2 (33%) and Helix v3 (33%) have no legacy folder structure.

## Legacy Folder Pattern

Ripplecom (v4) maintains deprecated schemas in dedicated `legacy/` folder, enabling zero-downtime content migration:

**Structure**:
```
schemaTypes/
├── components/          # Modern components (15 types)
│   ├── heroSection.ts
│   ├── textSection.ts
│   └── cardGrid.ts
├── legacy/              # Deprecated schemas (16 types)
│   ├── index.ts
│   └── sections/
│       ├── faqSection.ts
│       ├── videoList.ts
│       ├── bioModalList.ts
│       ├── collapsibleSectionList.ts
│       ├── marqueeLogoSection.ts
│       └── ... (11 more)
└── index.ts
```

**Characteristics**:
- **16 legacy section types** preserved
- Modern `components/` folder for new content
- Frontend supports both modern and legacy rendering
- Gradual migration as content is updated
- No content breakage during transition

## Legacy Schema Organization

```typescript
// schemaTypes/legacy/index.ts
import { SchemaTypeDefinition } from 'sanity'

// Legacy sections (deprecated but still in use)
import faqSection from './sections/faqSection'
import videoList from './sections/videoList'
import bioModalList from './sections/bioModalList'
import collapsibleSectionList from './sections/collapsibleSectionList'

export const legacyTypes: SchemaTypeDefinition[] = [
  faqSection,
  videoList,
  bioModalList,
  collapsibleSectionList,
  // ... 12 more legacy sections
]
```

## Main Schema Registry with Legacy Types

```typescript
// schemaTypes/index.ts
import { legacyTypes } from './legacy'
import { modernComponents } from './components'

export const schemaTypes: SchemaTypeDefinition[] = [
  // Modern schemas (preferred for new content)
  ...modernComponents,

  // Legacy schemas (deprecated, maintained for compatibility)
  ...legacyTypes,
]
```

## Migration Strategies

## Strategy 1: Dual Schema Support (Recommended)

**Approach**: Keep both legacy and modern schemas active simultaneously

**Benefits**:
- Zero content breakage
- Gradual migration
- Rollback capability
- Content editors choose when to migrate

**Implementation**:
```typescript
// Page document supports both old and new sections
defineField({
  name: "content",
  type: "array",
  of: [
    // Modern components
    { type: "heroSection" },
    { type: "textSection" },
    { type: "cardGrid" },

    // Legacy sections (still valid but deprecated)
    { type: "faqSection" },        // Deprecated: use collapsibleSection
    { type: "videoList" },          // Deprecated: use video component
    { type: "bioModalList" },       // Deprecated: use bioModal component
  ],
})
```

**Source Confidence**: 33% (ripplecom v4 implements this pattern)

## Strategy 2: Schema Versioning

**Approach**: Version schema names, migrate content programmatically

**Benefits**:
- Clear version tracking
- Explicit migration paths
- Can remove old versions after migration complete

**Implementation**:
```typescript
// v1 schemas (deprecated)
heroSectionV1
textSectionV1

// v2 schemas (current)
heroSection
textSection

// Migration script identifies v1 content
const needsMigration = await client.fetch(`
  count(*[_type == "page" && content[]._type match "*V1"])
`)
```

**Source Confidence**: N/A (not observed in analyzed projects)

## Strategy 3: Content Transformation Layer

**Approach**: Transform legacy content at query time

**Benefits**:
- No schema changes required
- Instant "migration"
- Can A/B test new patterns

**Tradeoffs**:
- Query performance impact
- Complex transformation logic
- Harder to debug

**Implementation**:
```typescript
// Transform legacy sections to modern format
const transformedContent = content.map((block) => {
  if (block._type === 'faqSection') {
    return {
      _type: 'collapsibleSection',
      items: block.faqs.map(faq => ({
        question: faq.question,
        answer: faq.answer,
      })),
    }
  }
  return block
})
```

**Source Confidence**: N/A (not observed, but common pattern)

## Frontend Rendering Strategies

## Unified Component Mapping

Map both legacy and modern schemas to appropriate components:

```typescript
// lib/componentMap.ts
const componentMap: Record<string, React.ComponentType<any>> = {
  // Modern components
  heroSection: HeroSection,
  textSection: TextSection,
  cardGrid: CardGrid,

  // Legacy components (map to modern or legacy renderers)
  faqSection: LegacyFaqSection,  // Render legacy format
  videoList: LegacyVideoList,     // Render legacy format

  // Or map legacy to modern components
  bioModalList: BioModalSection,  // Modern component handles legacy format
}
```

## Adapter Pattern

Create adapters that transform legacy data to modern component props:

```typescript
// components/legacy/FaqAdapter.tsx
import CollapsibleSection from '@/components/sanity/CollapsibleSection'

export default function FaqAdapter(props: LegacyFaqSectionProps) {
  // Transform legacy structure to modern format
  const modernProps = {
    _type: 'collapsibleSection',
    items: props.faqs.map(faq => ({
      heading: faq.question,
      content: faq.answer,
    })),
  }

  return <CollapsibleSection {...modernProps} />
}
```

**Benefits**:
- Reuse modern components
- Isolate transformation logic
- Easy to test transformations

## Legacy Renderer Component

Dedicated component handles all legacy formats:

```typescript
// components/LegacyRenderer.tsx
export default function LegacyRenderer({ block }: { block: LegacyBlock }) {
  switch (block._type) {
    case 'faqSection':
      return <LegacyFaqSection {...block} />
    case 'videoList':
      return <LegacyVideoList {...block} />
    case 'bioModalList':
      return <LegacyBioModalList {...block} />
    default:
      console.warn(`Unknown legacy type: ${block._type}`)
      return null
  }
}

// Usage in page builder
function renderBlock(block: SanityBlock) {
  if (block._type.startsWith('legacy')) {
    return <LegacyRenderer block={block} />
  }
  return <ModernRenderer block={block} />
}
```

## Studio UI Indicators

## Deprecation Warnings

Add visual indicators for deprecated schemas:

```typescript
// schemaTypes/legacy/sections/faqSection.ts
export default defineType({
  name: "faqSection",
  type: "object",
  title: "FAQ Section (Deprecated)",
  description: "⚠️ DEPRECATED: Use Collapsible Section instead. This component will be removed in Q3 2026.",
  fields: [
    // ... legacy fields
  ],
  preview: {
    prepare() {
      return {
        title: "FAQ Section (Deprecated)",
        subtitle: "⚠️ Migrate to Collapsible Section",
      }
    },
  },
})
```

## Hidden from Insert Menu

Prevent new usage while supporting existing content:

```typescript
// sanity.config.ts
export default defineConfig({
  schema: {
    types: schemaTypes,
    // Hide deprecated types from insert menu
    templates: (prev) => {
      return prev.filter(
        (template) => !template.id?.startsWith('legacy')
      )
    },
  },
})
```

**Benefit**: Existing content renders, but editors cannot add new legacy sections

## Migration Scripts

## Identify Content Needing Migration

```typescript
// scripts/identify-legacy-content.ts
import { client } from './sanityClient'

async function identifyLegacyContent() {
  // Find all documents with legacy sections
  const documents = await client.fetch(`
    *[_type == "page" && count(content[_type in [
      "faqSection",
      "videoList",
      "bioModalList"
    ]]) > 0] {
      _id,
      title,
      "legacySections": content[_type in ["faqSection", "videoList", "bioModalList"]] {
        _type,
        _key
      }
    }
  `)

  console.log(`Found ${documents.length} pages with legacy content:`)
  documents.forEach((doc) => {
    console.log(`  - ${doc.title} (${doc._id}): ${doc.legacySections.length} legacy sections`)
  })
}

identifyLegacyContent()
```

## Programmatic Migration

```typescript
// scripts/migrate-faq-to-collapsible.ts
import { client } from './sanityClient'

async function migrateFaqSections() {
  const pages = await client.fetch(`
    *[_type == "page" && count(content[_type == "faqSection"]) > 0] {
      _id,
      _rev,
      content
    }
  `)

  for (const page of pages) {
    const migratedContent = page.content.map((block) => {
      if (block._type === 'faqSection') {
        return {
          ...block,
          _type: 'collapsibleSection',
          items: block.faqs.map(faq => ({
            heading: faq.question,
            content: faq.answer,
            _key: faq._key,
          })),
          // Remove old faq field
          faqs: undefined,
        }
      }
      return block
    })

    await client
      .patch(page._id)
      .set({ content: migratedContent })
      .commit()

    console.log(`Migrated: ${page._id}`)
  }
}

migrateFaqSections()
```

**Important**: Always backup content before running migration scripts

## Phased Rollout

## Phase 1: Dual Schema Support

- Add modern schemas
- Keep legacy schemas active
- Update Studio UI with deprecation warnings
- Train content editors on new patterns

**Duration**: 1-2 months

**Goal**: All new content uses modern schemas

## Phase 2: Content Migration

- Identify legacy content
- Run migration scripts OR manually migrate
- Validate migrated content
- Monitor frontend for rendering issues

**Duration**: 2-4 months

**Goal**: 90%+ content migrated to modern schemas

## Phase 3: Legacy Deprecation

- Remove legacy types from schema registry
- Archive legacy schema files
- Update frontend to remove legacy renderers
- Final cleanup of unused code

**Duration**: 1 month

**Goal**: Zero legacy content, clean codebase

## Pattern Selection Guidelines

## Use Legacy Folder When:

- Major schema refactoring required
- 10+ schemas being deprecated
- Multi-month migration timeline
- Large existing content base

**Source Confidence**: 33% (ripplecom v4 only)

## Use Schema Versioning When:

- Breaking changes to popular schemas
- Need explicit version tracking
- Small number of schemas affected
- Programmatic migration feasible

**Source Confidence**: N/A (not observed)

## Use Transformation Layer When:

- Quick migration needed
- Content structure is similar
- Can't modify schemas directly
- Testing new patterns

**Source Confidence**: N/A (common pattern, not observed)

## Skip Legacy Management When:

- Small project (< 50 pages)
- Few content editors
- Fresh project (< 6 months old)
- Can coordinate big-bang migration

**Source Confidence**: 67% (helix + kariusdx have no legacy folders)

## Common Pitfalls

## Removing Schemas Before Content Migration

**Problem**: Content references deleted schemas, breaking Studio and frontend

**Solution**: Keep schemas until ALL content migrated

## No Migration Timeline

**Problem**: Legacy content accumulates indefinitely

**Solution**: Set explicit deprecation timeline (e.g., "Remove Q3 2026")

## Complex Migration Scripts Without Backups

**Problem**: Script error corrupts content

**Solution**: Always export/backup before running migrations

```bash
# Export dataset before migration
sanity dataset export production backup-$(date +%Y%m%d).tar.gz
```

## No Frontend Backward Compatibility

**Problem**: Deploy modern frontend before content migration complete

**Solution**: Frontend must support both legacy and modern during transition

## Monitoring Migration Progress

## Dashboard Query

```groq
{
  "total": count(*[_type == "page"]),
  "withLegacy": count(*[_type == "page" && count(content[_type in ["faqSection", "videoList"]]) > 0]),
  "modern": count(*[_type == "page" && count(content[_type in ["faqSection", "videoList"]]) == 0]),
  "percentMigrated": round(
    (count(*[_type == "page" && count(content[_type in ["faqSection", "videoList"]]) == 0]) /
     count(*[_type == "page"])) * 100
  )
}
```

**Output**:
```json
{
  "total": 150,
  "withLegacy": 23,
  "modern": 127,
  "percentMigrated": 85
}
```

## Related Patterns

- **Content Block Organization**: Legacy folder structure
- **Schema Definitions**: Modern defineType API vs legacy patterns
- **Page Builder Architecture**: Supporting multiple content patterns

## See Also

- [Content Block Organization](./content-block-organization.md)
- [Page Builder Architecture](./page-builder-architecture.md)
