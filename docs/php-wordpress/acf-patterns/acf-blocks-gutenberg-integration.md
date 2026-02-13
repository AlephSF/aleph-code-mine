# ACF Blocks for Gutenberg Integration

---
title: "ACF Blocks for Gutenberg Integration"
category: "wordpress-acf"
subcategory: "gutenberg-blocks"
tags: ["acf", "gutenberg", "blocks", "block-json", "headless"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Blocks integrate Advanced Custom Fields with WordPress Gutenberg block editor, enabling custom blocks backed by ACF field groups for structured data entry. Airbnb implements 15 ACF blocks using modern block.json registration with complete GraphQL integration. TheKelsey uses minimal ACF blocks (3 instances) with legacy programmatic registration. ACF Blocks are standard pattern for headless WordPress providing structured content APIs.

**Evidence:** 15 ACF blocks in airbnb (logo-cloud, city-portal, faq, featured-post, etc.), 3 in thekelsey. 100% of headless projects analyzed use ACF Blocks extensively.

## Block.json Registration (Modern Approach)

Modern ACF blocks use `block.json` files defining block metadata (name, title, category, icon) alongside PHP render templates or GraphQL-only data blocks. WordPress 6.0+ registers blocks via `register_block_type( __DIR__ . '/build/{block-name}' )`, auto-discovering block.json. Airbnb follows this pattern exclusively.

**Directory Structure:**

```
plugins/
└── airbnb-policy-blocks/
    ├── src/
    │   ├── logo-cloud-block/
    │   │   ├── block.json
    │   │   ├── edit.js
    │   │   ├── save.js
    │   │   └── style.scss
    │   ├── city-portal-block/
    │   │   ├── block.json
    │   │   └── ...
    │   └── [13 more blocks]
    └── airbnb-policy-blocks.php
```

**Block Registration (Plugin Init):**

```php
// airbnb-policy-blocks.php (lines 63-92)
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

**Key Pattern:** Array of block names, loop registration, block.json in each subdirectory.

## Block.json Structure

`block.json` defines block metadata WordPress uses for registration, editor UI, and Gutenberg integration. ACF blocks require minimal block.json (name, title, category) since ACF fields provide data structure. Airbnb blocks use standard WordPress core categories and Dashicons.

**Minimal block.json (ACF Block):**

```json
{
    "$schema": "https://schemas.wp.org/trunk/block.json",
    "apiVersion": 2,
    "name": "create-block/logo-cloud-block",
    "title": "Logo Cloud",
    "category": "widgets",
    "icon": "grid-view",
    "description": "Display a grid of client/partner logos with optional links",
    "supports": {
        "html": false,
        "align": ["wide", "full"]
    },
    "textdomain": "airbnb-policy-blocks",
    "editorScript": "file:./index.js",
    "editorStyle": "file:./index.css",
    "style": "file:./style-index.css"
}
```

**Key Properties:**
- `name` - Unique identifier (`namespace/block-name`)
- `title` - Editor display name
- `category` - Block category (widgets, formatting, layout, theme, embed)
- `icon` - Dashicon name or custom SVG
- `supports` - Block capabilities (alignment, HTML mode, anchors)

## ACF Field Group Location Rules for Blocks

ACF field groups attach to blocks via location rules using `param: "block"` and `value: "namespace/block-name"` matching block.json name. Fields appear in block sidebar or inspector when block is selected in Gutenberg editor.

**Field Group Location (Logo Cloud Block):**

```json
{
    "key": "group_680ad6fe615b8",
    "title": "Logo Cloud Block",
    "fields": [
        {
            "name": "logos",
            "type": "repeater",
            "sub_fields": [
                { "name": "logo", "type": "image" },
                { "name": "link", "type": "url" }
            ]
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
    ],
    "show_in_graphql": 1,
    "graphql_field_name": "logoCloudBlock"
}
```

**Critical:** `value` must exactly match block name from block.json.

## Headless ACF Blocks (No Render Template)

Headless WordPress ACF blocks serve pure data without server-side rendering. Blocks define data structure via ACF fields, expose to GraphQL, and rely on frontend applications (Next.js, React) for rendering. Airbnb follows this pattern for all 15 ACF blocks.

**Headless Block Pattern:**

1. `block.json` defines block metadata
2. ACF field group provides data schema (attached via location rules)
3. No `render.php` or `render` callback (data-only)
4. `show_in_graphql: 1` exposes block data to WPGraphQL
5. Frontend queries blocks via GraphQL and renders UI

**Editor Experience (Headless Blocks):**

- Editors insert blocks in Gutenberg
- ACF fields appear in block inspector/sidebar
- No live preview in editor (shows placeholder or basic preview)
- Real preview happens in frontend application

## GraphQL Block Queries

WPGraphQL exposes Gutenberg blocks as arrays in GraphQL queries, with ACF block data nested in `attributes.data` property. Frontend applications iterate blocks, render components based on block type, and consume ACF field data.

**GraphQL Query (Blocks Array):**

```graphql
query GetPageBlocks {
  page(id: "123") {
    title
    blocks {
      __typename
      name
      ... on CreateBlockLogoCloudBlock {
        attributes {
          data {
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
}
```

**Frontend Rendering (React/Next.js):**

```javascript
const BlockRenderer = ({ blocks }) => {
  return blocks.map((block, index) => {
    if (block.name === 'create-block/logo-cloud-block') {
      return <LogoCloudBlock key={index} data={block.attributes.data} />;
    }
    return null;
  });
};
```

## Traditional ACF Blocks with Render Templates

Traditional WordPress ACF blocks include PHP render templates (`render.php` or `render` callback) for server-side HTML generation. Editors see live preview in Gutenberg matching frontend output. TheKelsey uses this pattern for limited ACF blocks alongside template-heavy architecture.

**Programmatic Registration (Legacy Pattern):**

```php
acf_register_block_type(array(
    'name'            => 'testimonial',
    'title'           => __('Testimonial'),
    'description'     => __('A custom testimonial block.'),
    'render_callback' => 'render_testimonial_block',
    'category'        => 'formatting',
    'icon'            => 'admin-comments',
    'keywords'        => array('testimonial', 'quote'),
));

function render_testimonial_block($block, $content = '', $is_preview = false, $post_id = 0) {
    $author = get_field('author');
    $quote = get_field('quote');
    $company = get_field('company');

    ?>
    <blockquote class="testimonial">
        <p><?php echo esc_html($quote); ?></p>
        <cite>— <?php echo esc_html($author); ?>, <?php echo esc_html($company); ?></cite>
    </blockquote>
    <?php
}
```

**When to Use Render Templates:**
- Traditional PHP WordPress (non-headless)
- Blocks requiring server-side data processing
- Complex editor preview requirements
- Backward compatibility with non-GraphQL sites

## Block Supports (Alignment, HTML, Anchors)

Block.json `supports` property defines block capabilities: alignment options (left, center, right, wide, full), HTML mode toggle, custom anchor IDs, and custom class names. These settings affect Gutenberg editor UI and available block tools.

**Common Supports Configuration:**

```json
{
    "supports": {
        "align": ["wide", "full"],  // Allow wide/full width
        "html": false,               // Disable HTML edit mode
        "anchor": true,              // Allow custom anchor IDs
        "customClassName": true      // Allow custom CSS classes
    }
}
```

**Alignment Options:**
- `["left", "center", "right"]` - Text-level alignment
- `["wide", "full"]` - Layout alignment (requires theme support)
- `true` - All alignments enabled
- `false` or omit - No alignment controls

## Block Categories

WordPress provides default block categories: text, media, design, widgets, theme, embed. Custom plugins can register additional categories for organizational purposes. Airbnb uses standard categories without custom additions.

**Standard Categories:**

```json
{
    "category": "widgets"  // Logo Cloud, Stats, People Grid
}

{
    "category": "layout"  // Section wrappers, columns
}

{
    "category": "theme"  // Theme-specific blocks
}

{
    "category": "formatting"  // Content formatting blocks
}
```

**Custom Category Registration:**

```php
function register_custom_block_category($categories) {
    return array_merge(
        $categories,
        array(
            array(
                'slug'  => 'custom-blocks',
                'title' => __('Custom Blocks', 'textdomain'),
                'icon'  => 'admin-plugins',
            ),
        )
    );
}
add_filter('block_categories_all', 'register_custom_block_category');
```

## Block Icons (Dashicons and Custom SVGs)

Block icons identify blocks in Gutenberg inserter and block list. Dashicons (WordPress icon font) provide 300+ built-in icons. Custom SVG paths enable brand-specific or specialized iconography.

**Dashicon Icon:**

```json
{
    "icon": "grid-view"  // Dashicon name (without "dashicons-" prefix)
}
```

**Custom SVG Icon:**

```json
{
    "icon": {
        "src": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'></path></svg>"
    }
}
```

**Common Dashicons for Blocks:**
- `admin-comments` - Testimonials, reviews
- `grid-view` - Grids, galleries
- `list-view` - Lists, FAQs
- `admin-users` - Team members, people
- `admin-post` - Posts, content
- `admin-site` - Site sections, modules

## Block Whitelisting (Restricting Available Blocks)

WordPress allows whitelisting/blacklisting blocks per post type, preventing editors from using inappropriate blocks. Airbnb implements comprehensive block restrictions ensuring each post type only accesses relevant blocks.

**Block Restriction Pattern (Airbnb):**

```php
// airbnb-policy-blocks.php (lines 152-233)
function restrict_blocks($allowed_block_types, $editor_context) {
  // Universally allowed blocks
  $universally_allowed_blocks = array(
      'core/block',
      'core/paragraph',
      'core/heading',
      'core/image',
      'create-block/section-block',
      'create-block/faq-block',
      'create-block/stat-block',
      // ...
  );

  // Post type-specific blocks
  if ($editor_context->post->post_type === 'page') {
      return array_merge($universally_allowed_blocks, [
          'create-block/home-page-hero-block',
          'create-block/priorities-block',
      ]);
  }

  if ($editor_context->post->post_type === 'plc_local_pages') {
      return array_merge($universally_allowed_blocks, [
          'create-block/economic-impact-block',
          'create-block/host-community-block',
      ]);
  }

  return $universally_allowed_blocks;
}

add_filter('allowed_block_types_all', 'restrict_blocks', 10, 2);
```

**Benefits:**
- Prevents editor confusion (fewer block choices)
- Enforces content strategy (only approved blocks per post type)
- Maintains design consistency (block usage matches design system)

## ACF Block Data Access in PHP

ACF block fields are accessed via standard `get_field()` within render callbacks, with automatic context awareness (no post ID needed). ACF detects block context and retrieves fields accordingly.

**PHP Field Access (Render Callback):**

```php
function render_testimonial_block($block, $content = '', $is_preview = false, $post_id = 0) {
    // Context-aware field access (no post ID needed)
    $author = get_field('author');
    $quote = get_field('quote');
    $company = get_field('company');
    $photo = get_field('photo');

    // Block attributes (alignment, className, anchor)
    $align = $block['align'] ?? '';
    $class = $block['className'] ?? '';
    $anchor = $block['anchor'] ?? '';

    ?>
    <blockquote
        id="<?php echo esc_attr($anchor); ?>"
        class="testimonial <?php echo esc_attr($align); ?> <?php echo esc_attr($class); ?>"
    >
        <?php if ($photo): ?>
            <img src="<?php echo esc_url($photo['url']); ?>" alt="<?php echo esc_attr($author); ?>" />
        <?php endif; ?>
        <p><?php echo esc_html($quote); ?></p>
        <cite>— <?php echo esc_html($author); ?>, <?php echo esc_html($company); ?></cite>
    </blockquote>
    <?php
}
```

## Block.json vs Programmatic Registration

Block.json registration (modern) decentralizes block configuration into JSON files, improving IDE autocomplete, validation, and WordPress core compatibility. Programmatic registration (legacy) centralizes block definitions in PHP with `acf_register_block_type()` function calls. Both approaches work; block.json is future-proof standard.

**Comparison:**

| Aspect | block.json | Programmatic |
|--------|-----------|--------------|
| WordPress version | 5.8+ | 5.0+ |
| Configuration location | JSON file per block | Centralized PHP |
| IDE autocomplete | ✅ Yes | ❌ No |
| Validation | ✅ Schema validation | ❌ Runtime only |
| Performance | ✅ Cached by core | ⚠️ Re-evaluated each load |
| Future compatibility | ✅ Core standard | ⚠️ May deprecate |

**Migration Path:** Airbnb uses block.json exclusively (15 blocks). TheKelsey uses programmatic registration (3 blocks, legacy codebase).

## ACF Blocks and InnerBlocks

ACF blocks can contain InnerBlocks (nested blocks), enabling container blocks with structured content areas. Hero sections might have inner blocks for content, stat blocks might nest multiple metrics. Airbnb Section Block demonstrates this pattern.

**InnerBlocks Pattern:**

```php
function render_section_block($block) {
    $background_color = get_field('background_color');
    $padding = get_field('padding');

    ?>
    <section
        class="custom-section"
        style="background-color: <?php echo esc_attr($background_color); ?>; padding: <?php echo esc_attr($padding); ?>;"
    >
        <InnerBlocks />
    </section>
    <?php
}
```

**Editor Experience:** Section Block acts as container. Editors insert other blocks inside (paragraphs, images, custom blocks).

## Block Variations

Block variations create multiple block options from single block definition with different default attributes. WordPress core provides post, page, and custom post type variations of Query Loop block. Custom blocks can define variations for common configurations.

**Hypothetical Variation (Not in Analyzed Projects):**

```json
{
    "name": "create-block/stat-block",
    "variations": [
        {
            "name": "stat-percentage",
            "title": "Percentage Stat",
            "attributes": {
                "statType": "percentage",
                "suffix": "%"
            }
        },
        {
            "name": "stat-currency",
            "title": "Currency Stat",
            "attributes": {
                "statType": "currency",
                "prefix": "$",
                "suffix": "B"
            }
        }
    ]
}
```

**Use Case:** Single stat block code, multiple inserter options with pre-configured defaults.

## Common Pitfalls

Missing ACF field group location rules cause blocks to appear without fields. Incorrect block names in location rules (`value`) prevent field attachment. GraphQL-only blocks without render callbacks confuse traditional WordPress users. Over-restricting blocks in whitelist breaks editor workflows. Forgetting namespace in block name causes conflicts.

**Anti-Patterns:**

```json
// ❌ Missing namespace (conflicts with other plugins)
{
    "name": "logo-cloud-block"  // Should be "namespace/logo-cloud-block"
}

// ❌ Field group location value doesn't match block name
{
    "location": [
        [{
            "param": "block",
            "value": "create-block/logo-cloud"  // Missing "-block" suffix
        }]
    ]
}

// ❌ GraphQL-only block with render callback (unnecessary overhead)
function render_headless_block() {
    // Empty or placeholder - why include render callback?
}
```

## Related Patterns

- **ACF Field Groups** (provide data structure for blocks)
- **ACF Location Rules** (attach fields to blocks)
- **ACF + GraphQL Integration** (headless block data queries)
- **Gutenberg Block Development** (core block API)
- **Headless WordPress** (blocks as structured content)

## References

- Airbnb: `plugins/airbnb-policy-blocks/` (15 ACF blocks with block.json)
- Airbnb: `airbnb-policy-blocks.php` (lines 63-92: block registration, lines 152-233: block restrictions)
- TheKelsey: Limited ACF block usage (3 programmatic registrations)
- WordPress: [block.json Reference](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/)
- ACF: [ACF Blocks Documentation](https://www.advancedcustomfields.com/resources/blocks/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 6: ACF Blocks)
