---
title: "Route Groups for App Organization Without URL Segments"
category: "project-structure"
subcategory: "routing"
tags: ["route-groups", "app-router", "organization", "layouts"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Route Groups for App Organization Without URL Segments

## Overview

Route groups in Next.js App Router organize routes logically without affecting URL structure. Folders wrapped in parentheses `(groupName)` do not appear in the URL path. Helix uses route groups `(frontend)` and `(studio)` to separate public website from Sanity CMS admin (100% adoption in App Router projects).

**Benefits:** Multiple root layouts in single app, logical code organization, shared layouts per group, clearer project structure without URL pollution.

**Syntax:** Folder name in parentheses `(name)` creates route group. Routes inside behave normally but group folder invisible in URLs.

## Route Group Syntax

Route groups created by wrapping folder name in parentheses. Group folder does not become URL segment.

```
app/
├── (frontend)/        ← Route group (no URL segment)
│   ├── layout.tsx     ← Frontend-specific layout
│   ├── page.tsx       ← / (homepage)
│   └── about/
│       └── page.tsx   ← /about (not /(frontend)/about)
└── (studio)/          ← Route group (no URL segment)
    ├── layout.tsx     ← Studio-specific layout
    └── [[...index]]/
        └── page.tsx   ← /studio (not /(studio)/studio)
```

**URL mapping:**
- `app/(frontend)/page.tsx` → `/`
- `app/(frontend)/about/page.tsx` → `/about`
- `app/(studio)/[[...index]]/page.tsx` → `/studio` (configured via basePath)

**Pattern:** Parentheses mark organizational folder. Routes inside maintain original URL structure.

## Multiple Root Layouts with Route Groups

Route groups enable multiple root layouts in single application. Each group has its own `layout.tsx` that defines HTML structure, fonts, and global providers.

### Example: Frontend + CMS Admin Layouts

**Frontend layout:**

```tsx
// app/(frontend)/layout.tsx (helix pattern)
import ttNorms from './lib/fonts'
import SiteHeader from './components/SiteHeader'
import SiteFooter from './components/SiteFooter'
import './styles/globals.scss'

export default function FrontendLayout({ children }) {
  return (
    <html lang="en">
      <body className={ttNorms.variable}>
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  )
}
```

**CMS Studio layout:**

```tsx
// app/(studio)/layout.tsx (helix pattern)
export default function StudioLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        {children}  ← No header/footer for CMS
      </body>
    </html>
  )
}
```

**Result:** Frontend routes (`/`, `/about`) use frontend layout with header/footer. Studio route (`/studio`) uses minimal layout without site chrome.

**Benefit:** Different layouts for different app sections without conditional logic or route checking.

**Adoption:** 100% of App Router projects with multiple layouts use route groups (helix has 2 groups).

## Organizing Routes by Feature

Route groups organize related routes together even when URLs are at different levels.

```
app/
├── (marketing)/
│   ├── page.tsx           ← / (homepage)
│   ├── about/
│   │   └── page.tsx       ← /about
│   └── pricing/
│       └── page.tsx       ← /pricing
└── (dashboard)/
    ├── dashboard/
    │   └── page.tsx       ← /dashboard
    ├── settings/
    │   └── page.tsx       ← /settings
    └── profile/
        └── page.tsx       ← /profile
```

**Pattern:** Routes grouped by feature (`marketing` vs `dashboard`) instead of URL structure.

**Benefit:** Related code collocated. Easier to find and maintain feature-specific routes.

**When to use:** Multi-section applications with distinct feature areas (marketing site vs app, public vs admin, etc.).

## Route Groups vs Flat Structure

### Without Route Groups (Flat)

```
app/
├── layout.tsx
├── page.tsx              ← /
├── about/
│   └── page.tsx          ← /about
├── pricing/
│   └── page.tsx          ← /pricing
├── dashboard/
│   └── page.tsx          ← /dashboard
└── settings/
    └── page.tsx          ← /settings
```

**Limitation:** Single root layout applies to all routes. Mixed concerns (marketing + app) in one directory.

### With Route Groups (Organized)

```
app/
├── (marketing)/
│   ├── layout.tsx        ← Marketing layout
│   ├── page.tsx          ← /
│   ├── about/            ← /about
│   └── pricing/          ← /pricing
└── (app)/
    ├── layout.tsx        ← App layout
    ├── dashboard/        ← /dashboard
    └── settings/         ← /settings
```

**Benefit:** Separate layouts per section. Clear feature boundaries. Easier to navigate codebase.

**Comparison:** Route groups add organizational layer without URL complexity.

## Shared Layouts Per Group

Each route group can define shared layout for all child routes. Layout applies only to routes within group.

```tsx
// app/(marketing)/layout.tsx
export default function MarketingLayout({ children }) {
  return (
    <>
      <MarketingHeader />
      {children}
      <MarketingFooter />
      <NewsletterSignup />
    </>
  )
}

// app/(app)/layout.tsx
export default function AppLayout({ children }) {
  return (
    <>
      <AppSidebar />
      <main>{children}</main>
    </>
  )
}
```

**Pattern:** Group layout wraps all routes in group. Different groups use different layouts without conditional logic.

**Benefit:** Marketing routes automatically get marketing layout. App routes automatically get app layout. No manual layout switching.

## Nested Route Groups

Route groups can nest inside each other for deeper organization (rarely needed).

```
app/
└── (marketing)/
    ├── layout.tsx
    ├── (landing-pages)/     ← Nested route group
    │   ├── page.tsx         ← /
    │   └── features/
    │       └── page.tsx     ← /features
    └── (content)/           ← Nested route group
        ├── blog/
        │   └── page.tsx     ← /blog
        └── docs/
            └── page.tsx     ← /docs
```

**Pattern:** Route groups inside route groups. All maintain flat URL structure.

**Adoption:** 0% (not observed in analyzed projects). Single-level route groups sufficient for most use cases.

**Recommendation:** Avoid nested route groups unless clear organizational benefit. Adds complexity without URL structure benefit.

## Route Groups with Shared Components

Route groups often include shared components directory for group-specific components.

```
app/
└── (frontend)/
    ├── layout.tsx
    ├── components/          ← Shared frontend components
    │   ├── SiteHeader/
    │   ├── SiteFooter/
    │   └── Navigation/
    ├── page.tsx
    └── about/
        └── page.tsx
```

**Pattern:** Components used across group routes live in group's `components/` directory.

**Benefit:** Component scope matches usage. No global component bloat.

**Adoption:** 100% of App Router projects with route groups include group-specific components folder (helix: 57 components in (frontend)/components).

## When NOT to Use Route Groups

Route groups add organizational layer but increase directory depth. Skip when not needed.

**Don't use when:**
- Single layout for entire app (no multiple root layouts)
- Small app with < 10 routes (flat structure simpler)
- Routes already organized by URL structure
- Team unfamiliar with route groups concept

**Use when:**
- Multiple distinct app sections (marketing + app, public + admin)
- Different layouts per section
- Large codebase needing logical organization
- Separating concerns (frontend vs CMS, etc.)

## Route Groups vs Parallel Routes

Route groups are organizational. Parallel routes render multiple pages simultaneously in different slots.

**Route groups:** Same URL, different organization. One page per route.

**Parallel routes:** Same URL, multiple pages simultaneously (modals, split views). Uses `@folder` syntax.

**Don't confuse:** Route groups `(name)` = organization. Parallel routes `@name` = simultaneous rendering.

## Real-World Example: helix-dot-com-next

Helix uses two route groups to separate public website from Sanity Studio.

```
app/
├── (frontend)/              ← Public website
│   ├── layout.tsx           ← Full site layout (header, footer, analytics)
│   ├── components/          ← 57 shared components
│   ├── styles/              ← Design system
│   ├── [[...slug]]/
│   │   └── page.tsx         ← Dynamic content pages
│   └── resources/
│       ├── page.tsx         ← /resources
│       └── [slug]/
│           └── page.tsx     ← /resources/[slug]
└── (studio)/                ← Sanity CMS admin
    ├── layout.tsx           ← Minimal layout (no chrome)
    └── [[...index]]/
        └── page.tsx         ← /studio
```

**URLs:**
- `/` → frontend layout + homepage
- `/about` → frontend layout + about page
- `/studio` → studio layout (minimal) + CMS

**Pattern:** Route groups enable completely different layouts for public site vs admin without complex routing logic.

**Benefit:** CMS admin has zero site chrome (header, footer, navigation). Public site has full layout. No conditional rendering.

## Adoption Statistics

**Route group usage:**

| Project | Route Groups | Purpose | Adoption |
|---------|-------------|---------|----------|
| **helix** | `(frontend)` `(studio)` | Public site + CMS | ✅ Yes |
| **policy-node** | None (uses [lang] param) | i18n routing | ❌ No |
| **kariusdx** | N/A (Pages Router) | N/A | ❌ No |

**App Router projects with route groups:** 50% (helix only).

**Alternative pattern:** Policy-node uses `[lang]` dynamic parameter instead of route groups for i18n organization.

**Recommendation:** Use route groups when multiple root layouts needed. Use dynamic parameters `[param]` for runtime routing (i18n, multi-tenancy).

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for router comparison
- **Nested Layouts:** See `nested-layouts-pattern.md` for layout composition
- **Parallel Routes:** See Next.js docs for simultaneous page rendering
- **Dynamic Routes:** See `file-based-routing-conventions.md` for [param] patterns
