---
title: "Environment Variable Naming Conventions"
category: "environment-configuration"
subcategory: "code-standards"
tags: ["naming-conventions", "standards", "consistency"]
stack: "cross-stack"
priority: "low"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Environment Variable Naming Conventions

## Overview

**Industry Standard:** UPPER_SNAKE_CASE for all environment variables
**Adoption:** 100% of analyzed projects follow UPPER_SNAKE_CASE
**Prefixes:** Stack-specific prefixes indicate scope and exposure

## Universal Standards

**Format:** `[PREFIX_]COMPONENT_PURPOSE[_QUALIFIER]`

**Examples:**
```bash
# ✅ Good: Clear, descriptive, UPPER_SNAKE_CASE
DATABASE_URL="postgresql://..."
API_KEY_STRIPE="sk_..."
CACHE_TTL_SECONDS="3600"

# ❌ Bad: Mixed case, unclear
databaseUrl="..."
api-key="..."
CacheTTL="..."
```

## Stack-Specific Prefixes

### Next.js

**Client-Accessible:**
```bash
NEXT_PUBLIC_API_URL="https://api.example.com"
NEXT_PUBLIC_GTM_ID="GTM-XXXXXXX"
```

**Server-Only:**
```bash
DATABASE_URL="postgresql://..."
INTERNAL_API_SECRET="secret"
```

### WordPress

**Core:**
```bash
WP_ENV="production"
WP_DEBUG=true
WP_CACHE_KEY_SALT="unique-salt"
```

**VIP Platform:**
```bash
VIP_GO_APP_ENVIRONMENT="production"
VIP_GO_ENV="production"
```

### Sanity

```bash
SANITY_PROJECT_ID="abc123"
SANITY_DATASET="production"
SANITY_API_READ_TOKEN="sk..."
```

## Naming Patterns by Purpose

**API Endpoints:**
```bash
NEXT_PUBLIC_API_URL="..."        # Public API
INTERNAL_API_URL="..."          # Internal/private API
GRAPHQL_ENDPOINT="..."          # GraphQL-specific
```

**Secrets:**
```bash
API_KEY_[SERVICE]="..."         # API keys
[SERVICE]_SECRET="..."          # Secret keys
[SERVICE]_TOKEN="..."           # Auth tokens
```

**Feature Flags:**
```bash
ENABLE_[FEATURE]="true"         # Boolean flags
FEATURE_[NAME]_ENABLED="true"   # Alt format
```

**Timeouts/Limits:**
```bash
[SERVICE]_TIMEOUT_MS="5000"     # Milliseconds
[SERVICE]_MAX_RETRIES="3"       # Retry count
CACHE_TTL_SECONDS="3600"        # Duration
```

## Anti-Patterns

```bash
# ❌ Inconsistent case
DatabaseURL="..."
database_url="..."
DATABASE_Url="..."

# ❌ Vague names
KEY="..."           # Which key?
URL="..."           # Which URL?
SECRET="..."        # Which secret?

# ❌ No separation
databaseurlprimary="..."  # Hard to read
```

**Source:** Consistent UPPER_SNAKE_CASE adoption across all 8 repos (100%)
