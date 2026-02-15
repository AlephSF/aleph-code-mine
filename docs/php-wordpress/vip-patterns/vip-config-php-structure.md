---
title: "vip-config.php Structure for WordPress VIP Go"
category: "wordpress-vip"
subcategory: "configuration"
tags: ["vip-config", "bootstrap", "multisite", "wordpress-vip", "early-init"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## vip-config.php Overview

WordPress VIP Go uses `vip-config.php` as the VIP-equivalent of `wp-config.php` for custom constants and early-bootstrap logic. The file executes before WordPress core loads, enabling domain-based redirects, feature flags, security headers, and VIP platform integration. Database credentials are managed by VIP platform, so vip-config.php focuses on application-level configuration.

**Location:** Repository root (`vip-config.php`)
**Execution timing:** Before WordPress loads (very early bootstrap)
**Database access:** None (DB credentials managed by VIP platform)

```php
<?php
/**
 * vip-config.php is where you put things you'd usually put in wp-config.php.
 * Database settings are handled by VIP platform.
 */

// VIP constant: Enable Jetpack Photon for image optimization
define( 'WPCOM_VIP_USE_JETPACK_PHOTON', true );

// VIP constant: Disable Jetpack on specific sites
if ($http_host === 'news.airbnb.com') {
     define( 'VIP_JETPACK_SKIP_LOAD', true );
}
```

## Domain-Based Redirects in vip-config.php

WordPress VIP uses vip-config.php for early domain redirects before WordPress routing. Consolidated arrays support status codes, multiple domains, security headers. `/cache-healthcheck?` bypasses redirects.

```php
$http_host=$_SERVER['HTTP_HOST'];$request_uri=$_SERVER['REQUEST_URI'];
$redirects=[['domains'=>['press.atairbnb.com','press.airbnb.com'],'target'=>'https://news.airbnb.com','status'=>302],['domains'=>['realestate.withairbnb.com'],'target'=>'https://www.airbnb.com/airbnb-friendly','status'=>302,'headers'=>['Strict-Transport-Security: max-age=31536000','X-Frame-Options: SAMEORIGIN']]];
foreach($redirects as $r){if('/cache-healthcheck?'!==$request_uri&&in_array($http_host,$r['domains'],true)){if(!empty($r['headers'])){foreach($r['headers'] as $h){header($h);}}header('Location: '.$r['target'].$request_uri,true,$r['status']);exit;}}
```

**Security headers:** Inject CSP, HSTS, X-Frame-Options before WordPress.

```php
['domains'=>['realestate.withairbnb.com'],'target'=>'https://www.airbnb.com/airbnb-friendly','status'=>302,'headers'=>['Strict-Transport-Security: max-age=31536000; includeSubDomains; preload',"Content-Security-Policy: default-src 'self'",'X-Content-Type-Options: nosniff','X-Frame-Options: SAMEORIGIN','X-XSS-Protection: 1; mode=block','Referrer-Policy: strict-origin-when-cross-origin','Permissions-Policy: geolocation=(), camera=(), microphone=()']]
```

## VIP Proxy IP Verification

WordPress VIP Go uses Varnish caching layers that obscure true client IPs. The platform provides `HTTP_TRUE_CLIENT_IP` and `HTTP_X_VIP_PROXY_VERIFICATION` headers for secure IP detection. The verification key prevents IP spoofing attacks, ensuring geolocation, rate-limiting, and security plugins receive accurate client IPs.

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

**Security:** Without verification key, malicious requests could spoof `HTTP_TRUE_CLIENT_IP` to bypass rate limits or geofencing.

## VIP Feature Flags in vip-config.php

WordPress VIP provides constants for toggling platform features like Jetpack Photon (image CDN), Jetpack modules, and VIP maintenance mode. Feature flags can be domain-specific or blog_id-specific for multisite networks.

```php
// Enable Jetpack Photon globally
define( 'WPCOM_VIP_USE_JETPACK_PHOTON', true );

// Disable Jetpack on specific domains
if ($http_host === 'news.airbnb.com' || $http_host === 'news.next.airbnb.com') {
     define( 'VIP_JETPACK_SKIP_LOAD', true );
}

// Production-only feature flag
if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
    define( 'CUSTOM_ANALYTICS_ENABLED', true );
}

// Enable maintenance mode
define('VIP_MAINTENANCE_MODE', true);
```

**Common VIP Constants:**
- `WPCOM_VIP_USE_JETPACK_PHOTON`: Enable image CDN
- `VIP_JETPACK_SKIP_LOAD`: Skip Jetpack on specific sites
- `VIP_MAINTENANCE_MODE`: Enable maintenance mode

## vip-config.php Execution Order

vip-config.php executes before WordPress core, plugins, themes, and database connections initialize. This timing enables early redirects, security headers, and environment detection without WordPress overhead.

**Execution order:**
1. **vip-config.php** ← Runs first (redirects, constants)
2. VIP platform initialization (database, Varnish)
3. WordPress core (`wp-settings.php`)
4. Must-use plugins (`/wp-content/mu-plugins/`)
5. Regular plugins
6. Theme (`functions.php`)

**Cannot access in vip-config.php:**
- WordPress functions (`get_option()`, `is_admin()`, etc.)
- Database queries
- Plugin/theme functions

**Can access in vip-config.php:**
- `$_SERVER` superglobal
- `ABSPATH` constant
- PHP native functions (`header()`, `define()`, `file_exists()`)

## When to Use vip-config.php vs Client MU-Plugins

vip-config.php handles pre-WordPress logic (redirects, constants), while client MU-plugins handle WordPress-dependent logic (hooks, filters, custom post types). Use vip-config.php for early-stage initialization and client MU-plugins for WordPress-aware functionality.

**Use vip-config.php for:**
- Domain-based redirects
- Feature flag constants
- Security headers
- VIP proxy IP verification
- Environment detection (`VIP_GO_ENV`)

**Use client MU-plugins for:**
- WordPress hooks and filters
- Conditional plugin loading (`wpcom_vip_load_plugin()`)
- Custom post types and taxonomies
- Admin UI modifications
- GraphQL security layers

```php
// ❌ Don't use WordPress functions in vip-config.php
if ( is_admin() ) { // FAILS - is_admin() not available
    define('SOME_CONSTANT', true);
}

// ✅ Use $_SERVER or other PHP natives
if ( $_SERVER['HTTP_HOST'] === 'admin.example.com' ) {
    define('SOME_CONSTANT', true);
}
```
