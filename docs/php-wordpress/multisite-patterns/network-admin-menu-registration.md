---
title: "Network Admin Menu Registration"
category: "multisite-patterns"
subcategory: "network-admin-ui"
tags: ["wordpress-multisite", "admin-menu", "network-admin", "ui"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

# Network Admin Menu Registration

## Overview

WordPress multisite provides the `network_admin_menu` action hook for registering admin pages that appear only in the Network Admin area (/wp-admin/network/). Network Admin menus control network-wide settings like site creation, user management, and plugin configuration.

**Key Distinction:** `admin_menu` hook runs on individual sites, `network_admin_menu` hook runs only in Network Admin dashboard
**Access Control:** Requires `manage_network` or specific network capabilities
**Common Use Cases:** Network settings, site management, license configuration, SAML/SSO settings

## Pattern Implementation

```php
/**
 * Register network admin settings page
 * Only appears in Network Admin (/wp-admin/network/)
 */
add_action('network_admin_menu', 'register_network_settings_page', 5);

function register_network_settings_page() {
    add_menu_page(
        'Network Settings',              // Page title
        'My Plugin',                     // Menu title
        'manage_network_options',        // Capability
        'my-plugin-network-settings',    // Menu slug
        'render_network_settings_page',  // Callback function
        'dashicons-admin-network',       // Icon
        30                               // Position
    );
}
```

**Priority:** 5 (lower than default 10) allows other plugins to hook under this menu

**Source:** Yoast SEO Network Admin menu registration

## Related Patterns

- **Network-Wide Options** - Store network settings using get_site_option/update_site_option
- **is_network_admin() Checks** - Conditional logic for network admin context

**Pattern Adoption:** 100% of plugins with network-wide configuration
