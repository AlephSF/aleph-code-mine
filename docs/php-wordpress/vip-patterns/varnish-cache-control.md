---
title: "Varnish Cache Control for WordPress VIP"
category: "wordpress-vip"
subcategory: "performance"
tags: ["varnish", "cache-control", "caching", "cookies", "saml", "authentication"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Varnish Caching in WordPress VIP

WordPress VIP uses Varnish caching layer to serve cached HTML responses for anonymous users. Varnish dramatically improves performance by bypassing PHP/WordPress execution for repeat requests. Authenticated requests, personalized content, and dynamic forms must bypass Varnish using Cache-Control headers or cookie prefixes.

**Varnish architecture:**
```
User → Varnish Cache → WordPress/PHP (cache miss only)
       ↓
       Cached HTML (cache hit)
```

**Cache bypass mechanisms:**
1. `Cache-Control: private` header
2. Cookies prefixed with `wordpress_`
3. `/cache-healthcheck?` monitoring endpoint
4. Authenticated user sessions

**Performance impact:** 90-95% of anonymous traffic served from Varnish (sub-10ms response times)

## Cache-Control: private for Dynamic Requests

WordPress VIP uses `Cache-Control: private` header to force Varnish cache bypass for authenticated requests, SAML SSO flows, personalized content, and API mutations. Private caching instructs Varnish to skip cache and forward request to WordPress.

```php
// Force Varnish bypass for SAML authentication
function vipgo_saml_checker() {
    if ( ( true === isset( $_GET['saml_acs'] ) && false === empty( $_POST['SAMLResponse'] ) )
         || true === isset( $_GET['saml_sls'] ) ) {
        header( 'Cache-Control: private' );
    }
}
add_action( 'init', 'vipgo_saml_checker', 0 ); // Priority 0 = very early
```

**When to use `Cache-Control: private`:**
- SAML/OAuth authentication flows
- Personalized content (user dashboards)
- Form submissions (POST requests)
- API mutations (create, update, delete)
- Shopping carts and checkout flows

**Header syntax:**
```php
header( 'Cache-Control: private' );
header( 'Cache-Control: private, max-age=0' );
header( 'Cache-Control: private, no-store' );
```

## Cookie Prefixing for Varnish Bypass

WordPress VIP Varnish configuration bypasses cache for requests with cookies prefixed `wordpress_`, `wp-`, or `comment_author_`. Cookie prefixing enables user-specific caching without Cache-Control headers.

```php
// Prepend cookies with 'wordpress_' to bypass Varnish
if ( false === defined( 'SAML_LOGIN_COOKIE' ) ) {
    define( 'SAML_LOGIN_COOKIE', 'wordpress_saml_login' );
}
if ( false === defined( 'SAML_NAMEID_COOKIE' ) ) {
    define( 'SAML_NAMEID_COOKIE', 'wordpress_saml_nameid' );
}
if ( false === defined( 'SAML_SESSIONINDEX_COOKIE' ) ) {
    define( 'SAML_SESSIONINDEX_COOKIE', 'wordpress_saml_sessionindex' );
}
```

**VIP cookie prefixes (auto-bypass Varnish):**
- `wordpress_*`: Custom WordPress cookies
- `wp-*`: WordPress core cookies (wp-settings, wp-postpass)
- `comment_author_*`: Comment author cookies
- `wordpress_logged_in_*`: Logged-in user cookie
- `wordpress_test_cookie`: WordPress test cookie

**Example cookie bypass:**
```php
// Set custom cookie that bypasses Varnish
setcookie( 'wordpress_user_preference', 'dark_mode', time() + 3600, '/' );

// Set regular cookie (does NOT bypass Varnish)
setcookie( 'user_preference', 'dark_mode', time() + 3600, '/' ); // Cached!
```

## SAML SSO Varnish Bypass Pattern

WordPress VIP SAML SSO implementations use early-hook Cache-Control headers to bypass Varnish during authentication flows. Pattern detects SAML GET/POST parameters and sends private caching headers before WordPress routing initializes.

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

**SAML parameters:**
- `saml_acs`: Assertion Consumer Service (login callback)
- `SAMLResponse`: SAML authentication response (POST data)
- `saml_sls`: Single Logout Service (logout callback)

**Cookie prefixing for SAML sessions:**
```php
define( 'SAML_LOGIN_COOKIE', 'wordpress_saml_login' );
define( 'SAML_NAMEID_COOKIE', 'wordpress_saml_nameid' );
```

**Execution timing:** Priority 0 on `init` hook ensures headers sent before SAML plugin processes request.

## Cache Healthcheck Endpoint Bypass

WordPress VIP monitoring uses `/cache-healthcheck?` endpoint to verify Varnish and WordPress health. The endpoint always bypasses redirects in vip-config.php and returns WordPress healthcheck response.

```php
// vip-config.php
$request_uri = $_SERVER['REQUEST_URI'];

// Skip redirects for healthcheck endpoint
if ( '/cache-healthcheck?' !== $request_uri ) {
    // Domain redirect logic
    foreach ($redirects as $redirect) {
        if ( in_array($http_host, $redirect['domains'], true) ) {
            header('Location: ' . $redirect['target'] . $request_uri, true, $redirect['status']);
            exit;
        }
    }
}
```

**Healthcheck behavior:**
- Always bypasses Varnish cache
- Always bypasses vip-config.php redirects
- Returns HTTP 200 if WordPress is healthy
- Used by VIP monitoring infrastructure

**Endpoint pattern:** `/cache-healthcheck?` (note trailing `?`)

## Vary Header for User-Specific Caching

WordPress VIP uses `Vary` header to cache different versions of pages for logged-in vs anonymous users. Varnish creates separate cache entries based on Vary header values.

```php
// Cache different versions for logged-in users
if ( is_user_logged_in() ) {
    header( 'Vary: Cookie' );
}
```

**Vary header patterns:**
```php
// Cache different versions by cookie
header( 'Vary: Cookie' );

// Cache different versions by Accept-Encoding (gzip)
header( 'Vary: Accept-Encoding' );

// Multiple vary conditions
header( 'Vary: Cookie, Accept-Encoding' );
```

**Varnish behavior:**
- Creates separate cache entries per Vary value
- `Vary: Cookie` creates cache per unique cookie combination
- Too many Vary values reduce cache hit rate

**Best practice:** Use `Vary: Cookie` sparingly (reduces cache efficiency)

## Cache Purging Strategies

WordPress VIP provides VIP helper functions for cache purging after content updates. Purging invalidates Varnish cache entries, forcing fresh WordPress responses.

```php
// Purge cache for specific URL
wpcom_vip_purge_edge_cache_for_url( 'https://example.com/post-slug/' );

// Purge cache for post ID
wpcom_vip_purge_edge_cache_for_post( $post_id );

// Purge entire site cache (use sparingly)
wpcom_vip_purge_edge_cache_for_site();
```

**Auto-purge triggers:**
- Post/page publish or update
- Comment approval
- Menu changes
- Widget updates

**Manual purge use cases:**
- Custom post type updates
- External API data changes
- Taxonomy term modifications

## Varnish Cache TTL Configuration

WordPress VIP Varnish uses default cache TTL (time-to-live) based on content type. Customize TTL using Cache-Control max-age directives for specific pages or content types.

```php
// Set custom cache TTL (1 hour)
header( 'Cache-Control: public, max-age=3600' );

// Short TTL for frequently updated content (5 minutes)
if ( is_front_page() ) {
    header( 'Cache-Control: public, max-age=300' );
}

// Long TTL for static content (24 hours)
if ( is_singular() && ! is_user_logged_in() ) {
    header( 'Cache-Control: public, max-age=86400' );
}
```

**VIP default TTLs:**
- **Homepage:** 5 minutes (300 seconds)
- **Posts/Pages:** 1 hour (3600 seconds)
- **Archives:** 15 minutes (900 seconds)
- **404 pages:** 5 minutes (300 seconds)

**max-age recommendations:**
- **News sites:** 1-5 minutes (frequent updates)
- **Blogs:** 1 hour (occasional updates)
- **Documentation:** 24 hours (rare updates)

## Authenticated User Bypass Pattern

WordPress VIP automatically bypasses Varnish for logged-in users via `wordpress_logged_in_*` cookie. Pattern ensures personalized content (admin bar, user dashboards) never serves from cache.

```php
// WordPress core sets logged-in cookie
wp_set_auth_cookie( $user_id );

// Cookie name pattern: wordpress_logged_in_{COOKIEHASH}
// Example: wordpress_logged_in_a1b2c3d4e5f6

// Varnish automatically bypasses requests with this cookie
```

**Logged-in user behavior:**
- All requests bypass Varnish cache
- Personalized content served from WordPress
- Admin bar, dashboards, user-specific data visible
- Performance impact: ~200-500ms response times (no cache)

**Cache bypass verification:**
```bash
# Check response headers for cache status
curl -I https://example.com/ -H "Cookie: wordpress_logged_in_abc123=..."

# Look for header:
X-Cache: MISS  # Cache bypass (not from Varnish)
X-Cache: HIT   # Served from Varnish
```

## Prevent Caching Anti-Patterns

WordPress VIP developers avoid over-using cache bypass mechanisms that degrade Varnish performance. Excessive private caching, unnecessary cookie setting, and blanket no-cache headers reduce cache hit rates.

### Anti-Pattern: Global Private Caching

```php
// ❌ Don't force private caching globally
add_action( 'send_headers', function() {
    header( 'Cache-Control: private' );
}); // Disables Varnish for entire site!

// ✅ Use private caching selectively
add_action( 'send_headers', function() {
    if ( is_user_logged_in() || is_cart() || is_checkout() ) {
        header( 'Cache-Control: private' );
    }
});
```

### Anti-Pattern: Unnecessary Cookie Setting

```php
// ❌ Don't set wordpress_ cookies for non-critical preferences
setcookie( 'wordpress_font_size', 'large', time() + 86400, '/' );
// Bypasses Varnish for all users with font preference!

// ✅ Use non-bypass cookie for preferences
setcookie( 'font_size', 'large', time() + 86400, '/' );
// Or use localStorage (client-side only)
```

### Anti-Pattern: No-Store for Cacheable Content

```php
// ❌ Don't use no-store for public content
if ( is_singular() ) {
    header( 'Cache-Control: no-store' ); // Prevents all caching!
}

// ✅ Use max-age for cacheable content
if ( is_singular() && ! is_user_logged_in() ) {
    header( 'Cache-Control: public, max-age=3600' );
}
```

## Varnish Cache Debugging

WordPress VIP includes VIP response headers for Varnish cache debugging. Headers identify cache hits/misses, TTL, and cache age.

**VIP cache headers:**
```
X-Cache: HIT               # Served from Varnish cache
X-Cache: MISS              # Bypassed cache, served from WordPress
X-Cache-Hits: 42           # Number of cache hits for this URL
Age: 120                   # Seconds since cached (2 minutes ago)
Cache-Control: max-age=300 # Cache TTL (5 minutes)
```

**Debug cache status:**
```bash
# Check cache headers
curl -I https://example.com/

# Look for cache hit
# X-Cache: HIT

# Look for cache miss
# X-Cache: MISS
```

**Common cache miss reasons:**
- Logged-in user (wordpress_logged_in_* cookie)
- Private Cache-Control header
- First request for URL (cold cache)
- Recent cache purge
- Vary header mismatch
