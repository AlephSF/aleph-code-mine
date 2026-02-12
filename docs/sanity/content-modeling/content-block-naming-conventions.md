---
title: "Content Block Naming Conventions"
category: "content-modeling"
subcategory: "naming-standards"
tags: ["sanity", "naming-conventions", "components", "builder-blocks", "code-style"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Content Block Naming Conventions

## Overview

Consistent naming conventions for Sanity content blocks improve developer experience, enable pattern recognition, and facilitate frontend component mapping. All analyzed projects (100%) demonstrate clear naming patterns, with conventions varying by project architecture and Sanity version.

**Adoption**: 100% of projects follow consistent naming within their codebase. Patterns differ: modern purpose-driven names (ripplecom v4), descriptive technical names (kariusdx v2), minimal objects (helix v3).

## Naming Pattern Taxonomy

### Purpose-Driven Names (Modern)

Ripplecom (v4) uses descriptive names that emphasize component purpose over technical implementation:

**Pattern**: `[purpose][Type]` format

**Examples**:
- `heroSection` - Hero banner with CTA
- `textSection` - Text content block
- `imageSection` - Image display
- `ctaSection` - Call-to-action block
- `cardGrid` - Card layout
- `quote` - Quote block
- `spacer` - Spacing utility

**Characteristics**:
- Purpose-first naming
- `Section` suffix for full-width components
- Standalone names for inline/small components
- No technical implementation details in name

### Descriptive Technical Names (Legacy)

Kariusdx (v2) combines descriptive intent with technical details:

**Pattern**: `[component][Feature]` or domain-specific names

**Examples**:
- `pageSection` - Section wrapper with layout controls
- `richText` - Rich text editor
- `cardContent` - Card display
- `imageCarousel` - Image carousel
- `hubspotForm` - Form integration
- `wistiaEmbed` - Video embed
- `pathogenList` - Domain-specific list
- `diagnosisComparison` - Domain-specific comparison

**Characteristics**:
- Implementation details in name (`Carousel`, `Embed`)
- Domain-specific vocabulary (`pathogen`, `diagnosis`)
- Technical suffixes (`Form`, `Embed`)

### Minimal Metadata Objects

Helix (v3) uses simple descriptive names for reusable objects:

**Pattern**: `[dataType]` format

**Examples**:
- `featuredImage` - Image with hotspot
- `seo` - SEO metadata fields

**Characteristics**:
- Data-focused naming
- No redundant suffixes
- Minimal object count (2 total)

## Naming Components by Type

### Section Components

Full-width components that occupy dedicated page regions:

**Convention**: Use `Section` suffix

**Examples**:
```typescript
heroSection     // Hero banner
textSection     // Text content
imageSection    // Image display
ctaSection      // Call-to-action
cardGridSection // Card layout
```

**Rationale**:
- Clearly indicates full-width component
- Distinguishes from inline elements
- Maps to frontend section wrappers

### Inline Components

Small components embedded within other content:

**Convention**: No suffix, descriptive names

**Examples**:
```typescript
button          // CTA button
quote           // Pull quote
video           // Video player
stat            // Statistic display
badge           // Badge/tag
```

**Rationale**:
- Shorter names for common elements
- Reflects inline/embedded nature
- Matches HTML element names where appropriate

### Layout Components

Components that control spacing and arrangement:

**Convention**: Descriptive layout names

**Examples**:
```typescript
spacer          // Vertical spacing
columns         // Multi-column layout
divider         // Horizontal rule
grid            // Grid layout
```

**Rationale**:
- Clear layout intent
- Matches CSS layout concepts
- Easy pattern recognition

### Integration Components

Components connecting to external services:

**Convention**: `[service][Type]` format

**Examples**:
```typescript
hubspotForm     // HubSpot form integration
wistiaEmbed     // Wistia video embed
googleMapsEmbed // Google Maps embed
stripeCheckout  // Stripe payment integration
```

**Rationale**:
- Service name provides context
- Type suffix describes integration
- Clear external dependency

### Domain-Specific Components

Components unique to business domain:

**Convention**: Domain vocabulary + component type

**Examples (Medical - Kariusdx)**:
```typescript
pathogenList           // List of pathogens
diagnosisComparison    // Diagnosis comparison table
clinicalEvidence       // Clinical evidence display
```

**Examples (Finance - Ripplecom)**:
```typescript
rlusdBalance          // RLUSD balance display
investmentCard        // Investment opportunity card
```

**Rationale**:
- Uses domain language
- Improves business-dev communication
- Self-documenting for domain experts

## Case Conventions

### camelCase (Preferred)

**Adoption**: 100% of analyzed projects

**Format**: First word lowercase, subsequent words capitalized

**Examples**:
```typescript
heroSection
cardGrid
newsletterSignup
```

**Benefits**:
- Matches JavaScript conventions
- Compatible with JSON property names
- Consistent with Sanity documentation

### PascalCase (Avoid)

**Format**: All words capitalized

**Examples**:
```typescript
HeroSection    // ❌ Avoid - reserved for React components
CardGrid       // ❌ Avoid - conflicts with frontend
```

**Problem**: Conflicts with React component naming, creates confusion between schema types and frontend components

### kebab-case (Avoid)

**Format**: Lowercase with hyphens

**Examples**:
```typescript
"hero-section"    // ❌ Avoid - inconsistent with JS conventions
"card-grid"       // ❌ Avoid - requires quotes in object keys
```

**Problem**: Requires quotes, inconsistent with JavaScript property naming

## Suffix Guidelines

### When to Use "Section"

**Use `Section` suffix when**:
- Component occupies full page width
- Designed as standalone page region
- Includes significant whitespace/padding
- Maps to `<section>` HTML element

**Examples**:
```typescript
heroSection     // Full-width hero
textSection     // Full-width text content
ctaSection      // Full-width CTA
```

### When to Omit "Section"

**Omit `Section` suffix when**:
- Component is inline or embedded
- Size varies based on context
- Used within other components
- Maps to smaller HTML elements

**Examples**:
```typescript
button          // Not buttonSection
quote           // Not quoteSection
video           // Not videoSection
```

## Naming Anti-Patterns

### Over-Abbreviation

**Problem**: Unclear abbreviations reduce readability

```typescript
// ❌ Bad
imgCrsl         // Image carousel?
txtSec          // Text section?
ctaBtn          // CTA button?

// ✅ Good
imageCarousel
textSection
button
```

### Redundant Prefixes

**Problem**: Unnecessary prefixes add noise

```typescript
// ❌ Bad
sanityHeroSection     // "sanity" prefix is redundant
componentButton       // "component" prefix is redundant
blockQuote            // "block" prefix is redundant (in context of Sanity)

// ✅ Good
heroSection
button
quote
```

### Technical Implementation Details

**Problem**: Names expose technical implementation

```typescript
// ❌ Bad
reactHeroComponent    // React implementation detail
imageWithLazyLoad     // Loading strategy detail
formWithValidation    // Validation detail

// ✅ Good
heroSection
imageSection
form
```

### Inconsistent Suffixes

**Problem**: Mix of suffixes across similar components

```typescript
// ❌ Bad
heroSection
textBlock        // Inconsistent with "Section"
imageComponent   // Inconsistent suffix
ctaArea          // Inconsistent suffix

// ✅ Good
heroSection
textSection
imageSection
ctaSection
```

## Frontend Component Mapping

### Direct Name Mapping

```typescript
// lib/componentMap.ts
import HeroSection from '@/components/sanity/HeroSection'
import TextSection from '@/components/sanity/TextSection'
import CardGrid from '@/components/sanity/CardGrid'

export const componentMap: Record<string, React.ComponentType<any>> = {
  // Schema name (camelCase) → React component (PascalCase)
  heroSection: HeroSection,
  textSection: TextSection,
  cardGrid: CardGrid,
}

// Usage
function renderBlock(block: SanityBlock) {
  const Component = componentMap[block._type]
  return <Component {...block} />
}
```

**Benefits**:
- Clear schema-to-component mapping
- Type-safe with TypeScript
- Easy to extend

### Transform Mapping

When schema names differ from component names:

```typescript
// lib/componentMap.ts
const transformMap: Record<string, string> = {
  heroSection: 'HeroSection',
  textSection: 'TextBlock',      // Different component name
  ctaSection: 'CallToAction',    // Different component name
}

export function getComponent(schemaType: string) {
  const componentName = transformMap[schemaType]
  return componentMap[componentName]
}
```

## File Naming Conventions

### Schema Files

Match schema `name` field to filename:

```typescript
// schemaTypes/components/heroSection.ts
export default defineType({
  name: "heroSection",  // Matches filename
  type: "object",
  // ...
})
```

**Benefits**:
- Easy to locate schema files
- Grep-friendly (`grep "heroSection" schemaTypes/`)
- IDE autocomplete

### Frontend Component Files

Use PascalCase for React components:

```typescript
// components/sanity/HeroSection.tsx
export default function HeroSection(props: HeroSectionProps) {
  // ...
}
```

**Mapping Pattern**:
- `heroSection` (schema) → `HeroSection.tsx` (component file)
- `cardGrid` (schema) → `CardGrid.tsx` (component file)
- `ctaSection` (schema) → `CtaSection.tsx` (component file)

## Documentation Naming

### README Files

Document block purpose and usage:

```markdown
# Hero Section

Full-width hero banner with headline, subheadline, background image, and CTAs.

## Usage

Add to page `content` array:

\`\`\`typescript
content: [
  {
    _type: 'heroSection',
    headline: 'Welcome to Our Site',
    ...
  }
]
\`\`\`

## Fields

- `headline` (string, required)
- `subheadline` (text, optional)
- ...
```

## Pattern Selection Guidelines

### Use Purpose-Driven Names When:

- Building modern Sanity v3+ projects
- Emphasis on what component does
- Non-technical content editors
- Component library approach

**Source Confidence**: 33% (ripplecom v4 only)

### Use Descriptive Technical Names When:

- Legacy Sanity v2 projects
- Complex integrations (forms, embeds)
- Domain-specific components
- Technical team as primary users

**Source Confidence**: 33% (kariusdx v2 only)

### Use Minimal Names When:

- Small projects (< 10 schemas)
- Data-focused objects (SEO, metadata)
- No page builder architecture
- Simple content structure

**Source Confidence**: 33% (helix v3 uses minimal objects)

## Naming Checklist

Before finalizing component names, verify:

- [ ] Name describes component purpose
- [ ] Uses camelCase convention
- [ ] Consistent suffix usage (`Section` for full-width)
- [ ] No technical implementation details
- [ ] No redundant prefixes (`sanity`, `component`)
- [ ] Matches or maps cleanly to frontend component
- [ ] Easy to search/grep
- [ ] Self-documenting for content editors

## Common Pitfalls

### Changing Names After Launch

**Problem**: Renaming schema breaks existing content

**Solution**: Plan names carefully upfront, or use migration scripts

### Inconsistent Team Conventions

**Problem**: Different developers use different patterns

**Solution**: Document naming conventions in CONTRIBUTING.md

### Names Too Generic

**Problem**: `content`, `section`, `block` are ambiguous

**Solution**: Use specific, descriptive names (`textSection`, `cardGrid`)

## Related Patterns

- **Content Block Organization**: Folder structure mirrors naming conventions
- **Page Builder Architecture**: Component names used in page builder arrays
- **Reusable Content Objects**: Object naming vs component naming

## See Also

- [Content Block Organization](./content-block-organization.md)
- [Page Builder Architecture](./page-builder-architecture.md)
