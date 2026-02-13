---
title: "VIP Environment Constants for WordPress VIP Go"
category: "wordpress-vip"
subcategory: "configuration"
tags: ["environment", "constants", "vip-go-env", "feature-flags", "deployment"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## VIP Environment Constants Overview

WordPress VIP Go provides platform-specific constants for environment detection, feature flags, and VIP-specific configurations. Constants enable conditional logic for development/production environments, VIP platform integrations, and Jetpack feature control.

**Common VIP constants:**
- `VIP_GO_ENV`: Environment identifier (production, develop, preprod)
- `WPCOM_IS_VIP_ENV`: Boolean flag for VIP platform detection
- `WPCOM_VIP_USE_JETPACK_PHOTON`: Enable Jetpack Photon CDN
- `VIP_JETPACK_SKIP_LOAD`: Skip Jetpack loading
- `VIP_MAINTENANCE_MODE`: Enable maintenance mode

**Typical usage count:** 10-20 environment checks per codebase

## VIP_GO_ENV Environment Detection

WordPress VIP Go sets `VIP_GO_ENV` constant to identify deployment environment. The constant enables environment-specific feature flags, debug tools, caching strategies, and third-party service configurations.

```php
// Production environment check
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    // Production-only logic
    define( 'ENABLE_ANALYTICS', true );
    define( 'WP_DEBUG', false );
}

// Development environment check
if ( defined('VIP_GO_ENV') && 'develop' === VIP_GO_ENV ) {
    // Dev-only logic
    define( 'WP_DEBUG', true );
    define( 'SAVEQUERIES', true );
}

// Pre-production environment check
if ( defined('VIP_GO_ENV') && 'preprod' === VIP_GO_ENV ) {
    // Staging logic
    define( 'WP_CACHE', true );
    define( 'WP_DEBUG', false );
}
```

**VIP_GO_ENV values:**
- `'production'`: Live production site
- `'develop'`: Development environment
- `'preprod'`: Pre-production/staging (optional)

**Typical usage:** 11 environment checks per VIP codebase

## WPCOM_IS_VIP_ENV Platform Detection

WordPress VIP Go sets `WPCOM_IS_VIP_ENV` to `true` for code running on VIP infrastructure. The constant enables VIP-specific code paths, fallback logic for non-VIP environments, and portable codebase patterns.

```php
// Check if running on VIP platform
if ( defined('WPCOM_IS_VIP_ENV') && true === WPCOM_IS_VIP_ENV ) {
    // VIP-specific code
    wpcom_vip_load_plugin( 'vip-only-plugin' );
} else {
    // Non-VIP fallback
    require_once WP_PLUGIN_DIR . '/vip-only-plugin/plugin.php';
}

// Conditional feature flag
if ( defined('WPCOM_IS_VIP_ENV') && WPCOM_IS_VIP_ENV ) {
    // Use VIP object cache
    define( 'WP_CACHE', true );
} else {
    // Use file-based cache for local development
    define( 'WP_CACHE', false );
}
```

**Use cases:**
- Portable codebases (VIP and non-VIP environments)
- Conditional VIP helper function usage
- VIP-specific integrations (Varnish, Photon)

**Typical usage:** 5 platform checks per VIP codebase

## WPCOM_VIP_USE_JETPACK_PHOTON Image CDN

WordPress VIP provides `WPCOM_VIP_USE_JETPACK_PHOTON` constant to enable Jetpack Photon image CDN. Photon serves optimized images from WordPress.com CDN, reducing origin server load and improving performance.

```php
// vip-config.php
define( 'WPCOM_VIP_USE_JETPACK_PHOTON', true );
```

**Jetpack Photon features:**
- Automatic image optimization (WebP, compression)
- Responsive image resizing
- CDN delivery (WordPress.com infrastructure)
- Zero-configuration setup

**Image URL transformation:**
```
// Original image URL
https://example.com/wp-content/uploads/2024/image.jpg

// Photon CDN URL
https://i0.wp.com/example.com/wp-content/uploads/2024/image.jpg?w=800&quality=85
```

**Performance impact:** 40-60% reduction in image bandwidth for typical sites

## VIP_JETPACK_SKIP_LOAD Conditional Jetpack Loading

WordPress VIP allows skipping Jetpack loading on specific sites or domains using `VIP_JETPACK_SKIP_LOAD` constant. The pattern disables Jetpack for headless sites, API-only sites, or domains with Jetpack conflicts.

```php
// vip-config.php
// Disable Jetpack on specific domains
if ($http_host === 'news.airbnb.com' || $http_host === 'news.next.airbnb.com') {
     define( 'VIP_JETPACK_SKIP_LOAD', true );
}

// Disable Jetpack on headless GraphQL sites
if (get_current_blog_id() === 20) { // Headless site
     define( 'VIP_JETPACK_SKIP_LOAD', true );
}
```

**Use cases for skipping Jetpack:**
- Headless WordPress (no frontend rendering)
- API-only endpoints (GraphQL, REST)
- Sites with Jetpack module conflicts
- Performance optimization (reduce plugin overhead)

**Performance impact:** ~100-200ms reduction in page load time without Jetpack

## VIP_MAINTENANCE_MODE for Deployments

WordPress VIP provides `VIP_MAINTENANCE_MODE` constant for displaying maintenance pages during deployments, database migrations, or emergency downtime. The constant short-circuits WordPress routing.

```php
// vip-config.php
// Enable maintenance mode
define('VIP_MAINTENANCE_MODE', true);
```

**Maintenance mode behavior:**
- Returns HTTP 503 (Service Unavailable)
- Displays VIP-branded maintenance page
- Bypasses WordPress routing
- Allows administrator access (via IP allowlist)

**Common use cases:**
- Planned database migrations
- Major plugin updates
- Emergency security patches

**Deployment pattern:**
```php
// 1. Enable maintenance mode
define('VIP_MAINTENANCE_MODE', true);

// 2. Deploy code changes

// 3. Disable maintenance mode
// define('VIP_MAINTENANCE_MODE', false);
```

## Environment-Specific Debug Flags

WordPress VIP uses `VIP_GO_ENV` for environment-specific debug flags. Development environments enable query logging, error display, and debug tools, while production disables debugging for performance and security.

```php
// Development environment: Enable debugging
if ( defined('VIP_GO_ENV') && 'develop' === VIP_GO_ENV ) {
    define( 'WP_DEBUG', true );
    define( 'WP_DEBUG_DISPLAY', true );
    define( 'WP_DEBUG_LOG', true );
    define( 'SAVEQUERIES', true );
    define( 'SCRIPT_DEBUG', true );
}

// Production environment: Disable debugging
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    define( 'WP_DEBUG', false );
    define( 'WP_DEBUG_DISPLAY', false );
    define( 'WP_DEBUG_LOG', false );
}
```

**Debug flags:**
- `WP_DEBUG`: Enable WordPress debug mode
- `WP_DEBUG_DISPLAY`: Display errors on screen
- `WP_DEBUG_LOG`: Log errors to debug.log
- `SAVEQUERIES`: Save database queries for analysis
- `SCRIPT_DEBUG`: Use unminified JS/CSS

## Environment-Specific Plugin Loading

WordPress VIP combines `VIP_GO_ENV` with `wpcom_vip_load_plugin()` for environment-specific plugin activation. Development environments load debug tools, production loads performance monitoring.

```php
// client-mu-plugins/plugin-loader.php

// Development-only plugins
if ( defined('VIP_GO_ENV') && 'develop' === VIP_GO_ENV ) {
    wpcom_vip_load_plugin( 'query-monitor' );
    wpcom_vip_load_plugin( 'debug-bar' );
    wpcom_vip_load_plugin( 'debug-bar-console' );
}

// Production-only plugins
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    wpcom_vip_load_plugin( 'vip-performance-monitor' );
}

// All non-production environments
if ( ! defined('VIP_GO_ENV') || 'production' !== VIP_GO_ENV ) {
    wpcom_vip_load_plugin( 'developer-tools' );
}
```

**Common environment-specific plugins:**
- **Development:** Query Monitor, Debug Bar, WP-CLI Logger
- **Staging:** Performance profilers, load testers
- **Production:** Error tracking, APM tools

## Environment-Specific Third-Party Services

WordPress VIP uses `VIP_GO_ENV` for environment-specific API keys, service endpoints, and third-party integrations. Pattern prevents test data pollution in production services.

```php
// Environment-specific analytics
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    define( 'GOOGLE_ANALYTICS_ID', 'UA-12345678-1' ); // Production GA
} else {
    define( 'GOOGLE_ANALYTICS_ID', 'UA-12345678-2' ); // Staging GA
}

// Environment-specific API endpoints
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    define( 'API_ENDPOINT', 'https://api.example.com' );
} else {
    define( 'API_ENDPOINT', 'https://api-staging.example.com' );
}

// Environment-specific Stripe keys
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    define( 'STRIPE_SECRET_KEY', getenv('STRIPE_LIVE_SECRET') );
} else {
    define( 'STRIPE_SECRET_KEY', getenv('STRIPE_TEST_SECRET') );
}
```

## VIP Constant Definition Best Practices

WordPress VIP recommends defining constants in vip-config.php (pre-WordPress) or client MU-plugins (post-WordPress). Check for existing definitions before defining constants to prevent redefinition errors.

### Safe Constant Definition

```php
// ✅ Check before defining
if ( ! defined( 'CUSTOM_CONSTANT' ) ) {
    define( 'CUSTOM_CONSTANT', 'value' );
}

// ❌ Redefinition error
define( 'CUSTOM_CONSTANT', 'value' );
define( 'CUSTOM_CONSTANT', 'new_value' ); // Fatal error
```

### Conditional Constant Definition

```php
// ✅ Conditional definition with check
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    if ( ! defined( 'ENABLE_CACHE' ) ) {
        define( 'ENABLE_CACHE', true );
    }
}
```

### Boolean vs String Constants

```php
// ✅ Use boolean for feature flags
define( 'WPCOM_IS_VIP_ENV', true );
if ( WPCOM_IS_VIP_ENV ) { /* ... */ }

// ✅ Use string for environment names
define( 'VIP_GO_ENV', 'production' );
if ( 'production' === VIP_GO_ENV ) { /* ... */ }

// ❌ Don't use string for boolean flags
define( 'WPCOM_IS_VIP_ENV', 'true' ); // String, not boolean
if ( WPCOM_IS_VIP_ENV ) { /* Always truthy */ }
```

## Environment Detection Fallback Pattern

WordPress VIP codebases implement fallback logic for undefined environment constants. Pattern ensures compatibility with non-VIP environments and local development setups.

```php
// Safe environment check with fallback
$is_production = ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV );
$is_develop = ( defined('VIP_GO_ENV') && 'develop' === VIP_GO_ENV );

if ( $is_production ) {
    // Production logic
} elseif ( $is_develop ) {
    // Development logic
} else {
    // Local development fallback (VIP_GO_ENV not set)
    define( 'WP_DEBUG', true );
}

// Safe VIP platform check with fallback
$is_vip = ( defined('WPCOM_IS_VIP_ENV') && WPCOM_IS_VIP_ENV );

if ( $is_vip ) {
    // VIP-specific code
} else {
    // Non-VIP fallback
}
```

**Use cases:**
- Local development without VIP constants
- Portable codebases (VIP and non-VIP hosting)
- Gradual VIP migration
