---
title: "Dynamic Blocks with Server-Side Rendering"
category: "block-development"
subcategory: "advanced-blocks"
tags: ["wordpress", "gutenberg", "dynamic-blocks", "render-callback", "server-side-rendering"]
stack: "php-wp"
priority: "medium"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "40%"
last_updated: "2026-02-12"
---

# Dynamic Blocks with Server-Side Rendering

## Overview

WordPress dynamic blocks execute PHP rendering logic at runtime instead of saving static HTML markup. Dynamic blocks use render_callback parameter in register_block_type() to specify a PHP function that generates block output, enabling database queries, conditional logic, and PHP template rendering at display time.

**Why this matters:** Static blocks save HTML markup to post_content during editing, requiring block deprecation when markup changes. Dynamic blocks regenerate HTML on every page load, enabling real-time data queries (latest posts, user profiles, API calls) and template updates without block migration.

**Source confidence:** 40% adoption (2/5 plugins analyzed implement dynamic blocks). rkv-block-editor contains 2 dynamic blocks (Carousel, Marketo Form) with OOP base class pattern. airbnb-policy-blocks uses dynamic rendering for 15 ACF blocks.

## Basic Dynamic Block Registration

### PHP render_callback Pattern

WordPress dynamic blocks register via register_block_type() with render_callback parameter pointing to PHP function that returns block HTML. The callback receives attributes array and optional content string.

```php
function render_carousel_block( $attributes, $content ) {
  $images = $attributes['images'] ?? [];

  if ( empty( $images ) ) {
    return '<p>No images selected.</p>';
  }

  ob_start();
  ?>
  <div class="carousel" data-settings='<?php echo esc_attr( json_encode( $attributes['tsSettings'] ) ); ?>'>
    <?php foreach ( $images as $image ) : ?>
      <div class="carousel-slide">
        <?php echo wp_get_attachment_image( $image['id'], 'full' ); ?>
      </div>
    <?php endforeach; ?>
  </div>
  <?php
  return ob_get_clean();
}

register_block_type( 'rkv/carousel', [
  'attributes'      => [
    'images'     => [ 'type' => 'array', 'default' => [] ],
    'tsSettings' => [ 'type' => 'object', 'default' => [] ],
  ],
  'render_callback' => 'render_carousel_block',
] );
```

**render_callback parameters:**
- `$attributes`: Associative array of block attributes
- `$content`: InnerBlocks HTML content (optional, for blocks using InnerBlocks)

**Return value:** String of HTML markup rendered on frontend

### JavaScript save: null Pattern

WordPress dynamic blocks must return null from save function to signal server-side rendering. Returning JSX from save creates static block requiring deprecation strategy when render logic changes.

```javascript
import { registerBlockType } from '@wordpress/blocks';
import Edit from './edit';
import metadata from './block.json';

registerBlockType( metadata.name, {
  edit: Edit,
  save: () => null, // Forces server-side rendering
} );
```

**Key requirement:** save: () => null tells WordPress to invoke render_callback instead of using stored HTML from post_content.

## OOP Base Class Pattern

### Abstract Base Class for Template Hierarchy

WordPress dynamic blocks can use Object-Oriented Programming with abstract base class to standardize render_callback logic across multiple blocks. This pattern implements template hierarchy (child theme → parent theme → plugin) for PHP template overrides.

**inc/classes/Blocks/Base.php:**
```php
<?php
namespace RKV\Blocks;

abstract class Base {
  protected $namespace = 'rkv';
  protected $name;
  protected $attributes;

  public function __construct() {
    $this->set_attributes();
  }

  abstract protected function set_attributes();

  public function run() {
    register_block_type(
      $this->namespace . '/' . $this->name,
      [
        'attributes'      => $this->attributes,
        'render_callback' => [ $this, 'render' ],
      ]
    );
  }

  public function render( $attributes, $content ) {
    // Template hierarchy
    $directories = [
      get_stylesheet_directory() . '/template-parts/blocks/', // Child theme
      get_template_directory() . '/template-parts/blocks/',   // Parent theme
      RKV_BLOCK_EDITOR . 'templates/',                        // Plugin fallback
    ];

    $template = $this->get_template( $this->name, $directories );

    ob_start();
    include $template;
    $html = ob_get_clean();

    return $html;
  }

  private function get_template( $name, $directories ) {
    foreach ( $directories as $dir ) {
      $file = $dir . $name . '.php';
      if ( file_exists( $file ) ) {
        return $file;
      }
    }
    return $directories[2] . $name . '.php'; // Plugin fallback
  }
}
```

### Concrete Block Implementation

WordPress dynamic blocks extend base class by defining block name and attributes. The base class handles registration and rendering automatically.

**inc/classes/Blocks/Carousel.php:**
```php
<?php
namespace RKV\Blocks;

class Carousel extends Base {
  protected $name = 'carousel';

  protected function set_attributes() {
    $this->attributes = [
      'images'     => [
        'type'    => 'array',
        'default' => [],
      ],
      'className'  => [
        'type'    => 'string',
        'default' => '',
      ],
      'tsSettings' => [
        'type'    => 'object',
        'default' => [
          'autoplay'       => true,
          'autoplayTimeout' => 5000,
          'controls'       => true,
          'nav'            => true,
          'loop'           => true,
        ],
      ],
    ];
  }
}
```

**Block initialization:**
```php
$carousel = new \RKV\Blocks\Carousel();
$carousel->run();
```

**Template file (templates/carousel.php):**
```php
<?php
$images = $attributes['images'] ?? [];
$settings = $attributes['tsSettings'] ?? [];
$className = $attributes['className'] ?? '';
?>

<div class="rkv-carousel <?php echo esc_attr( $className ); ?>"
     data-settings='<?php echo esc_attr( json_encode( $settings ) ); ?>'>
  <?php foreach ( $images as $image ) : ?>
    <div class="carousel-slide">
      <?php echo wp_get_attachment_image( $image['id'], 'full' ); ?>
    </div>
  <?php endforeach; ?>
</div>
```

**Pattern benefits:**
- DRY principle: Template hierarchy logic written once
- Theme customization: Child/parent themes override plugin templates
- Testability: Block classes easily unit tested
- Scalability: Add new blocks by extending base class

**Real-world adoption:** 1/6 plugins use OOP pattern (17% confidence), indicating advanced developer skill level required.

## ACF Blocks with Dynamic Rendering

### ACF Block Registration

WordPress ACF (Advanced Custom Fields) Pro provides acf_register_block_type() wrapper that automatically implements dynamic rendering. ACF blocks use PHP templates with $block, $attributes, and ACF field functions.

```php
acf_register_block_type( [
  'name'            => 'testimonial',
  'title'           => __( 'Testimonial' ),
  'description'     => __( 'Customer testimonial block' ),
  'render_template' => 'template-parts/blocks/testimonial.php',
  'category'        => 'airbnb-policy-blocks',
  'icon'            => 'format-quote',
  'keywords'        => [ 'testimonial', 'quote', 'review' ],
  'supports'        => [
    'align'  => false,
    'anchor' => true,
  ],
] );
```

**ACF template file (template-parts/blocks/testimonial.php):**
```php
<?php
$quote = get_field( 'quote' );
$author = get_field( 'author' );
$company = get_field( 'company' );
?>

<blockquote class="testimonial">
  <p><?php echo esc_html( $quote ); ?></p>
  <footer>
    <cite>
      <?php echo esc_html( $author ); ?>
      <?php if ( $company ) : ?>
        <span class="company"><?php echo esc_html( $company ); ?></span>
      <?php endif; ?>
    </cite>
  </footer>
</blockquote>
```

**JavaScript registration (still required):**
```javascript
import { registerBlockType } from '@wordpress/blocks';
import Edit from './edit';
import metadata from './block.json';

registerBlockType( metadata.name, {
  edit: Edit,
  save: () => null, // ACF handles rendering
} );
```

**Real-world usage:** airbnb-policy-blocks contains 15 ACF blocks, representing 58% of total blocks in that plugin (15/26).

## Template Hierarchy Customization

### Theme Override Pattern

WordPress dynamic blocks with template hierarchy enable theme-level customization without modifying plugin code. Themes copy plugin templates to specific directories for override.

**Template search order:**
1. `wp-content/themes/child-theme/template-parts/blocks/carousel.php`
2. `wp-content/themes/parent-theme/template-parts/blocks/carousel.php`
3. `wp-content/plugins/rkv-block-editor/templates/carousel.php`

**Child theme override example:**
```php
<?php
// wp-content/themes/client-theme/template-parts/blocks/carousel.php
// Override carousel with custom styling and Swiper.js instead of tiny-slider

$images = $attributes['images'] ?? [];
?>

<div class="swiper client-carousel">
  <div class="swiper-wrapper">
    <?php foreach ( $images as $image ) : ?>
      <div class="swiper-slide">
        <?php echo wp_get_attachment_image( $image['id'], 'large' ); ?>
      </div>
    <?php endforeach; ?>
  </div>
  <div class="swiper-pagination"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-button-next"></div>
</div>
```

**Use case:** Agencies can customize plugin blocks per client without forking plugin code, enabling core plugin updates while maintaining client-specific presentation.

## Dynamic Data Queries

### WP_Query in render_callback

WordPress dynamic blocks excel at displaying real-time database queries. render_callback can execute WP_Query to fetch latest posts, custom post types, or taxonomies at page load time.

```php
function render_latest_posts_block( $attributes ) {
  $posts_per_page = $attributes['postsPerPage'] ?? 3;
  $category = $attributes['category'] ?? '';

  $query_args = [
    'post_type'      => 'post',
    'posts_per_page' => $posts_per_page,
    'post_status'    => 'publish',
  ];

  if ( $category ) {
    $query_args['category_name'] = $category;
  }

  $query = new WP_Query( $query_args );

  if ( ! $query->have_posts() ) {
    return '<p>No posts found.</p>';
  }

  ob_start();
  ?>
  <div class="latest-posts">
    <?php while ( $query->have_posts() ) : $query->the_post(); ?>
      <article class="post-card">
        <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
        <div class="post-excerpt"><?php the_excerpt(); ?></div>
        <time datetime="<?php echo get_the_date( 'c' ); ?>"><?php the_date(); ?></time>
      </article>
    <?php endwhile; ?>
  </div>
  <?php
  wp_reset_postdata();
  return ob_get_clean();
}
```

**Performance consideration:** WP_Query executes on every page load. Use object caching (wp_cache_set/get) or transients for expensive queries.

**Caching example:**
```php
$cache_key = 'latest_posts_' . md5( serialize( $query_args ) );
$cached = wp_cache_get( $cache_key );

if ( false !== $cached ) {
  return $cached;
}

// ... execute WP_Query and generate HTML ...

wp_cache_set( $cache_key, $html, '', 300 ); // Cache for 5 minutes
return $html;
```

## Edit Component for Dynamic Blocks

### ServerSideRender Component

WordPress ServerSideRender component previews dynamic block output in the editor by calling render_callback via REST API. This provides WYSIWYG preview for blocks that cannot render identical output in JavaScript.

```javascript
import { __ } from '@wordpress/i18n';
import { InspectorControls, useBlockProps } from '@wordpress/block-editor';
import { PanelBody, RangeControl, SelectControl } from '@wordpress/components';
import ServerSideRender from '@wordpress/server-side-render';

export default function Edit({ attributes, setAttributes }) {
  return (
    <>
      <InspectorControls>
        <PanelBody title={ __( 'Settings' ) }>
          <RangeControl
            label={ __( 'Number of Posts' ) }
            value={ attributes.postsPerPage }
            onChange={ ( value ) => setAttributes({ postsPerPage: value }) }
            min={ 1 }
            max={ 12 }
          />
          <SelectControl
            label={ __( 'Category' ) }
            value={ attributes.category }
            options={ [
              { label: 'All Categories', value: '' },
              { label: 'News', value: 'news' },
              { label: 'Blog', value: 'blog' },
            ] }
            onChange={ ( value ) => setAttributes({ category: value }) }
          />
        </PanelBody>
      </InspectorControls>
      <div { ...useBlockProps() }>
        <ServerSideRender
          block="rkv/latest-posts"
          attributes={ attributes }
        />
      </div>
    </>
  );
}
```

**ServerSideRender behavior:**
- Sends POST request to /wp/v2/block-renderer endpoint on attribute change
- Displays loading spinner during AJAX request
- Renders HTML returned by render_callback
- Re-renders on attribute updates

**Performance warning:** ServerSideRender triggers on every keystroke/change. Debounce expensive attributes or implement custom preview logic for better UX.

## When to Use Dynamic Blocks

### Dynamic vs Static Decision Matrix

WordPress blocks should use dynamic rendering when content changes frequently or requires runtime logic. Static blocks work better for fixed content that editors control entirely.

**Use dynamic blocks when:**
- Querying database (latest posts, related content, author profiles)
- Fetching external APIs (weather, stock prices, social feeds)
- Conditional logic based on user state (logged in/out, user roles)
- Content updates independent of post editing (comments count, like counts)
- Template customization needed per site/theme

**Use static blocks when:**
- Content fully controlled by editor (text, images, layouts)
- No database queries required
- Markup changes infrequently
- Performance critical (static HTML faster than PHP execution)
- Content should remain fixed even if database changes

**Real-world split:** airbnb-policy-blocks uses 11 static blocks (sections, layouts) and 15 dynamic ACF blocks (data-driven content). rkv-block-editor uses 2 dynamic blocks (Carousel, Marketo Form) for runtime logic.

## Common Pitfalls

### Forgetting save: () => null

WordPress dynamic blocks that return JSX from save function become static blocks, ignoring render_callback entirely. This creates confusing bugs where PHP changes don't reflect on frontend.

**❌ Incorrect:**
```javascript
save: () => {
  return <div>Static HTML</div>; // Ignores render_callback
}
```

**✅ Correct:**
```javascript
save: () => null, // Forces render_callback execution
```

### Missing wp_reset_postdata()

WordPress render_callback using WP_Query must call wp_reset_postdata() after loop to restore global $post object. Forgetting causes subsequent template tags (the_title, the_content) to reference query posts instead of current post.

**❌ Incorrect:**
```php
$query = new WP_Query( $args );
while ( $query->have_posts() ) : $query->the_post();
  // ... output posts ...
endwhile;
// Missing wp_reset_postdata()
```

**✅ Correct:**
```php
$query = new WP_Query( $args );
while ( $query->have_posts() ) : $query->the_post();
  // ... output posts ...
endwhile;
wp_reset_postdata(); // Reset global $post
```

### Unescaped Attribute Output

WordPress dynamic blocks must escape all attribute values in render_callback to prevent XSS vulnerabilities. Use esc_html(), esc_attr(), esc_url() based on context.

**❌ Incorrect:**
```php
<div class="<?php echo $attributes['className']; ?>"> // XSS risk
```

**✅ Correct:**
```php
<div class="<?php echo esc_attr( $attributes['className'] ); ?>">
```

## Related Patterns

- **block.json Metadata:** Define attributes schema for render_callback
- **ACF Blocks:** Simplified dynamic block registration with ACF Pro
- **InnerBlocks:** Combine with render_callback for dynamic containers
- **REST API:** ServerSideRender uses block-renderer endpoint

## References

- WordPress Block Editor Handbook: Dynamic Blocks - https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/#render
- ServerSideRender Component - https://developer.wordpress.org/block-editor/reference-guides/packages/packages-server-side-render/
- ACF Block Registration - https://www.advancedcustomfields.com/resources/acf_register_block_type/
- Source codebase analysis: 2/5 plugins use dynamic blocks (40% adoption)
- rkv-block-editor: OOP base class pattern with template hierarchy (2 dynamic blocks)
- airbnb-policy-blocks: 15 ACF dynamic blocks (58% of plugin blocks)
