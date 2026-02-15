---
title: "block.json Metadata API for Block Registration"
category: "block-development"
subcategory: "registration"
tags: ["wordpress", "gutenberg", "block-json", "metadata", "registration"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "20%"
last_updated: "2026-02-13"
---

# block.json Metadata API for Block Registration

## Overview

WordPress block.json metadata file serves as the single source of truth for block registration, replacing inline JavaScript metadata in registerBlockType(). The file defines block name, attributes, supports, and asset references, enabling PHP and JavaScript to share the same metadata without duplication.

**Why this matters:** Legacy blocks define metadata twice—once in JavaScript registerBlockType() and again in PHP register_block_type(). This duplication causes inconsistencies and maintenance overhead. The block.json approach centralizes metadata, enables server-side block validation, and unlocks WordPress 6.1+ features like block variations and API version 3.

**Source confidence:** 20% adoption (20 block.json files in airbnb-policy-blocks, 0 in other 4 block plugins using deprecated cgb-scripts). This represents WordPress recommended practice since version 5.8 (2021).


## Required Fields

WordPress block.json requires specific fields for valid block registration. The $schema field enables IDE autocomplete and validation against WordPress specification.

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "create-block/section-block",
  "version": "0.1.0",
  "title": "Section Block",
  "category": "text",
  "icon": "block-default",
  "description": "Section block groups content with a built-in horizontal rule on top."
}
```

**Required field purposes:**
- `apiVersion`: Block API version (use 3 for WordPress 6.3+)
- `name`: Unique block identifier with namespace prefix
- `title`: Human-readable name shown in block inserter
- `category`: Block inserter category (text, media, design, widgets, theme, embed)
- `icon`: Dashicon slug or custom SVG icon

**Validation:** WordPress validates block.json against JSON schema at plugin activation. Invalid files prevent block registration.

## Attributes Definition

WordPress block.json attributes define block data structure with type validation and default values. Attributes automatically sync between JavaScript and PHP without manual prop passing.

```json
{
  "attributes": {
    "jumpLinkText": {
      "type": "string"
    },
    "size": {
      "type": "string",
      "enum": ["default", "small"],
      "default": "default"
    },
    "hideHr": {
      "type": "boolean"
    },
    "removeMargins": {
      "type": "boolean"
    }
  }
}
```

**Type options:**
- `string`: Text values
- `boolean`: True/false toggles
- `number`: Numeric values (integer or float)
- `object`: Nested data structures
- `array`: Lists of values

**Advanced validation:**
- `enum`: Restrict to specific allowed values
- `default`: Fallback value when undefined
- `source`: HTML attribute selector for block parsing (deprecated in API v3)

## Supports Configuration

WordPress block.json supports field controls editor features like HTML editing, alignment options, and spacing controls. These settings integrate with theme.json design system.

```json
{
  "supports": {
    "html": false,
    "align": ["wide", "full"],
    "anchor": true,
    "color": {
      "background": true,
      "text": true,
      "link": false
    },
    "spacing": {
      "margin": true,
      "padding": true
    },
    "typography": {
      "fontSize": true,
      "lineHeight": true
    }
  }
}
```

**Common support options:**
- `html`: Allow editing block as HTML (default: true, disable for security)
- `align`: Enable alignment toolbar (left, center, right, wide, full)
- `anchor`: Allow custom HTML anchor for jump links
- `color`: Expose color picker for background, text, and links
- `spacing`: Enable margin and padding controls
- `typography`: Add font size and line height settings

**Theme integration:** Support values inherit from theme.json settings when not explicitly disabled.

## Asset References

WordPress block.json editorScript and editorStyle fields point to compiled JavaScript and CSS assets. The file:// prefix indicates build output paths relative to block.json location.

```json
{
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css",
  "style": "file:./style.css",
  "viewScript": "file:./view.js"
}
```

**Asset types:**
- `editorScript`: JavaScript loaded in block editor only
- `editorStyle`: CSS loaded in block editor only
- `style`: CSS loaded on both frontend and editor
- `viewScript`: JavaScript loaded on frontend only (for interactive blocks)

**Path resolution:** WordPress resolves `file:./` paths relative to block.json location. For `build/section-block/block.json`, `file:./index.js` resolves to `build/section-block/index.js`.


## Directory-Based Registration

WordPress register_block_type() accepts directory paths containing block.json files. This approach automatically reads metadata and registers blocks without manual attribute definitions.

```php
function airbnb_policy_blocks_block_init() {
  $blocks = [
    'centered-column-block',
    'economic-impact-block',
    'eyebrow-block',
    'flourish-block',
    'guest-community-block',
    'narrow-column-block',
    'related-content-block',
    'section-block',
    'slideshow-block',
  ];

  foreach ( $blocks as $block ) {
    register_block_type( __DIR__ . '/build/' . $block );
  }
}
add_action( 'init', 'airbnb_policy_blocks_block_init' );
```

**Registration flow:**
1. WordPress reads `build/section-block/block.json`
2. Parses attributes, supports, and asset paths
3. Registers block type with name from block.json
4. Enqueues editorScript and editorStyle automatically
5. Makes block available in block inserter

**Benefit:** Single PHP function registers 9+ blocks with ~10 lines of code.

## Asset Enqueuing Automation

WordPress register_block_type() automatically enqueues JavaScript and CSS when using file:// paths in block.json. Manual wp_enqueue_script() calls are unnecessary.

**Automatic enqueuing:**
```json
{
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css"
}
```

WordPress generates:
```php
wp_enqueue_script(
  'create-block-section-block-editor-script',
  plugins_url( 'build/section-block/index.js', __FILE__ ),
  array( 'wp-blocks', 'wp-element', 'wp-block-editor' ), // From index.asset.php
  filemtime( plugin_dir_path( __FILE__ ) . 'build/section-block/index.js' )
);

wp_enqueue_style(
  'create-block-section-block-editor-style',
  plugins_url( 'build/section-block/index.css', __FILE__ ),
  array( 'wp-edit-blocks' ),
  filemtime( plugin_dir_path( __FILE__ ) . 'build/section-block/index.css' )
);
```

**Handles:** WordPress generates unique handles based on block name (namespace + block slug).

## index.asset.php Dependency Loading

WordPress @wordpress/scripts build process generates index.asset.php files containing dependency arrays and version hashes. The register_block_type() function automatically loads these dependencies when block.json references the compiled script.

**Generated index.asset.php:**
```php
<?php return array(
  'dependencies' => array(
    'wp-block-editor',
    'wp-blocks',
    'wp-components',
    'wp-element',
    'wp-i18n'
  ),
  'version' => 'a1b2c3d4e5f6'
);
```

**Automatic loading:**
WordPress looks for `index.asset.php` next to `index.js` referenced in editorScript. The dependencies array becomes the script's $deps parameter in wp_enqueue_script().

**Version caching:** The version hash changes when build output changes, ensuring cache busting without manual version increments.


## Importing block.json Metadata

WordPress blocks import block.json as a JavaScript module to access metadata in registerBlockType(). This ensures JavaScript and PHP use identical block names and settings.

```javascript
/**
 * Registers a new block provided a unique name and an object defining its behavior.
 */
import { registerBlockType } from '@wordpress/blocks';
import './editor.scss';
import Edit from './edit';
import save from './save';
import metadata from './block.json';

/**
 * Every block starts by registering a new block type definition.
 */
registerBlockType( metadata.name, {
  edit: Edit,
  save,
} );
```

**metadata object structure:**
```javascript
{
  name: "create-block/section-block",
  title: "Section Block",
  category: "text",
  attributes: {
    jumpLinkText: { type: "string" },
    size: { type: "string", enum: ["default", "small"], default: "default" }
  },
  supports: { html: false }
}
```

**Benefit:** Changing block.json updates both PHP and JavaScript registration without touching code files.

## Minimal registerBlockType() Calls

WordPress registerBlockType() requires only edit and save functions when metadata comes from block.json. All other properties (title, icon, category, attributes) are inherited from the imported metadata.

**Modern pattern (minimal):**
```javascript
import { registerBlockType } from '@wordpress/blocks';
import metadata from './block.json';
import Edit from './edit';
import save from './save';

registerBlockType( metadata.name, {
  edit: Edit,
  save,
} );
```

**Legacy pattern (verbose):**
```javascript
const { registerBlockType } = wp.blocks;

registerBlockType( 'airbnb/hero-cluster', {
  title: __( 'Airbnb Careers Hero Cluster' ),
  description: __( 'Renders an image and headline in a stylish cluster.' ),
  icon: belo,
  category: 'airbnb-careers',
  keywords: [ __( 'Airbnb Hero Cluster' ) ],
  attributes: {
    primaryImg: { type: 'object', default: { id: null } },
    heading: { type: 'string' },
    buttonText: { type: 'string', default: 'Explore roles' }
  },
  edit: props => { /* ... */ },
  save: props => { /* ... */ }
} );
```

**Code reduction:** Metadata-driven registration reduces registerBlockType() from 15-30 lines to 5-8 lines.


## Server-Side Rendering Configuration

WordPress blocks using render_callback for server-side rendering still benefit from block.json metadata. The PHP register_block_type() call adds render_callback to the metadata-driven registration.

```php
// For ACF blocks with server-side rendering
foreach ( $blocks as $block ) {
  register_block_type( __DIR__ . '/src/' . $block, array(
    'render_callback' => 'airbnb_acf_block_render_callback'
  ) );
}

function airbnb_acf_block_render_callback( $attributes, $content, $block ) {
  // Custom PHP rendering logic
  $template = locate_template( 'template-parts/blocks/' . $block['name'] . '.php' );

  ob_start();
  include $template;
  return ob_get_clean();
}
```

**Combined approach:** block.json defines attributes and supports, PHP adds render_callback for dynamic data.

## save: () => null Pattern

WordPress dynamic blocks using server-side rendering should set save to null in JavaScript. This prevents generating static HTML since PHP render_callback produces the final output.

```javascript
import { registerBlockType } from '@wordpress/blocks';
import metadata from './block.json';
import Edit from './edit';

registerBlockType( metadata.name, {
  edit: Edit,
  save: () => null, // Server-side rendering via PHP
} );
```

**When to use:**
- Blocks querying database (recent posts, custom queries)
- Blocks requiring PHP-only APIs (WP_Query, get_posts)
- ACF blocks using ACF's render_template or render_callback


## Defining Variations in block.json

WordPress block.json supports variations array for creating block presets with predefined attributes. Variations appear as separate options in the block inserter without duplicating code.

```json
{
  "name": "create-block/button",
  "title": "Button",
  "attributes": {
    "style": { "type": "string", "enum": ["primary", "secondary", "outline"] }
  },
  "variations": [
    {
      "name": "primary-button",
      "title": "Primary Button",
      "icon": "button",
      "attributes": { "style": "primary" }
    },
    {
      "name": "outline-button",
      "title": "Outline Button",
      "icon": "button",
      "attributes": { "style": "outline" }
    }
  ]
}
```

**Variation purposes:**
- Pre-configured color schemes (dark mode, light mode)
- Different layout options (grid, list, masonry)
- Predefined content templates (FAQ, testimonial, pricing table)

**Inserter behavior:** Variations appear as separate blocks in the inserter, allowing users to select the appropriate preset.


## Block.json Example Patterns Overview

WordPress block.json patterns vary based on block complexity and feature requirements. Common patterns include simple content blocks, container blocks with InnerBlocks, and dynamic blocks with server rendering.

## Simple Content Block Pattern

WordPress blocks displaying static content use minimal block.json configuration with basic attributes and supports.

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "create-block/eyebrow-block",
  "version": "0.1.0",
  "title": "Eyebrow Block",
  "category": "text",
  "icon": "block-default",
  "description": "Small heading text above main content.",
  "attributes": {
    "text": {
      "type": "string",
      "default": "Eyebrow Text"
    }
  },
  "supports": {
    "html": false,
    "color": {
      "text": true,
      "background": false
    }
  },
  "textdomain": "airbnb-policy-blocks",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css"
}
```

## Container Block with InnerBlocks Pattern

WordPress blocks containing nested content use supports.html: false to prevent direct HTML editing and rely on InnerBlocks for content structure.

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "create-block/section-block",
  "version": "0.1.0",
  "title": "Section Block",
  "category": "text",
  "icon": "block-default",
  "description": "Section block groups content with a built-in horizontal rule on top. Includes option for a page nav jump link.",
  "example": {
    "innerBlocks": [
      {
        "name": "core/heading",
        "attributes": { "content": "Housing Supply" }
      },
      {
        "name": "core/paragraph",
        "attributes": { "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
      }
    ]
  },
  "attributes": {
    "jumpLinkText": { "type": "string" },
    "size": { "type": "string", "enum": ["default", "small"], "default": "default" },
    "hideHr": { "type": "boolean" },
    "removeMargins": { "type": "boolean" }
  },
  "supports": {
    "html": false
  },
  "textdomain": "airbnb-policy-blocks",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css"
}
```

**example field:** Defines preview content shown in block inserter hover state.


## Converting Inline Metadata Overview

WordPress blocks using legacy inline registerBlockType() metadata should extract properties to block.json for maintainability and WordPress 6.6+ compatibility. Migration reduces JavaScript code by 50% and creates single source of truth.

## Legacy Inline Metadata Pattern

WordPress legacy blocks define all metadata inline within registerBlockType() call:

```javascript
const { registerBlockType } = wp.blocks;

registerBlockType( 'thekelsey/slideshow', {
  title: __( 'Slideshow' ),
  description: __( 'Add Slides to a Slideshow' ),
  icon: 'buddicons-activity',
  category: 'thekelsey-custom-blocks',
  keywords: [
    __( 'slideshow carousel' ),
    __( 'slides' ),
  ],
  attributes: {
    imageSize: {
      type: 'string',
      default: 'slideshow-image',
    },
  },
  edit: props => { /* ... */ },
  save: function() { return <InnerBlocks.Content />; }
} );
```

## Migrated block.json Configuration

WordPress modern blocks extract metadata to block.json declarative format:

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "thekelsey/slideshow",
  "version": "1.0.0",
  "title": "Slideshow",
  "description": "Add Slides to a Slideshow",
  "icon": "buddicons-activity",
  "category": "thekelsey-custom-blocks",
  "keywords": ["slideshow carousel", "slides"],
  "attributes": {
    "imageSize": {
      "type": "string",
      "default": "slideshow-image"
    }
  },
  "supports": {
    "html": false
  },
  "editorScript": "file:./index.js"
}
```

## Migrated JavaScript Registration

WordPress migrated blocks import metadata and register with minimal JavaScript:

```javascript
import { registerBlockType } from '@wordpress/blocks';
import metadata from './block.json';
import Edit from './edit';
import save from './save';

registerBlockType( metadata.name, {
  edit: Edit,
  save,
} );
```

**Benefits:**
- 50% reduction in JavaScript code
- Single source of truth for metadata
- Automatic PHP/JS sync
- Easier unit testing (metadata is data, not code)


## Schema Validation

WordPress validates block.json against JSON schema at plugin activation. Invalid files log errors and prevent block registration. Use IDE extensions for real-time validation during development.

**Validation errors:**
```
Warning: Block type "create-block/section-block" is not registered.
Reason: Invalid block.json - Missing required field: "name"
```

**IDE setup for validation:**
```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json"
}
```

**VS Code:** Automatically validates JSON against schema URL, shows inline errors.

## Common Validation Issues

WordPress block.json validation failures often stem from incorrect field types or missing required properties. Check schema documentation for correct format.

**Issue: Invalid apiVersion**
```json
{
  "apiVersion": "3"  // ❌ String instead of number
}
```

**Fix:**
```json
{
  "apiVersion": 3  // ✅ Number
}
```

**Issue: Invalid attribute type**
```json
{
  "attributes": {
    "count": { "type": "integer" }  // ❌ "integer" not valid
  }
}
```

**Fix:**
```json
{
  "attributes": {
    "count": { "type": "number" }  // ✅ Use "number"
  }
}
```


## airbnb-policy-blocks section-block Overview

WordPress airbnb-policy-blocks section-block demonstrates complete block.json usage with attributes, supports, and example preview content for the block inserter.

## section-block block.json Configuration

WordPress section-block block.json includes example preview, enum validation, and boolean attributes:

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "create-block/section-block",
  "version": "0.1.0",
  "title": "Section Block",
  "category": "text",
  "icon": "block-default",
  "description": "Section block groups content with a built-in horizontal rule on top. Includes option for a page nav jump link.",
  "example": {
    "innerBlocks": [
      {
        "name": "core/separator",
        "attributes": { "content": "Housing Supply" }
      },
      {
        "name": "core/heading",
        "attributes": { "content": "Housing Supply" }
      },
      {
        "name": "core/paragraph",
        "attributes": { "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent et eros eu felis." }
      }
    ]
  },
  "attributes": {
    "jumpLinkText": {
      "type": "string"
    },
    "size": {
      "type": "string",
      "enum": [ "default", "small" ],
      "default": "default"
    },
    "hideHr": {
      "type": "boolean"
    },
    "removeMargins": {
      "type": "boolean"
    }
  },
  "supports": {
    "html": false
  },
  "textdomain": "airbnb-policy-blocks",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css"
}
```

## section-block PHP Registration

WordPress directory-based registration reads block.json automatically:

```php
register_block_type( __DIR__ . '/build/section-block' );
```

## section-block JavaScript Registration

WordPress block registration imports metadata and registers edit/save functions:

```javascript
import { registerBlockType } from '@wordpress/blocks';
import metadata from './block.json';
import Edit from './edit';
import save from './save';

registerBlockType( metadata.name, {
  edit: Edit,
  save,
} );
```

**Result:** 7 lines of code register a fully-featured block with 4 attributes, InnerBlocks support, and sidebar settings.

## References

- Block Metadata Documentation: https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/
- JSON Schema Specification: https://schemas.wp.org/trunk/block.json
- Block API Reference: https://developer.wordpress.org/block-editor/reference-guides/block-api/
- register_block_type() Function: https://developer.wordpress.org/reference/functions/register_block_type/

## Related Documentation

- `wp-scripts-build-pipeline.md` - Build tooling that processes block.json
- `edit-save-component-pattern.md` - Edit and save components referenced in registration
- `dynamic-blocks-server-rendering.md` - Using block.json with render_callback
- `block-patterns-and-styles.md` - Block variations and style presets
