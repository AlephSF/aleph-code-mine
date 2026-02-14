---
title: "ACF Group Fields for Nested Field Organization"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "group-fields", "nested-fields", "field-organization", "data-structure"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Group fields organize related fields into collapsible sections in the WordPress admin and nested objects in data structures. Groups improve field organization, reduce admin clutter, and create logical data hierarchies for template access and GraphQL queries.

WordPress projects analyzed show 100% adoption of group fields for nested organization (55 group fields across 393 total fields, 14% usage rate).

## Group Field Structure

Group fields contain sub-fields that render as a single unit in the WordPress admin.

### JSON Configuration

```json
{
  "key": "field_67e7246e92304",
  "label": "Metrics",
  "name": "metrics",
  "type": "group",
  "instructions": "Economic impact metrics for this municipality",
  "show_in_graphql": 1,
  "graphql_field_name": "metrics",
  "sub_fields": [
    {
      "key": "field_67e7248492305",
      "label": "Economic Impact",
      "name": "economic_impact",
      "type": "number",
      "show_in_graphql": 1,
      "graphql_field_name": "economicImpact"
    },
    {
      "key": "field_67e7249a92306",
      "label": "GDP Contribution",
      "name": "gdp_contribution",
      "type": "number",
      "show_in_graphql": 1,
      "graphql_field_name": "gdpContribution"
    },
    {
      "key": "field_67e724ac92307",
      "label": "Total Tax Generated",
      "name": "total_tax_generated",
      "type": "number",
      "show_in_graphql": 1,
      "graphql_field_name": "totalTaxGenerated"
    }
  ]
}
```

**Key Properties:**
- `type: "group"` identifies field as container
- `sub_fields` array contains nested fields
- Each sub-field has own key, label, name, type
- Group can have own GraphQL exposure settings

## Template Access Pattern

Group fields return associative arrays in PHP templates.

### PHP get_field() Usage

```php
<?php
// Get entire group as array
$metrics = get_field('metrics');

// Access sub-fields via array keys
echo $metrics['economic_impact'];
echo $metrics['gdp_contribution'];
echo $metrics['total_tax_generated'];

// Alternative: Direct sub-field access
echo get_field('metrics')['economic_impact'];

// Check if group has data
if( $metrics ) {
  echo '<div class="metrics">';
  echo '<p>Economic Impact: $' . number_format($metrics['economic_impact']) . '</p>';
  echo '<p>GDP Contribution: $' . number_format($metrics['gdp_contribution']) . '</p>';
  echo '<p>Total Tax: $' . number_format($metrics['total_tax_generated']) . '</p>';
  echo '</div>';
}
?>
```

### Blade Template Usage (Sage Framework)

```php
@php
  $metrics = get_field('metrics');
@endphp

@if($metrics)
  <div class="metrics-grid">
    <div class="metric">
      <span class="label">Economic Impact</span>
      <span class="value">${{ number_format($metrics['economic_impact']) }}</span>
    </div>
    <div class="metric">
      <span class="label">GDP Contribution</span>
      <span class="value">${{ number_format($metrics['gdp_contribution']) }}</span>
    </div>
    <div class="metric">
      <span class="label">Total Tax Generated</span>
      <span class="value">${{ number_format($metrics['total_tax_generated']) }}</span>
    </div>
  </div>
@endif
```

## GraphQL Query Pattern

Group fields become nested objects in GraphQL responses, improving API structure.

### GraphQL Schema

```graphql
type Page {
  metrics: Metrics
}

type Metrics {
  economicImpact: Float
  gdpContribution: Float
  totalTaxGenerated: Float
}
```

### GraphQL Query

```graphql
query GetMunicipality($id: ID!) {
  municipality(id: $id, idType: DATABASE_ID) {
    title
    metrics {
      economicImpact
      gdpContribution
      totalTaxGenerated
    }
  }
}
```

### GraphQL Response

```json
{
  "data": {
    "municipality": {
      "title": "San Francisco",
      "metrics": {
        "economicImpact": 85000000000,
        "gdpContribution": 24000000000,
        "totalTaxGenerated": 1000000000
      }
    }
  }
}
```

**Benefits:**
- Cleaner API structure (nested objects vs flat fields)
- Type safety in GraphQL schema
- Easier frontend data consumption

## Group Field Layout Modes

ACF group fields support two layout modes: `block` and `table`.

### Block Layout (Default)

```json
{
  "type": "group",
  "layout": "block",
  "sub_fields": [...]
}
```

**Rendering:**
- Each sub-field renders on its own row
- Labels appear above field inputs
- Best for: Complex fields (WYSIWYG, images, repeaters)

**Admin Preview:**
```
┌─ Metrics ───────────────────────┐
│ Economic Impact                 │
│ [_________] (number input)      │
│                                 │
│ GDP Contribution                │
│ [_________] (number input)      │
│                                 │
│ Total Tax Generated             │
│ [_________] (number input)      │
└─────────────────────────────────┘
```

### Table Layout

```json
{
  "type": "group",
  "layout": "table",
  "sub_fields": [...]
}
```

**Rendering:**
- Sub-fields render in columns
- Labels appear in table header
- Best for: Simple fields (text, number, select)

**Admin Preview:**
```
┌─ Metrics ──────────────────────────────────────┐
│ Economic Impact | GDP Contribution | Total Tax │
│ [___________]   | [___________]    | [_______] │
└────────────────────────────────────────────────┘
```

**Use Case:** Compact display for groups with 3-5 simple fields.

## Nested Groups Pattern

Groups can contain other groups, creating multi-level data hierarchies (use sparingly).

### Two-Level Nesting

```json
{
  "name": "location_data",
  "type": "group",
  "sub_fields": [
    {
      "name": "address",
      "type": "group",
      "sub_fields": [
        {"name": "street", "type": "text"},
        {"name": "city", "type": "text"},
        {"name": "state", "type": "text"},
        {"name": "zip", "type": "text"}
      ]
    },
    {
      "name": "coordinates",
      "type": "group",
      "sub_fields": [
        {"name": "latitude", "type": "number"},
        {"name": "longitude", "type": "number"}
      ]
    }
  ]
}
```

### Template Access (Nested)

```php
<?php
$location = get_field('location_data');

$street = $location['address']['street'];
$city = $location['address']['city'];
$lat = $location['coordinates']['latitude'];
$lng = $location['coordinates']['longitude'];

echo "{$street}, {$city}";
echo "Lat/Lng: {$lat}, {$lng}";
?>
```

**Warning:** Avoid nesting beyond 2 levels. Deep nesting creates brittle templates and confusing admin UI.

## Group vs Repeater vs Flexible Content

Choose the right field type based on data structure needs.

### When to Use Group

```
Use Group when:
✅ Fixed number of related fields
✅ Single instance (not repeating)
✅ Logical grouping (e.g., address, contact info, settings)

Example: Site footer settings
- Group: footer_settings
  - Sub-field: copyright_text
  - Sub-field: footer_logo
  - Sub-field: social_links (repeater)
```

### When to Use Repeater

```
Use Repeater when:
✅ Variable number of identical field sets
✅ List/array structure
✅ Add/remove/reorder rows

Example: Team members
- Repeater: team_members
  - Sub-field: photo
  - Sub-field: name
  - Sub-field: title
  - Sub-field: bio
```

### When to Use Flexible Content

```
Use Flexible Content when:
✅ Variable number of different field sets
✅ Page builder / layout system
✅ Different layouts per row

Example: Page builder
- Flexible Content: page_sections
  - Layout: hero_section (different fields)
  - Layout: text_block (different fields)
  - Layout: image_gallery (different fields)
```

## Real-World Examples

**News Article Details (airbnb):**
```json
{"name":"news_article_details","type":"group","sub_fields":[{"name":"headline","type":"text"},{"name":"link","type":"url"},{"name":"publication_name","type":"text"},{"name":"publication_date","type":"date_picker"}]}
```

```php
<?php $article = get_field('news_article_details'); ?>
<article class="external-news">
  <h3><a href="<?php echo $article['link']; ?>"><?php echo $article['headline']; ?></a></h3>
  <p class="meta"><?php echo $article['publication_name'] . ' - ' . date('F j, Y', strtotime($article['publication_date'])); ?></p>
</article>
```

**Social Media Links (thekelsey):**
```json
{"name":"social_media","type":"group","location":[{"param":"options_page"}],"sub_fields":[{"name":"facebook_url","type":"url"},{"name":"twitter_url","type":"url"},{"name":"instagram_url","type":"url"}]}
```

```php
<?php $social = get_field('social_media', 'option'); ?>
<div class="social-links">
  <?php if($social['facebook_url']): ?><a href="<?php echo $social['facebook_url']; ?>">Facebook</a><?php endif; ?>
  <?php if($social['twitter_url']): ?><a href="<?php echo $social['twitter_url']; ?>">Twitter</a><?php endif; ?>
</div>
```

## Conditional Logic with Groups

Group fields support conditional logic to show/hide based on other field values.

### Toggle + Conditional Group Pattern

```json
{
  "fields": [
    {
      "name": "show_announcement",
      "type": "true_false",
      "default_value": 0
    },
    {
      "name": "announcement",
      "type": "group",
      "conditional_logic": [
        [
          {
            "field": "field_show_announcement",
            "operator": "==",
            "value": "1"
          }
        ]
      ],
      "sub_fields": [
        {"name": "announcement_text", "type": "wysiwyg"},
        {"name": "announcement_type", "type": "select"}
      ]
    }
  ]
}
```

**Behavior:** `announcement` group only appears in admin when `show_announcement` is checked.

## Database Storage

Group fields store sub-field values as separate post meta entries with parent field name prefixed.

### Meta Key Pattern

```
Group field: metrics
- economic_impact sub-field

Database (wp_postmeta):
meta_key: "metrics_economic_impact"
meta_value: "85000000000"

meta_key: "_metrics_economic_impact"
meta_value: "field_67e7248492305"  (ACF field key reference)
```

**Query Pattern:**
```php
// Direct database query (avoid if possible, use get_field() instead)
global $wpdb;
$economic_impact = $wpdb->get_var(
  $wpdb->prepare(
    "SELECT meta_value FROM {$wpdb->postmeta}
     WHERE post_id = %d AND meta_key = 'metrics_economic_impact'",
    $post_id
  )
);
```

## Common Pitfalls

**Missing Null Check:**
```php
// Bad: Fatal error if group is empty
echo $metrics['economic_impact'];

// Good: Check group exists first
if( $metrics ) {
  echo $metrics['economic_impact'];
}
```

**Deep Nesting:**
```php
// Bad: 4 levels deep, brittle code
echo $data['location']['address']['additional']['notes']['text'];

// Good: Max 2 levels
echo $location['address']['street'];
```

**Inconsistent Sub-Field Access:**
```php
// Bad: Mixed access patterns
$economic = $metrics['economic_impact'];
$gdp = get_field('metrics')['gdp_contribution'];

// Good: Consistent pattern
$metrics = get_field('metrics');
$economic = $metrics['economic_impact'];
$gdp = $metrics['gdp_contribution'];
```

## Related Patterns

- **Repeater Fields:** Use for repeating instances of group-like structures
- **Options Pages:** Groups work well for organizing site-wide settings
- **WPGraphQL:** Groups create nested object types in GraphQL schema
- **Conditional Logic:** Show/hide groups based on toggle fields

**Source Projects:** airbnb (27 group fields, 16% of fields), thekelsey (28 group fields, 12% of fields), Combined: 55 group fields across 393 total fields (14%)
