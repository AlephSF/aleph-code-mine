---
title: "Content Hierarchies and Parent-Child Relationships"
category: "content-modeling"
subcategory: "content-structure"
tags: ["sanity", "hierarchical-content", "parent-child", "relationships", "tree-structure"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-12"
---

# Content Hierarchies and Parent-Child Relationships

## Overview

Hierarchical content structures model parent-child relationships between documents, enabling nested navigation, breadcrumbs, and URL path generation. Sanity supports hierarchies through self-referential references, though adoption is limited in favor of flat taxonomies.

**Adoption**: 33% of analyzed projects (helix v3 only) implement hierarchical page structures. Kariusdx v2 (33%) and Ripplecom v4 (33%) use flat document structures with taxonomies.

## Hierarchical Page Pattern

Helix (v3) implements self-referential parent-child relationships for nested page structures:

**Structure**:
- Pages reference optional parent page
- Slugs auto-generate from parent hierarchy
- Unlimited nesting depth
- Breadcrumb navigation support

### Schema Definition

```javascript
// schemas/documents/page.js
export default {
  name: 'page',
  type: 'document',
  title: 'Page',
  fields: [
    {
      name: 'title',
      type: 'string',
      title: 'Title',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'parent',
      type: 'reference',
      to: [
        {
          type: 'page',
        },
      ],
      options: {
        disableNew: true, // Prevent recursive creation
        filter: '_id != $documentId', // Prevent self-reference
      },
      description: 'Select parent page to create hierarchy',
    },
    {
      name: 'slug',
      type: 'slug',
      title: 'Slug/Path',
      description: 'Include entire path if child page (e.g., "parent-page/child-page")',
      options: {
        source: (doc, options) => ({ doc, options }),
        isUnique: isUniqueAcrossAllDocuments,
        slugify: asyncSlugifier, // Custom: prepends parent slug
      },
      validation: (Rule) => Rule.required(),
    },
    // ... other fields
  ],
}
```

### Async Slug Generation

Helix implements async slugification that fetches parent document and prepends parent slug:

```javascript
// lib/asyncSlugifier.js
async function asyncSlugifier(input, type, context) {
  const { getClient } = context
  const client = getClient({
    apiVersion: process.env.SANITY_STUDIO_API_VERSION || '2023-05-09',
  })

  const parentQuery = '*[_id == $id][0]'
  const parentQueryParams = {
    id: input.doc.parent?._ref || '',
  }

  const parent = await client.fetch(parentQuery, parentQueryParams)

  const parentSlug = parent?.slug?.current
    ? `${parent.slug.current}/`
    : ''

  const pageSlug = input.doc.title
    .toLowerCase()
    .replace(/\s+/g, '-')
    .slice(0, 200)

  return `${parentSlug}${pageSlug}`
}
```

**Result**:
- Parent: `about` → `/about`
- Child: `team` → `/about/team`
- Grandchild: `leadership` → `/about/team/leadership`

### Breadcrumb Support

GROQ query to fetch full ancestor path:

```groq
*[_type == "page" && slug.current == $slug][0] {
  title,
  slug,
  parent-> {
    title,
    slug,
    parent-> {
      title,
      slug,
      parent-> {
        title,
        slug
      }
    }
  }
}
```

**Frontend Breadcrumb Implementation**:
```typescript
function buildBreadcrumbs(page: Page): Breadcrumb[] {
  const breadcrumbs: Breadcrumb[] = []
  let current = page

  while (current) {
    breadcrumbs.unshift({
      title: current.title,
      url: `/${current.slug.current}`,
    })
    current = current.parent
  }

  return [{ title: 'Home', url: '/' }, ...breadcrumbs]
}
```

## Flat Taxonomy Pattern

Ripplecom (v4) and Kariusdx (v2) use flat document structures with taxonomy references:

**Structure**:
- No parent-child relationships
- Category and tag references
- Flat URL structure
- Filtering and grouping via taxonomies

### Category Taxonomy Example

```typescript
// schemaTypes/documents/blogPost.ts
export default defineType({
  name: "blogPost",
  type: "document",
  fields: [
    defineField({
      name: "title",
      type: "string",
    }),
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
      description: "Assign one or more categories",
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
      description: "Flexible labeling for organization",
    }),
  ],
})
```

### Taxonomy Document Example

```typescript
// schemaTypes/documents/category.ts
export default defineType({
  name: "category",
  type: "document",
  fields: [
    defineField({
      name: "title",
      type: "string",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "slug",
      type: "slug",
      options: {
        source: "title",
      },
    }),
    defineField({
      name: "description",
      type: "text",
      rows: 3,
    }),
  ],
})
```

### Querying Flat Taxonomies

```groq
// Get all posts in category
*[_type == "blogPost" && references(*[_type == "category" && slug.current == $categorySlug]._id)] {
  title,
  slug,
  categories[]-> {
    title,
    slug
  }
}

// Get all categories with post counts
*[_type == "category"] {
  title,
  slug,
  "postCount": count(*[_type == "blogPost" && references(^._id)])
} | order(postCount desc)
```

## Hybrid Pattern: Hierarchical Navigation

Some projects need hierarchical navigation without hierarchical content:

### Navigation-Only Hierarchy

```typescript
// schemaTypes/globals/navigation.ts
export default defineType({
  name: "navigation",
  type: "document",
  fields: [
    defineField({
      name: "items",
      type: "array",
      of: [
        {
          type: "object",
          name: "navItem",
          fields: [
            { name: "label", type: "string" },
            { name: "page", type: "reference", to: [{ type: "page" }] },
            {
              name: "children",
              type: "array",
              of: [
                {
                  type: "object",
                  fields: [
                    { name: "label", type: "string" },
                    { name: "page", type: "reference", to: [{ type: "page" }] },
                  ],
                },
              ],
            },
          ],
        },
      ],
    }),
  ],
})
```

**Benefits**:
- Flexible navigation structure independent of content hierarchy
- Pages can appear in multiple nav locations
- Content editors control navigation directly

## Pattern Comparison

### Hierarchical Pages vs Flat Taxonomies

| Aspect | Hierarchical Pages | Flat Taxonomies |
|--------|-------------------|-----------------|
| **URL Structure** | `/parent/child/grandchild` | `/blog/post-slug` |
| **Content Organization** | Tree structure | Tag-based |
| **Breadcrumbs** | Automatic from hierarchy | Manual or URL-based |
| **Multi-categorization** | No (single parent) | Yes (multiple categories/tags) |
| **Complexity** | Higher (async slugs, queries) | Lower (simple references) |
| **Use Case** | Documentation, corporate sites | Blogs, news, e-commerce |
| **Adoption** | 33% (helix only) | 67% (kariusdx + ripplecom) |

## Pattern Selection Guidelines

### Use Hierarchical Pages When:

- Site structure mirrors organizational hierarchy
- Breadcrumb navigation is important
- URLs should reflect content structure
- Content has single logical parent

**Source Confidence**: 33% (helix v3 only)

**Example Use Cases**:
- Documentation sites
- Corporate websites (About > Team > Leadership)
- Government sites with organizational structure

### Use Flat Taxonomies When:

- Content belongs to multiple categories
- Flexible filtering and sorting needed
- URL structure is independent of organization
- Blog or news content

**Source Confidence**: 67% (kariusdx v2 + ripplecom v4)

**Example Use Cases**:
- Blogs (posts have multiple categories/tags)
- E-commerce (products in multiple categories)
- News sites (articles cross multiple sections)

### Use Hybrid When:

- Navigation is hierarchical but content is flat
- Menu structure differs from content organization
- Marketing control over navigation required

**Source Confidence**: N/A (not observed in analyzed projects)

**Example Use Cases**:
- Marketing sites with flexible navigation
- Multi-brand sites
- Complex mega-menu requirements

## Frontend Implementation

### Hierarchical Page Routing

```typescript
// app/[...slug]/page.tsx (Next.js App Router)
export default async function Page({ params }: { params: { slug: string[] } }) {
  const slugPath = params.slug.join('/')

  const page = await client.fetch(
    groq`*[_type == "page" && slug.current == $slug][0] {
      title,
      content,
      parent-> {
        title,
        slug
      }
    }`,
    { slug: slugPath }
  )

  if (!page) notFound()

  const breadcrumbs = buildBreadcrumbs(page)

  return (
    <>
      <Breadcrumbs items={breadcrumbs} />
      <h1>{page.title}</h1>
      {/* Render page content */}
    </>
  )
}
```

### Flat Taxonomy Routing

```typescript
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await client.fetch(
    groq`*[_type == "blogPost" && slug.current == $slug][0] {
      title,
      content,
      categories[]-> {
        title,
        slug
      },
      tags[]-> {
        title,
        slug
      }
    }`,
    { slug: params.slug }
  )

  return (
    <>
      <h1>{post.title}</h1>
      <div>
        {post.categories.map(cat => (
          <Link key={cat.slug.current} href={`/category/${cat.slug.current}`}>
            {cat.title}
          </Link>
        ))}
      </div>
      {/* Render post content */}
    </>
  )
}
```

## Common Pitfalls

### Self-Referencing Pages

**Problem**: Page references itself as parent, creating infinite loop

**Solution**: Add filter to prevent self-reference:

```javascript
options: {
  filter: '_id != $documentId',
}
```

### Circular References

**Problem**: Page A → Page B → Page C → Page A (circular hierarchy)

**Solution**: Implement validation or limit depth:

```javascript
// Custom validation
validation: (Rule) => Rule.custom(async (value, context) => {
  if (!value || !value._ref) return true

  const client = context.getClient({ apiVersion: '2024-01-01' })
  let current = value._ref
  let depth = 0

  while (current && depth < 10) {
    const parent = await client.fetch('*[_id == $id][0].parent._ref', { id: current })
    if (parent === context.document._id) {
      return 'Circular reference detected'
    }
    current = parent
    depth++
  }

  if (depth >= 10) {
    return 'Hierarchy too deep (max 10 levels)'
  }

  return true
})
```

### Broken Slug Generation

**Problem**: Parent slug changes, child slugs don't update

**Solution**: Implement custom document action to cascade slug updates, or regenerate slugs on publish

### Over-Categorization

**Problem**: 50+ categories overwhelm content editors

**Solution**: Limit categories to 5-10, use tags for granular classification

## Migration Strategies

### From Flat to Hierarchical

**Phase 1**: Add optional `parent` reference field

**Phase 2**: Manually assign parent relationships

**Phase 3**: Regenerate slugs with parent paths

**Phase 4**: Update frontend routing to support nested paths

### From Hierarchical to Flat

**Phase 1**: Export hierarchical data with full paths

**Phase 2**: Create category documents from hierarchy levels

**Phase 3**: Assign categories to content

**Phase 4**: Remove parent references

**Phase 5**: Update slug generation (remove parent path logic)

## Related Patterns

- **Global Singleton Documents**: Navigation menus as global hierarchies
- **Content Block Organization**: Organizing schemas in hierarchical folders
- **Reusable Content Objects**: Link objects for internal navigation

## See Also

- [Global Singleton Documents](./global-singleton-documents.md)
- [Page Builder Architecture](./page-builder-architecture.md)
