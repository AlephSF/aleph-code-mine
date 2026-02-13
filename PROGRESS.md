# Codebase Mining Progress

**Last Updated:** February 12, 2026
**Current Phase:** Phase 4 - WordPress Domains ⏳ IN PROGRESS
**Overall Progress:** Phase 2 complete (9/9), Phase 3 complete (4/4), Phase 4 in progress (5/8 domains complete)
**Next Phase:** Continue Phase 4 - WordPress Domains (3 more domains)

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
| Phase 2: Next.js Domains (9) | ✅ Complete (9/9) | 24 hours (done) |
| - Domain 1: Component Patterns | ✅ Complete | 2.5 hours (done) |
| - Domain 2: Data Fetching | ✅ Complete | 4 hours (done) |
| - Domain 3: TypeScript Conventions | ✅ Complete | 3 hours (done) |
| - Domain 4: Hooks & State | ✅ Complete | 2.5 hours (done) |
| - Domain 5: Styling | ✅ Complete | 3.5 hours (done) |
| - Domain 6: Project Structure | ✅ Complete | 3 hours (done) |
| - Domain 7: Testing | ✅ Complete | 2.5 hours (done) |
| - Domain 8: Error Handling | ✅ Complete | 3 hours (done) |
| - Domain 9: Tooling Config | ✅ Complete | 2.5 hours (done) |
| Phase 3: Sanity Domains (4) | ⏳ In Progress (3/4) | 8-12 hours |
| - Domain 1: Schema Definitions | ✅ Complete | 3 hours (done) |
| - Domain 2: GROQ Queries | ✅ Complete | 3 hours (done) |
| - Domain 3: Content Modeling | ✅ Complete | 3 hours (done) |
| - Domain 4: Studio Customization | ⏳ Next | 2-3 hours |
| Phase 4: WordPress Domains (8) | ⏳ In Progress (5/8) | 16-24 hours (15 hours done) |
| Phase 5: Cross-Stack (4) | ⏳ Pending | 8-12 hours |
| Phase 6: Tooling Outputs | ⏳ Pending | 8-12 hours |
| **TOTAL** | **62% Complete** | **50/83 hours done** |

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
> "Continue the codebase mining project. Start Phase 4, Domain 3: [Next WordPress Domain]"

**Completed Domains:**
- ✅ Phase 1: Structural Reconnaissance (all 8 repos)
- ✅ Phase 2, Domain 1: Component Patterns (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 2: Data Fetching (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 3: TypeScript Conventions (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 4: Hooks & State (Next.js) - 8 docs + 3 Semgrep rules
- ✅ Phase 2, Domain 5: Styling (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 6: Project Structure (Next.js) - 7 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 7: Testing (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 8: Error Handling (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 9: Tooling Config (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 3, Domain 1: Schema Definitions (Sanity) - 8 docs + 4 Semgrep rules
- ✅ Phase 3, Domain 2: GROQ Queries (Sanity) - 8 docs + 4 Semgrep rules
- ✅ Phase 3, Domain 3: Content Modeling (Sanity) - 8 docs + 4 Semgrep rules
- ✅ Phase 3, Domain 4: Studio Customization (Sanity) - 8 docs + 4 Semgrep rules
- ✅ Phase 4, Domain 1: WPGraphQL Architecture (WordPress) - 8 docs + 4 Semgrep rules
- ✅ Phase 4, Domain 2: Custom Post Types & Taxonomies (WordPress) - 8 docs + 9 Semgrep rules

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

### Domain 8: Error Handling ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/error-handling/`
- 4 Semgrep rules in `tooling/semgrep/error-handling/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ custom-error-classes.md (33% confidence - policy-node pattern)
2. ✅ error-boundaries-react.md (0% confidence - gap pattern)
3. ✅ app-router-error-handling.md (50% confidence - error.tsx, notFound(), global-error.tsx)
4. ✅ structured-logging.md (0% confidence - Pino/Winston recommendations)
5. ✅ error-tracking-services.md (0% confidence - Sentry/Rollbar integration)
6. ✅ api-error-responses.md (33% confidence - NextResponse patterns, custom error classes)
7. ✅ silent-failure-antipatterns.md (33% confidence - Helix JobBoard antipattern)
8. ✅ error-context-wrapping.md (33% confidence - Policy-node error wrapping pattern)

**Semgrep Rules:**
1. ✅ warn-missing-error-boundary.yaml - Warn when route segments lack error.tsx
2. ✅ require-try-catch-async.yaml - Require try/catch in async functions with await
3. ✅ warn-silent-error-suppression.yaml - Detect catch blocks without logging/tracking (Helix JobBoard antipattern)
4. ✅ enforce-api-error-response.yaml - Enforce proper NextResponse error format with status codes

**Analysis Files:**
1. ✅ error-handling-comparison.md - Cross-project error handling analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending (semgrep not installed)

**Key Findings:**
- try/catch coverage: helix (1 block - minimal), kariusdx (5 blocks - minimal), policy-node (160 blocks - comprehensive)
- Custom error classes with HTTP status codes: 33% (policy-node only: MunicipalityError, PhraseError, MunicipalitySearchError)
- Error boundaries (React): 0% adoption (critical gap - no React error boundaries)
- App Router error.tsx: 50% adoption (policy-node only, helix missing)
- global-error.tsx: 0% adoption (critical gap for root layout errors)
- not-found.tsx: 0% adoption (despite 25 notFound() calls)
- Error tracking services: 0% adoption (no Sentry, Rollbar, Bugsnag)
- Structured logging: 0% adoption (no Winston, Pino - only console.error)
- Silent failure antipattern: 33% (helix JobBoard: commented-out error logging, returns undefined, no user feedback)
- Error context wrapping: 33% (policy-node: 80% of utilities wrap errors with contextual information)
- notFound() usage: 67% (helix: 6 calls, policy-node: 19 calls, kariusdx: 0 calls)
- console.error usage: 33% (policy-node: 116 calls, helix: 1 call, kariusdx: 0 calls)

### Domain 9: Tooling Config ✅ COMPLETE

**Duration:** ~2.5 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/js-nextjs/tooling-config/`
- 4 Semgrep enforcement rules in `tooling/semgrep/tooling-config/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ eslint-shared-configs.md (67% confidence - @aleph configs)
2. ✅ typescript-strict-path-aliases.md (100% confidence - strict mode + @/* aliases)
3. ✅ stylelint-scss-configuration.md (100% confidence - all use stylelint)
4. ✅ husky-lint-staged-pattern.md (67% confidence - helix + policy-node)
5. ✅ npm-scripts-conventions.md (100% confidence - lint, lint:styles, build patterns)
6. ✅ node-version-management.md (67% confidence - .nvmrc usage)
7. ✅ eslint-flat-config-migration.md (33% confidence - policy-node only)
8. ✅ editorconfig-missing-pattern.md (0% confidence - gap pattern)

**Semgrep Rules:**
1. ✅ warn-missing-editorconfig.yaml - Warn if .editorconfig missing
2. ✅ require-strict-typescript.yaml - Require strict: true in tsconfig.json
3. ✅ warn-no-husky.yaml - Warn if .husky directory missing
4. ✅ enforce-path-alias.yaml - Require @/* path alias in tsconfig.json

**Analysis Files:**
1. ✅ tooling-config-comparison.md - Cross-project tooling analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual adoption rates

**Key Findings:**
- ESLint adoption: 100% (helix/policy-node use @aleph shared configs, kariusdx uses Airbnb)
- TypeScript strict mode: 100% (all projects use "strict": true)
- stylelint for SCSS: 100% (helix/policy-node use @aleph shared configs)
- Husky pre-commit hooks: 67% (helix + policy-node, kariusdx has no enforcement)
- lint-staged: 33% (policy-node only - runs linting on changed files)
- TypeScript pre-commit check: 33% (policy-node only - tsc --noEmit)
- .nvmrc: 67% (helix v18.17.0, policy-node v22.13.1, kariusdx missing)
- .editorconfig: 0% (critical gap - no IDE consistency enforcement)
- ESLint flat config: 33% (policy-node only - ESLint 9+ format)
- Prettier explicit config: 33% (policy-node only, others implicit via @aleph)
- Path aliases (@/*): 67% (helix + policy-node, kariusdx missing)
- Turbopack in dev: 33% (policy-node only - Next.js 14+ feature)
- Bundle analyzer: 33% (helix only - build:analyze script)
- Storybook: 33% (helix only)

**Critical Gaps Identified:**
- Kariusdx has no Husky (developers can commit broken code)
- No .editorconfig files (IDE settings may differ: indentation, line endings)
- Kariusdx has no .nvmrc (team may use different Node versions)
- Only policy-node runs TypeScript type-checking in pre-commit (helix skips tsc --noEmit)

---

## Phase 4: WordPress Domains ⏳ IN PROGRESS

**Status:** 5 of 8 domains complete (62.5%)
**Focus:** Extract patterns from 2 WordPress repositories (airbnb VIP multisite, thekelsey-wp)

### Domain 1: WPGraphQL Architecture ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/php-wordpress/wpgraphql-architecture/`
- 4 Semgrep enforcement rules in `tooling/semgrep/wpgraphql-architecture/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ acf-field-graphql-configuration.md (100% confidence - 193 ACF fields)
2. ✅ conditional-plugin-loading-multisite.md (100% confidence)
3. ✅ cpt-taxonomy-graphql-registration.md (100% confidence)
4. ✅ custom-graphql-field-registration.md (100% confidence - 362 registrations)
5. ✅ graphql-security-dos-protection.md (100% confidence)
6. ✅ minimal-headless-theme-pattern.md (100% confidence)
7. ✅ polylang-graphql-integration.md (100% confidence)
8. ✅ vip-block-data-api-filters.md (100% confidence)

**Semgrep Rules:**
1. ✅ require-show-in-graphql.yaml (2 rules: CPT + taxonomy GraphQL exposure)
2. ✅ require-graphql-register-types-hook.yaml (2 rules: correct hook timing)
3. ✅ warn-graphql-dos-no-limits.yaml (3 rules: depth, batch, cost limits)
4. ✅ enforce-acf-graphql-naming.yaml (3 rules: field config, camelCase, descriptions)

**Analysis Files:**
1. ✅ wpgraphql-architecture-comparison.md (51 query files analyzed)

**Key Findings:**
- WPGraphQL adoption: 50% (airbnb 100% GraphQL-first, thekelsey 0% REST-only)
- GraphQL security: airbnb implements query depth limits (15), batch limits (10), 10KB query size limit
- ACF GraphQL integration: 193 fields with custom GraphQL names across 23 field groups
- Custom field registration: 362 `register_graphql_field()` calls
- Polylang multilingual: Language filtering, translations, locale switching via GraphQL
- Headless theme pattern: Minimal 200-line theme for admin-only WordPress

### Domain 2: Custom Post Types & Taxonomies ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/php-wordpress/custom-post-types-taxonomies/`
- 9 Semgrep enforcement rules in `tooling/semgrep/custom-post-types-taxonomies/`
- 1 cross-project comparison analysis (20 sections)

**Documentation Files:**
1. ✅ namespaced-cpt-registration.md (100% confidence)
2. ✅ class-based-cpt-organization.md (100% confidence)
3. ✅ hierarchical-taxonomies-pattern.md (100% confidence)
4. ✅ rest-api-configuration.md (50% confidence - architecture-dependent)
5. ✅ rewrite-slug-best-practices.md (100% confidence)
6. ✅ cpt-label-conventions.md (100% confidence)
7. ✅ menu-icon-positioning.md (50% confidence)
8. ✅ activation-hook-rewrite-flush.md (50% confidence)

**Semgrep Rules:**
1. ✅ require-cpt-namespace-prefix.yaml (2 rules: CPT + taxonomy prefixing)
2. ✅ warn-missing-text-domain.yaml (2 rules: i18n translation + consistency)
3. ✅ require-rest-base-if-show-in-rest.yaml (2 rules: REST base + controller)
4. ✅ warn-missing-rewrite-flush.yaml (3 rules: activation hooks + performance)

**Analysis Files:**
1. ✅ custom-post-types-taxonomies-comparison.md (20 sections, 13,698 chars)

**Key Findings:**
- CPT/Taxonomy registration: 8 custom post types, 7 custom taxonomies analyzed
- Namespace prefixing: 100% adoption (`bnb_`, `kelsey_` prefixes)
- Class-based organization: 100% adoption (separate vs monolithic patterns)
- Hierarchical taxonomies: 100% adoption (0% flat/tag-style)
- REST API: 50% adoption (thekelsey 100%, airbnb 20% GraphQL-first)
- Rewrite flush: 50% implement activation hooks (thekelsey best practice)
- Label i18n: 50% complete translation (airbnb 100%, thekelsey 0% for CPTs)
- Menu icons: 100% Dashicons, airbnb reuses icon for 80% of CPTs (UX issue)

### Domain 3: ACF (Advanced Custom Fields) Patterns ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/php-wordpress/acf-patterns/`
- 4 Semgrep enforcement rules in `tooling/semgrep/acf-patterns/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ acf-json-version-control.md (100% confidence)
2. ✅ field-group-organization.md (100% confidence)
3. ✅ conditional-logic-patterns.md (100% confidence)
4. ✅ custom-field-location-rules.md (100% confidence)
5. ✅ acf-flexible-content-pattern.md (100% confidence)
6. ✅ acf-clone-fields.md (50% confidence)
7. ✅ acf-options-pages.md (100% confidence)
8. ✅ acf-field-naming-conventions.md (100% confidence)

**Semgrep Rules:**
1. ✅ require-acf-json-directory.yaml (2 rules: JSON sync + save point)
2. ✅ enforce-field-key-prefix.yaml (2 rules: field + group key naming)
3. ✅ warn-get-field-without-check.yaml (3 rules: null checks + have_rows loops)
4. ✅ require-location-rules.yaml (2 rules: location + conditional logic)

**Analysis Files:**
1. ✅ phase4-domain3-acf-patterns-comparison.md

**Key Findings:**
- ACF adoption: 100% (both repos use ACF Pro for custom fields)
- JSON sync: 100% adoption (23 field groups in airbnb, 8 in thekelsey)
- Field groups: 31 total field groups across both repos
- Flexible content: 100% adoption for page builders (17 layouts in airbnb)
- Clone fields: 50% adoption (airbnb uses for SEO/meta reusability)
- Options pages: 100% adoption (site settings, theme options)
- Field naming: 100% snake_case (0 camelCase usage)
- Location rules: 100% proper configuration (post type, taxonomy, page template targeting)

### Domain 4: VIP Patterns ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/php-wordpress/vip-patterns/`
- 4 Semgrep enforcement rules in `tooling/semgrep/vip-patterns/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ vip-config-php-structure.md (100% confidence)
2. ✅ client-mu-plugins-pattern.md (100% confidence)
3. ✅ conditional-plugin-loading.md (100% confidence)
4. ✅ graphql-security-patterns.md (100% confidence)
5. ✅ vip-environment-constants.md (100% confidence)
6. ✅ varnish-cache-control.md (100% confidence)
7. ✅ multisite-blog-switching.md (100% confidence)
8. ✅ vip-redirect-patterns.md (100% confidence)

**Semgrep Rules:**
1. ✅ wpcom-vip-load-plugin.yml (3 rules: enforce VIP helper, detect scattered loading, document blog_id)
2. ✅ restore-current-blog.yml (4 rules: missing restore, exception safety, loop performance, redundant switches)
3. ✅ graphql-security.yml (6 rules: query size, complexity, deduplication, introspection, logging)
4. ✅ varnish-cache-control.yml (7 rules: SAML headers, early hooks, cookies, global caching, healthcheck, no-store, vary)

**Analysis Files:**
1. ✅ phase4-domain4-vip-patterns-comparison.md

**Key Findings:**
- VIP adoption: 100% (airbnb is WordPress VIP Go multisite)
- vip-config.php: 100% usage (early-stage redirects, constants, proxy IP verification)
- Client MU-plugins: 612 PHP files (security, performance, VIP integrations)
- wpcom_vip_load_plugin(): 11 instances (conditional plugin loading by blog_id)
- GraphQL security: Multi-layer DoS protection (10KB query size, 500 complexity, field deduplication)
- VIP environment constants: 11 VIP_GO_ENV checks, 5 WPCOM_IS_VIP_ENV checks
- Cache-Control headers: SAML SSO Varnish bypass, cookie prefixing (wordpress_*)
- Multisite blog switching: 52 get_current_blog_id(), ~30 switch_to_blog() calls
- VIP redirects: 5+ redirect configurations covering 15+ domains (consolidated array pattern)
- VIP proxy IP verification: HTTP_TRUE_CLIENT_IP + verification key for real client detection

### Domain 5: Security & Code Standards ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/php-wordpress/security-code-standards/`
- 4 Semgrep enforcement rules in `tooling/semgrep/security-code-standards/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ phpcs-vip-configuration.md (100% confidence - WordPressVIPMinimum + WordPress-VIP-Go)
2. ✅ input-sanitization-patterns.md (100% confidence - 623 sanitization calls)
3. ✅ output-escaping-patterns.md (100% confidence - 5,841 escaping calls)
4. ✅ nonce-verification-patterns.md (100% confidence - 462 nonce operations)
5. ✅ capability-check-patterns.md (100% confidence - 1,166 capability checks)
6. ✅ sql-security-patterns.md (69% confidence - 291 prepared statements)
7. ✅ vip-security-patterns.md (78% confidence - VIP-safe functions)
8. ✅ csrf-protection-patterns.md (100% confidence - multi-layer protection)

**Semgrep Rules:**
1. ✅ input-sanitization.yml (4 rules: unsanitized $_POST/$_GET, absint for IDs, password anti-pattern)
2. ✅ output-escaping.yml (4 rules: unescaped echo, wrong context, late escaping, trust database)
3. ✅ nonce-verification.yml (4 rules: admin_post, AJAX handlers, nonce before capability, generic actions)
4. ✅ sql-security.yml (6 rules: unprepared queries, concatenation, prefer WP functions, esc_like, eval, VIP file_get_contents)

**Analysis Files:**
1. ✅ phase4-domain5-security-code-standards-comparison.md

**Key Findings:**
- PHPCS adoption: 100% airbnb (WordPressVIPMinimum + WordPress-VIP-Go), 0% thekelsey
- Input sanitization: 623 calls total (sanitize_text_field 385, sanitize_key 157, sanitize_title 76)
- Output escaping: 5,841 calls total (esc_html 2,105, esc_attr 2,105, esc_url 1,121, wp_kses_post 384)
- Nonce operations: 462 calls (wp_create_nonce 142, wp_verify_nonce 119, check_ajax_referer 77, check_admin_referer 124)
- Capability checks: 1,166 calls (current_user_can 574, user_can 592)
- SQL security: 291 prepared statements (69% coverage), 127 unprepared queries (31% SQL injection risk)
- VIP-safe functions: 31 calls (wpcom_vip_file_get_contents 9, vip_safe_wp_remote_get 22)
- Critical gaps: 48 eval() calls, 677 unsanitized $_POST, 519 unsanitized $_GET, 127 unprepared SQL

### Remaining WordPress Domains (3)

**Priority order based on Phase 1 findings:**

5. **Theme Structure & Organization** - Medium priority
   - Sage framework (Roots), Blade templating
   - Traditional PHP themes
   - Estimated: 2-3 hours

6. **Security & Code Standards** - High priority
   - PHPCS (VIP WordPress standards)
   - Input sanitization, output escaping
   - Estimated: 2-3 hours

7. **Multisite Patterns** - Medium priority
   - Conditional plugin loading by blog_id
   - Network-wide vs site-specific functionality
   - Estimated: 2-3 hours

8. **Block Development (Gutenberg)** - Medium priority
   - Custom blocks (airbnb-policy-blocks: 12 custom + 15 ACF blocks)
   - Block registration patterns
   - Estimated: 2-3 hours

---

## Phase 3: Sanity.js Domains ✅ COMPLETE

**Status:** 1 of 4 domains complete (25%)
**Focus:** Extract patterns from 3 Sanity.js repositories (helix v3, kariusdx v2, ripplecom v4)

### Domain 1: Schema Definitions ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/sanity/schema-definitions/`
- 4 Semgrep enforcement rules in `tooling/semgrep/schema-definitions/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ modern-definetype-api.md (33% confidence - ripplecom v4 only)
2. ✅ field-groups-organization.md (12% confidence - low adoption)
3. ✅ validation-rules.md (100% confidence - universal pattern)
4. ✅ icon-customization.md (79% confidence - high adoption)
5. ✅ preview-configuration.md (52% confidence - medium adoption)
6. ✅ reference-fields-relationships.md (100% confidence - universal pattern)
7. ✅ seo-metadata-objects.md (100% confidence - universal pattern)
8. ✅ conditional-field-visibility.md (33% confidence - ripplecom only)

**Semgrep Rules:**
1. ✅ prefer-definetype-api.yaml - Suggest modern defineType() over object literals (v3+)
2. ✅ require-validation-for-required.yaml - Warn when required fields lack additional constraints
3. ✅ warn-missing-preview-config.yaml - Suggest preview config for document schemas
4. ✅ require-reference-to-array.yaml - Enforce 'to' array in reference fields

**Analysis Files:**
1. ✅ sanity-schema-comparison.md - Cross-project schema API and pattern analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending (semgrep not installed)

**Key Findings:**
- **API Evolution**: v2 → v3 → v4 shows significant breaking changes
- **Modern API adoption**: 33% (only ripplecom v4 uses defineType/defineField)
- **Validation rules**: 100% adoption (238 max(), 75 min() constraints in ripplecom)
- **Preview config**: 52% adoption across 147 schemas (UX improvement opportunity)
- **Field groups**: 12% adoption (low usage, primarily in complex schemas)
- **Icon customization**: 79% adoption (37 icons from @sanity/icons, 80 from react-icons)
- **Reference fields**: 100% proper configuration (156 references, all with 'to' array)
- **SEO metadata**: 100% adoption (dedicated seo/metadata objects in all projects)
- **Conditional visibility**: 33% adoption (ripplecom only, 18 hidden fields)

**Version-Specific Patterns:**
- **v2 (kariusdx)**: Object-literal pattern only, no modern API support
- **v3 (helix)**: Supports modern API but uses v2-compatible object literals for backward compatibility
- **v4 (ripplecom)**: Full modern API adoption (651 defineType/defineField instances)

**Critical Gaps Identified:**
- Helix (v3.10.0) not leveraging modern defineType API despite version support
- Low field groups adoption (12%) despite UX benefits for complex schemas
- 48% of document schemas lack preview configuration (poor Studio UX)

### Domain 3: Content Modeling ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/sanity/content-modeling/`
- 4 Semgrep enforcement rules in `tooling/semgrep/content-modeling/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ page-builder-architecture.md (67% confidence)
2. ✅ global-singleton-documents.md (33% confidence)
3. ✅ content-block-organization.md (67% confidence)
4. ✅ rich-text-configuration.md (100% confidence)
5. ✅ content-hierarchies.md (33% confidence)
6. ✅ content-block-naming-conventions.md (100% confidence)
7. ✅ legacy-content-migration.md (33% confidence)
8. ✅ reusable-content-objects.md (100% confidence)

**Semgrep Rules:**
1. ✅ require-seo-object.yaml - Require SEO object in document types
2. ✅ prefer-object-for-reusable-content.yaml - Enforce object type for reusable structures
3. ✅ warn-legacy-schema-usage.yaml - Warn on deprecated legacy schema types
4. ✅ enforce-link-validation.yaml - Enforce conditional link validation

**Analysis Files:**
1. ✅ content-modeling-comparison.md - Cross-project content architecture analysis

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- **Page Builder Adoption**: 67% (kariusdx v2 + ripplecom v4 use modular page builders)
  - Flat content array pattern (ripplecom v4): 33%
  - Nested section wrapper pattern (kariusdx v2): 33%
  - Minimal content structure (helix v3): 33%
- **Global/Singleton Documents**: 33% (ripplecom v4 only - 6 global documents)
- **Content Block Organization**: 67% use dedicated folders (components/ or builderBlocks/)
  - Ripplecom v4: 15 components in components/ folder
  - Kariusdx v2: 20 builder blocks in builderBlocks/ folder
- **Rich Text Configuration**: 100% use Portable Text
  - Object wrapper pattern (ripplecom v4): 33% (prevents nested array issues)
  - Direct array pattern (kariusdx v2 + helix v3): 67%
- **Content Hierarchies**: 33% (helix v3 only - hierarchical pages with parent references)
- **Flat Taxonomies**: 67% (kariusdx v2 + ripplecom v4 use categories/tags)
- **Naming Conventions**: 100% use camelCase
  - Purpose-driven names (ripplecom v4): heroSection, textSection
  - Descriptive technical names (kariusdx v2): pageSection, imageCarousel
- **Legacy Content Migration**: 33% (ripplecom v4 maintains 16 legacy sections in legacy/ folder)
- **Reusable Objects**: 100% adoption
  - SEO objects: 100%
  - Link objects: 67%
  - Image objects: 67%
  - Navigation items: 67%

**Content Block Counts:**
- Helix v3: 2 documents + 2 objects (minimal)
- Kariusdx v2: 11 documents + 20 builder blocks + 23 objects
- Ripplecom v4: 16 documents + 15 components + 6 globals + 16 legacy sections + 15 objects

**Critical Patterns:**
- Rich text wrapped in object type prevents nested array TypeErrors (ripplecom v4)
- Dual schema support enables zero-downtime content migration (legacy + modern)
- Internal/external link objects prevent broken links and improve UX
- Hierarchical slugs auto-generate from parent relationships (helix v3)

**Critical Gaps:**
- Most projects lack global/singleton documents (67% - no globals)
- Content hierarchies rarely used (67% - flat taxonomies only)
- Legacy migration strategy missing in 67% of projects

### Domain 2: GROQ Queries ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/sanity/groq-queries/`
- 4 Semgrep enforcement rules in `tooling/semgrep/groq-queries/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ query-file-organization.md (100% confidence)
2. ✅ modern-definequery-api.md (33% confidence)
3. ✅ reusable-query-partials.md (100% confidence)
4. ✅ reference-expansion.md (100% confidence)
5. ✅ projection-composition.md (100% confidence)
6. ✅ conditional-field-expansion.md (100% confidence)
7. ✅ ordering-filtering-pagination.md (67% confidence)
8. ✅ typescript-query-typing.md (100% confidence)

**Semgrep Rules:**
1. ✅ prefer-definequery-v4.yaml
2. ✅ require-image-metadata.yaml
3. ✅ warn-missing-spread-before-conditional.yaml
4. ✅ recommend-server-side-ordering.yaml

**Analysis Files:**
1. ✅ groq-queries-comparison.md (51 query files analyzed)

**Key Findings:**
- Modern defineQuery API: Ripplecom 94%, others use groq template
- Reference expansion: 134 instances across all projects
- Image partials: 100% adoption
- TypeScript typing: 100% adoption

---

## Phase 2 Summary: Next.js Domains ✅ COMPLETE

**Total Duration:** ~24 hours
**Domains Completed:** 9/9 (100%)
**Total Documentation Files:** 71 RAG-optimized markdown files
**Total Semgrep Rules:** 35 enforcement rules
**Total Analysis Files:** 9 cross-project comparisons

**Deliverables:**
- Component Patterns (8 docs + 4 rules)
- Data Fetching (8 docs + 4 rules)
- TypeScript Conventions (8 docs + 4 rules)
- Hooks & State (8 docs + 3 rules)
- Styling (8 docs + 4 rules)
- Project Structure (7 docs + 4 rules)
- Testing (8 docs + 4 rules)
- Error Handling (8 docs + 4 rules)
- Tooling Config (8 docs + 4 rules)

**Key Universal Patterns (100% Adoption):**
- TypeScript strict mode
- SCSS + CSS Modules
- 2-space indentation
- ISR revalidation
- Default exports for components
- Multiple useState over single state object
- Design system structure (_colors, _typography, _spacing)
- npm scripts (dev, build, start, lint)
- stylelint for SCSS

**Critical Gaps Identified:**
- Zero testing infrastructure (0% adoption)
- Zero error boundaries (0% adoption)
- Zero .editorconfig files (0% adoption)
- Minimal custom hooks (4 total across all projects)
- No type guards despite extensive API parsing
- Kariusdx lacks Husky pre-commit hooks
- Only policy-node runs tsc --noEmit before commit


### Domain 4: Studio Customization ✅ COMPLETE

**Duration:** ~3 hours
**Deliverables:**
- 8 RAG-optimized documentation files in `docs/sanity/studio-customization/`
- 4 Semgrep enforcement rules in `tooling/semgrep/studio-customization/`
- 1 cross-project comparison analysis

**Documentation Files:**
1. ✅ desk-structure-customization.md (67% confidence)
2. ✅ singleton-document-management.md (67% confidence)
3. ✅ presentation-tool-configuration.md (33% confidence)
4. ✅ custom-document-actions.md (33% confidence)
5. ✅ plugin-ecosystem-patterns.md (100% confidence)
6. ✅ custom-branding-theming.md (33% confidence)
7. ✅ custom-validation-utilities.md (33% confidence)
8. ✅ custom-ordering-configurations.md (33% confidence)
9. ✅ authentication-customization.md (33% confidence - SAML SSO)

**Semgrep Rules:**
1. ✅ prefer-structure-resolver.yaml
2. ✅ require-singleton-template-filtering.yaml
3. ✅ warn-missing-vision-tool.yaml
4. ✅ prefer-exclusion-filter-structure.yaml

**Analysis Files:**
1. ✅ studio-customization-comparison.md

**Validation:**
- ✅ All sections under 1,500 characters
- ✅ No pronoun-leading sentences
- ✅ All required frontmatter fields present
- ✅ Source confidence calculated from actual pattern counts
- ⏳ Semgrep rules validation pending

**Key Findings:**
- **Desk Structure Customization**: 67% adoption (kariusdx v2 + ripplecom v4)
- **Singleton Management**: 67% adoption (template filtering + desk grouping)
- **Vision Tool**: 100% adoption (essential dev tool)
- **Presentation Tool**: 33% adoption (ripplecom v4 only - requires v4+)
- **Media Plugin**: 67% adoption (enhanced asset management)
- **Custom Document Actions**: 33% adoption (kariusdx only - auto-slug + hierarchical paths)
- **Custom Branding**: 33% adoption (kariusdx only - logo + CSS overrides)
- **SAML SSO**: 33% adoption (ripplecom only - Okta integration)
- **Custom Orderings**: 33% adoption (ripplecom only - 13 orderings across 7 document types)

**Version-Specific Patterns:**
- **v2 (kariusdx)**: Parts system (deprecated), legacy structure builder, custom document views
- **v3 (helix)**: defineConfig API, minimal customization (2 plugins only)
- **v4 (ripplecom)**: Modern API, presentationTool, SAML SSO, 6 plugins

**Critical Gaps:**
- Helix lacks custom desk structure (no content organization)
- Kariusdx uses deprecated v2 APIs (migration needed to v3/v4)
- Presentation Tool underutilized (only ripplecom uses visual editing)
- No shared plugin strategy across projects

---

## Phase 3 Summary: Sanity.js Domains ✅ COMPLETE

**Total Duration:** ~12 hours
**Domains Completed:** 4/4 (100%)
**Total Documentation Files:** 32 RAG-optimized markdown files
**Total Semgrep Rules:** 16 enforcement rules
**Total Analysis Files:** 4 cross-project comparisons

**Deliverables:**
- Schema Definitions (8 docs + 4 rules)
- GROQ Queries (8 docs + 4 rules)
- Content Modeling (8 docs + 4 rules)
- Studio Customization (8 docs + 4 rules)

**Key Universal Patterns (67-100% Adoption):**
- Validation rules (100%)
- Reference field relationships (100%)
- SEO metadata objects (100%)
- Reusable query partials (100%)
- TypeScript query typing (100%)
- Portable Text for rich content (100%)
- Vision Tool for development (100%)
- Custom desk structure (67%)
- Singleton document management (67%)
- Media plugin (67%)

**Version-Specific Patterns:**
- **v2 (kariusdx)**: Object-literal schemas, parts system, legacy plugins
- **v3 (helix)**: defineType API, minimal Studio customization
- **v4 (ripplecom)**: Modern APIs, presentationTool, SAML SSO, extensive Studio customization

**Critical Findings:**
- Helix (v3) not leveraging modern defineType/defineField APIs
- Kariusdx (v2) requires migration to v3/v4 (breaking changes)
- Field groups underutilized (12% adoption)
- Presentation Tool adoption low (33% - only v4 feature)
- No standardized plugin set across projects

**Next Steps:**
- Phase 4: WordPress Domains (8 domains planned)
- Document WP patterns: theme structure, custom post types, ACF, hooks, security


