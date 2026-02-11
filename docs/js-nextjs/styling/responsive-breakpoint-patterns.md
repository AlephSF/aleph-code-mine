---
title: "Responsive Breakpoint Patterns with Desktop-First Approach"
category: "styling"
subcategory: "responsive-design"
tags: ["responsive", "breakpoints", "media-queries", "mixins", "mobile"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

# Responsive Breakpoint Patterns with Desktop-First Approach

## Overview

Next.js projects use breakpoint mixins for responsive styling with desktop-first approach. Helix and kariusdx define 593 total breakpoint mixin calls (helix: 291, kariusdx: 302), while policy-node uses raw @media queries sparingly (50 calls).

**Approach:** Desktop-first (styles default to desktop, override downward for smaller screens) using `media-breakpoint-down()` and `breakpoint(sm-down)` mixins. Zero mobile-first patterns observed.

**Adoption:** 67% (2 of 3 projects use mixins extensively). Helix and kariusdx standardize on mixin pattern, policy-node uses minimal responsive styling with raw @media.

## Breakpoint Scale Definition

All three projects define identical 5-breakpoint scale matching Bootstrap conventions. Breakpoints defined in `_spacing.scss` or `_variables.scss`.

```scss
// _spacing.scss (helix-dot-com-next)
$breakpoint-xs: 0;       // Extra small (mobile)
$breakpoint-sm: 576px;   // Small (large mobile)
$breakpoint-md: 768px;   // Medium (tablet)
$breakpoint-lg: 992px;   // Large (laptop)
$breakpoint-xl: 1200px;  // Extra large (desktop)
```

**Naming:** Breakpoint names (xs, sm, md, lg, xl) match Bootstrap and Tailwind conventions for familiarity.

**Values:** Identical across all three projects. No variation in breakpoint pixel values.

## Desktop-First Media Query Mixins

Helix uses `media-breakpoint-down()` mixin from `@aleph/nought-sass-mixins` library. This mixin generates max-width media queries for desktop-first responsive design.

```scss
// Component.module.scss (helix-dot-com-next)
@use "../../styles/mixins" as *;

.section {
  flex: 0 0 calc(25% - ($grid-column-gap * 3 / 4));  // Desktop default

  @include media-breakpoint-down(lg) {  // Max-width: 991px
    width: 100%;
  }

  @include media-breakpoint-down(sm) {  // Max-width: 575px
    padding: 16px;
  }
}
```

**Compiled output:**

```css
.section {
  flex: 0 0 calc(25% - 6px);
}

@media (max-width: 991px) {
  .section {
    width: 100%;
  }
}

@media (max-width: 575px) {
  .section {
    padding: 16px;
  }
}
```

**Pattern:** Desktop styles defined first without media query. Smaller breakpoints override via max-width queries (desktop-first cascade).

**Benefit:** Desktop experience is default, progressively simplified for smaller screens. Matches stakeholder priority (desktop users first).

## Breakpoint Mixin Variants

Helix includes both `media-breakpoint-down()` and `media-breakpoint-up()` for flexibility.

### media-breakpoint-down (Max-Width)

Apply styles at breakpoint and below (smaller screens). Most common pattern (95% of helix responsive code).

```scss
@include media-breakpoint-down(md) {
  // Applies when viewport ≤ 767px
}
```

**Usage:** Override desktop defaults for tablet and mobile.

### media-breakpoint-up (Min-Width)

Apply styles at breakpoint and above (larger screens). Rare in codebase (5% of responsive code).

```scss
@include media-breakpoint-up(lg) {
  // Applies when viewport ≥ 992px
}
```

**Usage:** Add enhancements for larger screens (only when base styles are mobile-first).

**Adoption:** 95% of breakpoint mixins use `down`, only 5% use `up`. Confirms desktop-first approach.

## Kariusdx Breakpoint Mixins

Kariusdx defines custom breakpoint mixin system with similar semantics but different syntax.

```scss
// _mixins.scss (kariusdx-next)
@mixin breakpoint($breakpoint) {
  @if $breakpoint == xs-down {
    @media (max-width: #{$breakpoint-sm - 1}) { @content; }
  }
  @if $breakpoint == sm-down {
    @media (max-width: #{$breakpoint-md - 1}) { @content; }
  }
  @if $breakpoint == md-down {
    @media (max-width: #{$breakpoint-lg - 1}) { @content; }
  }
  @if $breakpoint == lg-down {
    @media (max-width: #{$breakpoint-xl - 1}) { @content; }
  }
}
```

**Usage:**

```scss
.container {
  grid-column: 4 / 10;  // Desktop default

  @include breakpoint(sm-down) {
    grid-column: 2 / 6;
  }

  @include breakpoint(xs-down) {
    grid-column: 1 / -1;
  }
}
```

**Pattern:** Identical to helix semantics. Name suffix "-down" indicates max-width (desktop-first).

**Adoption:** 302 breakpoint mixin calls in kariusdx (vs 291 in helix). Both heavily rely on responsive mixins.

## Progressive Refinement Pattern

Desktop-first approach uses cascading overrides from large to small breakpoints. Each breakpoint refines previous styles.

```scss
// PageSection.module.scss (helix-dot-com-next)
.intro {
  @include columns(3, 11);  // Desktop: columns 3-11 (9 columns wide)

  @include media-breakpoint-down(md) {
    @include columns(1, -1);  // Tablet: full width
  }
}

.titleWrap {
  padding: to-rem(80px) to-rem(96px);  // Desktop: large padding

  @include media-breakpoint-down(lg) {
    padding: to-rem(64px) to-rem(38px);  // Laptop: medium padding
  }

  @include media-breakpoint-down(sm) {
    padding: to-rem(40px) to-rem(20px);  // Mobile: small padding
  }
}
```

**Pattern:** Start with desktop, progressively simplify layout and reduce spacing as viewport shrinks.

**Benefit:** Desktop experience is richest (multi-column, large spacing). Mobile experience is streamlined (single column, compact spacing).

## Touch Device Detection with Hover Media Query

Policy-node uses `@media (hover: hover)` to detect devices with hover capability. This prevents hover effects on touch devices where hover is non-functional.

```scss
// Button.module.scss (policy-node)
.Button {
  transition: transform $fast-curve-transition;

  @media (hover: hover) {
    &:hover {
      transform: scale(1.04);
    }
  }

  &:active {
    transform: scale(0.96);
  }
}
```

**How it works:** `hover: hover` matches devices with persistent hover capability (mice, trackpads). Excludes touch devices where hover is emulated on tap.

**Benefit:** Prevents confusing hover states on mobile. Active state (`:active`) works on both touch and mouse, so interactive feedback remains.

**Adoption:** 14 instances in policy-node. Helix and kariusdx do not use hover detection.

**Recommendation:** Use `@media (hover: hover)` for all hover effects to prevent touch device confusion.

## Print Styles with @media print

Policy-node includes print-specific styles for generating PDF reports.

```scss
.header {
  @include containerGrid;
  padding-top: space(3);
  padding-bottom: space(3);

  @media print {
    display: flex;
    justify-content: flex-end;
  }
}

.logoWordMark {
  display: none;

  @media print {
    display: block;

    svg {
      width: 100px;
      height: auto;
    }
  }
}
```

**Pattern:** Hide/show elements for print, simplify layout, adjust sizing for paper.

**Adoption:** < 5% of components include print styles. Policy-node only (policy-focused content requires printable reports).

## Responsive Grid Patterns

Both helix and kariusdx use CSS Grid with responsive column counts.

```scss
// Component.module.scss (helix-dot-com-next)
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);  // Desktop: 12 columns
  column-gap: $grid-column-gap;

  @include media-breakpoint-down(md) {
    grid-template-columns: repeat(8, 1fr);  // Tablet: 8 columns
  }

  @include media-breakpoint-down(sm) {
    grid-template-columns: repeat(4, 1fr);  // Mobile: 4 columns
  }
}

.item {
  grid-column: span 3;  // Desktop: 3 columns (4 items per row)

  @include media-breakpoint-down(md) {
    grid-column: span 4;  // Tablet: 4 columns (2 items per row)
  }

  @include media-breakpoint-down(sm) {
    grid-column: span 4;  // Mobile: 4 columns (1 item per row, full width)
  }
}
```

**Pattern:** Desktop uses 12-column grid (fine control), tablet uses 8 columns, mobile uses 4 columns (simpler layout).

**Benefit:** Consistent grid system across all breakpoints, items adapt column span to fit grid.

## Responsive Typography

Typography scales down at smaller breakpoints using separate mobile mixins.

```scss
// _typography.scss (helix-dot-com-next)
@mixin h1 {
  @include headerDesktopXl;  // Default: 64px/64px

  @include media-breakpoint-down(lg) {
    @include headerMobileLg;  // Mobile: 32px/40px
  }
}

@mixin h2 {
  @include headerDesktopLg;  // Default: 52px/56px

  @include media-breakpoint-down(lg) {
    @include headerMobileMd;  // Mobile: 30px/40px
  }
}
```

**Pattern:** Typography mixins include responsive variants internally. Components use `@include h1` and get responsive behavior automatically.

**Benefit:** Responsive typography centralized in design system. Components don't need per-breakpoint typography code.

## Common Responsive Patterns

**Pattern 1: Stack columns on mobile**

```scss
.columns {
  display: flex;
  gap: 24px;

  @include media-breakpoint-down(md) {
    flex-direction: column;
  }
}
```

**Pattern 2: Hide elements on mobile**

```scss
.desktopOnly {
  display: block;

  @include media-breakpoint-down(md) {
    display: none;
  }
}

.mobileOnly {
  display: none;

  @include media-breakpoint-down(md) {
    display: block;
  }
}
```

**Pattern 3: Reduce spacing on mobile**

```scss
.section {
  padding: to-rem(80px) to-rem(96px);

  @include media-breakpoint-down(sm) {
    padding: to-rem(40px) to-rem(20px);
  }
}
```

**Pattern 4: Full-width on mobile**

```scss
.container {
  max-width: $container-width;
  margin: 0 auto;

  @include media-breakpoint-down(sm) {
    max-width: 100%;
  }
}
```

## Policy-Node Raw Media Queries

Policy-node uses minimal responsive styling with raw @media queries instead of mixins.

```scss
.nav {
  @include spanColumns(10);

  @media (max-width: 768px) {
    position: fixed;
    inset: 0;
    background-color: $color-white;
    opacity: 0;
    visibility: hidden;

    &.nav__open {
      opacity: 1;
      visibility: visible;
    }
  }
}
```

**Pattern:** Raw pixel values instead of breakpoint variables. More verbose than mixin pattern.

**Adoption:** Only 50 @media queries total (vs 291-302 mixin calls in helix/kariusdx). Policy-node uses less responsive styling overall.

## Breakpoint Mixin vs Raw @media

**Mixin approach (helix/kariusdx):**

```scss
@include media-breakpoint-down(md) {
  // Styles
}
```

**Benefits:** Consistent breakpoint values, terser syntax, centralized breakpoint management, easy to change breakpoint values globally.

**Raw @media approach (policy-node):**

```scss
@media (max-width: 768px) {
  // Styles
}
```

**Benefits:** No dependency on mixin library, explicit pixel values, standard CSS syntax.

**Recommendation:** Use mixin approach for consistency and maintainability. Raw @media requires remembering exact pixel values.

## Adoption Statistics

**Responsive styling adoption:**

| Project | Breakpoint Mixins | Raw @media | Total Responsive Styles |
|---------|-------------------|-----------|------------------------|
| **helix-dot-com-next** | 291 | 5 | 296 |
| **kariusdx-next** | 302 | 0 | 302 |
| **policy-node** | 0 | 50 | 50 |
| **TOTAL** | **593** | **55** | **648** |

**Consistency:** Helix and kariusdx use mixins exclusively (98% mixin, 2% raw). Policy-node uses raw @media exclusively.

**Recommendation:** Standardize on mixin approach across all projects.

## Related Patterns

- **Design System:** See `design-system-structure.md` for breakpoint token definitions
- **Typography:** See `typography-mixin-system.md` for responsive typography patterns
- **Layout Mixins:** See `design-system-structure.md` for grid and column mixins
