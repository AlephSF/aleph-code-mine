---
title: "ACF Repeater Fields with have_rows() Loop Pattern"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "repeater-fields", "have-rows", "loops", "dynamic-content"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Repeater fields enable variable-length lists of identical field sets. The `have_rows()` loop pattern provides a WordPress-style API for iterating repeater data, similar to The Loop for posts.

WordPress projects analyzed show 100% adoption of `have_rows()` loop pattern for repeater field access (21 repeater fields across 393 total fields, with extensive template usage).

## Repeater Field Structure

Repeater fields contain sub-fields that can be duplicated multiple times by content editors.

### JSON Configuration

```json
{
  "key": "field_680ad6fe88bfb",
  "label": "Logos",
  "name": "logos",
  "type": "repeater",
  "instructions": "Add client/partner logos",
  "show_in_graphql": 1,
  "graphql_field_name": "logos",
  "layout": "block",
  "button_label": "Add Logo",
  "min": 0,
  "max": 0,
  "sub_fields": [
    {
      "key": "field_680ad71788bfc",
      "label": "Logo",
      "name": "logo",
      "type": "image",
      "return_format": "id",
      "required": 1
    },
    {
      "key": "field_680ad74888bfd",
      "label": "Link (optional)",
      "name": "link",
      "type": "url"
    }
  ]
}
```

**Key Properties:**
- `layout`: Display mode (`block`, `table`, `row`)
- `button_label`: Add row button text (defaults to "Add Row")
- `min`: Minimum rows (0 = optional)
- `max`: Maximum rows (0 = unlimited)
- `sub_fields`: Field definitions for each row

## have_rows() Loop Pattern

The standard WordPress pattern for iterating repeater fields.

### Basic Loop Structure

```php
<?php
if( have_rows('logos') ):
  while( have_rows('logos') ): the_row();

    // Get sub-field values for current row
    $logo_id = get_sub_field('logo');
    $link = get_sub_field('link');

    // Output HTML for current row
    echo wp_get_attachment_image( $logo_id, 'medium' );

  endwhile;
endif;
?>
```

**Functions:** `have_rows('logos')` checks data/setup iterator, `while(have_rows('logos'))` loops rows, `the_row()` advances row, `get_sub_field('logo')` gets value.

### Complete Template Example

```php
<?php
$block_wrapper_attributes = get_block_wrapper_attributes();
?>
<div <?php echo $block_wrapper_attributes; ?>>
  <?php if( have_rows('logos') ): ?>
    <div class="logo-grid">
      <?php while( have_rows('logos') ): the_row();
        $logo_id = get_sub_field('logo');
        $link = get_sub_field('link');
      ?>
        <div class="logo-item">
          <?php if( $link ): ?>
            <a href="<?php echo esc_url($link); ?>" target="_blank" rel="noopener">
          <?php endif; ?>

          <?php echo wp_get_attachment_image( $logo_id, 'medium', false, [
            'loading' => 'lazy'
          ]); ?>

          <?php if( $link ): ?>
            </a>
          <?php endif; ?>
        </div>
      <?php endwhile; ?>
    </div>
  <?php endif; ?>
</div>
```

## Nested Repeaters

Repeaters can contain other repeaters, creating multi-level data structures.

### Two-Level Repeater Structure

```json
{
  "name": "faq_accordion",
  "type": "repeater",
  "sub_fields": [
    {
      "name": "section_title",
      "type": "text"
    },
    {
      "name": "questions",
      "type": "repeater",
      "sub_fields": [
        {"name": "question", "type": "text"},
        {"name": "answer", "type": "wysiwyg"}
      ]
    }
  ]
}
```

### Nested Loop Pattern

```php
<?php
if( have_rows('faq_accordion') ):
  while( have_rows('faq_accordion') ): the_row();

    // Outer row data
    $section_title = get_sub_field('section_title');
    ?>

    <h2><?php echo esc_html($section_title); ?></h2>

    <?php
    // Inner repeater
    if( have_rows('questions') ):
      while( have_rows('questions') ): the_row();

        // Inner row data
        $question = get_sub_field('question');
        $answer = get_sub_field('answer');
        ?>

        <div class="faq-item">
          <h3><?php echo esc_html($question); ?></h3>
          <div><?php echo $answer; ?></div>
        </div>

      <?php endwhile;
    endif;

  endwhile;
endif;
?>
```

**Warning:** Avoid nesting beyond 2 levels. Deep nesting creates performance issues and confusing admin UI.

## Repeater with Custom Post ID

Access repeater fields from different posts or options pages.

### Options Page Repeater

```php
<?php
// Get repeater from ACF options page
if( have_rows('social_media_links', 'option') ):
  while( have_rows('social_media_links', 'option') ): the_row();

    $platform = get_sub_field('platform');
    $url = get_sub_field('url');
    ?>

    <a href="<?php echo esc_url($url); ?>">
      <?php echo esc_html($platform); ?>
    </a>

  <?php endwhile;
endif;
?>
```

### Specific Post Repeater

```php
<?php
$post_id = 123;

if( have_rows('team_members', $post_id) ):
  while( have_rows('team_members', $post_id) ): the_row();

    $name = get_sub_field('name');
    $photo = get_sub_field('photo');
    ?>

    <div class="team-member">
      <?php echo wp_get_attachment_image( $photo, 'thumbnail' ); ?>
      <h3><?php echo esc_html($name); ?></h3>
    </div>

  <?php endwhile;
endif;
?>
```

## Array Access Pattern (Alternative)

For programmatic access or processing, use `get_field()` array return.

### Array Format

```php
<?php
// Get repeater as array
$logos = get_field('logos');

// Array structure:
// [
//   0 => ['logo' => 123, 'link' => 'https://example.com'],
//   1 => ['logo' => 456, 'link' => 'https://example2.com'],
// ]

// Loop with foreach
if( $logos ) {
  foreach( $logos as $logo_item ) {
    echo wp_get_attachment_image( $logo_item['logo'], 'medium' );
    if( $logo_item['link'] ) {
      echo '<a href="' . esc_url($logo_item['link']) . '">Visit</a>';
    }
  }
}

// Access specific row
if( $logos && isset($logos[0]) ) {
  $first_logo = $logos[0];
  echo wp_get_attachment_image( $first_logo['logo'], 'large' );
}

// Count rows
$logo_count = is_array($logos) ? count($logos) : 0;
echo "Total logos: {$logo_count}";
?>
```

**When to Use Array Access:**
- Programmatic row manipulation (sorting, filtering)
- Counting rows before rendering
- Conditional rendering based on row count
- Processing repeater data in custom functions

## Repeater Layout Modes

Repeaters support three admin layout modes via `layout` property.

### Block Layout (Default)

```json
{"layout": "block"}
```

**Admin Rendering:**
- Each row in collapsible accordion
- Sub-fields stacked vertically
- Best for: Complex sub-fields (WYSIWYG, images, groups)

### Table Layout

```json
{"layout": "table"}
```

**Admin Rendering:**
- Rows displayed as table rows
- Sub-fields as columns
- Best for: Simple sub-fields (text, numbers, selects)
- Limit: 3-5 sub-fields for readability

### Row Layout

```json
{"layout": "row"}
```

**Admin Rendering:**
- Minimal layout with inline sub-fields
- Best for: Very simple repeaters (2-3 text fields)

## Min/Max Row Constraints

Control the number of rows editors can create.

### Configuration

```json
{
  "type": "repeater",
  "min": 3,
  "max": 10,
  "button_label": "Add Testimonial"
}
```

**Behavior:**
- `min: 3`: Minimum 3 rows required (validation error if fewer)
- `max: 10`: Maximum 10 rows allowed (Add button disappears at limit)
- `min: 0, max: 0`: No constraints (default)

**Use Cases:**
- Hero carousel: `min: 3, max: 5` (force 3-5 slides)
- Team grid: `min: 0, max: 12` (max 12 members)
- Fixed sections: `min: 4, max: 4` (exactly 4 sections)

## GraphQL Integration

Repeater fields expose as GraphQL lists when `show_in_graphql` is enabled.

### GraphQL Query

```graphql
query GetLogoCloudBlock($id: ID!) {
  page(id: $id, idType: DATABASE_ID) {
    editorBlocks {
      ... on CreateBlockLogoCloudBlock {
        logoCloudBlock {
          logos {
            logo {
              sourceUrl
              altText
            }
            link
          }
        }
      }
    }
  }
}
```

### GraphQL Response

```json
{
  "data": {
    "page": {
      "editorBlocks": [
        {
          "logoCloudBlock": {
            "logos": [
              {
                "logo": {
                  "sourceUrl": "https://example.com/logo1.png",
                  "altText": "Company 1"
                },
                "link": "https://example.com"
              },
              {
                "logo": {
                  "sourceUrl": "https://example.com/logo2.png",
                  "altText": "Company 2"
                },
                "link": null
              }
            ]
          }
        }
      ]
    }
  }
}
```

**Pattern:** Repeater becomes GraphQL list type. Sub-fields become nested object properties.

## Repeater Row Index

Access current row index during loops for numbering or styling.

### Row Index Pattern

```php
<?php
$row_index = 0;

if( have_rows('stats') ):
  while( have_rows('stats') ): the_row();
    $row_index++;

    $stat_value = get_sub_field('stat_value');
    ?>

    <div class="stat-item" data-index="<?php echo $row_index; ?>">
      <span class="stat-number"><?php echo $row_index; ?></span>
      <span class="stat-value"><?php echo esc_html($stat_value); ?></span>
    </div>

  <?php endwhile;
endif;
?>
```

**Alternative (Array Access):**
```php
<?php
$stats = get_field('stats');

if( $stats ) {
  foreach( $stats as $index => $stat ) {
    // $index is zero-based (0, 1, 2, ...)
    $display_number = $index + 1; // Convert to 1-based

    echo "<div class='stat' data-index='{$display_number}'>";
    echo esc_html($stat['stat_value']);
    echo "</div>";
  }
}
?>
```

## Blade Template Pattern (Sage Framework)

thekelsey-wp uses Blade templates for cleaner syntax.

### Blade Repeater Loop

```php
@if(have_rows('stats'))
  <div class="stats-grid">
    @while(have_rows('stats'))
      @php(the_row())

      <div class="stat-card">
        <span class="value">{{ get_sub_field('stat_value') }}</span>
        <span class="label">{{ get_sub_field('stat_label') }}</span>
      </div>
    @endwhile
  </div>
@endif
```

**Benefits:**
- Cleaner control structures (`@if`, `@while`)
- Automatic escaping with `{{ }}`
- Less PHP boilerplate

## Performance Optimization

Large repeaters (50+ rows) can impact page load times. Optimize with caching or pagination.

### Transient Caching Pattern

```php
<?php
function get_cached_logos() {
  $cache_key = 'logo_cloud_' . get_the_ID();
  $logos_html = get_transient( $cache_key );

  if ( false === $logos_html ) {
    ob_start();

    if( have_rows('logos') ):
      while( have_rows('logos') ): the_row();
        $logo_id = get_sub_field('logo');
        echo wp_get_attachment_image( $logo_id, 'medium' );
      endwhile;
    endif;

    $logos_html = ob_get_clean();
    set_transient( $cache_key, $logos_html, DAY_IN_SECONDS );
  }

  return $logos_html;
}

echo get_cached_logos();
?>
```

### Limit Rows Pattern

```php
<?php
// Show only first 10 rows
$max_rows = 10;
$current_row = 0;

if( have_rows('large_repeater') ):
  while( have_rows('large_repeater') && $current_row < $max_rows ): the_row();
    $current_row++;

    // Render row
    echo get_sub_field('content');

  endwhile;
endif;
?>
```

## Common Pitfalls

**Missing the_row():**
```php
// Bad: Infinite loop, sub-fields don't work
if( have_rows('logos') ):
  while( have_rows('logos') ):
    echo get_sub_field('logo'); // Returns empty
  endwhile;
endif;

// Good: the_row() advances iterator
while( have_rows('logos') ): the_row();
  echo get_sub_field('logo');
endwhile;
```

**Wrong Sub-Field Function:**
```php
// Bad: get_field() doesn't work inside have_rows()
while( have_rows('logos') ): the_row();
  echo get_field('logo'); // Returns wrong value
endwhile;

// Good: get_sub_field() for repeater sub-fields
while( have_rows('logos') ): the_row();
  echo get_sub_field('logo');
endwhile;
```

**Nested Repeater Same Name:**
```php
// Bad: Inner repeater field name matches outer
while( have_rows('items') ): the_row();
  while( have_rows('items') ): the_row(); // Conflict!
  endwhile;
endwhile;

// Good: Unique field names
while( have_rows('sections') ): the_row();
  while( have_rows('section_items') ): the_row();
  endwhile;
endwhile;
```

## Related Patterns

- **Group Fields:** Use groups for fixed field sets, repeaters for variable lists
- **Flexible Content:** Use for variable layouts, repeaters for identical row types
- **Options Pages:** Repeaters work on options pages for site-wide lists
- **GraphQL:** Repeaters become list types in GraphQL schema

**Source Projects:** airbnb (6 repeater fields), thekelsey (15 repeater fields), Combined: 21 repeater fields with 100% have_rows() adoption
