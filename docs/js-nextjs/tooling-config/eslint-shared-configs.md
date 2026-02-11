---
title: "ESLint Shared Configuration Pattern"
category: "tooling-config"
subcategory: "linting"
tags: ["eslint", "shared-config", "code-quality", "monorepo", "standards"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

## ESLint Shared Configuration Pattern for Next.js Projects

Next.js projects standardize linting rules using shared ESLint configurations distributed via npm packages. Helix and Policy-node adopt @aleph organization configs (@aleph/eslint-config-nought, @aleph/eslint-config), while Kariusdx uses standalone Airbnb style guide. Shared configs eliminate rule duplication across repositories and enforce consistent code standards organization-wide.

**Evidence:** 67% adoption rate (2/3 projects use @aleph shared configs).

## Configuration Structure

### Shared Config Pattern (Helix + Policy-node)

Projects extend organization-maintained shared configurations instead of defining rules inline. Helix uses JSON format with `@aleph/eslint-config-nought`, Policy-node uses ESM flat config with `@aleph/eslint-config`.

```json
// helix-dot-com-next/.eslintrc.json
{
  "root": true,
  "extends": [
    "next/core-web-vitals",
    "plugin:@next/next/recommended",
    "plugin:storybook/recommended",
    "@aleph/eslint-config-nought"
  ]
}
```

```javascript
// policy-node/eslint.config.js (ESM flat config)
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

**Key Characteristics:**
- Zero inline rules (all defined in shared package)
- Version-controlled via package.json dependency
- Extends Next.js recommended configs (next/core-web-vitals, next/typescript)
- FlatCompat enables backward compatibility during ESLint 9 flat config migration

## Standalone Configuration Pattern (Kariusdx)

Kariusdx defines 17 custom rules inline using Airbnb style guide as base. Configuration uses legacy JSON format with TypeScript overrides for .ts/.tsx files.

```json
// kariusdx-next/.eslintrc.json
{
  "root": true,
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
    "semi": ["error", "never"],
    "max-len": ["error", 120, 2, { "ignoreStrings": true }],
    "jsx-quotes": ["error", "prefer-single"],
    "comma-dangle": ["error", "always-multiline"],
    "no-underscore-dangle": ["error", {
      "allow": ["_createdAt", "_id", "_rev", "_type", "_updatedAt", "_key"]
    }],
    "react/jsx-props-no-spreading": "off",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off"
  }
}
```

**Key Characteristics:**
- Inline rule definitions (17 custom rules)
- Babel parser for JavaScript files, @typescript-eslint/parser for TypeScript
- Airbnb style guide (stricter than Next.js defaults)
- Explicit formatting rules (semi, max-len, jsx-quotes)
- Sanity CMS field allowances (_id, _type, etc.)

## Benefits of Shared Configurations

Shared ESLint configurations provide consistency, maintainability, and version control advantages over inline rule definitions.

**Consistency Across Projects:**
- All projects using @aleph configs enforce identical rules
- New projects inherit organization standards automatically
- Rule changes propagate via dependency updates

**Reduced Configuration Maintenance:**
- Zero lines of ESLint configuration in project repositories
- Helix .eslintrc.json: 9 lines (vs Kariusdx 151 lines)
- Plugin dependencies managed centrally in shared package

**Version Control and Auditing:**
- Shared config versions tracked in package.json
- Breaking changes communicated via semantic versioning
- Rollback capability via dependency downgrade

**Migration Path:**
- FlatCompat (Policy-node) enables gradual ESLint 9 migration
- Shared configs abstract flat config complexity from consuming projects
- Organization-wide migration coordinated through single package update

## When to Use Standalone Configuration

Standalone configurations remain appropriate when project-specific requirements diverge significantly from organization standards or shared configs don't exist.

**Project-Specific Constraints:**
Kariusdx requires semicolon-free code (semi: never) and single-quote JSX (jsx-quotes: prefer-single) due to team preferences established before organization-wide standards.

**Third-Party Integrations:**
Sanity CMS field naming (_id, _type, _createdAt) conflicts with no-underscore-dangle rule. Kariusdx explicitly allows these via custom rule configuration.

**Legacy Codebase Compatibility:**
Airbnb style guide (Kariusdx) may enforce stricter rules than Next.js defaults, preventing gradual migration. Projects locked to v12 (Kariusdx) cannot adopt modern flat config patterns without major refactoring.

## Implementation Requirements

### Shared Config Adoption

1. **Install Shared Package:**
```bash
npm install --save-dev @aleph/eslint-config
# or
npm install --save-dev @aleph/eslint-config-nought
```

2. **Minimal Project Configuration:**
```json
{
  "root": true,
  "extends": ["@aleph/eslint-config-nought"]
}
```

3. **Override Rules Sparingly:**
Only override when project-specific constraints exist. Overrides reduce shared config benefits.

```json
{
  "extends": ["@aleph/eslint-config"],
  "rules": {
    "no-console": "warn"  // Project-specific: allow console in dev
  }
}
```

### Flat Config Migration (ESLint 9+)

Policy-node demonstrates flat config adoption using FlatCompat for backward compatibility:

```javascript
const alephConfig = require('@aleph/eslint-config');
const { FlatCompat } = require('@eslint/eslintrc');

const compat = new FlatCompat({ baseDirectory: __dirname });

module.exports = [
  ...alephConfig,
  ...compat.extends('next/core-web-vitals'),
  ...compat.extends('next/typescript'),
];
```

**Migration Steps:**
1. Upgrade ESLint to v9+
2. Install @eslint/eslintrc for FlatCompat
3. Convert extends arrays to flat config spreads
4. Test linting across all file types

## Anti-Patterns

**❌ Inline Rule Proliferation:**
Do not define 15+ custom rules inline when shared config exists. Kariusdx approach increases maintenance burden and diverges from organization standards.

**❌ Mixing Shared + Standalone:**
Do not extend both @aleph configs and Airbnb. Conflicting rules create confusion about which standard applies.

**❌ Shared Config Overrides:**
Avoid overriding more than 3-5 rules from shared config. Excessive overrides indicate need for new shared config variant or project-specific config.

**❌ Unversioned Shared Configs:**
Do not use `@aleph/eslint-config@latest` in package.json. Pin versions to prevent unexpected rule changes breaking CI builds.

## Related Patterns

- **TypeScript Strict Mode Configuration** (tsconfig.json standards)
- **stylelint Shared Configurations** (@aleph/stylelint-config pattern)
- **Husky + lint-staged Integration** (pre-commit linting enforcement)
- **npm Scripts Conventions** (lint, lint:fix script standards)

## References

- ESLint Shareable Configs: https://eslint.org/docs/latest/extend/shareable-configs
- ESLint Flat Config: https://eslint.org/docs/latest/use/configure/configuration-files
- Next.js ESLint: https://nextjs.org/docs/app/building-your-application/configuring/eslint
