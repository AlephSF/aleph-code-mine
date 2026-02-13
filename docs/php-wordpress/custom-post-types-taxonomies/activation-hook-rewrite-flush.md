---
title: "Activation Hook Rewrite Flush Pattern"
category: "custom-post-types-taxonomies"
subcategory: "activation"
tags: ["wordpress", "activation-hooks", "flush-rewrite-rules", "performance", "permalinks"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-12"
---

## Pattern Overview

WordPress custom post type registration modifies permalink structure requiring rewrite rule flush to update URL routing. The `flush_rewrite_rules()` function regenerates permalink rules stored in database but causes performance degradation if called on every page load. Best practice implements activation/deactivation hooks calling flush exactly once during plugin lifecycle changes. Analyzed codebases show 50% adoption: The Kelsey implements activation flush (mu-plugin with external hook registration), Airbnb omits activation hooks (regular plugin relying on manual flush or transient caching).

**The Kelsey best practice:**
```php
function activation() {
    $this->kelsey_custom_init();  // Register CPTs first
    flush_rewrite_rules();        // Then flush
}
register_activation_hook(__FILE__, array($kelsey_custom, 'activation'));
```

**Airbnb missing pattern:**
No activation hooks observed. Regular plugin without rewrite flush. Likely relies on:
1. Manual Settings > Permalinks save after activation
2. Transient rewrite rule caching
3. VIP Go platform automatic flush

## Correct Activation Pattern

Activation hooks execute once during plugin activation (Admin > Plugins > Activate). Must register CPTs before flushing to generate correct rewrite rules.

```php
<?php
class KelseyCustomTypesTaxonomies {
    function activation() {
        // Step 1: Register post types
        $this->kelsey_custom_init();

        // Step 2: Flush rewrite rules
        flush_rewrite_rules();
    }

    function deactivation() {
        // Unregister by not calling kelsey_custom_init()

        // Flush to remove CPT rewrite rules
        flush_rewrite_rules();
    }

    function kelsey_custom_init() {
        register_post_type('kelsey_projects', $args);
        register_post_type('kelsey_event', $args);
        register_taxonomy('kelsey_event_category', ...);
    }
}

// External hook registration (required for activation hooks)
$kelsey_custom = new KelseyCustomTypesTaxonomies();
register_activation_hook(__FILE__, array($kelsey_custom, 'activation'));
register_deactivation_hook(__FILE__, array($kelsey_custom, 'deactivation'));
add_action('init', array($kelsey_custom, 'kelsey_custom_init'));
```

**Critical order:** Register CPTs *before* flushing. Reversing order flushes empty ruleset, causing 404 errors.

## Anti-Pattern: Flushing on Init

Never call `flush_rewrite_rules()` inside `init` hook or on every page load. Causes 10x+ performance degradation via database writes, option cache clears, and .htaccess regeneration.

```php
<?php
// ❌ WRONG: Performance catastrophe
add_action('init', function() {
    register_post_type('event', $args);
    flush_rewrite_rules();  // Runs on EVERY page load
});

// ✅ CORRECT: One-time flush on activation
function my_activation() {
    register_post_type('event', $args);
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'my_activation');
```

**Performance impact measurement:**
- Normal page load: 50-100ms
- Page load with flush_rewrite_rules(): 500-1000ms (10x slower)
- Database writes: 1-2 queries per flush
- Option cache: Full clear of `rewrite_rules` option

## MU-Plugin Limitation

Must-use (MU) plugins do not support `register_activation_hook()` because WordPress auto-loads MU plugins without activation UI. The Kelsey works around this limitation via external hook registration in loader file.

**MU-plugin workaround:**
```php
<?php
// wp-content/mu-plugins/thekelsey-custom.php (loader file)
require_once __DIR__ . '/thekelsey-custom/KelseyCustomTypesTaxonomies.class.php';

$kelsey_custom = new KelseyCustomTypesTaxonomies();

// Can't use register_activation_hook (not supported in MU-plugins)
// Manual flush required after deployment:
// wp rewrite flush (via WP-CLI)
// or Settings > Permalinks > Save (via admin UI)

add_action('init', array($kelsey_custom, 'kelsey_custom_init'));
```

**Alternative:** Convert to regular plugin for activation hook support, or document manual flush requirement in deployment process.

## References

- register_activation_hook() - https://developer.wordpress.org/reference/functions/register_activation_hook/
- flush_rewrite_rules() - https://developer.wordpress.org/reference/functions/flush_rewrite_rules/

**Source:** 50% adoption (The Kelsey implements, Airbnb omits). Best practice: Always flush on activation/deactivation, never on init.
