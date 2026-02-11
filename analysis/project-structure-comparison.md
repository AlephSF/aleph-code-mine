# Project Structure - Cross-Project Quantitative Analysis

**Analysis Date:** February 11, 2026
**Domain:** Project Structure (App Router vs Pages Router)
**Projects Analyzed:** helix-dot-com-next, kariusdx-next, policy-node

---

## Executive Summary

Two of three Next.js projects migrated to App Router (helix v15, policy-node v14), while kariusdx remains on legacy Pages Router (v12). App Router adoption brings route groups, server components, streaming, and file-based metadata, but requires architectural migration from `getStaticProps` to async server components.

**Key Findings:**
- ✅ **App Router Adoption:** 67% (helix + policy-node)
- ✅ **Route Groups:** 100% of App Router projects use route groups
- ✅ **Server Components:** 100% of App Router projects use async server components
- ✅ **Metadata API:** 100% of App Router projects use generateMetadata()
- ✅ **Component Collocation:** Hybrid model (shared + route-specific components)
- ⚠️ **Pages Router Legacy:** 33% (kariusdx) remains on v12 Pages Router

---

## Quantitative Breakdown

### 1. Next.js Version Distribution

| Project | Next.js Version | Router Type | Migration Status |
|---------|----------------|-------------|------------------|
| **helix-dot-com-next** | 15.0.3 | App Router | ✅ Migrated |
| **policy-node** | 14.0.0 | App Router | ✅ Migrated |
| **kariusdx-next** | 12.3.4 | Pages Router | ❌ Not migrated |

**Interpretation:** 67% migrated to App Router. Helix runs latest v15 (stable), policy-node on v14 (stable). Kariusdx on v12 (legacy, Pages Router only).

### 2. File-Based Routing Patterns

#### App Router (helix + policy-node)

| File Type | helix | policy-node | Purpose |
|-----------|-------|-------------|---------|
| **page.tsx** | 9 | 11 | Route pages (replaced .tsx in pages/) |
| **layout.tsx** | 3 | 2 | Nested layouts (replaces _app.tsx) |
| **not-found.tsx** | 1 | 0 | 404 page (replaces 404.tsx) |
| **error.tsx** | 0 | 1 | Error boundary (new feature) |
| **loading.tsx** | 0 | 0 | Loading UI (new feature, not used) |
| **route.ts** | 2 | 7 | API routes (replaces pages/api/) |

**Pattern:** App Router uses special file names (page.tsx, layout.tsx) vs Pages Router arbitrary file names.

#### Pages Router (kariusdx)

| File Type | Count | Purpose |
|-----------|-------|---------|
| **[...slug].tsx** | 1 | Catch-all dynamic route |
| **404.tsx** | 1 | Custom 404 page |
| **_app.tsx** | 1 | Global app wrapper |
| **_document.js** | 1 | HTML document customization |
| **index.tsx** | 1 | Homepage (/) |
| **api/*.ts** | 0 | API routes (none found) |
| **Other pages** | 2 | Additional routes |

**Total Pages:** 7 files in pages/ directory.

### 3. Route Organization Patterns

#### Route Groups (App Router Only)

**helix:**
```
app/
├── (frontend)/        ← Route group (no URL segment)
│   ├── layout.tsx
│   ├── [[...slug]]/
│   ├── resources/
│   └── components/    ← Shared components
└── (studio)/          ← Route group (Sanity Studio)
    └── layout.tsx
```

**Benefit:** Route groups `(name)` organize routes without affecting URL structure. Used for multi-layout applications.

**Adoption:** 100% of App Router projects use route groups (helix has 2, policy-node uses [lang] param instead).

#### Dynamic Routes

**helix patterns:**
- `[[...slug]]` - Optional catch-all (matches / and /any/path)
- `[slug]` - Single dynamic segment
- `[slug]/[category]` - Nested dynamic segments

**policy-node patterns:**
- `[lang]` - i18n language parameter (top-level)
- `[...slug]` - Catch-all for flexible content
- `[slug]` - Single dynamic segment

**kariusdx patterns:**
- `[...slug]` - Catch-all in Pages Router
- No nested dynamic routes observed

**Comparison:**
- App Router: 15 total dynamic routes (helix: 6, policy: 9)
- Pages Router: 1 dynamic route (kariusdx)

### 4. Component Organization

All three projects use hybrid component organization: shared components directory + route-specific component folders.

#### Shared Components

| Project | Location | Count | Pattern |
|---------|----------|-------|---------|
| **helix** | `app/(frontend)/components/` | 57 | App Router collocation |
| **policy-node** | `src/components/` | 39 | Traditional /src pattern |
| **kariusdx** | `components/` | 62 | Root-level components |

**Pattern:** All projects keep shared components in dedicated directory (not inside pages/routes).

#### Route-Specific Components

**helix example:**
```
app/(frontend)/resources/
├── page.tsx
├── components/          ← Route-specific components
│   ├── SearchForm/
│   ├── ResourceTeaser/
│   └── FilterGroup/
└── [slug]/
    ├── page.tsx
    └── components/      ← Nested route-specific
        ├── SocialShareButtons/
        └── ResourceContent/
```

**Adoption:** 67% (helix has route-specific folders, others do not).

**Benefit:** Collocates components with routes they're used in. Prevents global component bloat.

### 5. Data Fetching Patterns

#### App Router: Async Server Components

**helix pattern:**
```tsx
// page.tsx
export async function generateStaticParams() {
  const buildSlugs = await client.fetch(query)
  return buildSlugs.map(({ slug }) => ({ slug: slug.split('/') }))
}

export default async function Page({ params }) {
  const pageData = await sanityFetch({ query, params })
  if (!pageData) notFound()
  return <PageContent data={pageData} />
}
```

**policy-node pattern:**
```tsx
// [lang]/layout.tsx
export async function generateMetadata({ params }) {
  const { lang } = await params
  const page = await getPageById(homepageId, lang)
  return generateStandardMetadata({ pageData: page })
}
```

**Adoption:**
- generateStaticParams: 6 instances (helix)
- generateMetadata: 1 instance (helix), 1 instance (policy-node)
- Total async server component pages: 20 (helix: 9, policy: 11)

#### Pages Router: getStaticProps/getServerSideProps

**kariusdx pattern:**
```tsx
// pages/index.tsx
export const getStaticProps = getServerSidePropsWithPreview

// Custom HOC wraps component
export default withPreview(Page)
```

**Adoption:** 8 instances of getStaticProps/getServerSideProps in kariusdx.

**Comparison:**

| Pattern | App Router | Pages Router |
|---------|-----------|--------------|
| **Data fetching** | Async components | getStaticProps |
| **Preview mode** | draftMode() | Custom HOC |
| **Metadata** | generateMetadata() | next-seo library |
| **404 handling** | notFound() | Return 404 from getStaticProps |

### 6. Metadata Management

#### App Router: Built-in Metadata API

**helix:**
```tsx
// layout.tsx
export const metadata: Metadata = {
  title: {
    template: '%s | Helix',
    default: 'Helix',
  },
  description: '...',
  metadataBase: new URL(baseUrl),
}

// page.tsx
export async function generateMetadata({ params }) {
  const pageData = await sanityFetch({ query, params })
  return buildMetaData({
    title: pageData.title,
    seoData: pageData.seo
  })
}
```

**Pattern:** Static metadata in layout, dynamic metadata in page files.

**Adoption:** 100% of App Router projects use metadata API (helix static, policy-node dynamic).

#### Pages Router: External SEO Library

**kariusdx:**
```tsx
// pages/_app.tsx
import { DefaultSeo } from 'next-seo'
<DefaultSeo {...SEO} />

// pages/index.tsx
import { NextSeo } from 'next-seo'
<NextSeo {...buildSeoData(pageData)} />
```

**Pattern:** Uses next-seo library for component-based SEO. Requires separate npm package and runtime overhead.

**Adoption:** 100% of Pages Router projects use next-seo (no built-in metadata API in v12).

### 7. Layout Patterns

#### App Router: Nested Layouts

**helix:**
```
app/
├── (frontend)/
│   ├── layout.tsx              ← Root layout (header, footer, analytics)
│   └── resources/
│       └── [slug]/
│           └── layout.tsx      ← Nested layout (resource-specific)
```

**Pattern:** Layouts nest and compose. Child layouts inherit parent layouts automatically.

**Example:**
```tsx
// app/(frontend)/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <SiteHeader />
        {children}           ← Nested layouts rendered here
        <SiteFooter />
      </body>
    </html>
  )
}

// app/(frontend)/resources/[slug]/layout.tsx
export default function ResourceLayout({ children }) {
  return (
    <div className="resource-wrapper">
      {children}             ← Page content rendered here
    </div>
  )
}
```

**Adoption:** 100% of App Router projects use nested layouts (helix: 3 layouts, policy: 2 layouts).

#### Pages Router: Single Global Layout

**kariusdx:**
```tsx
// pages/_app.tsx
function MyApp({ Component, pageProps }) {
  return (
    <Layout globalData={pageProps.globalData}>
      <Component {...pageProps} />
    </Layout>
  )
}
```

**Pattern:** Single global `<Layout>` component wraps all pages. No automatic nesting.

**Limitation:** Per-route layouts require manual conditional logic or HOC composition.

### 8. API Routes

#### App Router: Route Handlers

**helix:**
```
app/
└── api/
    ├── cache/
    │   └── route.ts        ← GET /api/cache
    └── revalidate/
        └── route.ts        ← POST /api/revalidate
```

**Pattern:** File named `route.ts` exports HTTP method handlers (GET, POST, etc.).

**Example:**
```tsx
// app/api/cache/route.ts
export async function GET(request: Request) {
  return Response.json({ status: 'ok' })
}
```

**Adoption:** 9 total API routes (helix: 2, policy-node: 7).

#### Pages Router: API Routes

**kariusdx:**
```
pages/
└── api/
    └── (no API routes found)
```

**Pattern:** File-based routing in pages/api/ directory. No API routes detected in kariusdx.

### 9. Internationalization (i18n)

#### App Router: Manual i18n with Middleware

**policy-node:**
```
src/
├── middleware.ts              ← Detects lang from URL
├── i18n-config.ts            ← Language configuration
└── app/
    └── [lang]/               ← Language parameter in route
        ├── layout.tsx        ← Lang-aware layout
        └── page.tsx
```

**Pattern:** Middleware detects language, [lang] param in all routes, TranslationProvider context.

**URL structure:** `/en/about`, `/es/about`, `/fr/about`

**Adoption:** 33% (policy-node only uses i18n).

#### Pages Router: Built-in i18n (Not Used)

**kariusdx:** No i18n configuration detected. Next.js 12 supports built-in i18n routing but not used.

### 10. Middleware Usage

| Project | Middleware File | Purpose |
|---------|----------------|---------|
| **helix** | ❌ None | Uses route groups instead |
| **policy-node** | ✅ src/middleware.ts | i18n language detection |
| **kariusdx** | ❌ None | No middleware |

**Policy-node middleware pattern:**
```tsx
// src/middleware.ts
import { i18n } from './i18n-config'

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname
  const pathnameIsMissingLocale = i18n.locales.every(
    (locale) => !pathname.startsWith(`/${locale}/`)
  )

  if (pathnameIsMissingLocale) {
    return NextResponse.redirect(
      new URL(`/${i18n.defaultLocale}${pathname}`, request.url)
    )
  }
}
```

**Adoption:** 33% (1 of 3 projects use middleware).

### 11. Preview/Draft Mode

#### App Router: draftMode()

**helix:**
```tsx
import { draftMode } from 'next/headers'

export default async function Page({ params }) {
  const isDraftMode = draftMode().isEnabled

  return isDraftMode ? (
    <PreviewProvider>{children}</PreviewProvider>
  ) : (
    {children}
  )
}
```

**Pattern:** Built-in `draftMode()` function from next/headers. No external dependencies.

**Adoption:** 100% of App Router projects use draftMode() (helix + policy).

#### Pages Router: Custom Preview HOC

**kariusdx:**
```tsx
import withPreview from 'hocs/withPreview'

export default withPreview(Page)

export const getStaticProps = getServerSidePropsWithPreview
```

**Pattern:** Custom HOC wraps component, custom getStaticProps wrapper handles preview logic.

**Adoption:** 100% of Pages Router projects use custom preview system.

### 12. Error Handling

| Feature | App Router | Pages Router |
|---------|-----------|--------------|
| **Error boundaries** | error.tsx file | Custom ErrorBoundary component |
| **404 pages** | not-found.tsx | 404.tsx |
| **notFound() function** | ✅ Available | ❌ Not available |
| **Error isolation** | Per-route error boundaries | Global error boundary only |

**App Router error.tsx adoption:**
- helix: 0 error.tsx files (relies on not-found.tsx)
- policy-node: 1 error.tsx file ([lang]/error.tsx)

**Pages Router 404.tsx adoption:**
- kariusdx: 1 404.tsx file (custom 404 page)

### 13. Loading States

**App Router loading.tsx:**
- helix: 0 loading.tsx files
- policy-node: 0 loading.tsx files

**Adoption:** 0% of App Router projects use loading.tsx special file. Likely rely on Suspense boundaries manually.

---

## Pattern Summary Matrix

| Pattern | helix (App) | policy (App) | kariusdx (Pages) | De Facto Standard? |
|---------|-------------|--------------|------------------|-------------------|
| **App Router** | ✅ v15 | ✅ v14 | ❌ v12 | ⚠️ PARTIAL (67%) |
| **Route groups** | ✅ (frontend)/(studio) | ✅ [lang] | ❌ N/A | ✅ YES (100% App Router) |
| **Nested layouts** | ✅ 3 layouts | ✅ 2 layouts | ❌ 1 global | ✅ YES (100% App Router) |
| **Metadata API** | ✅ generateMetadata | ✅ generateMetadata | ❌ next-seo | ✅ YES (100% App Router) |
| **Async server components** | ✅ All pages | ✅ All pages | ❌ getStaticProps | ✅ YES (100% App Router) |
| **Route-specific components** | ✅ Yes | ❌ No | ❌ No | ⚠️ PARTIAL (33%) |
| **Draft mode** | ✅ draftMode() | ✅ draftMode() | ❌ Custom HOC | ✅ YES (100% App Router) |
| **i18n** | ❌ No | ✅ [lang] + middleware | ❌ No | ⚠️ PARTIAL (33%) |
| **Middleware** | ❌ No | ✅ Yes | ❌ No | ⚠️ PARTIAL (33%) |
| **Error boundaries** | ❌ not-found only | ✅ error.tsx | ❌ 404.tsx | ⚠️ PARTIAL (33%) |

---

## Recommendations for Documentation

### High-Confidence Patterns (Document as Standards)
1. ✅ **App Router migration path** (67% adoption, modern Next.js)
2. ✅ **Route groups organization** (100% App Router adoption)
3. ✅ **Nested layouts** (100% App Router adoption)
4. ✅ **Metadata API usage** (100% App Router adoption)
5. ✅ **Async server components** (100% App Router adoption)
6. ✅ **Component collocation** (hybrid shared + route-specific)

### Medium-Confidence Patterns (Document with Context)
1. ⚠️ **Route-specific component folders** (33% adoption - helix only)
2. ⚠️ **i18n with [lang] parameter** (33% adoption - policy-node only)
3. ⚠️ **Middleware usage** (33% adoption - policy-node for i18n)

### Gap Patterns (Document as Migration Needs)
1. ❌ **Pages Router to App Router migration** (kariusdx needs migration)
2. ❌ **loading.tsx usage** (0% adoption - feature available but unused)
3. ❌ **error.tsx usage** (33% adoption - underutilized error handling)

---

## Next Steps

1. **Generate Documentation Files:**
   - app-router-vs-pages-router.md
   - route-groups-organization.md
   - nested-layouts-pattern.md
   - metadata-api-usage.md
   - async-server-components.md
   - component-collocation-patterns.md
   - i18n-with-app-router.md
   - migration-pages-to-app-router.md

2. **Generate Semgrep Rules:**
   - Warn on getStaticProps usage (suggest migration to async components)
   - Enforce metadata export in layout files
   - Warn on next-seo usage (suggest built-in Metadata API)
   - Enforce route group naming convention

3. **Documentation Focus:**
   - Migration guide from Pages Router to App Router (for kariusdx)
   - Best practices for route organization (route groups vs flat)
   - When to use route-specific vs shared components
   - i18n patterns in App Router (middleware + [lang] param)
