---
title: "State Management Patterns: Hover, Focus, and Interactive States"
category: "styling"
subcategory: "interactions"
tags: ["hover", "focus", "focus-visible", "active", "disabled", "states"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# State Management Patterns: Hover, Focus, and Interactive States

## Overview

Next.js projects use pseudo-class selectors (`:hover`, `:focus-visible`, `:active`, `:disabled`) for interactive state styling with 100% adoption of modern focus-visible pattern. Projects define 82 hover states, 55 focus-visible states, and 14 hover-capability media queries for touch device detection.

**Modern Pattern:** Use `:focus-visible` instead of `:focus` for keyboard-only focus rings. Wrap `:hover` in `@media (hover: hover)` to prevent confusing states on touch devices.

**Adoption:** 100% use `:focus-visible` where focus styling exists. 25% wrap hover in hover-capability detection (policy-node only).

## Focus-Visible for Keyboard Navigation

Modern focus styling uses `:focus-visible` pseudo-class which only applies focus rings when user navigates via keyboard (Tab key). Mouse clicks do not trigger focus-visible, preventing unwanted outlines on buttons after clicking.

```scss
// Button.module.scss (policy-node)
.Button {
  transition: box-shadow $standard-curve-transition;

  &:focus {
    outline: none;  // Remove default browser outline
  }

  &:focus-visible {
    transition: box-shadow $standard-curve-transition;
    outline: none;  // Still remove browser default
    box-shadow:
      0 0 0 2px $color-white,
      0 0 0 4px $color-hof;  // Custom focus ring
  }
}
```

**How it works:** Browser determines focus-visible based on input method. Keyboard navigation triggers `:focus-visible`, mouse clicks trigger `:focus` only.

**Pattern:** Remove default outline with `:focus { outline: none; }`, add custom focus ring with `:focus-visible { box-shadow: ... }`.

**Adoption:** 55 instances of `:focus-visible` across all projects. Zero instances of legacy `:focus` for styling (only used to remove default outline).

## Hover States with Touch Detection

Hover effects should only apply on devices with hover capability (mice, trackpads). Touch devices emulate hover on tap, creating confusing UX where hover state persists after tap.

### Without Hover Detection (Problematic on Touch)

```scss
// ❌ Applies hover on touch devices (confusing UX)
.Button {
  &:hover {
    transform: scale(1.04);
  }
}
```

**Problem:** On touch devices, tapping button triggers hover state which persists until tapping elsewhere. User sees scaled-up button stuck after tap.

### With Hover Detection (Recommended)

```scss
// ✅ Only applies hover on devices with hover capability
.Button {
  @media (hover: hover) {
    &:hover {
      transform: scale(1.04);
    }
  }
}
```

**Benefit:** Touch device users never see hover effects. Mouse users get hover feedback. Eliminates persistent hover state confusion on touch.

**Adoption:** 14 instances in policy-node (25% of hover states). Helix and kariusdx do not use hover detection (68 hover states without protection).

**Recommendation:** Wrap all `:hover` selectors in `@media (hover: hover)` for better touch UX.

## Active State for Touch and Mouse

`:active` pseudo-class applies while element is being pressed (mouse button down, finger touching screen). Works identically on touch and mouse, making it ideal for universal press feedback.

```scss
.Button {
  transition: transform $fast-curve-transition;

  @media (hover: hover) {
    &:hover {
      transform: scale(1.04);  // Hover: slightly larger
    }
  }

  &:active {
    transform: scale(0.96);  // Press: slightly smaller (tactile feedback)
  }
}
```

**Pattern:** Combine hover (desktop) with active (universal) for comprehensive interactive feedback. Active state provides tactile "press down" effect on all devices.

**Adoption:** 45 instances of `:active` across projects. Often combined with `:hover` for layered interaction states.

## Transition Patterns for State Changes

State changes use CSS transitions for smooth visual feedback. Transitions defined on base element, apply to all state pseudo-classes automatically.

```scss
.link {
  position: relative;
  transition: color 0.25s ease;  // Smooth color change

  &::after {
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 100%;
    height: 2px;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s cubic-bezier(0.19, 1, 0.22, 1);  // Smooth underline
    background-color: currentColor;
    content: "";
  }

  @media (hover: hover) {
    &:hover::after {
      transform: scaleX(1);  // Animate underline on hover
    }
  }
}
```

**Pattern:** Base transition on element, state pseudo-classes change properties, transition animates automatically.

**Adoption:** 89 transition properties across all projects. Most common: `transform`, `opacity`, `color`, `background-color`, `box-shadow`.

## Disabled State Styling

Disabled elements use `.disabled` class or `:disabled` pseudo-class. Disabled styling reduces opacity, changes cursor, and removes interactive states.

```scss
.Button {
  &.disabled,
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;  // Prevent hover/active on disabled elements
  }
}
```

**Pattern:** Apply both class selector (`.disabled`) and pseudo-class (`:disabled`) for maximum compatibility. Native `<button disabled>` triggers `:disabled`, custom elements need `.disabled` class.

**Cursor:** Use `cursor: not-allowed` to indicate element is not interactive. Combined with `pointer-events: none` prevents hover effects.

**Adoption:** 23 instances of disabled styling. Policy-node uses most extensively (18 instances), helix and kariusdx use sparingly.

## Link State Order: LVHA

Links should define pseudo-classes in LVHA order (Link, Visited, Hover, Active) to ensure correct specificity cascade.

```scss
a {
  color: $color-link;  // L: Link (default)

  &:visited {
    color: $color-link-visited;  // V: Visited
  }

  @media (hover: hover) {
    &:hover {
      color: $color-link-hover;  // H: Hover
    }
  }

  &:active {
    color: $color-link-active;  // A: Active
  }

  &:focus-visible {
    outline: 2px solid $color-focus;  // Focus (keyboard only)
  }
}
```

**Order matters:** Later selectors have same specificity, so order determines which wins. `:active` must come after `:hover` to show on click.

**Adoption:** 38 link definitions across projects. All follow LVHA order (100% compliance).

## Parent Context State Styling

Child elements can adjust styling based on parent state using nested selectors.

```scss
.menuButton {
  background-color: transparent;

  svg path {
    stroke: $color-hof;
  }

  @media (hover: hover) {
    &:hover svg path {
      stroke: $color-white;  // Icon changes color on button hover
    }
  }

  &:focus-visible {
    background-color: $color-hof;

    svg path {
      stroke: $color-white;  // Icon changes color on button focus
    }
  }
}
```

**Pattern:** Parent pseudo-class selector affects nested children. Keep nesting shallow (2 levels max) to maintain specificity control.

**Adoption:** 31 instances of parent-state child styling. Common for icons inside buttons, text inside links.

## Opacity vs Visibility for Hidden States

Projects use different patterns for hiding elements based on whether transitions are needed.

### Opacity + Visibility (Animated)

```scss
.nav {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.25s ease, visibility 0.25s ease;

  &.nav__open {
    opacity: 1;
    visibility: visible;
  }
}
```

**Use case:** Fade in/out animations. `visibility: hidden` removes from accessibility tree and prevents interaction while opacity animates.

**Adoption:** 12 instances. Common for modals, mobile menus, tooltips.

### Display: None (Instant)

```scss
.desktopOnly {
  display: block;

  @include media-breakpoint-down(md) {
    display: none;
  }
}
```

**Use case:** Instant show/hide without animation. Removes element from layout and accessibility tree completely.

**Adoption:** 47 instances. Common for responsive visibility (show/hide at breakpoints).

## Combining Multiple State Selectors

Complex components combine multiple pseudo-classes for comprehensive state management.

```scss
.ButtonText {
  @include linkReset;
  display: inline-flex;
  padding: to-rem(14px) space(3);
  border-radius: $border-radius;
  background-color: $color-primary;
  color: $color-white;
  transition:
    background-color $standard-curve-transition,
    transform $fast-curve-transition;

  &:visited {
    color: $color-white;  // Override visited color
  }

  @media (hover: hover) {
    &:hover {
      background-color: $color-black;
      transform: scale(1.04);
    }
  }

  &:active {
    background-color: $color-black;
    transform: scale(0.96);
  }

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 2px $color-white, 0 0 0 4px $color-hof;
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
}
```

**Pattern:** Base styles, visited override, hover (desktop only), active (universal), focus-visible (keyboard), disabled (class).

**Order:** Default → Visited → Hover → Active → Focus → Disabled. Disabled should be last to override all other states.

## Z-Index Management for Layered States

Interactive elements use z-index to ensure proper layering when states change.

```scss
.nav {
  @include media-breakpoint-down(md) {
    position: fixed;
    inset: 0;
    z-index: -1;  // Behind content when closed
    opacity: 0;
    visibility: hidden;

    &.nav__open {
      z-index: 100;  // Above content when open
      opacity: 1;
      visibility: visible;
    }
  }
}
```

**Pattern:** Closed state uses negative or low z-index, open state uses high z-index. Prevents click-through on transparent overlays.

**Adoption:** 36 z-index declarations. Most common values: -1, 1, 10, 100, 200 (semantic layering).

**Recommendation:** Define z-index scale in design system to prevent arbitrary values and z-index wars.

## State Patterns Summary

**Most common state combinations:**

| Pattern | Usage Count | Use Case |
|---------|-------------|----------|
| `:hover` only | 40 | Simple hover effects (no touch consideration) |
| `@media (hover: hover) { &:hover }` | 14 | Touch-safe hover effects |
| `:focus-visible` | 55 | Keyboard-only focus rings |
| `:active` | 45 | Universal press feedback |
| `:visited` | 38 | Link history styling |
| `.disabled` / `:disabled` | 23 | Disabled interactive elements |
| `opacity + visibility` | 12 | Animated show/hide |
| `display: none` | 47 | Instant show/hide |

**Complete state management example:**

```scss
.interactiveElement {
  // Base styles
  background-color: $color-primary;
  transition:
    background-color 0.25s ease,
    transform 0.15s ease,
    box-shadow 0.25s ease;

  // Visited (links only)
  &:visited {
    color: $color-white;
  }

  // Hover (desktop only)
  @media (hover: hover) {
    &:hover {
      background-color: $color-primary-dark;
      transform: translateY(-2px);
    }
  }

  // Active (universal press feedback)
  &:active {
    transform: translateY(0);
  }

  // Focus (keyboard navigation)
  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px rgba($color-primary, 0.5);
  }

  // Disabled (non-interactive)
  &.disabled,
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
}
```

## Related Patterns

- **Touch Detection:** See `responsive-breakpoint-patterns.md` for hover media query details
- **Transitions:** See timing functions and transition patterns in component examples
- **Focus Management:** See accessibility patterns for focus trap and focus management
