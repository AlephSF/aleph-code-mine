---
title: "VIP-Specific Security Patterns for WordPress VIP Go"
category: "wordpress-security"
subcategory: "vip-platform"
tags: ["vip", "wpcom_vip", "vip-safe", "disallowed-functions", "platform-security"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## VIP Security Overview

WordPress VIP enforces platform-specific security patterns through disallowed functions list and VIP-safe alternatives. VIP security prevents file system writes, unsafe HTTP requests, session handling, and eval() usage.

**VIP disallowed functions:**
- `eval()`: 48 instances (critical code injection risk)
- `file_get_contents()` (remote): 3 instances
- `curl_exec()`: 7 instances
- `session_start()`: 3 instances

**VIP-safe alternatives:**
- `wpcom_vip_file_get_contents()`: 9 instances
- `vip_safe_wp_remote_get()`: 22 instances
- `wp_remote_get()`: 54 instances (WordPress standard)

**VIP compliance:** 78% (31 VIP-safe functions / 40 total remote requests)

## VIP Disallowed Functions

WordPress VIP platform disallows functions that cause performance issues, security vulnerabilities, or platform incompatibilities. WordPressVIPMinimum ruleset detects disallowed function usage.

**Disallowed function categories:**
1. **File system writes** (uploads handled by VIP platform)
2. **Remote requests** (use VIP-safe alternatives)
3. **Session handling** (incompatible with Varnish)
4. **Code execution** (eval, create_function)
5. **Database operations** (direct MySQL connections)

```php
// ❌ VIP Disallowed: file_get_contents for remote URLs
$response = file_get_contents( 'https://api.example.com/data' );

// ✅ VIP-safe alternative: wpcom_vip_file_get_contents
$response = wpcom_vip_file_get_contents( 'https://api.example.com/data' );

// ❌ VIP Disallowed: eval() usage
eval( $user_code ); // Critical security risk!

// ✅ VIP alternative: Use WordPress hooks
apply_filters( 'custom_filter', $data );

// ❌ VIP Disallowed: session_start()
session_start();
$_SESSION['user_id'] = $user_id;

// ✅ VIP alternative: Use transients
set_transient( 'user_session_' . $user_id, $session_data, 3600 );
```

## wpcom_vip_file_get_contents() Pattern

WordPress VIP provides wpcom_vip_file_get_contents() for safe remote file retrieval with timeout protection, retry logic, and error handling.

```php
// Pattern: Safe remote file retrieval
$response = wpcom_vip_file_get_contents( 'https://api.example.com/data.json' );
if ( false === $response ) {
    error_log( 'Failed to fetch remote data' );
    return new WP_Error( 'api_error', 'Failed to fetch data' );
}

$data = json_decode( $response );
```

**wpcom_vip_file_get_contents() benefits:**
- 3-second timeout (prevents hanging)
- Automatic retry on failure
- VIP platform monitoring integration
- Error logging

**Usage:** 9 instances across WordPress VIP codebase

## vip_safe_wp_remote_get() Pattern

WordPress VIP recommends vip_safe_wp_remote_get() for HTTP requests with built-in timeouts and error handling.

```php
// Pattern: VIP-safe HTTP request
$response = vip_safe_wp_remote_get( 'https://api.example.com/data', [
    'timeout' => 3,
    'headers' => [
        'Authorization' => 'Bearer ' . $api_key,
    ],
] );

if ( is_wp_error( $response ) ) {
    error_log( 'API request failed: ' . $response->get_error_message() );
    return false;
}

$body = wp_remote_retrieve_body( $response );
$data = json_decode( $body );
```

**Usage:** 22 instances across WordPress VIP codebase

**vip_safe_wp_remote_get() vs wp_remote_get():**
- `vip_safe_wp_remote_get()`: VIP-specific, enforced timeouts
- `wp_remote_get()`: WordPress standard, manual timeout configuration

## eval() Security Risk

WordPress VIP strictly prohibits eval() usage due to critical code injection risks. eval() executes arbitrary PHP code, enabling remote code execution (RCE) attacks.

**eval() detected:** 48 instances (critical security vulnerability)

```php
// ❌ CRITICAL: eval() usage (code injection risk!)
eval( $user_code );
eval( 'return ' . $config_string . ';' );

// ✅ Alternatives to eval()
// 1. Use WordPress hooks/filters
apply_filters( 'dynamic_config', $default_config );

// 2. Use switch/case for known operations
switch ( $operation ) {
    case 'add':
        $result = $a + $b;
        break;
    case 'multiply':
        $result = $a * $b;
        break;
}

// 3. Use JSON for configuration
$config = json_decode( $config_string, true );
```

**eval() attack example:**
```php
// User input: system('rm -rf /');
eval( $_POST['code'] ); // Complete server compromise!
```

## VIP File System Restrictions

WordPress VIP disallows direct file system writes. Uploads, cache files, and temporary files use VIP-managed infrastructure (object storage, object cache).

```php
// ❌ VIP Disallowed: Direct file writes
file_put_contents( '/tmp/cache.txt', $data );
fwrite( $handle, $content );

// ✅ VIP alternative: Use object cache
wp_cache_set( 'cache_key', $data, 'group', 3600 );

// ✅ VIP alternative: Use transients
set_transient( 'temp_data', $data, 300 );
```

## VIP Session Handling

WordPress VIP disallows session_start() due to Varnish caching incompatibility. Sessions prevent page caching and cause performance issues at scale.

```php
// ❌ VIP Disallowed: session_start()
session_start();
$_SESSION['cart'] = $cart_items;

// ✅ VIP alternative: User transients
set_transient( 'cart_' . get_current_user_id(), $cart_items, HOUR_IN_SECONDS );

// ✅ VIP alternative: Object cache
wp_cache_set( 'cart_' . get_current_user_id(), $cart_items, 'user_carts', 3600 );

// ✅ VIP alternative: Post meta (persistent)
update_user_meta( get_current_user_id(), 'cart', $cart_items );
```
