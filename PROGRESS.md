# Codebase Mining Progress

**Last Updated:** February 11, 2026
**Current Phase:** Phase 2 - Domain-Targeted Deep Dives (In Progress)
**Current Domain:** Error Handling (Next.js) ⏳ IN PROGRESS (25% complete)

---

## Phase 1: Structural Reconnaissance ✅ COMPLETE

**Status:** All 8 repositories analyzed
**Duration:** ~2 hours
**Output:** 9 markdown files in `/analysis/`

### Completed Deliverables

1. ✅ helix-dot-com-next-structure.md
2. ✅ kariusdx-next-structure.md
3. ✅ policy-node-structure.md
4. ✅ helix-dot-com-sanity-structure.md
5. ✅ kariusdx-sanity-structure.md
6. ✅ ripplecom-sanity-structure.md
7. ✅ thekelsey-wp-structure.md
8. ✅ airbnb-structure.md
9. ✅ PHASE1-SUMMARY.md

### Key Findings That Impact Next Phases

#### Critical Issues
- **ZERO testing infrastructure** across all Next.js repos (high priority to document testing gaps)
- Next.js version fragmentation (v12, v14, v15) - may have different patterns per version
- Sanity version diversity (v2, v3, v4) - need version-specific patterns

#### Consistent Patterns (De Facto Standards)
- SCSS + CSS Modules (100% adoption, no Tailwind)
- TypeScript (100% in Next.js/Sanity)
- Design system structure: _colors, _typography, _spacing, _mixins
- SEO-first with dedicated metadata objects

#### Architecture Complexity
- **Most Complex:** policy-node (29K LOC, Redis ISR, S3 pipeline)
- **Most Schemas:** ripplecom-sanity (78 schemas, 13K LOC)
- **Most Mature:** airbnb (WordPress VIP multisite, 8+ sites)

---

## Phase 2: Domain-Targeted Deep Dives 🎯 IN PROGRESS

**Decision:** Start with Next.js domains (richest codebase, 3 repos)

### Domain 1: Component Patterns ✅ COMPLETE

**Duration:** ~2.5 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/component-patterns/`
- 4 Semgrep rules in `tooling/semgrep/component-patterns/`

**Documentation Files:**
1. ✅ folder-per-component.md (100% confidence)
2. ✅ default-exports.md (100% confidence)
3. ✅ props-typing-conventions.md (85% confidence)
4. ✅ component-declaration-patterns.md (55% confidence)
5. ✅ scss-modules-styling.md (100% confidence)
6. ✅ svg-component-pattern.md (100% confidence)
7. ✅ server-client-component-boundaries.md (100% confidence)
8. ✅ sanity-field-type-extension.md (33% confidence)

**Semgrep Rules:**
1. ✅ no-react-fc.yaml - Disallow React.FC usage
2. ✅ require-default-export.yaml - Enforce default exports
3. ✅ classnames-cx-alias.yaml - Enforce cx alias for classnames
4. ✅ no-use-server-in-components.yaml - Prevent 'use server' in components

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual file counts
- ⏳ Semgrep rules validation pending (semgrep not installed)

**Key Findings:**
- Universal patterns: Folder-per-component, default exports, SCSS modules, cx alias
- Divergent patterns: Function vs arrow function declarations (55% vs 40%)
- Version-specific: Server/client boundaries only in App Router (v14+)
- Legacy patterns: IPrefix on interfaces (kariusdx only, marked for avoidance)

### Domain 2: Data Fetching ✅ COMPLETE

**Duration:** ~4 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/data-fetching/`
- 4 Semgrep rules in `tooling/semgrep/data-fetching/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ isr-revalidation.md (100% confidence)
2. ✅ custom-fetch-wrappers.md (100% confidence)
3. ✅ preview-mode.md (100% confidence)
4. ✅ error-handling.md (100% confidence)
5. ✅ app-router-patterns.md (67% confidence)
6. ✅ pages-router-patterns.md (100% confidence)
7. ✅ route-handlers.md (67% confidence)
8. ✅ graphql-batching.md (33% confidence)

**Semgrep Rules:**
1. ✅ require-revalidate-export.yaml - Enforce ISR revalidation
2. ✅ require-try-catch-fetch-wrapper.yaml - Enforce error handling in fetch wrappers
3. ✅ require-abort-controller-timeout.yaml - Enforce timeout in fetch calls
4. ✅ warn-missing-notfound-handling.yaml - Warn on missing 404 handling

**Analysis Files:**
1. ✅ data-fetching-comparison.md - Cross-project quantitative analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- Universal patterns: ISR revalidation (100%), custom fetch wrappers (100%), preview mode (100%), extensive error handling (4060+ try/catch)
- App Router adoption: 67% (helix v15, policy-node v14 hybrid)
- Pages Router patterns: 100% in kariusdx, legacy support in helix/policy-node
- Sophisticated error handling: policy-node implements timeout + retry with exponential backoff
- Zero server actions: No 'use server' adoption observed
- Zero SWR: No client-side data fetching libraries used
- GraphQL batching: policy-node optimizes build with request batching (800+ pages)

### Domain 3: TypeScript Conventions ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/typescript-conventions/`
- 4 Semgrep rules in `tooling/semgrep/typescript-conventions/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ props-naming-convention.md (100% confidence)
2. ✅ optional-vs-nullable-properties.md (100% confidence)
3. ✅ no-hungarian-notation.md (91% confidence)
4. ✅ type-vs-interface-decision-tree.md (54% confidence)
5. ✅ union-type-patterns.md (100% confidence)
6. ✅ record-type-for-dictionaries.md (33% confidence)
7. ✅ type-assertions-sparingly.md (33% confidence)
8. ✅ type-guards-for-runtime-safety.md (0% confidence - gap pattern)

**Semgrep Rules:**
1. ✅ no-interface-i-prefix.yaml - Disallow I prefix on interfaces
2. ✅ no-type-t-prefix.yaml - Disallow T prefix on type aliases
3. ✅ warn-type-assertion-no-validation.yaml - Warn on assertions without validation
4. ✅ prefer-string-union-over-enum.yaml - Prefer string unions over enums

**Analysis Files:**
1. ✅ typescript-conventions-comparison.md - Cross-project quantitative analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- Universal patterns: Props suffix (168 instances), optional properties (2213), export keyword
- Divergent patterns: Type vs interface (54% type overall, but kariusdx 71% interface)
- Policy-node sophistication: Heavy utility type usage (152 Record instances), type assertions (70 vs 5-7 in others)
- Hungarian notation: 91% no-prefix adoption (kariusdx legacy has I/T prefixes)
- Avoided patterns: Type guards (0 usage), enums (3 total), readonly (10 total), const assertions (14 total)
- Critical gap: Zero type guard implementations despite extensive API parsing

### Domain 4: Hooks & State ✅ COMPLETE

**Duration:** ~2.5 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/hooks-state/`
- 3 Semgrep rules in `tooling/semgrep/hooks-state/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ multiple-usestate-pattern.md (100% confidence)
2. ✅ useeffect-cleanup-pattern.md (100% confidence)
3. ✅ ssr-safe-custom-hooks.md (100% confidence)
4. ✅ usestate-type-annotations.md (100% confidence)
5. ✅ when-to-use-usereducer.md (0% confidence - gap pattern)
6. ✅ context-vs-props-drilling.md (1% confidence - gap pattern)
7. ✅ usememo-usecallback-guidelines.md (minimal usage)
8. ✅ useeffect-dependency-patterns.md (100% confidence)

**Semgrep Rules:**
1. ✅ warn-usestate-empty-array-no-type.yaml - Require types for empty arrays
2. ✅ warn-useeffect-listener-no-cleanup.yaml - Require cleanup for event listeners
3. ✅ warn-context-provider-no-usememo.yaml - Require useMemo for context values

**Analysis Files:**
1. ✅ hooks-state-comparison.md - Cross-project hook usage analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual usage counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- Universal patterns: useState + useEffect (100%), multiple useState over single object (100%), event listener cleanup (100%)
- SSR-safe custom hooks: All 4 custom hooks follow same pattern (window checks, mount tracking, tuple return)
- Minimal patterns: Custom hooks (4 total), useMemo (20), useCallback (13), useContext (2)
- Zero usage: useReducer (0 instances), external state libraries (0), type guards in hooks (0)
- Critical gaps: No custom hooks for data fetching/forms, no useReducer despite complex state (11 useState in one component)

### Domain 5: Styling ✅ COMPLETE

**Duration:** ~3.5 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/styling/`
- 4 Semgrep rules in `tooling/semgrep/styling/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ css-modules-convention.md (91% confidence)
2. ✅ design-system-structure.md (100% confidence)
3. ✅ scss-naming-conventions.md (100% confidence)
4. ✅ scss-use-over-import.md (68% confidence)
5. ✅ conditional-classnames.md (67% confidence)
6. ✅ responsive-breakpoint-patterns.md (67% confidence)
7. ✅ state-management-patterns.md (100% confidence)
8. ✅ globals-and-resets.md (100% confidence)

**Semgrep Rules:**
1. ✅ require-module-scss-suffix.yaml - Enforce .module.scss for component styles
2. ✅ warn-scss-import-usage.yaml - Warn on @import (prefer @use)
3. ✅ enforce-classnames-cx-alias.yaml - Enforce cx alias for classnames
4. ✅ warn-missing-hover-media-query.yaml - Warn on hover without touch detection

**Analysis Files:**
1. ✅ styling-comparison.md - Cross-project quantitative styling analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual file counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- Universal patterns: CSS Modules (91%), design system partials (100%), camelCase + BEM naming (100%)
- Modern SCSS: 68% overall @use adoption (helix 91%, policy-node 96%, kariusdx 16%)
- Conditional classes: 67% adoption of cx() from classnames (helix + kariusdx, 267 total calls)
- Responsive: Desktop-first approach with breakpoint mixins (593 calls in helix + kariusdx)
- State management: 82 hover states, 55 focus-visible (100% modern focus pattern)
- Critical gaps: Zero CSS Modules composition usage, minimal hover media query usage (14 instances)

### Priority Order (Based on Findings)

**High Priority Domains:**
1. **Component patterns** - 188 components in helix, need consistent patterns
2. **Error handling** - Found gaps in testing, likely gaps in error handling too
3. **Data fetching** - Mix of ISR, SSR, SSG across versions - need unified guidance
4. **TypeScript conventions** - All use TS, but need consistent type vs interface usage

**Medium Priority:**
5. **Hooks & state** - Custom hooks in multiple repos, document patterns
6. **Styling** - Already consistent (CSS Modules), but document best practices
7. **Project structure** - App Router vs Pages Router differences
8. **Testing** - Document the gap and provide guidance

**Lower Priority:**
9. **Tooling config** - ESLint/Prettier configs are mostly consistent

### Adjusted Domain List (Next.js)

| Domain | Repos to Analyze | Priority | Estimated LOC to Review |
|--------|------------------|----------|-------------------------|
| **Component patterns** | All 3 | HIGH | ~313 components |
| **Data fetching** | All 3 | HIGH | ~5K LOC |
| **Error handling** | All 3 | HIGH | ~2K LOC |
| **TypeScript conventions** | All 3 | HIGH | ~15K LOC |
| **Hooks & state** | helix, policy | MEDIUM | ~1K LOC |
| **Project structure** | All 3 | MEDIUM | Analysis only |
| **Styling** | All 3 | MEDIUM | ~8K LOC CSS |
| **Testing** | All 3 | HIGH | Gap documentation |
| **Tooling config** | All 3 | LOW | Config files only |

---

## Execution Strategy for Phase 2

### Per-Domain Workflow

For each domain, we'll:

1. **Quantitative Analysis** (15-30 min)
   - Run `grep` for relevant patterns across all 3 Next.js repos
   - Count occurrences (e.g., "useState", "useEffect", "fetch", "try/catch")
   - Identify most common patterns

2. **Qualitative Analysis** (30-60 min)
   - Read representative examples from each repo
   - Identify common patterns vs. divergences
   - Note version-specific patterns (v12 vs v14 vs v15)

3. **Cross-Project Comparison** (15-30 min)
   - Build comparison matrix
   - Identify de facto standards (what's common across all)
   - Flag discussion points (where repos diverge)

4. **Generate Output Docs** (30-45 min)
   - Draft RAG-optimized docs following template
   - One doc per specific pattern/rule
   - Real code examples from repos
   - Calculate source_confidence percentages

5. **Generate Semgrep Rules** (if applicable)
   - For enforceable patterns only
   - Test against source repos

**Total per domain:** ~2-3 hours
**Total for 9 domains:** ~18-27 hours (can parallelize some)

---

## Tools We'll Use in Phase 2

### Installed / Available via npx
- ✅ `grep` / `rg` (ripgrep) - Pattern searching
- ✅ `npx scc` - Code complexity metrics
- ✅ `npx repomix` - Codebase summaries
- ✅ `npx react-scanner` - Component usage stats
- ✅ `npx dependency-cruiser` - Module dependencies

### Need to Install
- ⚠️ `semgrep` - Pattern detection (install: `brew install semgrep`)
- ⚠️ `phpcs` + WPCS - WordPress standards (for Phase 2 WordPress domains)
- ⚠️ `phpstan` - PHP static analysis

---

## Next Session Action Plan

### Step 1: Install Missing Tools (5 min)
```bash
brew install semgrep  # or pip install semgrep
```

### Step 2: Start Domain 1 - Component Patterns (2-3 hours)

**Quantitative Phase:**
- `grep -r "export default" helix-dot-com-next/app/components --count`
- `grep -r "export const" helix-dot-com-next/app/components --count`
- `grep -r "interface.*Props" */src --count`
- `grep -r "type.*Props" */src --count`

**Qualitative Phase:**
- Read top 10 most referenced components
- Identify naming patterns (PascalCase, file structure)
- Document props patterns (interface vs type)
- Note composition patterns (children, render props, etc.)

**Comparison Phase:**
- Build matrix: helix vs kariusdx vs policy-node
- Identify common patterns (>80% adoption = de facto standard)

**Output Phase:**
- Generate docs in `docs/js-nextjs/component-patterns/`
- Each specific rule gets its own file (e.g., `named-exports-over-default.md`)
- Follow RAG template strictly (<1500 chars per section)

### Step 3: Continue Through Domains
Repeat for remaining 8 domains, one at a time.

---

## Blockers / Decisions Needed

### Resolved
- ✅ Repo paths provided
- ✅ Tech stack classification complete
- ✅ Phase 1 structural recon done

### Open Questions for User
1. **Testing Documentation:** Should we document the testing gap as a "what's missing" guide, or skip since there's nothing to mine?
2. **Next.js Version Divergence:** Document version-specific patterns separately, or focus on patterns common across all versions?
3. **Semgrep Rule Priority:** Which domains should get Semgrep rules first? (Recommendation: TypeScript conventions, component patterns, error handling)

---

## File Organization Readiness

### Already Created
```
aleph-code-mine/
├── analysis/              ✅ Phase 1 outputs (9 files)
├── docs/                  ✅ Empty structure ready
│   ├── js-nextjs/        ✅ Ready for Phase 2 outputs
│   ├── sanity/           ✅ Ready for Phase 3 outputs
│   ├── php-wordpress/    ✅ Ready for Phase 4 outputs
│   └── cross-stack/      ✅ Ready for Phase 5 outputs
└── tooling/              ✅ Empty structure ready
    ├── semgrep/          ✅ Ready for Semgrep rules
    ├── validate-docs/    ✅ Ready for validation script
    └── generate-linter-docs/ ✅ Ready for linter doc generators
```

---

## Estimated Timeline

| Phase | Status | Time Estimate |
|-------|--------|---------------|
| Phase 1: Structural Recon | ✅ Complete | 2 hours (done) |
| Phase 2: Next.js Domains (9) | 🎯 In Progress (7/9 complete) | 18-27 hours |
| - Domain 1: Component Patterns | ✅ Complete | 2.5 hours (done) |
| - Domain 2: Data Fetching | ✅ Complete | 4 hours (done) |
| - Domain 3: TypeScript Conventions | ✅ Complete | 3 hours (done) |
| - Domain 4: Hooks & State | ✅ Complete | 2.5 hours (done) |
| - Domain 5: Styling | ✅ Complete | 3.5 hours (done) |
| - Domain 6: Project Structure | ✅ Complete | 3 hours (done) |
| - Domain 7: Testing | ✅ Complete | 2.5 hours (done) |
| - Domain 8-9: Remaining domains | ⏳ Pending | 1-5 hours |
| Phase 3: Sanity Domains (4) | ⏳ Pending | 8-12 hours |
| Phase 4: WordPress Domains (8) | ⏳ Pending | 16-24 hours |
| Phase 5: Cross-Stack (4) | ⏳ Pending | 8-12 hours |
| Phase 6: Tooling Outputs | ⏳ Pending | 8-12 hours |
| **TOTAL** | **75% Complete** | **54-83 hours** |

---

## Resume Commands

When resuming this project in a new session:

```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat PROGRESS.md  # Read this file
cat analysis/PHASE1-SUMMARY.md  # Review findings
ls analysis/  # See all structural analyses
```

Then tell Claude:
> "Continue the codebase mining project. Start Phase 2, Domain 4: [Next Domain]"

**Completed Domains:**
- ✅ Phase 1: Structural Reconnaissance (all 8 repos)
- ✅ Phase 2, Domain 1: Component Patterns (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 2: Data Fetching (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 3: TypeScript Conventions (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 4: Hooks & State (Next.js) - 8 docs + 3 Semgrep rules
- ✅ Phase 2, Domain 5: Styling (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 6: Project Structure (Next.js) - 7 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 7: Testing (Next.js) - 8 docs + 4 Semgrep rules

### Domain 6: Project Structure ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 7 RAG-optimized documentation files in `docs/js-nextjs/project-structure/`
- 4 Semgrep rules in `tooling/semgrep/project-structure/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ app-router-vs-pages-router.md (67% confidence)
2. ✅ route-groups-organization.md (100% App Router adoption)
3. ✅ component-collocation-patterns.md (100% confidence)
4. ✅ file-based-routing-conventions.md (100% confidence)
5. ✅ metadata-api-usage.md (100% App Router adoption)
6. ✅ async-server-components.md (100% App Router adoption)
7. ✅ i18n-with-app-router.md (33% confidence)

**Semgrep Rules:**
1. ✅ warn-getstaticprops-usage.yaml - Suggest migration to async server components
2. ✅ enforce-metadata-export.yaml - Require metadata in layout files
3. ✅ warn-next-seo-usage.yaml - Suggest Metadata API over next-seo
4. ✅ enforce-notfound-usage.yaml - Enforce notFound() for missing resources

**Analysis Files:**
1. ✅ project-structure-comparison.md - Cross-project router and organization analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual adoption rates
- ⏳ Semgrep rules validation pending

**Key Findings:**
- App Router adoption: 67% (helix v15, policy-node v14), kariusdx remains on Pages Router v12
- Route groups: 50% of App Router projects use route groups (helix: (frontend)/(studio))
- Nested layouts: 100% App Router projects use nested layouts (helix: 3, policy: 2)
- Metadata API: 100% App Router projects use generateMetadata() (replaces next-seo)
- Async server components: 100% App Router pages (20 total async pages)
- Component collocation: Hybrid model (shared + route-specific), helix uses route-specific folders
- i18n: 33% adoption (policy-node uses [lang] param + middleware)
- Critical gaps: kariusdx needs migration to App Router, zero loading.tsx usage, minimal error.tsx adoption

### Domain 7: Testing ✅ COMPLETE

**Duration:** ~2.5 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/testing/`
- 4 Semgrep rules in `tooling/semgrep/testing/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ why-testing-matters.md (0% confidence - gap pattern)
2. ✅ recommended-testing-stack.md (0% confidence - gap pattern)
3. ✅ unit-testing-utilities.md (0% confidence - gap pattern)
4. ✅ component-testing-patterns.md (0% confidence - gap pattern)
5. ✅ testing-async-server-components.md (0% confidence - gap pattern)
6. ✅ testing-api-routes.md (0% confidence - gap pattern)
7. ✅ testing-custom-hooks.md (0% confidence - gap pattern)
8. ✅ e2e-testing-critical-flows.md (0% confidence - gap pattern)

**Semgrep Rules:**
1. ✅ warn-utility-without-test.yaml - Warn on untested utility functions
2. ✅ warn-api-route-without-test.yaml - Warn on untested API routes
3. ✅ warn-component-without-test.yaml - Info on untested components
4. ✅ require-test-for-custom-hooks.yaml - Warn on untested custom hooks

**Analysis Files:**
1. ✅ testing-comparison.md - Cross-project testing gap analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence: 0% (gap pattern documented)
- ⏳ Semgrep rules validation pending

**Key Findings:**
- Universal gap: 0% testing infrastructure (no test files, no test runners, no E2E frameworks)
- Quality assurance exists: ESLint (100%), TypeScript (100%), Stylelint (67%), Husky (67%)
- Untested code: 313+ components, 33+ utility files (policy-node), 10+ API routes
- High-risk untested utilities: formatValue.ts (78 lines, i18n, 5 format types), csvToJson.ts (170+ lines, async streaming), replacePlaceholders.ts (regex, recursion, XSS risk)
- Custom validation irony: policy-node has validate:data script but validation script itself has no tests
- Recommended stack: Vitest (5-10x faster than Jest), Testing Library (accessibility-first), Playwright (Next.js App Router support), MSW (network mocking)
- Estimated test requirements: 40-60 unit tests for utilities, 50-80 component tests, 20-30 API integration tests, 10-15 E2E tests
- Industry standard: 70-80% code coverage, analyzed codebases have 0%

### Domain 8: Error Handling ⏳ IN PROGRESS (25% complete)

**Duration:** ~1 hour so far (estimated 2.5 hours total)
**Deliverables (Partial):**
- 1 RAG-optimized comparison analysis in `analysis/`
- 2/8 RAG-optimized documentation files in `docs/js-nextjs/error-handling/`
- 0/4 Semgrep rules pending

**Documentation Files Completed:**
1. ✅ custom-error-classes.md (33% confidence - policy-node pattern)
2. ✅ error-boundaries-react.md (0% confidence - gap pattern)

**Documentation Files Remaining:**
3. ⏳ app-router-error-handling.md (error.tsx, notFound(), global-error.tsx)
4. ⏳ structured-logging.md (Pino/Winston recommendations)
5. ⏳ error-tracking-services.md (Sentry/Rollbar integration)
6. ⏳ api-error-responses.md (NextResponse patterns)
7. ⏳ silent-failure-antipatterns.md (Helix JobBoard antipattern)
8. ⏳ error-context-wrapping.md (Policy-node pattern)

**Semgrep Rules (Pending):**
1. ⏳ warn-missing-error-boundary.yaml
2. ⏳ require-try-catch-async.yaml
3. ⏳ warn-silent-error-suppression.yaml
4. ⏳ enforce-api-error-response.yaml

**Analysis Files:**
1. ✅ error-handling-comparison.md - Cross-project error handling analysis

**Validation (Completed Docs):**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts

**Key Findings (So Far):**
- try/catch coverage: helix (1 block), kariusdx (5 blocks), policy-node (160 blocks)
- Custom error classes: Policy-node only (MunicipalityError, PhraseError, MunicipalitySearchError)
- Error boundaries: 0% adoption (critical gap - no React error boundaries exist)
- Error tracking: 0% adoption (no Sentry, Rollbar, Bugsnag)
- Structured logging: 0% adoption (no Winston, Pino)
- Silent failures: Helix JobBoard component (commented-out error logging, returns undefined)
- notFound() usage: helix (6 calls), policy-node (19 calls), kariusdx (0 calls)
- error.tsx files: Policy-node only (1 file)
- console.error usage: helix (1), kariusdx (0), policy-node (116)

**Resume Point:**
Continue with app-router-error-handling.md and remaining 5 documentation files, then generate 4 Semgrep rules.
