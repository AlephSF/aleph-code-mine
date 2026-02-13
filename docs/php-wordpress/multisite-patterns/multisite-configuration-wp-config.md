---
title: "Multisite Configuration in wp-config.php"
category: "multisite-patterns"
subcategory: "configuration"
tags: ["wordpress-multisite", "wp-config", "setup", "constants"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-12"
---

# Multisite Configuration in wp-config.php

## Overview

WordPress multisite requires specific PHP constants in wp-config.php to enable and configure the network. These constants define subdomain vs subdirectory installation, the primary site domain, and network-wide settings.

**Required Constants:** MULTISITE, SUBDOMAIN_INSTALL, DOMAIN_CURRENT_SITE, PATH_CURRENT_SITE, SITE_ID_CURRENT_SITE, BLOG_ID_CURRENT_SITE
**Environment-Driven:** Best practice uses environment variables instead of hardcoded values
**Security:** Never commit sensitive constants to version control

## Pattern Implementation

```php
// Environment-driven multisite configuration
if(isset($_ENV['MULTISITE']) && $_ENV['MULTISITE']==true) {
    define('WP_ALLOW_MULTISITE', true);
    define('MULTISITE', true);
    define('SUBDOMAIN_INSTALL', $_ENV['SUBDOMAIN_INSTALL']);
    define('DOMAIN_CURRENT_SITE', $_ENV['DOMAIN_CURRENT_SITE']);
    define('PATH_CURRENT_SITE', '/');
    define('SITE_ID_CURRENT_SITE', 1);
    define('BLOG_ID_CURRENT_SITE', 1);
}
```

**Pattern:** Check environment variable → Define all multisite constants together
**Benefit:** Single env var controls multisite mode, easy staging/production parity

**Source:** airbnb/scripts/wp-config.php

## Subdomain vs Subdirectory

**Subdomain Install:** `define('SUBDOMAIN_INSTALL', true);`
- Sites: site1.example.com, site2.example.com
- Requires wildcard DNS: *.example.com → web server

**Subdirectory Install:** `define('SUBDOMAIN_INSTALL', false);`
- Sites: example.com/site1/, example.com/site2/
- No special DNS required

**Source Confidence:** 50% adoption (airbnb uses subdomain, thekelsey single site)
