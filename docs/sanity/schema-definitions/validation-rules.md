---
title: "Validation Rules for Schema Fields"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "validation", "required", "min", "max", "custom"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Validation Rules for Schema Fields

## Overview

Sanity validation rules enforce data quality constraints at the schema level, preventing invalid content from being published. All three analyzed repositories use validation rules, with adoption ranging from minimal (0.2 rules per schema in Helix) to extensive (2.3 rules per schema in Ripplecom). Validation syntax is 100% consistent across all projects.

## Pattern Adoption

**Adoption Rate:** 100% (all 3 repositories use validation)

**Rule Density:**
- **Ripplecom (v4)**: 179 rules across 78 schemas = **2.3 rules per schema**
- **Kariusdx (v2)**: 51 rules across 64 schemas = **0.8 rules per schema**
- **Helix (v3)**: 1 rule across 5 schemas = **0.2 rules per schema**

**Total:** 231 validation rules across 147 schemas = **1.57 rules per schema (average)**

## Common Validation Patterns

## Required Fields

The most common validation pattern ensures fields cannot be empty before publishing.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
defineField({
  name: "title",
  title: "Post Title",
  type: "string",
  validation: (Rule) => Rule.required(),
})

defineField({
  name: "content",
  title: "Post Content",
  type: "richText",
  validation: (Rule) => Rule.required(),
})
```

## String Length Constraints

Maximum length validation prevents content from exceeding character limits for SEO or design requirements.

```typescript
// Common pattern: SEO title limits
defineField({
  name: "seoTitle",
  title: "SEO Title",
  type: "string",
  validation: (Rule) => Rule.required().max(60),
  description: "Optimal length: 50-60 characters for search results",
})

defineField({
  name: "metaDescription",
  title: "Meta Description",
  type: "text",
  validation: (Rule) => Rule.max(160),
  description: "Optimal length: 150-160 characters",
})

defineField({
  name: "title",
  title: "Post Title",
  type: "string",
  validation: (Rule) => Rule.required().max(180),
})
```

## Minimum Length Requirements

Minimum length validation ensures content meets quality thresholds.

```typescript
defineField({
  name: "excerpt",
  title: "Post Excerpt",
  type: "text",
  validation: (Rule) => Rule.min(50).max(200),
  description: "Summary should be 50-200 characters",
})
```

## Numeric Ranges

Number fields use `min()` and `max()` to enforce valid ranges.

```typescript
defineField({
  name: "priority",
  title: "Display Priority",
  type: "number",
  validation: (Rule) => Rule.min(0).max(100),
  description: "0 = lowest priority, 100 = highest",
})

defineField({
  name: "stock",
  title: "Stock Quantity",
  type: "number",
  validation: (Rule) => Rule.min(0).integer(),
})
```

## Chaining Validation Rules

## Multiple Constraints on Single Field

Validation rules can be chained to enforce multiple requirements.

```typescript
defineField({
  name: "username",
  title: "Username",
  type: "string",
  validation: (Rule) =>
    Rule.required()
        .min(3)
        .max(20)
        .regex(/^[a-z0-9_-]+$/, {
          name: "username",
          invert: false,
        }),
  description: "3-20 characters, lowercase letters, numbers, hyphens, underscores only",
})
```

## Common Chaining Patterns

```typescript
// Required + length constraint
validation: (Rule) => Rule.required().max(180)

// Required + min/max range
validation: (Rule) => Rule.required().min(1).max(100)

// Optional but with length limit if provided
validation: (Rule) => Rule.max(60)

// Required + custom format
validation: (Rule) => Rule.required().regex(/^[A-Z]{2}-\d{4}$/)
```

## Custom Validation Functions

## Custom Validation with Error Messages

Custom validation functions provide conditional logic and contextual error messages.

```typescript
defineField({
  name: "endDate",
  title: "Event End Date",
  type: "datetime",
  validation: (Rule) =>
    Rule.custom((endDate, context) => {
      const startDate = context.document?.startDate

      if (!endDate) {
        return "End date is required"
      }

      if (startDate && new Date(endDate) < new Date(startDate)) {
        return "End date must be after start date"
      }

      return true // Validation passes
    }),
})
```

## Cross-Field Validation

Custom validation can reference other fields in the document for complex business rules.

```typescript
defineField({
  name: "discountPrice",
  title: "Discount Price",
  type: "number",
  validation: (Rule) =>
    Rule.custom((discountPrice, context) => {
      const regularPrice = context.document?.regularPrice

      if (!discountPrice) return true // Optional field

      if (regularPrice && discountPrice >= regularPrice) {
        return "Discount price must be less than regular price"
      }

      if (discountPrice < 0) {
        return "Price cannot be negative"
      }

      return true
    }),
})
```

## Async Validation with External Checks

Validation can perform asynchronous operations like API calls to verify uniqueness.

```typescript
defineField({
  name: "email",
  title: "Email Address",
  type: "string",
  validation: (Rule) =>
    Rule.custom(async (email) => {
      if (!email) return "Email is required"

      // Check email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        return "Invalid email format"
      }

      // Check if email already exists (example)
      // const exists = await checkEmailExists(email)
      // if (exists) return "Email already registered"

      return true
    }),
})
```

## Helix Pattern: Hierarchical Slug Validation

## Unique Slugs Across All Documents

Helix implements a unique slug validation that checks across all document types.

```javascript
// helix-dot-com-sanity/schemas/documents/page.js
import isUniqueAcrossAllDocuments from '../../lib/isUniqueAcrossAllDocuments'

export default {
  name: 'page',
  type: 'document',
  fields: [
    {
      name: 'slug',
      type: 'slug',
      title: 'Slug/Path',
      options: {
        source: (doc, options) => ({ doc, options }),
        isUnique: isUniqueAcrossAllDocuments, // Custom uniqueness check
        slugify: asyncSlugifier,
      },
      validation: (Rule) => Rule.required(),
    },
  ],
}
```

## Custom Uniqueness Validator Implementation

```javascript
// helix-dot-com-sanity/lib/isUniqueAcrossAllDocuments.js
export default async function isUniqueAcrossAllDocuments(slug, context) {
  const { document, getClient } = context
  const client = getClient({ apiVersion: '2023-05-09' })
  const id = document._id.replace(/^drafts\./, '')

  const params = {
    draft: `drafts.${id}`,
    published: id,
    slug: slug.current,
  }

  const query = `!defined(*[
    !(_id in [$draft, $published]) &&
    slug.current == $slug
  ][0]._id)`

  const result = await client.fetch(query, params)
  return result
}
```

## Array and Reference Validation

## Required Array with Minimum Items

Array fields can require a minimum number of items.

```typescript
defineField({
  name: "categories",
  title: "Categories",
  type: "array",
  of: [{ type: "reference", to: [{ type: "category" }] }],
  validation: (Rule) => Rule.required().min(1).max(3),
  description: "Select 1-3 categories",
})
```

## Reference Field Validation

Reference fields can be required and limited to specific quantities.

```typescript
defineField({
  name: "author",
  title: "Author",
  type: "reference",
  to: [{ type: "person" }],
  validation: (Rule) => Rule.required(),
})

defineField({
  name: "relatedPosts",
  title: "Related Posts",
  type: "array",
  of: [{ type: "reference", to: [{ type: "blogPost" }] }],
  validation: (Rule) => Rule.max(5),
  description: "Select up to 5 related posts",
})
```

## URL and Email Validation

## URL Format Validation

URL fields use regex to enforce valid URL patterns.

```typescript
defineField({
  name: "websiteUrl",
  title: "Website URL",
  type: "url",
  validation: (Rule) =>
    Rule.uri({
      scheme: ['http', 'https'],
      allowRelative: false,
    }),
})
```

## Email Format Validation

Email fields validate against standard email regex patterns.

```typescript
defineField({
  name: "contactEmail",
  title: "Contact Email",
  type: "string",
  validation: (Rule) =>
    Rule.regex(
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      { name: "email" }
    ).error("Must be a valid email address"),
})
```

## Conditional Validation

## Validation Based on Document State

Validation can vary based on other field values using custom functions.

```typescript
defineField({
  name: "externalUrl",
  title: "External URL",
  type: "url",
  validation: (Rule) =>
    Rule.custom((url, context) => {
      const isExternal = context.document?.linkType === "external"

      if (isExternal && !url) {
        return "External URL is required when link type is external"
      }

      return true
    }),
  hidden: ({ document }) => document?.linkType !== "external",
})
```

## Error Severity Levels

## Error vs Warning vs Info

Sanity supports different validation severity levels.

```typescript
// Error: Blocks publishing
validation: (Rule) => Rule.required().error("This field is required")

// Warning: Allows publishing with warning
validation: (Rule) =>
  Rule.max(60).warning("Titles over 60 characters may be truncated in search results")

// Info: Informational only
validation: (Rule) =>
  Rule.min(50).info("Longer descriptions tend to perform better")
```

## Validation Best Practices

## Progressive Validation Strategy

Start with basic required/max validation and add complexity as needed.

**Phase 1: Basic Validation**
```typescript
validation: (Rule) => Rule.required()
```

**Phase 2: Add Constraints**
```typescript
validation: (Rule) => Rule.required().max(180)
```

**Phase 3: Add Custom Logic**
```typescript
validation: (Rule) =>
  Rule.required()
      .max(180)
      .custom((value) => {
        // Additional business logic
        return true
      })
```

## Helpful Validation Messages

Provide clear, actionable error messages that explain what's wrong and how to fix it.

**❌ Bad: Vague message**
```typescript
validation: (Rule) => Rule.required().error("Invalid")
```

**✅ Good: Specific guidance**
```typescript
validation: (Rule) =>
  Rule.required()
      .max(60)
      .error("SEO title is required and must be 60 characters or less for optimal search display")
```

## Anti-Patterns

## Over-Validation

Excessive validation constraints frustrate editors and slow content creation.

**❌ Bad: Too restrictive**
```typescript
validation: (Rule) =>
  Rule.required()
      .min(100)
      .max(120)
      .regex(/^[A-Z]/)
      .custom((value) => {
        // 10 more custom checks...
      })
```

**✅ Good: Necessary constraints only**
```typescript
validation: (Rule) => Rule.required().max(180)
```

## Validation Without Description

Validation rules without field descriptions leave editors guessing requirements.

**❌ Bad: No guidance**
```typescript
defineField({
  name: "seoTitle",
  type: "string",
  validation: (Rule) => Rule.max(60),
})
```

**✅ Good: Clear description**
```typescript
defineField({
  name: "seoTitle",
  type: "string",
  validation: (Rule) => Rule.max(60),
  description: "Optimal length: 50-60 characters for search results",
})
```

## Blocking Validation for Optional Fields

Don't use `.error()` on optional fields; use `.warning()` instead.

**❌ Bad: Blocks publishing for optional field**
```typescript
validation: (Rule) => Rule.max(160).error("Too long")
```

**✅ Good: Warns but allows publishing**
```typescript
validation: (Rule) => Rule.max(160).warning("Descriptions over 160 characters may be truncated")
```

## Implementation Checklist

- [ ] Add `required()` validation to all mandatory fields
- [ ] Set `max()` limits for string fields with length requirements (titles, descriptions)
- [ ] Add `min()`/`max()` ranges for numeric fields
- [ ] Use custom validation for cross-field dependencies
- [ ] Provide clear `description` text explaining validation requirements
- [ ] Use `.warning()` for recommendations, `.error()` for hard requirements
- [ ] Test validation by attempting to publish invalid content
- [ ] Document custom validation logic in code comments

## Related Patterns

- **Field Groups**: Validation applies regardless of which group a field is in
- **Conditional Fields**: `hidden` fields may skip validation when hidden
- **Preview Configuration**: Validation does not affect preview display
- **Initial Values**: `initialValue` should satisfy validation rules

## References

- Ripplecom (v4): 179 validation rules (2.3 per schema)
- Kariusdx (v2): 51 validation rules (0.8 per schema)
- Helix (v3): 1 validation rule with custom uniqueness checker
- Sanity Validation Documentation: https://www.sanity.io/docs/validation
