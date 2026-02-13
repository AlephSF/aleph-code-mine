---
title: "Imperative Mood in Commit Messages"
category: "git-conventions"
subcategory: "writing-style"
tags: ["git", "commit-messages", "writing-conventions"]
stack: "cross-stack"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Imperative Mood in Commit Messages

## Overview

**Rule:** Write commit subjects as commands/instructions: "Add feature" not "Added feature"
**Adoption:** 100% of analyzed commits (60/60)
**Rationale:** Matches Git's own message style ("Merge branch", "Revert commit")

## Examples

```
✅ Good (Imperative):
feat: add dark mode
fix: resolve navigation bug
chore: update dependencies

❌ Bad (Past tense):
feat: added dark mode
fix: resolved navigation bug
chore: updated dependencies

❌ Bad (Present continuous):
feat: adding dark mode
fix: resolving navigation bug
```

## Mental Model

Complete this sentence: "If applied, this commit will..."

- ✅ "...add dark mode"
- ✅ "...fix navigation bug"
- ❌ "...added dark mode"

**Source:** 100% adoption across all 8 repos
