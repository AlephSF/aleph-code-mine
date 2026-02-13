---
title: "Git Co-Authorship Tags"
category: "git-conventions"
subcategory: "attribution"
tags: ["git", "co-authorship", "pair-programming"]
stack: "cross-stack"
priority: "low"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-12"
---

# Git Co-Authorship Tags

## Overview

**Current Adoption:** 0% (gap pattern - no commits use co-author tags)
**Recommendation:** Add for pair programming, AI assistance, collaborative work
**GitHub Support:** Displays multiple authors in commit UI

## Format

```
feat: implement new feature

Co-Authored-By: Jane Developer <jane@example.com>
Co-Authored-By: John Smith <john@example.com>
```

**Requirements:**
- Blank line after commit message
- Format: `Co-Authored-By: Name <email>`
- One tag per line
- Must use author's GitHub email for attribution

## Use Cases

**Pair Programming:**
```
feat: refactor authentication system

Implemented during pair programming session.

Co-Authored-By: Sarah Chen <sarah@example.com>
```

**AI Assistance:**
```
feat: add data validation utilities

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Mob Programming:**
```
feat: design new API architecture

Team collaboration session.

Co-Authored-By: Dev 1 <dev1@example.com>
Co-Authored-By: Dev 2 <dev2@example.com>
Co-Authored-By: Dev 3 <dev3@example.com>
```

## Benefits

1. **Proper Attribution:** GitHub shows all authors
2. **Contribution Tracking:** Counts toward all authors' stats
3. **Transparency:** Makes collaboration visible
4. **Credit:** Recognizes pair/mob programming work

**Current Status:** 0% adoption (opportunity for improvement)
