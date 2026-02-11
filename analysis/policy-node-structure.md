# Policy-Node (Airbnb Policy Site) - Structural Analysis

## Project Overview

**Name:** airbnb-policy-site  
**Type:** Next.js 15 Application (Headless WordPress CMS)  
**Version:** 0.1.0  
**Tech Stack:** Next.js 15.5.10, React 19.0.0, TypeScript 5.7.3, WordPress VIP GraphQL

---

## Code Metrics

- **Total Source Files:** 431
- **TypeScript/TSX Lines:** ~29,501 LOC
- **SCSS Lines:** ~4,536 LOC
- **React Components:** 40+
- **Build Cache System:** 2,806 LOC (dedicated)

---

## Testing Setup

**Current Status:** NO formal test framework configured

- No Jest, Vitest, Playwright, or Cypress

**Validation Strategy:**
- Data validation scripts (validate-data.ts)
- Manual testing scripts in /scripts

---

## Styling Approach

**Methodology:** CSS Modules with SCSS (Sass)

**Characteristics:**
1. **Global Styles:** globals.scss with resets, typography, print styles
2. **Component Styles:** Each component has `*.module.scss` (scoped)
3. **Design System:** @aleph/nought-sass-mixins with variables
4. **Features:** Print-friendly, responsive, accessible focus states
5. **Linting:** Stylelint with pre-commit hooks

**No Tailwind or Styled-Components** - Pure CSS Modules approach

---

## Notable Architectural Decisions

1. **ISR with Redis** - Custom cache handler for Next.js 15 with cross-instance cache sharing
2. **Language/i18n Architecture** - URL-based routing: `/[lang]/[...slug]`
3. **CSV Data Pipeline** - S3 as single source of truth, ~190MB data downloads, automated hourly GitHub Actions
4. **WordPress Integration** - GraphQL API with 60s+ timeout handling, preview routes
5. **Performance Optimizations** - Build-time caching (2.8K LOC), search index pre-generation, ~13,800 pages built
6. **Search Architecture** - Fuse.js for fuzzy search with pre-generated indices
7. **API Routes** - /api/metrics, /api/phrases, /api/cache (authenticated)
8. **Deployment Strategy** - WordPress VIP hosting with branch → environment mapping
9. **Multi-Environment Support** - VIP production with Redis, local with S3 cache
10. **Git Workflow** - GitHub Actions CI/CD, Husky hooks, auto-generated data update PRs

---

**Summary:** Sophisticated, production-grade Next.js 15 application designed for high-traffic, multi-language content delivery with complex data pipelines (CSV from S3), Redis ISR caching, and WordPress VIP headless integration. Emphasis on caching at multiple levels and automated data management.
