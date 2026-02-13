---
title: "Conventional Commits Format"
category: "git-conventions"
subcategory: "commit-messages"
tags: ["git", "conventional-commits", "version-control"]
stack: "cross-stack"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "83%"
last_updated: "2026-02-12"
---

# Conventional Commits Format

## Overview

**Format:** `<type>: <subject>` or `<type>(<scope>): <subject>`
**Adoption:** 83% of repos (5/6) follow Conventional Commits specification
**Types:** feat, fix, chore, docs, style, refactor, test

## Pattern

```
feat: add dark mode toggle
fix: resolve navigation bug on mobile
chore: update dependencies
feat(auth): implement JWT refresh tokens
```

**Type Distribution:**
- feat: 42% (new features)
- fix: 33% (bug fixes)
- chore: 20% (maintenance)

## Benefits

1. **Automated Changelogs:** Generate from commit history
2. **Semantic Versioning:** Determine version bumps
3. **Searchable History:** Filter by type (git log --grep="^feat")
4. **Clear Intent:** Instantly understand purpose

**Source:** 60 commits analyzed (feat: 25, fix: 20, chore: 12)
