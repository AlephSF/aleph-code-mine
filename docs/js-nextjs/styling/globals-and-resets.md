---
title: "Global Styles and HTML Resets in globals.scss"
category: "styling"
subcategory: "global-styles"
tags: ["globals", "resets", "html", "baseline-styles", "accessibility"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Global Styles and HTML Resets in globals.scss

## Overview

All Next.js projects include `globals.scss` file that establishes baseline HTML element styling, box-sizing resets, and typography defaults. This file is imported once in application root layout and outputs actual CSS (unlike partial files which only contain variables/mixins).

**Purpose:** Normalize browser defaults, apply design system typography to HTML elements, establish global CSS custom properties, provide accessibility features like skip-links.

**Adoption:** 100% (all three projects have globals.scss with similar structure).

## File Location and Import

Global styles file located in centralized styles directory and imported by application root layout or _app.tsx.

```
app/
└── (frontend)/
    └── styles/
        └── globals.scss  ← Global styles (not a partial, no underscore)

app/
└── layout.tsx or _app.tsx  ← Import point
```

**Import in Next.js 13+ (App Router):**

```tsx
// app/layout.tsx
import './styles/globals.scss'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

**Import in Next.js 12 (Pages Router):**

```tsx
// pages/_app.tsx
import '../styles/globals.scss'

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
```

**Critical:** Global styles must be imported exactly once at application root to avoid duplicate CSS output.

## Universal Box-Sizing Reset

All projects apply `box-sizing: border-box` to every element via universal selector. This makes width/height calculations include padding and border, preventing common layout bugs.

```scss
// globals.scss (helix-dot-com-next)
* {
  box-sizing: border-box;
}
```

**Why border-box:** Default `content-box` makes element width = width + padding + border, causing unexpected overflow. With `border-box`, width includes padding and border, matching developer mental model.

**Adoption:** 100% (all three projects use `* { box-sizing: border-box; }`).

**Performance:** Universal selector has negligible performance impact in modern browsers.

## HTML Root Element Styling

HTML element receives base font size, scroll behavior, and viewport constraints.

```scss
// globals.scss (helix-dot-com-next)
html {
  max-width: 100vw;
  background-color: $coolgray-300;
  font-size: $root-font-size;  // 16px
  scroll-behavior: smooth;
}
```

**Font size:** Sets base 16px for rem calculations. All rem values calculated relative to this.

**Max-width:** Prevents horizontal overflow on narrow viewports.

**Scroll-behavior:** Enables smooth scrolling for anchor links. Disable if implementing custom scroll animations.

**Adoption:** 100% set `font-size`, 67% set `scroll-behavior: smooth`, 67% set background-color.

## Body Element Reset

Body element receives typography baseline via mixin, zero margin, and text color from design system.

```scss
// globals.scss (helix-dot-com-next)
@use "./typography" as *;
@use "./colors" as *;

body {
  @include bodyBase;  // Typography mixin
  margin: 0;
  color: $body-text-color;
}
```

**Pattern:** Body inherits base typography (font-family, font-size, line-height) from mixin. All other elements inherit from body unless overridden.

**Adoption:** 100% apply typography mixin to body, 100% reset margin to zero, 100% set text color via design token.

## Typography Element Defaults

All HTML heading and paragraph elements receive typography mixins for consistent baseline styling.

```scss
// globals.scss (helix-dot-com-next)
h1 { @include h1; }
h2 { @include h2; }
h3 { @include h3; }
h4 { @include h4; }
h5 { @include h5; }
h6 { @include h6; }

p {
  margin-top: 0;
  margin-bottom: to-rem(spacing.$p-margin-bottom);
}
```

**Pattern:** Mixins encapsulate font-size, line-height, font-family, font-weight, and responsive variants. Changing design requires only mixin update, not global CSS changes.

**Benefit:** Unstyled HTML renders with correct typography automatically. Markdown, CMS content, and third-party widgets inherit consistent typography.

**Adoption:** 100% apply typography mixins to headings, 100% reset paragraph margins.

## Link Element Styling

Links receive base styling via mixin that defines color, text-decoration, and interaction states.

```scss
// globals.scss (helix-dot-com-next)
a {
  @include link;
}
```

**Mixin contents (from _mixins.scss):**

```scss
@mixin link {
  color: $link-color;
  text-decoration: underline;
  transition: color 0.25s ease;

  &:visited {
    color: $link-visited-color;
  }

  &:hover {
    color: $link-hover-color;
  }

  &:focus-visible {
    outline: 2px solid $focus-ring-color;
  }
}
```

**Pattern:** Global link mixin provides sensible defaults. Component-specific links can override with `@include linkReset` to remove defaults before applying custom styling.

**Adoption:** 67% use link mixin (helix, kariusdx). Policy-node defines link styles inline in globals.scss.

## CSS Custom Properties (CSS Variables)

Policy-node uses CSS custom properties in `:root` for runtime theming. This pattern enables light/dark mode switching without SCSS recompilation.

```scss
// globals.scss (policy-node)
:root {
  --background: #{$color-white};
  --foreground: #{$color-hof};
}

// Dark mode support (commented out, ready for implementation)
// @media (prefers-color-scheme: dark) {
//   :root {
//     --background: #{$color-hof};
//     --foreground: #{$color-white};
//   }
// }

body {
  background: var(--background);
  color: var(--foreground);
}
```

**Syntax:** `#{$variable}` interpolates SCSS variable into CSS custom property value. Properties available at runtime for JavaScript access.

**Benefit:** Theme switching without recompilation. JavaScript can update `document.documentElement.style.setProperty('--background', newColor)` for dynamic themes.

**Adoption:** 33% (policy-node only). Helix and kariusdx use SCSS variables only (compile-time).

## Accessibility: Skip to Main Content

Helix includes skip-link for keyboard navigation to bypass repeated header/navigation content.

```scss
// globals.scss (helix-dot-com-next)
.skipToMainContentLink {
  @include body6;
  position: absolute;
  left: 50%;
  padding: to-rem(spacing.$spacing-small);
  transform: translate(-50%, -100%);  // Hidden above viewport
  transition: transform 0.3s;
  border: 2px solid $body-text-color;
  border-radius: 3px;
  background: $coolgray-800;
  z-index: 200;
  clip-path: polygon(0 0, 0 0, 0 0, 0 0);  // Hide from screen readers when off-screen

  &:focus {
    transform: translate(-50%, 0);  // Slide into view on focus
    clip-path: none;
  }
}
```

**HTML usage:**

```tsx
<a href="#main" className="skipToMainContentLink">
  Skip to main content
</a>

<main id="main">
  {/* Page content */}
</main>
```

**Pattern:** Link positioned off-screen by default, animates into view when focused via Tab key. Provides keyboard users shortcut to main content.

**Adoption:** 33% (helix only). Recommended for all projects for WCAG 2.1 compliance.

## Print Styles

Policy-node includes print-specific resets for generating clean PDFs.

```scss
// globals.scss (policy-node)
@media print {
  * {
    margin: 0;
    padding: 0;
  }

  body {
    background-color: white;
    color: black;
  }
}
```

**Pattern:** Strip colors, reset spacing, use black text on white background for printer-friendly output.

**Adoption:** 33% (policy-node only). Useful for policy documents, reports, invoices.

## Global Utility Classes

Kariusdx defines global utility classes for container and grid layouts.

```scss
// globals.scss (kariusdx-next)
.container {
  @include container;  // Max-width, centering, padding
}

.container-grid {
  @include container-grid;  // Container + CSS Grid setup
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Pattern:** Utility classes for common layout needs. `.sr-only` hides content visually while remaining accessible to screen readers.

**Adoption:** 67% define utility classes in globals (kariusdx, policy-node). Helix avoids global utility classes, preferring component-scoped styles.

**Recommendation:** Minimize global utilities - prefer component-scoped classes via CSS Modules for better encapsulation.

## List Reset

Some projects reset list styling globally for cleaner defaults.

```scss
// globals.scss (kariusdx-next)
ol,
ul {
  padding-left: rem(25px);
}
```

**Pattern:** Adjust list indentation for better visual hierarchy. Full reset (remove bullets/numbers) should be component-scoped, not global.

**Adoption:** 33% globally reset lists. Most projects reset lists per-component using `@include listReset` mixin.

## Font Loading and Performance

Kariusdx loads web fonts via @import in globals.scss.

```scss
// globals.scss (kariusdx-next)
@import url('https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,600;0,700;1,400;1,700&family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500&display=swap');
```

**Pattern:** Google Fonts loaded via CSS @import. `display=swap` enables FOUT (flash of unstyled text) to prevent invisible text during load.

**Adoption:** 33% (kariusdx only). Helix and policy-node use variable fonts via Next.js font optimization.

**Recommendation:** Use Next.js `next/font` for better performance (font subsetting, preloading, automatic optimization).

## Global Styles Structure Pattern

Standard structure observed across all three projects:

```scss
// globals.scss - standard pattern
@use "./colors" as *;
@use "./mixins" as *;
@use "./typography" as *;
@use "./spacing";

// 1. Universal resets
* {
  box-sizing: border-box;
}

// 2. Root element
html {
  font-size: $root-font-size;
  scroll-behavior: smooth;
}

// 3. Body
body {
  @include bodyBase;
  margin: 0;
  color: $body-text-color;
}

// 4. Typography elements
h1 { @include h1; }
h2 { @include h2; }
h3 { @include h3; }
p { margin-bottom: to-rem($p-margin-bottom); }

// 5. Links
a {
  @include link;
}

// 6. Accessibility features
.skipToMainContentLink { /* ... */ }
.sr-only { /* ... */ }

// 7. Global utilities (sparingly)
.container { @include container; }
```

**Order:** Resets → Root → Body → Typography → Links → Accessibility → Utilities

**Consistency:** All three projects follow this general structure with minor variations.

## What NOT to Put in Globals

Global styles should only include baseline HTML element styling. Avoid component-specific styles, complex layouts, or business logic styling.

**❌ Avoid in globals.scss:**
- Component-specific classes (`.button`, `.card`, `.hero`)
- Complex layout grids (use CSS Modules in components)
- Third-party library overrides (use `:global()` in component modules instead)
- Business logic styling (colors for "premium tier", "discounted items", etc.)

**✅ Appropriate for globals.scss:**
- HTML element resets (`html`, `body`, `*`)
- Typography baseline (`h1`, `h2`, `p`, `a`)
- Accessibility utilities (`.sr-only`, skip links)
- CSS custom properties for theming
- Universal box-sizing reset

**Guideline:** If style applies to a single component or page, use CSS Modules. If style applies to all HTML elements or provides global utility, use globals.scss.

## Import Order and Specificity

Globals.scss loaded first in application. Component CSS Modules loaded on-demand per page/component. This creates natural specificity hierarchy.

**Load order:**
1. globals.scss (application root import)
2. Component.module.scss (per-component imports)

**Specificity:** Component styles override globals due to CSS Modules hashing (higher specificity). Globals provide defaults, components provide overrides.

**Example:**

```scss
// globals.scss
a {
  color: blue;
  text-decoration: underline;
}

// Component.module.scss
.customLink {  // Becomes .customLink_abc123
  color: red;  // Overrides global link color
  text-decoration: none;  // Overrides global underline
}
```

**Result:** Global link styling applies everywhere except components that explicitly override with CSS Module classes.

## Adoption Statistics

**Global styles patterns:**

| Pattern | helix | kariusdx | policy-node | Adoption % |
|---------|-------|----------|-------------|------------|
| `* { box-sizing: border-box; }` | ✅ | ✅ | ✅ | 100% |
| Typography mixins on HTML elements | ✅ | ✅ | ✅ | 100% |
| Link mixin on `<a>` | ✅ | ✅ | ✅ | 100% |
| `scroll-behavior: smooth` | ✅ | ✅ | ❌ | 67% |
| CSS custom properties | ❌ | ❌ | ✅ | 33% |
| Skip-link accessibility | ✅ | ❌ | ❌ | 33% |
| Global utility classes | ❌ | ✅ | ✅ | 67% |
| Print styles | ❌ | ❌ | ✅ | 33% |

**Core patterns (100% adoption):** Box-sizing reset, typography mixins, link styling.

**Recommended additions:** Skip-link (accessibility), CSS custom properties (theming), print styles (if needed).

## Related Patterns

- **Design System:** See `design-system-structure.md` for partial organization imported by globals
- **Typography:** See `typography-mixin-system.md` for mixin details applied to HTML elements
- **CSS Modules:** See `css-modules-convention.md` for component-scoped styling that overrides globals
- **Accessibility:** See accessibility patterns for skip-link and screen reader utilities
