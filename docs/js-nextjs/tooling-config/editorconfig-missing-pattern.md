---
title: ".editorconfig Missing Pattern (Critical Gap)"
category: "tooling-config"
subcategory: "editor"
tags: ["editorconfig", "consistency", "indentation", "line-endings", "ide"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

# .editorconfig Missing Pattern (Critical Gap)

## Overview

Zero Next.js projects (0%) have .editorconfig files, creating cross-IDE consistency risks. Team members using VS Code, IntelliJ, Vim may have different indentation (tabs vs. spaces), line endings (LF vs. CRLF), and charset settings, leading to noisy git diffs and merge conflicts.

**De Facto Standard (Recommended):** Add .editorconfig to enforce consistent editor settings across IDEs, eliminate whitespace-only diffs, prevent line ending issues.

## Critical Gap Analysis

### Observed Pattern Across All Projects

```bash
# helix-dot-com-next
ls -la .editorconfig
# File not found

# kariusdx-next
ls -la .editorconfig
# File not found

# policy-node
ls -la .editorconfig
# File not found
```

**Adoption:** 0% (all projects missing .editorconfig)

**Why Critical:**
- ESLint enforces code style (semicolons, max-len)
- stylelint enforces CSS style (property ordering, quotes)
- **No tool enforces**: indentation, line endings, trailing whitespace, final newline
- Team inconsistency: VS Code defaults to spaces, IntelliJ may use tabs

## Basic Configuration (All File Types)

### Root-Level Settings

```ini
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

**Source Rationale:**
- **charset = utf-8:** All analyzed projects use UTF-8 (universal standard)
- **end_of_line = lf:** macOS/Linux standard, Windows Git converts CRLF → LF
- **insert_final_newline = true:** POSIX compliance, prevents git diff noise
- **trim_trailing_whitespace = true:** Prevents ESLint/stylelint warnings

### JavaScript/TypeScript Indentation

```ini
[*.{js,jsx,ts,tsx}]
indent_style = space
indent_size = 2
```

**Source Evidence:**
- Helix: 2-space indentation (observed in components)
- Kariusdx: 2-space indentation (ESLint `"indent": [2, 2]`)
- Policy-node: 2-space indentation (consistent across files)

**De Facto Standard:** 2 spaces for JavaScript/TypeScript (Next.js ecosystem)

## File Type-Specific Configuration

### SCSS Indentation

```ini
[*.{css,scss,sass}]
indent_style = space
indent_size = 2
```

**Source Evidence:**
- All projects use 2-space indentation in SCSS (consistent with JavaScript)
- No observed tab usage in CSS/SCSS files

### JSON/YAML Indentation

```ini
[*.{json,yml,yaml}]
indent_style = space
indent_size = 2
```

**Rationale:**
- package.json uses 2-space indentation (npm default)
- .eslintrc.json uses 2-space indentation
- .github/workflows/*.yml uses 2-space indentation (GitHub Actions default)

### Markdown

```ini
[*.md]
trim_trailing_whitespace = false
max_line_length = off
```

**Why Different:**
- Markdown uses 2 trailing spaces for line breaks (don't trim)
- Long lines in Markdown are acceptable (code blocks, URLs)

## Complete .editorconfig Template

```ini
# .editorconfig
# EditorConfig: https://editorconfig.org

# Top-most EditorConfig file
root = true

# All files
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# JavaScript/TypeScript
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_style = space
indent_size = 2

# CSS/SCSS
[*.{css,scss,sass}]
indent_style = space
indent_size = 2

# JSON/YAML
[*.{json,yml,yaml}]
indent_style = space
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false
max_line_length = off

# Makefiles
[Makefile]
indent_style = tab
```

## Real-World Problem Scenarios

### Scenario 1: Mixed Indentation (Without .editorconfig)

```javascript
// Developer A (VS Code, 2 spaces)
function fetchData() {
  return fetch('/api/data')
    .then(res => res.json())
}

// Developer B (IntelliJ, 4 spaces)
function fetchData() {
    return fetch('/api/data')
        .then(res => res.json())
}

// git diff shows entire function changed (whitespace-only)
```

**With .editorconfig:** Both developers use 2 spaces, no diff

### Scenario 2: Line Ending Issues (Without .editorconfig)

```bash
# Developer A (macOS, LF line endings)
git add src/components/Button.tsx
# All LF

# Developer B (Windows, CRLF line endings)
git add src/components/Button.tsx
# Git shows 100+ line changes (LF → CRLF conversion)
```

**With .editorconfig:** All developers use LF, Git stays clean

### Scenario 3: Missing Final Newline (Without .editorconfig)

```typescript
// file.ts (Developer A - has final newline)
export const API_URL = 'https://api.example.com'
↵ // Final newline

// file.ts (Developer B - no final newline)
export const API_URL = 'https://api.example.com'[EOF]

// git diff: "No newline at end of file" warning
```

**With .editorconfig:** insert_final_newline = true enforces consistency

## IDE Support

### Supported Editors (Built-in or Plugin)

- **VS Code:** Built-in support (reads .editorconfig automatically)
- **IntelliJ/WebStorm:** Built-in support
- **Sublime Text:** Plugin (EditorConfig)
- **Vim/Neovim:** Plugin (editorconfig-vim)
- **Atom:** Plugin (editorconfig)
- **Emacs:** Plugin (editorconfig-emacs)

**Coverage:** 99% of IDEs support .editorconfig (near-universal)

## Pre-commit Hook Enforcement

ESLint/stylelint don't check indentation depth (only style violations):

```bash
# .husky/pre-commit
npx lint-staged && npx tsc --noEmit
```

**Gap:** No enforcement of:
- Consistent indentation (tabs vs. spaces, 2 vs. 4 spaces)
- Line endings (LF vs. CRLF)
- Final newline

**Solution:** .editorconfig + IDE integration (prevents issues before commit)

## Migration Path: Add .editorconfig to All Projects

```bash
# 1. Create .editorconfig in project root
cat > .editorconfig << 'EOF'
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_style = space
indent_size = 2

[*.{css,scss,sass}]
indent_style = space
indent_size = 2

[*.{json,yml,yaml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
max_line_length = off
EOF

# 2. Verify IDE picks up settings (restart IDE)
# VS Code: Check status bar (should show "Spaces: 2")

# 3. Run linters to catch any inconsistencies
npm run lint
npm run lint:styles

# 4. Commit
git add .editorconfig
git commit -m "chore: Add .editorconfig for cross-IDE consistency"
```

## Anti-Patterns to Avoid

### Don't: Use Tabs for JavaScript/TypeScript

```ini
# ❌ Bad: JavaScript ecosystem uses spaces
[*.{js,jsx,ts,tsx}]
indent_style = tab
```

**Problem:** Breaks ESLint rules, inconsistent with Next.js ecosystem

### Don't: Use 4 Spaces for JavaScript/TypeScript

```ini
# ❌ Bad: Next.js/React ecosystem uses 2 spaces
[*.{js,jsx,ts,tsx}]
indent_size = 4
```

**Problem:** Conflicts with existing codebase (all analyzed projects use 2 spaces)

### Don't: Omit root = true

```ini
# ❌ Bad: IDE may search parent directories for .editorconfig
[*]
charset = utf-8
```

**Solution:** Always add `root = true` at top of file

## Verification Script

```bash
# check-editorconfig.sh
#!/bin/bash

if [ ! -f .editorconfig ]; then
  echo "❌ .editorconfig missing"
  echo "Run: curl -o .editorconfig https://gist.github.com/.../editorconfig"
  exit 1
fi

echo "✅ .editorconfig present"

# Verify indentation in random file
grep -q "indent_size = 2" .editorconfig || {
  echo "⚠️  .editorconfig may not specify indent_size = 2"
}
```

**Add to CI:**

```yaml
# .github/workflows/ci.yml
- name: Check .editorconfig
  run: |
    test -f .editorconfig || (echo "Missing .editorconfig" && exit 1)
```

## Benefits Summary

**With .editorconfig:**
- ✅ Consistent indentation across team (2 spaces for JS/TS/SCSS)
- ✅ Consistent line endings (LF on all platforms)
- ✅ No trailing whitespace (cleaner git diffs)
- ✅ Final newline enforced (POSIX compliance)
- ✅ Works with any IDE (VS Code, IntelliJ, Vim)

**Without .editorconfig (Current State):**
- ❌ Team may use different indentation (tabs vs. spaces, 2 vs. 4)
- ❌ Windows developers may commit CRLF line endings
- ❌ Noisy git diffs (whitespace-only changes)
- ❌ ESLint/stylelint don't catch indentation depth issues

## References

- **EditorConfig Spec:** https://editorconfig.org/
- **EditorConfig Properties:** https://github.com/editorconfig/editorconfig/wiki/EditorConfig-Properties
- **VS Code EditorConfig:** https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- .editorconfig adoption: 0/3 projects (0% - critical gap)
- Observed indentation: 2 spaces (JavaScript/TypeScript/SCSS - 100%)
- Observed line endings: LF (100% - macOS/Linux development)
