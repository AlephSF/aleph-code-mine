---
title: "Desk Structure Customization"
category: "studio-customization"
subcategory: "navigation"
tags: ["sanity", "structure", "desk", "navigation", "organization"]
stack: "sanity"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

## Overview

Sanity Studio desk structure customization organizes content types into logical groups, hides system documents, and creates nested navigation hierarchies. Desk structure customization appears in 67% of analyzed Sanity projects (2 of 3 repos). Projects using custom desk structures provide better content editor UX through grouped singletons, ordered document lists, and visual separators.

## Modern Structure Resolver (v3+)

Sanity v3+ uses `StructureResolver` type with `structureTool()` plugin. Structure resolvers replace the legacy v2 "parts" system and provide TypeScript type safety.

**Basic Structure:**

```typescript
// structure/index.ts
import { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      ...S.documentTypeListItems(),
    ])
```

**Configuration:**

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { structure } from './structure'

export default defineConfig({
  plugins: [
    structureTool({ structure }),
    // ... other plugins
  ],
})
```

Ripplecom uses this pattern (v4.x). Helix does not provide custom structure, relying on default alphabetical listing.

## Filtering and Ordering Document Types

Custom structures control which document types appear in the desk and in what order. Two patterns emerge: **inclusion filtering** (kariusdx v2) and **exclusion filtering** (ripplecom v4).

**Exclusion Filter (Recommended):**

```typescript
export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      ...S.documentTypeListItems().filter(
        (item) =>
          ![
            'defaultSeo',
            'footerNavigation',
            'homepage',
            'navigation',
            'redirect',
            'regions',
          ].includes(item.getId() ?? ''),
      ),
      // ... grouped singletons below
    ])
```

Exclusion filters scale better than inclusion filters. Adding new document types requires no structure changes—they appear automatically unless explicitly excluded. Ripplecom excludes 12 singleton/system types, allowing ~10 regular document types to display without manual enumeration.

**Inclusion Filter (Legacy v2):**

```javascript
// deskStructure.js (v2 only)
export default () =>
  S.list()
    .title('Content')
    .items([
      ...S.documentTypeListItems().filter(listItem => ['page'].includes(listItem.getId())),
      ...S.documentTypeListItems().filter(listItem => ['news'].includes(listItem.getId())),
      ...S.documentTypeListItems().filter(listItem => ['pressRelease'].includes(listItem.getId())),
      // ... repeat for each type
    ])
```

Kariusdx uses inclusion filters (8 document types listed manually). This approach requires updating the structure file for every new document type. Avoid this pattern in v3+ projects.

## Singleton Grouping

Singleton documents (site settings, navigation, SEO defaults) should be grouped under a collapsible menu item to reduce desk clutter. 67% of projects with custom structures use singleton grouping.

**Pattern:**

```typescript
import { CogIcon, HomeIcon, MenuIcon, InfoOutlineIcon } from '@sanity/icons'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      ...S.documentTypeListItems().filter(/* exclude singletons */),
      S.divider(),
      S.listItem()
        .title('Global Options')
        .id('globalOptions')
        .icon(CogIcon)
        .child(
          S.list()
            .title('Global Options')
            .items([
              S.listItem()
                .title('Homepage Setting')
                .icon(HomeIcon)
                .child(
                  S.document()
                    .schemaType('homepage')
                    .documentId('homepage')
                    .title('Homepage Setting'),
                ),
              S.listItem()
                .title('Navigation Menus')
                .icon(MenuIcon)
                .child(
                  S.documentTypeList('navigation')
                    .title('Navigation Menus')
                    .filter('_type == "navigation"'),
                ),
              S.listItem()
                .title('Default SEO Settings')
                .icon(InfoOutlineIcon)
                .child(
                  S.document()
                    .schemaType('defaultSeo')
                    .documentId('defaultSeo')
                    .title('Default SEO Settings'),
                ),
            ]),
        ),
    ])
```

Ripplecom groups 6 singletons under "Global Options". Kariusdx groups 2 singletons under "Settings". Use `@sanity/icons` for official icon set (ripplecom) or `react-icons` for extended icon library (kariusdx).

## Legacy Content Grouping

Projects migrating from other CMSs or maintaining backward compatibility can group legacy content types under a dedicated section. Ripplecom demonstrates this pattern during Contentful migration.

**Pattern:**

```typescript
import { ComponentIcon, PlayIcon, CommentIcon } from '@sanity/icons'

S.listItem()
  .title('Legacy Content')
  .id('legacyContent')
  .icon(ComponentIcon)
  .child(
    S.list()
      .title('Legacy Content')
      .items([
        S.listItem()
          .title('Legacy Sections')
          .icon(ComponentIcon)
          .child(
            S.documentTypeList('section')
              .title('Legacy Sections')
              .filter('_type == "section"'),
          ),
        S.listItem()
          .title('Legacy Videos')
          .icon(PlayIcon)
          .child(
            S.documentTypeList('legacyVideo')
              .title('Legacy Videos')
              .filter('_type == "legacyVideo"'),
          ),
        S.listItem()
          .title('Legacy Quotes')
          .icon(CommentIcon)
          .child(
            S.documentTypeList('legacyQuote')
              .title('Legacy Quotes')
              .filter('_type == "legacyQuote"'),
          ),
      ]),
  ),
```

Ripplecom maintains 4 legacy content types (section, legacyVideo, legacyQuote, legacyCtaCard) while building modern replacements. Grouping prevents legacy content from cluttering the main desk interface.

## Visual Dividers

Dividers separate logical sections in the desk structure. Ripplecom uses dividers to separate regular documents from legacy content and global options.

**Pattern:**

```typescript
export const structure: StructureResolver = (S) =>
  S.list()
    .title('Base')
    .items([
      ...S.documentTypeListItems().filter(/* regular docs */),
      S.divider(),
      // Legacy content group
      S.divider(),
      // Global options group
    ])
```

Dividers improve visual scanning when the desk contains 15+ items split across multiple categories.

## Default Document Views

Kariusdx (v2) customizes document views to add Preview and SEO Analysis panes alongside the default Form view. This pattern uses `getDefaultDocumentNode` (v2 API, deprecated in v3+).

**Legacy v2 Pattern:**

```javascript
import Iframe from 'sanity-plugin-iframe-pane'
import { SeoToolsPane } from 'sanity-plugin-seo-tools'

export const getDefaultDocumentNode = ({documentId, schemaType}) => {
  if (schemaType === 'page') {
    return S.document().views([
      S.view.form(),
      S.view
        .component(Iframe)
        .options({
          url: (doc) => resolveProductionUrl(doc),
        })
        .title('Preview'),
      S.view
        .component(SeoToolsPane)
        .options({
          fetch: true,
          resolveProductionUrl: (doc) => resolveProductionUrl(doc),
          select: (doc) => ({
            focus_keyword: doc.seo?.focusKeyword ?? '',
            seo_title: (doc.seo?.seoTitle || doc.title) ?? '',
            meta_description: doc.seo?.seoDescription ?? '',
          })
        })
        .title('SEO Analysis')
    ])
  }
}
```

Kariusdx adds 2 additional views (Preview, SEO Analysis) to page and pressRelease documents. This pattern is replaced by `presentationTool()` in v3+ (see presentation-tool-configuration.md).

## When to Use Custom Desk Structure

**Use custom desk structure when:**

- Project has 5+ singleton documents (settings, navigation, SEO defaults)
- Maintaining legacy content types during migration
- Document types need specific ordering (not alphabetical)
- Multiple document type categories exist (content, settings, system)

**Skip custom desk structure when:**

- Project has <10 document types total
- All document types are regular content (no singletons)
- Default alphabetical ordering is acceptable
- Team prefers minimal configuration

Helix (v3) uses default desk structure with 3 document types (blogPost, page, tag). No customization needed for this scale.

## Migration from v2 Parts System

Kariusdx uses v2 "parts" system for desk structure. Migrating to v3+ requires converting `sanity.json` parts to `sanity.config.ts` plugins.

**v2 (sanity.json):**

```json
{
  "parts": [
    {
      "name": "part:@sanity/desk-tool/structure",
      "path": "./deskStructure.js"
    }
  ]
}
```

**v3+ (sanity.config.ts):**

```typescript
import { structure } from './structure'

export default defineConfig({
  plugins: [
    structureTool({ structure }),
  ],
})
```

Additionally, replace `@sanity/desk-tool/structure-builder` imports with `sanity/structure` imports and convert `S` builder calls to modern StructureResolver API.

## Anti-Patterns

**Anti-Pattern 1: Inclusion filters**

```typescript
// ❌ BAD: Breaks when adding new document types
...S.documentTypeListItems().filter(item => ['page', 'post', 'tag'].includes(item.getId()))
```

```typescript
// ✅ GOOD: New types appear automatically
...S.documentTypeListItems().filter(item => !['settings', 'navigation'].includes(item.getId()))
```

**Anti-Pattern 2: Deeply nested structures**

```typescript
// ❌ BAD: 4+ levels of nesting
S.listItem().child(S.list().items([
  S.listItem().child(S.list().items([
    S.listItem().child(S.list().items([
      // Too deep
    ]))
  ]))
]))
```

Limit nesting to 2 levels (main desk → grouped section). Ripplecom uses 2-level nesting for singletons and legacy content.

**Anti-Pattern 3: No icons**

```typescript
// ❌ BAD: Text-only navigation
S.listItem().title('Settings')

// ✅ GOOD: Visual icons improve scanning
S.listItem().title('Settings').icon(CogIcon)
```

Use icons from `@sanity/icons` for consistency with Sanity Studio design system.

## Related Patterns

- **singleton-document-management.md** - Template filtering for singletons
- **presentation-tool-configuration.md** - Modern alternative to custom preview panes
- **custom-document-actions.md** - Customizing publish/unpublish actions

## References

- Ripplecom: `apps/sanity-studio/structure/index.ts` (v4 exclusion filter pattern)
- Kariusdx: `deskStructure.js` (v2 inclusion filter + preview panes)
- Sanity Docs: Structure Builder API v3
