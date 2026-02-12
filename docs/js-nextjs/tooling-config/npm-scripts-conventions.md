---
title: "npm Scripts Conventions for Next.js Projects"
category: "tooling-config"
subcategory: "npm-scripts"
tags: ["npm", "package-json", "scripts", "lint", "build", "dev"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# npm Scripts Conventions for Next.js Projects

## Overview

npm scripts provide a consistent interface for common development tasks across Next.js projects. All analyzed projects (helix, kariusdx, policy-node) share core scripts (dev, build, start, lint) with variations for project-specific tooling.

**De Facto Standard:** Use standard script names (dev, build, lint, lint:styles), separate lint and lint:styles, provide :fix variants for auto-correction.

## Core Standard Scripts (100% Adoption)

### Essential Development Scripts

```json
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

**Adoption:** 100% (all projects use these exact scripts)

**Usage:**
- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build production bundle
- `npm run start` - Start production server (after build)
- `npm run lint` - Run ESLint via Next.js CLI

## Separate lint:styles Pattern (67% Adoption)

### Helix and Policy-node Pattern

```json
{
  "scripts": {
    "lint": "next lint",
    "lint:styles": "stylelint \"**/*.{css,sass,scss}\""
  }
}
```

**Why Separate:**
- ESLint (JavaScript/TypeScript) and stylelint (CSS/SCSS) are different tools
- Allows granular pre-commit hook configuration
- Developers can run style checks independently
- Better error messages (not mixed with JS lint errors)

**Adoption:** 67% (helix + policy-node)

**Kariusdx Gap:** Kariusdx has no separate `lint:styles` script (must run `npx stylelint` manually)

## Auto-fix Scripts (33% Adoption)

### Policy-node Pattern

```json
{
  "scripts": {
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "lint:styles": "stylelint \"**/*.{css,sass,scss}\"",
    "lint:styles:fix": "stylelint \"**/*.{css,sass,scss}\" --fix"
  }
}
```

**Benefits:**
- `npm run lint:fix` - Auto-fixes ESLint errors (e.g., semicolons, indentation)
- `npm run lint:styles:fix` - Auto-fixes stylelint errors (e.g., property ordering, quotes)

**Adoption:** 33% (policy-node only)

**Why Recommended:** Saves developer time - many lint errors are auto-fixable

## Advanced Development Scripts

### Turbopack (Next.js 14+)

```json
// policy-node
{
  "scripts": {
    "dev": "next dev --turbopack",
    "dev:https": "next dev --turbopack --experimental-https"
  }
}
```

**Features:**
- `--turbopack` - 5-10x faster than Webpack (Next.js 14+ feature)
- `--experimental-https` - Local HTTPS server (for OAuth, secure cookie testing)

**Adoption:** 33% (policy-node only)

**Why Policy-node Uses This:** Large codebase (29K LOC) benefits from Turbopack speed

### Build Variants

```json
// helix
{
  "scripts": {
    "build": "next build",
    "build:analyze": "ANALYZE=true yarn build"
  }
}
```

```json
// policy-node
{
  "scripts": {
    "build": "BUILD_CACHE=true next build"
  }
}
```

**Helix Pattern:** `build:analyze` visualizes bundle sizes (via @next/bundle-analyzer)
**Policy-node Pattern:** `BUILD_CACHE=true` enables Redis ISR caching during build

**Adoption:** 67% (helix + policy-node have custom build scripts)

## Project-Specific Tooling Scripts

### Sanity Codegen (Helix)

```json
{
  "scripts": {
    "codegen": "sanity-codegen codegen"
  }
}
```

Generates TypeScript types from Sanity schemas (runs after schema changes)

## Data Pipeline Scripts (Policy-node)

### Validation and Build Automation

```json
{
  "scripts": {
    "csv:split": "node scripts/split-translations-csv.mjs",
    "csv:join": "node scripts/join-translations-csv.mjs",
    "csv:test": "node scripts/test-split-load.mjs",
    "validate:data": "tsx scripts/validate-data.ts",
    "validate:baseline": "tsx scripts/generate-baseline.ts",
    "validate:report": "tsx scripts/validate-data.ts --report-only",
    "search:generate": "tsx scripts/generate-search-index.ts",
    "s3:check": "tsx scripts/check-s3-data.ts",
    "s3:download": "tsx scripts/download-s3-data.ts",
    "s3:build": "tsx scripts/build-if-new-data.ts",
    "s3:build:force": "tsx scripts/build-if-new-data.ts --force"
  }
}
```

**Pattern:** Namespace scripts with prefixes (csv:, validate:, s3:)

**Benefits:**
- Clear grouping (all CSV scripts start with csv:)
- Easy to discover (npm run shows all scripts)
- Autocomplete-friendly (npm run csv:<tab>)

**Adoption:** 33% (policy-node only - most complex tooling)

### Sitemap Generation (Kariusdx)

```json
{
  "scripts": {
    "build": "next build",
    "postbuild": "next-sitemap"
  }
}
```

**postbuild Hook:** Runs automatically after `next build` completes

**Adoption:** 33% (kariusdx only)

**Why Recommended:** Automates sitemap generation, developers can't forget to run it

## Storybook Scripts (33% Adoption)

```json
// helix
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

**Adoption:** 33% (helix only)

**Why Helix Uses This:** Component library documentation (188 components)

## prepare Script for Husky (67% Adoption)

```json
{
  "scripts": {
    "prepare": "husky install" // Husky 8.x
    // OR
    "prepare": "husky" // Husky 9.x
  }
}
```

**When prepare Runs:** Automatically after `npm install`

**Purpose:** Sets up Git hooks for new developers (no manual setup needed)

**Adoption:** 67% (helix + policy-node)

## Script Naming Conventions

### Use Colons for Namespacing

```json
{
  "scripts": {
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "lint:styles": "stylelint \"**/*.{css,sass,scss}\"",
    "lint:styles:fix": "stylelint \"**/*.{css,sass,scss}\" --fix"
  }
}
```

**Pattern:** `<base>:<variant>:<modifier>`

### Use Consistent Verbs

- **lint** - Check for issues (read-only)
- **lint:fix** - Auto-correct issues (write)
- **build** - Create production bundle
- **build:analyze** - Build with analysis
- **validate** - Check data integrity
- **generate** - Create files (codegen, sitemap, search index)

## Anti-Patterns to Avoid

### Don't: Mix lint and lint:styles

```json
// ❌ Bad: Single script runs both
{
  "scripts": {
    "lint": "next lint && stylelint \"**/*.scss\""
  }
}
```

**Problem:** Can't run ESLint or stylelint separately, harder to debug

### Don't: Use Non-standard Script Names

```json
// ❌ Bad: Custom names, harder for new developers
{
  "scripts": {
    "serve": "next dev", // Use "dev" instead
    "compile": "next build", // Use "build" instead
    "check": "next lint" // Use "lint" instead
  }
}
```

**Problem:** Breaks developer muscle memory, inconsistent with ecosystem

### Don't: Hardcode Paths in Scripts

```json
// ❌ Bad: Assumes Unix paths
{
  "scripts": {
    "lint:styles": "stylelint src/**/*.scss"
  }
}
```

**Problem:** Fails on Windows (use quotes: `"src/**/*.scss"`)

## Migration Checklist

Kariusdx improvements (based on helix/policy-node patterns):

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "postbuild": "next-sitemap", // ✅ Already has this
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix", // 🆕 Add for developer convenience
    "lint:styles": "stylelint \"**/*.{css,sass,scss}\"", // 🆕 Critical gap
    "lint:styles:fix": "stylelint \"**/*.{css,sass,scss}\" --fix", // 🆕 Add
    "prepare": "husky" // 🆕 Critical gap (no pre-commit hooks)
  }
}
```

## References

- **npm Scripts Docs:** https://docs.npmjs.com/cli/v10/using-npm/scripts
- **Next.js CLI:** https://nextjs.org/docs/app/api-reference/next-cli
- **stylelint CLI:** https://stylelint.io/user-guide/usage/cli

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- Core scripts (dev, build, start, lint): 3/3 projects (100%)
- Separate lint:styles: 2/3 projects (67%)
- Auto-fix scripts: 1/3 projects (33%)
- prepare script: 2/3 projects (67%)
- Custom tooling scripts: 3/3 projects (100%, but vary by project needs)
