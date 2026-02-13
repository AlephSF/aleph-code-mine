---
title: "WordPress VIP Go Configuration Patterns"
category: "environment-configuration"
subcategory: "platform-specific"
tags: ["wordpress-vip", "vip-go", "platform-configuration"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# WordPress VIP Go Configuration Patterns

## Overview

WordPress VIP Go uses `vip-config.php` for platform-specific configuration instead of traditional `wp-config.php`. This file handles redirects, feature flags, and VIP-specific constants.

**File:** `vip-config.php` (committed to version control)
**Purpose:** Early-stage configuration before WordPress bootstrap
**Adoption:** 100% of VIP Go installations (1/1 analyzed)

## vip-config.php Structure

```php
<?php
/**
 * VIP Go configuration file
 * Executes before WordPress loads
 */

// VIP-specific constants
define('WPCOM_VIP_USE_JETPACK_PHOTON', true);

// Environment detection
$http_host = $_SERVER['HTTP_HOST'];

// Conditional feature flags by site
if ($http_host === 'news.airbnb.com') {
    define('VIP_JETPACK_SKIP_LOAD', true);
}

// Domain redirects (early, before WP)
$redirects = [
    [
        'domains' => ['press.airbnb.com'],
        'target'  => 'https://news.airbnb.com',
        'status'  => 302,
    ],
];

foreach ($redirects as $redirect) {
    if (in_array($http_host, $redirect['domains'], true)) {
        header("Location: {$redirect['target']}", true, $redirect['status']);
        exit;
    }
}
```

## VIP Environment Constants

```php
// Check VIP environment
if (defined('VIP_GO_ENV')) {
    $env = VIP_GO_ENV; // 'production', 'develop', 'preprod'
}

if (VIP_GO_ENV === 'production') {
    // Production-only features
}
```

**Available Environments:**
- `production` - Live site
- `develop` - Development environment
- `preprod` - Pre-production staging

## Database Configuration (Handled by VIP)

**Don't define in vip-config.php:**
```php
// ❌ VIP provides these automatically
// define('DB_NAME', '...');
// define('DB_USER', '...');
// define('DB_PASSWORD', '...');
```

**VIP automatically configures:**
- Database connection
- Redis/Memcached
- File uploads to S3

## VIP-Specific Features

**Jetpack Photon:**
```php
define('WPCOM_VIP_USE_JETPACK_PHOTON', true);
```

**Skip Jetpack for specific sites:**
```php
if ($http_host === 'news.airbnb.com') {
    define('VIP_JETPACK_SKIP_LOAD', true);
}
```

## Security Headers in Redirects

```php
$redirects = [
    [
        'domains' => ['old.example.com'],
        'target'  => 'https://new.example.com',
        'status'  => 301,
        'headers' => [
            'Strict-Transport-Security: max-age=31536000',
            'X-Content-Type-Options: nosniff',
            'X-Frame-Options: SAMEORIGIN',
        ],
    ],
];
```

**Source:** airbnb/vip-config/vip-config.php (100% VIP adoption)
