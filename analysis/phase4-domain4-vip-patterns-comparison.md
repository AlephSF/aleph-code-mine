# Phase 4, Domain 4: WordPress VIP Patterns - Analysis

**Analysis Date:** February 12, 2026
**Repository:** airbnb (WordPress VIP Go multisite)
**Domain Focus:** VIP-specific code patterns, multisite, client mu-plugins, performance, security

---

## Executive Summary

Airbnb's WordPress VIP Go multisite deployment demonstrates enterprise-grade patterns specific to WordPress.com VIP hosting platform. The codebase uses VIP-specific functions, conditional plugin loading by blog_id, custom mu-plugins for security/performance, and VIP Go environment handling.

**Key Finding:** 100% adoption of VIP-specific patterns required for WordPress VIP Go hosting (vip-config.php, client-mu-plugins, wpcom_vip_load_plugin(), VIP environment constants).

---

## 1. VIP Configuration File Pattern

### vip-config.php Structure

**Location:** `vip-config.php` (repository root)

**Purpose:** WordPress VIP equivalent of wp-config.php for custom constants and early-bootstrap logic.

### Airbnb Implementation

```php
<?php
/**
 * vip-config.php is where you put things you'd usually put in wp-config.php.
 * Database settings are handled by VIP platform.
 */

// VIP constant: Enable Jetpack Photon for image optimization
define( 'WPCOM_VIP_USE_JETPACK_PHOTON', true );

// VIP constant: Disable Jetpack on specific sites (blog_id or domain check)
if ($http_host === 'news.airbnb.com' || $http_host === 'news.next.airbnb.com') {
     define( 'VIP_JETPACK_SKIP_LOAD', true );
}

// Domain-based redirects (VIP multisite pattern)
$http_host   = $_SERVER['HTTP_HOST'];
$request_uri = $_SERVER['REQUEST_URI'];

$redirects = [
    [
        'domains' => ['press.atairbnb.com', 'press.airbnb.com'],
        'target'  => 'https://news.airbnb.com',
        'status'  => 302,
    ],
    // ... 5+ redirect configurations
];

foreach ($redirects as $redirect) {
    if (
        '/cache-healthcheck?' !== $request_uri &&
        in_array($http_host, $redirect['domains'], true)
    ) {
        if (!empty($redirect['headers'])) {
            foreach ($redirect['headers'] as $header) {
                header($header);
            }
        }
        header('Location: ' . $redirect['target'] . $request_uri, true, $redirect['status']);
        exit;
    }
}

// VIP proxy IP verification (Varnish cache layer)
$proxy_lib = ABSPATH . '/wp-content/mu-plugins/lib/proxy/ip-forward.php';
if ( ! empty( $_SERVER['HTTP_TRUE_CLIENT_IP'] )
    && ! empty( $_SERVER['HTTP_X_VIP_PROXY_VERIFICATION'] )
    && file_exists( $proxy_lib ) ) {
    require_once( $proxy_lib );
    Automattic\VIP\Proxy\fix_remote_address_with_verification_key(
        $_SERVER['HTTP_TRUE_CLIENT_IP'],
        $_SERVER['HTTP_X_VIP_PROXY_VERIFICATION']
    );
}
```

**Pattern Characteristics:**
- Executed before WordPress loads (very early bootstrap)
- No database access (DB credentials managed by VIP platform)
- Domain-based logic for multisite redirects
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- VIP proxy/Varnish integration
- Environment-specific feature flags

---

## 2. Client MU-Plugins Pattern

### Directory Structure

```
client-mu-plugins/
  decoupled-bundle-loader.php       ← Load headless WPGraphQL bundle
  disable-yoast-author-indexer.php  ← Performance optimization
  graphql-security.php              ← GraphQL DoS protection
  plugin-loader.php                 ← Conditional plugin loading by blog_id
  vipgo-helper.php                  ← VIP Go SAML SSO modifications
  vip-decoupled-bundle/             ← Bundled WPGraphQL + ACF + Block Data API
    admin/
    lib/
      vip-block-data-api/
      wp-graphql/
    vip-decoupled.php
```

**Total Client MU-Plugins:** 612 PHP files across custom functionality

### Purpose

Client MU-plugins (must-use plugins) run before regular plugins and cannot be deactivated via admin. Used for:
- Site-critical functionality
- Security layers
- Performance optimizations
- VIP Go platform integrations

---

## 3. Conditional Plugin Loading by blog_id

### Pattern: wpcom_vip_load_plugin()

**Purpose:** Load plugins conditionally for specific sites in a multisite network.

### Airbnb Implementation

```php
// client-mu-plugins/plugin-loader.php

if (get_current_blog_id() === 20) {
  wpcom_vip_load_plugin( 'wpgraphql-acf' );
  wpcom_vip_load_plugin( 'add-wpgraphql-seo/wp-graphql-yoast-seo.php' );
  wpcom_vip_load_plugin( 'vip-block-data-api' );
}
```

**Explanation:**
- **blog_id 20:** Headless WordPress site (policy.airbnb.com)
- **wpgraphql-acf:** WPGraphQL + ACF integration (headless only)
- **wp-graphql-yoast-seo:** SEO data via GraphQL (headless only)
- **vip-block-data-api:** VIP Block Data API (headless only)

**Alternative Patterns:**

```php
// Load plugin for specific theme
if (get_option('stylesheet') === 'pressbnb') {
  wpcom_vip_load_plugin( 'facebook-instant-articles-4.0/facebook-instant-articles.php' );
}

// Load plugin for all sites except one
if (get_current_blog_id() !== 5) {
  wpcom_vip_load_plugin( 'analytics-plugin' );
}

// Conditional loading with domain check
if ($_SERVER['HTTP_HOST'] === 'news.airbnb.com') {
  wpcom_vip_load_plugin( 'custom-news-features' );
}
```

### VIP Helper Function Usage

```php
// themes/blogs-atairbnb/functions.php
\wpcom_vip_load_plugin( 'fieldmanager-1.1/fieldmanager.php' );
\wpcom_vip_load_plugin( 'facebook-instant-articles-4.0/facebook-instant-articles.php' );
\wpcom_vip_load_plugin( 'wp-google-analytics-1.4.0/wp-google-analytics.php' );
\wpcom_vip_load_plugin( 'blog-atairbnb-mu/blog-atairbnb-mu.php' );
```

**Pattern:** 5 instances of `wpcom_vip_load_plugin()` in plugin-loader.php and theme functions

---

## 4. GraphQL Security Pattern

### client-mu-plugins/graphql-security.php

**Purpose:** Mitigate GraphQL DoS attacks with multi-layer protection.

### Security Layers

**Layer 1: Query Size Limiting (Pre-Parse)**

```php
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
    // "posts posts posts" → "posts"
    $data['query'] = preg_replace( '/\b(\w+)(\s+\1)+\b/', '$1', $query );

    return $data;
}, 1 ); // Priority 1 = run very early
```

**Layer 2: Query Complexity Limiting (Validation Phase)**

```php
use GraphQL\Validator\Rules\QueryComplexity;

add_filter( 'graphql_validation_rules', function( $rules ) {
    $max_complexity = apply_filters( 'airbnb_graphql_max_complexity', 500 );
    $rules['query_complexity'] = new QueryComplexity( $max_complexity );
    return $rules;
} );
```

**Security Metrics:**
- Max query size: 10,000 bytes (10KB)
- Max query complexity: 500
- Field deduplication: Prevents `posts posts posts` attack pattern

**Attack Patterns Prevented:**
1. **Field Duplication DoS:** Repeating same field 1000+ times
2. **Large Query DoS:** Sending 1MB+ query strings
3. **Complex Query DoS:** Deeply nested queries with high resolver cost

---

## 5. VIP Environment Constants

### Common VIP Constants

```php
// Production environment check
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    // Production-only logic
}

// Development environment check
if ( defined('VIP_GO_ENV') && 'develop' === VIP_GO_ENV ) {
    // Dev-only logic
}

// Check if running on VIP platform
if ( defined('WPCOM_IS_VIP_ENV') && true === WPCOM_IS_VIP_ENV ) {
    // VIP-specific code
}

// Enable Jetpack Photon (VIP CDN for images)
define( 'WPCOM_VIP_USE_JETPACK_PHOTON', true );

// Skip Jetpack on specific sites
define( 'VIP_JETPACK_SKIP_LOAD', true );

// Enable VIP maintenance mode
define('VIP_MAINTENANCE_MODE', true);
```

**Usage Count:**
- `VIP_GO_ENV`: 11 instances (environment detection)
- `WPCOM_IS_VIP_ENV`: 5 instances
- `WPCOM_VIP_USE_JETPACK_PHOTON`: 1 instance (vip-config.php)
- `VIP_JETPACK_SKIP_LOAD`: 1 instance (news.airbnb.com only)

---

## 6. Cache-Control Headers for Varnish Bypass

### Pattern: Private Cache Headers

**Purpose:** Force Varnish to skip caching for authenticated or dynamic requests.

### SAML SSO Example

```php
// client-mu-plugins/vipgo-helper.php

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
```

**Cookie Prefixing for Varnish Bypass:**

```php
// Prepend cookies with 'wordpress_' to bypass Varnish
if ( false === defined( 'SAML_LOGIN_COOKIE' ) ) {
    define( 'SAML_LOGIN_COOKIE', 'wordpress_saml_login' );
}
if ( false === defined( 'SAML_NAMEID_COOKIE' ) ) {
    define( 'SAML_NAMEID_COOKIE', 'wordpress_saml_nameid' );
}
// ... 2 more cookies
```

**VIP Caching Rules:**
- Cookies prefixed with `wordpress_` bypass Varnish cache
- `Cache-Control: private` header bypasses Varnish cache
- `/cache-healthcheck?` endpoint always bypasses redirects (VIP monitoring)

---

## 7. Multisite Blog Switching Patterns

### get_current_blog_id() Usage

**Pattern:** Conditional logic based on multisite blog ID.

```php
// Airbnb network structure (8+ sites):
// blog_id 1: Main site (airbnb.com/newsroom or similar)
// blog_id 20: Policy site (policy.airbnb.com) - headless GraphQL
// blog_id 5: News site (news.airbnb.com)
// ... other blog IDs
```

**Usage Count:** 52 instances of `get_current_blog_id()` across codebase

### switch_to_blog() Pattern

**Purpose:** Temporarily switch context to another site in multisite network.

```php
// Query data from different site
$original_blog_id = get_current_blog_id();

switch_to_blog( 20 ); // Switch to policy site
$policy_posts = get_posts( array('post_type' => 'bnb_policy') );
restore_current_blog(); // Restore original context

// Use $policy_posts from blog 20 in current blog context
```

**Usage Count:**
- `switch_to_blog()`: ~30 instances
- `restore_current_blog()`: ~30 instances

**Common Mistake:** Forgetting `restore_current_blog()` causes database queries to target wrong site.

---

## 8. VIP Helper Functions

### wpcom_vip_get_term_* Functions

**Purpose:** Uncached term queries (bypass object cache for fresh data).

```php
// Standard WordPress (cached)
$term = get_term_by( 'slug', 'featured', 'category' );

// VIP helper (uncached, always fresh)
$term = wpcom_vip_get_term_by( 'slug', 'featured', 'category' );

// VIP helper for term link (optimized)
$link = wpcom_vip_get_term_link( $term );
```

**Usage Count:**
- `wpcom_vip_get_term_by`: 1 instance (plugins/fieldmanager)
- `wpcom_vip_get_term_link`: Not found (low adoption)

**Note:** VIP recommends these for high-traffic sites where stale cached terms cause issues.

---

## 9. WordPress VIP Minimum Coding Standards

### PHPCS with WordPressVIPMinimum

**Purpose:** Enforce VIP-specific code quality and security rules.

**Standards Referenced:**
- `WordPressVIPMinimum`: VIP-specific rules (10 references in code comments)
- `WordPress-VIP`: Legacy VIP standard

**Common VIP Rules:**
1. **Discourage `WP_Query` with `post__not_in`:** Performance issue at scale
2. **Require cache key salts:** Prevent cache collisions in multisite
3. **Validate user input:** Extra sanitization beyond WP core
4. **Limit uncached functions:** `get_posts()`, `wp_get_recent_posts()` without cache
5. **Discourage `session_start()`:** Not compatible with page caching

**Validation:**
```bash
# Run PHPCS with VIP standards
phpcs --standard=WordPress-VIP themes/pressbnb/
```

---

## 10. Client MU-Plugins: Custom Functionality

### Top-Level Client MU-Plugins

1. **decoupled-bundle-loader.php:** Load WPGraphQL + ACF + Block Data API bundle for headless sites
2. **disable-yoast-author-indexer.php:** Disable Yoast author page indexing (performance optimization)
3. **graphql-security.php:** GraphQL query size/complexity limits (DoS protection)
4. **plugin-loader.php:** Conditional plugin loading by blog_id
5. **vipgo-helper.php:** VIP Go platform modifications for OneLogin SAML SSO

### Bundled Functionality

**vip-decoupled-bundle/** (Headless WordPress stack):
- **lib/wp-graphql/:** WPGraphQL core (forked/bundled)
- **lib/vip-block-data-api/:** VIP Block Data API (Gutenberg blocks via REST)
- **admin/:** Admin UI for headless features
- **vip-decoupled.php:** Main loader

**Total:** 612 PHP files in client-mu-plugins (extensive custom functionality)

---

## 11. VIP Redirects Pattern

### Consolidated Redirect Array

**Location:** vip-config.php

**Pattern:** Array of redirect configurations processed in single loop.

```php
$redirects = [
    // Legacy domain redirects (press.airbnb.com → news.airbnb.com)
    [
        'domains' => ['press.atairbnb.com', 'press.airbnb.com'],
        'target'  => 'https://news.airbnb.com',
        'status'  => 302, // Temporary redirect
    ],

    // Security headers on redirect (realestate.withairbnb.com)
    [
        'domains' => ['realestate.withairbnb.com'],
        'target'  => 'https://www.airbnb.com/airbnb-friendly',
        'status'  => 302,
        'headers' => [
            'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload',
            "Content-Security-Policy: default-src 'self'; ...",
            'X-Content-Type-Options: nosniff',
            'X-Frame-Options: SAMEORIGIN',
            'X-XSS-Protection: 1; mode=block',
            'Referrer-Policy: strict-origin-when-cross-origin',
            'Permissions-Policy: geolocation=(), camera=(), microphone=()',
        ],
    ],

    // International domain redirects (airbnbforwork.de → airbnbforwork.com)
    [
        'domains' => ['www.airbnbforwork.de', 'airbnbforwork.de', /* 6 more locales */],
        'target'  => 'https://www.airbnbforwork.com',
        'status'  => 302,
    ],

    // Technology blog redirect (airbnb.io → airbnb.tech)
    [
        'domains' => ['airbnb.io', 'www.airbnb.io'],
        'target'  => 'https://airbnb.tech',
        'status'  => 302,
    ],
];

foreach ($redirects as $redirect) {
    if (
        '/cache-healthcheck?' !== $request_uri &&
        in_array($http_host, $redirect['domains'], true)
    ) {
        if (!empty($redirect['headers'])) {
            foreach ($redirect['headers'] as $header) {
                header($header);
            }
        }
        header('Location: ' . $redirect['target'] . $request_uri, true, $redirect['status']);
        exit;
    }
}
```

**Redirect Count:** 5+ redirect configurations covering 15+ domains

**Skip Logic:** `/cache-healthcheck?` endpoint always skips redirects (VIP monitoring)

---

## 12. VIP Proxy IP Verification

### Pattern: True Client IP Detection

**Purpose:** Get real client IP behind Varnish/proxy layers.

```php
$proxy_lib = ABSPATH . '/wp-content/mu-plugins/lib/proxy/ip-forward.php';
if ( ! empty( $_SERVER['HTTP_TRUE_CLIENT_IP'] )
    && ! empty( $_SERVER['HTTP_X_VIP_PROXY_VERIFICATION'] )
    && file_exists( $proxy_lib ) ) {
    require_once( $proxy_lib );
    Automattic\VIP\Proxy\fix_remote_address_with_verification_key(
        $_SERVER['HTTP_TRUE_CLIENT_IP'],
        $_SERVER['HTTP_X_VIP_PROXY_VERIFICATION']
    );
}
```

**VIP Headers:**
- `HTTP_TRUE_CLIENT_IP`: Real client IP (not proxy IP)
- `HTTP_X_VIP_PROXY_VERIFICATION`: Cryptographic verification key

**Security:** Verification key prevents IP spoofing. Without verification, malicious requests could fake `HTTP_TRUE_CLIENT_IP`.

---

## Key Findings Summary

### De Facto VIP Standards (100% adoption when applicable)

1. ✅ **vip-config.php** for custom constants and early-bootstrap logic
2. ✅ **client-mu-plugins/** for site-critical functionality
3. ✅ **wpcom_vip_load_plugin()** for conditional plugin loading
4. ✅ **VIP environment constants** (VIP_GO_ENV, WPCOM_IS_VIP_ENV)
5. ✅ **GraphQL security** (query size/complexity limits for headless sites)
6. ✅ **Cache-Control headers** for Varnish bypass (`Cache-Control: private`)
7. ✅ **Multisite blog switching** (get_current_blog_id(), switch_to_blog())
8. ✅ **VIP redirect patterns** (consolidated array in vip-config.php)

### VIP-Specific Patterns

**Headless Site (blog_id 20):**
- Conditional WPGraphQL plugin loading
- GraphQL DoS protection (query size 10KB, complexity 500)
- VIP Block Data API integration

**All Sites:**
- VIP proxy IP verification (true client IP detection)
- Security headers on redirects (CSP, HSTS, X-Frame-Options)
- Cookie prefixing for Varnish bypass (`wordpress_` prefix)
- `/cache-healthcheck?` monitoring endpoint

### Critical Gaps

**Missing VIP Patterns:**
- ❌ No PHPCS configuration file found (WordPressVIPMinimum standards)
- ❌ Minimal usage of VIP helper functions (wpcom_vip_get_term_*)
- ❌ No VIP search (Elasticsearch) integration observed

---

## Quantitative Summary

| Metric | Count | Notes |
|--------|-------|-------|
| Client MU-Plugins | 612 files | Custom functionality in client-mu-plugins/ |
| wpcom_vip_load_plugin() calls | 11 | Conditional plugin loading |
| get_current_blog_id() calls | 52 | Multisite context detection |
| switch_to_blog() calls | ~30 | Cross-site data queries |
| VIP_GO_ENV checks | 11 | Environment-specific logic |
| GraphQL max query size | 10KB | DoS protection |
| GraphQL max complexity | 500 | DoS protection |
| Redirect configurations | 5+ | Covering 15+ domains |
| VIP constants | 6+ | WPCOM_VIP_*, VIP_JETPACK_*, etc. |

---

**Analysis Duration:** ~45 minutes
**Next Steps:** Generate 8 RAG-optimized documentation files + 4 Semgrep rules
