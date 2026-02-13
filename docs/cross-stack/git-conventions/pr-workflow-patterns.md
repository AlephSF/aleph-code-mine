---
title: "Pull Request Workflow Patterns"
category: "git-conventions"
subcategory: "collaboration"
tags: ["git", "pull-requests", "code-review"]
stack: "cross-stack"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Pull Request Workflow Patterns

## Overview

**Adoption:** 100% of repos use PR-based workflow
**Merge Strategy:** Squash or merge commit (varies by repo)
**Review Required:** Enforced via GitHub branch protection

## Standard Workflow

```bash
# 1. Create feature branch
git checkout -b feat-add-dark-mode

# 2. Make commits
git commit -m "feat: add dark mode toggle"
git commit -m "feat: persist dark mode preference"

# 3. Push to remote
git push origin feat-add-dark-mode

# 4. Open PR via GitHub UI
# Title: feat: Add dark mode support
# Description: Implements user-requested dark mode...

# 5. Code review, CI checks
# 6. Merge via GitHub (creates merge commit)
```

## PR Merge Commits

```
Merge pull request #390 from myhelix/feat-upgrade-packages
Merge pull request #43 from KariusDx/feat-update-clinical-data-filters-ENG-1037
```

**Pattern:** GitHub's default PR merge message retained

## Branch Protection Rules

Observed enforcement:
- Require PR before merging to main
- Require CI checks to pass
- (Recommended) Require 1+ approving reviews

**Source:** 100% of repos show PR merge patterns
