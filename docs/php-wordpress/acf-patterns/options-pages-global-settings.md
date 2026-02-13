---
title: "ACF Options Pages for Global Site Settings"
category: "wordpress-acf"
subcategory: "site-configuration"
tags: ["acf", "options-pages", "global-settings", "site-wide-data", "multisite"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Options Pages provide admin interfaces for site-wide settings not tied to specific posts or pages. Common use cases include social media links, global modules, site-wide toggles, and API credentials.

WordPress projects analyzed show 100% adoption of ACF Options Pages for global settings (10+ options pages across 2 projects, primarily for social media, footer settings, and reusable content).

## Basic Options Page Registration

ACF Options Pages must be registered programmatically via PHP before field groups can attach to them.

### Simple Registration

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => 'Site Settings',
        'menu_title' => 'Site Settings',
        'menu_slug'  => 'site-settings',
        'capability' => 'edit_posts',
        'redirect'   => false
    ));
}
```

**Key Parameters:**
- `page_title`: Browser title and h1 heading
- `menu_title`: Admin menu item label
- `menu_slug`: URL slug (unique identifier)
- `capability`: WordPress capability required to access page
- `redirect`: Auto-redirect to first sub-page if true

### Function Existence Check Pattern

Always wrap `acf_add_options_page()` calls in existence check to prevent fatal errors if ACF is deactivated.

```php
// Good: Safe if ACF deactivated
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page( /* ... */ );
}

// Bad: Fatal error if ACF missing
acf_add_options_page( /* ... */ );
```

## Options Page with Custom Icon

Dashicons provide visual identification for options pages in the WordPress admin menu.

### Dashicon Pattern

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => __('Social Media'),
        'menu_title' => __('Social Media'),
        'menu_slug'  => 'social-media-settings',
        'icon_url'   => 'dashicons-networking', // Dashicon name
        'position'   => 30 // Menu position (below Pages)
    ));
}
```

**Common Dashicons for Settings:**
- `dashicons-networking`: Social media
- `dashicons-admin-site-alt3`: Global modules
- `dashicons-admin-generic`: General settings
- `dashicons-admin-tools`: Tools/utilities
- `dashicons-admin-appearance`: Theme settings

**Reference:** https://developer.wordpress.org/resource/dashicons/

## Parent/Sub-Page Hierarchy

Sub-pages organize related settings under a parent options page.

### Parent + Sub-Pages Pattern

```php
if( function_exists('acf_add_options_page') ) {
    // Parent page
    acf_add_options_page(array(
        'page_title' => 'Theme Settings',
        'menu_title' => 'Theme Settings',
        'menu_slug'  => 'theme-settings',
        'capability' => 'edit_posts',
        'redirect'   => true // Auto-redirect to first sub-page
    ));

    // Sub-page: Header
    acf_add_options_sub_page(array(
        'page_title'  => 'Header Settings',
        'menu_title'  => 'Header',
        'parent_slug' => 'theme-settings',
    ));

    // Sub-page: Footer
    acf_add_options_sub_page(array(
        'page_title'  => 'Footer Settings',
        'menu_title'  => 'Footer',
        'parent_slug' => 'theme-settings',
    ));

    // Sub-page: Social
    acf_add_options_sub_page(array(
        'page_title'  => 'Social Media',
        'menu_title'  => 'Social',
        'parent_slug' => 'theme-settings',
    ));
}
```

**Admin Menu Result:**
```
└─ Theme Settings
   ├─ Header
   ├─ Footer
   └─ Social
```

**Note:** `redirect: true` on parent automatically redirects to first sub-page when parent menu item is clicked.

## Accessing Options Page Data

Options page fields use `'option'` as the second parameter in `get_field()` calls.

### Basic Field Access

```php
<?php
// Get field from options page
$facebook_url = get_field('facebook_url', 'option');
$twitter_url = get_field('twitter_url', 'option');
$copyright_text = get_field('copyright_text', 'option');

// Use in template
if( $facebook_url ) {
    echo '<a href="' . esc_url($facebook_url) . '">Facebook</a>';
}
?>
```

### Repeater Field on Options Page

```php
<?php
// Global footer modules (repeater on options page)
if( have_rows('footer_modules', 'option') ):
    while( have_rows('footer_modules', 'option') ): the_row();

        $module_title = get_sub_field('module_title');
        $module_content = get_sub_field('module_content');
        ?>

        <div class="footer-module">
            <h3><?php echo esc_html($module_title); ?></h3>
            <div><?php echo $module_content; ?></div>
        </div>

    <?php endwhile;
endif;
?>
```

## Real-World Examples

### Example 1: Social Media Links (thekelsey)

```php
// mu-plugins/thekelsey-custom/thekelsey-custom.php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => __('Social Media'),
        'menu_title' => __('Social Media'),
        'icon_url'   => 'dashicons-networking'
    ));
}
```

**Field Group Location Rule:**
```json
{
  "location": [
    [
      {
        "param": "options_page",
        "operator": "==",
        "value": "acf-options-social-media"
      }
    ]
  ]
}
```

**Template Usage (Global Footer):**
```php
<footer class="site-footer">
    <div class="social-links">
        <?php if( get_field('facebook_url', 'option') ): ?>
            <a href="<?php the_field('facebook_url', 'option'); ?>">Facebook</a>
        <?php endif; ?>

        <?php if( get_field('twitter_url', 'option') ): ?>
            <a href="<?php the_field('twitter_url', 'option'); ?>">Twitter</a>
        <?php endif; ?>

        <?php if( get_field('instagram_url', 'option') ): ?>
            <a href="<?php the_field('instagram_url', 'option'); ?>">Instagram</a>
        <?php endif; ?>
    </div>
</footer>
```

### Example 2: Global Modules (thekelsey)

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => __('Global Modules'),
        'menu_title' => __('Global Modules'),
        'icon_url'   => 'dashicons-admin-site-alt3'
    ));
}
```

**Use Case:** Reusable content blocks (donation forms, event registration, global announcements) accessible across all templates.

### Example 3: Theme Settings Hierarchy (airbnb a4re theme)

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => 'Theme General Settings',
        'menu_title' => 'Theme Settings',
        'menu_slug'  => 'theme-general-settings',
        'capability' => 'edit_posts',
    ));

    acf_add_options_sub_page(array(
        'page_title'  => 'Theme Footer Settings',
        'menu_title'  => 'Footer',
        'parent_slug' => 'theme-general-settings',
    ));
}
```

## Options Page Capabilities

Control who can access options pages with WordPress capability strings.

### Capability Options

```php
// Editor and above
'capability' => 'edit_posts'

// Administrator only
'capability' => 'manage_options'

// Custom capability
'capability' => 'manage_site_settings'

// Super admin only (multisite)
'capability' => 'manage_network'
```

**Default:** `edit_posts` (authors, editors, admins can access)

**Best Practice:** Use `manage_options` for sensitive settings (API keys, payment gateways).

## Multisite Options Pages

WordPress VIP multisite (8+ sites) benefits from network-wide vs site-specific options pages.

### Network-Wide Options Page

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => 'Network Settings',
        'menu_title' => 'Network Settings',
        'menu_slug'  => 'network-settings',
        'capability' => 'manage_network',
        'parent'     => 'settings.php' // Add to Network Admin > Settings
    ));
}
```

**Access:** Network Admin → Settings → Network Settings

### Site-Specific Options Page

```php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => 'Site Settings',
        'menu_title' => 'Site Settings',
        'menu_slug'  => 'site-settings-' . get_current_blog_id(),
        'capability' => 'manage_options',
    ));
}
```

**Pattern:** Unique `menu_slug` per site using `get_current_blog_id()`.

## Field Group Attachment

ACF field groups attach to options pages via location rules.

### Options Page Location Rule

```json
{
  "key": "group_social_media",
  "title": "Social Media Links",
  "fields": [
    {"name": "facebook_url", "type": "url"},
    {"name": "twitter_url", "type": "url"},
    {"name": "instagram_url", "type": "url"}
  ],
  "location": [
    [
      {
        "param": "options_page",
        "operator": "==",
        "value": "acf-options-social-media"
      }
    ]
  ]
}
```

**Value Format:** `acf-options-{menu_slug}`

**Example Mappings:**
- `menu_slug: "social-media"` → `value: "acf-options-social-media"`
- `menu_slug: "theme-settings"` → `value: "acf-options-theme-settings"`
- `menu_slug: "footer"` (sub-page) → `value: "acf-options-footer"`

## WPGraphQL Integration

Options page fields expose to WPGraphQL when `show_in_graphql` is enabled.

### GraphQL Configuration

```json
{
  "key": "group_social_media",
  "title": "Social Media Links",
  "show_in_graphql": 1,
  "graphql_field_name": "socialMediaOptions",
  "location": [
    [
      {
        "param": "options_page",
        "operator": "==",
        "value": "acf-options-social-media"
      }
    ]
  ],
  "fields": [
    {
      "name": "facebook_url",
      "type": "url",
      "show_in_graphql": 1,
      "graphql_field_name": "facebookUrl"
    }
  ]
}
```

### GraphQL Query

```graphql
query GetSocialMediaOptions {
  socialMediaOptions {
    facebookUrl
    twitterUrl
    instagramUrl
  }
}
```

**Use Case:** Headless WordPress sites fetch global settings via GraphQL for Next.js footer/header components.

## Programmatic Update

Update options page fields programmatically (e.g., during plugin activation, imports).

### Update Pattern

```php
// Update single field
update_field('facebook_url', 'https://facebook.com/company', 'option');
update_field('copyright_text', '© 2026 Company Name', 'option');

// Update repeater field
$footer_modules = array(
  array(
    'module_title'   => 'Contact',
    'module_content' => '<p>Email: info@example.com</p>'
  ),
  array(
    'module_title'   => 'Hours',
    'module_content' => '<p>Mon-Fri: 9am-5pm</p>'
  )
);
update_field('footer_modules', $footer_modules, 'option');

// Get field value
$current_facebook = get_field('facebook_url', 'option');
```

## Options Page in Plugin vs Theme

Options pages can be registered in plugins or themes depending on persistence needs.

### Plugin Registration (Recommended)

```php
// plugins/site-settings/site-settings.php
add_action('acf/init', 'register_options_pages');

function register_options_pages() {
    if( function_exists('acf_add_options_page') ) {
        acf_add_options_page(array(
            'page_title' => 'Site Settings',
            'menu_title' => 'Site Settings',
            'menu_slug'  => 'site-settings',
        ));
    }
}
```

**Benefits:**
- Survives theme changes
- Can be network-activated on multisite
- Portable across projects

### Theme Registration

```php
// themes/kelsey/functions.php or mu-plugins/thekelsey-custom/thekelsey-custom.php
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page( /* ... */ );
}
```

**Use When:**
- Theme-specific settings (colors, layouts)
- Single-site installations
- Settings tightly coupled to theme

## Admin Menu Position

Control where options pages appear in the WordPress admin menu.

### Position Values

```php
'position' => 2   // Below Dashboard
'position' => 5   // Below Posts
'position' => 10  // Below Media
'position' => 20  // Below Pages
'position' => 25  // Below Comments
'position' => 60  // Below first separator
'position' => 65  // Below Plugins
'position' => 70  // Below Users
'position' => 75  // Below Tools
'position' => 80  // Below Settings
```

**Example:**
```php
acf_add_options_page(array(
    'page_title' => 'Site Settings',
    'menu_title' => 'Site Settings',
    'position'   => 30, // Below Comments, above first separator
));
```

## Common Pitfalls

**Missing Function Check:**
```php
// Bad: Fatal error if ACF deactivated
acf_add_options_page(array(
    'page_title' => 'Settings',
));

// Good: Safe fallback
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => 'Settings',
    ));
}
```

**Wrong get_field() Call:**
```php
// Bad: Missing 'option' parameter (returns post meta instead)
$facebook = get_field('facebook_url');

// Good: Specify 'option' for options page
$facebook = get_field('facebook_url', 'option');
```

**Incorrect Location Rule Value:**
```php
// Bad: Missing "acf-options-" prefix
"value": "social-media"

// Good: Full options page identifier
"value": "acf-options-social-media"
```

**Duplicate menu_slug:**
```php
// Bad: Two options pages with same slug
acf_add_options_page(array('menu_slug' => 'settings'));
acf_add_options_page(array('menu_slug' => 'settings')); // Conflict!

// Good: Unique slugs
acf_add_options_page(array('menu_slug' => 'general-settings'));
acf_add_options_page(array('menu_slug' => 'social-settings'));
```

## Related Patterns

- **ACF JSON Storage:** Options page field groups stored in `acf-json/` like other field groups
- **WPGraphQL Integration:** Options pages expose to GraphQL for headless architectures
- **Repeater Fields:** Options pages support repeaters for lists of global data
- **Multisite:** Network-wide options pages for VIP multisite deployments

**Source Projects:** thekelsey (2 explicit options pages: Social Media, Global Modules), airbnb (8+ options pages across themes for site settings, footer config, theme customization)
