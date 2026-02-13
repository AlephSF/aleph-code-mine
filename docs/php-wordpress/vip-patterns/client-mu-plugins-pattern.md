---
title: "Client MU-Plugins Pattern for WordPress VIP"
category: "wordpress-vip"
subcategory: "architecture"
tags: ["mu-plugins", "must-use", "vip-architecture", "site-critical", "bootstrap"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Client MU-Plugins Overview

WordPress VIP uses `client-mu-plugins/` directory for must-use plugins that load before regular plugins and cannot be deactivated via admin UI. Client MU-plugins handle site-critical functionality, security layers, performance optimizations, and VIP Go platform integrations. The directory structure supports top-level PHP files (auto-loaded) and subdirectories (require manual loading).

**Location:** `/client-mu-plugins/` (repository root)
**Loading order:** After VIP platform MU-plugins, before regular plugins
**Admin deactivation:** Not possible (always active)
**Typical file count:** 100-600+ PHP files for enterprise deployments

```
client-mu-plugins/
  decoupled-bundle-loader.php       ← Load headless WPGraphQL bundle
  disable-yoast-author-indexer.php  ← Performance optimization
  graphql-security.php              ← GraphQL DoS protection
  plugin-loader.php                 ← Conditional plugin loading by blog_id
  vipgo-helper.php                  ← VIP Go SAML SSO modifications
  vip-decoupled-bundle/             ← Bundled WPGraphQL + ACF (subdirectory)
    admin/
    lib/
    vip-decoupled.php
```

## When to Use Client MU-Plugins

Client MU-plugins enforce site-critical functionality that must always run regardless of admin changes. Use for security layers, performance guards, VIP platform integrations, and conditional plugin loading. Regular plugins are appropriate for non-critical features that site admins should control.

**Use client MU-plugins for:**
- Security layers (GraphQL rate limiting, authentication)
- Performance optimizations (query caching, lazy loading)
- VIP Go platform integrations (SAML SSO, proxy IP detection)
- Conditional plugin loading (`wpcom_vip_load_plugin()`)
- Multisite network-wide functionality
- Features that break site if disabled

**Use regular plugins for:**
- Site-specific features (contact forms, galleries)
- Admin-configurable functionality
- Third-party integrations (analytics, CRM)
- Features safe to disable temporarily

```php
// ❌ Don't put contact form in client MU-plugins
// client-mu-plugins/contact-form.php
add_shortcode('contact', 'render_contact_form'); // Site won't break if disabled

// ✅ Do put GraphQL security in client MU-plugins
// client-mu-plugins/graphql-security.php
add_filter('graphql_request_data', 'enforce_query_size_limits'); // Critical DoS protection
```

## Top-Level vs Subdirectory MU-Plugins

WordPress auto-loads PHP files in the root of `client-mu-plugins/` but ignores subdirectories. Use top-level files for single-file plugins and subdirectories for complex functionality with multiple files. Subdirectory plugins require explicit loader files in the root.

### Top-Level MU-Plugins (Auto-Loaded)

```php
// client-mu-plugins/disable-yoast-author-indexer.php
// ✅ Auto-loaded (single file in root)
<?php
add_filter('wpseo_accessible_post_types', function($post_types) {
    unset($post_types['author']); // Disable Yoast author page indexing
    return $post_types;
});
```

### Subdirectory MU-Plugins (Manual Loading)

```php
// client-mu-plugins/decoupled-bundle-loader.php
// ✅ Loader file in root (loads subdirectory plugin)
<?php
if ( file_exists( __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php' ) ) {
    require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}
```

**Directory structure:**
```
client-mu-plugins/
  decoupled-bundle-loader.php       ← Loader (auto-loaded)
  vip-decoupled-bundle/             ← Subdirectory (not auto-loaded)
    vip-decoupled.php               ← Main plugin file
    admin/                          ← Admin UI
    lib/                            ← Libraries
```

## Client MU-Plugins for Security Layers

WordPress VIP deployments use client MU-plugins for non-bypassable security features like GraphQL DoS protection, rate limiting, authentication middleware, and input sanitization. Security MU-plugins run before regular plugins, preventing attack vectors from third-party code.

### GraphQL DoS Protection

```php
// client-mu-plugins/graphql-security.php
<?php
add_filter( 'graphql_request_data', function( $data ) {
    if ( empty( $data['query'] ) ) {
        return $data;
    }

    $query = $data['query'];

    // Hard limit: 10KB max query size
    $max_size = apply_filters( 'airbnb_graphql_max_query_size', 10000 );
    if ( strlen( $query ) > $max_size ) {
        throw new \GraphQL\Error\UserError(
            sprintf( 'Query exceeds maximum size of %d bytes.', $max_size )
        );
    }

    // Dedupe repeated adjacent field names (neutralize field duplication attack)
    $data['query'] = preg_replace( '/\b(\w+)(\s+\1)+\b/', '$1', $query );

    return $data;
}, 1 ); // Priority 1 = run very early

use GraphQL\Validator\Rules\QueryComplexity;

add_filter( 'graphql_validation_rules', function( $rules ) {
    $max_complexity = apply_filters( 'airbnb_graphql_max_complexity', 500 );
    $rules['query_complexity'] = new QueryComplexity( $max_complexity );
    return $rules;
} );
```

**Security metrics:**
- Max query size: 10,000 bytes (10KB)
- Max query complexity: 500
- Field deduplication prevents `posts posts posts` attack pattern

## Client MU-Plugins for Performance Optimizations

WordPress VIP uses client MU-plugins for performance guards that prevent resource-heavy queries, disable unused indexing, and optimize object caching. Performance MU-plugins cannot be bypassed by site admins, ensuring consistent performance across multisite networks.

```php
// client-mu-plugins/disable-yoast-author-indexer.php
<?php
/**
 * Disable Yoast author page indexing (performance optimization).
 * Author pages trigger expensive user metadata queries at scale.
 */
add_filter('wpseo_accessible_post_types', function($post_types) {
    unset($post_types['author']);
    return $post_types;
});
```

**Common performance MU-plugins:**
- Disable expensive post meta queries
- Cache-bust prevention for high-traffic pages
- Lazy-load non-critical resources
- Query complexity limits for GraphQL/REST APIs

## Client MU-Plugins for VIP Go Platform Integrations

WordPress VIP Go requires client MU-plugins for platform-specific integrations like SAML SSO, Varnish cache control, proxy IP verification, and environment-specific feature flags. These MU-plugins interface with VIP-provided infrastructure.

### SAML SSO with Varnish Bypass

```php
// client-mu-plugins/vipgo-helper.php
<?php
/**
 * Send private Cache-Control headers when appropriate.
 * Triggered prior to SAML plugin (priority 0 on init hook).
 */
function vipgo_saml_checker() {
    if ( ( true === isset( $_GET['saml_acs'] ) && false === empty( $_POST['SAMLResponse'] ) )
         || true === isset( $_GET['saml_sls'] ) ) {
        header( 'Cache-Control: private' );
    }
}
add_action( 'init', 'vipgo_saml_checker', 0 ); // Priority 0 = very early

// Prepend cookies with 'wordpress_' to bypass Varnish
if ( false === defined( 'SAML_LOGIN_COOKIE' ) ) {
    define( 'SAML_LOGIN_COOKIE', 'wordpress_saml_login' );
}
if ( false === defined( 'SAML_NAMEID_COOKIE' ) ) {
    define( 'SAML_NAMEID_COOKIE', 'wordpress_saml_nameid' );
}
```

**VIP Caching Rules:**
- Cookies prefixed with `wordpress_` bypass Varnish cache
- `Cache-Control: private` header bypasses Varnish cache

## Bundled Functionality in Client MU-Plugins

WordPress VIP allows bundling third-party libraries or forked plugins in client MU-plugins subdirectories for version control, security patches, or VIP-specific modifications. Bundled plugins avoid WordPress.org update cycles.

```
client-mu-plugins/
  vip-decoupled-bundle/
    lib/
      wp-graphql/           ← Forked WPGraphQL (600+ files)
      vip-block-data-api/   ← VIP Block Data API
    admin/
      settings.php          ← Admin UI for bundle
    vip-decoupled.php       ← Main loader
```

**Common bundled functionality:**
- Forked WPGraphQL with VIP patches
- Custom block registration APIs
- VIP-specific admin UIs
- Security-hardened libraries

**Loader pattern:**
```php
// client-mu-plugins/decoupled-bundle-loader.php
<?php
if ( get_current_blog_id() === 20 ) { // Headless site only
    require_once __DIR__ . '/vip-decoupled-bundle/vip-decoupled.php';
}
```

## Client MU-Plugins Execution Order

WordPress VIP loads client MU-plugins after VIP platform MU-plugins but before regular plugins. Within client-mu-plugins, files load in alphabetical order. Use numeric prefixes or priority hooks to control execution sequence.

**Execution order:**
1. VIP platform MU-plugins (`/wp-content/mu-plugins/` - managed by VIP)
2. **Client MU-plugins** (`/client-mu-plugins/` - custom code)
3. Regular plugins (`/wp-content/plugins/`)
4. Theme (`functions.php`)

**Alphabetical loading:**
```
client-mu-plugins/
  00-critical-security.php  ← Loads first
  graphql-security.php      ← Loads second (alphabetically)
  plugin-loader.php         ← Loads third
  zz-late-init.php          ← Loads last
```

**Hook priorities override alphabetical order:**
```php
// graphql-security.php loads alphabetically first
add_filter('graphql_request_data', 'enforce_size', 10);

// plugin-loader.php loads alphabetically second
add_filter('graphql_request_data', 'log_queries', 1); // Priority 1 runs before 10
```
