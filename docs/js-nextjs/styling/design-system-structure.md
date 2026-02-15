---
title: "Design System Structure with Partial SCSS Files"
category: "styling"
subcategory: "design-tokens"
tags: ["design-system", "scss-partials", "design-tokens", "theming"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Design System Structure with Partial SCSS Files

## Overview

Next.js projects organize design tokens and global styles using SCSS partial files (prefixed with underscore) in a centralized `styles/` directory. This pattern achieves 100% adoption across all three codebases with identical file naming and structure conventions.

**Benefits:** Single source of truth for design tokens, prevents hard-coded values in components, enables theme consistency, simplifies design updates across entire application.

**Architecture:** Partial files contain only variables and mixins (no CSS output). Component files import only needed partials via `@use` directives, keeping bundle sizes minimal.

## Standard Directory Structure

All three projects use identical partial file naming and organization. The `styles/` directory contains design tokens that components import on-demand.

```
app/
└── (frontend)/
    └── styles/
        ├── _colors.scss       # Color palette + semantic aliases
        ├── _typography.scss   # Typography mixins + font tokens
        ├── _spacing.scss      # Spacing scale + layout tokens
        ├── _mixins.scss       # Utility mixins (resets, helpers)
        ├── _variables.scss    # Misc variables (optional)
        └── globals.scss       # Global resets (not a partial)
```

**Naming Convention:** Partials prefixed with underscore (\_colors.scss), non-partials without (globals.scss). SCSS compiler skips compiling partials directly - they are only imported by other files.

**Example from policy-node:**

```
src/
└── styles/
    ├── _colors.scss
    ├── _typography.scss
    ├── _spacing.scss
    ├── _mixins.scss
    ├── _variables.scss
    └── globals.scss
```

**Consistency:** Zero variation in partial file names across 3 projects. 100% adoption of this structure.

## Numbered Scale Color Pattern

Numbered scales provide light-to-dark progression (100 = darkest, 800 = lightest). Mirrors design systems like Tailwind and Material UI.

```scss
// _colors.scss (helix)
$pink-100:#92374f;$pink-200:#c34969;$pink-300:#f45b83;$pink-400:#f67c9c;
$pink-500:#f89db5;$pink-600:#fbbdcd;$pink-700:#fddee6;$pink-800:#feeff3;
$charcoal-100:#272727;$charcoal-200:#2c2d2c;$charcoal-300:#373837;
$charcoal-400:#5f605f;$charcoal-500:#878887;$charcoal-600:#afafaf;
$charcoal-700:#d7d7d7;$charcoal-800:#ebebeb;
// Semantic aliases
$body-text-color:$charcoal-300;
$link-color-on-dark:$white;
$link-hover-color-on-dark:$blue-500;
```

**Pattern:** Define base scale, then create semantic aliases. Components import semantic aliases, never raw scale values.

## Semantic Naming Color Pattern

Semantic naming uses descriptive color names instead of numbers. Improves readability but requires memorizing hierarchy.

```scss
// _colors.scss (policy-node)
$color-rausch:#ff385c;$color-hof:#222;$color-foggy:#6a6a6a;
$color-suva:#929292;$color-deco:#ddd;$color-white:#fff;
// Contextual aliases
$color-text:$color-hof;$color-primary:$color-hof;$color-link:$color-hof;
$color-link-active:$color-foggy;$color-link-visited:$color-foggy;
$color-link-focused:$color-white;$color-link-focused-bg:$color-charcoal;
```

**Pattern:** Base colors have memorable names (foggy, rausch, hof), contextual aliases describe usage. Components use contextual aliases.

**Comparison:** Numbered scales provide clear hierarchy but less memorable names. Semantic naming improves readability but obscures light-to-dark relationships. Both achieve same goal: abstraction layer between raw hex and component usage.

## Typography Mixin System

All three projects define comprehensive typography mixin libraries with desktop and mobile variants.

```scss
// _typography.scss (helix)
@use "sass:math";
$root-font-size:16px;
@function to-rem($px){$r:math.div($px,$root-font-size);@return #{$r}rem;}
@mixin fontSize($f:16,$l:24){font-size:to-rem($f);line-height:to-rem($l);}
@mixin body1(){@include fontSize(20,32);font-family:$font-family-tt-norms;font-weight:344;}
@mixin body2(){@include fontSize(18,28);font-family:$font-family-tt-norms;font-weight:344;}
@mixin headerDesktopLg(){@include fontSize(52,56);font-family:$font-family-tt-norms;font-weight:620;}
@mixin headerMobileLg(){@include fontSize(32,40);font-family:$font-family-tt-norms;font-weight:620;}
```

**Pattern:** Define base fontSize mixin, create semantic typography mixins (body1, h1), apply in components and globals.scss.

## Global Typography Application

Typography mixins applied to HTML elements in `globals.scss` establish baseline text styling without requiring classes.

```scss
// globals.scss (helix)
@use "./typography" as *;
body{@include bodyBase;margin:0;color:$body-text-color;}
h1{@include h1;}h2{@include h2;}h3{@include h3;}
h4{@include h4;}h5{@include h5;}h6{@include h6;}
p{margin-top:0;margin-bottom:to-rem($p-margin-bottom);}
```

**Benefit:** All unstyled HTML renders with correct typography by default. Components can override with different typography mixins as needed.

## Spacing Tokens (_spacing.scss)

Spacing partials define the spacing scale (margins, paddings, gaps) and layout constants (container widths, breakpoints). Components reference these tokens instead of hard-coding pixel values.

```scss
// _spacing.scss (helix-dot-com-next)

// Container layout
$container-width: 1174px;
$container-padding: 96px;
$container-padding-md: 38px;
$container-padding-sm: 20px;

// Grid system
$grid-column-gap: 24px;
$grid-column-gap-md: 16px;

// Spacing scale
$spacing-xx-large: 80px;
$spacing-x-large: 64px;
$spacing-large: 40px;
$spacing-medium: 32px;
$spacing-standard: 24px;
$spacing-small: 16px;
$spacing-x-small: 8px;

// Responsive breakpoints
$breakpoint-xs: 0;
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;

// Component-specific spacing
$p-margin-bottom: 24px;
$page-section-intro-margin-bottom: 40px;
$page-section-title-margin-bottom: 24px;
```

**Pattern:** Define base spacing scale (xx-large to x-small), container constants, breakpoints, then component-specific tokens that reference base scale.

**Usage in components:**

```scss
@use "../../styles/spacing" as s;

.container {
  padding: to-rem(s.$spacing-large);
  margin-bottom: to-rem(s.$page-section-intro-margin-bottom);
}
```

**Namespace:** Spacing tokens imported with `as s` alias to avoid name collisions with other partials.

## Reset Mixins

Reset mixins remove default browser styles from HTML elements, providing blank slate for custom styling.

```scss
// _mixins.scss (helix)
@mixin buttonReset{padding:0;border:0;background:transparent;color:inherit;font-family:inherit;cursor:pointer;appearance:none;}
@mixin listReset{margin:0;padding:0;list-style:none;}
@mixin linkReset{color:inherit;text-decoration:none;}
```

**Usage:**

```scss
.customButton{@include buttonReset;background-color:$brand-primary;padding:12px 24px;}
```

## Layout Mixins

Layout mixins encapsulate common responsive patterns and grid behaviors.

```scss
@mixin pageSectionWrap($s:"md"){padding-top:to-rem(80px);padding-bottom:to-rem(80px);overflow:hidden;@include media-breakpoint-down($s){padding-top:to-rem(40px);padding-bottom:to-rem(40px);}}
@mixin columns($start,$end){grid-column:#{$start}/#{$end};}
```

**Pattern:** Mixins accept parameters for flexibility, include responsive variants, eliminate repetitive code.

## Visual Effect Mixins

Effect mixins define common UI patterns like shadows, animations, and hover states.

```scss
@mixin dropShadow{box-shadow:5px 15px 46px 0 rgba(0 0 0/15%);backdrop-filter:blur(13.59px);}
@mixin underlineTransitionStartState($bg:inherit){position:relative;&::after{position:absolute;bottom:-2px;left:0;width:100%;height:2px;transform:scaleX(0);transform-origin:left;transition:transform .25s cubic-bezier(.19,1,.22,1);background-color:$bg;content:"";}&:hover,&:focus,&:active{&::after{transform:scaleX(1);}}}
```

**Usage:** Complex visual effects encapsulated in mixins prevent duplication and ensure consistency.

## Global Styles (globals.scss)

Unlike partials, `globals.scss` is compiled directly and outputs actual CSS. This file applies HTML resets, typography baseline, and accessibility features.

```scss
// globals.scss (helix-dot-com-next)
@use "./colors" as *;
@use "./mixins" as *;
@use "./typography" as *;
@use "./spacing";

// Universal box-sizing
* {
  box-sizing: border-box;
}

// HTML root settings
html {
  max-width: 100vw;
  background-color: $coolgray-300;
  font-size: $root-font-size;
  scroll-behavior: smooth;
}

// Body defaults
body {
  @include bodyBase;
  margin: 0;
  color: $body-text-color;
}

// Typography baseline
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

a {
  @include link;
}

// Accessibility: skip to main content link
.skipToMainContentLink {
  @include body6;
  position: absolute;
  left: 50%;
  padding: to-rem(spacing.$spacing-small);
  transform: translate(-50%, -100%);
  transition: transform 0.3s;
  border: 2px solid $body-text-color;
  border-radius: 3px;
  background: $coolgray-800;
  z-index: 200;

  &:focus {
    transform: translate(-50%, 0);
  }
}
```

**Pattern:** Import all partials, apply resets, establish typography baseline, add accessibility features.

## Import Strategy in Components

Component `.module.scss` files import only the partials they need. Modern `@use` syntax enables namespace control and prevents variable pollution.

```scss
// Button.module.scss (policy-node)
@use "../../styles/colors" as *;     // Import all color tokens
@use "../../styles/typography" as *; // Import all typography mixins
@use "../../styles/spacing" as *;    // Import spacing with namespace
@use "../../styles/mixins" as *;     // Import all utility mixins

.Button {
  @include focusVisibleRemove;  // From mixins
  background-color: $color-primary;  // From colors
  padding: to-rem(14px) space(3);    // From spacing + mixins
}
```

**Namespacing:** `as *` imports all members into global namespace. `as s` imports with namespace (access via `s.$token-name`). Use namespaces when names might conflict.

**Performance:** Importing partials has zero runtime cost - SCSS processes imports at build time and only includes used styles in final CSS bundle.

## Adoption Statistics

**Design System Partial Files:**

| Partial | helix | kariusdx | policy | Adoption % |
|---------|-------|----------|--------|------------|
| _colors.scss | ✅ | ✅ | ✅ | 100% |
| _typography.scss | ✅ | ✅ | ✅ | 100% |
| _spacing.scss | ✅ | ✅ | ✅ | 100% |
| _mixins.scss | ✅ | ✅ | ✅ | 100% |
| globals.scss | ✅ | ✅ | ✅ | 100% |
| _variables.scss | ❌ | ✅ | ✅ | 67% |

**Consistency:** Core four partials (colors, typography, spacing, mixins) have 100% adoption. Helix merges variables into other partials instead of separate \_variables.scss file.

## Related Patterns

- **CSS Modules:** See `css-modules-convention.md` for how components import these partials
- **Modern SCSS:** See `scss-use-over-import.md` for `@use` vs `@import` import strategy
- **Typography Mixins:** See `typography-mixin-system.md` for detailed typography patterns
- **Color Tokens:** See `color-token-strategies.md` for numbered vs semantic color naming
