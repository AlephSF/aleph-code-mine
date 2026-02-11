# Updated Plan: Mine Codebases and Generate RAG-Optimized Standards Docs

**Last Updated:** February 10, 2026
**Status:** Phase 1 Complete, Phase 2 Ready

---

## Changes from Original Plan

### Phase 1 Adjustments
✅ **Completed successfully** with minor adjustments:
- Agents were in read-only mode, so structural summaries were extracted and saved manually
- All 8 repos analyzed in parallel using Explore agents
- Generated 9 markdown files (8 repo analyses + 1 summary)

### Phase 2 Adjustments

**Original Plan:** Analyze all domains across all stacks simultaneously
**Updated Plan:** One stack at a time, one domain at a time

**Reason for Change:**
- Phase 1 revealed significant differences between Next.js versions (v12, v14, v15)
- Better to deeply understand one domain before moving to next
- Easier to identify patterns when focusing on single domain
- Prevents context switching and ensures comprehensive analysis

**New Domain Order (Next.js):**

1. **Component patterns** (HIGH) - 313 total components, need consistency
2. **Error handling** (HIGH) - Testing gap suggests error handling gaps too
3. **Data fetching** (HIGH) - ISR/SSR/SSG mix needs unified guidance
4. **TypeScript conventions** (HIGH) - Type vs interface, generics, strictness
5. **Hooks & state** (MEDIUM) - Custom hooks, useEffect patterns
6. **Project structure** (MEDIUM) - App Router vs Pages Router differences
7. **Styling** (MEDIUM) - Already consistent, document best practices
8. **Testing** (HIGH) - Gap documentation and guidance
9. **Tooling config** (LOW) - ESLint/Prettier mostly consistent

### Phase 3-5 Adjustments

**Original Plan:** Do all domains for all stacks before generating docs
**Updated Plan:** Generate docs immediately after each domain analysis

**Reason:**
- Findings fresh in mind
- Can validate output format early
- Can test Semgrep rules against source repos immediately
- Iterative approach allows course correction

---

## Revised Execution Strategy

### Per-Domain Workflow (2-3 hours each)

```
1. Quantitative Analysis (15-30 min)
   ├── grep/ripgrep for pattern counts
   ├── Run scc for complexity metrics
   └── Generate frequency data

2. Qualitative Analysis (30-60 min)
   ├── Read representative examples
   ├── Identify common vs divergent patterns
   └── Note version-specific variations

3. Cross-Project Comparison (15-30 min)
   ├── Build comparison matrix
   ├── Calculate percentages (de facto standards)
   └── Flag discussion points

4. Generate RAG-Optimized Docs (30-45 min)
   ├── One doc per specific rule/pattern
   ├── Follow template strictly (<1500 chars/section)
   ├── Real code examples with line numbers
   └── Calculate source_confidence percentages

5. Generate Semgrep Rules (15-30 min, if applicable)
   ├── Write YAML rule for enforceable patterns
   ├── Test against source repos
   └── Verify no false positives
```

### Parallel Work Opportunities

Can run in parallel:
- Quantitative analysis (grep multiple patterns at once)
- Reading existing docs while agents explore code

Cannot parallel:
- Qualitative analysis (needs focused attention)
- Writing output docs (needs synthesis)

---

## Phase 2: Next.js Domains (UPDATED)

### Domain 1: Component Patterns

**Files to Analyze:**
- helix-dot-com-next/app/(frontend)/components/*.tsx (188 files)
- kariusdx-next/components/*.tsx (85 files)
- policy-node/src/components/*.tsx (40+ files)

**Patterns to Extract:**
- Named vs default exports
- Props interface naming (ComponentProps vs ComponentProperties vs Props)
- Props destructuring patterns
- Children prop patterns
- Component file structure (single vs index.tsx)
- JSX return patterns (fragment vs element)
- Server vs Client components (helix, policy only - Next.js 13+)
- Component composition patterns

**Tools:**
- `grep -r "export default" --count`
- `grep -r "export const" --count`
- `grep -r "interface.*Props"`
- `grep -r "'use client'"`
- `grep -r "'use server'"`
- `npx react-scanner` (component usage frequency)

**Expected Output Docs (docs/js-nextjs/component-patterns/):**
- named-exports-for-components.md
- props-interface-naming.md
- props-destructuring.md
- component-file-organization.md
- server-vs-client-components.md (Next.js 13+)
- children-prop-patterns.md
- component-composition.md

**Semgrep Rules:**
- Enforce named exports
- Require Props interface for components
- Detect missing 'use client' for client-only APIs

---

### Domain 2: Error Handling

**Files to Analyze:**
- All .tsx/.ts files with try/catch blocks
- error.tsx files (App Router)
- Error boundary components
- API route error handling

**Patterns to Extract:**
- Try/catch usage and patterns
- Error boundary implementation
- User-facing error messages
- Error logging patterns
- API error handling (fetch failures)
- Validation error handling

**Tools:**
- `grep -r "try {" --count`
- `grep -r "catch" --count`
- `grep -r "ErrorBoundary"`
- `grep -r "error.tsx"`
- `grep -r "throw new Error"`

**Expected Output Docs (docs/js-nextjs/error-handling/):**
- try-catch-patterns.md
- error-boundaries.md
- user-facing-errors.md
- api-error-handling.md
- error-logging.md

**Semgrep Rules:**
- Detect try blocks without catch
- Detect empty catch blocks
- Require error logging in catch blocks

---

### Domain 3: Data Fetching

**Files to Analyze:**
- Server Components with async fetch (helix, policy)
- getServerSideProps (kariusdx - Pages Router)
- getStaticProps / getStaticPaths (kariusdx)
- API routes
- Cache configurations

**Patterns to Extract:**
- Fetch patterns (fetch vs axios vs client libraries)
- Caching strategies (ISR, SWR, React Query)
- Error handling in data fetching
- Loading states
- Server vs client data fetching
- Revalidation patterns

**Tools:**
- `grep -r "fetch(" --count`
- `grep -r "getServerSideProps"`
- `grep -r "getStaticProps"`
- `grep -r "revalidate"`
- `grep -r "cache:"`

**Expected Output Docs (docs/js-nextjs/data-fetching/):**
- server-side-fetch-patterns.md
- isr-and-revalidation.md
- client-side-fetch-patterns.md
- cache-strategies.md
- loading-states.md
- error-handling-in-fetch.md

**Semgrep Rules:**
- Require error handling for fetch calls
- Detect missing revalidate config
- Require loading states for async operations

---

### Domains 4-9: Similar Structure

Each domain follows same workflow:
1. Identify files to analyze
2. Run quantitative tools
3. Extract patterns
4. Build comparison matrix
5. Generate docs
6. Write Semgrep rules (if applicable)

---

## Phase 3: Sanity.js Domains

### Adjusted Domain List

1. **Schema definitions** (HIGH) - 78 schemas in ripplecom, patterns vary widely
2. **GROQ queries** (HIGH) - 14+ queries in kariusdx, need consistent patterns
3. **Content modeling** (MEDIUM) - References, slugs, validation patterns
4. **Studio customization** (LOW) - Custom components, desk structure (varies by version)

**Version-Specific Considerations:**
- v2 (kariusdx) - Legacy patterns, document for migration guidance
- v3 (helix) - Current stable, focus here
- v4 (ripplecom) - Latest, include new features (Presentation Tool)

---

## Phase 4: WordPress Domains

### Adjusted Domain List

1. **Security** (HIGH) - Nonces, escaping, sanitization, capability checks
2. **Hook patterns** (HIGH) - add_action/add_filter usage, priority patterns
3. **Architecture** (HIGH) - Theme/plugin structure, autoloading
4. **Templating** (MEDIUM) - Blade (Sage) vs traditional PHP
5. **Custom post types** (MEDIUM) - Registration patterns, meta fields
6. **REST API** (MEDIUM) - Endpoint registration, permissions
7. **Database** (MEDIUM) - WP_Query, custom queries, caching
8. **PHP standards** (LOW) - Naming, PHPCS compliance (already documented)

**Focus:**
- airbnb: GraphQL patterns, VIP-specific optimizations
- thekelsey: Sage/Blade patterns, ACF integration

---

## Phase 5: Cross-Stack Domains

### Updated List

1. **Git conventions** (HIGH) - Commit messages, branch naming, PR patterns
2. **Error handling** (MEDIUM) - Compare patterns across stacks
3. **Environment config** (MEDIUM) - .env patterns, config management
4. **API integration** (LOW) - How WP and Next.js communicate (airbnb only)

---

## Phase 6: Tooling Outputs

**Priority Order:**

1. **Doc validation script** (HIGH) - Immediate need to validate output docs
   - Check frontmatter presence
   - Validate section character counts (<1500)
   - Check for pronoun violations
   - Verify code examples have prose

2. **Semgrep rules** (HIGH) - Generated throughout Phase 2-5
   - Collect all rules
   - Organize by domain
   - Create root .semgrep.yml config
   - Test against all repos

3. **Linter doc generators** (MEDIUM) - Parse ESLint/PHPCS configs
   - ESLint config → markdown
   - PHPCS config → markdown
   - Regenerate on config changes

---

## Success Metrics

### Quality Metrics
- [ ] All output docs pass validation script
- [ ] Semgrep rules tested with <5% false positive rate
- [ ] Source confidence >70% for all "enforced" patterns
- [ ] All sections <1500 characters
- [ ] No section starts with pronouns

### Coverage Metrics
- [ ] 100% of identified domains analyzed
- [ ] All repos represented in each domain (where applicable)
- [ ] Existing docs gaps identified and filled
- [ ] Existing docs drift identified and documented

### Deliverable Metrics
- [ ] 50+ RAG-optimized docs generated
- [ ] 20+ Semgrep rules created and tested
- [ ] Doc validation script working
- [ ] Linter doc generator working

---

## Risk Mitigation

### Risk: Pattern Inconsistency Across Versions
**Mitigation:** Document version-specific patterns separately, provide migration guides

### Risk: Low Pattern Frequency (Not "De Facto Standards")
**Mitigation:** Flag as "Recommendation" not "Convention", include rationale from industry best practices

### Risk: Contradictory Patterns
**Mitigation:** Present comparison matrix, let team decide, document decision

### Risk: Scope Creep
**Mitigation:** Stick to one domain at a time, time-box each domain to 3 hours max

---

## Next Session Checklist

Before starting Phase 2, Domain 1:

1. [ ] Install semgrep: `brew install semgrep`
2. [ ] Read PROGRESS.md to recall context
3. [ ] Review analysis/PHASE1-SUMMARY.md for key findings
4. [ ] Create first domain directory: `mkdir -p docs/js-nextjs/component-patterns`
5. [ ] Start with quantitative analysis (grep patterns)
