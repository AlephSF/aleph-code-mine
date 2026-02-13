# Content Quality Fixes Needed

**Generated:** 2026-02-12
**Validation Report:** validation-report-v3.json

## Summary

After completing structural fixes (Phases 1-3), the following content quality issues remain:

### Issues by Type

| Issue Type | Count | Severity | Est. Time |
|------------|-------|----------|-----------|
| **section_length** | 347 | FAIL | 12-30 hours |
| **code_block_subsection** | 996 | WARN | 8-20 hours |
| **bare_code_block** | 686 | WARN | 5-12 hours |
| **heading_hierarchy** | 39 | WARN | 1-2 hours |
| **stub_file** | 11 | WARN | 3-6 hours |

**Total estimated effort:** 29-70 hours of careful manual work

---

## Priority 1: Section Length Violations (347 sections)

### Problem

347 sections exceed the 1,500 character limit required for optimal RAG chunk sizing with bge-large-en-v1.5 embeddings.

### Top Offenders

| File | Violations | Max Length |
|------|------------|------------|
| php-wordpress/theme-structure/headless-theme-architecture.md | 11 | 2,927 chars |
| php-wordpress/theme-structure/webpack-asset-compilation.md | 10 | ~2,500 chars |
| php-wordpress/theme-structure/laravel-blade-templating-wordpress.md | 10 | ~2,400 chars |
| php-wordpress/theme-structure/theme-vs-mu-plugins-separation.md | 9 | ~2,200 chars |

### Fix Strategy

For each oversized section:

1. **Identify natural break points:**
   - Separate concepts/topics
   - Before/after code blocks
   - Distinct configuration examples

2. **Create descriptive ### subsections:**
   - Each subsection should be self-contained
   - Start with technology-specific context (never pronouns)
   - Keep under 1,500 chars

3. **Move code blocks to ### subsections:**
   - Long code blocks (>10 lines) get their own subsection
   - Add 1-2 sentences of prose before each code block

### Example Fix

**Before (2,927 chars):**
```markdown
## functions.php Responsibilities

[2,900+ characters of mixed prose and code]
```

**After (3 sections, each <1,500 chars):**
```markdown
## functions.php Responsibilities

### Core Theme Setup and Feature Support

WordPress headless themes use functions.php to register theme support for features...
[~800 chars]

### WPGraphQL Schema Registration

WPGraphQL integration requires explicit schema registration in functions.php...
[~700 chars]

### Custom Post Type and Taxonomy Configuration

Custom content types register through functions.php using register_post_type()...
[~900 chars]
```

### Helper Tool

Use `tooling/validate-docs/section-analyzer.py` to analyze specific files:

```bash
python3 tooling/validate-docs/section-analyzer.py docs/path/to/file.md
```

---

## Priority 2: Stub Files Needing Expansion (11 files)

### Multisite Patterns (4 files) - Target: 150-300 lines

**Current:**
- `multisite-configuration-wp-config.md` (55 lines)
- `network-admin-menu-registration.md` (56 lines)
- `blog-id-constants-centralization.md` (64 lines)
- `new-site-provisioning-hooks.md` (80 lines)

**Expansion needs:**
- Add edge cases and error scenarios
- Include anti-patterns section
- Add debugging/troubleshooting guidance
- Expand code examples with inline comments
- Add performance considerations

### Git Conventions (6 files) - Status: Intentionally Concise

**Files:** branch-naming-conventions, co-authorship-tags, commit-message-length, conventional-commits-format, imperative-mood-commits, pr-workflow-patterns

**Decision:** These are intentionally brief (44-74 lines). Topics are simple and don't warrant expansion. **No action needed.**

### JS Next.js Files (2 files)

- `component-patterns/folder-per-component.md` (66 lines) - Could add more examples
- `testing/why-testing-matters.md` (59 lines) - Intentionally concise intro doc

---

## Priority 3: Code Block Subsections (996 warnings)

### Problem

996 code blocks exceed 10 lines but don't have their own `###` subsection with a descriptive heading.

### Fix Strategy

For code blocks >10 lines without a subsection:

1. Add a `###` heading before the code block
2. Heading should describe what the code demonstrates
3. Add 1-2 sentences of prose between heading and code

### Example

**Before:**
```markdown
## Configuration Pattern

Configure the webpack build with the following setup:

\`\`\`javascript
// 15 lines of webpack config
\`\`\`
```

**After:**
```markdown
## Configuration Pattern

Configure the webpack build using Sage-specific entry points and output paths.

### Webpack Configuration with Hot Module Replacement

Sage themes configure webpack with separate development and production modes:

\`\`\`javascript
// 15 lines of webpack config
\`\`\`
```

---

## Priority 4: Bare Code Blocks (686 warnings)

### Problem

686 code blocks appear immediately after headings without prose context.

### Fix Strategy

Add 1-2 sentences between the heading and code block to provide context.

### Example

**Before:**
```markdown
### API Route Implementation

\`\`\`typescript
export async function GET(request: NextRequest) {
```

**After:**
```markdown
### API Route Implementation

Next.js App Router API routes use the Web Request/Response APIs with async handlers:

\`\`\`typescript
export async function GET(request: NextRequest) {
```

---

## Priority 5: Heading Hierarchy (39 warnings)

### Problem

39 instances where heading levels skip (e.g., `##` → `####` without `###`).

### Fix Strategy

Insert intermediate headings or adjust hierarchy to not skip levels.

---

## Recommended Workflow

### Phase A: Automated Fixes (1-2 hours)
1. Fix heading hierarchy issues (39 instances)
2. Add prose before bare code blocks (straightforward text additions)

### Phase B: Semi-Automated Fixes (8-12 hours)
1. Add ### subsections for long code blocks (996 instances)
   - Can use regex to find blocks >10 lines
   - Semi-automated heading generation based on code context

### Phase C: Manual Content Work (20-50 hours)
1. Split 347 oversized sections systematically
   - Start with worst offenders (11, 10, 9 violations per file)
   - Work through files with 7-8 violations
   - Handle files with <5 violations last

2. Expand 4 multisite stub files
   - Research edge cases from source repos
   - Add anti-patterns and troubleshooting

### Phase D: Validation (2-3 hours)
1. Re-run validation after each batch of fixes
2. Track progress: target <50 section_length violations
3. Final validation: 0 FAIL, minimal WARN

---

## Progress Tracking

Create a tracking file to monitor fixes:

```bash
# Initial state
Total files: 188
Section length violations: 347 (115 files)
Code block violations: 996
Bare code violations: 686

# Target state
Section length violations: 0
Code block violations: <100 (acceptable for genuinely short blocks)
Bare code violations: <50 (acceptable for obvious code)
```

---

## Validation Commands

```bash
# Run full validation
cd tooling/validate-docs
python3 validate.py --json report.json

# Check specific file
python3 section-analyzer.py ../../docs/path/to/file.md

# Count remaining issues
cat report.json | jq '.summary'
```

---

## Notes

- **Do not rush:** These fixes require careful reading and understanding of each section
- **Preserve accuracy:** Content accuracy is more important than strict character limits
- **Test chunks:** Consider spot-checking embedded chunks to ensure they're self-contained
- **Update last_updated:** Change frontmatter date after significant content updates
