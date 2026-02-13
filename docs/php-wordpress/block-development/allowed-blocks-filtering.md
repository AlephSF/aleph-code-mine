---
title: "Allowed Blocks Filtering for Editor Access Control"
category: "block-development"
subcategory: "editor-customization"
tags: ["wordpress", "gutenberg", "allowed-blocks", "access-control", "editor-restrictions"]
stack: "php-wp"
priority: "medium"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "40%"
last_updated: "2026-02-12"
---

# Allowed Blocks Filtering for Editor Access Control

## Overview

WordPress allowed_block_types_all filter restricts available blocks in the editor inserter by defining allowlists per post type, user role, or editor context. The filter enables content governance by preventing editors from inserting incompatible or unsupported blocks into specific post types.

**Why this matters:** Default WordPress enables all registered blocks (core + custom) in every post type. This creates UX confusion for editors seeing irrelevant blocks and increases support burden when editors use blocks not styled for their context. Allowlists improve editor experience by showing only appropriate blocks per content type.

**Source confidence:** 40% adoption (2/5 plugins implement allowed block filtering). airbnb-policy-blocks uses tiered allowlist pattern for different post types (Pages, Priority Pages, Local Pages). rkv-block-editor restricts blocks for specific custom post types.

## Basic Allowlist Implementation

### Global Block Restriction

WordPress allowed_block_types_all filter receives current allowed blocks and editor context, returning filtered array of allowed block namespaces. Simplest implementation restricts to specific blocks globally.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  $allowed_blocks = array(
    'core/paragraph',
    'core/heading',
    'core/list',
    'core/image',
    'create-block/section-block',
    'create-block/slideshow-block',
  );

  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Filter parameters:**
- `$allowed_block_types`: Current allowed blocks (boolean true = all blocks, array = specific blocks)
- `$editor_context`: WP_Block_Editor_Context object containing post, post type, and editor name

**Return value:** Array of allowed block namespaces or boolean true to allow all blocks

**Use case:** Simplify editor for non-technical users by removing advanced blocks (embeds, code, custom HTML).

## Post-Type-Specific Allowlists

### Tiered Allowlist Pattern

WordPress post-type-specific allowlists enable different block access per content type. This pattern uses tiered allowlist arrays merged based on post type detection.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  // Blocks allowed everywhere
  $universally_allowed_blocks = array(
    'core/block',
    'core/paragraph',
    'core/heading',
    'core/list',
    'core/image',
    'core/quote',
    'core/separator',
    'create-block/section-block',
    'create-block/slideshow-block',
  );

  // Additional blocks for Pages
  $page_blocks = array(
    'create-block/home-page-hero-block',
    'create-block/priorities-block',
    'create-block/featured-post-block',
  );

  // Additional blocks for Custom Post Types
  $local_page_blocks = array(
    'create-block/economic-impact-block',
    'create-block/guest-community-block',
    'create-block/host-community-block',
  );

  // Check editor context
  if ( ! empty( $editor_context->post ) ) {
    $post_type = $editor_context->post->post_type;

    if ( $post_type === 'page' ) {
      return array_merge( $universally_allowed_blocks, $page_blocks );
    }

    if ( $post_type === 'plc_local_pages' ) {
      return array_merge( $universally_allowed_blocks, $local_page_blocks );
    }

    // Default for other post types
    return $universally_allowed_blocks;
  }

  return $universally_allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Pattern benefits:**
- Base allowlist ensures essential blocks always available
- Post-type-specific blocks appear only where relevant
- Easy to maintain (add blocks to appropriate tier)
- Scales to multiple post types without duplication

**Real-world example:** airbnb-policy-blocks implements 4-tier system (universal, page-type, pages-only, local-pages-only) managing 25+ block types across 3 post types.

## Editor Context Detection

### Pattern Editor Exception

WordPress pattern editor (core/edit-site) requires access to all blocks since patterns may use any registered block. Allowlist logic must detect pattern editor context and permit all blocks.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  $allowed_blocks = array(
    'core/paragraph',
    'core/heading',
    'create-block/section-block',
  );

  // Allow all blocks in pattern editor
  if ( ! empty( $editor_context->name ) && $editor_context->name === 'core/edit-site' ) {
    return true; // true = allow all blocks
  }

  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Why this matters:** Restricting blocks in pattern editor prevents pattern authors from using legitimate blocks in pattern compositions, breaking pattern registration workflow.

**Real-world usage:** airbnb-policy-blocks checks `$editor_context->name === 'core/edit-site'` and returns merged allowlist containing all site blocks (universal + page + local page blocks) for pattern creation.

### Template Editor Detection

WordPress Full Site Editing (FSE) templates require broader block access than post content. Template editor detection enables expanded allowlists for site builders.

```php
if ( ! empty( $editor_context->name ) && strpos( $editor_context->name, 'core/edit-site' ) !== false ) {
  // Template/pattern editor - allow layout blocks
  return array_merge(
    $allowed_blocks,
    array(
      'core/template-part',
      'core/query',
      'core/post-template',
      'core/navigation',
    )
  );
}
```

**FSE-specific blocks:** template-part, query, post-template, post-title, post-date, navigation, site-logo, site-title.

## Core Block Categories

### Selective Core Block Allowlist

WordPress core blocks span multiple categories. Allowlists can restrict to specific core block categories while enabling all custom blocks.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  // Allow essential core blocks only
  $core_essentials = array(
    // Text
    'core/paragraph',
    'core/heading',
    'core/list',
    'core/quote',

    // Media
    'core/image',
    'core/video',
    'core/audio',

    // Design
    'core/separator',
    'core/spacer',
    'core/buttons',
    'core/button',

    // Layout
    'core/group',
    'core/columns',
    'core/column',
  );

  // Get all registered custom blocks
  $registered_blocks = WP_Block_Type_Registry::get_instance()->get_all_registered();
  $custom_blocks = array();

  foreach ( $registered_blocks as $block_name => $block_type ) {
    // Include blocks with custom namespace (not core/, not core-embed/)
    if ( strpos( $block_name, 'core/' ) !== 0 ) {
      $custom_blocks[] = $block_name;
    }
  }

  return array_merge( $core_essentials, $custom_blocks );
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Pattern rationale:**
- Restrict potentially problematic core blocks (code, custom HTML, embeds)
- Allow all custom blocks (project-specific, known safe)
- Maintain essential core functionality (text, media, layout)

**Excluded core blocks:** code, custom-html, shortcode, freeform, missing, all embed variations (twitter, youtube, spotify, etc.).

## User Capability Detection

### Role-Based Allowlists

WordPress allowlists can vary by user capability, enabling power users (administrators) to access all blocks while restricting editors/authors to approved subset.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  // Administrators see all blocks
  if ( current_user_can( 'manage_options' ) ) {
    return true; // No restrictions
  }

  // Editors and Authors see limited blocks
  $allowed_blocks = array(
    'core/paragraph',
    'core/heading',
    'core/list',
    'core/image',
    'create-block/section-block',
  );

  // Authors cannot use custom blocks
  if ( current_user_can( 'edit_posts' ) && ! current_user_can( 'edit_others_posts' ) ) {
    return array_filter( $allowed_blocks, function( $block ) {
      return strpos( $block, 'core/' ) === 0; // Core blocks only
    });
  }

  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Capability-based tiers:**
- `manage_options`: Administrator (no restrictions)
- `edit_others_posts`: Editor (custom blocks allowed)
- `edit_posts`: Author (core blocks only)
- `edit_published_posts`: Contributor (text blocks only)

**Use case:** Multi-author sites where content quality varies by contributor experience level.

## Dynamic Allowlist Generation

### Registry-Based Allowlist

WordPress dynamic allowlists query block registry to programmatically build allowed block arrays based on block metadata patterns (category, keywords, custom attributes).

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  $registry = WP_Block_Type_Registry::get_instance();
  $allowed_blocks = array();

  foreach ( $registry->get_all_registered() as $block_name => $block_type ) {
    // Allow blocks in specific categories
    $allowed_categories = [ 'text', 'media', 'design', 'custom' ];

    if ( in_array( $block_type->category, $allowed_categories, true ) ) {
      $allowed_blocks[] = $block_name;
      continue;
    }

    // Allow blocks with specific support flags
    if ( isset( $block_type->supports['align'] ) && $block_type->supports['align'] === true ) {
      $allowed_blocks[] = $block_name;
      continue;
    }
  }

  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Dynamic criteria:**
- Block category membership
- Support flags (align, anchor, color, spacing)
- Block keywords
- Custom metadata (block.json fields)

**Benefits:** Automatically includes new blocks matching criteria without hardcoded namespace updates.

## Allowlist Maintenance

### Centralized Block List Constants

WordPress allowlists benefit from centralized constant definitions for maintainability. Constants enable reuse across multiple filter implementations.

```php
// Define block lists as constants
define( 'CORE_TEXT_BLOCKS', [
  'core/paragraph',
  'core/heading',
  'core/list',
  'core/quote',
] );

define( 'CORE_MEDIA_BLOCKS', [
  'core/image',
  'core/video',
  'core/audio',
  'core/gallery',
] );

define( 'CORE_LAYOUT_BLOCKS', [
  'core/group',
  'core/columns',
  'core/column',
  'core/separator',
  'core/spacer',
] );

define( 'CUSTOM_SITE_BLOCKS', [
  'create-block/section-block',
  'create-block/slideshow-block',
  'create-block/featured-post-block',
] );

function restrict_blocks( $allowed_block_types, $editor_context ) {
  $allowed_blocks = array_merge(
    CORE_TEXT_BLOCKS,
    CORE_MEDIA_BLOCKS,
    CORE_LAYOUT_BLOCKS,
    CUSTOM_SITE_BLOCKS
  );

  return $allowed_blocks;
}
add_filter( 'allowed_block_types_all', 'restrict_blocks', 10, 2 );
```

**Maintenance benefits:**
- Single location for block list updates
- Semantic grouping improves readability
- Easy to share lists across post types
- Constants available in other plugin code (admin interfaces, documentation)

## Complete Example

### Multi-Tier Post-Type-Aware Allowlist

WordPress production-ready allowlist implementation with tiered blocks, post-type detection, pattern editor exception, and maintainable structure.

```php
<?php
/**
 * Allowed Blocks Filter
 */

// Define block tiers
define( 'UNIVERSAL_BLOCKS', [
  'core/block',
  'core/paragraph',
  'core/heading',
  'core/list',
  'core/image',
  'core/quote',
  'core/separator',
  'core/buttons',
  'core/button',
  'core/group',
  'core/columns',
  'core/column',
  'create-block/section-block',
  'create-block/slideshow-block',
] );

define( 'PAGE_SPECIFIC_BLOCKS', [
  'create-block/home-page-hero-block',
  'create-block/priorities-block',
  'create-block/featured-post-block',
  'create-block/logo-cloud-block',
] );

define( 'LOCAL_PAGE_BLOCKS', [
  'create-block/economic-impact-block',
  'create-block/guest-community-block',
  'create-block/host-community-block',
] );

function airbnb_restrict_blocks( $allowed_block_types, $editor_context ) {
  // Allow all blocks in pattern/template editor
  if ( ! empty( $editor_context->name ) && $editor_context->name === 'core/edit-site' ) {
    return array_merge( UNIVERSAL_BLOCKS, PAGE_SPECIFIC_BLOCKS, LOCAL_PAGE_BLOCKS );
  }

  // Post-type-specific allowlists
  if ( ! empty( $editor_context->post ) ) {
    $post_type = $editor_context->post->post_type;

    // Pages: universal + page-specific blocks
    if ( $post_type === 'page' ) {
      return array_merge( UNIVERSAL_BLOCKS, PAGE_SPECIFIC_BLOCKS );
    }

    // Local pages: universal + local-specific blocks
    if ( $post_type === 'plc_local_pages' ) {
      return array_merge( UNIVERSAL_BLOCKS, LOCAL_PAGE_BLOCKS );
    }

    // Posts and other CPTs: universal blocks only
    return UNIVERSAL_BLOCKS;
  }

  // Default fallback
  return UNIVERSAL_BLOCKS;
}
add_filter( 'allowed_block_types_all', 'airbnb_restrict_blocks', 10, 2 );
```

**Implementation features:**
- Constants for maintainable block lists
- Pattern editor exception (all blocks for pattern creation)
- Three-tier system (universal, page-specific, local-page-specific)
- Post type detection via $editor_context->post
- Fallback to universal blocks for undefined contexts

## Performance Considerations

### Caching Allowlist Results

WordPress allowed_block_types_all filter executes on every editor load. Complex allowlist logic should cache results to prevent repeated computation.

```php
function restrict_blocks( $allowed_block_types, $editor_context ) {
  // Check cache
  $cache_key = 'allowed_blocks';
  if ( ! empty( $editor_context->post ) ) {
    $cache_key .= '_' . $editor_context->post->post_type;
  }

  $cached = wp_cache_get( $cache_key, 'block_editor' );
  if ( false !== $cached ) {
    return $cached;
  }

  // Build allowlist (expensive operation)
  $allowed_blocks = compute_allowed_blocks( $editor_context );

  // Cache for 1 hour
  wp_cache_set( $cache_key, $allowed_blocks, 'block_editor', 3600 );

  return $allowed_blocks;
}
```

**When to cache:**
- Dynamic allowlists querying block registry
- User capability checks hitting database
- Complex conditional logic (multiple post type checks)

**When NOT to cache:**
- Simple hardcoded array returns
- Allowlists already stored as constants

## Common Pitfalls

### Blocking Reusable Blocks

WordPress core/block type enables reusable blocks (synced patterns). Omitting core/block from allowlist prevents editors from using any reusable blocks, breaking expected editor functionality.

**❌ Incorrect:**
```php
$allowed_blocks = array(
  'core/paragraph',
  'core/heading',
  // Missing 'core/block' - breaks reusable blocks
);
```

**✅ Correct:**
```php
$allowed_blocks = array(
  'core/block', // Required for reusable blocks
  'core/paragraph',
  'core/heading',
);
```

### Blocking InnerBlocks

WordPress container blocks (group, columns, section-block) using InnerBlocks require child blocks in allowlist. Blocking child blocks renders container blocks unusable.

**Example:** create-block/section-block uses InnerBlocks allowing any blocks. If allowlist omits core/paragraph, users cannot add paragraphs to sections despite section-block being allowed.

**Solution:** When allowing container blocks, ensure commonly used child blocks (paragraph, heading, image) are also in allowlist.

### Pattern Editor Restrictions

WordPress pattern editor (core/edit-site) must access all site blocks to create patterns. Applying content allowlists to pattern editor breaks pattern creation workflow.

**Solution:** Always check editor context and return comprehensive allowlist (or true) for pattern/template editors.

## Related Patterns

- **Custom Block Categories:** Allowlists complement categories by further restricting available blocks
- **InnerBlocks allowedBlocks:** Block-level restrictions for parent-child relationships
- **User Capabilities:** Role-based access control for editor features
- **Block Patterns:** Patterns require broader block access than post content

## References

- WordPress Block Editor Handbook: allowed_block_types_all Filter - https://developer.wordpress.org/block-editor/reference-guides/filters/block-filters/#allowed_block_types_all
- WP_Block_Editor_Context - https://developer.wordpress.org/reference/classes/wp_block_editor_context/
- Source codebase analysis: 2/5 plugins implement allowed block filtering (40% adoption)
- airbnb-policy-blocks: Tiered allowlist with 25+ blocks across 4 tiers and 3 post types
- rkv-block-editor: Post-type-specific block restrictions
