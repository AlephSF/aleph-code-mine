---
title: "Multisite Blog Switching Patterns for WordPress VIP"
category: "wordpress-vip"
subcategory: "multisite"
tags: ["multisite", "blog-switching", "switch_to_blog", "get_current_blog_id", "cross-site-queries"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## WordPress Multisite Blog Switching Overview

WordPress multisite networks use `switch_to_blog()` and `restore_current_blog()` functions for cross-site data queries. Blog switching temporarily changes WordPress database context to query posts, users, or options from different sites, then restores original context. The pattern enables network-wide dashboards, cross-site content aggregation, and shared data queries.

**Core functions:**
- `get_current_blog_id()`: Get active site ID
- `switch_to_blog( $blog_id )`: Switch to different site
- `restore_current_blog()`: Restore original site

**Typical usage:** 30-50 blog switch calls per multisite codebase

**Critical rule:** Always call `restore_current_blog()` after `switch_to_blog()` to prevent context corruption.

## get_current_blog_id() for Site Detection

WordPress VIP multisite networks use `get_current_blog_id()` for conditional logic based on site ID. The pattern enables site-specific features, plugin loading, custom post types, and theme configurations.

```php
// Load GraphQL plugins only on headless site
if (get_current_blog_id() === 20) {
    wpcom_vip_load_plugin( 'wpgraphql-acf' );
    wpcom_vip_load_plugin( 'add-wpgraphql-seo/wp-graphql-yoast-seo.php' );
}

// Custom post type for news site only
if (get_current_blog_id() === 5) {
    register_post_type( 'press_release', [...] );
}

// Different analytics for each site
$analytics_id = get_current_blog_id() === 1 ? 'UA-111111' : 'UA-222222';
```

**Common network structure:**
- **blog_id 1:** Main site (network admin)
- **blog_id 20:** Headless site (WPGraphQL API)
- **blog_id 5:** News site (traditional theme)
- **blog_id 10+:** Additional microsites

**Usage count:** 52 instances of `get_current_blog_id()` in typical VIP multisite codebase

## switch_to_blog() Pattern

WordPress multisite uses `switch_to_blog()` to temporarily change database context to a different site. The function switches WordPress globals ($wpdb, $current_blog, etc.) to target blog, enabling cross-site queries.

```php
// Query data from different site
$original_blog_id = get_current_blog_id();

switch_to_blog( 20 ); // Switch to policy site (blog_id 20)
$policy_posts = get_posts( array('post_type' => 'bnb_policy') );
restore_current_blog(); // Restore original context

// Use $policy_posts from blog 20 in current blog context
foreach ( $policy_posts as $post ) {
    echo $post->post_title;
}
```

**Execution flow:**
1. Store current blog ID (optional, for reference)
2. Call `switch_to_blog( $blog_id )`
3. Execute database queries (get_posts, get_option, etc.)
4. Call `restore_current_blog()` to restore original site

**Usage count:** ~30 instances of `switch_to_blog()` in typical VIP multisite codebase

## restore_current_blog() Critical Pattern

WordPress multisite requires `restore_current_blog()` after every `switch_to_blog()` call. Forgetting restoration causes database queries to target wrong site, corrupting content, settings, and user data.

```php
// ✅ Correct pattern: Always restore
switch_to_blog( 20 );
$policy_posts = get_posts( array('post_type' => 'bnb_policy') );
restore_current_blog(); // Required!

// ❌ Common mistake: Forgot to restore
switch_to_blog( 20 );
$policy_posts = get_posts( array('post_type' => 'bnb_policy') );
// All subsequent queries now target blog 20!
$main_posts = get_posts(); // Queries blog 20 instead of main site!
```

**Consequences of missing restore_current_blog():**
- Content from wrong site appears on pages
- Options saved to wrong site database
- User permissions checked against wrong site
- SEO metadata corrupted (wrong site URLs)

**Critical bugs prevented:** Context corruption, data leakage, permission bypasses

## Exception-Safe Blog Switching Pattern

WordPress VIP multisite code uses try-finally blocks for exception-safe blog switching. Pattern ensures `restore_current_blog()` executes even if queries throw exceptions.

```php
// Exception-safe blog switching
switch_to_blog( 20 );
try {
    $policy_posts = get_posts( array('post_type' => 'bnb_policy') );
    $policy_count = count( $policy_posts );

    if ( empty( $policy_posts ) ) {
        throw new Exception( 'No policy posts found' );
    }

    // Process posts...
} finally {
    restore_current_blog(); // Always executes, even if exception thrown
}
```

**Use cases:**
- API integrations (may throw exceptions)
- Custom post type queries (may fail)
- External data fetches (timeout errors)

**Benefits:**
- Guarantees context restoration
- Prevents context corruption bugs
- Enables safe error handling

## Cross-Site Content Aggregation Pattern

WordPress VIP multisite networks aggregate content from multiple sites using `switch_to_blog()` loops. Pattern collects posts, pages, or custom post types from all network sites for unified dashboards or RSS feeds.

```php
// Aggregate recent posts from all network sites
$all_recent_posts = [];

// Get all blog IDs in network
$sites = get_sites( array('fields' => 'ids') );

foreach ( $sites as $blog_id ) {
    switch_to_blog( $blog_id );

    $posts = get_posts( array(
        'post_type'      => 'post',
        'posts_per_page' => 5,
        'orderby'        => 'date',
    ) );

    foreach ( $posts as $post ) {
        $all_recent_posts[] = array(
            'blog_id'   => $blog_id,
            'blog_name' => get_bloginfo('name'),
            'post'      => $post,
        );
    }

    restore_current_blog();
}

// Sort by date across all sites
usort( $all_recent_posts, function( $a, $b ) {
    return strtotime($b['post']->post_date) - strtotime($a['post']->post_date);
} );
```

**Use cases:**
- Network-wide recent posts
- Cross-site search results
- Unified RSS feeds
- Multi-site dashboards

## Cross-Site Option Queries

WordPress multisite uses `switch_to_blog()` to query options from different sites. Pattern enables reading theme settings, plugin configurations, or site metadata from network sites.

```php
// Get theme option from different site
switch_to_blog( 5 ); // News site
$news_site_logo = get_option( 'site_logo_url' );
restore_current_blog();

// Get plugin setting from headless site
switch_to_blog( 20 ); // Headless GraphQL site
$graphql_cache_enabled = get_option( 'wpgraphql_cache_enabled' );
restore_current_blog();

// Compare settings across sites
$sites = get_sites( array('fields' => 'ids') );
$cache_status = [];

foreach ( $sites as $blog_id ) {
    switch_to_blog( $blog_id );
    $cache_status[ $blog_id ] = get_option( 'wpgraphql_cache_enabled', false );
    restore_current_blog();
}
```

**Common cross-site option queries:**
- Theme settings
- Plugin configurations
- Site metadata (site URL, blog name)
- Feature flags

## Cross-Site User Queries

WordPress multisite shares users across network, but user roles and capabilities are site-specific. Blog switching enables querying user roles from different sites.

```php
// Check if user is editor on different site
$user_id = get_current_user_id();

switch_to_blog( 20 ); // Headless site
$is_editor_on_headless = user_can( $user_id, 'edit_posts' );
restore_current_blog();

// Get all sites where user is admin
$sites = get_blogs_of_user( $user_id );

foreach ( $sites as $site ) {
    switch_to_blog( $site->userblog_id );

    if ( user_can( $user_id, 'manage_options' ) ) {
        $admin_sites[] = $site->blogname;
    }

    restore_current_blog();
}
```

**User data patterns:**
- Users are global (shared across network)
- User roles are site-specific (editor on blog 1, subscriber on blog 2)
- User meta can be site-specific or global

## Blog Switching Performance Considerations

WordPress multisite blog switching has performance overhead (globals manipulation, database prefix switching). Minimize switches, cache results, and avoid switching in tight loops.

### Anti-Pattern: Switching in Loops

```php
// ❌ Bad: Switch inside loop (N switches)
$post_ids = [1, 2, 3, 4, 5];
foreach ( $post_ids as $post_id ) {
    switch_to_blog( 20 );
    $post = get_post( $post_id );
    $titles[] = $post->post_title;
    restore_current_blog();
}

// ✅ Good: Switch once, query all (1 switch)
switch_to_blog( 20 );
$posts = get_posts( array('include' => [1, 2, 3, 4, 5]) );
foreach ( $posts as $post ) {
    $titles[] = $post->post_title;
}
restore_current_blog();
```

### Anti-Pattern: Redundant Switches

```php
// ❌ Bad: Switch to same blog multiple times
switch_to_blog( 20 );
$policy_posts = get_posts();
restore_current_blog();

switch_to_blog( 20 ); // Redundant switch
$policy_pages = get_pages();
restore_current_blog();

// ✅ Good: Single switch for multiple queries
switch_to_blog( 20 );
$policy_posts = get_posts();
$policy_pages = get_pages();
restore_current_blog();
```

### Caching Cross-Site Queries

```php
// Cache cross-site query results
$cache_key = 'policy_posts_' . get_current_blog_id();
$policy_posts = wp_cache_get( $cache_key );

if ( false === $policy_posts ) {
    switch_to_blog( 20 );
    $policy_posts = get_posts( array('post_type' => 'bnb_policy') );
    restore_current_blog();

    wp_cache_set( $cache_key, $policy_posts, '', 3600 ); // 1 hour
}
```

## Nested Blog Switching Pattern

WordPress multisite supports nested `switch_to_blog()` calls with corresponding `restore_current_blog()` calls. Pattern uses stack-based restoration for complex cross-site queries.

```php
// Original: blog_id 1

switch_to_blog( 20 );
$policy_posts = get_posts();

    switch_to_blog( 5 ); // Nested switch
    $news_posts = get_posts();
    restore_current_blog(); // Restores to blog_id 20

$more_policy_posts = get_posts(); // Still on blog_id 20
restore_current_blog(); // Restores to blog_id 1
```

**Restoration stack:**
1. Start: blog_id 1
2. `switch_to_blog(20)`: blog_id 20 (stack: [1])
3. `switch_to_blog(5)`: blog_id 5 (stack: [1, 20])
4. `restore_current_blog()`: blog_id 20 (stack: [1])
5. `restore_current_blog()`: blog_id 1 (stack: [])

**Use case:** Comparing data across 3+ sites in single function

## get_blog_details() for Site Metadata

WordPress multisite uses `get_blog_details()` to query site metadata without switching context. Function returns site URL, name, and registration date without performance overhead of `switch_to_blog()`.

```php
// Get site metadata without switching
$site = get_blog_details( 20 );
echo $site->blogname; // "Policy Site"
echo $site->siteurl;  // "https://policy.airbnb.com"
echo $site->path;     // "/"

// ✅ Use get_blog_details() for metadata (fast)
$site = get_blog_details( 20 );
$site_name = $site->blogname;

// ❌ Don't use switch_to_blog() for simple metadata (slow)
switch_to_blog( 20 );
$site_name = get_bloginfo('name');
restore_current_blog();
```

**Available metadata:**
- `blogname`: Site name
- `siteurl`: Site URL
- `path`: Site path
- `registered`: Registration date
- `last_updated`: Last update timestamp

## Blog Switching Anti-Patterns Summary

WordPress VIP multisite developers avoid common blog switching mistakes that cause context corruption, performance degradation, and data integrity issues.

### Missing restore_current_blog()

```php
// ❌ Critical bug: Missing restoration
switch_to_blog( 20 );
$policy_posts = get_posts();
// Forgot restore_current_blog()!
```

### Switching in Tight Loops

```php
// ❌ Performance issue: Excessive switches
foreach ( $sites as $blog_id ) {
    foreach ( $post_ids as $post_id ) {
        switch_to_blog( $blog_id ); // O(N×M) switches!
        $post = get_post( $post_id );
        restore_current_blog();
    }
}
```

### Ignoring Exceptions

```php
// ❌ Context corruption on exception
switch_to_blog( 20 );
$posts = risky_query(); // May throw exception
restore_current_blog(); // Never executes if exception thrown!

// ✅ Use try-finally
switch_to_blog( 20 );
try {
    $posts = risky_query();
} finally {
    restore_current_blog();
}
```
