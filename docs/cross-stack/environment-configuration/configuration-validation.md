---
title: "Runtime Configuration Validation"
category: "environment-configuration"
subcategory: "error-prevention"
tags: ["validation", "startup-checks", "error-handling"]
stack: "cross-stack"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-12"
---

# Runtime Configuration Validation

## Overview

**Gap Pattern:** 0% of analyzed projects validate required environment variables at startup. Missing variables cause runtime failures with cryptic error messages.

**Recommendation:** Add explicit validation to fail fast with clear error messages
**Benefit:** Catch configuration errors before deployment, improve developer experience

## Recommended Pattern: Startup Validation

```typescript
// config/validateEnv.ts
const requiredEnvVars = [
    'NEXT_PUBLIC_API_URL',
    'DATABASE_URL',
    'INTERNAL_API_SECRET',
] as const;

export function validateEnv() {
    const missing: string[] = [];

    for (const envVar of requiredEnvVars) {
        if (!process.env[envVar]) {
            missing.push(envVar);
        }
    }

    if (missing.length > 0) {
        throw new Error(
            `Missing required environment variables:\n` +
            missing.map(v => `  - ${v}`).join('\n') +
            `\n\nPlease check your .env.local file.`
        );
    }
}

// Call in root layout or entry point
validateEnv();
```

## WordPress: Fallback with Warnings

```php
// wp-config.php
$required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST'];

foreach ($required_env_vars as $var) {
    if (!isset($_ENV[$var]) || empty($_ENV[$var])) {
        wp_die("Missing required environment variable: {$var}");
    }
}
```

## Zod Schema Validation (TypeScript)

```typescript
import { z } from 'zod';

const envSchema = z.object({
    NODE_ENV: z.enum(['development', 'production', 'test']),
    NEXT_PUBLIC_API_URL: z.string().url(),
    DATABASE_URL: z.string().startsWith('postgresql://'),
    PORT: z.string().regex(/^\d+$/).transform(Number).default('3000'),
});

// Validate and export typed env
export const env = envSchema.parse(process.env);

// TypeScript knows env.PORT is a number!
```

## Benefits of Validation

1. **Fail Fast:** Error at startup vs runtime
2. **Clear Messages:** "Missing DATABASE_URL" vs "Cannot read property 'connect' of undefined"
3. **Type Safety:** Zod provides TypeScript types
4. **Documentation:** Schema serves as env var documentation

**Current Adoption:** 0% (gap pattern)
**Recommendation Priority:** High (prevents deployment issues)
