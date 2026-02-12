---
title: "ESLint Flat Config Migration (ESLint 9+)"
category: "tooling-config"
subcategory: "eslint"
tags: ["eslint", "flat-config", "eslint-9", "migration", "eslint-config"]
stack: "js-nextjs"
priority: "low"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# ESLint Flat Config Migration (ESLint 9+)

## Overview

ESLint 9 introduces flat config (eslint.config.js) as the new default, deprecating .eslintrc.json. Only policy-node (33%) has migrated to flat config, while helix and kariusdx use legacy .eslintrc.json. Migration is low priority but future-proofs projects.

**De Facto Standard:** Use flat config (eslint.config.js) for new Next.js 14+ projects, legacy .eslintrc.json for Next.js 12 (ESLint 8 compatibility).

## Policy-node Flat Config Pattern

### ESLint 9 Configuration Example

```javascript
// eslint.config.js
import { FlatCompat } from '@eslint/eslintrc'
import nextPlugin from '@next/eslint-plugin-next'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'

const compat = new FlatCompat({
  baseDirectory: __dirname
})

export default [
  // Use FlatCompat for legacy configs
  ...compat.extends(
    '@aleph/eslint-config',
    'next/core-web-vitals',
    'next/typescript'
  ),

  // Native flat config overrides
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.json'
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      '@next/next': nextPlugin
    },
    rules: {
      // Custom rules here
    }
  }
]
```

**Source Evidence:** policy-node uses ESLint 9+ with flat config format

**Key Features:**
- ESM syntax (import/export, not require)
- Array of config objects (not single object)
- FlatCompat for backward compatibility with legacy configs (@aleph/eslint-config)
- Native flat config for TypeScript overrides

**Adoption:** 33% (policy-node only)

## Legacy .eslintrc.json Pattern

### Helix and Kariusdx Configurations

```json
// .eslintrc.json (helix)
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@next/next/recommended",
    "plugin:storybook/recommended",
    "@aleph/eslint-config-nought"
  ],
  "rules": {}
}
```

```json
// .eslintrc.json (kariusdx)
{
  "parser": "@babel/eslint-parser",
  "extends": [
    "eslint:recommended",
    "next/core-web-vitals",
    "plugin:react/recommended",
    "plugin:import/errors",
    "plugin:import/warnings",
    "plugin:jsx-a11y/recommended",
    "plugin:react-hooks/recommended",
    "airbnb"
  ],
  "rules": {
    "semi": "never",
    "max-len": ["error", { "code": 120 }]
  }
}
```

**Adoption:** 67% (helix + kariusdx)

**Why Still Common:**
- ESLint 8 is default in Next.js 12-14
- Shared configs (@aleph/eslint-config) may not support flat config yet
- Migration requires updating all ESLint plugins

## Flat Config Benefits

### 1. Simpler Configuration Model

**Legacy (.eslintrc.json):**
- Complex inheritance (extends, overrides, env, globals)
- Implicit plugin loading
- Config cascading across directories

**Flat Config:**
- Single flat array of objects
- Explicit plugin imports
- No cascading (one config file rules all)

### 2. Better TypeScript/IDE Support

```javascript
// eslint.config.js with type checking
/** @type {import('eslint').Linter.FlatConfig[]} */
export default [
  {
    files: ['**/*.ts'],
    rules: {
      // Autocomplete works here
    }
  }
]
```

### 3. ESM-First (Future-Proof)

```javascript
// Native ESM imports
import js from '@eslint/js'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import reactPlugin from 'eslint-plugin-react'

export default [
  js.configs.recommended,
  tsPlugin.configs.recommended,
  reactPlugin.configs.flat.recommended
]
```

**No require():** Modern JavaScript standard

## Migration Strategy: .eslintrc.json → eslint.config.js

### Step 1: Check ESLint Version

```bash
# Check current ESLint version
npm list eslint
# └─┬ eslint@8.39.0

# Upgrade to ESLint 9+
npm install --save-dev eslint@9
```

**Next.js Compatibility:**
- Next.js 14.2+: ESLint 9 supported
- Next.js 12-14.1: ESLint 8 (use legacy config)

### Step 2: Install FlatCompat (For Legacy Configs)

```bash
npm install --save-dev @eslint/eslintrc
```

**Why Needed:** @aleph/eslint-config uses legacy format, FlatCompat bridges the gap

### Step 3: Convert .eslintrc.json to eslint.config.js

**Before (.eslintrc.json):**

```json
{
  "extends": [
    "next/core-web-vitals",
    "@aleph/eslint-config-nought"
  ],
  "rules": {}
}
```

**After (eslint.config.js):**

```javascript
import { FlatCompat } from '@eslint/eslintrc'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname
})

export default [
  ...compat.extends(
    'next/core-web-vitals',
    '@aleph/eslint-config-nought'
  )
]
```

### Step 4: Test Configuration

```bash
# Run linter
npm run lint

# Check if rules still apply
npm run lint -- --debug
```

### Step 5: Remove .eslintrc.json

```bash
rm .eslintrc.json
git add eslint.config.js
git commit -m "chore: Migrate to ESLint flat config"
```

## Shared Config Challenges

### Problem: @aleph Configs Use Legacy Format

Policy-node uses FlatCompat as a bridge:

```javascript
// eslint.config.js
export default [
  // Legacy shared config via FlatCompat
  ...compat.extends('@aleph/eslint-config'),

  // Modern flat config overrides
  {
    files: ['**/*.ts', '**/*.tsx'],
    rules: {
      // Custom TypeScript rules
    }
  }
]
```

**When to Migrate:**
- @aleph/eslint-config releases flat config version
- Next.js upgrades to ESLint 9 by default
- Team prioritizes modern tooling

**Current Blocker:** @aleph configs may not have flat config versions yet

## Kariusdx-Specific Considerations

Kariusdx uses Airbnb style guide (not @aleph config):

```json
// .eslintrc.json (kariusdx)
{
  "extends": ["airbnb"]
}
```

**Migration Path:**

```javascript
// eslint.config.js
import airbnb from 'eslint-config-airbnb'
import { FlatCompat } from '@eslint/eslintrc'

const compat = new FlatCompat()

export default [
  // Airbnb doesn't have flat config yet (as of 2024)
  ...compat.extends('airbnb'),

  {
    rules: {
      'semi': ['error', 'never'],
      'max-len': ['error', { code: 120 }]
    }
  }
]
```

**Blocker:** eslint-config-airbnb has no flat config version (use FlatCompat)

## When to Migrate vs. Wait

### Migrate Now If:
- ✅ Using Next.js 14.2+ (ESLint 9 supported)
- ✅ No blockers from shared configs
- ✅ Team comfortable with ESM syntax

### Wait If:
- ⏳ Next.js 12 (ESLint 8 only)
- ⏳ Shared configs (@aleph, airbnb) don't support flat config
- ⏳ Limited time for non-critical migration

**Recommendation for Analyzed Projects:**
- **Policy-node:** ✅ Already migrated (ESLint 9)
- **Helix:** ⏳ Wait for @aleph/eslint-config-nought flat config version
- **Kariusdx:** ⏳ Upgrade to Next.js 14+ first, then migrate

## Anti-Patterns to Avoid

### Don't: Mix .eslintrc.json and eslint.config.js

```bash
# ❌ Bad: Both config files present
.eslintrc.json
eslint.config.js
```

**Problem:** ESLint 9 prioritizes eslint.config.js, ignores .eslintrc.json (confusing)

### Don't: Use FlatCompat for Everything

```javascript
// ❌ Bad: No native flat config usage
export default [
  ...compat.extends('next/core-web-vitals'),
  ...compat.extends('plugin:@typescript-eslint/recommended')
]
```

**Better:**

```javascript
import tsPlugin from '@typescript-eslint/eslint-plugin'

export default [
  // Legacy config via FlatCompat
  ...compat.extends('next/core-web-vitals'),

  // Native flat config for TypeScript
  {
    files: ['**/*.ts', '**/*.tsx'],
    plugins: { '@typescript-eslint': tsPlugin },
    rules: tsPlugin.configs.recommended.rules
  }
]
```

### Don't: Migrate Without Testing

```bash
# ❌ Bad: Commit without validation
git add eslint.config.js
git commit -m "Migrate to flat config"

# ✅ Good: Test first
npm run lint
npm run lint:fix
git add eslint.config.js
git commit -m "chore: Migrate to ESLint flat config"
```

## References

- **ESLint Flat Config Docs:** https://eslint.org/docs/latest/use/configure/configuration-files
- **FlatCompat Migration Guide:** https://eslint.org/docs/latest/use/configure/migration-guide
- **Next.js ESLint 9 Support:** https://nextjs.org/docs/app/api-reference/next-config-js/eslint

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- Flat config (ESLint 9): 1/3 projects (33% - policy-node)
- Legacy .eslintrc.json: 2/3 projects (67% - helix, kariusdx)
- FlatCompat usage: 1/3 projects (33% - policy-node)
