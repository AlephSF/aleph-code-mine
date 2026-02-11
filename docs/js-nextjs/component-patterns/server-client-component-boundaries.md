---
title: "Server-Client Component Boundaries"
category: "component-patterns"
subcategory: "react-server-components"
tags: ["app-router", "next-14", "next-15", "react-server-components", "use-client"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

## Default Server Component Rule

Next.js App Router (v13+) treats all components as React Server Components (RSC) by default. Server components render on the server, do not include client-side JavaScript, and cannot use browser APIs or React hooks. Components are server components unless explicitly marked with `'use client'` directive. This pattern applies to Next.js v14 and v15 App Router applications. Pages Router (v12-13) does not use this pattern.

Server components enable:
- Direct database queries without API routes
- Server-only code execution (no client bundle)
- Automatic code splitting
- Reduced JavaScript sent to browser

Components without interactivity (static content, layout wrappers, data-fetching pages) should remain server components.

## When to Use 'use client' Directive

Client components require the `'use client'` directive at the top of the file (before imports). Client components are necessary when components use React hooks, browser APIs, event handlers, or any interactive functionality. Client components render on both server (initial HTML) and client (hydration + interactivity).

```typescript
'use client'

import { useState } from 'react'
import cx from 'classnames'
import styles from './SiteHeader.module.scss'

type SiteHeaderProps = {
  navMenu: MenuItem[] | null
  currentLanguageCode: Locale
}

export default function SiteHeader({
  navMenu, currentLanguageCode,
}: SiteHeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className={styles.header}>
      <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
        Menu
      </button>
    </header>
  )
}
```

### Client Component Inventory

Components requiring `'use client'` include:
- Interactive components with event handlers (onClick, onChange, onSubmit)
- Components using React hooks (useState, useEffect, useContext)
- Components using browser APIs (window, document, localStorage)
- Components using usePathname, useRouter, useSearchParams (Next.js client hooks)
- Animation libraries (Framer Motion, GSAP with DOM manipulation)
- Components with refs (useRef for DOM access)

Analysis shows helix-dot-com-next has 35 client components (12% of total), policy-node has 19 client components (8% of total). Most components remain server components by default.

## Async Server Components with Data Fetching

Server components support async function syntax for data fetching. Async server components await data before rendering, eliminating the need for loading states or useEffect hooks for initial data. Async components must use function declaration syntax (not arrow functions).

```typescript
import { getBlockPatternsOptimized } from '@/lib/graphQL/queries/blockPatternsOptimized'

type PageProps = {
  page: PageByUriOrId
  currentLanguage: TLanguage
}

export default async function Page({
  page, currentLanguage,
}: PageProps) {
  // Direct async data fetching in component
  const blockPatterns = await getBlockPatternsOptimized(currentLanguage.code)

  return (
    <article>
      <PageHeader title={page.title} />
      <PageComponents blocks={blockPatterns} />
    </article>
  )
}
```

Async server components cannot:
- Use React hooks (useState, useEffect, useContext)
- Be marked with `'use client'`
- Handle browser events
- Use browser-only APIs

Async components are server-only and do not hydrate on the client. Parent components pass fetched data to client components via props.

## App Router vs Pages Router Context

App Router (Next.js 13+) introduced React Server Components and the `'use client'` directive. Pages Router (Next.js 12 and earlier) does not use this pattern - all components in Pages Router are client components by default. The three analyzed codebases span Next.js versions:
- helix-dot-com-next: v14 (App Router)
- policy-node: v15 (App Router)
- kariusdx-next: v12 (Pages Router - no RSC)

App Router patterns (v14/v15) represent the forward-looking standard documented here. Pages Router projects will migrate to App Router over time and should adopt these patterns during migration.
