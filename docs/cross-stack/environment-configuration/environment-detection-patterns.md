---
title: "Environment Detection Patterns Across Stacks"
category: "environment-configuration"
subcategory: "runtime-configuration"
tags: ["environment-detection", "nodejs", "php", "conditional-logic"]
stack: "cross-stack"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Environment Detection Patterns Across Stacks

## Overview

All stacks use environment detection to enable debug features, configure logging, and adjust behavior between development, staging, and production.

**Common Pattern:** Single environment variable (`NODE_ENV`, `WP_ENV`) determines mode
**Adoption:** 100% of projects use environment-based conditional logic

## Next.js: NODE_ENV

```typescript
// Automatic: Next.js sets NODE_ENV
const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

if (isDevelopment) {
    // Enable React DevTools, verbose logging
    console.log('Development mode enabled');
}

// Custom environments
const isStaging = process.env.NEXT_PUBLIC_ENVIRONMENT === 'staging';
```

**Values:** `development`, `production`, `test`
**Set By:** Next.js framework (`next dev` → development, `next build` → production)

## WordPress: WP_ENV Constant

```php
// scripts/wp-config.php
define('WP_ENV', $_ENV['WP_ENV'] ?? 'production');

if (WP_ENV === 'development') {
    define('WP_DEBUG', true);
    define('WP_DEBUG_LOG', true);
    define('SAVEQUERIES', true);
} elseif (WP_ENV === 'staging') {
    define('WP_DEBUG', true);
    define('WP_DEBUG_DISPLAY', false); // Log but don't show
} else { // production
    define('WP_DEBUG', false);
    @ini_set('display_errors', 0);
}
```

**Values:** `development`, `staging`, `production`
**Pattern:** Switch statement with fallback to production (secure default)

## VIP Go: VIP_GO_ENV

```php
// WordPress VIP platform
if (defined('VIP_GO_ENV') && VIP_GO_ENV === 'production') {
    // Production-only optimizations
    define('WPCOM_VIP_USE_JETPACK_PHOTON', true);
}
```

**Platform-Specific:** Set by WordPress VIP Go infrastructure

## Sanity: Inherits from Next.js

```typescript
// sanity.config.ts
export default defineConfig({
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
    dataset: process.env.NODE_ENV === 'development' 
        ? 'development' 
        : 'production',
});
```

## Multi-Environment Strategy

```typescript
// Custom environment tiers
const env = process.env.NEXT_PUBLIC_ENVIRONMENT || 'production';

const config = {
    development: {
        apiUrl: 'http://localhost:4000',
        debug: true,
    },
    staging: {
        apiUrl: 'https://api-staging.example.com',
        debug: true,
    },
    production: {
        apiUrl: 'https://api.example.com',
        debug: false,
    },
};

export default config[env];
```

**Source:** 103 process.env references (Next.js), 37 $_ENV references (WordPress)
