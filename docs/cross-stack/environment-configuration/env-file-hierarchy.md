---
title: "Environment File Hierarchy and Load Order"
category: "environment-configuration"
subcategory: "configuration-management"
tags: ["environment-variables", "dotenv", "configuration"]
stack: "cross-stack"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Environment File Hierarchy and Load Order

## Overview

Next.js loads environment files in priority order: `.env.local` (highest) → `.env.development` → `.env.production` → `.env` (lowest). Variables in higher-priority files override lower-priority files.

**Pattern:** Commit shared defaults, never commit local secrets
**Adoption:** 100% of Next.js projects (3/3 repos)

## File Priority Order (Highest to Lowest)

| File | Purpose | Git Commit | Use Case |
|------|---------|-----------|----------|
| `.env.local` | Local secrets/overrides | ❌ Never | Developer-specific keys |
| `.env.development` | Dev environment defaults | ✅ Yes | Shared dev config |
| `.env.production` | Production defaults | ✅ Yes | Shared prod config |
| `.env` | Universal defaults | ✅ Yes | Fallback values |
| `.env.example` | Documentation template | ✅ Yes | Onboarding new devs |

## Example Setup

**.env (committed - universal defaults):**
```bash
NEXT_PUBLIC_API_URL="http://localhost:3000"
```

**.env.development (committed - dev defaults):**
```bash
NEXT_PUBLIC_API_URL="https://api-dev.example.com"
NODE_ENV="development"
```

**.env.production (committed - prod defaults):**
```bash
NEXT_PUBLIC_API_URL="https://api.example.com"
NODE_ENV="production"
```

**.env.local (never committed - secrets):**
```bash
DATABASE_PASSWORD="local-dev-password"
INTERNAL_API_SECRET="your-secret-key"
```

## Load Behavior

**Development:** `next dev` loads `.env.local` → `.env.development` → `.env`
**Production:** `next build` loads `.env.local` → `.env.production` → `.env`

**Override Example:**
```bash
# .env
API_KEY="default-key"

# .env.local
API_KEY="override-key"  # This wins!

# Result: process.env.API_KEY === "override-key"
```

## .gitignore Configuration

```gitignore
# Local env files
.env.local
.env*.local

# But commit these
!.env.example
!.env.development
!.env.production
```

**Source:** policy-node/.env.example, helix-dot-com-next/.env.local
