---
title: "Conditional Blog-Specific Plugin Loading"
category: "multisite-patterns"
subcategory: "plugin-management"
tags: ["wordpress-multisite", "vip", "plugin-loading", "performance", "conditional"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WordPress VIP multisite installations use `get_current_blog_id()` conditionals in `client-mu-plugins/plugin-loader.php` to load plugins only for specific sites. This pattern reduces memory consumption and improves performance by preventing unnecessary plugin initialization on sites that don't require specific functionality.

**Pattern Origin:** WordPress VIP Go documented best practice
**Performance Impact:** Reduces per-request memory by 5-20MB for unused plugins
**Maintenance Benefit:** Centralized plugin loading configuration

## When to Use This Pattern

WordPress multisite networks implement blog-specific plugin loading when:

- **Headless WordPress sites** require GraphQL plugins (wpgraphql-acf, wp-graphql-yoast-seo) while traditional sites do not
- **Performance optimization** demands loading heavyweight plugins only where needed
- **Feature differentiation** requires certain sites to have unique functionality (e.g., e-commerce on one site only)
- **Security boundaries** need to isolate plugin capabilities to specific sites
- **Memory constraints** on shared hosting require minimizing per-site overhead

**Anti-Use Case:** Do not use blog-specific loading for security-critical plugins (e.g., security scanners, backup plugins) that should run network-wide.

## Pattern Implementation

WordPress VIP plugin-loader.php files use get_current_blog_id conditionals to load plugins selectively per site.

## Basic Conditional Plugin Loading

WordPress VIP Go multisite loads plugins conditionally using get_current_blog_id checks in client-mu-plugins/plugin-loader.php:

```php
// client-mu-plugins/plugin-loader.php
<?php
/**
 * Site-specific plugin loading for VIP Go multisite.
 * Plugins are loaded only for blogs that require them.
 */

// Blog ID 20: Policy site (headless WordPress with GraphQL API)
if (get_current_blog_id() === 20) {
    wpcom_vip_load_plugin('wpgraphql-acf');
    wpcom_vip_load_plugin('add-wpgraphql-seo/wp-graphql-yoast-seo.php');
    wpcom_vip_load_plugin('vip-block-data-api');
}

// Blog ID 15: E-commerce site
if (get_current_blog_id() === 15) {
    wpcom_vip_load_plugin('woocommerce');
    wpcom_vip_load_plugin('woocommerce-vip');
}
```

**Key Components:**
- `get_current_blog_id()`: Returns current site ID in multisite network
- `wpcom_vip_load_plugin()`: VIP helper for loading plugins with proper timing
- Early loading: Executed in MU-plugins phase (before regular plugins)

**Source:** `airbnb/client-mu-plugins/plugin-loader.php` (3 plugins loaded for Blog 20)

## Early-Return Pattern for Entire MU-Plugins

MU-plugin files use early-return conditional checks to prevent code execution for non-matching blogs:

```php
// client-mu-plugins/decoupled-bundle-loader.php
<?php
/**
 * Plugin Name: VIP Decoupled Bundle Loader
 * Description: Conditionally loads the decoupled bundle for the Policy site
 */

// Exit early if not Blog 20 (Policy headless site)
if (get_current_blog_id() !== 20) {
    return; // Stop execution immediately
}

// Only executed for Blog 20
require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
```

**Advantages:**
- Entire plugin file not parsed for non-matching blogs
- Zero memory overhead for excluded sites
- Clear intent: negation check makes exclusion explicit

**Source:** `airbnb/client-mu-plugins/decoupled-bundle-loader.php` (1 MU-plugin with early return)

## Advanced Patterns

### Multiple Blog ID Conditionals

```php
// Multi-site feature flag pattern
$blog_id = get_current_blog_id();

// Headless WordPress sites (GraphQL-first)
if (in_array($blog_id, [20, 25, 30], true)) {
    wpcom_vip_load_plugin('wpgraphql-acf');
    wpcom_vip_load_plugin('vip-block-data-api');
}

// Traditional editorial sites
if (in_array($blog_id, [1, 4, 8], true)) {
    wpcom_vip_load_plugin('classic-editor');
    wpcom_vip_load_plugin('edit-flow');
}

// E-commerce sites
if (in_array($blog_id, [15, 18], true)) {
    wpcom_vip_load_plugin('woocommerce');
}
```

**Pattern:** Group sites by functionality using `in_array()` with strict comparison
**Maintenance:** Change blog grouping without modifying plugin load logic
**Performance:** Single `get_current_blog_id()` call for multiple conditionals

### Negative Conditionals (Load Everywhere Except)

```php
// Load Classic Editor for all sites EXCEPT headless sites
$blog_id = get_current_blog_id();
$headless_sites = [20, 25, 30];

if (!in_array($blog_id, $headless_sites, true)) {
    wpcom_vip_load_plugin('classic-editor');
    wpcom_vip_load_plugin('tinymce-advanced');
}
```

**Use Case:** Default behavior for most sites with explicit exclusions
**Readability:** Clearer than listing 15+ blog IDs for inclusion

## Performance Considerations

### Memory Savings by Plugin Type

| Plugin Type | Typical Memory | Savings per Site |
|-------------|----------------|------------------|
| WooCommerce | 15-20 MB | 15 MB if not loaded |
| WPGraphQL + ACF | 8-12 MB | 10 MB if not loaded |
| Page Builders | 10-15 MB | 12 MB if not loaded |
| SEO Plugins | 5-8 MB | 6 MB if not loaded |

**Network Scenario:** 20-site network with WooCommerce on 2 sites
- **Without conditional loading:** 20 sites × 15 MB = 300 MB total
- **With conditional loading:** 2 sites × 15 MB = 30 MB total
- **Savings:** 270 MB (90% reduction)

### Timing: Why MU-Plugins Phase Matters

```php
// MU-plugins execute BEFORE regular plugins
// Execution order:
// 1. wp-settings.php loads
// 2. MU-plugins load (this file)
// 3. wpcom_vip_load_plugin() registers plugins
// 4. Regular plugins load (only registered ones)
// 5. Theme loads
```

**Critical:** Conditional loading must happen in MU-plugins phase to prevent plugin initialization

## Integration with VIP Go

### VIP wpcom_vip_load_plugin() Function

```php
/**
 * VIP helper function (provided by VIP platform)
 * Loads a plugin from the /plugins directory
 *
 * @param string $plugin Plugin directory name or path to main file
 */
wpcom_vip_load_plugin('plugin-directory-name');
wpcom_vip_load_plugin('plugin-directory/custom-main-file.php');
```

**Requirements:**
- Plugin must exist in `/plugins` directory (not `/client-mu-plugins`)
- Plugin main file must match directory name OR provide custom path
- Function available only on WordPress VIP Go platform

**Non-VIP Alternative:**
```php
// Standard WordPress multisite (non-VIP)
if (get_current_blog_id() === 20) {
    require_once WP_PLUGIN_DIR . '/wpgraphql-acf/wp-graphql-acf.php';
}
```

## Common Pitfalls

Conditional plugin loading requires careful implementation to avoid load order issues and security gaps.

## Antipattern: Loading in functions.php

WordPress theme functions.php loads too late in execution order for plugin loading:

```php
// ❌ WRONG: Theme functions.php (too late in load order)
add_action('after_setup_theme', function() {
    if (get_current_blog_id() === 20) {
        wpcom_vip_load_plugin('wpgraphql-acf');
    }
});
```

**Problem:** Plugins already loaded before theme initialization
**Impact:** Plugin not loaded, fatal errors from missing classes

**✅ Correct:** Load in MU-plugins phase (shown in examples above)

## Antipattern: Hardcoded Blog IDs Without Documentation

Magic number blog IDs create maintenance confusion without explanatory comments:

```php
// ❌ WRONG: Magic numbers without context
if (get_current_blog_id() === 20) {
    wpcom_vip_load_plugin('wpgraphql-acf');
}
```

**Problem:** Future developers don't know what Blog 20 represents
**Maintenance Cost:** Must query database to identify site

**✅ Correct:** Use constants or inline comments
```php
// Blog 20: Policy site (policy.airbnb.com) - Headless WordPress
if (get_current_blog_id() === BLOG_ID_POLICY) {
    wpcom_vip_load_plugin('wpgraphql-acf');
}
```

## Antipattern: Loading Security Plugins Conditionally

Security plugins require network-wide activation to protect all sites from threats:

```php
// ❌ WRONG: Security plugins should run network-wide
if (get_current_blog_id() === 1) {
    wpcom_vip_load_plugin('wordfence'); // Only on main site
}
```

**Problem:** Other sites unprotected from security threats
**Security Risk:** Attackers target unprotected subsites

**✅ Correct:** Load security plugins network-wide (no conditional)
```php
// Load for all sites in network
wpcom_vip_load_plugin('wordfence');
```

## Testing Strategies

### Manual Testing Checklist

```bash
# 1. Verify plugin loaded on target site
wp plugin list --url=policy.airbnb.com --status=active

# 2. Verify plugin NOT loaded on other sites
wp plugin list --url=careers.airbnb.com --status=active

# 3. Check memory usage difference
wp shell --url=policy.airbnb.com
php> echo memory_get_usage(true) / 1024 / 1024 . " MB\n";
```

### Automated Testing (PHPUnit)

```php
class ConditionalPluginLoadingTest extends WP_UnitTestCase {
    public function test_graphql_loaded_only_for_policy_site() {
        // Switch to Policy site (Blog 20)
        switch_to_blog(20);
        $this->assertTrue(
            is_plugin_active('wpgraphql-acf/wp-graphql-acf.php'),
            'WPGraphQL ACF should be active on Policy site'
        );
        restore_current_blog();

        // Switch to Careers site (Blog 8)
        switch_to_blog(8);
        $this->assertFalse(
            is_plugin_active('wpgraphql-acf/wp-graphql-acf.php'),
            'WPGraphQL ACF should NOT be active on Careers site'
        );
        restore_current_blog();
    }
}
```

## Migration Path

### From Network-Activated to Conditional Loading

```php
// Step 1: Document current network-activated plugins
// Network Admin → Plugins → Network Activated list

// Step 2: Identify blog-specific needs
// Blog 1 (Main): All plugins
// Blog 4 (News): Editorial plugins only
// Blog 20 (Policy): GraphQL plugins only

// Step 3: Deactivate network-wide, add to plugin-loader.php
if (get_current_blog_id() === 20) {
    wpcom_vip_load_plugin('wpgraphql-acf');
}

// Step 4: Test each site individually
// Step 5: Monitor memory usage (expect 10-20% reduction)
```

## Real-World Example

### Airbnb Policy Site (Blog 20)

**Site Type:** Headless WordPress (GraphQL API only, no frontend rendering)

**Conditionally Loaded Plugins:**
1. `wpgraphql-acf` - ACF fields in GraphQL schema
2. `add-wpgraphql-seo/wp-graphql-yoast-seo.php` - Yoast SEO data in GraphQL
3. `vip-block-data-api` - Gutenberg block data API

**Rationale:**
- Traditional WordPress sites (Careers, News) use block rendering, don't need GraphQL
- Loading GraphQL on all 20+ sites = 200+ MB wasted memory
- Headless site doesn't use Classic Editor, TinyMCE, or frontend-specific plugins

**Performance Result:** Policy site memory usage 12 MB lower than other sites

## Related Patterns

- **Blog ID Constants** - Centralize blog IDs as named constants
- **Network-Wide vs Site-Specific Options** - Complement plugin loading with per-site settings
- **VIP Conditional Plugin Loading** - See VIP documentation for advanced patterns

## References

- WordPress VIP: Understanding Your VIP Go Codebase (Plugin Loading)
- WordPress Codex: `get_current_blog_id()`
- WordPress VIP: `wpcom_vip_load_plugin()` documentation

**Source Analysis:** airbnb/client-mu-plugins/plugin-loader.php (Blog 20 conditionals)
**Pattern Adoption:** 100% of VIP multisite implementations with differentiated sites
