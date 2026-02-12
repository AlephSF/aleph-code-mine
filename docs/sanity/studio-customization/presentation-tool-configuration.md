# Presentation Tool Configuration

---
title: "Presentation Tool Configuration"
category: "studio-customization"
subcategory: "preview"
tags: ["sanity", "presentation", "preview", "visual-editing", "v4"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-12"
---

## Overview

Sanity Presentation Tool (v4+) provides visual editing with real-time preview of content changes in the live frontend. Presentation Tool replaces legacy preview panes (v2) and `@sanity/production-preview` plugin. Only 33% of analyzed projects use Presentation Tool (ripplecom v4 only), as helix v3 and kariusdx v2 predate this feature.

## Basic Configuration

Presentation Tool requires three components: plugin configuration, preview URL resolver, and CORS origin whitelist.

**Plugin Setup:**

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { presentationTool } from 'sanity/presentation'
import getPreviewUrl from './src/utils/getPreviewUrl'
import getAllowOrigins from './src/utils/getAllowOrigins'

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

Ripplecom configures Presentation Tool with dynamic preview URLs based on deployment environment (localhost, Vercel preview, production).

## Preview URL Resolution

Preview URLs must adapt to environment: local development uses `localhost:3000`, Vercel preview branches use `*.vercel.app` domains, production uses final domain.

**Environment-Aware URL Resolver:**

```typescript
// src/utils/getPreviewUrl.ts
function getPreviewUrl() {
  const env = process.env.SANITY_STUDIO_VERCEL_ENV // "development" | "preview" | "production"
  const rippleApp = process.env.SANITY_STUDIO_RIPPLE_APP_URL
  const envUrl = process.env.SANITY_STUDIO_VERCEL_URL

  const relatedProjectsRaw =
    process.env.SANITY_STUDIO_VERCEL_RELATED_PROJECTS ||
    process.env.VERCEL_RELATED_PROJECTS

  let relatedProjects
  if (relatedProjectsRaw) {
    try {
      relatedProjects = JSON.parse(relatedProjectsRaw)
    } catch (e) {
      console.warn('Failed to parse related projects, using fallback', e)
    }
  }

  if (env === 'production') {
    return rippleApp || 'https://ripple.com'
  }

  if (env === 'preview' && Array.isArray(relatedProjects)) {
    const rippleProject = relatedProjects.find(
      (p) => p.project.name === 'ripplecom-nextjs',
    )
    const { preview } = rippleProject || {}
    const { branch } = preview || {}

    if (!branch) {
      console.warn('No preview branch found, using fallback')
      return rippleApp
    }

    return `https://${branch}`
  }

  // Development environment
  return 'http://localhost:3000'
}

export default getPreviewUrl
```

Ripplecom uses Vercel's `VERCEL_RELATED_PROJECTS` environment variable to find the preview branch URL for the corresponding Next.js app. Critical for monorepo setups where Sanity Studio and frontend deploy separately.

## CORS Origin Whitelist

Presentation Tool requires CORS configuration to allow iframe embedding from frontend domains.

**Allow Origins Configuration:**

```typescript
// src/utils/getAllowOrigins.ts
function getAllowOrigins() {
  const env = process.env.VERCEL_ENV
  const vercelUrl = process.env.VERCEL_URL

  const origins = ['http://localhost:*'] // Always allow localhost

  if (env === 'production') {
    origins.push(process.env.NEXT_PUBLIC_SITE_URL || 'https://ripple.com')
  }

  if (env === 'preview') {
    if (vercelUrl) {
      origins.push(
        `https://${vercelUrl.replace('sanity-studio', 'ripplecom-nextjs')}`,
      )
    }
    origins.push('https://ripplecom-nextjs-*-ripple-com.vercel.app')
  }

  return origins
}

export default getAllowOrigins
```

Ripplecom allows `localhost:*` (all ports) for development, production domain for production, and wildcard Vercel preview domains for PR previews. Wildcards (`*`) enable preview without hardcoding every PR branch URL.

## Main Documents Configuration

Main documents define which document types support visual editing and map them to frontend routes.

**defineDocuments Pattern:**

```typescript
import { defineDocuments } from 'sanity/presentation'

presentationTool({
  resolve: {
    mainDocuments: defineDocuments([
      {
        route: '/customer-case-study/:slug',
        filter: '_type == "caseStudy" && slug.current == $slug',
      },
      {
        route: '/lp/:slug',
        filter:
          '(_type == "leadGeneration" || _type == "thankYouPage") && slug.current == $slug',
      },
      {
        route: '/insights/:slug',
        filter: '_type == "blogPost" && slug.current == $slug',
      },
      {
        route: '/ripple-press/:slug',
        filter: '_type == "pressRelease" && slug.current == $slug',
      },
    ]),
  },
})
```

Ripplecom defines 4 main document types with route-to-query mappings. Route parameters (`:slug`) map to GROQ filter variables (`$slug`). Presentation Tool uses these mappings to resolve which document to edit when opening a preview URL.

**Route Parameter Extraction:**

URL `https://ripple.com/insights/bitcoin-surge` with route `/insights/:slug` extracts `slug = "bitcoin-surge"` and queries `*[_type == "blogPost" && slug.current == "bitcoin-surge"][0]`.

## Custom Preview Locations

Preview locations provide multiple URLs per document. Useful for documents with conditional rendering (thank you pages, multi-language content, A/B test variants).

**defineLocations Pattern:**

```typescript
import { defineLocations } from 'sanity/presentation'

presentationTool({
  resolve: {
    locations: {
      leadGeneration: defineLocations({
        select: {
          title: 'title',
          slug: 'slug.current',
          thankYouPageEnabled: 'thankYouPage.enabled',
        },
        resolve: (doc) => {
          if (!doc?.slug) {
            return undefined
          }

          const locations = [
            {
              title: doc?.title || 'Untitled',
              href: `/lp/${doc?.slug}`,
            },
          ]

          if (doc?.thankYouPageEnabled) {
            locations.push({
              title: `Thank You Page - ${doc?.title || 'Untitled'}`,
              href: `/lp/thank-you-${doc?.slug}`,
            })
          }

          return {
            locations,
            message: 'Lead Generation page(s) available',
          }
        },
      }),
      blogPost: defineLocations({
        select: {
          title: 'title',
          slug: 'slug.current',
        },
        resolve: (doc) => {
          if (!doc?.slug) {
            return undefined
          }

          return {
            locations: [
              {
                title: doc?.title || 'Untitled',
                href: `/insights/${doc?.slug}`,
              },
            ],
          }
        },
      }),
    },
  },
})
```

Ripplecom defines 5 location resolvers (leadGeneration, blogPost, caseStudy, pressRelease, thankYouPage). `leadGeneration` returns 2 locations when thank you page is enabled. Content editors see a dropdown in Presentation Tool to switch between locations.

**Location Resolver Requirements:**

1. `select` object defines which fields to query
2. `resolve` function returns `{ locations, message? }` object
3. Each location needs `title` and `href`
4. Return `undefined` if document has no preview (e.g., missing slug)

## Draft Mode Integration (Next.js)

Presentation Tool requires Next.js draft mode API route to bypass static generation and show unpublished content.

**API Route:**

```typescript
// app/api/draft-mode/presentation-tool/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'
import { validatePreviewUrl } from '@sanity/preview-url-secret'

export async function GET(request: Request) {
  const { isValid, redirectTo = '/' } = await validatePreviewUrl(
    client.withConfig({ token: readToken }),
    request.url,
  )

  if (!isValid) {
    return new Response('Invalid secret', { status: 401 })
  }

  draftMode().enable()
  redirect(redirectTo)
}
```

Route validates preview URL secret (prevents unauthorized draft mode access), enables draft mode, and redirects to the requested URL. Presentation Tool calls this route before loading preview iframe.

**Draft Mode Content Fetching:**

```typescript
// lib/sanity.ts
import { draftMode } from 'next/headers'
import { client } from './client'

export async function sanityFetch({ query, params = {} }) {
  const isDraftMode = draftMode().isEnabled

  if (isDraftMode) {
    return client.fetch(query, params, {
      perspective: 'previewDrafts',
      useCdn: false,
      token: process.env.SANITY_READ_TOKEN,
    })
  }

  return client.fetch(query, params, {
    perspective: 'published',
    useCdn: true,
  })
}
```

Draft mode uses `perspective: 'previewDrafts'` to fetch unpublished drafts, disables CDN caching, and requires read token for authenticated queries.

## Monorepo Deployment Pattern

Ripplecom uses Turborepo with separate Sanity Studio and Next.js app deployments. Presentation Tool must find the corresponding frontend deployment for each Sanity Studio deployment.

**Challenge:** Sanity Studio preview deploys to `sanity-studio-git-feature-123.vercel.app`, but frontend deploys to `ripplecom-nextjs-git-feature-123.vercel.app`.

**Solution:** Use `VERCEL_RELATED_PROJECTS` environment variable to find the related Next.js deployment.

```typescript
const relatedProjects = JSON.parse(process.env.VERCEL_RELATED_PROJECTS)
const rippleProject = relatedProjects.find(
  (p) => p.project.name === 'ripplecom-nextjs',
)
const previewUrl = `https://${rippleProject.preview.branch}`
```

Vercel exposes related projects when deploying from a monorepo. Parse JSON and extract the frontend preview URL.

## When to Use Presentation Tool

**Use Presentation Tool when:**

- Team includes non-technical content editors who need visual editing
- Frontend uses Next.js App Router with draft mode support
- Content changes need real-time preview (not just after publish)
- Multiple preview locations per document (thank you pages, variants)
- Project uses Sanity v4+

**Skip Presentation Tool when:**

- Team consists of technical users comfortable with form-based editing
- Frontend doesn't support draft mode (static sites, non-Next.js)
- Preview URLs are complex or require authentication
- Project uses Sanity v2 or v3 (not available)

Kariusdx (v2) uses legacy `@sanity/production-preview` plugin with iframe preview panes. This provides basic preview without visual editing.

## Migration from Legacy Preview Panes (v2)

Kariusdx uses v2 preview panes via `getDefaultDocumentNode`. Migrating to Presentation Tool (v4) requires removing custom document views and configuring Presentation Tool plugin.

**v2 Preview Panes (Deprecated):**

```javascript
import Iframe from 'sanity-plugin-iframe-pane'

export const getDefaultDocumentNode = ({ schemaType }) => {
  if (schemaType === 'page') {
    return S.document().views([
      S.view.form(),
      S.view.component(Iframe).options({
        url: (doc) => resolveProductionUrl(doc),
      }).title('Preview'),
    ])
  }
}
```

**v4 Presentation Tool (Modern):**

```typescript
presentationTool({
  previewUrl: {
    origin: getPreviewUrl(),
    previewMode: {
      enable: '/api/draft-mode/presentation-tool',
    },
  },
  resolve: {
    mainDocuments: defineDocuments([
      {
        route: '/page/:slug',
        filter: '_type == "page" && slug.current == $slug',
      },
    ]),
  },
})
```

Presentation Tool provides superior UX: click-to-edit overlays, real-time updates, and multi-location support. Migrate when upgrading to v4.

## Anti-Patterns

**Anti-Pattern 1: Hardcoded preview URLs**

```typescript
// ❌ BAD: Breaks in preview environments
previewUrl: {
  origin: 'https://ripple.com',
}
```

Use environment-aware resolver that handles localhost, preview, and production.

**Anti-Pattern 2: Missing CORS wildcards**

```typescript
// ❌ BAD: Breaks for new PR branches
allowOrigins: ['https://ripplecom-nextjs-git-main.vercel.app']

// ✅ GOOD: Handles all preview branches
allowOrigins: ['https://ripplecom-nextjs-*-ripple-com.vercel.app']
```

**Anti-Pattern 3: No draft mode validation**

```typescript
// ❌ BAD: Anyone can enable draft mode
export async function GET(request: Request) {
  draftMode().enable()
  redirect('/')
}

// ✅ GOOD: Validate secret before enabling
const { isValid } = await validatePreviewUrl(client, request.url)
if (!isValid) {
  return new Response('Invalid secret', { status: 401 })
}
```

## Related Patterns

- **desk-structure-customization.md** - Legacy v2 preview panes (deprecated)
- **preview-mode.md** (Next.js docs) - ISR with draft mode
- **custom-document-actions.md** - Customizing publish workflows

## References

- Ripplecom: `apps/sanity-studio/sanity.config.ts` (Presentation Tool configuration)
- Ripplecom: `apps/sanity-studio/src/utils/getPreviewUrl.ts` (environment-aware URLs)
- Ripplecom: `apps/sanity-studio/src/utils/getAllowOrigins.ts` (CORS configuration)
- Sanity Docs: Presentation Tool v4
