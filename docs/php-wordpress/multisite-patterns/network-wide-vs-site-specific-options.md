---
title: "Network-Wide vs Site-Specific Options"
category: "multisite-patterns"
subcategory: "option-management"
tags: ["wordpress-multisite", "options", "configuration", "network-admin"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WordPress multisite provides separate option storage systems: network-wide options (shared across all sites) and site-specific options (isolated per site). Understanding when to use `get_site_option()` versus `get_option()` is critical for multisite architecture decisions.

**Key Distinction:** Network options stored in `wp_sitemeta` table (single shared table), site options stored in per-site `wp_N_options` tables
**Common Use Cases:** License keys, network settings, API credentials (network), site preferences, theme options (per-site)
**Performance:** Network options slightly faster (no table prefix calculation)

## When to Use Network-Wide Options

WordPress multisite implementations use `get_site_option()` for network-wide storage when:

- **License keys or purchase codes** apply to entire network (single purchase for all sites)
- **API credentials** shared across all sites (e.g., Google Analytics tracking ID, Mailchimp API key)
- **Network configuration** affects all sites (e.g., allowed themes, plugin settings)
- **Cross-site feature flags** enable/disable functionality network-wide
- **Authentication tokens** for network-level integrations (SAML, SSO)

**Anti-Use Case:** Do not use network options for site-specific user preferences, theme settings, or per-site feature flags.

## Network Option Storage Pattern

Network-wide options use get_site_option and update_site_option for shared configuration across all sites.

### License Key Promotion Pattern

```php
/**
 * Store plugin license key network-wide
 * One license activates plugin for all sites in network
 */
// Check if already activated on main site
$main_site_license = get_blog_option(1, 'plugin_license_key');

if ($main_site_license) {
    // Promote to network option (shared by all sites)
    update_site_option('plugin_license_key', $main_site_license);
    update_site_option('license_activation_date', current_time('mysql'));
}

// Later: Check license from any site
$license = get_site_option('plugin_license_key', '');
if (empty($license)) {
    show_activation_prompt();
}
```

**Pattern:** Check main site option → Promote to network option → All sites share value
**Adoption:** Visual Composer, Freemius licensing framework (2 plugins)

**Source:** `airbnb/plugins/js_composer/include/autoload/bc-multisite-options.php`

## Network-Activated Plugin Detection

WordPress stores network-activated plugins in wp_sitemeta table under active_sitewide_plugins option.

### Network Activation Check Pattern

```php
/**
 * Check if plugin is network-activated
 * Network-activated plugins stored in wp_sitemeta
 */
if (is_multisite() && is_network_admin()) {
    $active_plugins = (array) get_site_option('active_sitewide_plugins', array());
    $active_plugins = array_keys($active_plugins);

    if (in_array('advanced-custom-fields-pro/acf.php', $active_plugins)) {
        // ACF is network-activated, enable network features
        enable_network_acf_sync();
    }
}
```

**WordPress Core Option:** `active_sitewide_plugins` (array of network-activated plugins)
**Format:** Array with plugin basename as key, activation timestamp as value
**Adoption:** 5 plugins check network activation status

**Source:** `airbnb/plugins/advanced-custom-fields-pro/acf.php`

## Site-Specific Option Storage Pattern

Per-site options use standard get_option and update_option functions with site-specific wp_N_options tables.

### Theme Options Per Site

```php
/**
 * Store per-site theme options
 * Each site has independent color scheme, logo, etc.
 */
// Site 1 (Main) - Blue theme
switch_to_blog(1);
update_option('theme_primary_color', '#0066CC');
update_option('site_logo_id', 123);
restore_current_blog();

// Site 4 (Newsroom) - Red theme
switch_to_blog(4);
update_option('theme_primary_color', '#CC0000');
update_option('site_logo_id', 456);
restore_current_blog();

// Later: Get current site's theme color
$color = get_option('theme_primary_color', '#000000');
```

**Pattern:** Each site stores independent values in own `wp_N_options` table
**Isolation:** Site 1 options do not affect Site 4 options
**Adoption:** 100% of site-specific settings (theme options, widget config, etc.)

## Network Option with Site Override Pattern

Hybrid approach allows network defaults with per-site override capability for special cases.

### Override Cascade Implementation

```php
/**
 * Network default with site-specific override capability
 * Example: Google Analytics tracking (network default, per-site override)
 */
function get_google_analytics_id() {
    // Check for site-specific override first
    $site_ga_id = get_option('ga_tracking_id', '');

    if (!empty($site_ga_id)) {
        return $site_ga_id; // Site override takes precedence
    }

    // Fall back to network default
    $network_ga_id = get_site_option('network_ga_tracking_id', '');
    return $network_ga_id;
}
```

**Pattern:** Site option → Network option → Default fallback
**Use Case:** Most sites use network default, special sites override
**Flexibility:** 20 sites share network ID, 2 sites use custom IDs

## Per-Site Feature Flags Pattern

get_blog_option function enables reading any site's options without context switching.

### Network-Wide Feature Flag Iteration

```php
/**
 * Enable SAML SSO per-site using feature flags
 * Network admin controls which sites have SAML enabled
 */
$sites = get_sites(['number' => 1000]);

foreach ($sites as $site) {
    $saml_enabled = get_blog_option($site->id, 'onelogin_saml_enabled', false);
    $saml_autocreate = get_blog_option($site->id, 'onelogin_saml_autocreate', false);

    if ($saml_enabled) {
        configure_saml_for_site($site->id, $saml_autocreate);
    }
}
```

**Function:** `get_blog_option($blog_id, $option, $default)` - Read option from any site without switching
**Pattern:** Network admin iterates all sites, checks per-site flags, configures selectively
**Adoption:** OneLogin SAML SSO plugin (8 get_blog_option calls, 4 update_blog_option calls)

**Source:** `airbnb/plugins/onelogin-saml-sso/php/functions.php`

## Network Menu Permissions Pattern

WordPress Network Admin menu visibility controlled by network option menu_items.

### Role-Based Menu Control

```php
/**
 * Control network admin menu visibility per user role
 * Stored in network option: 'menu_items'
 */
$menu_perms = get_site_option('menu_items', []);

if (empty($menu_perms['plugins']) && !current_user_can('manage_network_plugins')) {
    // Plugins menu disabled for this user role
    return false;
}

// User can see plugins menu in Network Admin
add_menu_page('Network Plugins', 'Plugins', 'manage_network', 'network-plugins');
```

**WordPress Core Option:** `menu_items` (controls Network Admin menu access)
**Security:** Restrict network admin UI based on capabilities
**Adoption:** WPGraphQL uses this for permission checks (2 occurrences)

**Source:** `airbnb/client-mu-plugins/vip-decoupled-bundle/lib/wp-graphql/src/Data/Connection/PluginConnectionResolver.php`

## Option Storage Decision Tree

```
Is the option value...

├─ Shared by ALL sites? (license key, API token)
│  └─ Use get_site_option() / update_site_option()
│
├─ Different per site? (theme color, logo, widgets)
│  └─ Use get_option() / update_option()
│
├─ Network default with per-site override? (GA tracking ID)
│  ├─ Store network default: update_site_option('network_ga_id', ...)
│  └─ Store site override: update_option('site_ga_id', ...)
│
└─ Read-only, set during install? (site domain, blog_id)
   └─ Use get_blog_details() or get_current_blog_id()
```

## Performance Considerations

### Database Table Comparison

```sql
-- Network options (shared table)
SELECT option_value FROM wp_sitemeta WHERE meta_key = 'plugin_license_key';

-- Site-specific options (per-site table)
SELECT option_value FROM wp_4_options WHERE option_name = 'theme_color';
```

**Query Performance:**
- Network option: Single table, no prefix calculation (faster)
- Site option: Per-site table with prefix `wp_N_` (requires blog_id lookup)

**Cache Behavior:**
- Network options cached in `site_options` cache group
- Site options cached in per-site `options` cache group
- Both benefit from object caching (Memcached/Redis)

### Bulk Read Optimization

```php
// ❌ INEFFICIENT: Multiple network option reads
for ($i = 1; $i <= 10; $i++) {
    $value = get_site_option("setting_{$i}");
}

// ✅ EFFICIENT: Single read of serialized array
$all_settings = get_site_option('all_network_settings', []);
for ($i = 1; $i <= 10; $i++) {
    $value = $all_settings["setting_{$i}"] ?? null;
}
```

**Pattern:** Store related network options as single serialized array
**Performance Gain:** 10 database queries → 1 database query

## Antipattern: Storing Per-Site Data in Network Options

Site-specific configuration should use per-site options not network options with blog ID prefixes.

### Namespace Pollution Example

```php
// ❌ WRONG: Site-specific theme color in network option
update_site_option('blog_4_theme_color', '#FF0000');
update_site_option('blog_8_theme_color', '#0000FF');
```

**Problem:** Namespace pollution, difficult to manage, not scalable
**Impact:** 1000 sites = 1000 network options for theme colors

**✅ Correct:** Use per-site options
```php
switch_to_blog(4);
update_option('theme_color', '#FF0000');
restore_current_blog();

switch_to_blog(8);
update_option('theme_color', '#0000FF');
restore_current_blog();
```

## Antipattern: Using get_option for Network-Wide Data

Network-wide configuration requires get_site_option to avoid per-site context switching.

### Site Option for Network Data Example

```php
// ❌ WRONG: License key stored per-site
switch_to_blog(1);
$license = get_option('plugin_license_key');
restore_current_blog();
```

**Problem:** Other sites don't have access to license, must switch context
**Maintenance:** Update license on main site only, other sites unaware

**✅ Correct:** Use network option
```php
$license = get_site_option('plugin_license_key');
// Available from any site, no context switching
```

## Antipattern: Not Checking is_multisite Before Network Options

Plugins must check is_multisite to ensure compatibility between multisite and single-site installations.

### Missing Multisite Check Example

```php
// ❌ WRONG: Assumes multisite, breaks on single site
$license = get_site_option('plugin_license_key');
```

**Problem:** `get_site_option()` works on single site but inconsistent with `get_option()`
**Portability:** Plugin fails when moved from multisite to single site

**✅ Correct:** Fallback pattern
```php
$license = is_multisite()
    ? get_site_option('plugin_license_key', '')
    : get_option('plugin_license_key', '');
```

## Testing Strategies

### PHPUnit Test for Option Isolation

```php
class NetworkOptionTest extends WP_UnitTestCase {
    public function test_network_option_shared_across_sites() {
        // Set network option
        update_site_option('shared_api_key', 'abc123');

        // Verify accessible from Blog 1
        switch_to_blog(1);
        $this->assertEquals('abc123', get_site_option('shared_api_key'));
        restore_current_blog();

        // Verify accessible from Blog 4
        switch_to_blog(4);
        $this->assertEquals('abc123', get_site_option('shared_api_key'));
        restore_current_blog();
    }

    public function test_site_options_isolated() {
        // Set different values on two sites
        switch_to_blog(1);
        update_option('theme_color', 'blue');
        restore_current_blog();

        switch_to_blog(4);
        update_option('theme_color', 'red');
        restore_current_blog();

        // Verify isolation
        switch_to_blog(1);
        $this->assertEquals('blue', get_option('theme_color'));
        restore_current_blog();

        switch_to_blog(4);
        $this->assertEquals('red', get_option('theme_color'));
        restore_current_blog();
    }
}
```

## Real-World Examples

### Example 1: Visual Composer License (Network Option)

**Scenario:** Single Visual Composer license for entire network (20+ sites)

**Implementation:**
```php
// Check main site activation
$main_license = get_blog_option(1, 'wpb_js_js_composer_purchase_code');

if ($main_license) {
    // Promote to network option (all sites share)
    update_site_option('wpb_js_js_composer_purchase_code', $main_license);
    update_site_option('vc_bc_options_called', true);
}
```

**Benefit:** Single license activation, no per-site license entry required

**Source:** `airbnb/plugins/js_composer/include/autoload/bc-multisite-options.php`

### Example 2: OneLogin SAML Per-Site Enablement

**Scenario:** SAML SSO available network-wide, but only enabled for specific sites (corporate sites, not public blogs)

**Implementation:**
```php
// Network admin UI sets per-site flags
update_blog_option(1, 'onelogin_saml_enabled', true);  // Main site
update_blog_option(4, 'onelogin_saml_enabled', true);  // Newsroom
update_blog_option(8, 'onelogin_saml_enabled', false); // Careers (public)

// SAML plugin checks flag per site
$sites = get_sites();
foreach ($sites as $site) {
    $enabled = get_blog_option($site->id, 'onelogin_saml_enabled', false);
    if ($enabled) {
        enable_saml_for_site($site->id);
    }
}
```

**Pattern:** Network plugin, per-site feature flags, selective activation

**Source:** `airbnb/plugins/onelogin-saml-sso/php/functions.php`

## Migration Path

### Converting Site Option to Network Option

```php
/**
 * Migrate plugin settings from main site to network option
 * Run once during multisite conversion
 */
function migrate_to_network_option() {
    if (!is_multisite()) {
        return; // Skip on single site
    }

    // Read from main site (Blog 1)
    $old_value = get_blog_option(1, 'plugin_api_key', '');

    if (!empty($old_value)) {
        // Promote to network option
        update_site_option('plugin_api_key', $old_value);

        // Optionally remove from main site
        delete_blog_option(1, 'plugin_api_key');

        // Mark migration complete
        update_site_option('plugin_migrated_to_network', true);
    }
}
add_action('admin_init', 'migrate_to_network_option');
```

## Related Patterns

- **Conditional Blog-Specific Plugin Loading** - Combine with network options for feature flags
- **Network Admin Menu Registration** - Store network admin settings in network options
- **switch_to_blog Pattern** - Alternative to get_blog_option for complex reads

## References

- WordPress Codex: `get_site_option()`
- WordPress Codex: `update_site_option()`
- WordPress Codex: `get_blog_option()`

**Source Analysis:** airbnb codebase (93 get_site_option calls, 18 update_site_option calls, 8 get_blog_option calls)
**Pattern Adoption:** 100% of network-wide configuration storage in multisite
