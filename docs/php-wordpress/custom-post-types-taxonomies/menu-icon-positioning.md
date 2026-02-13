---
title: "Menu Icon and Positioning Patterns"
category: "custom-post-types-taxonomies"
subcategory: "admin-ui"
tags: ["wordpress", "dashicons", "menu-position", "admin-menu", "ux"]
stack: "php-wp"
priority: "low"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-12"
---

## Pattern Overview

WordPress custom post types require menu icon and positioning configuration for admin sidebar navigation. Analyzed codebases demonstrate 100% Dashicons adoption with divergent positioning strategies: 50% explicit menu_position values (The Kelsey) for precise ordering versus 50% default positioning (Airbnb) accepting WordPress automatic placement. Menu icons improve visual scanning and content type recognition but require unique icon-per-CPT assignment to maximize UX benefits.

**The Kelsey explicit positioning:**
```php
'menu_position' => 5,  // After Posts (5), before Media (10)
'menu_icon'     => 'dashicons-building',
```

**Airbnb default positioning:**
```php
'menu_position' => null,  // WordPress determines placement
'menu_icon'     => 'dashicons-groups',
```

**Adoption:** 100% Dashicons, 50% explicit positioning, 0% unique icons per CPT (Airbnb reuses `dashicons-groups` for 80% of CPTs).

## Dashicons Integration

WordPress ships with Dashicons icon font providing 300+ admin UI icons accessible via `menu_icon` argument. Custom post types default to generic pushpin icon if `menu_icon` omitted.

```php
<?php
$args = array(
    'menu_icon' => 'dashicons-tickets-alt',  // Icon CSS class
);

// WordPress menu positions:
// 5  - Posts
// 10 - Media
// 15 - Links
// 20 - Pages
// 25 - Comments
```

**Complete Dashicons references:** https://developer.wordpress.org/resource/dashicons/

**Analyzed icon usage:**
```php
// The Kelsey (unique icons)
'dashicons-building'        // Projects
'dashicons-tickets-alt'     // Events
'dashicons-welcome-learn-more'  // Resources

// Airbnb (repeated icon - UX issue)
'dashicons-groups'          // Profile, Leadership, Gallery, Slider (4 CPTs)
'dashicons-format-gallery'  // Media (1 CPT)
```

**Custom SVG icons** (not observed in analyzed codebases):
```php
'menu_icon' => 'data:image/svg+xml;base64,' . base64_encode($svg),
```

## Menu Position Strategy

WordPress assigns menu positions numerically (5, 10, 15, 20, 25, ...). Custom values between increments (e.g., 6, 7, 8) enable precise insertion.

**The Kelsey explicit positioning:**
```php
register_post_type('kelsey_projects', array(
    'menu_position' => 5,  // After Posts
));

register_post_type('kelsey_event', array(
    'menu_position' => 6,  // After Projects
));

register_post_type('kelsey_resource', array(
    'menu_position' => 7,  // After Events
));
```

**Result:** Projects → Events → Learn Center (sequential ordering).

**Airbnb null positioning:**
```php
register_post_type('bnb_profile', array(
    'menu_position' => null,  // WordPress default placement
));
```

**Result:** WordPress places CPT after Comments (position 25+) in registration order.

**Adoption:** 50% explicit positioning (The Kelsey places primary content near Posts for quick access), 50% default positioning (Airbnb press portal CPTs less frequently accessed).

## Recommendations

1. **Unique icons:** Assign distinct Dashicons per CPT (avoid Airbnb pattern of reusing `dashicons-groups`)
2. **Explicit positioning:** Define `menu_position` for primary content CPTs
3. **Sequential numbering:** Use consecutive numbers (5, 6, 7) for related CPTs
4. **Icon semantics:** Match icon visual metaphor to content type (building=projects, ticket=events)

## References

- Dashicons - https://developer.wordpress.org/resource/dashicons/
- register_post_type() menu_icon - https://developer.wordpress.org/reference/functions/register_post_type/#menu-icon

**Source:** 100% Dashicons adoption. 50% explicit positioning (The Kelsey). Airbnb icon reuse represents UX anti-pattern (4/5 CPTs identical icons).
