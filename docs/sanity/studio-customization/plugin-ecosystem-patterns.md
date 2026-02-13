---
title: "Plugin Ecosystem Patterns"
category: "studio-customization"
subcategory: "plugins"
tags: ["sanity", "plugins", "media", "color", "table", "vision", "seo"]
stack: "sanity"
priority: "medium"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Sanity Studio plugin ecosystem extends functionality with official and community plugins. Common plugins include visionTool (GROQ testing), structureTool (desk customization), media (asset management), colorInput (color pickers), and table (markdown tables). 100% of analyzed projects use at least 2 plugins.

## Vision Tool (100% Adoption)

Vision Tool provides in-Studio GROQ query testing interface. Essential development tool for testing queries before moving to frontend.

**Configuration (v3+):**

```typescript
import { defineConfig } from 'sanity'
import { visionTool } from '@sanity/vision'

export default defineConfig({
  plugins: [
    visionTool(),
  ],
})
```

**Configuration (v2):**

```json
{
  "plugins": [
    "@sanity/vision"
  ],
  "env": {
    "development": {
      "plugins": ["@sanity/vision"]
    }
  }
}
```

Kariusdx restricts Vision Tool to development environment. Production Studio deployments should not expose Vision Tool to non-technical users. Helix and ripplecom include Vision Tool in all environments for flexibility.

**Common Usage:**

Content editors use Vision Tool to troubleshoot missing data ("Why doesn't my page show up?"), test filters ("Show all published posts from last month"), and understand reference relationships ("Which pages link to this document?").

## Structure Tool (67% Adoption)

Structure Tool (v3+) replaces legacy desk-tool (v2) and enables custom desk structure. Required for singleton grouping, content organization, and legacy content sections.

**v3+ Configuration:**

```typescript
import { structureTool } from 'sanity/structure'
import { structure } from './structure'

export default defineConfig({
  plugins: [
    structureTool({ structure }),
  ],
})
```

**v2 Configuration:**

```json
{
  "plugins": [
    "@sanity/desk-tool"
  ]
}
```

Ripplecom and kariusdx use Structure Tool with custom desk organization. Helix uses Structure Tool but provides no custom structure (default behavior). See desk-structure-customization.md for full patterns.

## Media Plugin (67% Adoption)

Media plugin replaces default Sanity asset library with enhanced asset management: grid view, bulk uploads, folder organization, image tagging, and advanced search.

**Installation:**

```bash
npm install sanity-plugin-media
```

**Configuration:**

```typescript
import { media } from 'sanity-plugin-media'

export default defineConfig({
  plugins: [
    media(),
  ],
})
```

Ripplecom and kariusdx use media plugin for improved asset management UX. Helix uses default Sanity asset library (simple list view). Media plugin particularly valuable for projects with 100+ images/videos.

**Key Features:**

- **Grid view** - Visual thumbnail grid instead of list
- **Bulk uploads** - Drag-drop multiple files
- **Folder organization** - Create folders for categorization
- **Image tagging** - Add tags to assets for search
- **Advanced filters** - Filter by file type, date, tags, orientation

## Color Input Plugin (33% Adoption)

Color Input plugin adds visual color picker for color fields. Stores hex values with opacity support.

**Installation:**

```bash
npm install @sanity/color-input
```

**Configuration:**

```typescript
import { colorInput } from '@sanity/color-input'

export default defineConfig({
  plugins: [
    colorInput(),
  ],
})
```

**Schema Usage:**

```typescript
export default defineType({
  name: 'heroSection',
  fields: [
    {
      name: 'backgroundColor',
      title: 'Background Color',
      type: 'color',
      options: {
        disableAlpha: false,
      },
    },
  ],
})
```

Ripplecom uses color input for theme customization fields (background colors, accent colors, gradient stops). Helix and kariusdx use string fields with manual hex entry.

**Stored Value:**

```json
{
  "backgroundColor": {
    "_type": "color",
    "hex": "#3b82f6",
    "alpha": 1,
    "hsl": {
      "h": 217,
      "s": 0.91,
      "l": 0.60,
      "a": 1
    },
    "hsv": {
      "h": 217,
      "s": 0.77,
      "v": 0.96,
      "a": 1
    },
    "rgb": {
      "r": 59,
      "g": 130,
      "b": 246,
      "a": 1
    }
  }
}
```

Plugin stores multiple color formats (hex, RGB, HSL, HSV). Frontend queries `backgroundColor.hex` for CSS usage.

## Table Plugin (33% Adoption)

Table plugin adds markdown table editor for structured tabular data in rich text.

**Installation:**

```bash
npm install @sanity/table
```

**Configuration:**

```typescript
import { table } from '@sanity/table'

export default defineConfig({
  plugins: [
    table(),
  ],
})
```

**Schema Usage:**

```typescript
export default defineType({
  name: 'blogPost',
  fields: [
    {
      name: 'content',
      type: 'array',
      of: [
        { type: 'block' },
        {
          type: 'table',
          options: {
            allowHeaderRow: true,
            allowHeaderColumn: false,
          },
        },
      ],
    },
  ],
})
```

Ripplecom uses table plugin for comparison tables, pricing tables, and data tables in blog posts. Helix and kariusdx have no table support—users must paste HTML tables.

**Frontend Rendering:**

```tsx
// components/PortableText.tsx
import { PortableText } from '@portabletext/react'
import Table from './Table'

const components = {
  types: {
    table: ({ value }) => <Table rows={value.rows} />,
  },
}

export default function Content({ content }) {
  return <PortableText value={content} components={components} />
}
```

Table values are arrays of row objects. Custom React component renders HTML `<table>` element.

## SEO Tools Plugin (33% Adoption)

SEO Tools plugin (v2 only) provides Yoast-style SEO analysis with keyword density, readability scoring, and meta tag preview.

**Installation (v2):**

```bash
npm install sanity-plugin-seo-tools
```

**Configuration (v2):**

```json
{
  "plugins": [
    "seo-tools"
  ]
}
```

**Custom Document View:**

```javascript
import { SeoToolsPane } from 'sanity-plugin-seo-tools'

export const getDefaultDocumentNode = ({ schemaType }) => {
  if (schemaType === 'page') {
    return S.document().views([
      S.view.form(),
      S.view
        .component(SeoToolsPane)
        .options({
          fetch: true,
          resolveProductionUrl: (doc) => resolveProductionUrl(doc),
          select: (doc) => ({
            focus_keyword: doc.seo?.focusKeyword ?? '',
            seo_title: (doc.seo?.seoTitle || doc.title) ?? '',
            meta_description: doc.seo?.seoDescription ?? '',
            focus_synonyms: doc.seo?.focusSynonyms?.split(',') ?? [],
          }),
        })
        .title('SEO Analysis'),
    ])
  }
}
```

Kariusdx adds SEO Analysis tab to page, video, and pressRelease documents. Plugin fetches published URL, analyzes content, and provides real-time SEO recommendations.

**Note:** SEO Tools plugin is v2-only and not compatible with v3+. V3+ projects should use alternative SEO validation approaches.

## Presentation Tool (33% Adoption)

Presentation Tool (v4+) enables visual editing with real-time preview. Official replacement for production-preview plugin (v2).

**Installation:**

Presentation Tool ships with Sanity v4—no separate installation needed.

**Configuration:**

```typescript
import { presentationTool } from 'sanity/presentation'

export default defineConfig({
  plugins: [
    presentationTool({
      previewUrl: {
        origin: getPreviewUrl(),
        previewMode: {
          enable: '/api/draft-mode/presentation-tool',
        },
      },
      allowOrigins: getAllowOrigins(),
    }),
  ],
})
```

Ripplecom uses Presentation Tool for visual editing with Vercel preview branches. See presentation-tool-configuration.md for full configuration patterns.

## Plugin Selection Strategy

**Official Sanity Plugins (@sanity/*):**
- Maintained by Sanity team
- Version compatibility guaranteed
- Best documentation and support
- Examples: @sanity/vision, @sanity/color-input, @sanity/table

**Community Plugins (sanity-plugin-*):**
- Maintained by community
- May lag behind Sanity version updates
- Check GitHub activity before adoption
- Examples: sanity-plugin-media, sanity-plugin-seo-tools, sanity-plugin-iframe-pane

**Version Compatibility Matrix:**

| Plugin | v2 | v3 | v4 |
|--------|----|----|-----|
| @sanity/vision | ✅ | ✅ | ✅ |
| @sanity/desk-tool | ✅ | ❌ | ❌ |
| structureTool | ❌ | ✅ | ✅ |
| @sanity/color-input | ✅ | ✅ | ✅ |
| @sanity/table | ✅ | ✅ | ✅ |
| sanity-plugin-media | ✅ | ✅ | ✅ |
| sanity-plugin-seo-tools | ✅ | ❌ | ❌ |
| @sanity/production-preview | ✅ | ❌ | ❌ |
| presentationTool | ❌ | ❌ | ✅ |

Check plugin README for version compatibility before installation.

## When to Add Plugins

**Add plugins for:**

- Functionality not available in core Sanity (color pickers, tables, media organization)
- Development tools that improve team efficiency (Vision Tool)
- Visual editing for non-technical content editors (Presentation Tool)
- Enhanced UX for common tasks (media plugin for 100+ assets)

**Skip plugins for:**

- Features achievable with custom input components
- Unmaintained plugins (no commits in 2+ years)
- Plugins with poor documentation
- Plugins incompatible with your Sanity version

Helix uses minimal plugins (2 total: structureTool, visionTool). Ripplecom uses 6 plugins. More plugins ≠ better—only add plugins that solve real team needs.

## Plugin Configuration Best Practices

**1. Environment-specific plugins:**

```typescript
export default defineConfig({
  plugins: [
    structureTool(),
    ...(process.env.NODE_ENV === 'development' ? [visionTool()] : []),
  ],
})
```

Hide development tools (Vision Tool) from production Studio.

**2. Conditional plugin loading:**

```typescript
const plugins = [
  structureTool({ structure }),
  visionTool(),
]

if (process.env.SANITY_STUDIO_ENABLE_PRESENTATION === 'true') {
  plugins.push(presentationTool({ /* config */ }))
}

export default defineConfig({
  plugins,
})
```

Feature-flag expensive plugins for gradual rollout.

**3. Plugin option validation:**

```typescript
import { media } from 'sanity-plugin-media'

export default defineConfig({
  plugins: [
    media({
      // Validate file types before upload
      accept: 'image/*, video/mp4',
      // Limit file size to 10MB
      maximumUploadSize: 10485760,
    }),
  ],
})
```

Configure plugin constraints to prevent misuse.

## Anti-Patterns

**Anti-Pattern 1: Plugin for simple features**

```typescript
// ❌ BAD: Plugin for basic color picker
plugins: [colorInput()]

// Schema uses plugin
{
  name: 'color',
  type: 'color', // Requires plugin
}

// ✅ GOOD: String field with validation
{
  name: 'color',
  type: 'string',
  validation: (Rule) => Rule.regex(/^#[0-9A-F]{6}$/i, 'Must be hex color'),
}
```

Only add plugins when built-in field types cannot solve the need.

**Anti-Pattern 2: Outdated plugins**

```bash
# ❌ BAD: v2 plugin in v3 project
npm install sanity-plugin-seo-tools
# Breaks: Plugin uses deprecated APIs
```

Check plugin version compatibility before installation.

**Anti-Pattern 3: No plugin configuration**

```typescript
// ❌ BAD: Default options may not fit project needs
plugins: [media()]

// ✅ GOOD: Configure upload constraints
plugins: [
  media({
    maximumUploadSize: 10485760,
    accept: 'image/*',
  }),
]
```

## Related Patterns

- **desk-structure-customization.md** - structureTool configuration
- **presentation-tool-configuration.md** - presentationTool setup
- **custom-branding-theming.md** - Visual customization

## References

- Ripplecom: `apps/sanity-studio/sanity.config.ts` (6 plugins)
- Kariusdx: `sanity.json` (7 plugins, v2 configuration)
- Helix: `sanity.config.ts` (2 plugins, minimal setup)
- Sanity Plugins Directory: https://www.sanity.io/plugins
