# Studio Customization - Cross-Project Comparison

**Date:** February 12, 2026
**Phase:** Phase 3, Domain 4
**Projects Analyzed:** helix-dot-com-sanity (v3), kariusdx-sanity (v2), ripplecom-nextjs (v4)
**Total Files Reviewed:** 6 config files, 3 structure files, 2 custom actions, 2 branding files

---

## Executive Summary

### Key Findings

1. **Configuration API Evolution (v2 → v3 → v4)**
   - v2 (kariusdx): JSON-based sanity.json + "parts" system
   - v3 (helix): defineConfig() with deskTool()
   - v4 (ripplecom): defineConfig() with structureTool()

2. **Desk Structure Adoption**
   - **100%** - All projects customize desk structure
   - v2: Export function, legacy S builder
   - v3/v4: Modern structure resolver, StructureResolver type

3. **Plugin Ecosystem**
   - visionTool: 100% adoption (dev environment)
   - presentationTool: 33% (ripplecom only - v4 feature)
   - media plugin: 67% (kariusdx + ripplecom)
   - Third-party plugins: 67% (colorInput, table, seo-tools)

4. **Custom Document Actions**
   - 33% adoption (kariusdx only)
   - Auto-slug generation on publish
   - Hierarchical path management

5. **Branding Customization**
   - 33% adoption (kariusdx only)
   - Custom logo, CSS variable overrides, tutorial overlay

---

## 1. Configuration Files

### Helix (v3.10.0) - Modern API, Minimal Customization

**File:** `sanity.config.ts`

```typescript
export default defineConfig({
  name: 'default',
  title: 'helix-dot-com-sanity',
  projectId: sanityProjectId || 'g5irbagy',
  dataset: sanityDataset || 'staging',
  plugins: [deskTool(), visionTool()],
  schema: {
    types: schemaTypes,
  },
})
```

**Plugins:** 2 (deskTool, visionTool)
**Custom branding:** None
**Custom actions:** None
**Desk structure:** Not specified (uses default)

---

### Kariusdx (v2.x) - Legacy Parts System, Extensive Customization

**File:** `sanity.json`

```json
{
  "root": true,
  "api": {
    "projectId": "nj4jfuv6",
    "dataset": "production"
  },
  "project": {
    "name": "Karius"
  },
  "plugins": [
    "@sanity/base",
    "@sanity/default-layout",
    "@sanity/default-login",
    "@sanity/desk-tool",
    "seo-tools",
    "media",
    "@sanity/production-preview"
  ],
  "parts": [
    {
      "name": "part:@sanity/base/schema",
      "path": "./schemas/schema"
    },
    {
      "implements": "part:@sanity/base/root",
      "path": "plugins/sanity-plugin-tutorial/CustomDefaultLayout"
    },
    {
      "name": "part:@sanity/desk-tool/structure",
      "path": "./deskStructure.js"
    },
    {
      "implements": "part:@sanity/base/brand-logo",
      "path": "./components/logo.js"
    },
    {
      "implements": "part:@sanity/base/theme/variables/override-style",
      "path": "variableOverrides.css"
    },
    {
      "implements": "part:@sanity/production-preview/resolve-production-url",
      "path": "./resolveProductionUrl.js"
    },
    {
      "implements": "part:@sanity/base/document-actions/resolver",
      "path": "./schemas/documentActions.js"
    }
  ]
}
```

**Plugins:** 7 (base, default-layout, desk-tool, seo-tools, media, production-preview, vision)
**Custom branding:** Custom logo SVG, CSS variable overrides, tutorial overlay
**Custom actions:** Auto-slug on publish, hierarchical path management
**Desk structure:** Custom structure with settings grouping
**Additional customizations:** Preview URL resolution, custom root layout

---

### Ripplecom (v4.x) - Modern API, Advanced Features

**File:** `sanity.config.ts`

```typescript
export default defineConfig({
  name: "default",
  title: "ripplecom-nextjs",
  projectId: sanityProjectId,
  dataset: sanityDataset,
  plugins: [
    structureTool({ structure }),
    colorInput(),
    media(),
    table(),
    visionTool(),
    presentationTool({
      previewUrl: {
        origin: getPreviewUrl(),
        previewMode: {
          enable: "/api/draft-mode/presentation-tool",
        },
      },
      allowOrigins: getAllowOrigins(),
      resolve: {
        mainDocuments: defineDocuments([...]),
        locations: {...},
      },
    }),
  ],
  schema: {
    types: schemaTypes,
    templates: (prev) =>
      prev.filter((template) => !singletonTypes.has(template.id)),
  },
  auth: createAuthStore({
    projectId: sanityProjectId,
    dataset: sanityDataset,
    redirectOnSingle: false,
    mode: "append",
    providers: [
      {
        name: "saml",
        title: "Ripple Okta",
        url: "https://api.sanity.io/v2021-10-01/auth/saml/login/44054204",
      },
    ],
    loginMethod: "dual",
  }),
})
```

**Plugins:** 6 (structureTool, colorInput, media, table, visionTool, presentationTool)
**Custom branding:** None (relies on default Studio branding)
**Custom actions:** None (uses default actions)
**Desk structure:** Custom structure with singleton grouping and legacy content section
**Additional customizations:**
- SAML SSO with Okta
- Presentation tool with environment-aware preview URLs
- Singleton template filtering
- Preview locations for 5 document types

---

## 2. Desk Structure Patterns

### Helix (v3) - No Custom Structure

**Observation:** Helix does not provide a custom desk structure, relying entirely on Sanity's default alphabetical document list.

**Impact:** Simplest configuration, but lacks content organization (no settings grouping, no ordering).

---

### Kariusdx (v2) - Legacy Structure Builder + Document Views

**File:** `deskStructure.js`

**Key Features:**
1. **Custom document views** with Preview + SEO Analysis panes
2. **Manual ordering** of document types (page, news, pressRelease, etc.)
3. **Settings grouping** with nested structure
4. **Icons** from react-icons (FiSettings, GiHamburgerMenu, GoSettings)
5. **Singleton documents** (siteSettings, navigation)

**Code:**
```javascript
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
          select: (doc) => ({...})
        })
        .title('SEO Analysis')
    ])
  }
}

export default () =>
  S.list()
    .title('Content')
    .items([
      ...S.documentTypeListItems().filter(listItem => ['page'].includes(listItem.getId())),
      ...S.documentTypeListItems().filter(listItem => ['news'].includes(listItem.getId())),
      // ... more manual filters
      S.listItem()
        .title('Settings')
        .icon(FiSettings)
        .child(
          S.list()
            .title('Settings')
            .items([
              S.listItem()
                .title('General Settings')
                .icon(GoSettings)
                .child(
                  S.document()
                    .title('General Settings')
                    .schemaType('siteSettings')
                    .documentId('siteSettings')
                ),
              // ...
            ])
        ),
    ])
```

**Document Type Count:** 8 document types + 2 singletons in Settings

---

### Ripplecom (v4) - Modern Structure Resolver + Legacy Content Grouping

**File:** `structure/index.ts`

**Key Features:**
1. **Exclusion filter** for system/singleton types (cleaner than manual inclusion)
2. **Legacy content grouping** with nested structure
3. **Global options grouping** for singletons
4. **Icons** from @sanity/icons (official icon set)
5. **Dividers** for visual separation
6. **Singleton documents** (homepage, defaultSeo, regions, rlusdBalance, footerNavigation)

**Code:**
```typescript
export const structure: StructureResolver = (S) =>
  S.list()
    .title("Base")
    .items([
      ...S.documentTypeListItems().filter(
        (item) =>
          ![
            "defaultSeo", "footerNavigation", "homepage",
            "legacyCtaCard", "legacyQuote", "legacyVideo",
            "navigation", "redirect", "regions",
            "rlusdBalance", "section", "settings",
          ].includes(item.getId() ?? ""),
      ),
      S.divider(),
      S.listItem()
        .title("Legacy Content")
        .id("legacyContent")
        .icon(ComponentIcon)
        .child(
          S.list()
            .title("Legacy Content")
            .items([
              S.listItem().title("Legacy Sections")...
              S.listItem().title("Legacy Videos")...
              S.listItem().title("Legacy Quotes")...
              S.listItem().title("Legacy CTA Cards")...
            ]),
        ),
      S.divider(),
      S.listItem()
        .title("Global Options")
        .id("globalOptions")
        .icon(CogIcon)
        .child(
          S.list()
            .title("Global Options")
            .items([
              S.listItem().title("Homepage Setting")...
              S.listItem().title("Navigation Menus")...
              S.listItem().title("Footer Navigation")...
              S.listItem().title("Default SEO Settings")...
              S.listItem().title("Global Regions")...
              S.listItem().title("RLUSD Balances")...
              S.listItem().title("URL Redirects")...
            ]),
        ),
    ])
```

**Document Type Count:** ~10 regular document types + 4 legacy types + 6 globals

---

## 3. Plugin Usage

### Vision Tool (Dev Environment Query Testing)

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ✅ Yes | Default plugin |
| Kariusdx | ✅ Yes | Dev environment only |
| Ripplecom | ✅ Yes | Default plugin |

**Adoption:** 100%

---

### Presentation Tool (v4 Feature - Visual Editing)

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ❌ No | Not available in v3 |
| Kariusdx | ❌ No | Uses @sanity/production-preview (legacy) |
| Ripplecom | ✅ Yes | Full integration with defineDocuments + defineLocations |

**Adoption:** 33%

**Ripplecom Configuration:**
- **4 main document types** with route mapping (caseStudy, leadGeneration, blogPost, pressRelease)
- **5 location resolvers** for custom preview URLs
- **Environment-aware preview URLs** (localhost:3000, Vercel preview branches, production)
- **CORS configuration** with allowOrigins

---

### Media Plugin (Sanity Asset Manager)

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ❌ No | Uses default media library |
| Kariusdx | ✅ Yes | Third-party media plugin |
| Ripplecom | ✅ Yes | Third-party media plugin |

**Adoption:** 67%

---

### Color Input Plugin

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ❌ No | - |
| Kariusdx | ❌ No | - |
| Ripplecom | ✅ Yes | @sanity/color-input |

**Adoption:** 33%

---

### Table Plugin

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ❌ No | - |
| Kariusdx | ❌ No | - |
| Ripplecom | ✅ Yes | @sanity/table |

**Adoption:** 33%

---

### SEO Tools Plugin

| Project | Adoption | Notes |
|---------|----------|-------|
| Helix | ❌ No | - |
| Kariusdx | ✅ Yes | sanity-plugin-seo-tools with Yoast-like analysis |
| Ripplecom | ❌ No | - |

**Adoption:** 33%

---

## 4. Custom Document Actions

### Helix

**Adoption:** None

---

### Kariusdx - Auto-Slug and Hierarchical Path Management

**File:** `schemas/documentActions.js`

**Purpose:** Replace default Publish action with custom action that:
1. Auto-generates slug from title if not set
2. Calculates full path from parent page hierarchy
3. Updates all child pages when parent path changes

**Code:**
```javascript
export default function useDocumentActions(props) {
  return defaultResolve(props).map((Action) =>
    Action === PublishAction ? SetSlugAndPublishAction : Action
  );
}
```

**Custom Action:** `SetSlugAndPublishAction`

**Key Features:**
- Async patch operations before publish
- Recursive child page path updates
- Validation status checking (can't publish invalid docs)
- "Publishing..." label during operation
- Hierarchical pagePath calculation

**Adoption:** 33% (kariusdx only)

---

### Ripplecom

**Adoption:** None (uses default actions)

---

## 5. Custom Branding

### Helix

**Adoption:** None (uses default Sanity branding)

---

### Kariusdx - Full Brand Customization

**Files:**
- `components/logo.js` - Custom SVG logo
- `variableOverrides.css` - CSS variable overrides
- `plugins/sanity-plugin-tutorial/CustomDefaultLayout.js` - Tutorial overlay

**CSS Variables:**
```css
:root {
    --brand-primary: #212944;
    --brand-secondary: #cc4e13;
    --brand-tertiary: #0d7479;
    --brand-gray: #9ea1a5;
    --brand-gray-light: #f5f5f5;
    --main-navigation-color: var(--brand-gray-light);
}

:global([data-ui='Navbar']) {
    border-bottom: 1px var(--brand-gray) solid;
}

/* Font size resets */
:global([data-testid='text-style--h1']),
:global([data-testid='text-style--h2']),
...
{
    font-size: 1rem !important;
}
```

**Custom Logo:** Full Karius logo SVG (781×174px) with brand colors

**Tutorial Overlay:** Role-based tutorial for new users

**Adoption:** 33% (kariusdx only)

---

### Ripplecom

**Adoption:** None (uses default Sanity branding)

---

## 6. Custom Validation Functions

### Helix - Unique Slug Validation

**File:** `lib/isUniqueAcrossAllDocuments.js`

**Purpose:** Async validation to ensure slugs are unique across all document types

**Code:**
```javascript
const isUniqueAcrossAllDocuments = async (slug, context) => {
  const { document, getClient } = context
  const client = getClient({ apiVersion: '2023-05-09' })
  const id = document._id.replace(/^drafts\./, '')
  const params = {
    draft: `drafts.${id}`,
    published: id,
    slug,
  }
  const query = '!defined(*[!(_id in [$draft, $published]) && slug.current == $slug][0]._id)'
  const result = await client.fetch(query, params)
  return result
}
```

**Adoption:** 33% (helix only)

---

### Kariusdx

**Adoption:** None (no custom validation utilities)

---

### Ripplecom

**Adoption:** None (no custom validation utilities)

---

## 7. Custom Orderings

### Ripplecom - Custom Sort Orders

**Count:** 13 schemas with custom orderings

**Examples:**
- `blogPost`: `orderings: [{ title: 'Publication Date (Newest First)', name: 'publishedAtDesc', by: [{ field: 'publishedAt', direction: 'desc' }] }]`
- `event`: Date ascending/descending
- `person`: Name alphabetical
- `video`: Date descending
- `category`: Name alphabetical
- `tag`: Name alphabetical

**Adoption:** 33% (ripplecom only)

---

### Helix & Kariusdx

**Adoption:** None (use default orderings)

---

## 8. Authentication Customization

### Helix

**Adoption:** None (default Sanity authentication)

---

### Kariusdx

**Adoption:** None (default Sanity authentication)

---

### Ripplecom - SAML SSO with Okta

**Configuration:**
```typescript
auth: createAuthStore({
  projectId: sanityProjectId,
  dataset: sanityDataset,
  redirectOnSingle: false,
  mode: "append",
  providers: [
    {
      name: "saml",
      title: "Ripple Okta",
      url: "https://api.sanity.io/v2021-10-01/auth/saml/login/44054204",
    },
  ],
  loginMethod: "dual",
})
```

**Features:**
- SAML authentication via Okta
- Dual login method (SAML + email/password fallback)
- Append mode (multiple auth providers)

**Adoption:** 33% (ripplecom only)

---

## Summary Statistics

| Feature | Helix (v3) | Kariusdx (v2) | Ripplecom (v4) | Adoption % |
|---------|------------|---------------|----------------|------------|
| Custom desk structure | ❌ No | ✅ Yes | ✅ Yes | 67% |
| visionTool | ✅ Yes | ✅ Yes | ✅ Yes | 100% |
| presentationTool | ❌ No (v3) | ❌ No (v2) | ✅ Yes | 33% |
| media plugin | ❌ No | ✅ Yes | ✅ Yes | 67% |
| colorInput plugin | ❌ No | ❌ No | ✅ Yes | 33% |
| table plugin | ❌ No | ❌ No | ✅ Yes | 33% |
| seo-tools plugin | ❌ No | ✅ Yes | ❌ No | 33% |
| Custom document actions | ❌ No | ✅ Yes | ❌ No | 33% |
| Custom branding | ❌ No | ✅ Yes | ❌ No | 33% |
| Custom validation utils | ✅ Yes | ❌ No | ❌ No | 33% |
| Custom orderings | ❌ No | ❌ No | ✅ Yes | 33% |
| SAML SSO | ❌ No | ❌ No | ✅ Yes | 33% |
| Preview panes | ❌ No | ✅ Yes | ❌ No | 33% |
| Singleton grouping | ❌ No | ✅ Yes | ✅ Yes | 67% |
| Legacy content grouping | ❌ No | ❌ No | ✅ Yes | 33% |

---

## De Facto Standards

### High Adoption (67-100%)

1. **visionTool for dev environment** - 100%
2. **Custom desk structure** - 67%
3. **media plugin** - 67%
4. **Singleton grouping** - 67%

### Medium Adoption (33-66%)

1. **presentationTool** - 33% (v4+ only)
2. **Custom document actions** - 33%
3. **Custom branding** - 33%
4. **Third-party plugins** - 33-67% (varies by plugin)

### Low Adoption (0-32%)

1. **Custom validation utilities** - 33%
2. **Custom orderings** - 33%
3. **SAML SSO** - 33%
4. **Preview panes** - 33%

---

## Critical Gaps

1. **Helix lacks custom structure** - No content organization or singleton grouping
2. **v2 (kariusdx) uses deprecated APIs** - Parts system removed in v3, migration needed
3. **Presentation tool underutilized** - Only ripplecom uses modern visual editing
4. **Inconsistent plugin strategy** - No shared plugin set across projects
5. **Authentication not standardized** - Only ripplecom uses SSO

---

## Recommendations

1. **Migrate kariusdx to v3/v4** - Parts system deprecated, breaking changes in v3
2. **Standardize plugin set** - Consider media plugin + presentationTool across all projects
3. **Add desk structure to helix** - Improve content organization and UX
4. **Extract reusable utilities** - Share validation/preview utilities across projects
5. **Document custom actions pattern** - Kariusdx's auto-slug pattern is valuable
6. **Consider SSO for all projects** - Ripplecom's SAML pattern improves security
7. **Standardize singleton handling** - Use template filtering (ripplecom pattern)

---

**Next Steps:**
1. Generate RAG-optimized documentation for 8 key patterns
2. Create 4 Semgrep rules for desk structure and plugin usage
3. Document migration path from v2 parts system to v3/v4 defineConfig
