---
title: "ACF Blocks Registration with block.json (Modern Approach)"
category: "wordpress-acf"
subcategory: "gutenberg-integration"
tags: ["acf-blocks", "gutenberg", "block-json", "wordpress-6", "headless"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Blocks enable custom Gutenberg blocks powered by Advanced Custom Fields instead of React. The modern block.json registration pattern provides automatic asset enqueuing, block metadata, and WPGraphQL integration for headless WordPress architectures.

WordPress projects analyzed show 100% adoption of block.json registration for ACF blocks in modern headless implementations (15 ACF blocks registered via block.json, 0 using legacy `acf_register_block()` PHP-only pattern).

## block.json Registration Pattern

WordPress 5.8+ introduced block.json as the preferred block registration method. ACF blocks use this same pattern.

### Directory Structure

```
plugins/
  airbnb-policy-blocks/
    src/
      logo-cloud-block/
        block.json          ← Block metadata
        edit.js             ← (Optional) Custom block editor
        save.js             ← (Optional) Save functionality
        style.css           ← Frontend styles
        editor.css          ← Editor-only styles
        logo-cloud-block.php ← PHP render template
    acf-json/
      group_680ad6fe615b8.json  ← ACF fields for this block
    airbnb-policy-blocks.php  ← Registration code
```

### block.json Configuration

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "create-block/logo-cloud-block",
  "version": "0.1.0",
  "title": "Logo Cloud Block",
  "category": "media",
  "icon": "smiley",
  "description": "Display a grid of logos with optional links",
  "example": {},
  "supports": {
    "html": false,
    "anchor": true,
    "align": ["wide", "full"]
  },
  "textdomain": "airbnb-policy-blocks",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css",
  "style": "file:./style-index.css",
  "render": "file:./logo-cloud-block.php",
  "acf": {
    "mode": "preview",
    "renderTemplate": "logo-cloud-block.php"
  }
}
```

**Key Fields for ACF Blocks:**
- `render`: Path to PHP template file (ACF-specific)
- `acf.mode`: Display mode (`preview`, `edit`, `auto`)
- `acf.renderTemplate`: Template filename (redundant with `render` but kept for compatibility)

### PHP Registration Code

```php
// airbnb-policy-blocks.php
function airbnb_policy_blocks_acf_block_init() {
  $blocks = [
    'all-posts-teaser-grid-block',
    'city-portal-block',
    'external-news-block',
    'faq-block',
    'featured-post-block',
    'home-page-hero-block',
    'logo-cloud-block',
    'municipalities-search-block',
    'people-grid-block',
    'policy-toolkit-block',
    'post-teaser-grid-block',
    'priorities-block',
    'public-policy-priorities-block',
    'stat-block',
    'text-image-block',
  ];

  foreach ( $blocks as $block ) {
    register_block_type( __DIR__ . '/src/' . $block );
  }
}
add_action( 'init', 'airbnb_policy_blocks_acf_block_init' );
```

**Pattern:**
- `register_block_type()` accepts a directory path
- WordPress auto-loads `block.json` from that directory
- No need to pass block metadata array (block.json provides it)
- Registers on `init` hook (standard WordPress timing)

## ACF Field Group Location Rules

ACF fields attach to blocks via location rules in the JSON configuration.

### Block Location Rule Pattern

```json
{
  "key": "group_680ad6fe615b8",
  "title": "Logo Cloud Block",
  "fields": [
    {
      "key": "field_680ad6fe88bfb",
      "label": "Logos",
      "name": "logos",
      "type": "repeater",
      "show_in_graphql": 1
    }
  ],
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

**Critical Details:**
- `"param": "block"` targets a specific block type
- `"value"` must match block.json `name` field exactly
- One field group per block (granular organization)
- Fields appear in block sidebar when block is selected

## PHP Render Template

ACF blocks use PHP templates for rendering, enabling headless WordPress architectures.

### Basic Render Template

```php
<?php
/**
 * Logo Cloud Block Template
 *
 * @param   array $block The block settings and attributes.
 * @param   string $content The block inner HTML (empty).
 * @param   bool $is_preview True during AJAX preview.
 * @param   (int|string) $post_id The post ID this block is saved to.
 */

// Get ACF field values
$logos = get_field('logos');

// Block wrapper attributes (includes anchor, align, etc.)
$block_wrapper_attributes = get_block_wrapper_attributes();
?>

<div <?php echo $block_wrapper_attributes; ?>>
  <?php if( $logos ): ?>
    <div class="logo-grid">
      <?php foreach( $logos as $logo ): ?>
        <div class="logo-item">
          <?php if( $logo['link'] ): ?>
            <a href="<?php echo esc_url($logo['link']); ?>">
          <?php endif; ?>

          <?php echo wp_get_attachment_image( $logo['logo'], 'medium' ); ?>

          <?php if( $logo['link'] ): ?>
            </a>
          <?php endif; ?>
        </div>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>
</div>
```

**Template Variables:**
- `$block`: Block metadata (name, attributes, anchor, etc.)
- `$content`: Inner blocks HTML (rarely used in ACF blocks)
- `$is_preview`: True when rendering in editor preview
- `$post_id`: Post ID where block is used

### InnerBlocks Support

ACF blocks can contain nested blocks using `<InnerBlocks>`.

```php
<?php
$allowed_blocks = ['core/paragraph', 'core/heading'];
$template = [
  ['core/heading', ['level' => 2, 'placeholder' => 'Enter title...']],
  ['core/paragraph', ['placeholder' => 'Enter content...']],
];

$block_wrapper_attributes = get_block_wrapper_attributes();
?>

<div <?php echo $block_wrapper_attributes; ?>>
  <div class="container">
    <?php if( get_field('heading') ): ?>
      <h2><?php the_field('heading'); ?></h2>
    <?php endif; ?>

    <InnerBlocks
      allowedBlocks="<?php echo esc_attr( wp_json_encode( $allowed_blocks ) ); ?>"
      template="<?php echo esc_attr( wp_json_encode( $template ) ); ?>"
    />
  </div>
</div>
```

## WPGraphQL Integration

ACF blocks automatically expose to WPGraphQL when `show_in_graphql` is enabled on field groups.

### GraphQL Field Exposure

```json
{
  "key": "group_680ad6fe615b8",
  "title": "Logo Cloud Block",
  "show_in_graphql": 1,
  "graphql_field_name": "logoCloudBlock",
  "fields": [
    {
      "name": "logos",
      "type": "repeater",
      "show_in_graphql": 1,
      "graphql_field_name": "logos",
      "sub_fields": [
        {
          "name": "logo",
          "type": "image",
          "show_in_graphql": 1,
          "graphql_field_name": "logo"
        },
        {
          "name": "link",
          "type": "url",
          "show_in_graphql": 1,
          "graphql_field_name": "link"
        }
      ]
    }
  ]
}
```

### GraphQL Query Pattern

```graphql
query GetPageBlocks($id: ID!) {
  page(id: $id, idType: DATABASE_ID) {
    editorBlocks {
      name
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

**Response Shape:**
```json
{
  "data": {
    "page": {
      "editorBlocks": [
        {
          "name": "create-block/logo-cloud-block",
          "logoCloudBlock": {
            "logos": [
              {
                "logo": {
                  "sourceUrl": "https://example.com/logo1.png",
                  "altText": "Company 1"
                },
                "link": "https://example.com"
              }
            ]
          }
        }
      ]
    }
  }
}
```

## Block Display Modes

ACF blocks support three display modes via `acf.mode` in block.json.

### Mode: preview (Recommended)

```json
{
  "acf": {
    "mode": "preview"
  }
}
```

**Behavior:**
- Shows live preview of rendered template in editor
- Editor can click "Edit" to show fields
- Best for blocks with complex layouts

### Mode: edit

```json
{
  "acf": {
    "mode": "edit"
  }
}
```

**Behavior:**
- Shows ACF fields by default in editor
- Editor can click "Preview" to see rendered output
- Best for simple blocks with few fields

### Mode: auto

```json
{
  "acf": {
    "mode": "auto"
  }
}
```

**Behavior:**
- Shows preview after data is entered
- Shows edit mode if block is empty
- Balance between preview and edit modes

## Block Restriction by Post Type

Headless WordPress sites often restrict blocks to prevent content inconsistency.

### Whitelist Pattern

```php
function restrict_blocks_by_post_type( $allowed_blocks, $editor_context ) {
  // Get current post type
  $post_type = $editor_context->post->post_type ?? '';

  if ( $post_type === 'bnb_policy' ) {
    return [
      // Core blocks
      'core/paragraph',
      'core/heading',
      'core/list',
      'core/image',

      // ACF blocks
      'create-block/home-page-hero-block',
      'create-block/stat-block',
      'create-block/text-image-block',
      'create-block/faq-block',
      'create-block/post-teaser-grid-block',
    ];
  }

  // Return all allowed blocks for other post types
  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks_by_post_type', 10, 2 );
```

**Benefits:**
- Enforces content structure
- Prevents editor confusion
- Improves GraphQL API consistency

## Legacy Pattern: acf_register_block_type()

Pre-block.json registration via PHP (deprecated but still functional).

### Legacy PHP Registration

```php
acf_register_block_type(array(
  'name'              => 'logo-cloud',
  'title'             => __('Logo Cloud'),
  'description'       => __('Display a grid of logos'),
  'render_template'   => plugin_dir_path(__FILE__) . 'blocks/logo-cloud.php',
  'category'          => 'media',
  'icon'              => 'grid-view',
  'keywords'          => array('logo', 'cloud', 'grid'),
  'mode'              => 'preview',
  'supports'          => array(
    'align' => array('wide', 'full'),
    'anchor' => true,
  ),
));
```

**Why Avoid:**
- No automatic asset enqueuing
- Harder to maintain (PHP vs JSON)
- No `$schema` validation
- WPGraphQL integration less clean

**Migration:** Convert legacy ACF blocks to block.json format for better maintainability.

## Performance Considerations

ACF blocks load ACF field data on every page render. Optimize for headless architectures.

### Caching Pattern

```php
<?php
// Check if cached
$cache_key = 'logo_cloud_block_' . $post_id;
$logos_html = get_transient( $cache_key );

if ( false === $logos_html ) {
  // Build HTML
  ob_start();

  $logos = get_field('logos');
  foreach( $logos as $logo ) {
    echo wp_get_attachment_image( $logo['logo'], 'medium' );
  }

  $logos_html = ob_get_clean();

  // Cache for 1 hour
  set_transient( $cache_key, $logos_html, HOUR_IN_SECONDS );
}

echo $logos_html;
?>
```

**When to Cache:**
- Blocks with expensive `get_field()` calls (e.g., repeaters with 50+ rows)
- Blocks querying external APIs
- Blocks with complex image processing

## Common Pitfalls

**Missing block.json:** Registering `__DIR__ . '/src/logo-cloud-block'` without `block.json` file causes silent failure.

**Name Mismatch:** ACF location rule `"value": "create-block/logo-cloud"` must match block.json `"name": "create-block/logo-cloud"` exactly.

**GraphQL Field Name Collision:** Using `graphql_field_name: "title"` conflicts with WordPress core `post.title` field.

**Mode Confusion:** `mode: edit` shows fields by default, confusing editors expecting preview.

## Related Patterns

- **ACF JSON Storage:** Block field groups stored in `acf-json/` directory
- **WPGraphQL Integration:** Blocks auto-expose to GraphQL with `show_in_graphql`
- **Field Naming Conventions:** Block fields use camelCase for GraphQL

**Source Projects:** airbnb-policy-blocks (15 ACF blocks, 100% block.json registration), thekelsey (3 ACF blocks, legacy registration)
