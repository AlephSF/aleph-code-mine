---
title: "NEXT_PUBLIC_ Prefix for Client-Side Environment Variables"
category: "environment-configuration"
subcategory: "security"
tags: ["nextjs", "environment-variables", "security", "client-side"]
stack: "cross-stack"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# NEXT_PUBLIC_ Prefix for Client-Side Environment Variables

## Overview

Next.js exposes environment variables to the browser only when prefixed with `NEXT_PUBLIC_`. All other variables remain server-side only. This pattern prevents accidental secret exposure to client-side JavaScript.

**Security Rule:** Never prefix secrets with `NEXT_PUBLIC_`
**Pattern Origin:** Next.js framework convention (adopted by Vercel, Netlify)
**Adoption:** 100% of Next.js projects

## Pattern Implementation

```bash
# .env.local

# ✅ Exposed to browser (safe for public access)
NEXT_PUBLIC_API_URL="https://api.example.com"
NEXT_PUBLIC_GTM_ID="GTM-XXXXXXX"
NEXT_PUBLIC_SANITY_PROJECT_ID="abc123"

# ✅ Server-only (never exposed to browser)
DATABASE_URL="postgresql://user:pass@localhost/db"
INTERNAL_API_SECRET="secret-key-here"
SANITY_API_WRITE_TOKEN="sk..."
```

## Usage in Code

```typescript
// Client component (runs in browser)
'use client';

export default function ClientComponent() {
    // ✅ Accessible (prefixed with NEXT_PUBLIC_)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    // ❌ Returns undefined (not prefixed, server-only)
    const secret = process.env.INTERNAL_API_SECRET;
}

// Server component (runs on server)
export default async function ServerComponent() {
    // ✅ Both accessible on server
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    const secret = process.env.INTERNAL_API_SECRET;
}
```

## What Gets Exposed

**Build Time:** Next.js inlines `NEXT_PUBLIC_` variables into JavaScript bundle
**Result:** Values visible in browser DevTools → Network tab → JS files

**Example Build Output:**
```javascript
// Before build
const url = process.env.NEXT_PUBLIC_API_URL;

// After build (inlined)
const url = "https://api.example.com";
```

## Common Pitfall: Secrets with NEXT_PUBLIC_

```bash
# ❌ WRONG: Secret exposed to all website visitors
NEXT_PUBLIC_DATABASE_PASSWORD="supersecret123"
NEXT_PUBLIC_STRIPE_SECRET_KEY="sk_live_..."
```

**Impact:** Anyone can view source code and extract secrets

## Related Patterns

- **Env File Hierarchy** - Load order for environment files
- **Never Commit Secrets** - Protecting secrets in version control

**Source:** policy-node, helix-dot-com-next (100% adoption across 3 Next.js repos)
