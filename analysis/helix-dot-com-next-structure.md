# Helix.com Next.js Repository - Structural Analysis

## Project Overview

**Project:** helix-dot-com-next  
**Version:** 0.1.0  
**Type:** Full-stack monorepo combining Next.js frontend with Sanity CMS  
**Description:** Renders both the Next.js-based frontend UI and Sanity-based CMS ("Studio") for https://www.helix.com

### Tech Stack Overview
- **Frontend Framework:** Next.js 14.0.3 with App Router
- **Runtime:** Node.js v18.17.0 (specified in .nvmrc)
- **Language:** TypeScript 5.0.4
- **CMS:** Sanity 3.20.1 with Sanity Studio
- **Package Manager:** Yarn 3.5.1
- **React Version:** 18.2.0
- **Styling:** SCSS modules + styled-components 6.0.0-rc.1
- **Component Documentation:** Storybook 7.5.0

---

## Code Metrics

### Source Code Statistics
- **TypeScript/JavaScript Files:** 415 files
- **Total Lines of Source Code:** ~14,068 lines
- **Component Files (.tsx):** 188 files
- **CSS/SCSS Files:** 75 files
- **Sanity Schema Files:** 72 files

---

## Testing Setup

### Current State
- **NO Jest/Vitest configuration** detected
- **NO Playwright/Cypress configuration** detected
- **NO Unit/E2E testing framework installed**

### Testing Infrastructure Present
- **Storybook:** Used for component documentation and visual testing
- **@storybook/testing-library:** For interaction testing within Storybook
- **Husky:** Git hooks configured via prepare script

---

## Styling Approach

### Primary Styling Methods

1. **CSS Modules (SCSS)**
   - File pattern: `*.module.scss`
   - Found: 10+ files throughout components
   - Used for component-scoped styling

2. **Global SCSS Stylesheets**
   - globals.scss: Main entry point with custom properties and resets
   - Design system partials: _colors.scss, _typography.scss, _spacing.scss, _mixins.scss, _misc.scss

3. **Styled Components**
   - Version: ^6.0.0-rc.1
   - Used for dynamic, CSS-in-JS styling
   - Alongside CSS modules for flexibility

### Design System Integration
- **Aleph Nought Design System** (@aleph/nought-sass-mixins, @aleph/stylelint-config-nought)
- Centralized color, typography, and spacing tokens
- No Tailwind CSS (uses custom SCSS system)

---

## Notable Architectural Decisions

1. **Route Groups Organization** - Clear separation between `(frontend)` and `(studio)`
2. **Headless CMS with Static Generation** - Sanity with ISR, cache invalidation API
3. **Dynamic Routing with Catch-All** - `[[...slug]]` for flexible content routing
4. **Unified Search with Algolia** - Real-time search indexing
5. **Monorepo Pattern** - Single repo contains frontend, CMS, component library
6. **Type Safety with Sanity Codegen** - Automatic TypeScript type generation
7. **Rich Content Building** - 40+ component blocks, Portable Text support
8. **Advanced Component Patterns** - Storybook, CSS modules, custom hooks
9. **Performance Optimizations** - Next.js Image optimization, bundle analyzer
10. **Preview & Draft Mode** - Sanity preview kit for real-time editing

---

**Summary:** helix-dot-com-next is a sophisticated, production-grade monorepo combining Next.js 14 frontend, integrated Sanity CMS, Storybook component docs, Algolia search, type-safe code generation, and custom SCSS design system. The architecture prioritizes developer experience, content flexibility, and performance.
