# ACF Location Rules Strategy

---
title: "ACF Location Rules Strategy"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "location-rules", "conditional-display", "post-types", "templates", "blocks"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF location rules determine where field groups appear in WordPress admin, attaching fields to specific post types, templates, blocks, taxonomies, or options pages. Location rule strategy differs dramatically between traditional PHP-based sites (template-centric) and headless sites (block-centric). TheKelsey uses 75% template-based location rules while Airbnb uses 44% block-based rules, reflecting architectural patterns.

**Evidence:** 74 location rules analyzed across 165 field groups (34 in airbnb, 40 in thekelsey). 100% of projects use location rules to scope field visibility appropriately.

## Location Rule Anatomy

Location rules consist of three components: parameter (what to match), operator (comparison type), and value (target). Multiple rules within a group use AND logic (all must match). Multiple rule groups use OR logic (any group matches). This boolean logic enables complex targeting like "Post Type = Event AND Post Template = Featured Event" OR "Post Type = News".

**Basic Location Rule Structure:**

```json
{
    "location": [
        [
            {
                "param": "post_type",
                "operator": "==",
                "value": "event"
            }
        ]
    ]
}
```

**Location Trigger:** Field group appears when editing any post of type "event".

**Multiple Rules (AND Logic):**

```json
{
    "location": [
        [
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            },
            {
                "param": "page_template",
                "operator": "==",
                "value": "template-about.php"
            }
        ]
    ]
}
```

**Location Trigger:** Field group appears only when editing Pages (post_type = page) that use About template (page_template = template-about.php). Both conditions required.

## OR Logic (Multiple Rule Groups)

Multiple rule groups create OR conditions where field groups appear if any group's rules match. Airbnb uses this pattern to show announcement fields on both municipality pages and specific options pages, without duplicating field groups.

**OR Logic Example:**

```json
{
    "location": [
        [
            {
                "param": "post_type",
                "operator": "==",
                "value": "plc_local_pages"
            }
        ],
        [
            {
                "param": "options_page",
                "operator": "==",
                "value": "global_settings"
            }
        ]
    ]
}
```

**Location Trigger:** Field group appears when editing Local Pages posts OR when editing Global Settings options page. Either condition triggers display.

## Template-Based Location Rules (TheKelsey Pattern)

TheKelsey attaches 75% of field groups to page or post templates (30 of 40 rules use `post_template` or `page_template` parameters). This pattern suits traditional PHP-rendered WordPress sites where templates define page structure and require template-specific data. Sage framework with Blade templates drives this approach.

**Template Location Pattern:**

```json
{
    "key": "group_5f91b18180b23",
    "title": "Text and Aside",
    "fields": [...],
    "location": [
        [
            {
                "param": "post_template",
                "operator": "==",
                "value": "views/template-about.blade.php"
            }
        ]
    ]
}
```

**Use Case:** About page template needs specific fields (intro text, aside image, aside text). Fields only appear when editing posts using this template.

**Template Parameter Options:**
- `post_template` - Match post templates (custom post types)
- `page_template` - Match page templates (page post type)
- Value: Relative path from theme root (`views/template-about.blade.php`)

**TheKelsey Template Distribution:**
- `post_template`: 20 rules (50%)
- `page_template`: 10 rules (25%)
- `post_type`: 5 rules (13%)
- `options_page`: 4 rules (10%)
- `page`: 1 rule (3%)

## Block-Based Location Rules (Airbnb Pattern)

Airbnb attaches 44% of field groups to Gutenberg blocks (15 of 34 rules use `param: "block"`). This pattern enables ACF fields to power custom blocks in headless WordPress, where blocks provide structured data for GraphQL consumption. Each custom block has dedicated field group defining its data schema.

**Block Location Pattern:**

```json
{
    "key": "group_680ad6fe615b8",
    "title": "Logo Cloud Block",
    "fields": [...],
    "location": [
        [
            {
                "param": "block",
                "operator": "==",
                "value": "create-block/logo-cloud-block"
            }
        ]
    ]
}
```

**Use Case:** Logo Cloud block renders list of client logos. Field group defines `logos` repeater (logo image + optional link). Fields appear when editing Logo Cloud block in Gutenberg editor.

**Block Value Format:** `{namespace}/{block-name}` matching block.json registration.

**Airbnb Block Distribution:**
- `block`: 15 rules (44%)
- `options_page`: 8 rules (24%)
- `post_type`: 6 rules (18%)
- `page_template`: 3 rules (9%)
- `taxonomy`: 1 rule (3%)
- `page_type`: 1 rule (3%)

**Pattern Insight:** Headless sites prioritize blocks as structured content units, making block-based location rules dominant.

## Post Type Location Rules

Post type rules attach field groups to all posts of a given type, regardless of template or other conditions. Both projects use post type rules for custom post types requiring consistent metadata (events, team members, projects).

**Post Type Pattern:**

```json
{
    "location": [
        [
            {
                "param": "post_type",
                "operator": "==",
                "value": "kelsey_event"
            }
        ]
    ]
}
```

**Use Case:** Event posts need event_date, funraise_form_id, and event_color fields. Fields appear on all event posts.

**Common Post Types:**
- `post` - Standard blog posts
- `page` - WordPress pages
- `{custom_post_type}` - Registered CPTs (events, team, projects, etc.)

**When to Use:**
- Fields required for all posts of a type
- Core CPT attributes (event date, project status, team member role)
- No template or block variations needed

## Options Page Location Rules

Options pages provide global settings accessible across the site. Both projects use options page rules for site-wide configurations like social media links, API keys, and global modules. Options pages require `acf_add_options_page()` function registration before field groups can target them.

**Options Page Pattern:**

```php
// Register options page
if( function_exists('acf_add_options_page') ) {
    acf_add_options_page(array(
        'page_title' => __('Social Media'),
        'menu_title' => __('Social Media'),
        'menu_slug' => 'social-media',
        'icon_url' => 'dashicons-networking'
    ));
}
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

**Access in PHP:**

```php
$facebook = get_field('facebook_url', 'option');  // Note: 'option' parameter
```

**Common Options Pages:**
- Social Media (social links)
- Site Settings (analytics IDs, feature flags)
- Global Modules (reusable content blocks)
- API Configuration (service credentials)

## Taxonomy Location Rules

Taxonomy location rules attach fields to term edit screens, adding metadata to categories, tags, or custom taxonomies. Airbnb uses this for municipality taxonomy, storing per-municipality override data. TheKelsey does not use taxonomy location rules.

**Taxonomy Location Pattern:**

```json
{
    "location": [
        [
            {
                "param": "taxonomy",
                "operator": "==",
                "value": "municipality"
            }
        ]
    ]
}
```

**Use Case:** Municipality terms need override fields for stats, announcements, and inheritance settings.

**When to Use:**
- Term-specific metadata (featured image for category)
- Taxonomy-level configuration (tax rate per region)
- Term relationships (parent term overrides)

**Limitation:** Can't combine with post type rules (taxonomy rules match term edit screens only, not post edit screens with taxonomy selected).

## NOT Operator for Exclusions

Location rules support `!=` operator to exclude specific contexts. This enables "show everywhere except X" patterns without enumerating all valid locations. Neither analyzed project uses NOT operator extensively, preferring explicit positive rules.

**Exclusion Pattern:**

```json
{
    "location": [
        [
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            },
            {
                "param": "page_template",
                "operator": "!=",
                "value": "template-home.php"
            }
        ]
    ]
}
```

**Location Trigger:** Field group appears on all Pages except homepage template.

**Use Case:** Global page fields not relevant to homepage (e.g., sidebar config).

**Alternative:** Create separate field groups for specific templates (more explicit, easier to understand).

## Page-Specific Location Rules

Page-specific rules target individual pages by ID, useful for site-unique pages like homepage or contact page requiring custom fields. TheKelsey uses one instance (`param: "page"`) for page-specific customization.

**Page-Specific Pattern:**

```json
{
    "location": [
        [
            {
                "param": "page",
                "operator": "==",
                "value": "42"  // Page ID
            }
        ]
    ]
}
```

**When to Use:**
- One-off pages with unique requirements (homepage)
- Landing pages with specialized fields
- Contact page with form configuration

**Limitation:** Page ID is environment-specific (different IDs across dev/staging/production). Prefer template-based rules for portability.

## User Role Location Rules

Location rules can target user role edit screens for user metadata fields. Neither analyzed project uses this pattern, but it's common for membership sites storing user profile data.

**User Role Pattern:**

```json
{
    "location": [
        [
            {
                "param": "user_role",
                "operator": "==",
                "value": "subscriber"
            }
        ]
    ]
}
```

**Use Case:** Subscriber users need membership level, renewal date, and subscription ID fields.

**Access in PHP:**

```php
$membership = get_field('membership_level', 'user_' . $user_id);
```

## Menu Location Rules

Menu location rules attach fields to nav menu items for custom link attributes (icon, badge, external link indicator). Neither analyzed project uses menu location rules, as nav menus typically use static configuration.

**Menu Pattern:**

```json
{
    "location": [
        [
            {
                "param": "nav_menu_item",
                "operator": "==",
                "value": "all"
            }
        ]
    ]
}
```

**Use Case:** Add icon field to every menu item for visual enhancement.

**Access in Walker Class:**

```php
$icon = get_field('menu_icon', $item->ID);
```

## Location Rule Performance

Each location rule adds conditional logic checking during admin page load. Complex rule sets (10+ rule groups with multiple AND conditions) can slow admin. Keep location rules simple. Prefer specific rules over broad rules with exclusions.

**Performance Guidelines:**
- 1-3 rule groups: Negligible performance impact
- 4-10 rule groups: Acceptable for complex requirements
- 10+ rule groups: Refactor into multiple field groups

**Anti-Pattern:**

```json
{
    "location": [
        // 20 rule groups checking every possible location
        // SLOW - shows on most content types
    ]
}
```

**Better Approach:** Split into focused field groups per content type.

## Architecture-Specific Strategy

Traditional PHP WordPress sites use template-based location rules matching PHP file rendering. Headless WordPress sites use block-based location rules providing structured data for API consumption. Options page rules are universal across architectures for global settings.

**Traditional (TheKelsey):**
- 75% template-based (`post_template`, `page_template`)
- Templates define page structure
- Fields provide template-specific data
- Sage/Blade framework integration

**Headless (Airbnb):**
- 44% block-based (`param: "block"`)
- Blocks are content units
- Fields power block schemas
- GraphQL exposes block data

**Shared:**
- Options pages for global settings (24% airbnb, 10% thekelsey)
- Post type rules for CPT metadata (18% airbnb, 13% thekelsey)

## Common Pitfalls

Overly broad location rules cause fields to appear on irrelevant edit screens, confusing editors. Page-specific rules (by ID) break across environments. Missing location rules hide field groups entirely (zero locations = never visible). Complex OR logic with 10+ groups becomes unmaintainable.

**Anti-Patterns:**

```json
// ❌ Too broad - shows on all posts
{
    "location": [[{ "param": "post_type", "operator": "==", "value": "post" }]]
}

// ❌ Environment-specific (page ID)
{
    "location": [[{ "param": "page", "operator": "==", "value": "42" }]]
}

// ❌ No location rules (never visible)
{
    "location": []
}

// ❌ Overcomplicated (15 OR groups)
{
    "location": [
        [/* group 1 */],
        [/* group 2 */],
        // ... 13 more groups
    ]
}
```

## Location Rule Testing

After defining location rules, verify field group visibility by navigating to target admin screens (post edit, template select, block insert). ACF Debug Mode (`WP_DEBUG` + `WP_DEBUG_LOG`) logs location rule evaluation, helping diagnose visibility issues.

**Testing Checklist:**
1. ✅ Field group appears on intended screen
2. ✅ Field group does NOT appear on unintended screens
3. ✅ Multiple rule groups (OR logic) work correctly
4. ✅ AND logic within groups works correctly
5. ✅ Values match actual post type/template/block names

**Debug Logging:**

```php
// wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);

// Location rule evaluation logged to wp-content/debug.log
```

## Related Patterns

- **ACF Field Groups** (containers for fields with location rules)
- **ACF Blocks** (custom Gutenberg blocks with ACF fields)
- **ACF Options Pages** (global settings with ACF fields)
- **Custom Post Types** (CPTs targeted by location rules)
- **Page Templates** (traditional PHP templates with ACF fields)

## References

- Airbnb ACF JSON: `plugins/airbnb-policy-blocks/acf-json/group_*.json` (34 location rules analyzed)
- TheKelsey ACF JSON: `mu-plugins/thekelsey-custom/acf-json/group_*.json` (40 location rules analyzed)
- ACF Documentation: [Location Rules](https://www.advancedcustomfields.com/resources/custom-location-rules/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 5: Location Rules)
