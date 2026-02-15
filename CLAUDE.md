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

**Project Status:** ✅ COMPLETE
**Progress:** 100% complete (all phases finished)

### Final Deliverables
- **188 RAG-optimized documentation files** (23 domains across 4 stacks)
- **221 Semgrep enforcement rules** (95 YAML files)
- **35 analysis files** (8 structural + 27 cross-project comparisons)
- **100% RAG optimization** (0 section length failures, 0 empty headings)

### Completed Phases
- ✅ Phase 1: Structural Reconnaissance (8/8 repos analyzed)
- ✅ Phase 2: JS Next.js Domains (9 domains, 71 docs, 35 Semgrep rules)
- ✅ Phase 3: PHP WordPress Domains (8 domains, 71 docs, 158 Semgrep rules)
- ✅ Phase 4: Sanity Domains (4 domains, 33 docs, 16 Semgrep rules)
- ✅ Phase 5: Cross-Stack Domains (2 domains, 13 docs, 12 Semgrep rules)
- ✅ Phase 6: QA Validation & Cleanup (all structural issues resolved)
- ✅ Waves 1-11: RAG Optimization (all sections <1500 chars, no empty headings)

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

## Completed Deliverables Summary

### Documentation by Stack

| Stack | Domains | Docs | Semgrep Rules | Lines |
|-------|---------|------|---------------|-------|
| **JS Next.js** | 9 | 71 | 35 rules (35 files) | ~25,000 |
| **PHP WordPress** | 8 | 71 | 158 rules (40 files) | ~32,000 |
| **Sanity** | 4 | 33 | 16 rules (16 files) | ~16,000 |
| **Cross-Stack** | 2 | 13 | 12 rules (4 files) | ~1,000 |
| **TOTAL** | **23** | **188** | **221 rules (95 files)** | **~74,000** |

### JS Next.js Domains (9 complete)
1. Component Patterns (8 docs + 4 rules)
2. Data Fetching (8 docs + 4 rules)
3. TypeScript Conventions (8 docs + 4 rules)
4. Hooks & State (8 docs + 3 rules)
5. Styling (8 docs + 4 rules)
6. Project Structure (7 docs + 4 rules)
7. Testing (8 docs + 4 rules)
8. Error Handling (8 docs + 4 rules)
9. Tooling Config (8 docs + 4 rules)

### PHP WordPress Domains (8 complete)
1. ACF Patterns (8 docs + 29 rules)
2. Block Development (8 docs + 17 rules)
3. Custom Post Types & Taxonomies (8 docs + 9 rules)
4. Multisite Patterns (8 docs + 19 rules)
5. Security & Code Standards (8 docs + 18 rules)
6. Theme Structure (15 docs + 36 rules)
7. VIP Patterns (8 docs + 20 rules)
8. WPGraphQL Architecture (8 docs + 10 rules)

### Sanity Domains (4 complete)
1. Content Modeling (8 docs + 4 rules)
2. GROQ Queries (8 docs + 4 rules)
3. Schema Definitions (8 docs + 4 rules)
4. Studio Customization (9 docs + 4 rules)

### Cross-Stack Domains (2 complete)
1. Environment Configuration (7 docs + 6 rules)
2. Git Conventions (6 docs + 6 rules)

### Phase 1: Structural Reconnaissance ✅
- 8 structural analysis files in `analysis/`
- PHASE1-SUMMARY.md with cross-project insights

### Example Domain Detail: Component Patterns ✅
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

## Project Complete

All 23 domains have been documented, validated, and optimized. The project achieved:
- ✅ 100% RAG optimization (0 section_length failures, 0 empty headings)
- ✅ 100% frontmatter compliance
- ✅ 221 validated Semgrep rules across 95 files
- ✅ 188 production-ready documentation files

For detailed metrics, see `FINAL-QA-METRICS.md`.
For project history, see `PROGRESS.md`.

**Integration Status:** Ready for RAG deployment (BGE-large-en-v1.5 + Qdrant)
