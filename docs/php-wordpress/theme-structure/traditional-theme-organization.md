---
title: "Traditional WordPress Theme Organization with inc/ Directory Pattern"
category: "theme-structure"
subcategory: "code-organization"
tags: ["traditional", "inc-directory", "template-hierarchy", "functions-php", "classic-themes"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-13"
---

# Traditional WordPress Theme Organization with inc/ Directory Pattern

## Overview

Traditional WordPress theme architecture follows classic template hierarchy with PHP files in theme root and modular code organization in `inc/` directory. **50% of analyzed themes** (7 of 14) use `inc/` directory pattern for separating concerns, while remaining 43% either use Sage framework or minimal structure.

Traditional themes comprise **71% of analyzed themes** (10 of 14), demonstrating continued prevalence despite modern framework adoption. Pattern works well for simple-to-medium complexity sites (10-50 templates) where team familiarity with WordPress template hierarchy outweighs benefits of MVC frameworks.

**Key Characteristics:**
- Template files in theme root (`archive.php`, `single.php`, `page.php`)
- Code organization in `inc/` directory (CPT registration, custom functions, widgets)
- Manual asset loading via `wp_enqueue_scripts`
- Direct WordPress hooks and filters in `functions.php`
- No build tools or compilation required (optional Gulp/webpack)

## Directory Structure

Traditional theme structure mirrors WordPress template hierarchy with templates in root, modular code in `inc/`, and static assets in subdirectories.

```
airbnbtech/ (traditional theme example)
├── inc/                          # Code organization
│   ├── careers-setup.php         # Careers CPT registration
│   ├── events-setup.php          # Events CPT registration
│   ├── teams-setup.php           # Teams CPT registration
│   ├── research-setup.php        # Research CPT registration
│   ├── custom-functions.php      # Helper functions
│   ├── customizer.php            # Theme Customizer API
│   ├── template-tags.php         # Template helper functions
│   ├── template-functions.php    # Complex template logic
│   └── widgets/                  # Custom widget classes
│       ├── recent-posts-widget.php
│       └── facebook-like-widget.php
├── css/                          # Stylesheets
│   ├── styles.css                # Main stylesheet
│   └── admin.css                 # Admin styles
├── js/                           # JavaScript files
│   ├── site-scripts.js           # Frontend JavaScript
│   └── custom-admin.js           # Admin JavaScript
├── images/                       # Image assets
│   ├── logo.png
│   └── icons/
├── fonts/                        # Web fonts
│   ├── custom-font.woff2
│   └── custom-font.woff
├── functions.php                 # Main theme file
├── style.css                     # Theme header + critical CSS
├── header.php                    # Site header
├── footer.php                    # Site footer
├── sidebar.php                   # Primary sidebar
├── index.php                     # Fallback template
├── front-page.php                # Homepage template
├── archive.php                   # Archive pages
├── single.php                    # Single post
├── page.php                      # Static pages
├── 404.php                       # Error page
├── search.php                    # Search results
├── author.php                    # Author archive
├── category.php                  # Category archive
├── tag.php                       # Tag archive
├── attachment.php                # Media attachment
└── comments.php                  # Comments template
```

**Compared to Sage:** No `app/`, `resources/`, `config/`, `dist/`, or `vendor/` directories. All PHP in root or `inc/`.

## functions.php Structure

Central theme file loads `inc/` modules, registers theme support, enqueues assets, and defines global configuration. Organized with clear sections using comments.

```php
<?php
/**
 * Theme Name: Airbnb Tech
 * Main functions file
 */

/**
 * =============================================================================
 * WORDPRESS CLEANUP (Security & Performance)
 * =============================================================================
 */

// Remove emoji detection script
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('admin_print_scripts', 'print_emoji_detection_script');
remove_action('wp_print_styles', 'print_emoji_styles');
remove_action('admin_print_styles', 'print_emoji_styles');

// Remove version number from head (security)
remove_action('wp_head', 'wp_generator');

// Remove REST API links from head (reduces HTML bloat)
remove_action('wp_head', 'rest_output_link_wp_head', 10);
remove_action('wp_head', 'wp_oembed_add_discovery_links', 10);

// Remove query strings from static resources (CDN caching)
function cleanup_query_string($src) {
    $parts = explode('?', $src);
    return $parts[0];
}
add_filter('script_loader_src', 'cleanup_query_string', 15, 1);
add_filter('style_loader_src', 'cleanup_query_string', 15, 1);

/**
 * =============================================================================
 * THEME SETUP
 * =============================================================================
 */

// Add theme support features
add_theme_support('automatic-feed-links');
add_theme_support('title-tag');
add_theme_support('post-thumbnails');

// Add excerpt support to pages
add_post_type_support('page', 'excerpt');

// Enable tags on pages for better taxonomy
function enable_tags_for_pages() {
    register_taxonomy_for_object_type('post_tag', 'page');
}
add_action('init', 'enable_tags_for_pages');

/**
 * =============================================================================
 * LOAD INC/ MODULES
 * =============================================================================
 */

require get_template_directory() . '/inc/careers-setup.php';
require get_template_directory() . '/inc/events-setup.php';
require get_template_directory() . '/inc/teams-setup.php';
require get_template_directory() . '/inc/research-setup.php';
require get_template_directory() . '/inc/custom-functions.php';
require get_template_directory() . '/inc/customizer.php';

/**
 * =============================================================================
 * ASSET LOADING
 * =============================================================================
 */

function site_styles() {
    wp_register_style('site-styles',
        get_template_directory_uri() . '/css/styles.css',
        array(), '1.0', 'all');
    wp_enqueue_style('site-styles');
}
add_action('wp_enqueue_scripts', 'site_styles');

function site_scripts() {
    wp_enqueue_script('sitescripts',
        get_template_directory_uri() . '/js/site-scripts.js',
        array('jquery'), NULL, true);

    // Localize AJAX endpoints
    wp_localize_script('sitescripts', 'wp_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('ajax-nonce')
    ));
}
add_action('wp_enqueue_scripts', 'site_scripts');

function enqueue_custom_admin_scripts() {
    wp_enqueue_media();  // Media library for admin
    wp_enqueue_script('custom-admin-script',
        get_template_directory_uri() . '/js/custom-admin.js',
        array('jquery'), null, true);
}
add_action('admin_enqueue_scripts', 'enqueue_custom_admin_scripts');

/**
 * =============================================================================
 * HELPER FUNCTIONS
 * =============================================================================
 */

// Format page title
function page_title($title, $sep) {
    if (is_feed()) {
        return $title;
    }

    if (is_home() || is_front_page()) {
        $title = get_bloginfo('name', 'display') . " | " .
                 get_bloginfo('description', 'display');
    } else if (is_post_type_archive('resources')) {
        $title = "Resource Library | " . get_bloginfo('name', 'display');
    } else {
        $title = get_the_title() . " | " . get_bloginfo('name', 'display');
    }

    return $title;
}
add_filter('wp_title', 'page_title', 10, 2);

// Limit excerpt word count
function excerpt_limit($wordstring, $word_limit) {
    $words = explode(' ', $wordstring, ($word_limit + 1));
    if (count($words) > $word_limit) {
        array_pop($words);
        return implode(' ', $words) . '...';
    }
    return implode(' ', $words);
}

/**
 * =============================================================================
 * NAVIGATION MENUS
 * =============================================================================
 */

register_nav_menus(array(
    'primary' => __('Primary Menu'),
    'footer' => __('Footer Menu')
));
```

**Organization Pattern:**
1. **Security/Cleanup:** Remove unnecessary WordPress features
2. **Theme Setup:** Register theme support, post type support
3. **Load Modules:** Require `inc/` files for specific features
4. **Asset Loading:** Enqueue styles and scripts
5. **Helper Functions:** Utility functions for templates
6. **Navigation:** Register menus

## inc/ Directory Organization

Separate feature-specific code into dedicated files in `inc/` directory, loaded via `require` in `functions.php`. Each file handles single responsibility (CPT registration, widgets, customizer, helpers).

## CPT Registration (inc/careers-setup.php)

```php
<?php
/**
 * Register Careers Custom Post Type
 */

function register_careers_cpt() {
    $labels = array(
        'name' => 'Careers',
        'singular_name' => 'Career',
        'add_new' => 'Add New Career',
        'add_new_item' => 'Add New Career',
        'edit_item' => 'Edit Career',
        'new_item' => 'New Career',
        'view_item' => 'View Career',
        'search_items' => 'Search Careers',
        'not_found' => 'No careers found',
        'not_found_in_trash' => 'No careers found in trash',
    );

    $args = array(
        'labels' => $labels,
        'public' => true,
        'has_archive' => true,
        'menu_position' => 5,
        'menu_icon' => 'dashicons-businessman',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'careers'),
    );

    register_post_type('career', $args);
}
add_action('init', 'register_careers_cpt');
```

**Pattern:** One file per CPT or taxonomy. Prevents `functions.php` from becoming monolithic.

## Custom Functions (inc/custom-functions.php)

```php
<?php
/**
 * Theme-specific helper functions
 */

/**
 * Get related posts by category
 *
 * @param int $post_id Current post ID
 * @param int $limit Number of posts to return
 * @return WP_Post[] Array of post objects
 */
function get_related_posts($post_id, $limit = 3) {
    $categories = wp_get_post_categories($post_id);

    if (empty($categories)) {
        return array();
    }

    $args = array(
        'category__in' => $categories,
        'post__not_in' => array($post_id),
        'posts_per_page' => $limit,
        'ignore_sticky_posts' => 1,
    );

    return get_posts($args);
}

/**
 * Check if page has sidebar
 *
 * @return bool
 */
function has_sidebar() {
    return !in_array(true, array(
        is_404(),
        is_front_page(),
        is_page_template('template-fullwidth.php'),
    ));
}

/**
 * Format reading time
 *
 * @param string $content Post content
 * @return string Reading time (e.g., "5 min read")
 */
function calculate_reading_time($content) {
    $word_count = str_word_count(strip_tags($content));
    $reading_time = ceil($word_count / 250);  // 250 WPM average

    return $reading_time . ' min read';
}
```

**Pattern:** Reusable functions called from templates, not WordPress hooks.

## Template Tags (inc/template-tags.php)

```php
<?php
/**
 * Template tags for use in templates
 */

/**
 * Display post meta (author, date, categories)
 */
function display_post_meta() {
    ?>
    <div class="post-meta">
        <span class="author">
            By <?php the_author_posts_link(); ?>
        </span>
        <span class="date">
            <?php echo get_the_date(); ?>
        </span>
        <span class="categories">
            <?php the_category(', '); ?>
        </span>
    </div>
    <?php
}

/**
 * Display breadcrumbs
 */
function display_breadcrumbs() {
    if (is_front_page()) {
        return;
    }

    echo '<nav class="breadcrumbs">';
    echo '<a href="' . home_url('/') . '">Home</a> &raquo; ';

    if (is_category() || is_single()) {
        the_category(' &raquo; ');
        if (is_single()) {
            echo " &raquo; ";
            the_title();
        }
    } elseif (is_page()) {
        echo the_title();
    }

    echo '</nav>';
}

/**
 * Display social share buttons
 */
function display_social_share() {
    $url = urlencode(get_permalink());
    $title = urlencode(get_the_title());
    ?>
    <div class="social-share">
        <a href="https://twitter.com/share?url=<?php echo $url; ?>&text=<?php echo $title; ?>"
           target="_blank">Share on Twitter</a>
        <a href="https://www.facebook.com/sharer.php?u=<?php echo $url; ?>"
           target="_blank">Share on Facebook</a>
        <a href="https://www.linkedin.com/shareArticle?url=<?php echo $url; ?>&title=<?php echo $title; ?>"
           target="_blank">Share on LinkedIn</a>
    </div>
    <?php
}
```

**Usage in Templates:**
```php
<?php get_header(); ?>

<article>
    <h1><?php the_title(); ?></h1>

    <?php display_post_meta(); ?>
    <?php display_breadcrumbs(); ?>

    <div class="content">
        <?php the_content(); ?>
    </div>

    <?php display_social_share(); ?>
</article>

<?php get_footer(); ?>
```

## Theme Customizer (inc/customizer.php)

```php
<?php
/**
 * Theme Customizer settings
 */

function customize_register($wp_customize) {
    // Add header section
    $wp_customize->add_section('header_settings', array(
        'title' => 'Header Settings',
        'priority' => 30,
    ));

    // Logo upload
    $wp_customize->add_setting('header_logo', array(
        'default' => '',
        'sanitize_callback' => 'esc_url_raw',
    ));

    $wp_customize->add_control(new WP_Customize_Image_Control($wp_customize, 'header_logo', array(
        'label' => 'Header Logo',
        'section' => 'header_settings',
        'settings' => 'header_logo',
    )));

    // Header CTA text
    $wp_customize->add_setting('header_cta_text', array(
        'default' => 'Get Started',
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control('header_cta_text', array(
        'label' => 'Call to Action Text',
        'section' => 'header_settings',
        'type' => 'text',
    ));

    // Header CTA URL
    $wp_customize->add_setting('header_cta_url', array(
        'default' => '',
        'sanitize_callback' => 'esc_url_raw',
    ));

    $wp_customize->add_control('header_cta_url', array(
        'label' => 'Call to Action URL',
        'section' => 'header_settings',
        'type' => 'url',
    ));
}
add_action('customize_register', 'customize_register');
```

**Usage in header.php:**
```php
<?php if (get_theme_mod('header_logo')) : ?>
    <img src="<?php echo esc_url(get_theme_mod('header_logo')); ?>" alt="Logo">
<?php endif; ?>

<?php if (get_theme_mod('header_cta_url')) : ?>
    <a href="<?php echo esc_url(get_theme_mod('header_cta_url')); ?>" class="cta-button">
        <?php echo esc_html(get_theme_mod('header_cta_text', 'Get Started')); ?>
    </a>
<?php endif; ?>
```

## Custom Widgets (inc/widgets/recent-posts-widget.php)

```php
<?php
/**
 * Custom Recent Posts Widget
 */

class Custom_Recent_Posts_Widget extends WP_Widget {

    public function __construct() {
        parent::__construct(
            'custom_recent_posts',
            'Custom Recent Posts',
            array('description' => 'Display recent posts with thumbnails')
        );
    }

    public function widget($args, $instance) {
        echo $args['before_widget'];

        $title = !empty($instance['title']) ? $instance['title'] : 'Recent Posts';
        echo $args['before_title'] . esc_html($title) . $args['after_title'];

        $count = !empty($instance['count']) ? intval($instance['count']) : 5;

        $recent_posts = get_posts(array(
            'numberposts' => $count,
            'post_status' => 'publish',
        ));

        if (!empty($recent_posts)) {
            echo '<ul class="recent-posts-widget">';
            foreach ($recent_posts as $post) {
                ?>
                <li>
                    <?php if (has_post_thumbnail($post)) : ?>
                        <div class="thumbnail">
                            <?php echo get_the_post_thumbnail($post, 'thumbnail'); ?>
                        </div>
                    <?php endif; ?>
                    <div class="post-info">
                        <a href="<?php echo get_permalink($post); ?>">
                            <?php echo esc_html($post->post_title); ?>
                        </a>
                        <span class="date"><?php echo get_the_date('', $post); ?></span>
                    </div>
                </li>
                <?php
            }
            echo '</ul>';
        }

        echo $args['after_widget'];
    }

    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : '';
        $count = !empty($instance['count']) ? intval($instance['count']) : 5;
        ?>
        <p>
            <label for="<?php echo $this->get_field_id('title'); ?>">Title:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('title'); ?>"
                   name="<?php echo $this->get_field_name('title'); ?>" type="text"
                   value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('count'); ?>">Number of posts:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('count'); ?>"
                   name="<?php echo $this->get_field_name('count'); ?>" type="number"
                   value="<?php echo esc_attr($count); ?>" min="1" max="20">
        </p>
        <?php
    }

    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = !empty($new_instance['title']) ?
            sanitize_text_field($new_instance['title']) : '';
        $instance['count'] = !empty($new_instance['count']) ?
            intval($new_instance['count']) : 5;
        return $instance;
    }
}

function register_custom_recent_posts_widget() {
    register_widget('Custom_Recent_Posts_Widget');
}
add_action('widgets_init', 'register_custom_recent_posts_widget');
```

## Template File Structure

WordPress template hierarchy determines which template file loads. Traditional themes place all templates in root directory with specific filenames that WordPress recognizes.

## Archive Template (archive.php)

```php
<?php get_header(); ?>

<div class="container">
    <div class="content-area">

        <?php if (have_posts()) : ?>

            <header class="page-header">
                <?php
                the_archive_title('<h1 class="page-title">', '</h1>');
                the_archive_description('<div class="archive-description">', '</div>');
                ?>
            </header>

            <div class="posts-grid">
                <?php while (have_posts()) : the_post(); ?>

                    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                        <?php if (has_post_thumbnail()) : ?>
                            <div class="post-thumbnail">
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('medium'); ?>
                                </a>
                            </div>
                        <?php endif; ?>

                        <header class="entry-header">
                            <h2 class="entry-title">
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_title(); ?>
                                </a>
                            </h2>

                            <?php display_post_meta(); ?>
                        </header>

                        <div class="entry-summary">
                            <?php the_excerpt(); ?>
                        </div>

                        <a href="<?php the_permalink(); ?>" class="read-more">
                            Read More
                        </a>
                    </article>

                <?php endwhile; ?>
            </div>

            <?php
            the_posts_pagination(array(
                'prev_text' => '&laquo; Previous',
                'next_text' => 'Next &raquo;',
            ));
            ?>

        <?php else : ?>

            <p>No posts found.</p>

        <?php endif; ?>

    </div>

    <?php if (has_sidebar()) : ?>
        <?php get_sidebar(); ?>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
```

**Template Hierarchy:** WordPress checks for specific templates in order: `category-{slug}.php`, `category-{id}.php`, `category.php`, `archive.php`, `index.php`.

## Single Post Template (single.php)

```php
<?php get_header(); ?>

<div class="container">
    <div class="content-area">

        <?php while (have_posts()) : the_post(); ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

                <header class="entry-header">
                    <h1 class="entry-title"><?php the_title(); ?></h1>
                    <?php display_post_meta(); ?>
                    <?php display_breadcrumbs(); ?>
                </header>

                <?php if (has_post_thumbnail()) : ?>
                    <div class="featured-image">
                        <?php the_post_thumbnail('large'); ?>
                    </div>
                <?php endif; ?>

                <div class="entry-content">
                    <?php the_content(); ?>

                    <?php
                    wp_link_pages(array(
                        'before' => '<div class="page-links">Pages: ',
                        'after' => '</div>',
                    ));
                    ?>
                </div>

                <footer class="entry-footer">
                    <?php display_social_share(); ?>

                    <div class="tags">
                        <?php the_tags('Tags: ', ', ', ''); ?>
                    </div>
                </footer>

            </article>

            <?php
            // Related posts
            $related_posts = get_related_posts(get_the_ID(), 3);
            if (!empty($related_posts)) :
                ?>
                <section class="related-posts">
                    <h2>Related Posts</h2>
                    <div class="related-posts-grid">
                        <?php foreach ($related_posts as $post) : setup_postdata($post); ?>
                            <article>
                                <?php if (has_post_thumbnail($post)) : ?>
                                    <a href="<?php the_permalink($post); ?>">
                                        <?php echo get_the_post_thumbnail($post, 'medium'); ?>
                                    </a>
                                <?php endif; ?>
                                <h3>
                                    <a href="<?php the_permalink($post); ?>">
                                        <?php echo get_the_title($post); ?>
                                    </a>
                                </h3>
                            </article>
                        <?php endforeach; wp_reset_postdata(); ?>
                    </div>
                </section>
            <?php endif; ?>

            <?php
            // Comments
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;
            ?>

        <?php endwhile; ?>

    </div>

    <?php if (has_sidebar()) : ?>
        <?php get_sidebar(); ?>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
```

## Page Template (page.php)

```php
<?php get_header(); ?>

<div class="container">
    <div class="content-area">

        <?php while (have_posts()) : the_post(); ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

                <header class="entry-header">
                    <h1 class="entry-title"><?php the_title(); ?></h1>
                    <?php display_breadcrumbs(); ?>
                </header>

                <div class="entry-content">
                    <?php the_content(); ?>
                </div>

            </article>

        <?php endwhile; ?>

    </div>

    <?php if (has_sidebar()) : ?>
        <?php get_sidebar(); ?>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
```

## Custom Page Template (template-fullwidth.php)

```php
<?php
/**
 * Template Name: Full Width
 * Description: Full width page template without sidebar
 */

get_header();
?>

<div class="container-fluid">
    <div class="fullwidth-content">

        <?php while (have_posts()) : the_post(); ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class('fullwidth'); ?>>

                <header class="entry-header">
                    <h1 class="entry-title"><?php the_title(); ?></h1>
                </header>

                <div class="entry-content">
                    <?php the_content(); ?>
                </div>

            </article>

        <?php endwhile; ?>

    </div>
</div>

<?php get_footer(); ?>
```

**Template Name Comment:** WordPress detects custom templates via `Template Name:` comment at top of file. Shows in Page Attributes meta box.

## Template Parts Pattern

Break repeated markup into reusable template parts loaded via `get_template_part()`. Reduces duplication and improves maintainability.

## Using Template Parts

```php
// archive.php
<?php while (have_posts()) : the_post(); ?>

    <?php
    /*
     * Load content-{post_type}.php or content.php
     * For post_type=post: loads content.php
     * For post_type=career: loads content-career.php
     */
    get_template_part('content', get_post_type());
    ?>

<?php endwhile; ?>
```

## Template Part File (content.php)

```php
<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

    <?php if (has_post_thumbnail()) : ?>
        <div class="post-thumbnail">
            <a href="<?php the_permalink(); ?>">
                <?php the_post_thumbnail('medium'); ?>
            </a>
        </div>
    <?php endif; ?>

    <header class="entry-header">
        <h2 class="entry-title">
            <a href="<?php the_permalink(); ?>">
                <?php the_title(); ?>
            </a>
        </h2>
        <?php display_post_meta(); ?>
    </header>

    <div class="entry-summary">
        <?php the_excerpt(); ?>
    </div>

    <a href="<?php the_permalink(); ?>" class="read-more">
        Read More
    </a>

</article>
```

## Custom Post Type Template Part (content-career.php)

```php
<article id="post-<?php the_ID(); ?>" <?php post_class('career-listing'); ?>>

    <header class="entry-header">
        <h2 class="entry-title">
            <a href="<?php the_permalink(); ?>">
                <?php the_title(); ?>
            </a>
        </h2>

        <div class="career-meta">
            <?php
            $location = get_post_meta(get_the_ID(), 'location', true);
            $department = get_post_meta(get_the_ID(), 'department', true);
            ?>
            <span class="location"><?php echo esc_html($location); ?></span>
            <span class="department"><?php echo esc_html($department); ?></span>
        </div>
    </header>

    <div class="entry-summary">
        <?php the_excerpt(); ?>
    </div>

    <a href="<?php the_permalink(); ?>" class="apply-button">
        Apply Now
    </a>

</article>
```

**Analyzed Usage:** `blogs-atairbnb` theme uses `get_template_part()` 8 times for content variations (content-page, content-search, content-none).

## Asset Management (Manual Enqueue)

Traditional themes manually register and enqueue stylesheets and scripts without build tools. No minification, concatenation, or cache-busting unless manually added.

```php
/**
 * Enqueue stylesheets
 */
function site_styles() {
    // Main stylesheet
    wp_register_style('site-styles',
        get_template_directory_uri() . '/css/styles.css',
        array(),  // Dependencies
        '1.0',    // Version (manual cache-busting)
        'all'     // Media type
    );
    wp_enqueue_style('site-styles');

    // Google Fonts
    wp_enqueue_style('google-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap',
        array(),
        null
    );

    // Conditional admin styles
    if (is_admin()) {
        wp_enqueue_style('admin-styles',
            get_template_directory_uri() . '/css/admin.css',
            array(),
            '1.0'
        );
    }
}
add_action('wp_enqueue_scripts', 'site_styles');

/**
 * Enqueue scripts
 */
function site_scripts() {
    // Main JavaScript (footer placement)
    wp_enqueue_script('sitescripts',
        get_template_directory_uri() . '/js/site-scripts.js',
        array('jquery'),  // Depends on jQuery
        NULL,             // No version (use file modification time)
        true              // Load in footer
    );

    // Localize script with PHP data
    wp_localize_script('sitescripts', 'wp_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('ajax-nonce'),
        'home_url' => home_url('/'),
    ));

    // Conditional comment reply script
    if (is_single() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'site_scripts');
```

**Limitations:**
- Manual version management (forget to update → stale cache)
- No minification (serves full CSS/JS in production)
- No concatenation (multiple HTTP requests)
- No critical CSS extraction
- No tree-shaking unused code

**Alternative:** See `build-tool-configuration.md` for webpack/Gulp integration.

## Performance Optimizations

Traditional themes manually optimize WordPress output by removing unnecessary features, query strings, and bloat. No automated build pipeline unless Gulp/webpack added.

```php
/**
 * Remove emoji detection script (reduces page weight by ~15 KB)
 */
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('admin_print_scripts', 'print_emoji_detection_script');
remove_action('wp_print_styles', 'print_emoji_styles');
remove_action('admin_print_styles', 'print_emoji_styles');

/**
 * Remove version numbers from head (security + clean HTML)
 */
remove_action('wp_head', 'wp_generator');

/**
 * Remove post relational links (rarely used, bloats <head>)
 */
remove_action('wp_head', 'start_post_rel_link');
remove_action('wp_head', 'index_rel_link');
remove_action('wp_head', 'adjacent_posts_rel_link');

/**
 * Remove REST API links from head (unless using REST API)
 */
remove_action('wp_head', 'rest_output_link_wp_head', 10);
remove_action('wp_head', 'wp_oembed_add_discovery_links', 10);
remove_action('template_redirect', 'rest_output_link_header', 11, 0);

/**
 * Remove query strings from static resources (improves CDN caching)
 * Converts /style.css?ver=5.8 to /style.css
 */
function cleanup_query_string($src) {
    $parts = explode('?', $src);
    return $parts[0];
}
add_filter('script_loader_src', 'cleanup_query_string', 15, 1);
add_filter('style_loader_src', 'cleanup_query_string', 15, 1);

/**
 * Remove Live Writer manifest (obsolete service)
 */
remove_action('wp_head', 'wlwmanifest_link');

/**
 * Clean up excerpt formatting (remove auto <p> tags)
 */
remove_filter('the_excerpt', 'wpautop');
```

**Impact:** Reduces HTML from ~8 KB to ~5 KB by removing unused WordPress defaults.

## When to Use Traditional vs Sage

**Use Traditional When:**
- Simple blog or marketing site (10-30 templates)
- Team unfamiliar with Laravel/Blade/Composer
- Client needs to edit templates directly (no build step)
- Minimal asset compilation needs (hand-written CSS/JS)
- Budget constraints (no time for framework learning curve)
- Plugin compatibility issues with Blade

**Use Sage When:**
- Content-heavy site with complex template logic (50+ templates)
- Need template inheritance, components, partials
- Want modern asset pipeline (webpack, cache-busting, minification)
- Team familiar with MVC and Laravel
- Budget allows for setup time (4-8 hours initial, 2-5 days learning curve)

**Analyzed Distribution:** 50% use `inc/` directory pattern (7 of 14 themes). Combined with non-modular traditional themes, 71% use traditional architecture vs 29% Sage.

## Migration Path (Traditional → Sage)

**Step 1:** Create Sage theme with `composer create-project roots/sage`
**Step 2:** Convert templates to Blade (`.php` → `.blade.php`)
**Step 3:** Move `header.php`, `footer.php` to `resources/views/layouts/app.blade.php`
**Step 4:** Extract repeated markup to `resources/views/partials/`
**Step 5:** Move logic from templates to `app/Controllers/`
**Step 6:** Replace manual `wp_enqueue` with webpack
**Step 7:** Test thoroughly (template hierarchy changes)

**Estimated Time:** 8-16 hours for small theme, 40-80 hours for large theme.

## Related Patterns

- **Sage Framework:** See `sage-framework-structure.md` for modern MVC alternative
- **Blade Templating:** See `blade-templating-pattern.md` for template engine syntax
- **MVC Controllers:** See `mvc-controllers-pattern.md` for separating logic from views
- **Build Tools:** See `build-tool-configuration.md` for webpack/Gulp integration
- **Template Hierarchy:** See `template-hierarchy-usage.md` for WordPress template resolution

## Common Pitfalls

**1. Monolithic functions.php:**
```php
// Bad: 2,000+ line functions.php
```
**Fix:** Separate into `inc/` modules by feature.

**2. Forgetting get_template_directory():**
```php
// Wrong - breaks in child themes
require 'inc/custom-functions.php';

// Correct - works in child themes
require get_template_directory() . '/inc/custom-functions.php';
```

**3. No version in wp_enqueue:**
```php
// Bad - no cache-busting
wp_enqueue_style('styles', get_template_directory_uri() . '/css/styles.css');

// Better - manual version
wp_enqueue_style('styles', get_template_directory_uri() . '/css/styles.css', array(), '1.0.1');

// Best - file modification time
wp_enqueue_style('styles',
    get_template_directory_uri() . '/css/styles.css',
    array(),
    filemtime(get_template_directory() . '/css/styles.css')
);
```

**4. Missing text domain:**
```php
// Wrong - no text domain
__('Read More');

// Correct - allows translations
__('Read More', 'themename');
```

**5. No escaping in templates:**
```php
// Security vulnerability
<h1><?php echo get_bloginfo('name'); ?></h1>

// Correct - escaped output
<h1><?php echo esc_html(get_bloginfo('name')); ?></h1>
```

## References

- **WordPress Template Hierarchy:** https://developer.wordpress.org/themes/basics/template-hierarchy/
- **Theme Handbook:** https://developer.wordpress.org/themes/
- **wp_enqueue_script:** https://developer.wordpress.org/reference/functions/wp_enqueue_script/
- **get_template_part:** https://developer.wordpress.org/reference/functions/get_template_part/
- **Theme Customizer API:** https://developer.wordpress.org/themes/customize-api/
