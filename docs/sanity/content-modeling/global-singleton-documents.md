---
title: "Global Singleton Documents"
category: "content-modeling"
subcategory: "site-wide-content"
tags: ["sanity", "globals", "singleton", "navigation", "site-settings"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

# Global Singleton Documents

## Overview

Global singleton documents manage site-wide content that exists once across the entire website: navigation menus, footer links, SEO metadata, and homepage configuration. Sanity CMS supports singletons through dedicated schema patterns and desk structure customization.

**Adoption**: 33% of analyzed projects (ripplecom v4 only) implement dedicated global document architecture. Kariusdx v2 uses single `siteSettings` document (33%). Helix v3 has no global documents (33%).

## Global Document Pattern

Global documents differ from regular documents in three ways:

1. **Single Instance**: Only one document of this type should exist
2. **Managed Access**: Hidden from regular document lists in Studio
3. **Dedicated UI**: Custom desk structure provides direct access

**Implementation requires**:
- Schema definition (document type)
- Desk structure plugin configuration
- Optional singleton enforcement

## Schema Definition

## Homepage Selector Example

```typescript
// schemaTypes/globals/homepage.ts
import { HomeIcon } from '@sanity/icons'
import { defineType, defineField } from 'sanity'

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
      options: {
        filter: '_type == "page" && !(_originalId match "drafts.*")',
      },
      description: 'Choose a page to be the homepage (only published pages)',
    }),
  ],
  preview: {
    select: {
      pageTitle: 'selectedPage.title',
    },
    prepare({ pageTitle }) {
      return {
        title: 'Homepage Setting',
        subtitle: pageTitle ? `Current: ${pageTitle}` : 'No homepage selected',
      }
    },
  },
})
```

## Navigation Menu Example

```typescript
// schemaTypes/globals/navigation.ts
import { MenuIcon } from '@sanity/icons'
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'navigation',
  title: 'Navigation',
  type: 'document',
  icon: MenuIcon,
  fields: [
    defineField({
      name: 'title',
      title: 'Menu Title',
      type: 'string',
      initialValue: 'Main Navigation',
      readOnly: true,
    }),
    defineField({
      name: 'items',
      title: 'Navigation Items',
      type: 'array',
      of: [
        { type: 'navigationItem' },    // Simple link
        { type: 'navigationDropdown' }, // Mega menu
      ],
      validation: (Rule) => Rule.required().min(1),
    }),
  ],
})
```

## Common Global Document Types

## Observed Patterns (Ripplecom v4)

**6 global documents identified**:

1. **homepage** - Page reference for homepage routing
2. **navigation** - Main navigation menu structure
3. **footerNavigation** - Footer links and columns
4. **seoMetadata** - Global SEO defaults (site name, OG image)
5. **regions** - Geographic regions for content filtering
6. **rlusdBalance** - Dynamic data (balance information)

**Pattern**: Globals cover navigation, SEO, and site-wide configuration

## SEO Metadata Global Example

```typescript
// schemaTypes/globals/seoMetadata.ts
export default defineType({
  name: 'seoMetadata',
  title: 'Global SEO Settings',
  type: 'document',
  fields: [
    defineField({
      name: 'siteName',
      title: 'Site Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'siteUrl',
      title: 'Site URL',
      type: 'url',
      description: 'Used for canonical URLs and sitemaps',
      validation: (Rule) => Rule.required().uri({ scheme: ['https'] }),
    }),
    defineField({
      name: 'defaultOgImage',
      title: 'Default OpenGraph Image',
      type: 'image',
      description: 'Fallback image for social sharing',
    }),
    defineField({
      name: 'twitterHandle',
      title: 'Twitter Handle',
      type: 'string',
      validation: (Rule) => Rule.regex(/^@[A-Za-z0-9_]+$/),
    }),
  ],
})
```

## Footer Navigation Global Example

```typescript
// schemaTypes/globals/footerNavigation.ts
export default defineType({
  name: 'footerNavigation',
  title: 'Footer Navigation',
  type: 'document',
  fields: [
    defineField({
      name: 'sections',
      title: 'Footer Sections',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'heading', title: 'Section Heading', type: 'string' },
            {
              name: 'links',
              title: 'Links',
              type: 'array',
              of: [{ type: 'link' }],
            },
          ],
        },
      ],
    }),
    defineField({
      name: 'copyrightText',
      title: 'Copyright Text',
      type: 'text',
      rows: 2,
    }),
    defineField({
      name: 'socialLinks',
      title: 'Social Media Links',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'platform', title: 'Platform', type: 'string' },
            { name: 'url', title: 'URL', type: 'url' },
          ],
        },
      ],
    }),
  ],
})
```

## Desk Structure Configuration

## Registering Global Documents

Sanity Studio v3+ uses `structure` function in `sanity.config.ts` to customize desk panes. Global documents are registered in the structure builder with fixed `documentId` values to ensure singleton behavior.

**Key Configuration Requirements**:
- Fixed `documentId` ensures only one instance exists
- `filter` removes globals from regular document lists
- Custom `child` provides direct edit access
- Icon customization improves UX

## Structure Builder Configuration Example

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { deskTool, StructureBuilder } from 'sanity/desk'

export default defineConfig({
  plugins: [
    deskTool({
      structure: (S: StructureBuilder) =>
        S.list()
          .title('Content')
          .items([
            S.listItem()
              .title('Global Settings')
              .child(
                S.list()
                  .title('Global Settings')
                  .items([
                    S.listItem()
                      .title('Homepage')
                      .icon(HomeIcon)
                      .child(
                        S.document()
                          .schemaType('homepage')
                          .documentId('homepage')
                      ),
                    S.listItem()
                      .title('Navigation')
                      .icon(MenuIcon)
                      .child(
                        S.document()
                          .schemaType('navigation')
                          .documentId('navigation')
                      ),
                    // Repeat for footerNavigation, seoMetadata, etc.
                  ])
              ),
            S.divider(),
            ...S.documentTypeListItems().filter(
              (item) => !['homepage', 'navigation'].includes(item.getId() || '')
            ),
          ]),
    }),
  ],
})
```

## Singleton Enforcement

## Document Actions Customization

Prevent deletion and duplication of global documents:

```typescript
// schemaTypes/globals/navigation.ts (continued)
export default defineType({
  name: 'navigation',
  // ... fields
  // Sanity v3+ document actions
  __experimental_actions: [
    'create', // Allow initial creation
    'update',
    'publish',
    // Omit 'delete' and 'duplicate'
  ],
})
```

## GROQ Query Pattern

Always query globals by fixed `_id`:

```groq
// ❌ Incorrect: May return multiple or none
*[_type == "navigation"][0]

// ✅ Correct: Fixed document ID
*[_id == "navigation"][0] {
  title,
  items[] {
    _type,
    _type == "navigationItem" => {
      label,
      link
    }
  }
}
```

## Alternative Pattern: Single Settings Document

Kariusdx (v2) uses a single monolithic `siteSettings` document for all global configuration:

```javascript
// schemas/documents/siteSettings.js
export default {
  name: 'siteSettings',
  type: 'document',
  title: 'Site Settings',
  groups: [
    { name: 'general', title: 'General', default: true },
    { name: 'social', title: 'Social Media' },
    { name: 'footer', title: 'Footer' },
  ],
  fields: [
    {
      name: 'siteName',
      type: 'string',
      title: 'Site Name',
      group: 'general',
    },
    {
      name: 'footerText',
      type: 'text',
      title: 'Footer Text',
      group: 'footer',
    },
    {
      name: 'socialLinks',
      type: 'array',
      of: [{ type: 'link' }],
      group: 'social',
    },
    {
      name: 'announcementBar',
      type: 'object',
      fields: [
        { name: 'enabled', type: 'boolean' },
        { name: 'message', type: 'string' },
      ],
      group: 'general',
    },
  ],
}
```

**Benefits**:
- Simpler to configure (one document)
- Easier GROQ queries

**Tradeoffs**:
- Large, unwieldy editor interface
- All settings in one transaction
- Harder to version control specific sections

## Frontend Data Fetching

## Next.js App Router Example

```typescript
// lib/sanity/queries.ts
export const navigationQuery = groq`
  *[_id == "navigation"][0] {
    items[] {
      _type,
      _type == "navigationItem" => {
        label,
        "url": link.url,
        "target": link.newWindow ? "_blank" : "_self"
      },
      _type == "navigationDropdown" => {
        label,
        columns[] {
          heading,
          links[] {
            label,
            "url": link.url
          }
        }
      }
    }
  }
`

// app/layout.tsx
export default async function RootLayout({ children }) {
  const navigation = await client.fetch(navigationQuery)
  const footerNav = await client.fetch(footerNavigationQuery)
  const seo = await client.fetch(seoMetadataQuery)

  return (
    <html>
      <head>
        <title>{seo.siteName}</title>
        <meta property="og:site_name" content={seo.siteName} />
      </head>
      <body>
        <Header navigation={navigation} />
        {children}
        <Footer navigation={footerNav} copyright={seo.copyrightText} />
      </body>
    </html>
  )
}
```

## Caching Strategy

Global documents change infrequently, so aggressive caching is appropriate:

```typescript
// lib/sanity/client.ts
import { createClient } from '@sanity/client'

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: '2024-01-01',
  useCdn: true, // Enable CDN for globals
})

// Fetch with Next.js cache
export async function getGlobalData() {
  return await client.fetch(
    groq`{
      "navigation": *[_id == "navigation"][0],
      "footer": *[_id == "footerNavigation"][0],
      "seo": *[_id == "seoMetadata"][0]
    }`,
    {},
    {
      next: { revalidate: 3600 }, // Cache for 1 hour
    }
  )
}
```

## Pattern Selection Guidelines

## Use Multiple Global Documents When:

- Site has 5+ distinct global settings areas
- Different team members manage different globals
- Versioning requirements differ by section

**Source Confidence**: 33% (ripplecom v4 only)

## Use Single Settings Document When:

- Site has < 5 global settings
- Single person manages all site-wide content
- Simplicity is prioritized over organization

**Source Confidence**: 33% (kariusdx v2 only)

## Skip Global Documents When:

- All configuration is hard-coded in frontend
- Site is purely content-driven (blog, documentation)
- Team size is minimal (< 2 content editors)

**Source Confidence**: 33% (helix v3 has no globals)

## Common Pitfalls

## Forgetting Fixed Document IDs

**Problem**: Querying `*[_type == "navigation"][0]` may return nothing or wrong document.

**Solution**: Always use fixed `_id` in GROQ queries and desk structure.

## Allowing Deletion

**Problem**: Content editors accidentally delete global navigation, breaking site.

**Solution**: Customize document actions to omit `delete` action.

## Over-Globalization

**Problem**: Creating globals for content that should be page-specific (hero images, taglines).

**Solution**: Only globalize content that truly appears site-wide or in layouts.

## Related Patterns

- **Reusable Content Objects**: Objects vs global documents for shared content
- **Content Hierarchies**: Parent-child relationships vs flat globals
- **SEO Metadata Objects**: Page-level SEO vs global SEO defaults

## See Also

- [Reusable Content Objects](./reusable-content-objects.md)
- [Content Block Organization](./content-block-organization.md)
