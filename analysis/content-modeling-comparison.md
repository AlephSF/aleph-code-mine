# Content Modeling - Cross-Project Comparison

**Analysis Date:** February 12, 2026
**Scope:** Phase 3, Domain 3 - Content Modeling Patterns
**Repositories:**
- helix-dot-com-sanity (Sanity v3.10.0)
- kariusdx-sanity (Sanity v2.30.0)
- ripplecom-nextjs/apps/sanity-studio (Sanity v4.3.0)

---

## Executive Summary

**Schema File Counts:**
- Helix (v3): 2 document types (minimal CMS)
- Kariusdx (v2): 11 document types + 20 builder blocks
- Ripplecom (v4): 16 document types + 15 components + 6 globals + 16 legacy sections
- **Total**: 29 document types + 35 reusable content blocks

**Key Findings**:
- **Page Builder Adoption**: 67% (kariusdx + ripplecom use modular page builders)
- **Global/Singleton Documents**: 33% (ripplecom only - navigation, homepage, SEO metadata)
- **Content Hierarchies**: 33% (helix only - parent-child page relationships)
- **Rich Text Patterns**: 100% (all use portable text / block content)

---

## 1. Page Builder Architecture

### Pattern: Flat Content Array (Ripplecom v4)

**Adoption**: 33% (ripplecom only)

**Structure**:
```typescript
content: array of [
  { type: "heroSection" },
  { type: "textSection" },
  { type: "imageSection" },
  { type: "video" },
  { type: "cardGrid" },
  { type: "quote" },
  { type: "ctaSection" },
  { type: "spacer" },
]
```

**Characteristics**:
- Flat array structure (no nesting)
- Each section is self-contained
- 15 component types available
- Modern section names (heroSection, textSection, ctaSection)

**Example (ripplecom page.ts)**:
```typescript
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
})
```

---

### Pattern: Nested Section Wrappers (Kariusdx v2)

**Adoption**: 33% (kariusdx only)

**Structure**:
```javascript
pageBuilder: array of [
  {
    type: "pageSection",
    fields: {
      sectionTitle: string,
      backgroundcolor: enum,
      innerBlocks: array of [20 block types]
    }
  },
  { type: "pathogenList" },
  { type: "wistiaEmbed" },
  { type: "jobPostings" },
]
```

**Characteristics**:
- Nested array structure (section wrapper + innerBlocks)
- `pageSection` provides layout controls (background color, padding)
- 20 builder block types available
- Flexible nesting of content blocks

**Example (kariusdx pageSection.js)**:
```javascript
{
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
    },
    {
      name: 'innerBlocks',
      type: 'array',
      of: [
        { type: 'button' },
        { type: 'richText' },
        { type: 'imageCarousel' },
        // ... 17 more block types
      ],
    },
  ],
}
```

---

### Pattern: Minimal Content Structure (Helix v3)

**Adoption**: 33% (helix only)

**Structure**:
- No page builder
- Simple field-based content structure
- Hierarchical pages (parent-child relationships)

**Characteristics**:
- 2 document types only (page, blogPost)
- No modular content blocks
- Portable text for rich content
- Focus on hierarchy over modularity

---

## 2. Content Block Naming Conventions

### Component Names (Ripplecom v4)

**Pattern**: `[purpose]Section` or `[component]` format

**Examples**:
- `heroSection` - Hero banner
- `textSection` - Text content block
- `imageSection` - Image display
- `ctaSection` - Call-to-action block
- `cardGrid` - Card layout
- `quote` - Quote block
- `spacer` - Spacing utility

**Philosophy**: Descriptive, purpose-driven names

---

### Builder Block Names (Kariusdx v2)

**Pattern**: `[component][Type]` or descriptive names

**Examples**:
- `pageSection` - Section wrapper
- `richText` - Rich text editor
- `cardContent` - Card display
- `imageCarousel` - Image carousel
- `hubspotForm` - Form integration
- `wistiaEmbed` - Video embed
- `pathogenList` - Domain-specific list
- `diagnosisComparison` - Domain-specific comparison

**Philosophy**: Descriptive names + domain-specific components

---

## 3. Global / Singleton Documents

### Pattern: Global Schema Folder (Ripplecom v4)

**Adoption**: 33% (ripplecom only)

**Globals Folder Structure**:
```
schemaTypes/
  globals/
    - homepage.ts (reference to page to use as homepage)
    - navigation.ts (main navigation menu)
    - footerNavigation.ts (footer links)
    - seoMetadata.ts (global SEO defaults)
    - regions.ts (geographic regions)
    - rlusdBalance.ts (dynamic data)
```

**Characteristics**:
- Dedicated `globals/` folder
- 6 global/singleton documents
- Each global uses `singleton: true` (implied by structure)
- Managed via desk structure plugin

**Example (homepage.ts)**:
```typescript
export default defineType({
  name: 'homepage',
  title: 'Homepage Setting',
  type: 'document',
  icon: HomeIcon,
  fields: [
    defineField({
      name: 'selectedPage',
      title: 'Select Homepage',
      type: 'reference',
      to: [{ type: 'page' }],
      description: 'Choose a page to be the homepage',
    }),
  ],
})
```

---

### Pattern: Single Global Document (Kariusdx v2)

**Adoption**: 33% (kariusdx only)

**Structure**:
- Single `siteSettings` document
- Contains global configuration (social links, footer, announcements)

**Example (siteSettings.js)**:
```javascript
{
  name: 'siteSettings',
  type: 'document',
  title: 'Site Settings',
  fields: [
    { name: 'footerText', type: 'text' },
    { name: 'socialLinks', type: 'array', of: [{ type: 'link' }] },
    { name: 'announcementBar', type: 'object', ... },
  ],
}
```

---

### Pattern: No Globals (Helix v3)

**Adoption**: 33% (helix only)

**Approach**: All content is document-based, no global settings in CMS

---

## 4. Rich Text / Portable Text Configuration

### Pattern: Rich Text as Object Wrapper (Ripplecom v4)

**Adoption**: 33% (ripplecom only)

**Structure**:
```typescript
{
  name: "richText",
  type: "object", // Wrapped in object to avoid nested array issues
  fields: [
    {
      name: "content",
      type: "array",
      of: [
        { type: "block", styles: [...], marks: {...} },
        { type: "image" },
        { type: "video" },
        { type: "quote" },
        { type: "button" },
        { type: "codeSnippet" },
        { type: "tableBlock" },
      ],
    },
  ],
}
```

**Rationale** (from source comments):
> "This schema is structured as an object type (not array) to avoid nested array issues when used in pageBuilder arrays. Sanity's array input renderer can experience TypeErrors with nested arrays."

**Features**:
- Custom text styles (Normal, H1-H4, Blockquote)
- Enhanced decorators (Bold, Italic, Underline, Strike, Code)
- Bullet and numbered lists
- Link annotations
- Inline objects (image, video, quote, button, codeSnippet, table)

---

### Pattern: Custom Rich Text Field (Kariusdx v2)

**Adoption**: 33% (kariusdx only)

**Structure**:
```javascript
{
  name: 'richTextCustom',
  type: 'array',
  of: [
    {
      type: 'block',
      styles: [
        { title: 'Normal', value: 'normal' },
        { title: 'H2', value: 'h2' },
        { title: 'H3', value: 'h3' },
      ],
      marks: {
        decorators: [
          { title: 'Strong', value: 'strong' },
          { title: 'Emphasis', value: 'em' },
        ],
        annotations: [
          { name: 'link', type: 'object', ... },
        ],
      },
    },
  ],
}
```

**Features**:
- Custom heading levels (H2, H3 only)
- Basic marks (strong, em)
- Link annotations

---

### Pattern: Standard Portable Text (Helix v3)

**Adoption**: 33% (helix only)

**Structure**: Uses default Sanity block content configuration

---

## 5. Content Hierarchies & Relationships

### Pattern: Hierarchical Pages (Helix v3)

**Adoption**: 33% (helix only)

**Structure**:
```javascript
{
  name: 'parent',
  type: 'reference',
  to: [{ type: 'page' }],
  options: {
    disableNew: true, // Must select existing page
  },
}
```

**Features**:
- Self-referential parent-child relationships
- Async slug generation (parent-slug/child-slug)
- Hierarchical URL structure

**Example**:
- Parent: `/about`
- Child: `/about/team`
- Grandchild: `/about/team/leadership`

---

### Pattern: Flat Taxonomy (Kariusdx + Ripplecom)

**Adoption**: 67% (kariusdx + ripplecom)

**Structure**: Flat document structure with taxonomies (categories, tags)

**Ripplecom Taxonomies**:
- `category` (blog categories)
- `tag` (flexible labeling)
- `author` (content attribution via `person` document)

**Example (ripplecom blogPost.ts)**:
```typescript
defineField({
  name: "categories",
  type: "array",
  of: [
    {
      type: "reference",
      to: [{ type: "category" }],
    },
  ],
})
```

---

## 6. Content Block Reusability

### Pattern: Components Folder (Ripplecom v4)

**Adoption**: 33% (ripplecom only)

**Organization**:
```
schemaTypes/
  components/
    - heroSection.ts
    - textSection.ts
    - cardGrid.ts
    - quote.ts
    - button.ts
    - ctaSection.ts
    - ... (15 total)
```

**Characteristics**:
- Dedicated `components/` folder
- Each component is an `object` type
- Reusable across multiple document types
- Modern naming conventions

---

### Pattern: Builder Blocks Folder (Kariusdx v2)

**Adoption**: 33% (kariusdx only)

**Organization**:
```
schemas/
  builderBlocks/
    - pageSection.js
    - richText.js
    - cardContent.js
    - imageCarousel.js
    - hubspotForm.js
    - ... (20 total)
```

**Characteristics**:
- Dedicated `builderBlocks/` folder
- Mix of layout, content, and integration blocks
- Domain-specific blocks (pathogenList, diagnosisComparison)

---

### Pattern: Inline Objects (Helix v3)

**Adoption**: 33% (helix only)

**Organization**:
```
schemas/
  objects/
    - featuredImage.js
    - seo.js
```

**Characteristics**:
- Minimal reusable objects
- Focused on metadata (SEO, featured image)
- No content blocks

---

## 7. Legacy Content Migration

### Pattern: Legacy Folder (Ripplecom v4)

**Adoption**: 33% (ripplecom only)

**Organization**:
```
schemaTypes/
  legacy/
    sections/
      - agendaSection.ts
      - bioModalList.ts
      - collapsibleSectionList.ts
      - faqSection.ts
      - videoList.ts
      - ... (16 total legacy sections)
```

**Characteristics**:
- 16 legacy section types
- Maintained for backward compatibility
- New content uses modern `components/` sections
- Gradual migration strategy

**Insight**: Demonstrates evolution from complex legacy sections to simpler modern components

---

## 8. Field Organization Patterns

### Pattern: Field Groups + Tabs (Ripplecom v4 + Kariusdx v2)

**Adoption**: 67% (kariusdx + ripplecom)

**Ripplecom Groups**:
- `content` (default) - Primary content fields
- `meta` - Metadata (author, publish date, tags)
- `seo` - SEO settings

**Kariusdx Groups**:
- `mainContent` (default) - Primary content fields
- `pageSettings` - SEO + page configuration

**Example (ripplecom page.ts)**:
```typescript
groups: [
  {
    name: "content",
    title: "Content",
    default: true,
  },
  {
    name: "meta",
    title: "Meta",
  },
  {
    name: "seo",
    title: "SEO",
  },
]
```

---

## De Facto Standards (≥67% Adoption)

1. ✅ **Page Builder Architecture** (67% - kariusdx + ripplecom)
   - Modular content blocks
   - Array-based page composition

2. ✅ **Portable Text / Rich Text** (100% - all projects)
   - Block-based content editing
   - Custom marks and annotations

3. ✅ **SEO Metadata Objects** (100% - all projects)
   - Dedicated SEO field groups
   - OpenGraph configuration

4. ✅ **Field Groups** (67% - kariusdx + ripplecom)
   - Content / Meta / SEO separation
   - Improved editor UX

---

## Gap Patterns (Low Adoption)

1. ⚠️ **Global/Singleton Documents** (33% - ripplecom only)
   - **Gap**: Most projects lack global settings management
   - **Impact**: Hard-coded navigation, footer, and site-wide config

2. ⚠️ **Content Hierarchies** (33% - helix only)
   - **Gap**: Most projects use flat structure
   - **Impact**: Cannot model complex site architectures

3. ⚠️ **Domain-Specific Content Types** (33% - kariusdx only)
   - **Pattern**: Medical/diagnostic-specific schemas (pathogen, clinicalEvidence)
   - **Insight**: Custom content modeling for specialized domains

---

## Version-Specific Patterns

### Sanity v2 (Kariusdx)
- `builderBlocks/` folder convention
- Nested section wrappers (`pageSection` + `innerBlocks`)
- Single global document (`siteSettings`)

### Sanity v3 (Helix)
- Minimal content structure (2 document types)
- Hierarchical page relationships
- No page builder

### Sanity v4 (Ripplecom)
- `components/` folder convention
- Flat section array (no wrappers)
- `globals/` folder for singletons
- `legacy/` folder for migration
- Rich text wrapped in object type (nested array workaround)

---

## Recommended Documentation Topics

Based on this analysis, the following 8 documentation files should be created:

1. **Page Builder Architecture** (67% confidence - flat vs nested patterns)
2. **Global/Singleton Documents** (33% confidence - ripplecom pattern)
3. **Content Block Organization** (67% confidence - components vs builderBlocks)
4. **Rich Text Configuration** (100% confidence - portable text patterns)
5. **Content Hierarchies** (33% confidence - hierarchical pages pattern)
6. **Content Block Naming Conventions** (100% confidence - consistent patterns)
7. **Legacy Content Migration** (33% confidence - ripplecom pattern)
8. **Reusable Content Objects** (100% confidence - SEO, featured images)

---

## Next Steps

1. ✅ Complete quantitative analysis (this document)
2. ⏳ Create 8 RAG-optimized documentation files
3. ⏳ Generate 4 Semgrep enforcement rules
4. ⏳ Test Semgrep rules against source repos
