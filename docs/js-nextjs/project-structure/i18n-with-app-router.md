---
title: "Internationalization with App Router and Middleware"
category: "project-structure"
subcategory: "i18n"
tags: ["i18n", "internationalization", "localization", "middleware", "app-router"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Internationalization with App Router and Middleware

## Overview

Next.js App Router uses manual i18n implementation with middleware and `[lang]` dynamic parameter. Policy-node implements this pattern (33% adoption) with language detection middleware and translated content fetching. Pages Router offered built-in i18n config (not used in analyzed codebases).

**Pattern:** Middleware detects language from URL, `[lang]` parameter in all routes, context provider for translations, GraphQL queries fetch translated content.

**Benefits:** Full control over i18n behavior, supports complex translation needs, works with headless CMS (WordPress Polylang).

## URL Structure with Language Parameter

All routes include `[lang]` parameter as first segment.

```
app/
└── [lang]/
    ├── layout.tsx           ← Language-aware root layout
    ├── page.tsx             ← Homepage with lang param
    ├── news/
    │   └── page.tsx         ← News with lang param
    └── [...slug]/
        └── page.tsx         ← Catch-all with lang param
```

**URL pattern:**
- `/en` - English homepage
- `/es/news` - Spanish news page
- `/fr/about` - French about page

**Pattern:** `[lang]` parameter in route structure. All routes receive language as param.

## i18n Configuration

Language configuration defines available locales and default language.

```tsx
// i18n-config.ts (policy-node pattern)
export const i18n = {
  defaultLocale: 'en',
  locales: ['en', 'es', 'fr', 'de'],
  localeData: {
    en: { locale: 'en-US', name: 'English', direction: 'ltr' },
    es: { locale: 'es-ES', name: 'Español', direction: 'ltr' },
    fr: { locale: 'fr-FR', name: 'Français', direction: 'ltr' },
    de: { locale: 'de-DE', name: 'Deutsch', direction: 'ltr' },
  },
} as const

export type Locale = (typeof i18n)['locales'][number]
```

**Pattern:** Centralized config exports locales array, default locale, and metadata per locale.

**Type safety:** `Locale` type derived from config ensures type-safe language params.

## Middleware for Language Detection

Middleware detects language and redirects to correct URL if missing.

```tsx
// middleware.ts (policy-node pattern)
import { NextRequest, NextResponse } from 'next/server'
import { i18n } from './i18n-config'

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if pathname already has locale
  const pathnameHasLocale = i18n.locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  if (pathnameHasLocale) return  // Already has locale, continue

  // Detect locale from Accept-Language header
  const locale = getLocale(request) || i18n.defaultLocale

  // Redirect to URL with locale
  return NextResponse.redirect(
    new URL(`/${locale}${pathname}`, request.url)
  )
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',  // Skip API routes and static files
  ],
}
```

**Pattern:** Check for locale in URL. Redirect to locale-prefixed URL if missing. Detect locale from headers or use default.

**Benefit:** URLs without language prefix automatically redirect. Handles initial visits without language.

## Language-Aware Root Layout

Root layout receives `[lang]` param and sets HTML lang attribute.

```tsx
// app/[lang]/layout.tsx (policy-node pattern)
import { i18n, Locale } from '@/i18n-config'
import { notFound } from 'next/navigation'

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ lang: Locale }>
}) {
  const { lang } = await params

  // Validate language is supported
  if (!i18n.locales.includes(lang)) {
    notFound()  // 404 for invalid language codes
  }

  const htmlLang = i18n.localeData[lang].locale  // en-US, es-ES, etc.

  return (
    <html lang={htmlLang}>
      <body>
        <TranslationProvider lang={lang}>
          {children}
        </TranslationProvider>
      </body>
    </html>
  )
}
```

**Pattern:** Validate lang param, set HTML lang attribute, wrap in translation provider.

**Benefit:** Correct lang attribute for accessibility and search engines. Translation context available to all components.

## Fetching Translated Content

Content fetched with language code parameter.

```tsx
// app/[lang]/page.tsx (policy-node pattern)
import normalizeLanguageSlug from '@/utils/normalizeLanguageSlug'
import { getPageById } from '@/lib/graphQL/queries/pages'

export default async function Page({ params }) {
  const { lang } = await params
  const languageCode = normalizeLanguageSlug(lang)  // en → EN, es → ES

  // Fetch translated content from WordPress Polylang
  const page = await getPageById(homepageId, languageCode)

  if (!page) notFound()

  return <PageContent page={page} />
}
```

**Pattern:** Normalize language slug, pass to content API, fetch translated version.

**CMS integration:** WordPress Polylang stores translations per language code. GraphQL query filters by language.

## Translation Provider Context

Context provides translations to components.

```tsx
// context/TranslationContext.tsx (policy-node pattern)
'use client'

import { createContext, useContext } from 'react'
import { Locale } from '@/i18n-config'

const TranslationContext = createContext<{ lang: Locale } | null>(null)

export function TranslationProvider({
  children,
  lang,
}: {
  children: React.ReactNode
  lang: Locale
}) {
  return (
    <TranslationContext.Provider value={{ lang }}>
      {children}
    </TranslationContext.Provider>
  )
}

export function useTranslation() {
  const context = useContext(TranslationContext)
  if (!context) throw new Error('useTranslation must be used within TranslationProvider')
  return context
}
```

**Pattern:** Context provides current language to client components. Hook accesses language.

**Usage:**
```tsx
'use client'

import { useTranslation } from '@/context/TranslationContext'

export default function LanguageSwitcher() {
  const { lang } = useTranslation()
  return <div>Current language: {lang}</div>
}
```

## Generating Static Params for All Locales

Generate static pages for all language variants.

```tsx
// app/[lang]/[...slug]/page.tsx
export async function generateStaticParams() {
  const pages = await fetchAllPages()
  const locales = i18n.locales

  // Generate params for all locale + slug combinations
  return pages.flatMap(page =>
    locales.map(lang => ({
      lang,
      slug: page.slug.split('/'),
    }))
  )
}
```

**Pattern:** Cross-product of locales and slugs. Generates static page per language variant.

**Build output:** English blog post + Spanish translation = 2 static HTML files.

## Language Switcher Component

Language switcher navigates to current page in different language.

```tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { i18n } from '@/i18n-config'

export default function LanguageSwitcher() {
  const pathname = usePathname()

  const switchLanguage = (newLang: string) => {
    // Replace current lang with new lang in pathname
    const segments = pathname.split('/')
    segments[1] = newLang  // First segment is lang
    return segments.join('/')
  }

  return (
    <nav>
      {i18n.locales.map(lang => (
        <Link key={lang} href={switchLanguage(lang)}>
          {i18n.localeData[lang].name}
        </Link>
      ))}
    </nav>
  )
}
```

**Pattern:** Replace language segment in current URL. Link to same page in different language.

**Benefit:** Users stay on same page, just switch language.

## Metadata with i18n

Generate metadata per language using generateMetadata.

```tsx
// app/[lang]/layout.tsx
export async function generateMetadata({ params }) {
  const { lang } = await params
  const page = await getTranslatedPage(homepageId, lang)

  return {
    title: page.seo?.title || page.title,
    description: page.seo?.description,
    alternates: {
      canonical: `/${lang}`,
      languages: {
        'en-US': '/en',
        'es-ES': '/es',
        'fr-FR': '/fr',
      },
    },
  }
}
```

**Pattern:** Fetch translated metadata, set alternate language links for SEO.

**Benefit:** Search engines discover all language variants via hreflang links.

## Adoption Statistics

**i18n patterns:**

| Project | i18n Method | Languages | Middleware | Context |
|---------|-------------|-----------|-----------|---------|
| **helix** | None | N/A | ❌ No | ❌ No |
| **policy-node** | [lang] param + middleware | 4 (en, es, fr, de) | ✅ Yes | ✅ Yes |
| **kariusdx** | None | N/A | ❌ No | ❌ No |

**i18n adoption:** 33% (policy-node only).

**Recommendation:** Use [lang] parameter pattern for App Router i18n. Middleware handles redirects, context provides translations.

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for routing comparison
- **Middleware:** See `file-based-routing-conventions.md` for middleware patterns
- **Dynamic Routes:** See Next.js docs for [param] patterns
