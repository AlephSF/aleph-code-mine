# ACF Group Fields for Nested Organization

---
title: "ACF Group Fields for Nested Organization"
category: "wordpress-acf"
subcategory: "field-organization"
tags: ["acf", "group-fields", "nesting", "organization", "data-structure"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Group fields organize related sub-fields under a parent namespace, creating logical data structures and reducing field list clutter. All analyzed projects use Group fields extensively (55 instances across 165 field groups), treating them as the primary organizational mechanism for complex data models. Groups provide both UI organization in WordPress admin and structured data access in code.

**Evidence:** 27 group fields in airbnb (16% of 166 fields), 28 group fields in thekelsey (12% of 227 fields). 100% confidence pattern across both traditional and headless architectures.

## Basic Group Field Structure

Group fields contain sub-fields that logically belong together, such as address components, social media links, or metric datasets. The group field itself has a name that acts as a namespace, and sub-fields are accessed via array syntax in PHP or nested objects in GraphQL. WordPress admin displays groups as collapsible sections.

**Simple Group Example:**

```json
{
    "key": "field_social_group",
    "label": "Social Media Links",
    "name": "social_links",
    "type": "group",
    "sub_fields": [
        {
            "key": "field_facebook",
            "label": "Facebook URL",
            "name": "facebook_url",
            "type": "url"
        },
        {
            "key": "field_twitter",
            "label": "Twitter URL",
            "name": "twitter_url",
            "type": "url"
        },
        {
            "key": "field_instagram",
            "label": "Instagram URL",
            "name": "instagram_url",
            "type": "url"
        }
    ]
}
```

## PHP Access Patterns

ACF provides two syntax options for accessing grouped fields: array syntax (explicit) and underscore syntax (ACF magic). Array syntax returns the entire group as an associative array, suitable for templates that iterate over group data. Underscore syntax retrieves individual sub-fields directly via dot notation converted to underscores.

**Array Syntax (Explicit):**

```php
$social = get_field('social_links');
echo $social['facebook_url'];
echo $social['twitter_url'];
echo $social['instagram_url'];

// Null-safe access
if ($social && isset($social['facebook_url'])) {
    echo '<a href="' . esc_url($social['facebook_url']) . '">Facebook</a>';
}
```

**Underscore Syntax (ACF Magic):**

```php
$facebook = get_field('social_links_facebook_url');
$twitter = get_field('social_links_twitter_url');
$instagram = get_field('social_links_instagram_url');

// Equivalent to array syntax but more verbose for multiple fields
```

**Recommendation:** Use array syntax when accessing multiple sub-fields from the same group (fewer database queries, cleaner code). Use underscore syntax for one-off sub-field access.

## Nested Groups (Two Levels Deep)

Groups can contain other groups, creating hierarchical data structures up to reasonable nesting depths. Airbnb's `metrics` group demonstrates two-level nesting: `metrics` → `economic_impact` → `gdp_contribution`. This pattern organizes complex statistical data with logical categorization.

**Two-Level Nesting Example:**

```json
{
    "name": "metrics",
    "type": "group",
    "sub_fields": [
        {
            "name": "economic_impact",
            "type": "group",
            "sub_fields": [
                { "name": "gdp_contribution", "type": "text" },
                { "name": "hide", "type": "true_false" }
            ]
        }
    ]
}
```

**PHP Access:**

```php
$metrics = get_field('metrics');
$gdp = $metrics['economic_impact']['gdp_contribution'];
```

**Best Practice:** Limit nesting to 2 levels for code readability and manageable complexity. Deeper nesting indicates over-engineering.

## GraphQL Access with Nested Groups

WPGraphQL represents ACF groups as nested objects matching JSON structure, creating clean hierarchical GraphQL queries. Airbnb's camelCase `graphql_field_name` properties apply at every nesting level, transforming snake_case PHP structure into idiomatic GraphQL.

**GraphQL Query (Nested Groups):**

```graphql
query GetPostMetrics {
  post(id: "123") {
    statBlock {
      metrics {
        economicImpact {
          gdpContribution
          hide
          applyToDescendants
        }
        hostMetrics {
          hostingNotPrimaryOccupation
          hide
        }
      }
    }
  }
}
```

**GraphQL Response:**

```json
{
  "data": {
    "post": {
      "statBlock": {
        "metrics": {
          "economicImpact": {
            "gdpContribution": "85B",
            "hide": false,
            "applyToDescendants": true
          },
          "hostMetrics": {
            "hostingNotPrimaryOccupation": "87%",
            "hide": false
          }
        }
      }
    }
  }
}
```

**Advantage:** GraphQL clients receive strongly-typed nested objects matching expected data structures, no flattening required.

## Group Fields for Address Data

Address data is the canonical use case for group fields, bundling street, city, state, and zip into a single logical unit. While neither analyzed project demonstrates this pattern explicitly, it represents best-practice usage common across WordPress projects.

**Address Group Pattern:**

```json
{
    "name": "location",
    "type": "group",
    "sub_fields": [
        { "name": "street_address", "type": "text" },
        { "name": "city", "type": "text" },
        { "name": "state", "type": "text" },
        { "name": "zip_code", "type": "text" },
        { "name": "country", "type": "text", "default_value": "USA" }
    ]
}
```

**PHP Access:**

```php
$location = get_field('location');
echo $location['street_address'] . '<br>';
echo $location['city'] . ', ' . $location['state'] . ' ' . $location['zip_code'];
```

**Why Group:** Address components are meaningless in isolation. Grouping prevents 5 separate meta queries and clarifies relationships.

## Groups vs Repeaters: When to Use Which

Group fields organize fixed sets of related fields (one instance). Repeater fields store multiple instances of the same field structure (dynamic list). Use groups for singular concepts (address, social links, hero section). Use repeaters for collections (team members, testimonials, logos).

**Group (Singular Concept):**

```json
{
    "name": "hero_section",
    "type": "group",
    "sub_fields": [
        { "name": "title", "type": "text" },
        { "name": "subtitle", "type": "text" },
        { "name": "background_image", "type": "image" }
    ]
}
```

**Repeater (Collection):**

```json
{
    "name": "team_members",
    "type": "repeater",
    "sub_fields": [
        { "name": "name", "type": "text" },
        { "name": "title", "type": "text" },
        { "name": "photo", "type": "image" }
    ]
}
```

**Decision Matrix:**

- **One instance, multiple fields** → Group
- **Multiple instances, same structure** → Repeater
- **One instance, variable structure** → Flexible Content
- **Multiple instances, variable structure** → Repeater of Flexible Content

## Group Layout Options

ACF groups support three layout modes: Block (default, stacked fields), Table (compact inline fields), and Row (horizontal single row). Block layout dominates analyzed projects (95%+) for maximum editor clarity. Table and Row layouts suit specialized use cases like compact settings panels.

**Block Layout (Default):**

```json
{
    "name": "social_links",
    "type": "group",
    "layout": "block",  // Each field on separate row
    "sub_fields": [...]
}
```

**Table Layout (Compact):**

```json
{
    "name": "dimensions",
    "type": "group",
    "layout": "table",  // Fields in table columns
    "sub_fields": [
        { "name": "width", "type": "number" },
        { "name": "height", "type": "number" }
    ]
}
```

**Row Layout (Single Line):**

```json
{
    "name": "coordinates",
    "type": "group",
    "layout": "row",  // Fields in single horizontal row
    "sub_fields": [
        { "name": "latitude", "type": "number" },
        { "name": "longitude", "type": "number" }
    ]
}
```

**Recommendation:** Block layout for most use cases (clear labeling, easy editing). Table/Row layouts only for true columnar data where horizontal scanning makes sense.

## Groups with Conditional Logic

Group fields can contain sub-fields with conditional logic based on other sub-fields, creating wizard-like editor experiences. A boolean toggle in one sub-field can show/hide dependent sub-fields. Airbnb uses this pattern extensively (50 conditional logic instances across 166 fields, 30% adoption).

**Conditional Logic Pattern:**

```json
{
    "name": "announcement",
    "type": "group",
    "sub_fields": [
        {
            "name": "show_announcement",
            "type": "true_false",
            "default_value": 0
        },
        {
            "name": "announcement_text",
            "type": "textarea",
            "conditional_logic": [
                [{
                    "field": "field_show_announcement",
                    "operator": "==",
                    "value": "1"
                }]
            ]
        },
        {
            "name": "announcement_type",
            "type": "select",
            "choices": { "info": "Info", "warning": "Warning", "error": "Error" },
            "conditional_logic": [
                [{
                    "field": "field_show_announcement",
                    "operator": "==",
                    "value": "1"
                }]
            ]
        }
    ]
}
```

**Editor Experience:** When editors toggle "Show Announcement" ON, the text and type fields appear. Toggle OFF, they disappear. Reduces editor cognitive load.

## Group Fields in Repeaters

Repeaters can contain groups, creating structured collections with multiple related fields per row. Logo Cloud blocks (airbnb) use this pattern: a repeater of logos where each row is a group containing logo image + optional link URL.

**Repeater of Groups Pattern:**

```json
{
    "name": "logos",
    "type": "repeater",
    "layout": "block",
    "sub_fields": [
        {
            "name": "logo_item",
            "type": "group",
            "sub_fields": [
                {
                    "name": "logo",
                    "type": "image",
                    "required": 1
                },
                {
                    "name": "link",
                    "type": "url",
                    "required": 0
                }
            ]
        }
    ]
}
```

**Why Group Inside Repeater:** Semantically groups related data (logo + link). In practice, simpler to flatten (repeater with logo and link as direct sub-fields). Use only when group provides true organizational value.

**Simplified Alternative (More Common):**

```json
{
    "name": "logos",
    "type": "repeater",
    "sub_fields": [
        { "name": "logo", "type": "image", "required": 1 },
        { "name": "link", "type": "url", "required": 0 }
    ]
}
```

Analyzed projects show minimal nesting of groups in repeaters, favoring flat repeater structures for simplicity.

## Group Field Return Format

PHP `get_field()` returns groups as associative arrays with sub-field names as keys. This format enables direct sub-field access, null-safe checking, and iteration. Array format matches JSON structure, making serialization trivial for API responses.

**Return Format Example:**

```php
$group = get_field('metrics');
var_dump($group);
/*
array(2) {
  ["economic_impact"]=> array(3) {
    ["gdp_contribution"]=> string(3) "85B"
    ["hide"]=> bool(false)
    ["apply_to_descendants"]=> bool(true)
  }
  ["host_metrics"]=> array(2) {
    ["hosting_not_primary_occupation"]=> string(3) "87%"
    ["hide"]=> bool(false)
  }
}
*/

// Direct sub-field access
echo $group['economic_impact']['gdp_contribution'];  // "85B"

// Null-safe checking
if (isset($group['economic_impact']) && !$group['economic_impact']['hide']) {
    echo $group['economic_impact']['gdp_contribution'];
}
```

**Serialization for APIs:**

```php
// Group data already in array format - JSON encode directly
header('Content-Type: application/json');
echo json_encode(get_field('metrics'));
```

## Performance Considerations

ACF loads groups as single serialized postmeta entries, making groups more efficient than separate top-level fields for related data. A group with 5 sub-fields requires 1 database query, while 5 separate fields require 5 queries (or 1 query + 5 array lookups). Groups reduce database overhead for related fields.

**Database Storage:**

```sql
-- Group field (1 meta entry)
meta_key: social_links
meta_value: a:3:{s:12:"facebook_url";s:30:"https://facebook.com/example";...}

-- Separate fields (3 meta entries)
meta_key: facebook_url
meta_value: https://facebook.com/example

meta_key: twitter_url
meta_value: https://twitter.com/example

meta_key: instagram_url
meta_value: https://instagram.com/example
```

**Advantage:** Fewer database rows, single retrieval, atomic updates for related data.

**Caveat:** Can't query by individual sub-field values efficiently in SQL (serialized data). If you need to query "all posts with facebook_url set", groups hinder that use case.

## Groups vs Clone Fields

Clone fields duplicate existing field definitions across multiple field groups (DRY principle). Groups organize related fields within a single field group (logical structure). Both analyzed projects use Clone fields sparingly (3 instances total) compared to Groups (55 instances), indicating Groups address different needs.

**Use Group When:**
- Organizing related fields within one field group
- Creating hierarchical data structures
- Grouping fields that always appear together

**Use Clone When:**
- Sharing identical field definitions across multiple field groups
- Avoiding duplicate field configuration
- Maintaining consistency for repeated field patterns

**Example:** A "SEO Settings" field group might be cloned across multiple post types, while each instance uses Groups internally to organize title, description, and social meta fields.

## WordPress Admin UI Behavior

Groups render as collapsible accordion sections in WordPress post editor, reducing visual clutter for complex field sets. Editors expand groups as needed, focusing on relevant sections. All analyzed projects leverage this UI behavior, never using Group fields purely for data organization without UI benefit.

**UI States:**

- **Collapsed:** Shows group label only, hides sub-fields (default on page load)
- **Expanded:** Shows all sub-fields for editing

**Best Practice:** Name groups clearly (`Hero Section`, `Social Media Links`, `Contact Information`) so editors understand content without expanding.

## Anti-Patterns

Over-nesting groups (3+ levels deep) creates confusing editor experiences and unwieldy PHP access patterns. Single-field groups add unnecessary abstraction (just use a top-level field). Groups without logical relationships confuse editors (putting unrelated fields in a group named "Other Settings").

**Anti-Pattern Examples:**

```php
// ❌ Over-nested (3 levels)
get_field('page_settings')['hero']['background']['image']['url']

// ❌ Single-field group (pointless abstraction)
{
    "name": "hero_title_group",
    "type": "group",
    "sub_fields": [
        { "name": "title", "type": "text" }  // Just use top-level field
    ]
}

// ❌ Unrelated fields in group
{
    "name": "miscellaneous",  // Bad: vague name
    "type": "group",
    "sub_fields": [
        { "name": "twitter_url", "type": "url" },  // Social media
        { "name": "form_id", "type": "number" },    // Form integration
        { "name": "background_color", "type": "color_picker" }  // Styling
    ]
}
```

## Related Patterns

- **ACF Repeater Fields** (collections of related data)
- **ACF Flexible Content** (page builder layouts)
- **ACF Clone Fields** (DRY field definitions)
- **ACF Field Naming Conventions** (sub-field names don't need prefixes)
- **ACF + GraphQL Integration** (nested object queries)

## References

- Airbnb ACF JSON: `plugins/airbnb-policy-blocks/acf-json/group_*.json` (27 group fields)
- TheKelsey ACF JSON: `mu-plugins/thekelsey-custom/acf-json/group_*.json` (28 group fields)
- ACF Documentation: [Group Field](https://www.advancedcustomfields.com/resources/group/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 11: Advanced ACF Features)
