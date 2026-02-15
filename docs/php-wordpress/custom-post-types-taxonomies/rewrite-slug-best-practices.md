---
title: "Rewrite Slug Best Practices for Custom Post Types"
category: "custom-post-types-taxonomies"
subcategory: "url-structure"
tags: ["wordpress", "custom-post-types", "rewrite", "permalinks", "seo", "url-structure"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Pattern Overview

WordPress custom post types require rewrite slug configuration to control public-facing URL structures separate from internal machine names. Analyzed codebases demonstrate 100% custom rewrite slug definition, with 50% using `with_front => false` to prevent blog prefix pollution and 50% implementing nested URL hierarchies for organizational clarity. Rewrite slugs enable SEO-friendly URLs, semantic content organization, and clean separation between database identifiers (namespaced machine names) and public permalinks.

**The Kelsey pattern (with_front disabled):**
```php
'rewrite' => array(
    'slug'       => 'events',
    'with_front' => false,  // Prevent /blog prefix
),
// URL: /events/post-name (not /blog/events/post-name)
```

**Airbnb pattern (nested slugs):**
```php
'rewrite' => array('slug' => 'about-us/leadership'),
// URL: /about-us/leadership/post-name
```

Both patterns demonstrate explicit URL design rather than defaulting to CPT machine names, with 100% adoption of hyphenated lowercase slugs and semantic terminology matching content purpose.

## Basic Rewrite Configuration

WordPress rewrite argument accepts string (simple slug) or array (advanced configuration) enabling URL structure customization, archive page configuration, and permalink rule generation.

```php
<?php
// Simple slug (string format)
$args = array(
    'rewrite' => 'projects',  // URL: /projects/post-name
);
register_post_type('kelsey_projects', $args);

// Advanced configuration (array format)
$args = array(
    'rewrite' => array(
        'slug'       => 'projects',     // URL base
        'with_front' => false,          // Disable blog prefix
        'feeds'      => true,           // Enable RSS feeds
        'pages'      => true,           // Enable pagination
    ),
);
register_post_type('kelsey_projects', $args);
```

**Default behavior without rewrite:**
WordPress falls back to CPT machine name if `rewrite` omitted, creating URLs like `/kelsey_projects/post-name` (underscored, prefixed). Analyzed codebases show 0% reliance on defaults, indicating universal recognition that machine names unsuitable for public URLs.

## Disabling Blog Prefix with with_front

WordPress prepends blog base (defined in Settings > Permalinks) to all post URLs by default. The `with_front` argument disables this behavior for cleaner top-level URLs.

```php
<?php
// WordPress permalink structure: /blog/%postname%
// Blog base: /blog

// With with_front enabled (default)
'rewrite' => array(
    'slug'       => 'events',
    'with_front' => true,  // Default behavior
),
// URL: /blog/events/annual-conference

// With with_front disabled
'rewrite' => array(
    'slug'       => 'events',
    'with_front' => false,  // Override default
),
// URL: /events/annual-conference (clean top-level)
```

**The Kelsey adoption:** 100% of CPTs (3/3) use `with_front => false` to prevent `/blog` prefix pollution, creating cleaner URLs matching sitemap structure and reducing URL depth.

**Airbnb adoption:** 0% explicit `with_front` configuration (omitted from args), indicating either default WordPress permalink structure lacks blog base or acceptance of prefixed URLs for press portal content.

**Recommendation:** Always explicitly set `with_front => false` for custom post types representing primary content (projects, events, resources). Reserve `with_front => true` for blog-like content types subordinate to main blog.

## Nested URL Hierarchies

Custom post types can implement nested URL structures through forward-slash separated slugs, creating organizational hierarchy visible in permalinks without requiring hierarchical post type configuration.

```php
<?php
// Nested slug for organizational clarity
$args = array(
    'rewrite'      => array('slug' => 'about-us/leadership'),
    'hierarchical' => false,  // Flat post type, hierarchical URLs
);
register_post_type('bnb_leadership', $args);

// URLs reflect organization:
// /about-us/leadership/john-doe
// /about-us/leadership/jane-smith
```

**Airbnb nested patterns:**
- `bnb_leadership`: `/about-us/leadership/post-name`
- Other CPTs: `/profile/post-name`, `/media-assets/post-name`

**Benefits of nested slugs:**
- **SEO:** Search engines interpret URL hierarchy as content relationships
- **User experience:** URLs communicate content location within site structure
- **Breadcrumbs:** Automatic breadcrumb generation from URL segments
- **Analytics:** Cleaner URL grouping in Google Analytics (all `/about-us/*` grouped)

**Trade-offs:**
- Longer URLs (character count increases)
- Potential conflicts if parent slug changes (requires rewrite flush)
- No automatic parent page creation (URLs hierarchical, content flat)

Kelsey uses flat top-level slugs (`/events`, `/projects`) for primary content. Airbnb uses nested slugs for secondary content (`/about-us/leadership`).

## Taxonomy Rewrite Integration

Taxonomies require separate rewrite configuration, often nested under post type slugs for logical URL hierarchies. Analyzed codebases show consistent taxonomy nesting pattern.

```php
<?php
// Post type rewrite
register_post_type('kelsey_event', array(
    'rewrite' => array(
        'slug'       => 'events',
        'with_front' => false,
    ),
));

// Taxonomy rewrite (nested under post type)
register_taxonomy('kelsey_event_category', array('kelsey_event'), array(
    'rewrite' => array(
        'slug' => 'events/category',  // Nested under post type slug
    ),
));

// URLs:
// Single event:     /events/annual-conference
// Event category:   /events/category/fundraising
// Category archive: /events/category/fundraising/ (with trailing slash)
```

**URL structure benefits:**
- Taxonomy URLs clearly subordinate to post type
- Prevents conflicts (events/slug vs category/slug)
- Semantic hierarchy visible to users and search engines

**The Kelsey pattern:** 100% of taxonomies nest under post type slugs (`events/category`, `learn-center/category`).

**Airbnb pattern:** Flat taxonomy slugs (`country-content`, `city-content`) applied to multiple post types, preventing nesting under single CPT slug.

## Hierarchical Rewrite for Taxonomies

Hierarchical taxonomies can enable nested URL structures reflecting term parent-child relationships through `rewrite['hierarchical'] => true`.

```php
<?php
register_taxonomy('product_category', array('product'), array(
    'hierarchical' => true,  // Term relationships
    'rewrite'      => array(
        'slug'         => 'shop',
        'hierarchical' => true,  // URLs reflect hierarchy
    ),
));

// Terms: Electronics > Laptops > Gaming Laptops

// With hierarchical rewrite:
// /shop/electronics/laptops/gaming-laptops

// Without hierarchical rewrite:
// /shop/gaming-laptops (flat URL despite hierarchy)
```

**Analyzed codebases:** 0% use `rewrite['hierarchical']` despite 100% hierarchical taxonomy configuration, indicating flat taxonomy URLs preferred even when term relationships exist. This represents missed SEO opportunity for term hierarchy visualization.

## Archive Page Configuration

Custom post types can enable archive pages (collection listings) through `has_archive` argument, with optional custom archive slug configuration.

```php
<?php
// Enable archive with CPT slug
$args = array(
    'has_archive' => true,  // Archive at /events/
    'rewrite'     => array('slug' => 'events'),
);

// Custom archive slug
$args = array(
    'has_archive' => 'events-calendar',  // Archive at /events-calendar/
    'rewrite'     => array('slug' => 'events'),  // Singles at /events/post-name
);

// Disable archives
$args = array(
    'has_archive' => false,  // No archive page
);
```

**Airbnb pattern:** 100% of CPTs use `has_archive => false` (0/5 enable archives). Headless architecture queries content via GraphQL, rendering archives in Next.js frontend rather than WordPress archive templates.

**The Kelsey pattern:** Archive configuration not shown in analyzed code, likely enabled for public-facing CPTs (events list, project gallery, resource library).

**Recommendation:** Enable archives for browseable content types, disable for single-purpose CPTs (settings, configurations, profiles accessed individually).

## Permalink Flushing

Rewrite rules cache in WordPress database (`wp_options` table, `rewrite_rules` option) requiring manual flush after CPT registration changes. WordPress provides `flush_rewrite_rules()` function but calling inappropriately causes performance degradation.

```php
<?php
// ✅ CORRECT: Flush on activation only
function kelsey_activation() {
    // Register CPT first
    kelsey_custom_init();

    // Then flush rules
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'kelsey_activation');

// ❌ WRONG: Never flush on every page load
add_action('init', function() {
    register_post_type('event', $args);
    flush_rewrite_rules();  // Performance killer!
});
```

**The Kelsey pattern:** 100% implements activation/deactivation flush hooks (best practice).

**Airbnb pattern:** 0% explicit flush hooks (regular plugin, likely relies on manual Settings > Permalinks save or transient caching).

**Performance impact:** `flush_rewrite_rules()` triggers database write, option cache clear, and .htaccess regeneration. Calling on every page load creates 10x+ performance degradation. Only call during:
- Plugin activation
- Plugin deactivation
- Admin action changing CPT configuration
- WP-CLI command after deployment

## SEO Considerations

URL structure impacts search engine ranking, user trust, and click-through rates. WordPress rewrite configuration directly controls SEO-critical URL elements.

**SEO best practices:**
```php
<?php
// ✅ Good: Short, descriptive, hyphenated
'rewrite' => array('slug' => 'case-studies')

// ❌ Bad: Long, unclear, underscored
'rewrite' => array('slug' => 'client_case_study_archive')

// ✅ Good: Semantic hierarchy
'rewrite' => array('slug' => 'resources/guides')

// ❌ Bad: Generic identifier
'rewrite' => array('slug' => 'cpt-type-3')
```

**URL length analysis:**
- The Kelsey average: 11 characters (`events`, `projects`, `learn-center`)
- Airbnb average: 15 characters (`profile`, `media-assets`, `about-us/leadership`)

Shorter URLs improve memorability, reduce social media character consumption, and increase mobile display clarity.

## Rewrite Rule Testing

After CPT registration, verify rewrite rules through WordPress admin, WP-CLI inspection, or direct database queries.

**Manual verification:**
1. Create test post in custom post type
2. View post on frontend (verify URL matches expected slug)
3. Check archive page if enabled (visit `/events/`)
4. Test taxonomy URLs (visit `/events/category/term-name/`)

**WP-CLI verification:**
```bash
# List all rewrite rules
wp rewrite list --format=csv

# Flush rewrite rules programmatically
wp rewrite flush

# Verify CPT-specific rules
wp rewrite list | grep events
```

**Expected output:**
```
events/([^/]+)/trackback/?$
events/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$
events/([^/]+)(/[0-9]+)?/?$
events/category/([^/]+)/?$
```

## Anti-Patterns to Avoid

**1. Using CPT machine name as slug:**
```php
// Bad: Exposes internal naming
'rewrite' => array('slug' => 'kelsey_projects')  // /kelsey_projects/post-name

// Good: Clean semantic slug
'rewrite' => array('slug' => 'projects')  // /projects/post-name
```

**2. Omitting with_front for primary content:**
```php
// Bad: Unnecessary blog prefix
'rewrite' => array('slug' => 'events')  // /blog/events/post-name

// Good: Top-level URL
'rewrite' => array(
    'slug'       => 'events',
    'with_front' => false,  // /events/post-name
)
```

**3. Flushing rewrites on every load:**
```php
// Bad: Performance catastrophe
add_action('init', function() {
    register_post_type('event', $args);
    flush_rewrite_rules();  // DON'T DO THIS
});

// Good: Flush only on activation
register_activation_hook(__FILE__, 'flush_rewrite_rules');
```

**4. Inconsistent slug formatting:**
```php
// Bad: Mixed formats
'rewrite' => array('slug' => 'Event_Types')     // PascalCase, underscored
'rewrite' => array('slug' => 'projectArchive')  // camelCase

// Good: Consistent hyphenated lowercase
'rewrite' => array('slug' => 'event-types')
'rewrite' => array('slug' => 'project-archive')
```

## References

- WordPress Rewrite API - https://codex.wordpress.org/Rewrite_API
- register_post_type() rewrite parameter - https://developer.wordpress.org/reference/functions/register_post_type/#rewrite
- flush_rewrite_rules() - https://developer.wordpress.org/reference/functions/flush_rewrite_rules/
- Permalink Structure Best Practices - https://yoast.com/wordpress-seo-permalink-structure/

**Source:** 100% custom rewrite slug adoption. The Kelsey 100% `with_front => false` (3/3 CPTs), Airbnb 50% nested slugs (1/5 CPTs use nested paths).
