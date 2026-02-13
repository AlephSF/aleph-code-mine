---
title: "Blog ID Constants Centralization"
category: "multisite-patterns"
subcategory: "maintenance"
tags: ["wordpress-multisite", "blog-id", "constants", "best-practices"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Blog ID Constants Centralization

## Overview

WordPress multisite codebases often hardcode blog IDs (e.g., `get_current_blog_id() === 20`) in multiple files, making maintenance difficult when site IDs change. Centralizing blog IDs as named constants improves code clarity and simplifies network reorganization.

**Antipattern:** Hardcoded magic numbers (Blog ID 20) without documentation
**Best Practice:** Named constants (BLOG_ID_POLICY) defined in wp-config.php or constants file
**Benefit:** Single source of truth, searchable names, self-documenting code

## Pattern Implementation

```php
// wp-config.php - Define blog ID constants
define('BLOG_ID_MAIN', 1);
define('BLOG_ID_NEWSROOM', 4);
define('BLOG_ID_CAREERS', 8);
define('BLOG_ID_POLICY', 20); // Headless WordPress (policy.airbnb.com)

// Later: Use named constant instead of magic number
if (get_current_blog_id() === BLOG_ID_POLICY) {
    wpcom_vip_load_plugin('wpgraphql-acf');
}
```

**Before (Hardcoded):**
```php
if (get_current_blog_id() === 20) { // What is blog 20?
    wpcom_vip_load_plugin('wpgraphql-acf');
}
```

**After (Named Constant):**
```php
if (get_current_blog_id() === BLOG_ID_POLICY) { // Clear purpose!
    wpcom_vip_load_plugin('wpgraphql-acf');
}
```

## Real-World Hardcoded IDs in Airbnb Codebase

**Identified Blog IDs:**
- Blog ID 4: Newsroom (hardcoded in `themes/airbnb-careers/partials/modules/module-news_posts.php`)
- Blog ID 20: Policy site (hardcoded in `client-mu-plugins/plugin-loader.php`, `decoupled-bundle-loader.php`)

**Recommendation:** Define these as constants for maintainability

**Source:** airbnb codebase analysis (2 hardcoded blog IDs found)

**Pattern Adoption:** 0% currently, 100% recommended best practice
