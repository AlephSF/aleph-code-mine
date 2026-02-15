---
title: "Conditional Plugin Loading in WordPress Multisite"
category: "wpgraphql-architecture"
subcategory: "multisite"
tags: ["multisite", "conditional-loading", "blog-id", "wpgraphql", "performance"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WordPress VIP multisite networks serving 8+ production sites require conditional plugin loading based on `get_current_blog_id()` to prevent unnecessary plugin initialization on non-headless sites. Must-use plugin pattern loads VIP decoupled bundle and WPGraphQL exclusively for site #20 (Policy/Impact) while traditional sites continue serving WordPress frontend without GraphQL overhead. Conditional loading reduces memory footprint by 50-100MB per request on non-headless sites, eliminates GraphQL schema generation overhead, and prevents accidental API exposure on sites lacking proper authentication. Pattern extends to ACF field groups, custom post types, taxonomies, and theme features requiring site-specific configuration.

## Must-Use Plugin Loader Pattern

Must-use plugins execute conditionally by checking blog ID before loading dependencies, preventing plugin initialization on wrong sites.

### Decoupled Bundle Loader
```php
<?php
/**
 * Plugin Name: VIP Decoupled Bundle Loader
 * Description: Conditionally loads decoupled bundle for Policy site
 */

// Only load for site #20 (Policy/Impact site)
if (get_current_blog_id() !== 20) {
  return; // Exit immediately, don't load plugin
}

// Site #20: Load VIP decoupled bundle
require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
```

**How It Works:**
1. Mu-plugin executes on every request (all sites)
2. `get_current_blog_id()` returns current site ID
3. Non-matching sites: Early return, no further execution
4. Site #20: Loads decoupled bundle with WPGraphQL

**Result:**
- Sites 1-19: No GraphQL overhead
- Site #20: Full headless capabilities

**Source:** airbnb/client-mu-plugins/decoupled-bundle-loader.php (12 lines total, 100% confidence)

## Blog ID Determination

WordPress multisite assigns unique integer IDs to each site during creation, retrievable via `get_current_blog_id()`.

### Finding Site Blog IDs
```bash
# WP-CLI: List all sites with blog IDs
wp site list --fields=blog_id,url,domain

# Example output:
# blog_id  url                           domain
# 1        https://newsroom.airbnb.com   newsroom.airbnb.com
# 2        https://tech.airbnb.com       tech.airbnb.com
# 20       https://policy.airbnb.com     policy.airbnb.com
# 35       https://careers.airbnb.com    careers.airbnb.com
```

### Programmatic ID Retrieval
```php
// Get current site's blog ID
$blog_id = get_current_blog_id();

// Get blog ID by URL
$blog_id = get_blog_id_from_url('policy.airbnb.com', '/');

// Get blog details
$blog_details = get_blog_details($blog_id);
echo $blog_details->blogname;  // Site name
echo $blog_details->siteurl;   // Site URL
```

**Important:** Blog IDs persist across environments (staging, production) if databases synced, but differ across independent installations

## Multiple Site Conditional Loading

Complex multisites load plugins for multiple specific sites using array membership checks.

```php
<?php
/**
 * Plugin Name: GraphQL Sites Loader
 * Description: Load GraphQL for headless sites only
 */

// Define headless site IDs
$headless_sites = [20, 35, 42];  // Policy, Careers, Custom site

// Check if current site is headless
if (!in_array(get_current_blog_id(), $headless_sites, true)) {
  return; // Traditional WordPress sites skip GraphQL
}

// Load GraphQL infrastructure
require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
require_once __DIR__ . '/graphql-security.php';
```

**Benefits:**
- Centralized headless site configuration
- Easy addition of new headless sites
- Clear documentation of which sites use GraphQL

## Conditional Custom Post Type Registration

Custom post types register selectively preventing taxonomy bloat on sites not using the content type.

```php
add_action('init',function(){
 $b=get_current_blog_id();
 if($b===20){
  register_post_type('plc_local_pages',['label'=>'Local Pages','public'=>true,'show_in_rest'=>true,'show_in_graphql'=>true,'graphql_single_name'=>'localPage','graphql_plural_name'=>'localPages']);
  register_post_type('plc_airlab_posts',['label'=>'AirLab Posts','public'=>true,'show_in_rest'=>true,'show_in_graphql'=>true,'graphql_single_name'=>'airLabPost','graphql_plural_name'=>'airLabPosts']);
 }
 if($b===35)register_post_type('job_posting',['label'=>'Job Postings','public'=>true,'show_in_rest'=>true,'show_in_graphql'=>true,'graphql_single_name'=>'jobPosting','graphql_plural_name'=>'jobPostings']);
});
```

**Performance Impact:** Prevents 10-50 unused post types in admin menus, reduces taxonomy queries, simplifies GraphQL schema

## Conditional ACF Field Group Loading

ACF field groups load per site preventing irrelevant fields from cluttering post editors on other sites.

```php
// Mu-plugin: Conditional ACF JSON paths
add_filter('acf/settings/load_json', function($paths) {
  $blog_id = get_current_blog_id();

  // Site-specific ACF JSON directories
  switch ($blog_id) {
    case 20: // Policy site
      $paths[] = WPMU_PLUGIN_DIR . '/acf-json-policy';
      break;

    case 35: // Careers site
      $paths[] = WPMU_PLUGIN_DIR . '/acf-json-careers';
      break;

    case 2: // Tech blog
      $paths[] = WPMU_PLUGIN_DIR . '/acf-json-tech';
      break;
  }

  return $paths;
});
```

**Directory Structure:**
```
mu-plugins/
├── acf-json-policy/
│   ├── group_stat_block.json
│   ├── group_municipality_search.json
│   └── [20 more field groups]
├── acf-json-careers/
│   ├── group_job_posting.json
│   └── group_benefits.json
└── acf-json-tech/
    ├── group_code_sample.json
    └── group_author_bio.json
```

**Benefits:**
- Post editors see only relevant fields
- Faster ACF initialization (fewer field groups)
- Prevents accidental field misuse across sites
- Cleaner GraphQL schema

## Conditional Plugin Filter Modification

Filters modify plugin behavior differently per site without forking plugin code.

```php
// Modify GraphQL security limits per site
add_filter('airbnb_graphql_max_query_size', function($default) {
  $blog_id = get_current_blog_id();

  switch ($blog_id) {
    case 20: // Policy site: Higher limits (complex queries)
      return 50000; // 50KB

    case 35: // Careers site: Standard limits
      return 10000; // 10KB

    default:
      return $default;
  }
});

add_filter('airbnb_graphql_max_complexity', function($default) {
  $blog_id = get_current_blog_id();

  switch ($blog_id) {
    case 20: // Policy site: Complex queries allowed
      return 1000;

    case 35: // Careers site: Standard complexity
      return 500;

    default:
      return $default;
  }
});
```

**Use Cases:**
- Site-specific rate limits
- Per-site feature flags
- Environment-based configuration
- API quota management

## Conditional Theme Loading

Multisite networks assign different themes per site, but conditional logic enables theme-independent feature toggling.

```php
// In plugin or mu-plugin
add_action('after_setup_theme', function() {
  $blog_id = get_current_blog_id();

  // Headless sites: Disable theme features
  if (in_array($blog_id, [20, 35, 42], true)) {
    // Remove sidebar support
    remove_theme_support('widgets');

    // Remove theme customizer panels
    add_action('customize_register', function($wp_customize) {
      $wp_customize->remove_section('colors');
      $wp_customize->remove_section('header_image');
    });

    // Disable WordPress frontend CSS
    add_action('wp_enqueue_scripts', function() {
      wp_dequeue_style('wp-block-library');
      wp_dequeue_style('wp-block-library-theme');
      wp_dequeue_style('global-styles');
    }, 100);
  }

  // Traditional sites: Full theme features
  else {
    add_theme_support('widgets');
    add_theme_support('custom-header');
    add_theme_support('custom-background');
  }
});
```

**Rationale:** Headless sites don't need sidebar widgets, customizer options, or WordPress frontend CSS

## Performance Monitoring Per Site

Conditional plugin loading requires monitoring to verify performance improvements materialize.

### Memory Usage Tracking
```php
// Mu-plugin: Log memory per site
add_action('shutdown', function() {
  $blog_id = get_current_blog_id();
  $memory = memory_get_peak_usage(true) / 1024 / 1024; // MB

  error_log(sprintf(
    'Site %d memory: %.2f MB',
    $blog_id,
    $memory
  ));
});
```

**Expected Results:**
- Site 20 (GraphQL): 180-220 MB
- Sites 1-19 (no GraphQL): 80-120 MB
- Memory savings: 50-100 MB per request

### Query Performance Logging
```php
add_action('shutdown', function() {
  global $wpdb;

  error_log(sprintf(
    'Site %d queries: %d (%s seconds)',
    get_current_blog_id(),
    $wpdb->num_queries,
    timer_stop()
  ));
});
```

**Monitoring Stack:**
- New Relic APM: Per-site memory graphs
- WordPress VIP Dashboard: Query count per site
- CloudWatch Logs: Memory usage alerts
- Custom Datadog metrics: Blog ID tags

## Conditional REST API Routes

Custom REST API routes register conditionally preventing endpoint exposure on sites not using them.

```php
add_action('rest_api_init', function() {
  $blog_id = get_current_blog_id();

  // Policy site: Municipality search API
  if ($blog_id === 20) {
    register_rest_route('policy/v1', '/municipalities', [
      'methods' => 'GET',
      'callback' => 'get_municipalities',
      'permission_callback' => '__return_true',
    ]);
  }

  // Careers site: Job application webhook
  if ($blog_id === 35) {
    register_rest_route('careers/v1', '/applications', [
      'methods' => 'POST',
      'callback' => 'process_job_application',
      'permission_callback' => 'verify_greenhouse_webhook',
    ]);
  }
});
```

**Security Benefit:** API endpoints don't exist on sites not using them, preventing unauthorized access attempts

## Environment-Based Conditional Loading

Development and staging environments require different plugin configurations than production.

```php
// Mu-plugin: Environment-aware loading
$is_production = (defined('WP_ENV') && WP_ENV === 'production');
$blog_id = get_current_blog_id();

// Load GraphQL only on Policy site in production
if ($is_production && $blog_id === 20) {
  require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}

// Development: Load GraphQL on all sites for testing
elseif (!$is_production) {
  require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}
```

**Rationale:**
- Production: Strict conditional loading (performance)
- Staging: Liberal loading (testing headless on any site)
- Development: Load everywhere (feature development)

## Blog ID Migration and Deployment

Blog IDs differ across environments requiring deployment strategies handling ID changes.

### Configuration Constant Approach
```php
// wp-config.php or environment-specific config
define('HEADLESS_SITE_IDS', [
  'production' => [20, 35, 42],
  'staging' => [15, 28, 31],
  'development' => [3, 4, 5],
]);

// Mu-plugin: Use environment-specific IDs
$env = defined('WP_ENV') ? WP_ENV : 'production';
$headless_ids = HEADLESS_SITE_IDS[$env];

if (in_array(get_current_blog_id(), $headless_ids, true)) {
  require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}
```

### Domain-Based Approach (Environment-Agnostic)
```php
// Mu-plugin: Load by domain instead of blog ID
$current_domain = parse_url(home_url(), PHP_URL_HOST);
$headless_domains = ['policy.airbnb.com', 'careers.airbnb.com'];

if (in_array($current_domain, $headless_domains, true)) {
  require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}
```

**Trade-offs:**
- Blog ID: Fast, requires per-environment config
- Domain: Portable, requires domain lookup

## Testing Conditional Loading

### Verify Plugin Loaded
```php
// Test helper function
function is_graphql_loaded() {
  return class_exists('WPGraphQL');
}

// Test on site 20
switch_to_blog(20);
assert(is_graphql_loaded() === true);
restore_current_blog();

// Test on site 1
switch_to_blog(1);
assert(is_graphql_loaded() === false);
restore_current_blog();
```

### WP-CLI Testing
```bash
# Test GraphQL availability per site
for site_id in 1 2 20 35; do
  wp eval "
    switch_to_blog($site_id);
    echo 'Site $site_id GraphQL: ' . (class_exists('WPGraphQL') ? 'YES' : 'NO') . PHP_EOL;
    restore_current_blog();
  "
done

# Expected output:
# Site 1 GraphQL: NO
# Site 2 GraphQL: NO
# Site 20 GraphQL: YES
# Site 35 GraphQL: YES
```

### Memory Usage Comparison
```bash
# Memory with GraphQL (site 20)
wp eval "switch_to_blog(20); echo memory_get_usage(true) / 1024 / 1024 . ' MB';"

# Memory without GraphQL (site 1)
wp eval "switch_to_blog(1); echo memory_get_usage(true) / 1024 / 1024 . ' MB';"
```

## Error: Missing Early Return

WordPress mu-plugins load on all sites without early return preventing further execution.

```php
// ❌ Wrong: Condition checks but doesn't prevent execution
if(get_current_blog_id()!==20){}
require_once __DIR__.'/plugin.php'; // Still loads

// ✅ Correct: Early return exits mu-plugin immediately
if(get_current_blog_id()!==20)return;
require_once __DIR__.'/plugin.php';
```

## Error: Blog ID Type Mismatch

WordPress `get_current_blog_id()` returns integer requiring integer comparison not string.

```php
// ❌ Wrong: String comparison always false
if(get_current_blog_id()!=='20')

// ✅ Correct: Integer comparison
if(get_current_blog_id()!==20)

// ✅ Also correct: Strict array check
if(!in_array(get_current_blog_id(),[20,35],true))
```

## Error: Hook Timing Too Early

WordPress mu-plugins execute before `muplugins_loaded` hook when blog ID already determined.

```php
// ❌ Wrong: muplugins_loaded too early (blog ID returns 0 or 1)
add_action('muplugins_loaded',function(){
 if(get_current_blog_id()===20)require_once __DIR__.'/plugin.php';
});

// ✅ Correct: Direct execution (no hook needed, blog ID already set)
if(get_current_blog_id()===20)require_once __DIR__.'/plugin.php';
```

## Error: Admin UI Not Loaded

WordPress multisite plugins with admin UI require loading on target sites OR network admin.

```php
// ❌ Wrong: Plugin admin UI not accessible from network admin
if(get_current_blog_id()===20)require_once __DIR__.'/plugin-with-admin.php';

// ✅ Correct: Load on target sites OR network admin
if(get_current_blog_id()===20||is_network_admin())require_once __DIR__.'/plugin-with-admin.php';
```
