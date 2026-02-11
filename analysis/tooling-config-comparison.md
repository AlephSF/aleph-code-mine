# Tooling Configuration Comparison - Next.js Projects

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)

---

## Executive Summary

**Key Findings:**
- 100% ESLint adoption with divergent configurations (JSON vs JS flat config)
- 67% Aleph shared configs (@aleph/eslint-config, @aleph/stylelint-config)
- 33% Prettier adoption (policy-node only, implicit in others via Aleph configs)
- 100% stylelint adoption for SCSS
- 67% Husky + lint-staged (helix, policy-node)
- 67% Node version management (.nvmrc: helix v18.17.0, policy-node v22.13.1)
- 0% .editorconfig adoption (critical gap for cross-IDE consistency)
- TypeScript strict mode: 100% (all use "strict": true)

**Critical Gaps:**
- No .editorconfig files (team members may have inconsistent IDE settings)
- No Prettier configs in helix/kariusdx (assumed bundled in @aleph configs)
- Kariusdx lacks Husky (no pre-commit enforcement)
- No shared Babel config (kariusdx uses custom .babelrc)

---

## 1. ESLint Configuration

### Helix (.eslintrc.json)
- **Format:** JSON (legacy)
- **Extends:**
  - next/core-web-vitals
  - plugin:@next/next/recommended
  - plugin:storybook/recommended
  - @aleph/eslint-config-nought
- **Custom Rules:** 0 (all from shared config)
- **Version:** ESLint 8.39.0

### Kariusdx (.eslintrc.json)
- **Format:** JSON (legacy)
- **Parser:** @babel/eslint-parser
- **Extends:**
  - eslint:recommended
  - next/core-web-vitals
  - plugin:react/recommended
  - plugin:import/errors + warnings
  - plugin:jsx-a11y/recommended
  - plugin:react-hooks/recommended
  - airbnb
- **Custom Rules:** 17 (most comprehensive)
  - semi: "never" (no semicolons)
  - max-len: 120 characters
  - jsx-quotes: "prefer-single"
  - object-curly-spacing: "always"
  - comma-dangle: "always-multiline"
  - no-underscore-dangle: allows Sanity fields (_id, _type, _createdAt, etc.)
- **TypeScript Overrides:** Yes (files: *.ts, *.tsx)
- **Version:** ESLint 8.18.0

### Policy-node (eslint.config.js)
- **Format:** ESM Flat Config (modern, ESLint 9+ style)
- **Extends:**
  - @aleph/eslint-config
  - next/core-web-vitals
  - next/typescript
- **Custom Rules:** 0 (all from shared config)
- **Migration Status:** Using FlatCompat for backward compatibility
- **Version:** Not specified in devDependencies (managed by @aleph/eslint-config)

### Pattern Analysis
- **Shared Config Adoption:** 67% (helix + policy-node use @aleph configs)
- **Flat Config Migration:** 33% (policy-node only)
- **Airbnb Style Guide:** 33% (kariusdx only)
- **Semicolons:** Kariusdx forbids, others unspecified (likely default 'yes')
- **Max Line Length:** Kariusdx 120 chars, others unspecified

**De Facto Standard:**
- All use next/core-web-vitals (100%)
- React hooks rules: 100%
- TypeScript support: 100%
- Custom rules preferred over airbnb: 67% (helix + policy-node minimal rules)

---

## 2. TypeScript Configuration

### Helix (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "esnext",
    "lib": ["dom", "dom.iterable", "esnext"],
    "strict": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "paths": { "@/*": ["./*"] },
    "moduleResolution": "node",
    "plugins": [{ "name": "next" }]
  }
}
```
- **Strict Mode:** Yes
- **Path Aliases:** @/* -> ./*
- **Module Resolution:** node
- **Target:** esnext
- **Next.js Plugin:** Yes

### Kariusdx (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "es6",
    "lib": ["dom", "dom.iterable", "esnext"],
    "strict": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "moduleResolution": "node"
  }
}
```
- **Strict Mode:** Yes
- **Path Aliases:** None (uses baseUrl only)
- **Module Resolution:** node
- **Target:** es6 (older than helix/policy-node)
- **Next.js Plugin:** No (Next.js 12 didn't have this)

### Policy-node (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "strict": true,
    "jsx": "preserve",
    "paths": { "@/*": ["./src/*"] },
    "moduleResolution": "bundler",
    "plugins": [{ "name": "next" }]
  }
}
```
- **Strict Mode:** Yes
- **Path Aliases:** @/* -> ./src/*
- **Module Resolution:** bundler (modern, Next.js 14+ feature)
- **Target:** ES2017
- **Next.js Plugin:** Yes

### Pattern Analysis
- **strict: true:** 100% (all projects)
- **jsx: "preserve":** 100%
- **baseUrl:** 100% (but different path alias strategies)
- **Path Aliases:** 67% (helix + policy-node use @/* prefix)
- **Next.js Plugin:** 67% (helix + policy-node only)
- **moduleResolution: "bundler":** 33% (policy-node only - Next.js 14+ feature)

**De Facto Standard:**
- Always enable strict mode
- Use @/* path aliases (except kariusdx due to v12 limitations)
- Use Next.js TypeScript plugin (when available)
- Target: esnext or ES2017+ (avoid es6)

---

## 3. Stylelint Configuration

### Helix (.stylelintrc)
```json
{
  "extends": ["@aleph/stylelint-config-nought"]
}
```
- **Format:** JSON
- **Shared Config:** Yes (@aleph/stylelint-config-nought)
- **Custom Rules:** 0

### Kariusdx (.stylelintrc)
```json
{
  "extends": "stylelint-config-standard-scss",
  "plugins": ["stylelint-order", "stylelint-scss"],
  "rules": {
    "scss/dollar-variable-pattern": "^(-?[a-z][a-z0-9]*)(-[a-z0-9]+)*$",
    "string-quotes": "single",
    "order/properties-order": [ /* 80+ properties in specific order */ ]
  }
}
```
- **Format:** JSON
- **Shared Config:** No (uses standard-scss)
- **Custom Rules:** 20+ (most comprehensive)
- **Property Ordering:** Enforced (display -> position -> flex -> dimensions -> spacing -> typography)
- **Variable Naming:** kebab-case enforced
- **String Quotes:** Single quotes required

### Policy-node (stylelint.config.mjs)
```js
export default {
  extends: ['@aleph/stylelint-config']
}
```
- **Format:** ESM
- **Shared Config:** Yes (@aleph/stylelint-config)
- **Custom Rules:** 0

### Pattern Analysis
- **stylelint Adoption:** 100%
- **Shared Config:** 67% (helix + policy-node use @aleph configs)
- **SCSS Plugin:** 100%
- **Property Ordering:** 33% enforced (kariusdx only, likely in @aleph configs)
- **Variable Naming:** 33% enforced explicitly (kariusdx: kebab-case)
- **String Quotes:** 33% enforced (kariusdx: single)

**De Facto Standard:**
- Always use stylelint with SCSS plugin
- Enforce property ordering (improves readability)
- Use shared config when available (reduces duplication)

---

## 4. Prettier Configuration

### Helix
- **Config File:** None (assumed bundled in @aleph/eslint-config-nought)
- **Dependency:** Not listed in devDependencies
- **npm Script:** None

### Kariusdx
- **Config File:** None
- **Dependency:** Not listed in devDependencies
- **npm Script:** None
- **Note:** ESLint rules define formatting (semi: never, max-len: 120, etc.)

### Policy-node
- **Config File:** None (assumed bundled in @aleph configs)
- **Dependency:** Yes (prettier: ^3.4.2 in dependencies, not devDependencies)
- **npm Script:** None explicit (likely runs via lint-staged)

### Pattern Analysis
- **Prettier Adoption:** 33% explicit (policy-node only)
- **Prettier + ESLint Integration:** 0% (no eslint-config-prettier or eslint-plugin-prettier)
- **Config Files:** 0% (all rely on defaults or bundled configs)

**De Facto Standard:**
- Prettier is optional (ESLint handles most formatting)
- When used, integrate via shared config (not standalone)
- No separate "format" npm script needed

---

## 5. Pre-commit Hooks (Husky + lint-staged)

### Helix (.husky/pre-commit)
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

yarn lint:styles && yarn lint
```
- **Husky Version:** 8.0.0
- **lint-staged:** No (runs full lint on entire codebase)
- **Commands:**
  - yarn lint:styles -> stylelint "**/*.{css,sass,scss}"
  - yarn lint -> next lint
- **TypeScript Check:** No

### Kariusdx
- **Husky:** Not installed
- **Pre-commit Hooks:** None
- **Note:** Critical gap - no enforcement before commit

### Policy-node (.husky/pre-commit + .lintstagedrc.mjs)
```bash
npx lint-staged && npx tsc --noEmit
```
```js
// .lintstagedrc.mjs
const lintCommands = {
  '*.{js,jsx,ts,tsx}': [buildEslintCommand],
  '**/*.{css,sass,scss}': 'stylelint',
}
```
- **Husky Version:** Latest (no version in devDependencies)
- **lint-staged:** Yes (only lints changed files)
- **Commands:**
  - ESLint: next lint --file <changed files>
  - stylelint: changed CSS/SCSS files only
  - TypeScript: tsc --noEmit (type-check entire project)
- **TypeScript Check:** Yes (critical for catching type errors)

### Pattern Analysis
- **Husky Adoption:** 67% (helix + policy-node)
- **lint-staged Adoption:** 33% (policy-node only)
- **TypeScript Check:** 33% (policy-node only)
- **Runs on Changed Files Only:** 33% (policy-node only)
- **Full Codebase Lint:** 33% (helix only - slow on large codebases)

**De Facto Standard:**
- Use Husky for pre-commit hooks
- Prefer lint-staged (faster, scales better)
- Always run TypeScript type-checking (tsc --noEmit)
- Run both ESLint and stylelint before commit

**Critical Gap:**
- Kariusdx has no pre-commit hooks (developers can commit broken code)

---

## 6. npm Scripts

### Helix (package.json scripts)
```json
{
  "dev": "next dev",
  "build": "next build",
  "build:analyze": "ANALYZE=true yarn build",
  "start": "next start",
  "lint": "next lint",
  "lint:styles": "stylelint \"**/*.{css,sass,scss}\"",
  "prepare": "husky install",
  "storybook": "storybook dev -p 6006",
  "build-storybook": "storybook build",
  "codegen": "sanity-codegen codegen"
}
```
- **Storybook:** Yes
- **Bundle Analyzer:** Yes (build:analyze)
- **Sanity Codegen:** Yes (generates TypeScript types)
- **lint:styles:** Separate script (good)

### Kariusdx (package.json scripts)
```json
{
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint",
  "postbuild": "next-sitemap"
}
```
- **Sitemap Generation:** Yes (postbuild hook)
- **Separate lint:styles:** No
- **Minimal Scripts:** Yes (5 total)

### Policy-node (package.json scripts)
```json
{
  "dev": "next dev --turbopack",
  "dev:https": "next dev --turbopack --experimental-https",
  "build": "BUILD_CACHE=true next build",
  "start": "next start",
  "lint": "next lint",
  "lint:fix": "next lint --fix",
  "lint:styles": "stylelint \"**/*.{css,sass,scss}\"",
  "lint:styles:fix": "stylelint \"**/*.{css,sass,scss}\" --fix",
  "prepare": "husky",
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
```
- **Turbopack:** Yes (--turbopack in dev)
- **HTTPS Dev:** Yes (experimental)
- **lint:fix Scripts:** Yes (ESLint + stylelint)
- **Custom Data Scripts:** 11 scripts (CSV, validation, S3, search indexing)
- **BUILD_CACHE:** Yes (environment variable)

### Pattern Analysis
- **Separate lint:styles Script:** 67% (helix + policy-node)
- **lint:fix Scripts:** 33% (policy-node only)
- **Turbopack:** 33% (policy-node only - Next.js 14+)
- **Custom Build Scripts:** 67% (helix: analyze, policy-node: cache + data)
- **postbuild Hooks:** 33% (kariusdx: sitemap generation)
- **Storybook:** 33% (helix only)

**De Facto Standard:**
- Always separate lint and lint:styles
- Provide lint:fix convenience scripts
- Use build:analyze for bundle inspection
- Add custom scripts for project-specific tooling (codegen, validation, etc.)

---

## 7. Node Version Management

### .nvmrc Files
- **Helix:** v18.17.0 (LTS)
- **Kariusdx:** None
- **Policy-node:** v22.13.1 (Current)

### Pattern Analysis
- **.nvmrc Adoption:** 67% (helix + policy-node)
- **Node 18 LTS:** 33% (helix)
- **Node 22 Current:** 33% (policy-node)
- **No Version Control:** 33% (kariusdx - developers may use different versions)

**De Facto Standard:**
- Always include .nvmrc (critical for team consistency)
- Use LTS versions for production projects
- Consider Current version for new features (policy-node uses --experimental-https)

**Critical Gap:**
- Kariusdx has no .nvmrc (team may have version mismatches)

---

## 8. Missing Configurations

### .editorconfig
- **Adoption:** 0% (none have .editorconfig)
- **Impact:** IDE settings may differ (indentation, line endings, charset)
- **Recommended Settings:**
  ```ini
  root = true

  [*]
  indent_style = space
  indent_size = 2
  end_of_line = lf
  charset = utf-8
  trim_trailing_whitespace = true
  insert_final_newline = true

  [*.md]
  trim_trailing_whitespace = false
  ```

### .prettierignore
- **Adoption:** 0%
- **Impact:** Prettier may format generated files, build outputs
- **Recommended:**
  ```
  .next/
  node_modules/
  out/
  .storybook/
  *.min.js
  *.lock
  ```

### .eslintignore
- **Adoption:** 0% (ESLint uses .gitignore by default)
- **Impact:** Low (Next.js automatically ignores .next, node_modules)

---

## Confidence Scores

| Pattern | Confidence | Evidence |
|---------|-----------|----------|
| ESLint for JS/TS linting | 100% | 3/3 projects |
| stylelint for SCSS | 100% | 3/3 projects |
| TypeScript strict mode | 100% | 3/3 projects |
| Shared Aleph configs | 67% | 2/3 (helix + policy-node) |
| Husky pre-commit hooks | 67% | 2/3 (helix + policy-node) |
| lint-staged for efficiency | 33% | 1/3 (policy-node only) |
| TypeScript type-check in pre-commit | 33% | 1/3 (policy-node only) |
| .nvmrc for Node version | 67% | 2/3 (helix + policy-node) |
| Prettier explicit config | 33% | 1/3 (policy-node only) |
| .editorconfig | 0% | 0/3 (critical gap) |
| Flat Config ESLint | 33% | 1/3 (policy-node only) |
| Turbopack in dev | 33% | 1/3 (policy-node only) |
| Bundle analyzer | 33% | 1/3 (helix only) |
| Storybook | 33% | 1/3 (helix only) |

---

## Recommendations

### High Priority (Immediate)
1. **Add .editorconfig to all projects** (ensures IDE consistency)
2. **Add Husky + lint-staged to kariusdx** (enforce code quality)
3. **Add .nvmrc to kariusdx** (prevent Node version mismatches)
4. **Add TypeScript type-checking to helix pre-commit** (catch type errors early)

### Medium Priority (Next Sprint)
1. **Migrate helix to ESLint flat config** (future-proof, ESLint 9+ standard)
2. **Migrate kariusdx to ESLint flat config** (align with policy-node)
3. **Add lint:fix scripts to helix/kariusdx** (developer convenience)
4. **Add .prettierignore files** (prevent formatting generated code)

### Low Priority (Technical Debt)
1. **Consolidate ESLint rules** (kariusdx has 17 custom rules, others have 0)
2. **Add bundle analyzer to all projects** (monitor bundle size)
3. **Upgrade kariusdx to Node 18 LTS** (security, performance)
4. **Add postbuild hooks where needed** (sitemap, manifest generation)

---

## Semgrep Rule Candidates

1. **warn-missing-editorconfig.yaml** - Warn if .editorconfig is missing
2. **require-strict-typescript.yaml** - Require strict: true in tsconfig.json
3. **warn-no-husky.yaml** - Warn if .husky directory is missing
4. **enforce-path-alias.yaml** - Require @/* path alias in tsconfig.json

---

## Cross-Project Matrix

| Feature | Helix | Kariusdx | Policy-node | De Facto |
|---------|-------|----------|-------------|----------|
| ESLint | ✅ JSON | ✅ JSON | ✅ Flat Config | ✅ Yes |
| Shared ESLint Config | ✅ @aleph | ❌ Airbnb | ✅ @aleph | ✅ @aleph |
| TypeScript strict | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Path Aliases | ✅ @/* | ❌ No | ✅ @/* | ✅ @/* |
| Next.js Plugin | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| stylelint | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Shared stylelint Config | ✅ @aleph | ❌ Standard | ✅ @aleph | ✅ @aleph |
| Prettier | ⚠️ Implicit | ❌ No | ✅ Yes | ⚠️ Optional |
| Husky | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| lint-staged | ❌ No | ❌ No | ✅ Yes | ⚠️ Recommended |
| TypeScript Pre-commit | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| .nvmrc | ✅ v18 | ❌ No | ✅ v22 | ✅ Yes |
| .editorconfig | ❌ No | ❌ No | ❌ No | ❌ Gap |
| lint:styles Script | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| lint:fix Scripts | ❌ No | ❌ No | ✅ Yes | ⚠️ Recommended |
| Turbopack | ❌ No | ❌ No | ✅ Yes | ⚠️ Optional |
| Storybook | ✅ Yes | ❌ No | ❌ No | ⚠️ Optional |

---

## Code Examples

### ESLint Flat Config Pattern (Policy-node)
```js
// eslint.config.js
const alephConfig = require('@aleph/eslint-config');
const { FlatCompat } = require('@eslint/eslintrc');

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

module.exports = [
  ...alephConfig,
  ...compat.extends('next/core-web-vitals'),
  ...compat.extends('next/typescript'),
];
```

### lint-staged Configuration (Policy-node)
```js
// .lintstagedrc.mjs
import path from 'path'

const buildEslintCommand = (filenames) =>
  `next lint --file ${filenames
    .map((f) => path.relative(process.cwd(), f))
    .join(' --file ')}`

const lintCommands = {
  '*.{js,jsx,ts,tsx}': [buildEslintCommand],
  '**/*.{css,sass,scss}': 'stylelint',
}

export default lintCommands
```

### Husky Pre-commit with TypeScript Check
```bash
#!/usr/bin/env sh
# .husky/pre-commit
npx lint-staged && npx tsc --noEmit
```

### TypeScript Path Alias Configuration
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

**End of Analysis**
