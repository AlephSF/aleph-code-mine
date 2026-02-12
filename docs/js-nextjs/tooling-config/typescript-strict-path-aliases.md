---
title: "TypeScript Strict Mode with Path Aliases"
category: "tooling-config"
subcategory: "typescript"
tags: ["typescript", "tsconfig", "path-aliases", "strict-mode", "import"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# TypeScript Strict Mode with Path Aliases

## Overview

TypeScript strict mode (`"strict": true`) combined with path aliases (`@/*`) provides type safety and clean imports across Next.js projects. All analyzed Next.js codebases (helix, kariusdx, policy-node) enable strict mode, and 67% use @/ path aliases (helix, policy-node).

**De Facto Standard:** Always enable strict mode and configure @/* path aliases pointing to project root or src directory.

## Core Pattern: Strict Mode + Path Aliases

### Basic Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    },
    "target": "esnext",
    "lib": ["dom", "dom.iterable", "esnext"],
    "jsx": "preserve",
    "moduleResolution": "bundler",
    "plugins": [{ "name": "next" }]
  }
}
```

**Source Evidence:**
- Helix: `"strict": true`, `"paths": { "@/*": ["./*"] }`
- Policy-node: `"strict": true`, `"paths": { "@/*": ["./src/*"] }`
- Kariusdx: `"strict": true` (no path aliases - Next.js v12 limitation)

### Path Alias Variants

```json
// Root-level alias (helix pattern)
{
  "baseUrl": ".",
  "paths": { "@/*": ["./*"] }
}

// Src-level alias (policy-node pattern)
{
  "baseUrl": ".",
  "paths": { "@/*": ["./src/*"] }
}
```

**Import Examples:**

```typescript
// Without path alias (kariusdx)
import { Button } from '../../../components/Button'
import { formatDate } from '../../../utils/formatDate'

// With @/* alias (helix, policy-node)
import { Button } from '@/components/Button'
import { formatDate } from '@/utils/formatDate'
```

## Strict Mode Benefits

TypeScript strict mode enables multiple type-safety flags:

1. **noImplicitAny** - Errors on implicit any types
2. **strictNullChecks** - null and undefined are distinct types
3. **strictFunctionTypes** - Contravariant function parameter checking
4. **strictBindCallApply** - Type-checks bind/call/apply methods
5. **strictPropertyInitialization** - Class properties must be initialized
6. **noImplicitThis** - Errors on implicit any type for this
7. **alwaysStrict** - Parse files in strict mode and emit "use strict"

**Real-World Impact:**
- Helix (15,300 LOC): 168 Props interfaces, strict typing enforced
- Policy-node (29,000 LOC): 2,213 optional properties (? operator), strict null checks prevent undefined errors
- Kariusdx (19,700 LOC): 91% no Hungarian notation (no I/T prefixes), strict mode catches type errors

## Module Resolution Strategies

### Modern: moduleResolution: "bundler"

```json
// policy-node (Next.js 14+)
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "target": "ES2017"
  }
}
```

**Benefits:**
- Optimized for Next.js 14+ bundler
- Supports package.json "exports" field
- Faster resolution than "node"

### Legacy: moduleResolution: "node"

```json
// helix, kariusdx (Next.js 12-15)
{
  "compilerOptions": {
    "moduleResolution": "node",
    "target": "esnext"
  }
}
```

**When to Use:**
- Next.js 12-13 projects (kariusdx)
- Legacy dependency compatibility

## Next.js TypeScript Plugin

```json
{
  "compilerOptions": {
    "plugins": [{ "name": "next" }]
  }
}
```

**Adoption:** 67% (helix, policy-node - Next.js 14+ feature)

**Features Provided:**
- Auto-completion for Next.js config
- Type-checks for Server/Client Components
- Route segment config validation
- Metadata API type-safety

**Missing in Kariusdx:** Next.js 12 predates this plugin

## Target ECMAScript Versions

**Observed Patterns:**
- Helix: `"target": "esnext"` (latest features)
- Policy-node: `"target": "ES2017"` (stable, async/await native)
- Kariusdx: `"target": "es6"` (legacy, avoid for new projects)

**Recommendation:** Use `"esnext"` or `"ES2017"` minimum. Avoid `"es6"` (2015) - outdated for modern Next.js.

## Migration Path for Kariusdx

Kariusdx (Next.js 12) lacks path aliases and modern TypeScript features:

```bash
# 1. Upgrade to Next.js 14+
npm install next@14 react@18 react-dom@18

# 2. Update tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "target": "esnext",
    "moduleResolution": "bundler",
    "paths": { "@/*": ["./*"] },
    "plugins": [{ "name": "next" }]
  }
}

# 3. Refactor imports (automated with codemod)
npx jscodeshift -t transform-imports.js src/
```

## Anti-Patterns to Avoid

### Don't: Disable Strict Mode Flags

```json
// ❌ Bad: Weakens type safety
{
  "strict": true,
  "noImplicitAny": false,
  "strictNullChecks": false
}
```

### Don't: Multiple Path Alias Prefixes

```json
// ❌ Bad: Inconsistent, harder to remember
{
  "paths": {
    "@/*": ["./src/*"],
    "~/*": ["./src/*"],
    "#/*": ["./lib/*"]
  }
}
```

**Reason:** @/* is the de facto standard, use one prefix consistently.

### Don't: Omit baseUrl with Path Aliases

```json
// ❌ Bad: Path aliases require baseUrl
{
  "paths": { "@/*": ["./*"] }
  // Missing baseUrl
}
```

## Enforcement

Use pre-commit hooks to validate tsconfig.json:

```bash
# .husky/pre-commit
npx tsc --noEmit || (echo "TypeScript errors detected" && exit 1)
```

**Adoption:** 33% (policy-node only - critical gap in helix/kariusdx)

## References

- **TypeScript Handbook:** https://www.typescriptlang.org/tsconfig#strict
- **Next.js TypeScript Docs:** https://nextjs.org/docs/app/building-your-application/configuring/typescript
- **Path Mapping:** https://www.typescriptlang.org/docs/handbook/module-resolution.html#path-mapping

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- Strict mode: 3/3 projects (100%)
- Path aliases: 2/3 projects (67%)
- Next.js plugin: 2/3 projects (67%)
