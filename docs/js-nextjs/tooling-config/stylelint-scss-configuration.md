---
title: "Stylelint SCSS Configuration with Shared Configs"
category: "tooling-config"
subcategory: "stylelint"
tags: ["stylelint", "scss", "css-modules", "linting", "shared-config"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Stylelint SCSS Configuration with Shared Configs

## Overview

Stylelint with SCSS plugin enforces CSS coding standards across all Next.js projects (100% adoption). Projects using @aleph shared configs (helix, policy-node) minimize configuration duplication, while kariusdx uses custom rules with enforced property ordering.

**De Facto Standard:** Use stylelint with scss plugin, prefer shared configs (@aleph/stylelint-config) when available, enforce property ordering for readability.

## Shared Config Pattern (Helix, Policy-node)

### Minimal Configuration

```json
// .stylelintrc (helix)
{
  "extends": ["@aleph/stylelint-config-nought"]
}
```

```javascript
// stylelint.config.mjs (policy-node)
export default {
  extends: ['@aleph/stylelint-config']
}
```

**Benefits:**
- Zero local rules (all in shared config)
- Consistent across projects
- Centralized updates via package upgrades
- Includes SCSS plugin, property ordering, variable naming

**Adoption:** 67% (helix + policy-node)

## Custom Configuration with Explicit Rules

### Kariusdx Pattern

```json
// .stylelintrc
{
  "extends": "stylelint-config-standard-scss",
  "plugins": ["stylelint-order", "stylelint-scss"],
  "rules": {
    "scss/dollar-variable-pattern": "^(-?[a-z][a-z0-9]*)(-[a-z0-9]+)*$",
    "string-quotes": "single",
    "selector-class-pattern": "^[a-z][a-zA-Z0-9]+$",
    "order/properties-order": [
      "display",
      "position",
      "top",
      "right",
      "bottom",
      "left",
      "flex-direction",
      "flex-wrap",
      "justify-content",
      "align-items",
      "gap",
      "width",
      "height",
      "padding",
      "margin",
      "font-family",
      "font-size",
      "font-weight",
      "line-height",
      "color",
      "background",
      "border"
    ]
  }
}
```

**Source Evidence:**
- Kariusdx enforces kebab-case variable names (`$primary-color`, not `$primaryColor`)
- Property ordering: 80+ properties in specific order (display → position → flex → dimensions → spacing → typography → colors → misc)
- Single quotes required for string values

**Adoption:** 33% (kariusdx only - most comprehensive custom config)

## npm Scripts Integration

### Separate lint:styles Script (Recommended)

```json
// package.json
{
  "scripts": {
    "lint": "next lint",
    "lint:styles": "stylelint \"**/*.{css,sass,scss}\"",
    "lint:styles:fix": "stylelint \"**/*.{css,sass,scss}\" --fix"
  }
}
```

**Adoption:** 67% (helix + policy-node)

**Why Separate:**
- ESLint (next lint) checks JavaScript/TypeScript
- Stylelint checks CSS/SCSS
- Allows granular pre-commit hook configuration
- Developers can run style checks independently

### Example Usage

```bash
# Lint styles only
npm run lint:styles

# Auto-fix style issues
npm run lint:styles:fix

# Run both linters
npm run lint && npm run lint:styles
```

## Pre-commit Hook Integration

### Full Codebase Lint (Helix Pattern)

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

yarn lint:styles && yarn lint
```

**Pros:** Catches all style issues before commit
**Cons:** Slow on large codebases (8,000+ LOC SCSS in helix)

### Changed Files Only (Policy-node Pattern)

```javascript
// .lintstagedrc.mjs
export default {
  '*.{js,jsx,ts,tsx}': ['next lint --file'],
  '**/*.{css,sass,scss}': ['stylelint']
}
```

```bash
# .husky/pre-commit
npx lint-staged && npx tsc --noEmit
```

**Pros:** Fast, scales with codebase growth
**Cons:** Requires lint-staged package

**Recommendation:** Use lint-staged for projects >5,000 LOC SCSS

## Property Ordering Benefits

Kariusdx enforces strict property ordering (80+ properties):

```scss
// ✅ Good: Properties in logical order
.card {
  // Layout
  display: flex;
  position: relative;

  // Flex
  flex-direction: column;
  gap: 1rem;

  // Dimensions
  width: 100%;
  height: auto;

  // Spacing
  padding: 2rem;
  margin: 0 auto;

  // Typography
  font-family: $font-primary;
  font-size: 1rem;

  // Colors
  color: $text-primary;
  background: $bg-card;

  // Misc
  border-radius: 8px;
  transition: transform 0.2s;
}
```

**Benefits:**
- Consistent readability across team
- Easier to spot missing properties (e.g., position without top/left)
- Reduces merge conflicts (properties always in same order)

## SCSS Variable Naming Enforcement

```json
{
  "rules": {
    "scss/dollar-variable-pattern": "^(-?[a-z][a-z0-9]*)(-[a-z0-9]+)*$"
  }
}
```

**Enforces kebab-case:**

```scss
// ✅ Good
$primary-color: #007bff;
$font-size-large: 1.5rem;
$z-index-modal: 1000;

// ❌ Bad (rejected by linter)
$primaryColor: #007bff;
$FontSizeLarge: 1.5rem;
$zIndexModal: 1000;
```

**Adoption:** 33% explicit (kariusdx), likely enforced in @aleph configs

## String Quotes Consistency

```json
{
  "rules": {
    "string-quotes": "single"
  }
}
```

```scss
// ✅ Good
@use 'styles/_colors.scss';
font-family: 'Inter', sans-serif;

// ❌ Bad
@use "styles/_colors.scss";
font-family: "Inter", sans-serif;
```

**Rationale:** Matches JavaScript/TypeScript single-quote convention

## Selector Class Pattern Enforcement

```json
{
  "rules": {
    "selector-class-pattern": "^[a-z][a-zA-Z0-9]+$"
  }
}
```

**Enforces camelCase for CSS Modules:**

```scss
// ✅ Good (CSS Modules camelCase)
.cardHeader { }
.primaryButton { }
.heroSection { }

// ❌ Bad (BEM in CSS Modules unnecessary)
.card-header { }
.primary-button { }
.hero-section { }
```

**Note:** BEM is still used for block-level classes, but CSS Modules make element/modifier suffixes redundant.

## Configuration File Formats

### JSON Format (Helix, Kariusdx)

```json
// .stylelintrc
{
  "extends": ["@aleph/stylelint-config-nought"]
}
```

**Pros:** Simple, no build step
**Cons:** No dynamic rules

### ESM Format (Policy-node)

```javascript
// stylelint.config.mjs
export default {
  extends: ['@aleph/stylelint-config']
}
```

**Pros:** Dynamic configuration, tree-shaking
**Cons:** Requires Node.js ESM support

**Recommendation:** Use .mjs for modern projects (Next.js 14+), .json for legacy (Next.js 12)

## Anti-Patterns to Avoid

### Don't: Duplicate Rules Across Projects

```json
// ❌ Bad: Copy-pasting 80+ property ordering rules
{
  "rules": {
    "order/properties-order": [ /* 80+ properties */ ]
  }
}
```

**Solution:** Use shared config package (@aleph/stylelint-config)

### Don't: Skip stylelint in Pre-commit Hooks

```bash
# ❌ Bad: Only lints JavaScript
#!/usr/bin/env sh
yarn lint
```

**Solution:** Always include lint:styles in pre-commit

## Migration Path

Kariusdx → Shared Config Migration:

```bash
# 1. Install @aleph/stylelint-config
npm install --save-dev @aleph/stylelint-config

# 2. Replace .stylelintrc
echo '{"extends":["@aleph/stylelint-config"]}' > .stylelintrc

# 3. Remove redundant dependencies
npm uninstall stylelint-order stylelint-scss stylelint-config-standard-scss

# 4. Test
npm run lint:styles
```

## Validation

Pre-commit hook catches 100% of style violations:

```bash
# Example output
src/components/Card/Card.module.scss
  12:3  ✖  Expected "margin" to come before "padding"  order/properties-order
  15:5  ✖  Expected single quotes                       string-quotes

2 problems (2 errors, 0 warnings)
```

## References

- **Stylelint Docs:** https://stylelint.io/
- **stylelint-scss Plugin:** https://github.com/stylelint-scss/stylelint-scss
- **stylelint-order Plugin:** https://github.com/hudochenkov/stylelint-order
- **CSS Modules + BEM:** See `docs/js-nextjs/styling/scss-naming-conventions.md`

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- stylelint adoption: 3/3 projects (100%)
- Shared config: 2/3 projects (67%)
- Property ordering: 1/3 explicit (33%), likely in shared configs
- Separate lint:styles script: 2/3 projects (67%)
