---
title: "Commit Message Length Guidelines"
category: "git-conventions"
subcategory: "formatting"
tags: ["git", "commit-messages", "best-practices"]
stack: "cross-stack"
priority: "low"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Commit Message Length Guidelines

## Overview

**Recommended:** 50-72 characters for subject line
**Observed Average:** 38 characters across 60 commits
**Hard Limit:** GitHub truncates at 72 characters in UI

## Length Analysis by Repo

| Repo | Avg Length | Range |
|------|-----------|-------|
| helix | 35 chars | 20-60 |
| kariusdx | 45 chars | 30-75 |
| policy-node | 52 chars | 35-80 |
| airbnb | 28 chars | 15-50 |
| thekelsey | 32 chars | 20-45 |

## Guidelines

**Subject (First Line):**
- Aim for 50 characters
- Hard limit: 72 characters
- GitHub shows 72 chars before truncation

**Body (Optional):**
- Wrap at 72 characters
- Separate from subject with blank line
- Explain why, not what (code shows what)

## Examples

```
Good (48 chars):
feat: add JWT refresh token rotation mechanism

Too long (85 chars):
feat: add JWT refresh token rotation mechanism with Redis storage and automatic cleanup

Better with body:
feat: add JWT refresh token rotation

Implements automatic rotation with Redis storage
for improved security. Tokens expire after 7 days.
```

**Source:** 38 character average across 60 analyzed commits
