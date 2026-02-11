---
title: "CSS Modules Convention with .module.scss Suffix"
category: "styling"
subcategory: "css-architecture"
tags: ["css-modules", "scss", "component-styles", "scoping"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "91%"
last_updated: "2026-02-11"
---

# CSS Modules Convention with .module.scss Suffix

## Overview

Next.js projects use CSS Modules with SCSS preprocessing for component-scoped styling. Files with `.module.scss` suffix are automatically treated as CSS Modules by Next.js, providing local scoping by default. This pattern is adopted in 194 out of 213 SCSS files (91% adoption) across all three Next.js codebases.

**Benefits:** Prevents global namespace pollution, enables component co-location, provides automatic class name hashing for uniqueness, eliminates CSS specificity wars.

**Scope:** Component-level styles only. Global styles, design tokens, and utility mixins use non-module .scss files.

## File Naming Convention

CSS Module files must use the `.module.scss` suffix and match their component file name exactly. This co-location pattern enables developers to find styles immediately adjacent to component logic.

```
ComponentName/
├── ComponentName.tsx
├── ComponentName.module.scss
└── index.ts
```

**Example from helix-dot-com-next (78 files, 92% modules):**

```
FooterNav/
├── FooterNav.tsx
├── FooterNav.module.scss
└── index.ts

PartnerLogoGrid/
├── PartnerLogoGrid.tsx
├── PartnerLogoGrid.module.scss
└── index.ts
```

**Example from policy-node (73 files, 90% modules):**

```
Button/
├── Button.tsx
├── Button.module.scss
└── index.ts

SiteHeader/
├── SiteHeader.tsx
├── SiteHeader.module.scss
└── index.ts
```

**Consistency:** All three projects follow identical naming conventions. Zero exceptions found across 194 module files.

## Import Pattern in Components

CSS Module files are imported as a default export with the alias `styles`. TypeScript automatically infers type-safe class names from the SCSS file structure.

```tsx
// FooterNav.tsx (helix-dot-com-next)
import styles from './FooterNav.module.scss'

export default function FooterNav({ sections }) {
  return (
    <nav className={styles.nav}>
      <div className={styles.navList}>
        {sections.map(section => (
          <div key={section._key} className={styles.section}>
            <h4 className={styles.title}>{section.title}</h4>
          </div>
        ))}
      </div>
    </nav>
  )
}
```

**Type Safety:** Next.js TypeScript plugin provides autocomplete for `styles.*` properties, preventing typos and dead CSS references.

## Component SCSS File Structure

CSS Module files import design tokens via `@use` directives (modern SCSS) and define component-scoped class names. All class names are automatically scoped to avoid global conflicts.

```scss
// FooterNav.module.scss (helix-dot-com-next)
@use "sass:math";
@use "../../styles/colors" as *;
@use "../../styles/mixins" as *;
@use "../../styles/spacing" as spacing;
@use "../../styles/typography" as *;

.nav {
  @include media-breakpoint-down(lg) {
    margin-top: to-rem(-$menu-button-padding-v);
  }
}

.navList {
  @include media-breakpoint-up(lg) {
    display: flex;
    flex-wrap: wrap;
    column-gap: $grid-column-gap;
  }
}

.section {
  flex: 0 0 calc(25% - ($grid-column-gap * 3 / 4));

  @include media-breakpoint-down(lg) {
    width: 100%;
  }
}

.title {
  @include body7;
  color: $charcoal-300;
  text-align: left;
}
```

**Pattern:** Import design tokens at top, define local classes below. Classes use camelCase naming (see scss-naming-conventions.md).

## What Goes in CSS Modules vs Global Styles

CSS Modules are exclusively for component-scoped styles. Design tokens, global resets, and shared utilities belong in non-module SCSS files.

**CSS Modules (.module.scss) - 194 files:**
- Component-specific class names
- Component layout and structure
- Component-specific state variations
- Component-specific responsive behavior

**Global SCSS (no .module suffix) - 19 files:**
- Design tokens: `_colors.scss`, `_typography.scss`, `_spacing.scss`
- Utility mixins: `_mixins.scss`
- Global resets: `globals.scss`
- HTML element defaults: `h1 { @include h1; }`

**Example structure:**

```
styles/
├── _colors.scss           # Design tokens (not a module)
├── _typography.scss       # Typography mixins (not a module)
├── _spacing.scss          # Spacing tokens (not a module)
├── _mixins.scss           # Utility mixins (not a module)
└── globals.scss           # Global resets (not a module)

components/
└── Button/
    ├── Button.tsx
    └── Button.module.scss  # Component styles (IS a module)
```

**Rule:** If styles apply to a single component, use CSS Modules. If styles are reusable across components, use design tokens or mixins.

## Escaping CSS Modules Scope with :global()

CSS Modules provide `:global()` syntax for targeting third-party library classes or HTML elements that bypass module scoping. This is used sparingly (31 files, 15% of modules) for integrations like HubSpot forms or design system library components.

```scss
// PageSection.module.scss (kariusdx-next)
.wrap {
  &__bg_darkBlue {
    background-color: $brand-primary;

    // Target third-party class from HubSpot
    :global(.portableTextButton) {
      border-color: $brand-secondary-light;
      background-color: $brand-secondary-light;

      &:hover,
      &:focus-visible {
        border-color: $brand-primary;
        background-color: $brand-primary;
      }
    }
  }
}
```

**Usage:** 15% of CSS Module files use `:global()` for third-party integration. Zero files use `:global()` for regular component styling.

**Guideline:** Use `:global()` only when targeting classes outside your control (libraries, CMSs, embedded widgets). Never use `:global()` to work around module scoping - restructure your CSS instead.

## CSS Modules Features Not Used

CSS Modules support composition via `composes:` keyword, but zero files across all three projects use this feature. Composition allows sharing styles between classes without duplicating CSS.

```scss
/* NOT USED - composition pattern found in 0 files */
.button {
  padding: 10px 20px;
  border-radius: 4px;
}

.primaryButton {
  composes: button;
  background-color: blue;
}
```

**Reason for non-adoption:** Projects prefer SCSS mixins for style reuse instead of CSS Modules composition. Mixins provide more flexibility and work across module boundaries.

## Migration Notes

Helix and policy-node migrated to modern `@use` syntax (91-96% adoption), while kariusdx remains on legacy `@import` (84% of files). Both work identically with CSS Modules - the difference is in SCSS module resolution, not CSS Module behavior.

**See also:** `scss-use-over-import.md` for details on `@use` vs `@import` migration.

## Adoption Statistics

**Cross-project summary:**

| Project | Total SCSS | CSS Modules | CSS Module % |
|---------|------------|-------------|--------------|
| helix-dot-com-next | 78 | 72 | 92% |
| kariusdx-next | 62 | 56 | 90% |
| policy-node | 73 | 66 | 90% |
| **AVERAGE** | **213** | **194** | **91%** |

**Consistency:** All three projects standardized on `.module.scss` suffix with 90-92% adoption. Non-module files are exclusively design tokens and global styles.

## Related Patterns

- **Design System Structure:** See `design-system-structure.md` for organizing non-module SCSS files
- **Naming Conventions:** See `scss-naming-conventions.md` for class naming patterns inside modules
- **Conditional Classes:** See `conditional-classnames.md` for composing multiple CSS Module classes dynamically
- **Modern SCSS:** See `scss-use-over-import.md` for `@use` directive usage in modules
