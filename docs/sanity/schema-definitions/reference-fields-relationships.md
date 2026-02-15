---
title: "Reference Fields for Content Relationships"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "references", "relationships", "content-modeling"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Reference Fields for Content Relationships

## Overview

Sanity reference fields create typed relationships between documents, enabling structured content modeling with categories, authors, related content, and hierarchical navigation. Reference fields have 100% consistent syntax across all projects, though adoption varies significantly (Ripplecom uses extensively, Helix minimally). Total usage: 32 reference fields across 147 schemas (22% adoption).

## Pattern Adoption

**Adoption Rate:** 22% (32 of 147 schemas use references)

- **Ripplecom (v4)**: 24 reference fields (31% of schemas)
- **Kariusdx (v2)**: 7 reference fields (11% of schemas)
- **Helix (v3)**: 1 reference field (20% of schemas)

**Observation:** Ripplecom uses references 3x more than other projects, primarily for taxonomies (categories, tags) and author attribution.


## Single Reference Field

Reference a single related document with type safety.

```javascript
// helix-dot-com-sanity/schemas/documents/page.js
export default {
  name: 'page',
  type: 'document',
  fields: [
    {
      name: 'parent',
      type: 'reference',
      to: [
        {
          type: 'page', // ← References another page document
        },
      ],
      options: {
        disableNew: true, // Prevent creating new parent pages inline
      },
    },
  ],
}
```

**Use Case:** Hierarchical page structures (parent-child relationships).

## Reference with Multiple Target Types

References can target multiple document types (polymorphic references).

```typescript
// Example: Link to any content type
defineField({
  name: "link",
  title: "Link To",
  type: "reference",
  to: [
    { type: "page" },
    { type: "blogPost" },
    { type: "event" },
  ],
  description: "Link to any page, blog post, or event",
})
```


## Categories and Tags (Most Common)

The most common reference pattern: arrays of taxonomy references.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
export default defineType({
  name: "blogPost",
  fields: [
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
    }),
    defineField({
      name: "tags",
      title: "Tags",
      type: "array",
      of: [
        {
          type: "reference",
          to: [{ type: "tag" }],
        },
      ],
      group: "meta",
      description: "Tags for flexible content labeling and organization",
    }),
  ],
})
```

## Validation for Array References

Limit the number of selected references to prevent over-categorization.

```typescript
defineField({
  name: "categories",
  title: "Categories",
  type: "array",
  of: [{ type: "reference", to: [{ type: "category" }] }],
  validation: (Rule) => Rule.required().min(1).max(3),
  description: "Select 1-3 categories",
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


## Single Author Attribution

Blog posts and content typically reference a single author.

```typescript
defineField({
  name: "author",
  title: "Author",
  type: "reference",
  to: [{ type: "person" }],
  validation: (Rule) => Rule.required(),
  group: "meta",
})
```

## Multiple Authors (Array)

Some content types support multiple authors.

```typescript
defineField({
  name: "authors",
  title: "Authors",
  type: "array",
  of: [{ type: "reference", to: [{ type: "person" }] }],
  validation: (Rule) => Rule.required().min(1),
  description: "Primary author should be first in the list",
})
```


## Related Posts/Articles

Arrays of references for "You might also like" sections.

```typescript
defineField({
  name: "relatedPosts",
  title: "Related Posts",
  type: "array",
  of: [{ type: "reference", to: [{ type: "blogPost" }] }],
  validation: (Rule) => Rule.max(5),
  description: "Manually curated related content",
})
```

## Excluding Self-References

Prevent documents from referencing themselves.

```typescript
defineField({
  name: "relatedPosts",
  type: "array",
  of: [{ type: "reference", to: [{ type: "blogPost" }] }],
  validation: (Rule) =>
    Rule.custom((references, context) => {
      const currentId = context.document?._id?.replace(/^drafts\./, '')

      if (!references) return true

      const selfReference = references.find(
        (ref) => ref._ref?.replace(/^drafts\./, '') === currentId
      )

      if (selfReference) {
        return "A post cannot be related to itself"
      }

      return true
    }),
})
```


## Disable Inline Creation (disableNew)

Prevent creating referenced documents inline to maintain content organization.

```javascript
{
  name: 'parent',
  type: 'reference',
  to: [{ type: 'page' }],
  options: {
    disableNew: true, // ← Cannot create new pages from this field
  },
}
```

**Use Case:** Hierarchical references where the parent must be created first.

## Filter Available References

Limit which documents can be selected based on criteria.

```typescript
defineField({
  name: "parentPage",
  type: "reference",
  to: [{ type: "page" }],
  options: {
    filter: ({ document }) => {
      // Prevent circular references
      return {
        filter: "_id != $id",
        params: { id: document._id },
      }
    },
  },
})
```

## Custom Reference Filters

Filter references based on field values.

```typescript
defineField({
  name: "category",
  type: "reference",
  to: [{ type: "category" }],
  options: {
    filter: "active == true && language == $lang",
    filterParams: { lang: "en" },
  },
  description: "Only active English categories are shown",
})
```


## Standard vs Weak References

Standard references prevent deletion of referenced documents. Weak references allow deletion.

```typescript
// Standard reference (default - prevents deletion)
defineField({
  name: "author",
  type: "reference",
  to: [{ type: "person" }],
  weak: false, // Default - cannot delete person if referenced
})

// Weak reference (allows deletion)
defineField({
  name: "suggestedAuthor",
  type: "reference",
  to: [{ type: "person" }],
  weak: true, // ← Person can be deleted even if referenced here
})
```

**Use Case:** Weak references for suggestions, drafts, or non-critical relationships.


## Parent-Child Page Relationships

Helix uses self-referencing for hierarchical page structures.

```javascript
// helix-dot-com-sanity/schemas/documents/page.js
async function asyncSlugifier(input, type, context) {
  const { getClient } = context
  const client = getClient({ apiVersion: '2023-05-09' })

  const parentQuery = '*[_id == $id][0]'
  const parentQueryParams = {
    id: input.doc.parent?._ref || '',
  }

  const parent = await client.fetch(parentQuery, parentQueryParams)
  const parentSlug = parent?.slug?.current ? `${parent.slug.current}/` : ''
  const pageSlug = input.doc.title
    .toLowerCase()
    .replace(/\s+/g, '-')
    .slice(0, 200)

  return `${parentSlug}${pageSlug}` // Prepends parent slug
}

export default {
  name: 'page',
  fields: [
    {
      name: 'parent',
      type: 'reference',
      to: [{ type: 'page' }], // ← Self-reference for hierarchy
      options: {
        disableNew: true,
      },
    },
    {
      name: 'slug',
      type: 'slug',
      options: {
        slugify: asyncSlugifier, // Uses parent reference
      },
    },
  ],
}
```

**Result:** Pages like `/about-us/team` where "Team" page references "About Us" as parent.


## Displaying Referenced Data in Previews

Fetch referenced document data for preview displays.

```typescript
export default defineType({
  name: "blogPost",
  preview: {
    select: {
      title: "title",
      media: "featuredImage",
      authorName: "author.name", // ← Fetches author's name
      authorImage: "author.image", // ← Fetches author's image
    },
    prepare({ title, media, authorName, authorImage }) {
      return {
        title: title || "Untitled",
        subtitle: authorName ? `By ${authorName}` : "No author",
        media: media || authorImage,
      }
    },
  },
})
```


## Fetching Referenced Documents

GROQ queries dereference relationships using `->` operator.

```javascript
// Fetch blog post with author details
const query = `*[_type == "blogPost"] {
  title,
  slug,
  author-> {
    name,
    bio,
    image
  },
  categories[]-> {
    title,
    slug
  }
}`
```

## Filtering by Referenced Fields

Query documents based on referenced document properties.

```javascript
// Find posts by specific author
const query = `*[_type == "blogPost" && author->name == "John Doe"]`

// Find posts in specific category
const query = `*[_type == "blogPost" && "Technology" in categories[]->title]`
```


## Taxonomy Systems

Categories, tags, and classification systems.

```typescript
// Category taxonomy
fields: [
  defineField({
    name: "categories",
    type: "array",
    of: [{ type: "reference", to: [{ type: "category" }] }],
    validation: (Rule) => Rule.min(1).max(3),
  }),
  defineField({
    name: "tags",
    type: "array",
    of: [{ type: "reference", to: [{ type: "tag" }] }],
  }),
]
```

## Attribution

Author, contributor, and creator references.

```typescript
fields: [
  defineField({
    name: "author",
    type: "reference",
    to: [{ type: "person" }],
    validation: (Rule) => Rule.required(),
  }),
  defineField({
    name: "contributors",
    type: "array",
    of: [{ type: "reference", to: [{ type: "person" }] }],
  }),
]
```

## Content Relationships

Related content, recommendations, cross-references.

```typescript
fields: [
  defineField({
    name: "relatedArticles",
    type: "array",
    of: [{ type: "reference", to: [{ type: "article" }] }],
    validation: (Rule) => Rule.max(5),
  }),
]
```

## Hierarchical Navigation

Parent-child, breadcrumb, and tree structures.

```typescript
fields: [
  defineField({
    name: "parent",
    type: "reference",
    to: [{ type: "page" }],
    options: { disableNew: true },
  }),
]
```


## Over-Referencing Simple Data

Don't use references for simple enum-like data.

**❌ Bad: Reference for simple status**
```typescript
// Don't create a "status" document type
defineField({
  name: "status",
  type: "reference",
  to: [{ type: "status" }], // Overkill for "draft", "published", "archived"
})
```

**✅ Good: String with predefined options**
```typescript
defineField({
  name: "status",
  type: "string",
  options: {
    list: [
      { title: "Draft", value: "draft" },
      { title: "Published", value: "published" },
      { title: "Archived", value: "archived" },
    ],
  },
})
```

## Circular References Without Protection

Allow circular references only with explicit filtering.

**❌ Bad: Allows infinite loops**
```typescript
defineField({
  name: "relatedPages",
  type: "array",
  of: [{ type: "reference", to: [{ type: "page" }] }],
  // No filter - Page A → Page B → Page A (circular)
})
```

**✅ Good: Prevents self-reference**
```typescript
defineField({
  name: "relatedPages",
  type: "array",
  of: [{ type: "reference", to: [{ type: "page" }] }],
  validation: (Rule) =>
    Rule.custom((refs, context) => {
      const currentId = context.document?._id?.replace(/^drafts\./, '')
      const hasSelf = refs?.some((ref) => ref._ref?.replace(/^drafts\./, '') === currentId)
      return hasSelf ? "Cannot reference itself" : true
    }),
})
```

## Missing Validation on Required References

Always validate required reference fields.

**❌ Bad: No validation**
```typescript
defineField({
  name: "author",
  type: "reference",
  to: [{ type: "person" }],
  // Missing required validation
})
```

**✅ Good: Required validation**
```typescript
defineField({
  name: "author",
  type: "reference",
  to: [{ type: "person" }],
  validation: (Rule) => Rule.required(),
})
```

## Implementation Checklist

- [ ] Identify relationships in your content model (authors, categories, related content)
- [ ] Use single references for one-to-one relationships (author, parent page)
- [ ] Use array references for one-to-many relationships (categories, tags)
- [ ] Add validation: `required()` for mandatory refs, `max()` for array refs
- [ ] Set `disableNew: true` for references that shouldn't be created inline
- [ ] Prevent circular references with validation or filters
- [ ] Configure previews to display referenced document data
- [ ] Test GROQ queries to ensure references are dereferenced correctly

## Related Patterns

- **Validation Rules**: Use `required()`, `min()`, `max()` for reference arrays
- **Preview Configuration**: Display referenced data in document previews
- **Field Groups**: Group related references (e.g., all taxonomy refs in "Meta" tab)
- **Conditional Fields**: Show/hide reference fields based on document type

## References

- Ripplecom (v4): 24 reference fields (categories, tags, authors, relations)
- Kariusdx (v2): 7 reference fields
- Helix (v3): 1 reference field (hierarchical page parent)
- Sanity References Guide: https://www.sanity.io/docs/reference-type
- GROQ Dereferencing: https://www.sanity.io/docs/how-queries-work#references-and-joins
