---
title: "SCSS Modules Styling Pattern"
category: "component-patterns"
subcategory: "styling"
tags: ["scss", "css-modules", "classnames", "design-system"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

## Module Naming Convention

Component styles use SCSS modules with the `.module.scss` extension. Style files live in the same folder as the component and follow the naming pattern `ComponentName.module.scss`. All three analyzed codebases use SCSS modules exclusively (190 SCSS module files, zero usage of Tailwind or CSS-in-JS). Module naming must match the component name exactly to maintain clear file associations.

```
Button/
├── Button.tsx
├── Button.module.scss    # Matches component name
└── index.ts
```

Next.js automatically scopes CSS module classes to the component, preventing global namespace collisions. Styles defined in `.module.scss` files are locally scoped by default.

## Import and Usage Pattern

SCSS modules import using a default import aliased to `styles`. The `styles` object contains all class names defined in the SCSS file as properties. Class names in SCSS use camelCase (or BEM syntax), and JavaScript accesses them via property notation.

```typescript
import styles from './Button.module.scss'

export default function Button({ text, link }: ButtonProps) {
  return (
    <Link href={link} className={styles.Button}>
      <span className={styles.text}>{text}</span>
    </Link>
  )
}
```

SCSS file defines classes using standard CSS syntax:

```scss
.Button {
  padding: 1rem 2rem;
  background: var(--color-primary);
}

.text {
  font-size: 1rem;
  font-weight: 600;
}
```

## Classnames Library as cx Alias

Components use the `classnames` library for conditional class application and combining multiple classes. The library imports with the alias `cx` universally across all three codebases (100% adoption). Never import as `classNames` or `cn` - always use `cx` to maintain consistency.

```typescript
import cx from 'classnames'
import styles from './Button.module.scss'

export default function Button({
  text, buttonStyle = 'solid', size = 'large', className
}: ButtonProps) {
  const linkClasses = cx(
    styles.Button,
    styles[buttonStyle],     // Dynamic class based on prop
    styles[size],            // Dynamic class based on prop
    className,               // External className prop
  )

  return <Link href={link} className={linkClasses}>{text}</Link>
}
```

### Conditional Classes with Object Syntax

The `cx` function accepts object notation for conditional classes where keys are class names and values are boolean expressions:

```typescript
const linkClasses = cx(
  styles.Button,
  {
    [styles.Button__download]: download,           // Apply if download is true
    [styles.text__long]: shortText,                // Apply if shortText exists
  },
  className,
)
```

## Design System Variables

SCSS modules reference design system variables for colors, typography, and spacing. Variables define values in a centralized design system file (typically `_variables.scss`, `_colors.scss`, `_typography.scss`) and components import these files or reference CSS custom properties.

```scss
// Component styles reference design system
@import '../../styles/variables';

.Button {
  padding: $spacing-md $spacing-lg;
  background: $color-primary;
  font-family: $font-family-base;
  font-size: $font-size-md;
  border-radius: $border-radius-sm;
}
```

CSS custom properties (CSS variables) alternative:

```scss
.Button {
  background: var(--color-primary);
  font-family: var(--font-family-base);
  padding: var(--spacing-md) var(--spacing-lg);
}
```

All three codebases maintain design system files with standardized naming: `_colors.scss`, `_typography.scss`, `_spacing.scss`.
