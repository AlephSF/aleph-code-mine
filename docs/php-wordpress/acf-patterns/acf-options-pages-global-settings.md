# ACF Options Pages for Global Settings

---
title: "ACF Options Pages for Global Settings"
category: "wordpress-acf"
subcategory: "global-settings"
tags: ["acf", "options-pages", "global-settings", "site-config"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Options Pages provide WordPress admin screens for site-wide settings accessible across all posts, templates, and pages. Both analyzed projects use options pages for social media links, global modules, and site configuration. Options pages store values as WordPress site options (not postmeta), making them available via `get_field('field_name', 'option')` regardless of current post context.

**Evidence:** 12 options page location rules across 74 total rules (8 in airbnb, 4 in thekelsey). 100% of projects use options pages for global settings. Pattern is architecture-agnostic (works in traditional and headless WordPress).

## Basic Options Page Registration

Options pages require programmatic registration using `acf_add_options_page()` function before field groups can target them. Registration defines page title, menu title, menu slug, and icon. TheKelsey demonstrates standard pattern in MU-plugin initialization.

**Basic Registration (TheKelsey):**

```php
// mu-plugins/thekelsey-custom/thekelsey-custom.php (lines 96-102)
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => __('Social Media'),
        'menu_title' => __('Social Media'),
        'icon_url' => 'dashicons-networking'
    ));
}
```

**Function Existence Check:** Always wrap in `function_exists()` check since ACF Pro is required (prevents fatal errors if ACF deactivated).

**Result:** Creates "Social Media" menu item in WordPress admin (typically under Settings or top-level).

## Options Page Parameters

`acf_add_options_page()` accepts array of parameters controlling page behavior and appearance. Key parameters include page_title (browser title), menu_title (sidebar menu text), menu_slug (URL identifier), icon_url (Dashicons icon), and capability (required user permission).

**Complete Parameter Example:**

```php
acf_add_options_page(array(
    'page_title'  => __('Site Settings'),        // Browser <title>
    'menu_title'  => __('Site Settings'),        // Admin menu text
    'menu_slug'   => 'site-settings',            // URL slug (admin.php?page=site-settings)
    'capability'  => 'manage_options',           // Required capability (default)
    'icon_url'    => 'dashicons-admin-generic',  // Dashicons class
    'position'    => 60,                         // Menu position (lower = higher)
    'parent_slug' => '',                         // Empty = top-level menu
    'redirect'    => true,                       // Redirect to first sub-page (if sub-pages exist)
    'post_id'     => 'options',                  // Options storage key (default 'options')
    'autoload'    => false,                      // Don't autoload (performance)
    'update_button' => __('Update'),             // Button text
    'updated_message' => __('Settings Saved')    // Success message
));
```

## Dashicons Integration

WordPress provides Dashicons icon font for admin UI consistency. Options pages use `icon_url` parameter with `dashicons-{icon-name}` classes. Both projects leverage Dashicons for semantic icon selection.

**TheKelsey Dashicons Usage:**

```php
// Social Media options page
'icon_url' => 'dashicons-networking'

// Global Modules options page
'icon_url' => 'dashicons-admin-site-alt3'
```

**Common Dashicons for Options Pages:**
- `dashicons-admin-generic` - Generic settings
- `dashicons-admin-site` - Site configuration
- `dashicons-admin-site-alt3` - Global modules
- `dashicons-networking` - Social media
- `dashicons-admin-plugins` - Plugin settings
- `dashicons-admin-tools` - Tools/utilities

**Reference:** [Dashicons Directory](https://developer.wordpress.org/resource/dashicons/)

## Field Group Targeting

After registering options page, field groups use location rules with `param: "options_page"` and `value: "{menu_slug}"` to attach fields. The menu_slug from registration becomes the location rule value.

**Registration:**

```php
acf_add_options_page(array(
    'menu_slug' => 'social-media'
));
```

**Field Group Location:**

```json
{
    "location": [
        [
            {
                "param": "options_page",
                "operator": "==",
                "value": "social-media"  // Matches menu_slug
            }
        ]
    ]
}
```

**Critical:** `value` must exactly match `menu_slug` from registration (case-sensitive).

## Accessing Options Page Fields

Options page fields use special `'option'` parameter in `get_field()` calls instead of post ID. This signals ACF to retrieve from wp_options table rather than postmeta. Omitting `'option'` parameter attempts to read from current post context (wrong data).

**Correct PHP Access:**

```php
// Get option field
$facebook_url = get_field('facebook_url', 'option');

// Display in template
if ($facebook_url) {
    echo '<a href="' . esc_url($facebook_url) . '">Facebook</a>';
}

// Multiple option fields
$social = array(
    'facebook' => get_field('facebook_url', 'option'),
    'twitter'  => get_field('twitter_url', 'option'),
    'instagram' => get_field('instagram_url', 'option')
);
```

**Incorrect (Missing 'option'):**

```php
$facebook_url = get_field('facebook_url');  // ❌ Tries to read from current post
```

## GraphQL Integration (Headless Sites)

WPGraphQL for ACF exposes options page fields at root query level, making global settings accessible without post context. Airbnb's headless architecture leverages this pattern for site-wide configuration consumed by Next.js frontend.

**GraphQL Query (Options):**

```graphql
query GetSiteSettings {
  optionsSocialMedia {  # Matches options page title/slug (camelCase)
    facebookUrl
    twitterUrl
    instagramUrl
  }
}
```

**GraphQL Response:**

```json
{
  "data": {
    "optionsSocialMedia": {
      "facebookUrl": "https://facebook.com/example",
      "twitterUrl": "https://twitter.com/example",
      "instagramUrl": "https://instagram.com/example"
    }
  }
}
```

**Field Group Configuration for GraphQL:**

```json
{
    "show_in_graphql": 1,
    "graphql_field_name": "optionsSocialMedia",
    "fields": [
        {
            "name": "facebook_url",
            "show_in_graphql": 1,
            "graphql_field_name": "facebookUrl"
        }
    ]
}
```

## Sub-Pages (Hierarchical Options)

Options pages can have sub-pages for organized settings, creating nested admin menus. Use `acf_add_options_sub_page()` with `parent_slug` matching parent page's `menu_slug`. Neither analyzed project uses sub-pages, but pattern is common for complex sites with many settings categories.

**Hierarchical Pattern:**

```php
// Parent page
acf_add_options_page(array(
    'page_title' => 'Site Settings',
    'menu_title' => 'Site Settings',
    'menu_slug'  => 'site-settings'
));

// Sub-page 1
acf_add_options_sub_page(array(
    'page_title'  => 'Social Media Settings',
    'menu_title'  => 'Social Media',
    'parent_slug' => 'site-settings'  // Matches parent menu_slug
));

// Sub-page 2
acf_add_options_sub_page(array(
    'page_title'  => 'API Configuration',
    'menu_title'  => 'APIs',
    'parent_slug' => 'site-settings'
));
```

**Admin Menu Result:**

```
Site Settings (parent)
├── Social Media (sub-page)
└── APIs (sub-page)
```

## Common Use Cases

Options pages suit site-wide configuration that applies globally rather than per-post. Social media links, analytics IDs, API credentials, global modules, and feature flags are canonical examples. Both projects follow these patterns.

**Social Media Links (TheKelsey):**

```php
// Fields: facebook_url, twitter_url, instagram_url, linkedin_url, vimeo_url

// Usage in footer template
$facebook = get_field('facebook_url', 'option');
if ($facebook) {
    echo '<a href="' . esc_url($facebook) . '">Follow us on Facebook</a>';
}
```

**Global Modules (TheKelsey):**

```php
// Fields: Reusable content blocks for site-wide components

// Usage
$global_cta = get_field('global_cta', 'option');
echo $global_cta['title'];
echo $global_cta['button_text'];
```

**API Configuration (Common Pattern):**

```php
// Fields: google_analytics_id, google_maps_api_key, mailchimp_api_key

// Usage in header
$ga_id = get_field('google_analytics_id', 'option');
if ($ga_id) {
    echo "<!-- GA tracking code with ID: $ga_id -->";
}
```

## Multisite Considerations

Options pages work differently in WordPress multisite. By default, options are site-specific (each subsite has independent settings). ACF Pro supports network-level options pages accessible to super admins across all sites. Neither analyzed project is multisite-configured, but Airbnb's VIP platform supports multisite architecture.

**Multisite Options Page:**

```php
acf_add_options_page(array(
    'page_title'  => 'Network Settings',
    'menu_title'  => 'Network Settings',
    'menu_slug'   => 'network-settings',
    'capability'  => 'manage_network_options',  // Super admin only
    'parent_slug' => 'settings.php'             // Network Admin > Settings
));
```

**Access in Multisite:**

```php
// Current site's options
$site_setting = get_field('site_setting', 'option');

// Network-wide options (across all subsites)
$network_setting = get_field('network_setting', 'option');
```

## Capability-Based Access Control

Options pages use WordPress capabilities to restrict access. Default `manage_options` capability limits to administrators. Custom capabilities enable role-based access for editor-level settings pages or developer-only configuration.

**Admin-Only (Default):**

```php
acf_add_options_page(array(
    'capability' => 'manage_options'  // Administrators only
));
```

**Editor-Accessible:**

```php
acf_add_options_page(array(
    'capability' => 'edit_posts'  // Editors and above
));
```

**Custom Capability:**

```php
acf_add_options_page(array(
    'capability' => 'manage_site_settings'  // Custom capability
));

// Grant capability to editor role
$role = get_role('editor');
$role->add_cap('manage_site_settings');
```

## Options Page vs Customizer

WordPress Customizer provides live-preview theme options. ACF Options Pages provide form-based settings without live preview. Use Customizer for visual theme settings (colors, fonts, layouts). Use Options Pages for data-driven configuration (API keys, feature flags, global content).

**Decision Matrix:**

| Requirement | Use Customizer | Use Options Pages |
|-------------|----------------|-------------------|
| Live preview needed | ✅ | ❌ |
| Theme-specific settings | ✅ | Maybe |
| Plugin settings | ❌ | ✅ |
| Complex data structures | ❌ | ✅ |
| Repeater fields | ❌ | ✅ |
| Developer-focused config | ❌ | ✅ |

**Common Pattern:** Combine both. Customizer for theme appearance, Options Pages for site functionality.

## Database Storage

Options page fields save to WordPress `wp_options` table with option_name matching field name (or custom post_id prefix). Single options page can result in dozens of wp_options rows. Unlike postmeta (per-post data), options are site-global.

**Database Example:**

```sql
-- ACF options page fields
option_name: options_facebook_url
option_value: https://facebook.com/example

option_name: options_twitter_url
option_value: https://twitter.com/example

option_name: options_instagram_url
option_value: https://instagram.com/example
```

**Prefix:** `options_` prefix added automatically. Custom prefixes via `post_id` parameter in registration.

## Options Page Autoload

WordPress options can autoload (loaded on every page request) or load on-demand. Options pages default to `autoload: false` for performance (ACF loads when accessed via `get_field()`). Override with `autoload: true` only for critical, frequently-accessed settings.

**Performance Pattern (Default):**

```php
acf_add_options_page(array(
    'autoload' => false  // Don't load on every request (performance)
));
```

**Critical Settings (Use Sparingly):**

```php
acf_add_options_page(array(
    'autoload' => true  // Load on every request (if critical)
));
```

**Recommendation:** Keep `autoload: false` unless settings are used on 100% of page loads. Most settings are conditional (social links in footer only).

## Validation and Required Fields

Options page fields support validation and required field rules like post fields. Editors cannot save options page until required fields are filled and validation passes. This prevents incomplete configuration from breaking site functionality.

**Required Field Example:**

```json
{
    "name": "google_analytics_id",
    "type": "text",
    "required": 1,
    "instructions": "Required for site analytics to function"
}
```

**Custom Validation:**

```php
add_filter('acf/validate_value/name=google_analytics_id', function($valid, $value, $field, $input_name) {
    if (!$valid) {
        return $valid;  // Already invalid
    }

    // Validate GA ID format (UA-XXXXXXXX-X or G-XXXXXXXXXX)
    if (!preg_match('/^(UA-\d{6,10}-\d|G-[A-Z0-9]{10})$/', $value)) {
        $valid = 'Invalid Google Analytics ID format';
    }

    return $valid;
}, 10, 4);
```

## JSON Sync with Options Pages

Options pages field groups sync via ACF JSON like post-based field groups. Location rules target options pages by menu_slug. All analyzed projects commit options page field groups to version control alongside post/template field groups.

**JSON Storage:**

```json
{
    "key": "group_social_media",
    "title": "Social Media Options",
    "fields": [...],
    "location": [
        [
            {
                "param": "options_page",
                "operator": "==",
                "value": "social-media"
            }
        ]
    ]
}
```

**Version Control:** Commit JSON files alongside options page registration code. Team members sync via Git pull + ACF sync.

## Common Pitfalls

Forgetting `'option'` parameter in `get_field()` causes fields to return null or wrong post data. Missing function existence checks break site when ACF deactivated. Using autoload for rarely-accessed options wastes memory. Creating too many options pages fragments settings (use sub-pages or field groups with tabs instead).

**Anti-Patterns:**

```php
// ❌ No function existence check
acf_add_options_page([...]);  // Fatal error if ACF deactivated

// ❌ Missing 'option' parameter
$facebook = get_field('facebook_url');  // Returns null or wrong data

// ❌ Excessive autoload
acf_add_options_page(['autoload' => true]);  // Memory waste for rarely-used settings

// ❌ Too many top-level options pages (10+)
// Better: Use sub-pages or tabs within fewer parent pages
```

## Related Patterns

- **ACF Location Rules** (targeting options pages)
- **ACF Field Groups** (organizing options fields)
- **ACF + GraphQL Integration** (exposing options to headless frontends)
- **WordPress Customizer** (alternative for theme-specific visual settings)
- **Custom Post Types** (alternative for entity-based data vs site-global settings)

## References

- TheKelsey: `mu-plugins/thekelsey-custom/thekelsey-custom.php` (lines 96-110, options page registration)
- ACF Documentation: [Options Pages](https://www.advancedcustomfields.com/resources/options-page/)
- WordPress: [Dashicons](https://developer.wordpress.org/resource/dashicons/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 9: Options Pages)
