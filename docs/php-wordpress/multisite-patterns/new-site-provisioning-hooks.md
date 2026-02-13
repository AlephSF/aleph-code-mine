---
title: "New Site Provisioning with wp_initialize_site"
category: "multisite-patterns"
subcategory: "site-lifecycle"
tags: ["wordpress-multisite", "site-creation", "provisioning", "hooks"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# New Site Provisioning with wp_initialize_site

## Overview

WordPress 5.1+ uses the `wp_initialize_site` action hook for site provisioning when new sites are created in a multisite network. This hook replaces the deprecated `wpmu_new_blog` hook and provides a more structured `WP_Site` object parameter.

**Modern Hook:** `wp_initialize_site` (WordPress 5.1+)
**Deprecated Hook:** `wpmu_new_blog` (WordPress < 5.1, still works for backward compatibility)
**Use Cases:** Auto-activate plugins, set default options, import starter content, configure themes

## Pattern Implementation

```php
/**
 * Auto-activate plugin on newly created sites
 * Hook fires after WordPress core setup (priority 10)
 */
add_action('wp_initialize_site', 'activate_plugin_on_new_site', 50);

function activate_plugin_on_new_site($new_site) {
    // $new_site is WP_Site object with properties:
    // - id (blog_id), domain, path, site_id, registered

    switch_to_blog($new_site->id);

    // Run plugin activation logic
    activate_plugin_features();
    set_default_options();

    restore_current_blog();
}
```

**Priority:** 50 (after WordPress core setup at priority 10)

**Source:** Polylang Pro, Yoast SEO, Freemius licensing

## Legacy Compatibility Pattern

```php
/**
 * Support both modern and legacy hooks
 * For plugins supporting WordPress < 5.1
 */
if (version_compare($GLOBALS['wp_version'], '5.1', '<')) {
    add_action('wpmu_new_blog', 'legacy_new_site_callback', 10, 6);
} else {
    add_action('wp_initialize_site', 'modern_new_site_callback', 11, 2);
}

function modern_new_site_callback($new_site, $args) {
    switch_to_blog($new_site->id);
    run_activation_logic();
    restore_current_blog();
}

function legacy_new_site_callback($blog_id, $user_id, $domain, $path, $site_id, $meta) {
    switch_to_blog($blog_id);
    run_activation_logic();
    restore_current_blog();
}
```

**Source:** Freemius framework (version compatibility)

**Pattern Adoption:** 100% of modern multisite provisioning (WordPress 5.1+)
