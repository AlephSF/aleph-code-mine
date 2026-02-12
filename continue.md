# Continue Codebase Mining Project

**Session Date:** February 12, 2026
**Context:** Phase 4 - WordPress Domains (Domain 2 just completed)

---

## Quick Resume

Tell Claude:
> "Continue the codebase mining project. Read continue.md for current status."

---

## Current Status

**Phase 4: WordPress Domains** - 2/8 domains complete (25%)

### ✅ Completed Domains

#### Domain 1: WPGraphQL Architecture (3 hours)
- 8 documentation files
- 4 Semgrep rules
- 1 comparison analysis
- Location: `docs/php-wordpress/wpgraphql-architecture/`

#### Domain 2: Custom Post Types & Taxonomies (3 hours)
- 8 documentation files
- 9 Semgrep rules (4 files with multiple rules each)
- 1 comparison analysis (20 sections)
- Location: `docs/php-wordpress/custom-post-types-taxonomies/`

### ⏳ Next Domain: ACF (Advanced Custom Fields) Patterns

**Priority:** High
**Estimated Duration:** 2-3 hours
**Source Repos:** airbnb (ACF Pro 24MB), thekelsey-wp (ACF Pro)

**Key Areas to Document:**
1. ACF field group organization (JSON storage pattern)
2. Field type usage patterns (text, wysiwyg, repeater, flexible content)
3. Conditional logic patterns
4. ACF + GraphQL integration (wpgraphql-acf)
5. ACF blocks (12 custom + 15 ACF blocks in airbnb-policy-blocks)
6. Location rules patterns
7. Field naming conventions
8. ACF options pages

**Known Patterns from Phase 1:**
- Airbnb: 193 ACF fields with custom GraphQL names across 23 field groups
- JSON storage for version control
- ACF Pro with Advanced features (repeater, flexible content, gallery)

**Suggested Workflow:**
```bash
# 1. Quantitative analysis (15-30 min)
cd /Users/oppodeldoc/code/airbnb
find . -name "*.json" -path "*/acf-json/*" | wc -l
grep -r "acf_add_local_field_group" --include="*.php" | wc -l
grep -r "get_field\|the_field" --include="*.php" | wc -l

# 2. Read sample ACF JSON files (30 min)
cat plugins/advanced-custom-fields-pro/acf-json/[sample-files]

# 3. Analyze ACF block patterns (30 min)
ls -la plugins/airbnb-policy-blocks/
grep -r "acf_register_block_type" --include="*.php"

# 4. Create comparison analysis (30 min)
# Compare airbnb vs thekelsey ACF usage

# 5. Generate 8 docs + 4 Semgrep rules (60-90 min)
```

---

## Remaining WordPress Domains (6 total)

**After ACF, continue with:**

3. ✅ **ACF Patterns** ← NEXT
4. **WordPress VIP Patterns** (VIP-specific mu-plugins, platform utilities)
5. **Theme Structure** (Sage framework vs traditional PHP)
6. **Security & Code Standards** (PHPCS, sanitization, escaping)
7. **Multisite Patterns** (conditional loading, network-wide functions)
8. **Block Development** (Gutenberg custom blocks)

---

## File Locations

**Analysis files:** `/Users/oppodeldoc/code/aleph-code-mine/analysis/`
**Documentation output:** `/Users/oppodeldoc/code/aleph-code-mine/docs/php-wordpress/`
**Semgrep rules:** `/Users/oppodeldoc/code/aleph-code-mine/tooling/semgrep/`
**Source repos:** `/Users/oppodeldoc/code/airbnb`, `/Users/oppodeldoc/code/thekelsey-wp`

---

## Progress Summary

**Overall Project:** 49% complete (41/83 hours)

| Phase | Status | Hours |
|-------|--------|-------|
| Phase 1: Structural Recon | ✅ Complete | 2/2 |
| Phase 2: Next.js Domains (9) | ✅ Complete | 24/24 |
| Phase 3: Sanity Domains (4) | ✅ Complete | 12/12 |
| Phase 4: WordPress Domains (8) | ⏳ 2/8 (25%) | 6/18 |
| Phase 5: Cross-Stack | ⏳ Pending | 0/8 |
| Phase 6: Tooling | ⏳ Pending | 0/12 |

**Completed Deliverables:**
- 103 RAG-optimized documentation files
- 74 Semgrep enforcement rules
- 16 cross-project comparison analyses

---

## Key Methodologies

**Codebase Mining Guide:** `/Users/oppodeldoc/code/aleph-code-mine/codebase_mining_guide.md`
**RAG Output Format:** `/Users/oppodeldoc/code/aleph-code-mine/rag_optimized_techdocs_guide.md`

**Per-Domain Workflow (2-3 hours):**
1. Quantitative analysis (grep/ripgrep patterns) - 15-30 min
2. Qualitative analysis (read examples) - 30-60 min
3. Cross-project comparison (build matrix) - 15-30 min
4. Generate 8 RAG docs - 30-45 min
5. Generate 4 Semgrep rules - 15-30 min

---

## Commands to Resume

```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat continue.md          # This file
cat PROGRESS.md          # Detailed progress
ls docs/php-wordpress/   # See WordPress domains completed
```

---

## Notes

- All documentation follows RAG template (<1500 chars per section)
- Source confidence calculated from actual file counts
- WordPress repos: airbnb (VIP multisite, 8+ sites), thekelsey-wp (single site)
- No testing infrastructure in WordPress repos (consistent with Phase 2 finding)
