# Aleph Code Mine - RAG-Optimized Standards Extraction

Automated extraction and documentation of coding standards from real codebases, optimized for RAG retrieval (BGE-large-en-v1.5 + Qdrant).

## Source Repositories

**Next.js (3):**
- `/Users/oppodeldoc/code/helix-dot-com-next`
- `/Users/oppodeldoc/code/kariusdx-next`
- `/Users/oppodeldoc/code/policy-node`

**Sanity.js (3):**
- `/Users/oppodeldoc/code/helix-dot-com-sanity`
- `/Users/oppodeldoc/code/kariusdx-sanity`
- `/Users/oppodeldoc/code/ripplecom-nextjs` (Sanity patterns only)

**WordPress (2):**
- `/Users/oppodeldoc/code/thekelsey-wp`
- `/Users/oppodeldoc/code/airbnb`

**Existing Documentation:**
- `/Users/oppodeldoc/code/aleph-docs`

## Project Structure

```
aleph-code-mine/
├── analysis/              # Raw findings and comparison matrices
├── docs/                  # RAG-optimized output documentation
│   ├── js-nextjs/
│   ├── sanity/
│   ├── php-wordpress/
│   └── cross-stack/
└── tooling/               # Enforcement and validation tools
    ├── semgrep/          # Custom Semgrep rules
    ├── validate-docs/    # Doc quality validation
    └── generate-linter-docs/  # Auto-generate linter docs
```

## Methodology

Follows guides in:
- `codebase_mining_guide.md` - Analysis methodology
- `rag_optimized_techdocs_guide.md` - Output format specification

## Current Progress

**Phase 1: Structural Reconnaissance** ✅ COMPLETE
- 8 structural analysis files
- Cross-project insights documented

**Phase 2: Domain-Targeted Deep Dives** 🎯 IN PROGRESS (31% complete)
- ✅ Domain 1: Component Patterns (8 docs + 4 Semgrep rules)
- ✅ Domain 2: Data Fetching (8 docs + 4 Semgrep rules)
- ⏳ Domains 3-9: Remaining Next.js patterns

## Deliverables to Date

**Documentation:** 16 RAG-optimized markdown files
**Enforcement:** 8 Semgrep rules
**Analysis:** 10 comparison/findings files
**Total Lines:** ~5,000 lines of production-ready documentation

See `PROGRESS.md` for detailed status and next steps.
