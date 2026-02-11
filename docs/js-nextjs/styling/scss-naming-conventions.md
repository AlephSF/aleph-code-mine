---
title: "SCSS Naming Conventions: camelCase with BEM Modifiers"
category: "styling"
subcategory: "naming-conventions"
tags: ["scss", "bem", "camelCase", "naming", "css-modules"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# SCSS Naming Conventions: camelCase with BEM Modifiers

## Overview

Next.js projects use camelCase for base CSS class names combined with BEM-style double-underscore modifiers for variants. This hybrid naming convention achieves 100% consistency across all three codebases with zero exceptions found in 194 CSS Module files.

**Benefits:** camelCase enables natural JavaScript property access (`styles.className` vs `styles['class-name']`), BEM modifiers provide clear hierarchy and variant relationships, CSS Modules scoping eliminates need for block prefixes.

**Scope:** Component CSS Modules only. Design token variables use kebab-case (`$body-text-color`), but component class names use camelCase exclusively.

## Base Class Naming: camelCase

All CSS class names use camelCase convention where first word is lowercase and subsequent words are capitalized. This pattern enables dot notation access in JavaScript/TypeScript.

```scss
// FooterNav.module.scss (helix-dot-com-next)
.nav { }           // Base element
.navList { }       // Compound word: camelCase
.section { }       // Single word: lowercase
.title { }         // Single word: lowercase
.titleWrap { }     // Compound word: camelCase
.linkItem { }      // Compound word: camelCase
.subheader { }     // Compound word: camelCase
```

**Usage in components:**

```tsx
import styles from './FooterNav.module.scss'

<nav className={styles.nav}>
  <div className={styles.navList}>
    <div className={styles.section}>
      <h4 className={styles.title}>...</h4>
    </div>
  </div>
</nav>
```

**TypeScript benefit:** Autocomplete and type-checking work naturally with dot notation. Invalid class names are caught at compile time.

### Forbidden Patterns

Projects avoid kebab-case, snake_case, and PascalCase for CSS class names. These patterns either break JavaScript dot notation or conflict with React component naming.

```scss
/* ❌ NEVER USE - kebab-case breaks dot notation */
.nav-list { }
.title-wrap { }

/* ❌ NEVER USE - snake_case not idiomatic in CSS */
.nav_list { }
.title_wrap { }

/* ❌ NEVER USE - PascalCase conflicts with components */
.NavList { }
.TitleWrap { }

/* ✅ CORRECT - camelCase works with dot notation */
.navList { }
.titleWrap { }
```

**Consistency:** Zero kebab-case or snake_case class names found in 194 CSS Module files. 100% camelCase adoption.

## BEM Modifiers: Double Underscore

Class variants use BEM (Block Element Modifier) convention with double underscore (`__`) to indicate relationship to base class. CSS Modules eliminate need for block prefixes since all classes are automatically scoped.

### Element Modifiers (State or Type Variants)

Element modifiers describe different states or types of the base element. The double underscore signals this class modifies the base behavior.

```scss
// FooterNav.module.scss (helix-dot-com-next)
.title {
  @include body7;
  color: $charcoal-300;
  text-align: left;

  // Modifier: mobile button variant
  &__mobileBtn {
    @include buttonReset;
  }
}

// Compiled class names (CSS Modules adds hash):
// .title_abc123
// .title__mobileBtn_def456
```

**Usage:**

```tsx
<button className={cx(styles.title, styles.title__mobileBtn)}>
  {section.title}
</button>
```

**Pattern:** Base class (`.title`) establishes defaults. Modifier class (`.title__mobileBtn`) applied alongside base class to override specific properties.

### Layout Modifiers

Layout modifiers indicate positional or layout variations of base element. Common pattern for components with multiple layout options.

```scss
// PageSection.module.scss (helix-dot-com-next)
.textWrap {
  display: flex;
  flex-direction: column;
  gap: 24px;

  // Modifier: image positioned left
  &__imgleft {
    flex-direction: row;
  }

  // Modifier: image positioned right
  &__imgright {
    flex-direction: row-reverse;
  }
}
```

**Usage:**

```tsx
<div className={cx(
  styles.textWrap,
  imagePosition === 'left' && styles.textWrap__imgleft,
  imagePosition === 'right' && styles.textWrap__imgright
)}>
  ...
</div>
```

**Pattern:** Base class defines default layout (column). Modifier classes change flex direction based on image position.

### Size Modifiers

Size modifiers provide variant sizing for components. Common pattern for buttons, icons, and typography.

```scss
// Button.module.scss (policy-node)
.ButtonIcon {
  width: to-rem(48px);
  height: to-rem(48px);

  // Modifier: large variant
  &__large {
    width: space(8);
    height: space(8);

    svg {
      width: space(4);
      height: space(4);
    }
  }

  // Modifier: small variant
  &__small {
    width: space(4);
    height: space(4);

    svg {
      width: space(2);
      height: space(2);
    }
  }
}
```

**Usage:**

```tsx
<button className={cx(
  styles.ButtonIcon,
  size === 'large' && styles.ButtonIcon__large,
  size === 'small' && styles.ButtonIcon__small
)}>
  <IconComponent />
</button>
```

**Pattern:** Base class defines default size. Modifier classes override dimensions for specific sizes. Always applied alongside base class.

### Context Modifiers

Context modifiers adapt element styling based on surrounding context or theme. Common pattern for navigation items, links, and layout elements.

```scss
// SiteHeader.module.scss (policy-node)
.menuItem {
  padding: space(2);
  color: $color-hof;

  // Modifier: secondary navigation context
  &__secondaryNav {
    padding: space(1);
    font-size: to-rem(14px);
    color: $color-foggy;
  }
}
```

**Usage:**

```tsx
<li className={cx(
  styles.menuItem,
  isSecondaryNav && styles.menuItem__secondaryNav
)}>
  {item.title}
</li>
```

**Pattern:** Base class defines primary nav styling. Modifier adapts styling for secondary navigation context.

## Parent Context Styling

CSS Modules enable parent-aware styling where child elements adjust based on parent modifier class. This pattern creates theme variations without duplicating child selectors.

```scss
// PageSection.module.scss (helix-dot-com-next)
.wrap {
  &__bgdarkBlue {
    background-color: $darkblue-100;
  }
}

.title {
  @include pageSectionHeader;

  // Adjust when inside dark background parent
  .wrap__bgdarkBlue & {
    color: $white;
  }
}

.text {
  @include pageSectionIntroBody;

  // Adjust when inside dark background parent
  .wrap__bgdarkBlue & {
    color: $white;

    a {
      @include linkOnDark;
    }
  }
}
```

**Usage:**

```tsx
<div className={cx(styles.wrap, isDarkTheme && styles.wrap__bgdarkBlue)}>
  <h2 className={styles.title}>Title</h2>
  <p className={styles.text}>Text with <a href="#">link</a></p>
</div>
```

**Pattern:** Parent modifier (`.wrap__bgdarkBlue`) controls background. Children use `.wrap__bgdarkBlue &` selector to adapt their own styling when inside that parent. CSS Modules scoping makes this safe - no global namespace pollution.

## SCSS Nesting with Parent Selector

SCSS parent selector (`&`) enables defining modifiers directly nested under base class. This keeps related styles grouped together and reduces repetition.

```scss
// Before nesting (repetitive):
.button {
  padding: 10px 20px;
}

.button__primary {
  background-color: blue;
}

.button__secondary {
  background-color: gray;
}

// After nesting (DRY):
.button {
  padding: 10px 20px;

  &__primary {
    background-color: blue;
  }

  &__secondary {
    background-color: gray;
  }
}
```

**Compiled output:** Identical to non-nested version. `&__primary` compiles to `.button__primary`. SCSS nesting is purely organizational - final CSS is flat.

**Guideline:** Nest modifiers (single `&` reference) but avoid deep nesting (2-3 levels maximum). Over-nesting increases specificity and makes styles harder to override.

## Naming Patterns Summary

**Observed class name patterns from 194 CSS Module files:**

| Pattern Type | Examples | Count | Purpose |
|--------------|----------|-------|---------|
| **Container/Wrapper** | `.wrap`, `.container`, `.wrapInner` | 45 | Outer element or layout container |
| **List/Grid** | `.navList`, `.logoGrid`, `.cardGrid` | 23 | Collection containers |
| **Header/Title** | `.header`, `.title`, `.subheader` | 38 | Heading elements |
| **Nav/Menu** | `.nav`, `.menu`, `.menuItem` | 19 | Navigation elements |
| **Content** | `.content`, `.text`, `.intro` | 31 | Content containers |
| **Visual** | `.logo`, `.icon`, `.image` | 17 | Visual elements |

**Most common compound words:** `titleWrap`, `navList`, `linkItem`, `innerBlock`, `textWrap`, `headerWrap`

**Modifier suffixes:** `__mobile`, `__desktop`, `__active`, `__disabled`, `__large`, `__small`, `__primary`, `__secondary`

## Real-World Example

Complete component showing naming conventions in practice:

```scss
// PageSection.module.scss (helix-dot-com-next)
.wrap {
  @include pageSectionWrap;

  &__bgwhite {
    background-color: $white;
  }

  &__bgdarkBlue {
    background-color: $darkblue-100;
  }
}

.wrapInner {
  position: relative;
}

.introWrap {
  @include containerGrid;
  margin-bottom: to-rem($page-section-intro-margin-bottom);
}

.intro {
  @include pageSectionColumns;
  text-align: center;
}

.title {
  @include pageSectionHeader;

  .wrap__bgdarkBlue & {
    color: $white;
  }
}

.text {
  @include pageSectionIntroBody;

  .wrap__bgdarkBlue & {
    color: $white;
  }
}

.innerBlocks {
  > :not(:last-child) {
    margin-bottom: to-rem(40px);
  }
}
```

**Component usage:**

```tsx
import cx from 'classnames'
import styles from './PageSection.module.scss'

export default function PageSection({ bgColor, children }) {
  return (
    <section className={cx(
      styles.wrap,
      bgColor === 'white' && styles.wrap__bgwhite,
      bgColor === 'darkBlue' && styles.wrap__bgdarkBlue
    )}>
      <div className={styles.wrapInner}>
        <div className={styles.introWrap}>
          <div className={styles.intro}>
            <h2 className={styles.title}>Title</h2>
            <p className={styles.text}>Introduction text</p>
          </div>
        </div>
        <div className={styles.innerBlocks}>
          {children}
        </div>
      </div>
    </section>
  )
}
```

**Benefits:** Clear hierarchy via nesting, self-documenting class names, type-safe access via dot notation, automatic scoping via CSS Modules, easy theming via parent modifiers.

## Design Token Naming (Variables)

While component classes use camelCase, SCSS variables for design tokens use kebab-case with descriptive prefixes. This distinction separates component structure (camelCase classes) from design values (kebab-case variables).

```scss
// _colors.scss
$charcoal-300: #373837;        // Base color: kebab-case
$body-text-color: $charcoal-300;  // Semantic alias: kebab-case

// _spacing.scss
$spacing-standard: 24px;       // Spacing token: kebab-case
$grid-column-gap: 24px;        // Layout token: kebab-case

// Component.module.scss
.title {                       // Class name: camelCase
  color: $body-text-color;     // Variable: kebab-case
  margin-bottom: $spacing-standard;  // Variable: kebab-case
}
```

**Rationale:** kebab-case for variables matches traditional CSS custom property syntax (`--body-text-color`). camelCase for classes enables JavaScript dot notation. Both conventions coexist without conflict.

## Migration from kebab-case

Projects migrating from kebab-case to camelCase can update incrementally. CSS Modules support bracket notation for compatibility during transition.

```tsx
// During migration: bracket notation works with kebab-case
<div className={styles['nav-list']}>

// After migration: dot notation with camelCase
<div className={styles.navList}>
```

**Recommendation:** Migrate all files in single PR to maintain consistency. Mixed naming conventions create confusion and maintenance burden.

## Related Patterns

- **CSS Modules:** See `css-modules-convention.md` for scoping and import patterns
- **Conditional Classes:** See `conditional-classnames.md` for applying multiple classes with cx()
- **Design Tokens:** See `design-system-structure.md` for variable naming in partials
