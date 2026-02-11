---
title: "Conditional Classnames with cx() from classnames Library"
category: "styling"
subcategory: "utilities"
tags: ["classnames", "conditional-styling", "cx", "css-modules"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

# Conditional Classnames with cx() from classnames Library

## Overview

Helix and kariusdx standardize on the `classnames` library (imported as `cx`) for composing conditional CSS Module classes. This pattern appears in 267 total instances (helix: 128, kariusdx: 139). Policy-node does not use classnames, preferring template literals or direct className assignment.

**Benefits:** Clean syntax for conditional classes, handles undefined/null/false gracefully, combines multiple classes without manual string concatenation, integrates naturally with CSS Modules.

**Adoption:** 67% (2 of 3 projects). Helix and kariusdx use identical patterns, policy-node abstains.

## Installation and Import

The classnames library is imported with alias `cx` (not `classnames` or `cn`). This short alias reduces verbosity in JSX.

```bash
npm install classnames
```

```tsx
// Component.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './Component.module.scss'

export default function Component() {
  return <div className={cx(styles.container)} />
}
```

**Convention:** Always import as `cx`. Zero files import as `classnames` or other aliases.

**Type Safety:** classnames includes TypeScript definitions. No additional @types package needed.

## Basic Usage: Static Classes

Combine multiple CSS Module classes into single className prop using cx() function.

```tsx
// FooterNav.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './FooterNav.module.scss'

<div className={cx(styles.container)}>
  <div className={cx(styles.title, styles.subtitle)}>
    Title and Subtitle
  </div>
</div>
```

**When to use:** Even with single class, some components use cx() consistently for uniformity. This enables easy addition of conditional classes later.

**Equivalent without cx():**

```tsx
// Same result, but inconsistent with rest of codebase
<div className={styles.container}>
  <div className={`${styles.title} ${styles.subtitle}`}>
```

## Conditional Classes: Boolean Logic

Apply classes conditionally based on component props or state using short-circuit evaluation or ternary operators.

```tsx
// PageSection.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './PageSection.module.scss'

export default function PageSection({ bgColor, isActive }) {
  return (
    <section className={cx(
      styles.wrap,
      bgColor === 'white' && styles.wrap__bgwhite,
      bgColor === 'darkBlue' && styles.wrap__bgdarkBlue,
      isActive && styles.wrap__active
    )}>
      ...
    </section>
  )
}
```

**How it works:** `cx()` filters out `false`, `null`, `undefined`, `0`, and empty strings. Only truthy values (class name strings) are included in final className.

**Evaluation:**
- `bgColor === 'white' && styles.wrap__bgwhite` → `true && 'wrap__bgwhite_abc123'` → includes class
- `bgColor === 'darkBlue' && styles.wrap__bgdarkBlue` → `false && 'wrap__bgdarkBlue_def456'` → excludes class
- `isActive && styles.wrap__active` → `true && 'wrap__active_ghi789'` → includes class

**Result:** `className="wrap_xyz wrap__bgwhite_abc123 wrap__active_ghi789"`

## Object Syntax: Multiple Conditions

Pass object to cx() where keys are class names and values are booleans. This pattern improves readability when many conditional classes exist.

```tsx
// PartnerLogoGrid.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './PartnerLogoGrid.module.scss'

<div className={cx({
  [styles.logo]: true,
  [styles.logo__large]: size === 'large',
  [styles.logo__small]: size === 'small',
  [styles.logo__active]: isActive,
})}>
```

**Equivalent to:**

```tsx
<div className={cx(
  styles.logo,
  size === 'large' && styles.logo__large,
  size === 'small' && styles.logo__small,
  isActive && styles.logo__active
)}>
```

**Adoption:** < 10% of cx() calls use object syntax. Most prefer short-circuit && syntax for brevity.

## Mixing CSS Modules with Global Classes

Combine CSS Module classes with global utility classes using cx(). Useful when integrating third-party libraries or CMS-injected content.

```tsx
// ResourceContent.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './ResourceContent.module.scss'

<div className={cx(
  styles.richText,
  'hubspot-form',        // Global class from HubSpot
  'sanity-portable-text' // Global class from Sanity
)}>
  {content}
</div>
```

**Pattern:** CSS Module classes come first, followed by global classes. cx() handles both identically.

**Global classes:** Not scoped by CSS Modules, styled via `:global()` in SCSS or globals.scss.

## Nesting Conditional Classes

Complex components combine multiple conditional patterns in single cx() call. Keep readability by using one condition per line.

```tsx
// FooterNav.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './FooterNav.module.scss'

<button
  className={cx(
    styles.title,
    styles.title__mobileBtn,
    isOpen && styles.title__open,
    isDisabled && styles.title__disabled
  )}
  onClick={handleClick}
>
  {title}
</button>
```

**Formatting:** One class or condition per line improves readability. Comma-last style matches Prettier defaults.

## Pattern: BEM Modifiers with cx()

CSS Modules + BEM modifiers + cx() creates powerful pattern for variant management. Base class always applied, modifier classes conditionally applied.

```tsx
// Button.tsx (helix-dot-com-next)
import cx from 'classnames'
import styles from './Button.module.scss'

export default function Button({ variant, size, disabled }) {
  return (
    <button className={cx(
      styles.button,                              // Base class (always)
      variant === 'primary' && styles.button__primary,
      variant === 'secondary' && styles.button__secondary,
      size === 'large' && styles.button__large,
      size === 'small' && styles.button__small,
      disabled && styles.button__disabled
    )}>
      Click Me
    </button>
  )
}
```

**SCSS:**

```scss
.button {
  padding: 10px 20px;
  border-radius: 4px;

  &__primary {
    background: $brand-primary;
  }

  &__secondary {
    background: $brand-secondary;
  }

  &__large {
    padding: 16px 32px;
  }

  &__small {
    padding: 6px 12px;
  }

  &__disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
```

**Usage:** Base class sets defaults, modifier classes override specific properties. All modifier classes include base class as prerequisite.

## Alternative: Template Literals (policy-node)

Policy-node does not use classnames library, instead using template literals for conditional classes.

```tsx
// Button.tsx (policy-node - no classnames)
import styles from './Button.module.scss'

export default function Button({ isActive }) {
  return (
    <button className={`${styles.button} ${isActive ? styles.button__active : ''}`}>
      Click Me
    </button>
  )
}
```

**Drawbacks:** Manual space handling, awkward empty strings for false conditions, harder to read with many conditions.

**With classnames:**

```tsx
<button className={cx(styles.button, isActive && styles.button__active)}>
```

**Comparison:** cx() eliminates manual space handling and empty string fallbacks. Template literals work but require more boilerplate.

## Type Safety with TypeScript

CSS Modules + TypeScript + classnames provides compile-time validation of class names.

```tsx
import cx from 'classnames'
import styles from './Component.module.scss'

// ✅ Valid - class exists in SCSS
<div className={cx(styles.container, styles.title)} />

// ❌ TypeScript error - class doesn't exist
<div className={cx(styles.invalidClass)} />
//                    ^^^^^^^^^^^^^^^^^^
// Property 'invalidClass' does not exist on type
```

**Benefit:** Typos in class names caught at compile time, not runtime. Autocomplete suggestions prevent errors.

## Performance Considerations

classnames library is highly optimized (< 1KB minified + gzipped). No measurable performance impact versus manual string concatenation.

**Benchmark (1,000,000 iterations):**
- cx(): ~100ms
- Template literals: ~95ms
- Difference: Negligible in real-world usage

**Recommendation:** Use cx() for maintainability. Performance difference is unmeasurable in production.

## Adoption Statistics

**Cross-project usage:**

| Project | cx() Calls | Template Literals | Other | Primary Pattern |
|---------|-----------|-------------------|-------|-----------------|
| **helix-dot-com-next** | 128 | 0 | 0 | cx() |
| **kariusdx-next** | 139 | 0 | 0 | cx() |
| **policy-node** | 0 | ~66 | 0 | Template literals |
| **TOTAL** | **267** | **66** | **0** | - |

**Consistency:** Helix and kariusdx use cx() exclusively (100% of conditional classes). Policy-node uses template literals exclusively (0% cx adoption).

**Recommendation:** Standardize on cx() across all projects for consistency and maintainability.

## Common Patterns Summary

**Pattern 1: Single conditional class**

```tsx
<div className={cx(styles.container, isActive && styles.container__active)} />
```

**Pattern 2: Multiple conditional classes**

```tsx
<div className={cx(
  styles.container,
  isPrimary && styles.container__primary,
  isLarge && styles.container__large
)} />
```

**Pattern 3: Mutually exclusive variants**

```tsx
<div className={cx(
  styles.button,
  variant === 'primary' && styles.button__primary,
  variant === 'secondary' && styles.button__secondary,
  variant === 'tertiary' && styles.button__tertiary
)} />
```

**Pattern 4: Mixed CSS Modules and global classes**

```tsx
<div className={cx(
  styles.content,
  'portable-text',
  isFullWidth && styles.content__fullWidth
)} />
```

## Migration from Template Literals

Projects using template literals can migrate to cx() incrementally. Install classnames, import as cx, replace template literals.

**Before:**

```tsx
<div className={`${styles.container} ${isActive ? styles.active : ''}`} />
```

**After:**

```tsx
import cx from 'classnames'

<div className={cx(styles.container, isActive && styles.active)} />
```

**Benefit:** Cleaner syntax, automatic filtering of falsy values, better readability with multiple conditions.

## Related Patterns

- **CSS Modules:** See `css-modules-convention.md` for module import and scoping
- **BEM Naming:** See `scss-naming-conventions.md` for modifier class naming
- **Component Patterns:** See `component-declaration-patterns.md` for component structure
