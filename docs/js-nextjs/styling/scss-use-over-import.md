---
title: "Modern SCSS: @use Over @import for Module Imports"
category: "styling"
subcategory: "scss-modules"
tags: ["scss", "@use", "@import", "modules", "namespacing"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "68%"
last_updated: "2026-02-11"
---

# Modern SCSS: @use Over @import for Module Imports

## Overview

Modern Next.js projects adopt SCSS `@use` directive instead of legacy `@import` for loading design token partials. Helix and policy-node achieved 91-96% @use adoption, while kariusdx remains on @import (16% @use adoption). The Sass team deprecated @import in October 2021 and will remove it in Dart Sass 2.0.

**Benefits:** @use provides explicit namespacing to prevent variable collisions, loads each file only once (vs @import which can load files multiple times), enables better tree-shaking for smaller bundles, provides clearer dependency graphs.

**Migration Status:** 68% average adoption across projects. Helix (91%) and policy-node (96%) migrated fully. Kariusdx (16%) remains on legacy @import.

## Syntax Comparison

The @use directive replaces @import with explicit namespace control and one-time loading semantics.

### Legacy @import Pattern (Deprecated)

```scss
// Component.module.scss (kariusdx-next - legacy)
@import 'styles/variables';
@import 'styles/grid';
@import 'styles/typography';
@import 'styles/mixins';

.container {
  background-color: $brand-primary;    // From variables
  @include container-grid;             // From grid
}
```

**Problems:** Variables and mixins imported into global namespace (collision risk), files can be imported multiple times (bloat), no clear dependency tracking, imports resolved relative to entry file (not current file).

### Modern @use Pattern (Recommended)

```scss
// Component.module.scss (helix-dot-com-next / policy-node - modern)
@use "../../styles/colors" as *;
@use "../../styles/typography" as *;
@use "../../styles/spacing" as s;
@use "../../styles/mixins" as *;

.container {
  background-color: $darkblue-100;     // From colors
  padding: s.$spacing-large;           // From spacing (namespaced)
  @include containerGrid;              // From mixins
}
```

**Benefits:** Each file loaded exactly once (performance), explicit namespacing prevents collisions, relative paths from current file (predictable), tree-shaking removes unused code.

## Namespace Control with 'as' Keyword

The `as` keyword controls how imported members are accessed. Three patterns: global (`as *`), custom (`as name`), and default (basename).

**Global namespace (`as *`):** Import all into global namespace without prefix. Use when no name collisions exist.

```scss
@use "../../styles/colors" as *;
@use "../../styles/typography" as *;
@use "../../styles/mixins" as *;
.title{@include h1;color:$charcoal-300;}
```

**When to use:** Design token files with unique names (colors, typography, mixins). Reduces verbosity.

**Adoption:** 91% of helix and policy-node use `as *` for colors, typography, and mixins.

**Custom namespace (`as [name]`):** Import behind custom prefix. Use when variable names might collide.

```scss
@use "../../styles/spacing" as s;
.container{padding:s.$spacing-large;margin-bottom:s.$grid-column-gap;}
```

**When to use:** Files with generic names (spacing, variables) or overlapping names.

**Adoption:** 75% use `as s` for spacing to avoid collision.

**Default namespace (basename):** Omit `as` to use file's basename as namespace. Rarely used.

```scss
@use "../../styles/colors";
@use "../../styles/spacing";
.container{background:colors.$darkblue-100;padding:spacing.$spacing-large;}
```

**Adoption:** < 5%. Most files use explicit `as *` or `as s`.

## Import Path Resolution

@use resolves paths relative to current file, unlike @import which resolves relative to entry file. This makes @use more predictable and portable.

```scss
// Incorrect @import path (resolved from entry point)
@import 'styles/colors';

// Correct @use path (resolved from current file)
@use "../../styles/colors" as *;
```

**Directory structure:**

```
app/
└── (frontend)/
    ├── styles/
    │   ├── _colors.scss
    │   ├── _typography.scss
    │   └── _spacing.scss
    └── components/
        └── Button/
            └── Button.module.scss  // Current file location
```

**From Button.module.scss:**

```scss
// Correct: relative path from Button.module.scss to _colors.scss
@use "../../styles/colors" as *;

// Two directories up (../../) to reach app/(frontend)/
// Then into styles/ directory
// Then colors.scss (underscore and extension optional)
```

**Benefit:** Moving component to different directory only requires updating path depth, not path structure.

## Underscore and Extension Omission

SCSS allows omitting leading underscore and `.scss` extension in @use paths. Both forms are equivalent.

```scss
// All equivalent:
@use "../../styles/_colors.scss" as *;
@use "../../styles/colors.scss" as *;
@use "../../styles/_colors" as *;
@use "../../styles/colors" as *;  // ✅ Preferred (shortest)
```

**Convention:** Omit both underscore and extension for brevity. SCSS automatically finds partial files with leading underscore.

**Adoption:** 100% of @use statements omit underscore and extension across helix and policy-node.

## Single Load Guarantee

@use loads each file exactly once per compilation, even if multiple files @use the same partial. @import loads files every time they are imported, leading to code duplication.

```scss
// Component1.module.scss
@use "../../styles/colors" as *;  // Loads colors.scss

// Component2.module.scss
@use "../../styles/colors" as *;  // Reuses already-loaded colors.scss

// Result: colors.scss compiled once and shared
```

**With @import (deprecated):**

```scss
// Component1.module.scss
@import 'styles/colors';  // Loads colors.scss

// Component2.module.scss
@import 'styles/colors';  // Loads colors.scss AGAIN (duplication)

// Result: colors.scss compiled twice, bloating CSS bundle
```

**Benefit:** Smaller CSS bundles, faster builds, clearer dependency graph.

## Forwarding with @forward

@forward directive re-exports another module's members, enabling "barrel file" pattern for design system organization.

```scss
// _index.scss (design system barrel file)
@forward "./colors";
@forward "./typography";
@forward "./spacing";
@forward "./mixins";

// Component.module.scss
@use "../../styles" as *;  // Loads all via index

.container {
  background: $darkblue-100;      // From colors (forwarded)
  @include h1;                    // From typography (forwarded)
  padding: $spacing-large;        // From spacing (forwarded)
}
```

**Adoption:** 0% - no projects use @forward barrel pattern. All projects import partials individually for explicitness.

**Reason for non-adoption:** Individual imports make dependencies clearer and enable better tree-shaking. Barrel files can obscure what tokens a component actually uses.

## Configuring Modules with 'with' Keyword

@use supports passing configuration variables into modules with `with` keyword. Useful for configuring mixin libraries or theme frameworks.

```scss
// Component.module.scss (helix-dot-com-next)
@use "sass:math";
@use "./colors" as *;
@use "./spacing" as *;

@forward "@aleph/nought-sass-mixins" with (
  $grid-column-count: 12,
  $grid-column-gap: $grid-column-gap,
  $container-width: $container-width,
  $container-padding: $container-padding,
  $grid-responsive-column-counts: (
    md: 8,
    sm: 4,
  ),
  $grid-breakpoints: (
    xs: $breakpoint-xs,
    sm: $breakpoint-sm,
    md: $breakpoint-md,
    lg: $breakpoint-lg,
    xl: $breakpoint-xl,
  )
);

@use "@aleph/nought-sass-mixins" as *;
```

**Usage:** Configure third-party mixin libraries (like @aleph/nought-sass-mixins) with project-specific values. Variables must be declared with `!default` in source module to be configurable.

**Adoption:** < 5% of files use `with` keyword. Primarily for configuring external libraries, not internal partials.

## Migration Strategy from @import to @use

Helix and policy-node successfully migrated from @import to @use. Recommended approach is incremental file-by-file migration with codemods.

### Step 1: Install sass-migrator

```bash
npm install -g sass-migrator
```

### Step 2: Run Migration Tool

```bash
sass-migrator module --migrate-deps \
  app/**/*.scss \
  components/**/*.scss
```

**Flags:**
- `module`: Convert @import to @use
- `--migrate-deps`: Recursively migrate imported files

### Step 3: Review and Test

Migration tool converts syntax but may create overly-verbose namespaces. Review output and simplify:

```scss
// Auto-generated (verbose):
@use "../../styles/colors" as colors;

.title {
  color: colors.$charcoal-300;
}

// Simplified (preferred):
@use "../../styles/colors" as *;

.title {
  color: $charcoal-300;
}
```

### Step 4: Update Build Pipeline

Verify Sass compilation still works. Next.js supports @use out-of-box (Sass 1.23+).

**Testing:** Run `npm run build` and inspect compiled CSS for correctness.

### Migration Statistics

| Project | @use Files | @import Files | Migration % | Status |
|---------|------------|---------------|-------------|--------|
| **helix-dot-com-next** | 71 | 7 | 91% | Complete |
| **policy-node** | 70 | 3 | 96% | Complete |
| **kariusdx-next** | 10 | 52 | 16% | Incomplete |

**Recommendation:** Kariusdx should migrate remaining 52 @import files to @use before Dart Sass 2.0 removes @import support.

## Common @use Patterns

Standard @use pattern observed in 141 files across helix and policy-node:

```scss
// Component.module.scss (standard pattern)
@use "sass:math";                          // Built-in Sass modules
@use "../../styles/colors" as *;           // Colors: global namespace
@use "../../styles/typography" as *;       // Typography: global namespace
@use "../../styles/spacing" as s;          // Spacing: namespaced
@use "../../styles/mixins" as *;           // Mixins: global namespace

.container {
  @include containerGrid;                  // Mixin (global)
  background: $darkblue-100;               // Color (global)
  padding: s.$spacing-large;               // Spacing (namespaced)
}
```

**Order convention:** Sass built-ins first, then design tokens (colors, typography, spacing, mixins).

**Namespace convention:** Global (`as *`) for colors/typography/mixins, namespaced (`as s`) for spacing.

## Deprecation Timeline

Sass team announced @import deprecation timeline:

- **October 2021:** @import officially deprecated
- **October 2022:** Deprecation warnings in Dart Sass
- **Dart Sass 2.0 (TBD):** @import removed entirely

**Recommendation:** Migrate all @import usage to @use before Dart Sass 2.0 release to avoid breaking changes.

## Related Patterns

- **CSS Modules:** See `css-modules-convention.md` for component file structure
- **Design Tokens:** See `design-system-structure.md` for partial file organization
- **Naming:** See `scss-naming-conventions.md` for variable naming conventions
