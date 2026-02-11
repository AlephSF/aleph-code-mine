# Kariusdx-Next Structural Reconnaissance Report

## Project Overview

**Project Name:** kariusdx-next  
**Version:** 0.1.0  
**Type:** Next.js 12 Medical/Clinical Diagnostic Website  
**Tech Stack:** Next.js 12.2.0, React 18.2.0, TypeScript 4.7.4, Sanity CMS

**Production URL:** https://kariusdx-next.vercel.app  

---

## Code Metrics

- **Total Files:** 338 source files
- **Lines of Code:** ~8,144 lines (TypeScript/JavaScript)
- **Components:** 85 TSX components
- **Styling:** 54 SCSS modules + global styles
- **Type Definitions:** 45+ TypeScript definition files
- **Sanity Queries:** 14+ GROQ query files

---

## Testing Setup

**Status:** NO TESTING FRAMEWORK DETECTED

- No Jest, Vitest, Playwright, or Cypress configuration
- No test files found
- No testing dependencies in package.json

**Gap:** Production site with 85 components and complex data fetching but no unit/integration/E2E tests.

---

## Styling Approach: SCSS WITH CSS MODULES

**Architecture:**
- CSS Modules for component scoping
- Global SCSS imports
- SCSS variables, mixins, and utility functions
- BEM-like naming convention

**No:** Tailwind CSS, styled-components, Emotion, or inline styles

---

## Routing Structure

**Pages Router (Next.js 12):**
- pages/_app.tsx: Global layout wrapper
- pages/[...slug]/index.tsx: **Catch-all dynamic pages** (main content from Sanity)
- Supports nested URLs like `/about-us/licensure`
- Server-side rendering with preview mode support

---

## Sanity CMS Integration

**Architecture:**
- Headless CMS for content management
- GROQ queries for data fetching
- Dual clients: Production (CDN) + Preview (draft support)

**Content Blocks (Page Builder Pattern):**
- Dynamic component rendering via `PageContent` component
- Type-safe block mapping
- Supports: ImageCarousel, ClinicalData, FAQ, NewsGrid, etc.

---

## Notable Architectural Patterns

1. **Page Builder Pattern** - Sanity-driven page composition with reusable content blocks
2. **Preview Mode Implementation** - withPreview HOC for draft content
3. **Modular Component Architecture** - Folder-per-component with colocated styles
4. **Security Headers** - CORS, CSP with Sanity whitelisting
5. **URL Redirects** - 20+ permanent/temporary redirects for legacy URLs
6. **Data Filtering & State** - Clinical Data filters with URL parameters
7. **Performance Optimizations** - Dynamic imports, bundle analyzer, Sanity CDN
8. **SEO Implementation** - next-seo integration, sitemap generation
9. **Third-party Integrations** - HubSpot, Wistia, Google Maps, Algolia
10. **Type Safety** - Strict TypeScript mode with 45+ custom type definitions

---

**Summary:** Mature, well-structured Next.js 12 medical website using Sanity CMS with comprehensive component library (85+ components), strong TypeScript typing, SCSS-based styling, and security-conscious architecture. Main gap: absence of automated testing.
