---
title: "Never Commit Secrets to Version Control"
category: "environment-configuration"
subcategory: "security"
tags: ["security", "secrets-management", "gitignore"]
stack: "cross-stack"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Never Commit Secrets to Version Control

## Overview

**Critical Security Rule:** Never commit API keys, passwords, tokens, or secrets to Git. Use `.gitignore` to prevent accidental commits and provide `.env.example` templates for documentation.

**Universal Pattern:** 100% of analyzed repos (8/8) properly ignore secret files
**Common Violation:** Accidentally committing `.env.local` or hardcoded secrets

## Proper .gitignore Configuration

**Next.js / Node.js:**
```gitignore
# Environment files with secrets
.env.local
.env*.local

# But document structure
!.env.example
```

**WordPress:**
```gitignore
# Generated config with database credentials
wp-config.php

# Local environment overrides
.env
.env.local

# Debug logs may contain sensitive data
*.log
debug.log
```

## Provide .env.example Instead

**Bad (committed actual secrets):**
```bash
# ❌ .env (committed to Git)
DATABASE_PASSWORD="actualpassword123"
STRIPE_SECRET_KEY="sk_live_actual_key"
```

**Good (placeholder template):**
```bash
# ✅ .env.example (committed to Git)
DATABASE_PASSWORD=""
STRIPE_SECRET_KEY=""

# ✅ .env.local (never committed)
DATABASE_PASSWORD="actualpassword123"
STRIPE_SECRET_KEY="sk_live_actual_key"
```

## Onboarding New Developers

```bash
# Step 1: Clone repo
git clone https://github.com/org/project.git

# Step 2: Copy example to local
cp .env.example .env.local

# Step 3: Fill in actual secrets
# Edit .env.local with real API keys
```

## Secrets Already Committed? Remove from History

```bash
# WARNING: Rewrites Git history (coordinate with team)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGEROUS)
git push origin --force --all

# IMPORTANT: Rotate all exposed secrets immediately!
```

## Alternative: Use Secret Management Services

- **Vercel:** Environment variables in dashboard
- **Netlify:** Build environment variables
- **GitHub:** Encrypted secrets for Actions
- **WordPress VIP:** VIP secrets API

**Benefit:** Secrets never touch local filesystem or Git history

**Source:** All repos properly configure .gitignore (100% adoption)
