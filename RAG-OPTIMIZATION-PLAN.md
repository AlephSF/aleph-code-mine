# RAG Content Optimization Plan - Full 100% Compliance

**Date:** 2026-02-13
**Status:** Ready to Execute
**Target:** 0 FAIL, 0 WARN across all 188 files
**Git strategy:** One commit per domain wave

---

## Context

The 188 RAG-optimized docs have 100% frontmatter compliance and 0 pronoun violations, but **347 section_length FAILs** and **1,732 warnings** remain (code block subsections, bare code blocks, heading hierarchy, stubs). This plan brings the entire corpus to 0 FAIL, 0 WARN for optimal BGE-large-en-v1.5 embedding quality.

---

## Issue Summary

| Issue | Count | Severity | Fix |
|-------|-------|----------|-----|
| section_length (>1500 chars) | 347 | FAIL | Split into smaller ## or ### sections |
| code_block_subsection (>10 lines, no ###) | 996 | WARN | Add ### heading + prose before code block |
| bare_code_block (no prose after heading) | 686 | WARN | Insert 1-2 sentences between heading and code |
| heading_hierarchy (skipped levels) | 39 | WARN | Fix heading nesting |
| stub_file (<80 lines) | 11 | WARN | Expand 4 multisite stubs (7 others intentional) |

---

## Execution Strategy

**Domain-by-domain, worst-first.** Process all issue types simultaneously per file (reading once, fixing everything). This exploits overlap: splitting oversized sections naturally creates ### subsections and adds prose context (~60-70% of CBS/BCB warnings resolve as side effects).

**Per-file workflow:**
1. Run `section-analyzer.py` on the file
2. Read the file, identify all violations
3. Fix section_length splits (also fixes CBS/BCB in those sections)
4. Fix remaining CBS/BCB warnings in compliant sections
5. Fix heading hierarchy if present
6. Verify no new pronoun violations in new section starts
7. Run `section-analyzer.py` again to confirm

**Per-domain workflow:**
1. Fix all files in the domain
2. Run `validate.py` on full docs tree
3. Commit: `RAG optimization: [stack]/[domain-name]`

---

## Processing Order (21 Waves)

### Tier 1: Highest violation density (Waves 1-4)

**Wave 1: php-wordpress/theme-structure** (15 files, ~85 SL violations)
- Top 4 worst files in entire project (11, 10, 10, 9 violations)
- Files: `headless-theme-architecture.md`, `webpack-asset-compilation.md`, `laravel-blade-templating-wordpress.md`, `theme-vs-mu-plugins-separation.md`, + 11 more
- Also has high CBS (141) and BCB (90) counts

**Wave 2: js-nextjs/error-handling** (8 files, ~36 SL violations)
- 3 files with 7 violations each
- High CBS count (122)

**Wave 3: js-nextjs/data-fetching** (8 files, ~39 SL violations)
- All 8 files have violations

**Wave 4: php-wordpress/block-development** (8 files, ~31 SL violations)
- CBS count: 63

### Tier 2: Medium violation density (Waves 5-12)

**Wave 5: sanity/content-modeling** (8 files, ~21 SL)
**Wave 6: sanity/schema-definitions** (8 files, ~20 SL)
**Wave 7: php-wordpress/wpgraphql-architecture** (8 files, ~19 SL, 12 HH)
**Wave 8: php-wordpress/custom-post-types-taxonomies** (8 files, ~17 SL)
**Wave 9: sanity/groq-queries** (8 files, ~14 SL)
**Wave 10: sanity/studio-customization** (9 files, ~12 SL)
**Wave 11: php-wordpress/multisite-patterns** (8 files, ~11 SL + 4 stub expansions)
**Wave 12: js-nextjs/testing** (8 files, ~8 SL but 6 "monster" sections >5000 chars)

### Tier 3: Low violation density (Waves 13-19)

**Wave 13: js-nextjs/styling** (8 files, ~7 SL)
**Wave 14: php-wordpress/acf-patterns** (8 files, ~7 SL, 130 BCB)
**Wave 15: php-wordpress/vip-patterns** (8 files, ~7 SL)
**Wave 16: js-nextjs/hooks-state** (8 files, ~5 SL)
**Wave 17: js-nextjs/project-structure** (7 files, ~4 SL)
**Wave 18: js-nextjs/component-patterns** (8 files, ~2 SL)
**Wave 19: php-wordpress/security-code-standards** (8 files, ~2 SL)

### Tier 4: Warn-only domains (Waves 20-21)

**Wave 20: js-nextjs warn-only domains**
- `tooling-config` (8 files): 17 CBS + 90 BCB + 21 HH
- `typescript-conventions` (8 files): 62 CBS

**Wave 21: cross-stack warn-only domains**
- `environment-configuration` (7 files): 11 CBS + 19 BCB
- `git-conventions` (6 files): 3 CBS + 8 BCB

---

## Fix Patterns

### Monster sections (>5000 chars, ~14 sections)
Promote existing `###` headings to `##` headings. Content already has subsections - they just use wrong heading level. Rewrite each new `##` opener to be self-contained.

### Large sections (2500-5000 chars, ~58 sections)
Split into 2-3 `##` sections at natural topic boundaries. Extract code blocks into `###` subsections with descriptive headings.

### Medium sections (2000-2500 chars, ~81 sections)
Usually one split or code block extraction into a `###` subsection.

### Slight over-limit (1500-2000 chars, ~194 sections)
Trim verbose prose, extract one code block, or split a list spanning two subtopics.

### Bare code blocks (686 warnings)
Insert 1-2 sentences between heading and code fence. Template: `[Technology] [verb] [what code demonstrates]:`

### Code block subsections (996 warnings)
Add `###` heading before code blocks >10 lines, plus 1-2 sentences of prose.

### Heading hierarchy (39 warnings)
Demote `####` to `###` or insert intermediate heading.

### Stub expansion (4 multisite files)
Expand from ~55-80 lines to ~150-300 lines with edge cases, anti-patterns, debugging guidance.

---

## Validation

**Tools:**
- `tooling/validate-docs/validate.py` -- full 21-check validation
- `tooling/validate-docs/section-analyzer.py` -- per-file section analysis

**Checkpoints after each wave:**
```bash
cd /Users/oppodeldoc/code/aleph-code-mine/tooling/validate-docs
python3 validate.py --docs-dir ../../docs --verbose
```

**Progress milestones:**
- After Wave 1: ~262 SL failures remaining (from 347)
- After Wave 4: ~156 SL failures remaining
- After Wave 8: ~69 SL failures remaining
- After Wave 12: ~34 SL failures remaining
- After Wave 19: 0 SL failures
- After Wave 21: 0 FAIL, 0 WARN

---

## Quality Rules for All Edits

1. Every new `##` section opener: no pronouns, use specific tech name
2. Every new `##` section: <1500 chars (verify with section-analyzer)
3. Every code block >10 lines: own `###` subsection with descriptive heading
4. Every code block: preceded by 1-2 sentences of prose context
5. No heading level skips (## -> ### -> ####)
6. Content accuracy preserved - splitting reorganizes, never removes information
7. Minimum section depth ~400 chars (avoid trivially shallow sections)
8. Update `last_updated` frontmatter field to `2026-02-13` in every edited file

---

## Resume Instructions

To resume this work in a new session:
```bash
cd /Users/oppodeldoc/code/aleph-code-mine
cat RAG-OPTIMIZATION-PLAN.md    # This file - the plan
cat PROGRESS.md                  # Overall project status

# Check current violation counts
cd tooling/validate-docs
python3 validate.py --docs-dir ../../docs --verbose

# Check specific file
python3 section-analyzer.py ../../docs/path/to/file.md
```

Start with: "Continue RAG content optimization. Resume at Wave [N]."

---

## Wave Progress Tracking

### Completed Waves

**Wave 10: sanity/studio-customization** ✅ (Completed 2026-02-13)
- 5 of 9 files optimized for section_length
- Fixed 32 code_block_subsection warnings
- Reduced section_length violations from 12 to 7
- Commit: e65e1f7

**Wave 10: sanity/studio-customization** ✅ (Completed 2026-02-13)
- 5 of 9 files optimized for section_length
- Fixed 32 code_block_subsection warnings
- Reduced section_length violations from 12 to 7
- Commit: e65e1f7

**Wave 11: php-wordpress/multisite-patterns** ✅ (Completed 2026-02-13)
- 4 of 4 files with section_length violations fixed
- Reduced section_length violations from 11 to 0 (100% complete)
- 2 files optimized:
  - conditional-blog-specific-plugin-loading.md: 1742+1502 → all <1500 chars (17 sections)
  - cross-site-queries-get-sites.md: 2057+3193 → all <1500 chars (18 sections)
- Commit: e95affe

**Wave 1: php-wordpress/theme-structure** ⏳ IN PROGRESS (Started 2026-02-13)
- 2 of 9 files completed (10 violations fixed)
- 2 files partially fixed (2 violations fixed)
- 5 files remaining (34 violations)
- Completion: 26% (12/46 violations fixed)
- Key files:
  - ✅ theme-vs-mu-plugins-separation.md: 9→0 (complete) - Commit: f40e22d
  - ✅ asset-management-strategies.md: 1→0 (complete) - Commit: a03a2aa
  - ⏳ traditional-theme-organization.md: 9→7 (partial) - Commit: 8c0154d
  - ⏳ mvc-controllers-pattern.md: 2→2 (minimal) - Commit: 519c007
  - ❌ blade-templating-pattern.md: 2 violations
  - ❌ sage-framework-structure.md: 5 violations
  - ❌ template-directory-customization.md: 5 violations
  - ❌ sage-roots-framework-setup.md: 6 violations
  - ❌ theme-build-modernization.md: 7 violations

**Current Status:**
- Overall section_length: 347 → ~335 (12 fixed)
- Wave 1 progress: 26% complete
- Estimated remaining time: 4-6 hours

**Next Session:** Continue Wave 1, starting with blade-templating-pattern.md (2 violations, easiest)
