---
title: "VIP Redirect Patterns in vip-config.php"
category: "wordpress-vip"
subcategory: "configuration"
tags: ["redirects", "vip-config", "domain-migration", "security-headers", "301-redirects"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## VIP Redirect Architecture

WordPress VIP uses vip-config.php for early-stage domain redirects before WordPress routing initializes. Early redirects execute before database connections, plugin loading, and WordPress core initialization, providing sub-millisecond redirect performance for legacy domains, international locales, and site migrations.

**Redirect timing:**
```
vip-config.php (redirects) → WordPress core → Plugins → Theme
```

**Performance benefit:** ~200-300ms faster than WordPress-based redirects (no DB connection, no plugin loading)

**Common use cases:**
- Legacy domain migrations (press.airbnb.com → news.airbnb.com)
- International domain redirects (airbnbforwork.de → airbnbforwork.com)
- Technology blog redirects (airbnb.io → airbnb.tech)
- Security header injection on redirects

## Consolidated Redirect Array Pattern

WordPress VIP uses consolidated redirect arrays in vip-config.php for maintainable, DRY redirect configurations. Pattern defines all redirects in single data structure with domains, targets, status codes, and optional headers.

```php
//vip-config.php
$h=$_SERVER['HTTP_HOST'];$u=$_SERVER['REQUEST_URI'];
$redirects=[['domains'=>['press.atairbnb.com','press.airbnb.com'],'target'=>'https://news.airbnb.com','status'=>302],['domains'=>['www.airbnbforwork.de','airbnbforwork.de','airbnbforwork.fr'],'target'=>'https://www.airbnbforwork.com','status'=>302],['domains'=>['airbnb.io','www.airbnb.io'],'target'=>'https://airbnb.tech','status'=>302]];
foreach($redirects as $r){
if('/cache-healthcheck?'!==$u&&in_array($h,$r['domains'],true)){
if(!empty($r['headers'])){foreach($r['headers'] as $hdr){header($hdr);}}
header('Location:'.$r['target'].$u,true,$r['status']);exit;
}}
```

**Array structure:**
- `domains`: Array of source domains to redirect
- `target`: Destination URL (without path)
- `status`: HTTP status code (301 or 302)
- `headers`: Optional security headers

## Request URI Preservation Pattern

WordPress VIP redirect patterns preserve request URIs (paths + query strings) by appending `$request_uri` to redirect targets. Pattern ensures deep links survive domain migrations.

```php
// Redirect with URI preservation
header('Location: ' . $redirect['target'] . $request_uri, true, $redirect['status']);
exit;
```

**Example redirects:**
```
Source: https://press.airbnb.com/releases/quarterly-earnings
Target: https://news.airbnb.com/releases/quarterly-earnings
        ↑ URI preserved

Source: https://press.airbnb.com/media/?filter=2024
Target: https://news.airbnb.com/media/?filter=2024
        ↑ Path + query string preserved
```

**SEO benefit:** Preserves deep links, preventing 404 errors and link equity loss

**Alternative (path replacement):**
```php
// Custom path transformation
if (in_array($http_host, ['old.example.com'], true)) {
    $new_uri = str_replace('/old-path/', '/new-path/', $request_uri);
    header('Location: https://new.example.com' . $new_uri, true, 301);
    exit;
}
```

## HTTP 301 vs 302 Redirect Status Codes

WordPress VIP uses HTTP 301 (permanent) for completed domain migrations and HTTP 302 (temporary) for experimental migrations or A/B testing. Status code selection impacts SEO, browser caching, and search engine indexing.

```php
[
    'domains' => ['old-domain.com'],
    'target'  => 'https://new-domain.com',
    'status'  => 301, // Permanent redirect (SEO transfer)
],

[
    'domains' => ['test-domain.com'],
    'target'  => 'https://www.example.com',
    'status'  => 302, // Temporary redirect (no SEO transfer)
],
```

**HTTP 301 (Permanent):**
- Transfers SEO link equity to new domain
- Browsers cache redirect aggressively
- Search engines update indexes to new URL
- **Use for:** Completed domain migrations, permanent URL changes

**HTTP 302 (Temporary):**
- Does NOT transfer SEO link equity
- Browsers may not cache redirect
- Search engines keep original URL indexed
- **Use for:** A/B testing, temporary migrations, experimental redirects

**VIP recommendation:** Use 302 for initial migrations, switch to 301 after 30-60 days

## Security Headers on Redirects

WordPress VIP injects security headers during redirects for domains requiring CSP, HSTS, X-Frame-Options, or other protective headers before reaching destination. Pattern hardens legacy domains without modifying destination site.

```php
[
    'domains' => ['realestate.withairbnb.com'],
    'target'  => 'https://www.airbnb.com/airbnb-friendly',
    'status'  => 302,
    'headers' => [
        'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload',
        "Content-Security-Policy: default-src 'self'",
        'X-Content-Type-Options: nosniff',
        'X-Frame-Options: SAMEORIGIN',
        'X-XSS-Protection: 1; mode=block',
        'Referrer-Policy: strict-origin-when-cross-origin',
        'Permissions-Policy: geolocation=(), camera=(), microphone=()',
    ],
],
```

**Common security headers:**
- `Strict-Transport-Security`: Force HTTPS (HSTS)
- `Content-Security-Policy`: Prevent XSS attacks
- `X-Frame-Options`: Prevent clickjacking
- `X-Content-Type-Options`: Prevent MIME sniffing
- `Referrer-Policy`: Control referrer information
- `Permissions-Policy`: Control browser features

**Use case:** Legacy domains with security requirements before redirect completes

## Cache Healthcheck Bypass Pattern

WordPress VIP monitoring uses `/cache-healthcheck?` endpoint to verify Varnish and WordPress health. All redirect logic skips healthcheck endpoint to prevent monitoring failures.

```php
foreach ($redirects as $redirect) {
    if (
        '/cache-healthcheck?' !== $request_uri && // Always skip healthcheck
        in_array($http_host, $redirect['domains'], true)
    ) {
        header('Location: ' . $redirect['target'] . $request_uri, true, $redirect['status']);
        exit;
    }
}
```

**Healthcheck bypass logic:**
- `'/cache-healthcheck?' !== $request_uri` condition executes before redirect check
- VIP monitoring receives HTTP 200 from WordPress (not redirect)
- Redirect logic never interferes with platform monitoring

**Critical pattern:** Never redirect `/cache-healthcheck?` endpoint (breaks VIP monitoring)

## International Locale Redirect Pattern

WordPress VIP consolidates international domain redirects for multi-locale sites migrating to unified .com domains. Pattern redirects 5-10 country-specific TLDs to single global domain.

```php
[
    'domains' => [
        'www.airbnbforwork.de',
        'airbnbforwork.de',
        'www.airbnbforwork.fr',
        'airbnbforwork.fr',
        'www.airbnbforwork.es',
        'airbnbforwork.es',
        'www.airbnbforwork.it',
        'airbnbforwork.it',
    ],
    'target'  => 'https://www.airbnbforwork.com',
    'status'  => 302,
],
```

**Common international redirect patterns:**
- **Country TLDs:** .de, .fr, .es, .it → .com
- **www prefixes:** Both www and non-www variants
- **Locale subdomains:** de.example.com → example.com/de

**Advanced pattern (locale path mapping):**
```php
// Redirect .de to /de path
if (in_array($http_host, ['www.airbnbforwork.de', 'airbnbforwork.de'], true)) {
    $new_uri = '/de' . $request_uri;
    header('Location: https://www.airbnbforwork.com' . $new_uri, true, 302);
    exit;
}
```

## Legacy Domain Migration Pattern

WordPress VIP uses vip-config.php redirects for legacy domain migrations after rebranding, acquisitions, or domain consolidation. Pattern handles press/blog/news domain changes common in corporate WordPress networks.

```php
// Press domain migration
[
    'domains' => ['press.atairbnb.com', 'press.airbnb.com'],
    'target'  => 'https://news.airbnb.com',
    'status'  => 302, // Temporary (testing phase)
],

// Technology blog migration
[
    'domains' => ['airbnb.io', 'www.airbnb.io'],
    'target'  => 'https://airbnb.tech',
    'status'  => 302, // Temporary (testing phase)
],
```

**Migration timeline:**
1. **Week 1-4:** HTTP 302 redirects (temporary, testing)
2. **Week 5-8:** Monitor analytics, fix broken links
3. **Week 9+:** Change to HTTP 301 (permanent, SEO transfer)

**Common legacy domains:**
- press.example.com → news.example.com
- blog.example.com → www.example.com/blog
- example.io → example.tech

## Subdomain to Path Redirect Pattern

WordPress VIP redirects subdomains to path-based URLs for SEO consolidation and simplified site architecture. Pattern transforms `blog.example.com` to `www.example.com/blog` while preserving URIs.

```php
// Redirect subdomain to path
if ($http_host === 'blog.airbnb.com') {
    $new_uri = '/blog' . $request_uri;
    header('Location: https://www.airbnb.com' . $new_uri, true, 301);
    exit;
}

// Redirect subdomain with URI transformation
if ($http_host === 'press.airbnb.com') {
    // Transform /releases/2024 → /newsroom/releases/2024
    $new_uri = '/newsroom' . $request_uri;
    header('Location: https://www.airbnb.com' . $new_uri, true, 301);
    exit;
}
```

**SEO benefits:**
- Consolidates domain authority
- Simplifies SSL certificate management
- Improves crawl efficiency

**Use cases:**
- Blog subdomain → /blog path
- Press subdomain → /newsroom path
- Help subdomain → /support path

## Domain Canonicalization Pattern

WordPress VIP redirects www/non-www variants to canonical domain for consistent branding and SEO consolidation. Pattern enforces single canonical domain across network.

```php
// Enforce www prefix (www.example.com is canonical)
if ($http_host === 'airbnb.com') {
    header('Location: https://www.airbnb.com' . $request_uri, true, 301);
    exit;
}

// Enforce non-www (example.com is canonical)
if ($http_host === 'www.example.io') {
    header('Location: https://example.io' . $request_uri, true, 301);
    exit;
}
```

**Canonical domain selection:**
- **www.example.com:** Enterprise branding (www prefix)
- **example.com:** Tech/startup branding (no prefix)

**SEO impact:** Prevents duplicate content penalties from www/non-www splits

## Redirect Array Maintainability

WordPress VIP consolidated redirect arrays improve maintainability by centralizing redirect logic in single data structure. Pattern enables bulk updates, testing, and auditing.

**Benefits:**
- Single source of truth for all redirects
- Easy to add/remove redirects
- Testable redirect logic
- Self-documenting redirect rules

**Anti-pattern (scattered redirects):**
```php
// ❌ Hard to maintain
if ($http_host === 'press.airbnb.com') {
    header('Location: https://news.airbnb.com' . $request_uri);
    exit;
}

// ... 500 lines later ...

if ($http_host === 'airbnb.io') {
    header('Location: https://airbnb.tech' . $request_uri);
    exit;
}
```

**Recommended pattern:**
```php
// ✅ Easy to maintain
$redirects = [
    ['domains' => ['press.airbnb.com'], 'target' => 'https://news.airbnb.com', 'status' => 302],
    ['domains' => ['airbnb.io'], 'target' => 'https://airbnb.tech', 'status' => 302],
];
```

## Redirect Performance Optimization

WordPress VIP redirect arrays execute in O(N×M) time (N redirects × M domains per redirect). Optimize by using early `in_array()` checks and strict type comparison.

```php
foreach($redirects as $r){
if('/cache-healthcheck?'!==$request_uri&&in_array($http_host,$r['domains'],true)){
if(!empty($r['headers'])){foreach($r['headers'] as $h){header($h);}}
header('Location:'.$r['target'].$request_uri,true,$r['status']);exit;
}}
```

**Performance considerations:**
- Use `in_array($h,$d,true)` (strict comparison ~10% faster)
- Call `exit` immediately after redirect
- Skip healthcheck first (most common request)
- Limit redirects to <20 rules (linear search acceptable)

**Alternative (hash map for 50+ redirects):**
```php
$map=[];foreach($redirects as $r){foreach($r['domains'] as $d){$map[$d]=$r;}}
if(isset($map[$http_host])){$r=$map[$http_host];header('Location:'.$r['target'].$request_uri,true,$r['status']);exit;}
```

## Testing VIP Redirects

WordPress VIP redirects should be tested using curl or browser dev tools before deployment. Testing verifies correct status codes, URI preservation, and header injection.

```bash
# Test redirect with curl
curl -I https://press.airbnb.com/releases/quarterly

# Expected output:
# HTTP/1.1 302 Found
# Location: https://news.airbnb.com/releases/quarterly

# Test redirect status code
curl -I https://old-domain.com | grep "HTTP/"
# HTTP/1.1 301 Moved Permanently  (permanent)
# HTTP/1.1 302 Found              (temporary)

# Test security headers on redirect
curl -I https://realestate.withairbnb.com
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: SAMEORIGIN

# Test healthcheck bypass
curl -I https://press.airbnb.com/cache-healthcheck?
# HTTP/1.1 200 OK  (NOT redirected)
```

**Testing checklist:**
- ✅ Correct HTTP status code (301 or 302)
- ✅ URI preservation (path + query string)
- ✅ Security headers present (if configured)
- ✅ Healthcheck endpoint bypasses redirect
- ✅ www/non-www variants redirect correctly
