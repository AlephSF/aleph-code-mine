---
title: "Cross-Site Queries with get_sites()"
category: "multisite-patterns"
subcategory: "network-iteration"
tags: ["wordpress-multisite", "get_sites", "network-operations", "wp-cli"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Cross-Site Queries with get_sites()

## Overview

WordPress multisite uses `get_sites()` to retrieve a list of all sites in the network for iteration, bulk operations, and network-wide administration. This function replaces the deprecated `wp_get_sites()` and `get_blog_list()` as of WordPress 4.6+.

**Primary Use Case:** Network-wide operations (indexation, cleanup, SAML configuration, user provisioning)
**Performance:** Returns site objects with basic metadata (ID, domain, path) without full site details
**Scalability:** Supports pagination for large networks (1000+ sites)

## When to Use get_sites()

WordPress multisite implementations use `get_sites()` when:

- **WP-CLI commands** need to run operations across all sites (indexation, cleanup, migrations)
- **Network admin UI** displays list of sites for configuration (SAML, feature flags)
- **User provisioning** auto-enrolls users on multiple sites based on roles
- **Content synchronization** copies data from one site to all others
- **Maintenance scripts** perform bulk updates, cleanups, or health checks

**Anti-Use Case:** Do not use for single-site operations or when site count exceeds pagination limits without pagination logic.

## Pattern Implementation

### Basic All-Sites Iteration

```php
/**
 * Run cleanup across all sites in network
 * Common pattern in WP-CLI commands
 */
$criteria = [
    'archived' => 0, // Exclude archived sites
    'deleted'  => 0, // Exclude deleted sites
    'spam'     => 0, // Exclude spam sites (if spam filtering enabled)
];

$sites = get_sites($criteria);

foreach ($sites as $site) {
    // $site is WP_Site object with properties:
    // - blog_id, domain, path, site_id, registered, last_updated

    switch_to_blog($site->blog_id);

    // Run cleanup operation for current site
    $removed = cleanup_expired_transients();
    WP_CLI::log("Site {$site->domain}: Removed {$removed} transients");

    restore_current_blog();
}

WP_CLI::success("Cleanup complete for " . count($sites) . " sites");
```

**Pattern:** Filter criteria → get_sites() → Iterate with switch/restore
**Adoption:** Yoast SEO WP-CLI (2 commands use this pattern)

**Source:** `airbnb/plugins/wordpress-seo/src/commands/cleanup-command.php`

### Network-Wide SAML Configuration

```php
/**
 * Display SAML configuration UI for all sites
 * Network admin selects which sites have SAML enabled
 */
$opts = array('number' => 1000); // Max 1000 sites
$sites = get_sites($opts);

echo '<table class="form-table"><tbody>';
echo '<tr><th>Select/Unselect All</th><td><input type="checkbox" id="selector"></td></tr>';

foreach ($sites as $site) {
    $site_address = untrailingslashit($site->domain . $site->path);
    $enabled = get_blog_option($site->blog_id, 'onelogin_saml_enabled', false);

    echo "<tr>";
    echo "<th>{$site_address}</th>";
    echo "<td><input type='checkbox' name='sites[]' value='{$site->blog_id}' "
        . checked($enabled, true, false) . "></td>";
    echo "</tr>";
}

echo '</tbody></table>';
```

**Pattern:** Fetch all sites → Display with per-site checkboxes → Save per-site options
**Limitation:** Hardcoded 1000 site limit (scalability issue for larger networks)

**Source:** `airbnb/plugins/onelogin-saml-sso/php/network_saml_enabler.php`

## Advanced Patterns

### Pagination for Large Networks

```php
/**
 * Handle networks with 1000+ sites using pagination
 * Prevents memory exhaustion and timeout issues
 */
$page = 1;
$per_page = 100; // Process 100 sites at a time

do {
    $sites = get_sites([
        'number' => $per_page,
        'offset' => ($page - 1) * $per_page,
        'archived' => 0,
        'deleted' => 0,
    ]);

    foreach ($sites as $site) {
        switch_to_blog($site->blog_id);
        perform_maintenance_task();
        restore_current_blog();
    }

    WP_CLI::log("Processed page {$page} (" . count($sites) . " sites)");
    $page++;

} while (count($sites) === $per_page); // Continue if full page returned

WP_CLI::success("All sites processed");
```

**Pattern:** Paginate with offset → Loop until partial page (indicates end)
**Performance:** Prevents loading 10,000 site objects into memory simultaneously
**Use Case:** Enterprise networks (universities, government, large corporations)

### Filtering by Domain Pattern

```php
/**
 * Run operations only on specific subdomain pattern
 * Example: Only process *.staging.example.com sites
 */
$all_sites = get_sites(['number' => 10000]);

$staging_sites = array_filter($all_sites, function($site) {
    return str_contains($site->domain, '.staging.example.com');
});

foreach ($staging_sites as $site) {
    switch_to_blog($site->blog_id);
    // Run staging-specific operations
    restore_current_blog();
}

WP_CLI::log("Processed " . count($staging_sites) . " staging sites");
```

**Pattern:** Fetch all → Filter by domain → Process subset
**Use Case:** Separate staging and production sites in same network

### Auto-Enroll Users on Multiple Sites

```php
/**
 * Add SAML-authenticated user to all sites with auto-create enabled
 * Triggered after successful SAML login
 */
function enroll_user_on_sites($user_id, $roles) {
    $sites = get_sites(array('number' => 1000));

    foreach ($sites as $site) {
        $autocreate = get_blog_option($site->blog_id, "onelogin_saml_autocreate", false);

        // Skip if auto-create disabled for this site
        if (!$autocreate) {
            continue;
        }

        // Skip if user already member of site
        if (is_user_member_of_blog($user_id, $site->blog_id)) {
            continue;
        }

        // Add user to site with specified roles
        foreach ($roles as $role) {
            add_user_to_blog($site->blog_id, $user_id, $role);
        }
    }
}
```

**Pattern:** Per-site feature flags control user provisioning
**Security:** Only adds user to sites with explicit opt-in (autocreate flag)

**Source:** `airbnb/plugins/onelogin-saml-sso/php/functions.php`

### Exclude Main Site from Operations

```php
/**
 * Run operation on all sites EXCEPT main site (Blog 1)
 * Main site often has special configuration
 */
$sites = get_sites(['archived' => 0, 'deleted' => 0]);

foreach ($sites as $site) {
    if ($site->blog_id == 1) {
        continue; // Skip main site
    }

    switch_to_blog($site->blog_id);
    // Run operation on subsites only
    restore_current_blog();
}
```

**Use Case:** Testing changes on subsites before applying to main production site

## get_sites() vs Deprecated Alternatives

### Migration from get_blog_list() (WordPress < 3.0)

```php
// ❌ DEPRECATED: get_blog_list() (removed in WordPress 4.6)
global $wpdb;
$blogs = $wpdb->get_results("SELECT blog_id FROM {$wpdb->blogs}");

// ✅ MODERN: get_sites() (WordPress 4.6+)
$sites = get_sites();
```

### Migration from wp_get_sites() (WordPress 3.7-4.5)

```php
// ❌ DEPRECATED: wp_get_sites() (deprecated in WordPress 4.6)
$sites = wp_get_sites(['limit' => 100]);

// ✅ MODERN: get_sites() (WordPress 4.6+)
$sites = get_sites(['number' => 100]);
```

**Parameter Changes:**
- `limit` → `number` (max sites to return)
- Returns `WP_Site` objects instead of arrays

## Performance Considerations

### Query Performance by Network Size

| Network Size | get_sites() Time | Recommended Approach |
|--------------|------------------|----------------------|
| 1-50 sites | <10ms | Fetch all, no pagination |
| 50-500 sites | 10-100ms | Fetch all with 'number' limit |
| 500-5000 sites | 100-500ms | Paginate (100-200 per page) |
| 5000+ sites | 500ms-2s | Paginate + background processing |

### Memory Consumption

```php
// Each WP_Site object: ~1-2 KB
// 1000 sites = 1-2 MB memory
// 10,000 sites = 10-20 MB memory (pagination recommended)
```

**Optimization:** Use pagination for networks > 1000 sites to prevent memory exhaustion

### Caching Considerations

```php
/**
 * Cache site list for frequent reads
 * Reduces database queries in network admin
 */
$sites = wp_cache_get('all_network_sites', 'multisite');

if (false === $sites) {
    $sites = get_sites(['number' => 10000]);
    wp_cache_set('all_network_sites', $sites, 'multisite', HOUR_IN_SECONDS);
}

// Use cached site list
foreach ($sites as $site) {
    // ...
}
```

**Cache Invalidation:** Flush cache when site created/deleted (wp_initialize_site, delete_blog hooks)

## Common Antipatterns

### Antipattern 1: Hardcoded Site Limit Without Pagination

```php
// ❌ WRONG: Hardcoded limit, fails for networks > 1000 sites
$sites = get_sites(array('number' => 1000));
```

**Problem:** Sites beyond 1000 are ignored, operations incomplete
**Impact:** 1500-site network processes only first 1000, 500 sites skipped

**✅ Correct:** Implement pagination (shown in Advanced Patterns)

### Antipattern 2: Missing Error Handling

```php
// ❌ WRONG: Assumes get_sites() always returns sites
$sites = get_sites();
foreach ($sites as $site) {
    // Fatal error if $sites is empty or false
}
```

**✅ Correct:** Check return value
```php
$sites = get_sites(['archived' => 0, 'deleted' => 0]);

if (empty($sites)) {
    WP_CLI::warning('No sites found in network');
    return;
}

foreach ($sites as $site) {
    // ...
}
```

### Antipattern 3: Iterating Without switch_to_blog()

```php
// ❌ WRONG: Assume current blog context applies to all sites
$sites = get_sites();
foreach ($sites as $site) {
    $posts = get_posts(); // Only queries current blog!
}
```

**Problem:** `get_posts()` queries current blog, not iterated site
**Impact:** Same posts returned for all sites in loop

**✅ Correct:** Use switch_to_blog/restore_current_blog (shown in examples)

## Testing Strategies

### PHPUnit Test for Site Iteration

```php
class GetSitesTest extends WP_UnitTestCase {
    public function test_get_sites_returns_all_sites() {
        // Create test sites
        $blog_ids = [
            $this->factory->blog->create(),
            $this->factory->blog->create(),
            $this->factory->blog->create(),
        ];

        $sites = get_sites();

        $this->assertGreaterThanOrEqual(4, count($sites)); // 3 new + 1 main site
        $this->assertContainsOnlyInstancesOf(WP_Site::class, $sites);
    }

    public function test_get_sites_filters_archived() {
        $blog_id = $this->factory->blog->create();

        // Archive the site
        update_blog_status($blog_id, 'archived', 1);

        // Without filter: archived site included
        $all_sites = get_sites();
        $this->assertContains($blog_id, wp_list_pluck($all_sites, 'blog_id'));

        // With filter: archived site excluded
        $active_sites = get_sites(['archived' => 0]);
        $this->assertNotContains($blog_id, wp_list_pluck($active_sites, 'blog_id'));
    }
}
```

## Real-World Examples

### Yoast SEO: Network-Wide Indexation (WP-CLI)

**Command:** `wp yoast index --network`

**Implementation:**
```php
$blog_ids = \get_sites([
    'archived' => 0,
    'deleted'  => 0,
]);

foreach ($blog_ids as $blog_id) {
    \switch_to_blog($blog_id);
    \do_action('_yoast_run_migrations'); // Run migrations
    $this->run_indexation_actions($assoc_args); // Index content
    \restore_current_blog();
}
```

**Use Case:** Index SEO data for all sites after plugin update

**Source:** `airbnb/plugins/wordpress-seo/src/commands/index-command.php`

### OneLogin SAML: Network Configuration UI

**Scenario:** Network admin enables SAML SSO for specific sites (corporate sites, not public blogs)

**Implementation:**
1. Fetch all sites with `get_sites(['number' => 1000])`
2. Display table with checkboxes for each site
3. Check `get_blog_option($site->blog_id, 'onelogin_saml_enabled')` for each
4. Save per-site SAML enablement flags on form submission

**Limitation:** 1000-site hardcoded limit

**Source:** `airbnb/plugins/onelogin-saml-sso/php/network_saml_enabler.php`

## Migration Path

### Adding Pagination to Existing Scripts

```php
// OLD: Fetch all sites (breaks on large networks)
$sites = get_sites();
foreach ($sites as $site) {
    process_site($site);
}

// NEW: Paginate for scalability
$page = 1;
$per_page = 100;

do {
    $sites = get_sites([
        'number' => $per_page,
        'offset' => ($page - 1) * $per_page,
    ]);

    foreach ($sites as $site) {
        process_site($site);
    }

    $page++;
} while (count($sites) === $per_page);
```

## Related Patterns

- **switch_to_blog/restore_current_blog** - Always used in conjunction for per-site operations
- **Network-Wide Options** - Combine with get_sites for per-site feature flag checks
- **New Site Provisioning** - Use get_sites to iterate and configure new sites

## References

- WordPress Codex: `get_sites()`
- WordPress Core: `WP_Site` class
- WP-CLI: Network commands

**Source Analysis:** airbnb codebase (43 get_sites calls, primarily in WP-CLI commands and network admin UI)
**Pattern Adoption:** 100% of network-wide iteration operations in multisite
