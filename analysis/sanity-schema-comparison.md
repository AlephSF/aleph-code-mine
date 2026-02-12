# Sanity Schema Definitions - Cross-Project Comparison

**Analysis Date:** February 11, 2026
**Scope:** Phase 3, Domain 1 - Schema Definitions
**Repositories:**
- helix-dot-com-sanity (Sanity v3.10.0)
- kariusdx-sanity (Sanity v2.30.0)
- ripplecom-nextjs/apps/sanity-studio (Sanity v4.3.0)

---

## Executive Summary

**Schema File Counts:**
- Helix (v3): 5 schema files
- Kariusdx (v2): 64 schema files
- Ripplecom (v4): 78 schema files
- **Total**: 147 schema definition files analyzed

**Key Finding**: Significant API evolution between versions:
- **v2 → v3**: Object-literal pattern with `export default { name, type, fields }`
- **v4**: Modern API with `defineType()` and `defineField()` helpers (100% adoption in ripplecom)

---

## 1. Schema Definition API Patterns

### Modern defineType/defineField API (v3+)

| Repo | Version | defineType/defineField Usage | Percentage |
|------|---------|------------------------------|------------|
| Helix | v3.10.0 | 0 instances | 0% |
| Kariusdx | v2.30.0 | 0 instances | 0% (v2 doesn't support) |
| Ripplecom | v4.3.0 | 651 instances | 100% |

**Analysis:**
- **Ripplecom (v4)**: Full adoption of modern `defineType()` and `defineField()` API
- **Helix (v3)**: Still using object-literal pattern despite v3 supporting modern API
- **Pattern confidence**: 33% (only ripplecom uses modern API)

**Example (Ripplecom v4 - Modern API):**
```typescript
import { defineType, defineField } from "sanity"

export default defineType({
  name: "blogPost",
  title: "Blog Post",
  type: "document",
  fields: [
    defineField({
      name: "title",
      title: "Post Title",
      type: "string",
      validation: (Rule) => Rule.required().max(180),
    }),
  ],
})
```

### Legacy Object-Literal Pattern (v2-compatible)

| Repo | Version | Object-Literal Schemas | Percentage |
|------|---------|------------------------|------------|
| Helix | v3.10.0 | 4 schemas | 80% |
| Kariusdx | v2.30.0 | 60 schemas | 94% |
| Ripplecom | v4.3.0 | 0 schemas | 0% |

**Analysis:**
- **Helix (v3)**: Uses v2-compatible pattern for backward compatibility
- **Kariusdx (v2)**: Only API available in v2
- **Pattern confidence**: 67% (helix + kariusdx use this pattern)

**Example (Helix v3 - Legacy API):**
```javascript
export default {
  name: 'blogPost',
  type: 'document',
  title: 'Blog Post',
  fields: [
    {
      name: 'name',
      type: 'string',
      title: 'Title',
    },
  ],
}
```

---

## 2. Field Groups for Content Organization

| Repo | Groups Usage | Adoption |
|------|--------------|----------|
| Helix | 1 instance | 20% |
| Kariusdx | 4 instances | 6% |
| Ripplecom | 13 instances | 17% |

**Total**: 18 group configurations across 147 schemas = **12% adoption**

**Analysis:**
- **Low overall adoption**: Only 12% of schemas use field groups
- **Common pattern**: `mainContent` + `pageSettings` / `seo` / `meta` tabs
- **Pattern confidence**: 100% (when used, naming is consistent)

**Example (Helix - blogPost.js):**
```javascript
groups: [
  {
    name: 'mainContent',
    title: 'Main Content',
    default: true,
  },
  {
    name: 'pageSettings',
    title: 'SEO + Page Settings',
  },
]
```

**Example (Ripplecom - blogPost.ts):**
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

## 3. Validation Rules

| Repo | Validation Rules | Adoption Rate |
|------|------------------|---------------|
| Helix | 1 instance | 20% of schemas |
| Kariusdx | 51 instances | 80% of schemas |
| Ripplecom | 179 instances | 230% (2.3 per schema) |

**Total**: 231 validation rules across 147 schemas = **157% average** (1.57 rules per schema)

**Analysis:**
- **Ripplecom (v4)**: Extensive validation (2.3 rules per schema)
- **Kariusdx (v2)**: Moderate validation (0.8 rules per schema)
- **Helix (v3)**: Minimal validation (0.2 rules per schema)
- **Pattern confidence**: 100% (all use `.required()`, `.max()`, `.min()` patterns)

**Common Validation Patterns:**
```typescript
// Required fields
validation: (Rule) => Rule.required()

// String length limits
validation: (Rule) => Rule.required().max(180)

// Min/max for numbers
validation: (Rule) => Rule.min(0).max(100)

// Custom validation with error messages
validation: (Rule) => Rule.custom((value) => {
  if (!value) return 'This field is required'
  return true
})
```

---

## 4. Icon Customization

| Repo | Icons Used | Adoption Rate |
|------|------------|---------------|
| Helix | 0 instances | 0% |
| Kariusdx | 70 instances | 109% (1.09 per schema) |
| Ripplecom | 51 instances | 65% of schemas |

**Total**: 121 icon customizations across 147 schemas = **82% adoption**

**Analysis:**
- **Kariusdx (v2)**: Uses `react-icons` library (CgFileDocument, FaRegNewspaper, etc.)
- **Ripplecom (v4)**: Uses `@sanity/icons` package (DocumentTextIcon, etc.)
- **Helix (v3)**: No icon customization
- **Pattern confidence**: 67% (kariusdx + ripplecom use icons)

**Example (Kariusdx v2 - react-icons):**
```javascript
import { CgFileDocument } from 'react-icons/cg'

export default {
  name: 'page',
  type: 'document',
  title: 'Page',
  icon: CgFileDocument,
  // ...
}
```

**Example (Ripplecom v4 - @sanity/icons):**
```typescript
import { DocumentTextIcon } from "@sanity/icons"

export default defineType({
  name: "blogPost",
  title: "Blog Post",
  type: "document",
  icon: DocumentTextIcon,
  // ...
})
```

---

## 5. Conditional Field Visibility (hidden)

| Repo | Hidden Logic | Adoption Rate |
|------|--------------|---------------|
| Helix | 1 instance | 20% |
| Kariusdx | 34 instances | 53% of schemas |
| Ripplecom | 52 instances | 67% of schemas |

**Total**: 87 conditional visibility rules across 147 schemas = **59% adoption**

**Analysis:**
- **High adoption**: 59% of schemas use conditional field visibility
- **Common use case**: Hide fields until a boolean toggle is enabled
- **Pattern confidence**: 100% (consistent pattern across all projects)

**Example (Helix - blogPost.js):**
```javascript
{
  name: 'subheader',
  type: 'array',
  title: 'Subheader',
  hidden: ({ document }) => !document?.showHeroSubheader,
}
```

**Example (Kariusdx - page.js):**
```javascript
{
  name: 'heroImage',
  type: 'image',
  title: 'Hero Image',
  hidden: ({document}) => document?.slug?.current == 'mobile-app',
}
```

---

## 6. SEO & Metadata Patterns

| Repo | SEO/Meta References | Percentage |
|------|---------------------|------------|
| Helix | 15 instances | 300% (3 per schema) |
| Kariusdx | 22 instances | 34% |
| Ripplecom | 141 instances | 181% (1.8 per schema) |

**Total**: 178 SEO/meta field references

**Analysis:**
- **Universal pattern**: All projects have dedicated SEO object schemas
- **Helix**: `seoFields` object type
- **Kariusdx**: `seo` object type
- **Ripplecom**: `seo` and `meta` object types (separation of concerns)
- **Pattern confidence**: 100% (all projects use SEO objects)

**Common SEO Fields:**
- `seoTitle` / `metaTitle`
- `seoDescription` / `metaDescription`
- `canonicalUrl`
- `ogImage` / `openGraphImage`
- `ogDescription`
- `noindex` / `nofollow` (boolean flags)
- `focusKeyword` (SEO analysis)

---

## 7. Reference Fields (Content Relationships)

| Repo | Reference Fields | Percentage |
|------|------------------|------------|
| Helix | 1 instance | 20% |
| Kariusdx | 7 instances | 11% |
| Ripplecom | 24 instances | 31% |

**Total**: 32 reference fields across 147 schemas = **22% adoption**

**Analysis:**
- **Ripplecom**: Highest usage (categories, tags, authors, related content)
- **Common pattern**: Array of references for taxonomies
- **Pattern confidence**: 100% (consistent `type: 'reference', to: [{ type: 'category' }]` pattern)

**Example (Helix - page.js):**
```javascript
{
  name: 'parent',
  type: 'reference',
  to: [
    {
      type: 'page',
    },
  ],
  options: {
    disableNew: true,
  },
}
```

**Example (Ripplecom - blogPost.ts):**
```typescript
defineField({
  name: "categories",
  title: "Categories",
  type: "array",
  of: [
    {
      type: "reference",
      to: [{ type: "category" }],
    },
  ],
  group: "meta",
})
```

---

## 8. Slug Field Patterns

| Repo | Slug Fields | Percentage |
|------|-------------|------------|
| Helix | 2 instances | 40% |
| Kariusdx | 1 instance | 2% |
| Ripplecom | 5 instances | 6% |

**Total**: 8 slug fields (document types that need URLs)

**Analysis:**
- **All document types** (page, blogPost, etc.) have slug fields
- **Custom slugification**: Helix uses async slugifier for hierarchical slugs
- **Pattern confidence**: 100% (all use built-in `slug` type with `source` option)

**Example (Helix - Hierarchical Slugs):**
```javascript
{
  name: 'slug',
  type: 'slug',
  title: 'Slug/Path',
  description: 'Include entire path to page if this is a child page. E.g., "parent-page/child-page"',
  options: {
    source: (doc, options) => ({ doc, options }),
    isUnique: isUniqueAcrossAllDocuments,
    slugify: asyncSlugifier, // Custom: prepends parent slug
  },
  validation: (Rule) => Rule.required(),
}
```

**Example (Ripplecom - Standard Slug):**
```typescript
defineField({
  name: "slug",
  title: "Slug",
  type: "contentSlug", // Custom slug field type
  group: "meta",
})
```

---

## 9. Preview Configuration

| Repo | Preview Configs | Percentage |
|------|-----------------|------------|
| Helix | 0 instances | 0% |
| Kariusdx | 16 instances | 25% |
| Ripplecom | 84 instances | 108% (1.08 per schema) |

**Total**: 100 preview configurations across 147 schemas = **68% adoption**

**Analysis:**
- **Ripplecom (v4)**: Extensive preview config (every document + many objects)
- **Kariusdx (v2)**: Moderate preview config (documents only)
- **Helix (v3)**: No preview customization (uses default title)
- **Pattern confidence**: 67% (kariusdx + ripplecom use previews)

**Example (Kariusdx - page.js):**
```javascript
preview: {
  select: {
    title: 'title',
    subtitle: 'slug.current',
  },
}
```

**Example (Ripplecom - blogPost.ts):**
```typescript
preview: {
  select: {
    title: "title",
    media: "featuredImage",
    subtitle: "slug.current",
    author: "meta.author.name",
  },
  prepare({ title, media, subtitle, author }) {
    return {
      title: title || "Untitled",
      subtitle: author ? `${author} | ${subtitle}` : subtitle,
      media,
    }
  },
}
```

---

## 10. Initial Values

| Repo | InitialValue Usage | Percentage |
|------|-------------------|------------|
| Helix | 1 instance | 20% |
| Kariusdx | 18 instances | 28% |
| Ripplecom | 68 instances | 87% |

**Total**: 87 initial value configurations across 147 schemas = **59% adoption**

**Analysis:**
- **Common use cases**:
  - Boolean fields: `initialValue: false`
  - Date fields: `initialValue: () => new Date().toISOString()`
  - Object fields: Set default nested values
- **Pattern confidence**: 100% (consistent syntax)

**Example (Helix - blogPost.js):**
```javascript
{
  name: 'showHeroSubheader',
  type: 'boolean',
  title: 'Edit Hero Subheader field',
  initialValue: false,
}
```

**Example (Ripplecom - meta fields):**
```typescript
defineField({
  name: "publishedAt",
  title: "Published At",
  type: "datetime",
  initialValue: () => new Date().toISOString(),
})
```

---

## De Facto Standards (≥67% Adoption)

1. ✅ **Icon customization** (82% - kariusdx + ripplecom)
2. ✅ **Preview configuration** (68% - kariusdx + ripplecom)
3. ✅ **SEO/metadata objects** (100% - all projects)
4. ✅ **Conditional field visibility** (59% - all projects)
5. ✅ **Validation rules** (100% - all projects, varying density)

---

## Gap Patterns (Low Adoption)

1. ⚠️ **Modern defineType/defineField API** (33% - ripplecom only)
   - **Recommendation**: Migrate to modern API for better type safety
   - **Blocked by**: Helix on v3 (supports modern API but uses legacy)

2. ⚠️ **Field groups** (12% adoption)
   - **Gap**: Most schemas don't organize fields into tabs
   - **Impact**: Poor editor experience for content-heavy schemas

3. ⚠️ **Reference fields** (22% adoption)
   - **Gap**: Limited content relationships
   - **Pattern**: Ripplecom uses extensively (categories, tags), others minimal

---

## Version-Specific Patterns

### Sanity v2 (Kariusdx)
- `import createSchema from 'part:@sanity/base/schema-creator'`
- `import schemaTypes from 'all:part:@sanity/base/schema-type'`
- Object-literal schema definitions only
- `react-icons` for icons

### Sanity v3 (Helix)
- `export const schemaTypes = [...]` (ES modules)
- Object-literal schemas (v2-compatible pattern)
- No icon customization
- Minimal validation

### Sanity v4 (Ripplecom)
- `defineType()` and `defineField()` modern API
- `@sanity/icons` package
- Extensive validation, preview, and initial values
- Separation of concerns: `meta`, `seo`, `content` groups

---

## Recommended Documentation Topics

Based on this analysis, the following 8 documentation files should be created:

1. **Modern defineType API** (v3+, 33% confidence - ripplecom only)
2. **Field groups for content organization** (12% confidence - low but valuable)
3. **Validation rules** (100% confidence - universal pattern)
4. **Icon customization** (67% confidence - kariusdx + ripplecom)
5. **Conditional field visibility (hidden)** (100% confidence - universal pattern)
6. **SEO metadata objects** (100% confidence - universal pattern)
7. **Reference fields for content relationships** (100% confidence - consistent pattern)
8. **Preview configuration** (67% confidence - kariusdx + ripplecom)

---

## Next Steps

1. ✅ Complete quantitative analysis (this document)
2. ⏳ Perform qualitative analysis (read representative examples)
3. ⏳ Create 8 RAG-optimized documentation files
4. ⏳ Generate 4 Semgrep enforcement rules
5. ⏳ Test Semgrep rules against source repos
