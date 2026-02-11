---
title: "Component Collocation: Shared vs Route-Specific Organization"
category: "project-structure"
subcategory: "organization"
tags: ["components", "collocation", "organization", "file-structure"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Component Collocation: Shared vs Route-Specific Organization

## Overview

Next.js projects organize components using hybrid approach: shared components directory for reusable components + route-specific component folders for page-local components. All three projects maintain dedicated shared components directory (helix: 57, policy-node: 39, kariusdx: 62), while helix additionally uses route-specific component folders (33% adoption).

**Benefits:** Shared components easily findable in central location, route-specific components prevent global bloat, clear component ownership and usage scope.

**Pattern:** App Router enables component collocation in `app/` directory alongside routes. Pages Router requires separate `components/` directory.

## Shared Components Directory

All three projects maintain dedicated `components/` directory for globally reusable components.

### App Router Pattern (helix, policy-node)

```
app/
└── (frontend)/
    ├── components/          ← Shared components (57 in helix)
    │   ├── SiteHeader/
    │   │   ├── SiteHeader.tsx
    │   │   └── SiteHeader.module.scss
    │   ├── SiteFooter/
    │   ├── Button/
    │   ├── Card/
    │   └── Navigation/
    ├── page.tsx
    └── resources/
        └── page.tsx
```

**Location:** Inside route group `(frontend)/components` or at app root `app/components`.

**Benefit:** Components collocated with routes they serve. App Router folder structure flexible (components can live anywhere in `app/`).

### Pages Router Pattern (kariusdx)

```
components/              ← Shared components (62 total)
├── Header/
├── Footer/
├── Button/
└── Card/

pages/
├── _app.tsx
└── index.tsx
```

**Location:** Root-level `components/` directory separate from `pages/`.

**Requirement:** Components must live outside `pages/` to avoid becoming routes.

**Comparison:** App Router allows components in `app/` directory (any non-special file name). Pages Router requires separate directory.

## Route-Specific Component Folders

Helix uses route-specific component folders to collocate components with the routes that use them exclusively.

```
app/(frontend)/
└── resources/
    ├── page.tsx                 ← /resources route
    ├── components/              ← Route-specific components
    │   ├── SearchForm/
    │   ├── ResourceTeaser/
    │   ├── FilterGroup/
    │   └── StickyNav/
    └── [slug]/
        ├── page.tsx             ← /resources/[slug] route
        └── components/          ← Nested route-specific
            ├── SocialShareButtons/
            └── ResourceContent/
```

**Pattern:** `components/` folder inside route folder contains components used only by that route.

**Benefit:** Clear component ownership. No global component bloat from one-off components. Easier to delete routes with all dependencies.

**Adoption:** 33% (helix only). Policy-node and kariusdx use only shared components directory.

## Decision Tree: Shared vs Route-Specific

### Use Shared Components When:
- Component reused across 2+ routes
- Component is part of design system (Button, Card, Input)
- Component is layout structure (Header, Footer, Sidebar)
- Component is utility (Modal, Tooltip, Dropdown)

```
app/
└── components/
    ├── Button/          ← Used site-wide
    ├── Card/            ← Used in multiple routes
    └── Modal/           ← Utility component
```

### Use Route-Specific Components When:
- Component used only in single route
- Component tightly coupled to route data structure
- Component unlikely to be reused elsewhere
- Want to delete route with all dependencies easily

```
app/
└── blog/
    ├── page.tsx
    └── components/
        ├── BlogPostList/      ← Only used on blog page
        ├── BlogFilters/       ← Only used on blog page
        └── BlogPagination/    ← Only used on blog page
```

## Component Folder Structure

All projects follow folder-per-component pattern regardless of shared vs route-specific.

```
ComponentName/
├── ComponentName.tsx
├── ComponentName.module.scss
├── ComponentName.test.tsx      ← If testing exists
├── index.ts                    ← Barrel export
└── subcomponents/              ← Optional nested components
    └── SubComponent/
```

**Pattern:** Component folder contains all related files (component, styles, tests). Barrel export (`index.ts`) enables clean imports.

**Import:**
```tsx
import SiteHeader from '@/components/SiteHeader'  // Resolves to index.ts
```

**Adoption:** 100% use folder-per-component structure.

## Import Path Patterns

### Absolute Imports with @ Alias

All projects configure TypeScript path alias `@` for clean imports from anywhere.

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./app/*"]  // or ["./src/*"]
    }
  }
}
```

**Usage:**
```tsx
import SiteHeader from '@/components/SiteHeader'        // Shared component
import BlogList from '@/blog/components/BlogList'       // Route-specific
import { sanityFetch } from '@/lib/sanity'              // Utility
```

**Benefit:** No relative path hell (`../../../components`). Imports consistent regardless of file depth.

**Adoption:** 100% use `@` path alias.

### Relative Imports for Local Files

Route-specific components use relative imports when importing from same route.

```tsx
// app/blog/page.tsx
import BlogList from './components/BlogList'  // Same route
import Card from '@/components/Card'          // Shared component
```

**Pattern:** Relative paths (`./`) for same-route imports, absolute paths (`@/`) for cross-route imports.

**Benefit:** Clear distinction between local and shared dependencies.

## Shared Component Categories

Shared components typically fall into categories:

### Layout Components
Structural elements used across many routes.

```
components/
├── SiteHeader/
├── SiteFooter/
├── Sidebar/
├── Navigation/
└── Container/
```

**Adoption:** 100% of projects have header/footer layout components.

### Design System Components
Reusable UI primitives from design system.

```
components/
├── Button/
├── Card/
├── Input/
├── Select/
└── Checkbox/
```

**Adoption:** 67% have design system components (helix + policy-node).

### Feature Components
Shared feature components used across multiple routes.

```
components/
├── SearchBar/
├── NewsletterSignup/
├── SocialShare/
└── Breadcrumbs/
```

**Adoption:** 100% have feature components.

### Utility Components
Helper components for common patterns.

```
components/
├── Modal/
├── Tooltip/
├── Dropdown/
└── Tabs/
```

**Adoption:** 67% have utility components.

## Component Naming Conventions

Component names use PascalCase for both file and folder names.

```
components/
├── SiteHeader/              ← PascalCase folder
│   ├── SiteHeader.tsx       ← PascalCase file
│   └── SiteHeader.module.scss
└── Button/
    ├── Button.tsx
    └── Button.module.scss
```

**Rule:** Component name matches folder name matches file name.

**Benefit:** Predictable structure. Easy to find component by name.

**Adoption:** 100% use PascalCase for component names.

## Component Export Patterns

All projects use barrel exports (`index.ts`) for clean component imports.

```tsx
// components/Button/index.ts
export { default } from './Button'
export type { ButtonProps } from './Button'
```

**Usage:**
```tsx
import Button from '@/components/Button'  // Resolves to index.ts → Button.tsx
```

**Benefit:** Encapsulates internal file structure. Consumers import from folder, not specific file.

**Adoption:** 100% use barrel exports in component folders.

## App Router vs Pages Router Collocation

### App Router: Flexible Collocation

App Router allows components anywhere in `app/` directory. Only special file names (`page.tsx`, `layout.tsx`) have routing significance.

```
app/
├── components/              ← Shared components
├── blog/
│   ├── components/          ← Route-specific
│   ├── utils/               ← Route-specific utilities
│   └── page.tsx
└── lib/                     ← Shared utilities
```

**Benefit:** Route-related code collocated together. Clear feature boundaries.

### Pages Router: Strict Separation

Pages Router treats all files in `pages/` as routes. Components must live outside.

```
components/                  ← All components (no choice)
├── Header/
└── Button/

pages/                       ← Routes only
├── _app.tsx
└── index.tsx
```

**Limitation:** Cannot collocate route-specific components with routes. All components treated as global.

**Workaround:** Naming convention (`BlogPostList` prefix) to indicate route ownership, but files still globally accessible.

## Component Discovery Patterns

### Shared Components

Developers find shared components by browsing `components/` directory or IDE autocomplete.

**Discovery methods:**
1. Browse `components/` directory tree
2. TypeScript autocomplete (`import * from '@/components/`...)
3. Search for component name in IDE

### Route-Specific Components

Developers find route-specific components by navigating to route folder.

**Discovery:**
1. Navigate to route folder (`app/blog/`)
2. Check `components/` subfolder
3. Components clearly scoped to route

**Benefit:** No confusion whether component is shared or route-specific. Location indicates scope.

## Migration Considerations

### Moving Component from Route-Specific to Shared

When component becomes reused, move from route folder to shared components.

**Before:**
```
app/blog/
└── components/
    └── Card/           ← Used only in blog
```

**After:**
```
app/
└── components/
    └── Card/           ← Now shared across routes
```

**Update imports:**
```tsx
// Before
import Card from './components/Card'

// After
import Card from '@/components/Card'
```

**Recommendation:** Wait until component reused in 2+ routes before moving to shared. Premature abstraction creates global bloat.

## Adoption Statistics

**Component organization patterns:**

| Project | Shared Components | Route-Specific | Total Components |
|---------|------------------|----------------|------------------|
| **helix** | 57 in app/(frontend)/components | 2 route folders | 57+ route-specific |
| **policy-node** | 39 in src/components | 0 route folders | 39 total |
| **kariusdx** | 62 in components/ | 0 (Pages Router) | 62 total |

**Route-specific adoption:** 33% (helix only uses route-specific component folders).

**Recommendation:** Use route-specific components for App Router projects to prevent global component bloat. Move to shared when reused.

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for router comparison enabling collocation
- **Route Groups:** See `route-groups-organization.md` for organizing shared components per group
- **Component Patterns:** See `folder-per-component.md` for detailed folder structure
- **Import Conventions:** See TypeScript conventions for path alias configuration
