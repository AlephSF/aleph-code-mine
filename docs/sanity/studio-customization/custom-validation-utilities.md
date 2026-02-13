---
title: "Custom Validation Utilities"
category: "studio-customization"
subcategory: "validation"
tags: ["sanity", "validation", "async", "unique", "slugs", "utilities"]
stack: "sanity"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

## Overview

Custom validation utilities in Sanity Studio extend built-in validation rules with async GROQ queries, uniqueness checks, and business logic validation. Custom validators enable cross-document validation, external API calls, and complex field relationships. Only 33% of analyzed projects use custom validation utilities (helix v3 only).

## Unique Slug Validation

Sanity built-in slug fields validate format but not uniqueness. Custom async validator ensures slugs are unique across all document types.

**Validation Utility:**

```javascript
// lib/isUniqueAcrossAllDocuments.js
const isUniqueAcrossAllDocuments = async (slug, context) => {
  const { document, getClient } = context
  const client = getClient({
    apiVersion: process.env.SANITY_STUDIO_API_VERSION || '2023-05-09',
  })
  const id = document._id.replace(/^drafts\./, '')
  const params = {
    draft: `drafts.${id}`,
    published: id,
    slug,
  }
  const query =
    '!defined(*[!(_id in [$draft, $published]) && slug.current == $slug][0]._id)'
  const result = await client.fetch(query, params)
  return result
}

export default isUniqueAcrossAllDocuments
```

**Schema Integration:**

```typescript
// schemaTypes/documents/page.ts
import { defineType } from 'sanity'
import isUniqueAcrossAllDocuments from '../../lib/isUniqueAcrossAllDocuments'

export default defineType({
  name: 'page',
  type: 'document',
  fields: [
    {
      name: 'slug',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 200,
      },
      validation: (Rule) =>
        Rule.required().custom(async (slug, context) => {
          const isUnique = await isUniqueAcrossAllDocuments(slug?.current, context)
          return isUnique || 'Slug is already in use'
        }),
    },
  ],
})
```

Helix uses this pattern for `page` and `blogPost` document types. Validation runs on slug change and prevents duplicate slugs across different document types (prevents `/about` page conflicting with `/about` blog post).

**Key Features:**

1. **Draft/published awareness** - Checks both `drafts.page-123` and `page-123` IDs
2. **Self-exclusion** - Excludes current document from uniqueness check
3. **Cross-document** - Validates against all document types with slugs
4. **Async** - Uses `Rule.custom(async ...)` for GROQ query

## Validation Context Object

Custom validation functions receive `context` object with document metadata and Sanity client.

**Context Properties:**

```typescript
interface ValidationContext {
  document: {
    _id: string // 'drafts.page-123' or 'page-123'
    _type: string // 'page'
    _rev: string // Revision ID
    // ... all document fields
  }
  parent?: object // Parent field (for array/object items)
  getClient: (config?: { apiVersion: string }) => SanityClient
}
```

**Accessing Document Fields:**

```typescript
validation: (Rule) =>
  Rule.custom((value, context) => {
    const { document } = context
    if (document.category === 'premium' && !value) {
      return 'Premium content requires this field'
    }
    return true
  })
```

Use `context.document` to access other fields for conditional validation.

## Async Validation Patterns

Async validators support Promises for external API calls, GROQ queries, and slow validation logic.

**External API Validation:**

```typescript
const validateEmailDomain = async (email) => {
  const domain = email?.split('@')[1]
  if (!domain) return 'Invalid email format'

  const response = await fetch(`https://api.mailcheck.ai/domain/${domain}`)
  const { disposable } = await response.json()

  return disposable ? 'Disposable email addresses not allowed' : true
}

export default defineType({
  fields: [
    {
      name: 'email',
      type: 'string',
      validation: (Rule) => Rule.required().custom(validateEmailDomain),
    },
  ],
})
```

**GROQ Query Validation:**

```typescript
const validateCategoryExists = async (categoryRef, context) => {
  if (!categoryRef?._ref) return true

  const { getClient } = context
  const client = getClient({ apiVersion: '2023-05-09' })

  const category = await client.fetch('*[_id == $id][0]', {
    id: categoryRef._ref,
  })

  return category ? true : 'Referenced category no longer exists'
}

export default defineType({
  fields: [
    {
      name: 'category',
      type: 'reference',
      to: [{ type: 'category' }],
      validation: (Rule) => Rule.custom(validateCategoryExists),
    },
  ],
})
```

Validates that referenced document still exists (catches broken references from deletions).

## Conditional Required Fields

Custom validators enable conditional required fields based on other field values.

**Pattern:**

```typescript
export default defineType({
  name: 'event',
  fields: [
    {
      name: 'isVirtual',
      type: 'boolean',
      initialValue: false,
    },
    {
      name: 'location',
      type: 'string',
      validation: (Rule) =>
        Rule.custom((value, context) => {
          const { document } = context
          if (!document.isVirtual && !value) {
            return 'Location required for in-person events'
          }
          return true
        }),
    },
    {
      name: 'meetingUrl',
      type: 'url',
      validation: (Rule) =>
        Rule.custom((value, context) => {
          const { document } = context
          if (document.isVirtual && !value) {
            return 'Meeting URL required for virtual events'
          }
          return true
        }),
    },
  ],
})
```

Validation logic: in-person events require `location`, virtual events require `meetingUrl`. Conditional validation prevents editor confusion.

## Cross-Field Validation

Validate field values against other fields in the document.

**Date Range Validation:**

```typescript
export default defineType({
  name: 'event',
  fields: [
    { name: 'startDate', type: 'datetime', validation: (Rule) => Rule.required() },
    {
      name: 'endDate',
      type: 'datetime',
      validation: (Rule) =>
        Rule.required().custom((value, context) => {
          const end = new Date(value)
          const start = new Date(context.document.startDate)
          return end <= start ? 'End date must be after start date' : true
        }),
    },
  ],
})
```

**Mutually Exclusive Fields:**

```typescript
export default defineType({
  fields: [
    {
      name: 'externalUrl',
      type: 'url',
      validation: (Rule) =>
        Rule.custom((value, context) => {
          const { document } = context
          if (value && document.internalPage) {
            return 'Cannot set both external URL and internal page'
          }
          return true
        }),
    },
    {
      name: 'internalPage',
      type: 'reference',
      to: [{ type: 'page' }],
      validation: (Rule) =>
        Rule.custom((value, context) => {
          const { document } = context
          if (value && document.externalUrl) {
            return 'Cannot set both internal page and external URL'
          }
          return true
        }),
    },
  ],
})
```

Ensures content editors set exactly one of two options, never both.

## Array Item Validation

Validate array items based on surrounding items or document context.

**Unique Array Items:**

```typescript
export default defineType({
  fields: [
    {
      name: 'sections',
      type: 'array',
      of: [
        {
          type: 'reference',
          to: [{ type: 'section' }],
        },
      ],
      validation: (Rule) =>
        Rule.custom((sections) => {
          if (!sections) return true

          const sectionIds = sections.map((s) => s._ref)
          const uniqueIds = new Set(sectionIds)

          if (sectionIds.length !== uniqueIds.size) {
            return 'Cannot use the same section multiple times'
          }

          return true
        }),
    },
  ],
})
```

Prevents duplicate references in array fields.

**Maximum Array Length:**

```typescript
validation: (Rule) =>
  Rule.custom((items) => {
    if (!items) return true
    if (items.length > 10) {
      return 'Maximum 10 featured posts allowed'
    }
    return true
  })
```

Built-in `Rule.max(10)` validates array length, but custom validation provides clearer error messages.

## Error Message Best Practices

Validation error messages should:

1. **Be specific** - "Slug 'about' already used by page 'About Us'" beats "Slug not unique"
2. **Suggest fixes** - "Use 'about-company' instead" provides actionable guidance
3. **Use plain language** - "Email required" beats "Field cannot be empty"
4. **Reference field labels** - Use field title, not field name

**Good Error Messages:**

```typescript
// ✅ GOOD: Specific, actionable
return 'Phone number must be in format: (555) 123-4567'

// ✅ GOOD: Provides context
return `Featured image dimensions must be at least 1200×630 (current: ${width}×${height})`

// ✅ GOOD: Suggests alternative
return 'Slug "blog" is reserved. Try "blog-posts" or "articles" instead'
```

**Bad Error Messages:**

```typescript
// ❌ BAD: Vague
return 'Invalid value'

// ❌ BAD: Technical jargon
return 'Validation predicate failed'

// ❌ BAD: No guidance
return 'Error'
```

## Performance Considerations

Async validators run on every field change. Expensive validation (external APIs, complex GROQ queries) causes Studio lag.

**Optimization Strategies:**

**1. Debounce validation:**

```typescript
import debounce from 'lodash/debounce'

const debouncedValidation = debounce(async (value, context) => {
  // Expensive validation logic
}, 500)

validation: (Rule) =>
  Rule.custom((value, context) => {
    return debouncedValidation(value, context)
  })
```

Wait 500ms after typing stops before running validation.

**2. Early return for unchanged values:**

```typescript
let previousValue = null

validation: (Rule) =>
  Rule.custom(async (value, context) => {
    if (value === previousValue) {
      return true // Skip validation if value unchanged
    }
    previousValue = value
    // Run expensive validation
  })
```

**3. Cache validation results:**

```typescript
const validationCache = new Map()

validation: (Rule) =>
  Rule.custom(async (value, context) => {
    if (validationCache.has(value)) {
      return validationCache.get(value)
    }

    const result = await expensiveValidation(value)
    validationCache.set(value, result)
    return result
  })
```

## When to Use Custom Validation

**Use custom validation for:**

- Uniqueness constraints (slugs, email addresses, SKUs)
- External API validation (disposable email check, address verification)
- Cross-field logic (date ranges, mutually exclusive fields)
- Business rules (pricing tiers, stock limits, category restrictions)

**Don't use custom validation for:**

- Simple required fields (use `Rule.required()`)
- Format validation (use `Rule.regex()`, `Rule.email()`, `Rule.url()`)
- Min/max length (use `Rule.min()`, `Rule.max()`)
- Allowed values (use `Rule.enum()`)

Helix only uses custom validation for slug uniqueness. Other projects (kariusdx, ripplecom) use built-in validation rules exclusively.

## Anti-Patterns

**Anti-Pattern 1: Synchronous API calls**

```typescript
// ❌ BAD
validation: (Rule) =>
  Rule.custom((value) => {
    const result = fetch(`https://api.example.com/validate?value=${value}`)
    return result.ok
  })

// ✅ GOOD: Async validation
validation: (Rule) =>
  Rule.custom(async (value) => {
    const response = await fetch(`https://api.example.com/validate?value=${value}`)
    const { valid } = await response.json()
    return valid || 'Validation failed'
  })
```

**Anti-Pattern 2: No error handling**

```typescript
// ❌ BAD
validation: (Rule) =>
  Rule.custom(async (value, context) => {
    const result = await context.getClient().fetch(query)
    return result ? true : 'Not found'
  })

// ✅ GOOD: Catches errors
validation: (Rule) =>
  Rule.custom(async (value, context) => {
    try {
      const result = await context.getClient().fetch(query)
      return result ? true : 'Not found'
    } catch (error) {
      return true // Allow save on errors
    }
  })
```

**Anti-Pattern 3: Mutating context**

```typescript
// ❌ BAD: Modifies context object
validation: (Rule) =>
  Rule.custom((value, context) => {
    context.document.validated = true
    return true
  })

// ✅ GOOD: Read-only context access
validation: (Rule) =>
  Rule.custom((value, context) => {
    const { document } = context
    return document.category ? true : 'Category required'
  })
```

## Related Patterns

- **schema-definitions/validation-rules.md** - Built-in validation rules
- **custom-document-actions.md** - Pre-publish validation
- **groq-queries/query-file-organization.md** - GROQ queries for validation

## References

- Helix: `lib/isUniqueAcrossAllDocuments.js` (unique slug validator)
- Sanity Docs: Custom Validation
- Sanity Docs: Validation Context
