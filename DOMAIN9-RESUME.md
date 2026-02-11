# Domain 9: Tooling Config - Resume Instructions

**Status:** 13% complete (1/8 docs, 0/4 Semgrep rules)
**Last Updated:** February 11, 2026
**Estimated Time Remaining:** 2 hours

---

## What's Done ✅

### Analysis Complete
- ✅ Comprehensive comparison analysis: `analysis/tooling-config-comparison.md`
- ✅ All config files scanned (ESLint, TypeScript, stylelint, Prettier, Husky)
- ✅ Cross-project matrix with confidence scores
- ✅ Critical gaps identified

### Documentation Complete
1. ✅ `eslint-shared-configs.md` (67% confidence)
   - @aleph/eslint-config pattern
   - Flat config migration with FlatCompat
   - Shared vs standalone configurations

---

## What's Remaining ⏳

### Documentation Files (7 remaining)

2. **typescript-strict-path-aliases.md** (100% confidence)
   - Pattern: All projects use `"strict": true`
   - Pattern: 67% use `@/*` path aliases (helix, policy-node)
   - Path alias targets: `@/*` -> `./*` (helix) vs `./src/*` (policy-node)
   - moduleResolution: "bundler" (policy-node) vs "node" (helix/kariusdx)
   - Next.js plugin: 67% (helix + policy-node)

3. **stylelint-scss-configuration.md** (100% confidence)
   - Pattern: All projects use stylelint with SCSS
   - Shared configs: 67% (@aleph/stylelint-config)
   - Kariusdx: 20+ custom rules (property ordering, variable naming)
   - lint:styles script: 67% (helix + policy-node)

4. **husky-lint-staged-pattern.md** (67% confidence)
   - Pattern: Helix + policy-node use Husky
   - lint-staged: 33% (policy-node only - recommended)
   - TypeScript pre-commit: 33% (policy-node: `tsc --noEmit`)
   - Helix runs full lint (slow), policy-node runs changed files only (fast)
   - Kariusdx gap: No pre-commit hooks (critical)

5. **npm-scripts-conventions.md** (100% confidence)
   - Pattern: All have `lint`, `lint:styles` (67%), `dev`, `build`, `start`
   - lint:fix: 33% (policy-node only - recommended)
   - Turbopack: 33% (policy-node: `--turbopack` flag)
   - Bundle analyzer: 33% (helix: `build:analyze`)
   - Custom scripts: Policy-node has 11 data/validation scripts

6. **node-version-management.md** (67% confidence)
   - Pattern: Helix uses v18.17.0 (LTS), policy-node uses v22.13.1 (Current)
   - Kariusdx gap: No .nvmrc file (critical)
   - Recommendation: Use LTS for production, Current for experimental features

7. **eslint-flat-config-migration.md** (33% confidence)
   - Pattern: Policy-node uses ESLint 9+ flat config
   - FlatCompat for backward compatibility
   - Migration path from JSON to ESM flat config
   - Helix + kariusdx still use legacy JSON format

8. **editorconfig-missing-pattern.md** (0% confidence - gap pattern)
   - Critical gap: No .editorconfig files in any project
   - Impact: IDE settings may differ (indentation, line endings, charset)
   - Recommended config provided in analysis
   - Related gaps: No .prettierignore, no .eslintignore

---

## Semgrep Rules to Generate (4 total)

1. **warn-missing-editorconfig.yaml**
   - Warn if .editorconfig missing in project root
   - Message: "Add .editorconfig for IDE consistency"

2. **require-strict-typescript.yaml**
   - Require `"strict": true` in tsconfig.json
   - Fail if strict is false or missing

3. **warn-no-husky.yaml**
   - Warn if .husky directory missing
   - Message: "Add Husky pre-commit hooks for code quality enforcement"

4. **enforce-path-alias.yaml**
   - Require `@/*` path alias in tsconfig.json
   - Check for baseUrl + paths configuration
   - Fail if missing (prevents import inconsistencies)

---

## Key Data Points from Analysis

### Confidence Scores
| Pattern | Confidence | Projects |
|---------|-----------|----------|
| ESLint | 100% | 3/3 |
| TypeScript strict | 100% | 3/3 |
| stylelint | 100% | 3/3 |
| @aleph shared configs | 67% | 2/3 (helix, policy-node) |
| Husky | 67% | 2/3 (helix, policy-node) |
| .nvmrc | 67% | 2/3 (helix, policy-node) |
| lint-staged | 33% | 1/3 (policy-node) |
| TypeScript pre-commit | 33% | 1/3 (policy-node) |
| Flat config | 33% | 1/3 (policy-node) |
| .editorconfig | 0% | 0/3 (gap) |

### Critical Gaps
1. **Kariusdx has no Husky** - Developers can commit broken code
2. **No .editorconfig files** - IDE settings inconsistent across team
3. **Kariusdx has no .nvmrc** - Node version mismatches possible
4. **Helix skips TypeScript check** - Pre-commit only runs ESLint/stylelint

---

## File Locations

**Analysis:** `/Users/oppodeldoc/code/aleph-code-mine/analysis/tooling-config-comparison.md`
**Docs:** `/Users/oppodeldoc/code/aleph-code-mine/docs/js-nextjs/tooling-config/`
**Semgrep:** `/Users/oppodeldoc/code/aleph-code-mine/tooling/semgrep/tooling-config/` (to create)

**Source Repos:**
- `/Users/oppodeldoc/code/helix-dot-com-next/` (Next.js v15)
- `/Users/oppodeldoc/code/kariusdx-next/` (Next.js v12)
- `/Users/oppodeldoc/code/policy-node/` (Next.js v14)

---

## Code Examples Ready for Docs

### TypeScript Strict + Path Aliases
```json
// Recommended pattern (policy-node)
{
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] },
    "moduleResolution": "bundler"
  }
}
```

### Husky + lint-staged (Policy-node)
```bash
# .husky/pre-commit
npx lint-staged && npx tsc --noEmit
```

```js
// .lintstagedrc.mjs
const buildEslintCommand = (filenames) =>
  `next lint --file ${filenames
    .map((f) => path.relative(process.cwd(), f))
    .join(' --file ')}`

export default {
  '*.{js,jsx,ts,tsx}': [buildEslintCommand],
  '**/*.{css,sass,scss}': 'stylelint',
}
```

### npm Scripts Pattern
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

### .editorconfig (Missing - Recommended)
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

---

## Resume Command

```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat DOMAIN9-RESUME.md
cat PROGRESS.md | grep -A50 "Domain 9"
```

**Tell Claude:**
"Continue Domain 9: Tooling Config. Generate remaining 7 documentation files (typescript-strict-path-aliases.md through editorconfig-missing-pattern.md), then generate 4 Semgrep rules. Work in batches of 2-3 docs, commit between batches."

---

## Documentation Template Checklist

For each doc, ensure:
- ✅ Frontmatter complete (title, category, tags, confidence, etc.)
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ Technology names explicit (not "it", "this", "these")
- ✅ Code blocks >10 lines get dedicated subsections
- ✅ Real examples from helix/kariusdx/policy-node
- ✅ Confidence score matches analysis percentages

---

## Batch Strategy

**Batch 1 (Next):**
- typescript-strict-path-aliases.md
- stylelint-scss-configuration.md
- husky-lint-staged-pattern.md

**Batch 2:**
- npm-scripts-conventions.md
- node-version-management.md

**Batch 3:**
- eslint-flat-config-migration.md
- editorconfig-missing-pattern.md

**Batch 4:**
- Generate 4 Semgrep rules
- Validate all docs
- Update PROGRESS.md to 100%

Commit after each batch to preserve work and keep context manageable.
