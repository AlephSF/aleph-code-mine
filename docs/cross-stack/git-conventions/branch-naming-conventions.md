---
title: "Git Branch Naming Conventions"
category: "git-conventions"
subcategory: "branching-strategy"
tags: ["git", "branches", "naming-conventions"]
stack: "cross-stack"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Git Branch Naming Conventions

## Overview

**Format:** `type-description` or `type-description-TICKET`
**Case:** lowercase with hyphens
**Adoption:** 100% (inferred from PR merge commits)

## Pattern

```
feat-add-dark-mode
fix-navigation-mobile-bug
chore-update-dependencies
feat-jwt-refresh-tokens-ENG-1234
```

**Components:**
1. **Type prefix:** matches commit type (feat, fix, chore)
2. **Hyphenated description:** lowercase, clear, concise
3. **Optional ticket ID:** project tracking reference

## Examples from Repos

```
feat-upgrade-packages                          # helix
feat-update-clinical-data-filters-ENG-1037    # kariusdx
feat-add-dark-mode                            # policy-node
```

## Long-Lived Branches

- `main` / `master` - production
- `develop` - integration branch
- `edge` - pre-production (observed in thekelsey)

**Source:** 100% use hyphenated lowercase naming
