# Aleph Code Mine - AI Assistant Context

## Project Purpose

Extract coding standards from real codebases and generate RAG-optimized documentation (for BGE-large-en-v1.5 + Qdrant).

**Goal:** Produce a library of small, focused markdown docs with rich frontmatter, self-contained sections (<1500 chars), and real code examples that serve as both human-readable standards and RAG-ingestible knowledge.

## Source Repositories

**Located at:** `/Users/oppodeldoc/code/`

- **Next.js (3):** helix-dot-com-next, kariusdx-next, policy-node
- **Sanity.js (3):** helix-dot-com-sanity, kariusdx-sanity, ripplecom-nextjs
- **WordPress (2):** thekelsey-wp, airbnb

**Existing docs:** `/Users/oppodeldoc/code/aleph-docs`

## Project Structure

```
aleph-code-mine/
├── PROGRESS.md           # Current status, resume instructions
├── PLAN-UPDATED.md       # Detailed updated plan
├── analysis/             # Phase 1 outputs (structural reconnaissance)
├── docs/                 # RAG-optimized standards docs (output)
│   ├── js-nextjs/
│   ├── sanity/
│   ├── php-wordpress/
│   └── cross-stack/
└── tooling/              # Semgrep rules, validation scripts
```

## Current Status

**Phase:** Phase 2 - Domain-Targeted Deep Dives (In Progress)
**Progress:** 67% complete
**Completed:**
- ✅ Phase 1: Structural Reconnaissance (8/8 repos)
- ✅ Phase 2, Domain 1: Component Patterns (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 2: Data Fetching (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 3: TypeScript Conventions (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 4: Hooks & State (Next.js) - 8 docs + 3 Semgrep rules
- ✅ Phase 2, Domain 5: Styling (Next.js) - 8 docs + 4 Semgrep rules
- ✅ Phase 2, Domain 6: Project Structure (Next.js) - 7 docs + 4 Semgrep rules

**Next Domain:** Testing / Error Handling / Tooling Config (Next.js)

**To Resume:** Read `PROGRESS.md` for detailed status and next steps.

## Key Methodologies

1. **Codebase Mining Guide:** `/Users/oppodeldoc/code/aleph-code-mine/codebase_mining_guide.md`
2. **RAG Output Format:** `/Users/oppodeldoc/code/aleph-code-mine/rag_optimized_techdocs_guide.md`

## Critical Constraints

### Output Doc Requirements (from RAG guide)
- Each `##` section: **MAX 1,500 characters** (~250-350 words)
- Never start sections with pronouns ("It", "This", "These")
- Always use specific technology names
- Code blocks >10 lines get their own `###` subsection
- Every section must be self-contained (make sense if retrieved alone)

### Frontmatter Template
```yaml
---
title: "[Specific rule/pattern name]"
category: "[domain]"
subcategory: "[sub-domain]"
tags: ["tag1", "tag2", "tag3"]
stack: "[js-nextjs|sanity|php-wp|cross-stack]"
priority: "high|medium|low"
audience: "[frontend|backend|fullstack]"
complexity: "[beginner|intermediate|advanced]"
doc_type: "standard"
source_confidence: "N%"  # % of files following pattern
last_updated: "YYYY-MM-DD"
---
```

## Phase 1 Key Findings

### Critical Issues
- ❌ **Zero testing infrastructure** across all Next.js repos
- Next.js version fragmentation (v12, v14, v15)
- Sanity version diversity (v2, v3, v4)

### De Facto Standards (100% adoption)
- ✅ SCSS + CSS Modules (not Tailwind)
- ✅ TypeScript in Next.js/Sanity
- ✅ Design system structure: _colors, _typography, _spacing
- ✅ SEO-first with metadata objects

## Workflow (Per Domain)

1. **Quantitative:** grep/ripgrep for pattern counts (15-30 min)
2. **Qualitative:** Read examples, identify patterns (30-60 min)
3. **Comparison:** Build matrix, find de facto standards (15-30 min)
4. **Generate Docs:** RAG-optimized files, one per rule (30-45 min)
5. **Semgrep Rules:** For enforceable patterns (15-30 min)

**Total:** 2-3 hours per domain

## Tools

**Available:**
- grep/ripgrep (pattern search)
- npx scc (code metrics)
- npx repomix (codebase summaries)
- npx react-scanner (component stats)
- npx dependency-cruiser (module deps)

**Need to Install:**
- semgrep (`brew install semgrep`)

## Quick Resume Commands

```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat PROGRESS.md                    # Detailed status
cat PLAN-UPDATED.md                # Updated plan
ls analysis/                       # Phase 1 outputs
```

## Important Notes

- Analyze **one domain at a time** (focus, prevent context switching)
- Generate docs **immediately after analysis** (findings fresh)
- Calculate **source_confidence** from actual file counts
- Test Semgrep rules against source repos (no false positives)
- Each domain takes ~2-3 hours (time-box to prevent scope creep)

## Completed Deliverables

### Phase 1: Structural Reconnaissance ✅
- 8 structural analysis files in `analysis/`
- PHASE1-SUMMARY.md with cross-project insights

### Phase 2, Domain 1: Component Patterns ✅
**Location:** `docs/js-nextjs/component-patterns/`
**Deliverables:**
- 8 RAG-optimized documentation files (877 lines)
- 4 Semgrep enforcement rules in `tooling/semgrep/component-patterns/`
- All validated: sections <1500 chars, no pronouns, complete frontmatter

**Key Patterns Documented:**
- Folder-per-component structure (100% confidence)
- Default exports with barrel files (100% confidence)
- Props typing conventions (85% confidence)
- SCSS modules styling (100% confidence)
- Server/client component boundaries (100% confidence)
- SVG component patterns (100% confidence)

### Phase 2, Domain 2: Data Fetching ✅
**Location:** `docs/js-nextjs/data-fetching/`
**Deliverables:**
- 8 RAG-optimized documentation files (~2,400 lines)
- 4 Semgrep enforcement rules in `tooling/semgrep/data-fetching/`
- 1 cross-project comparison analysis
- All validated: sections <1500 chars, no pronouns, complete frontmatter

**Key Patterns Documented:**
- ISR revalidation (100% confidence - universal pattern)
- Custom fetch wrappers (100% confidence - Sanity, GraphQL, retry logic)
- Preview mode (100% confidence - App Router + Pages Router)
- Error handling (100% confidence - try/catch, timeout, exponential backoff)
- App Router patterns (67% confidence - async components, generateStaticParams)
- Pages Router patterns (100% confidence - getStaticProps/Paths, fallback modes)
- Route handlers (67% confidence - NextRequest/Response, webhooks)
- GraphQL batching (33% confidence - performance optimization)

### Phase 2, Domain 3: TypeScript Conventions ✅
**Location:** `docs/js-nextjs/typescript-conventions/`
**Deliverables:**
- 8 RAG-optimized documentation files (~2,000 lines)
- 4 Semgrep enforcement rules in `tooling/semgrep/typescript-conventions/`
- 1 cross-project comparison analysis

**Key Patterns Documented:**
- Props naming (Props suffix - 100% confidence, 168 instances)
- Optional vs nullable (100% confidence - 2,213 optional properties)
- No Hungarian notation (91% confidence - avoid I/T prefixes)
- Type vs interface (54% type preference, decision tree provided)
- Union types (100% confidence - 329 instances)
- Record for dictionaries (33% confidence - policy-node only)
- Type assertions sparingly (33% confidence - policy-node heavy usage)
- Type guards for runtime safety (0% confidence - gap pattern)

### Phase 2, Domain 4: Hooks & State ✅
**Location:** `docs/js-nextjs/hooks-state/`
**Deliverables:**
- 8 RAG-optimized documentation files (~2,700 lines)
- 3 Semgrep enforcement rules in `tooling/semgrep/hooks-state/`
- 1 cross-project comparison analysis

**Key Patterns Documented:**
- Multiple useState (100% confidence - 0 single state objects)
- useEffect cleanup (100% confidence - all event listeners cleaned up)
- SSR-safe custom hooks (100% confidence - 4/4 follow pattern)
- useState type annotations (100% confidence - 27% typed, 73% inferred)
- When to use useReducer (0% confidence - gap pattern)
- Context vs props drilling (1% confidence - 99% use props)
- useMemo/useCallback guidelines (minimal usage - helix: 0 useMemo)
- useEffect dependencies (100% confidence - separated by concern)

### Phase 2, Domain 5: Styling ✅
**Location:** `docs/js-nextjs/styling/`
**Deliverables:**
- 8 RAG-optimized documentation files (~3,000 lines)
- 4 Semgrep enforcement rules in `tooling/semgrep/styling/`
- 1 cross-project comparison analysis

**Key Patterns Documented:**
- CSS Modules convention (91% confidence - 194/213 files)
- Design system structure (100% confidence - all have _colors, _typography, _spacing, _mixins)
- SCSS naming conventions (100% confidence - camelCase + BEM)
- @use over @import (68% confidence - helix 91%, policy-node 96%, kariusdx 16%)
- Conditional classnames with cx() (67% confidence - 267 calls)
- Responsive breakpoint patterns (67% confidence - desktop-first, 593 mixin calls)
- State management patterns (100% confidence - :focus-visible, hover media queries)
- Globals and resets (100% confidence - all have globals.scss)

### Phase 2, Domain 6: Project Structure ✅
**Location:** `docs/js-nextjs/project-structure/`
**Deliverables:**
- 7 RAG-optimized documentation files (~2,500 lines)
- 4 Semgrep enforcement rules in `tooling/semgrep/project-structure/`
- 1 cross-project comparison analysis

**Key Patterns Documented:**
- App Router vs Pages Router (67% App Router adoption - helix v15, policy-node v14)
- Route groups organization (50% App Router - helix uses (frontend)/(studio))
- Component collocation patterns (100% confidence - hybrid shared + route-specific)
- File-based routing conventions (100% confidence - special file names)
- Metadata API usage (100% App Router - replaces next-seo)
- Async server components (100% App Router - 20 pages)
- i18n with App Router (33% confidence - policy-node uses [lang] + middleware)

## Next Session

Start with: "Continue the codebase mining project. Start Phase 2, Domain 7: [Next Domain]"

**Recommended next domains:**
- Testing (document the gap and provide guidance)
- Error Handling (patterns + best practices)
- Tooling Config (ESLint/Prettier/tsconfig)

**Files to Review Before Starting:**
```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat PROGRESS.md                              # Current status & detailed findings
cat analysis/PHASE1-SUMMARY.md             # Phase 1 insights
ls docs/js-nextjs/component-patterns/      # Domain 1 deliverables
ls docs/js-nextjs/data-fetching/           # Domain 2 deliverables
ls docs/js-nextjs/typescript-conventions/  # Domain 3 deliverables
ls docs/js-nextjs/hooks-state/             # Domain 4 deliverables
ls docs/js-nextjs/styling/                 # Domain 5 deliverables
ls docs/js-nextjs/project-structure/       # Domain 6 deliverables
```
