# Phase 4, Domain 6: Theme Structure & Organization - Cross-Project Comparison

**Analysis Date:** February 12, 2026
**Repositories Analyzed:**
- airbnb (WordPress VIP multisite) - 13 themes
- thekelsey-wp - 1 theme (Sage framework)

**Total Themes:** 14

---

## Executive Summary

WordPress theme architecture shows clear evolution from traditional template-based themes to modern MVC frameworks. **29% of themes** (4/14) use the Sage framework with Blade templating, **348 total Blade templates**, and PSR-4 autoloading. **71% remain traditional** with inc/ directory organization and classic PHP templates.

**Key Finding:** airbnb multisite uses **dual strategy** - Sage for content-heavy sites (presser: 128 Blade files, onboard: 53, protools: 53), traditional PHP for simpler blogs (airbnbtech, blogs-atairbnb, pressbnb). thekelsey-wp is **100% Sage**.

---

## 1. Framework Adoption

### Sage Framework (Roots)

**Adoption:** 4/14 themes (29%)

| Theme | Repository | Blade Files | Composer | Controllers | Build Tool |
|-------|------------|-------------|----------|-------------|------------|
| kelsey | thekelsey-wp | 114 | ✅ | ✅ (9 files) | webpack |
| presser | airbnb | 128 | ✅ | ✅ | webpack |
| onboard | airbnb | 53 | ✅ | ✅ | webpack |
| protools | airbnb | 53 | ✅ | ✅ | webpack |

**Total Blade Templates:** 348 files

**Sage Version:** All use Sage 9.x (based on Illuminate/Laravel 8.x components)

### Traditional WordPress Themes

**Adoption:** 10/14 themes (71%)

| Theme | Repository | Template Files | inc/ Directory | Build Tool | ACF JSON |
|-------|------------|----------------|----------------|------------|----------|
| airbnbtech | airbnb | ✅ | ✅ | None | None |
| blogs-atairbnb | airbnb | ✅ | ✅ | None | None |
| pressbnb | airbnb | ✅ | ✅ | gulpfile.js | ✅ (44 files) |
| airbnb-careers | airbnb | ✅ | ✅ | Laravel Mix | None |
| airbnb-dls-blog | airbnb | ✅ | Unknown | None | None |
| airbnb-olympics | airbnb | ✅ (child) | Unknown | None | None |
| a4re | airbnb | ✅ | ✅ | None | None |
| rkv | airbnb | ✅ | Unknown | None | None |
| aleph-nothing | airbnb | Minimal (200 lines) | None | None | None |
| twentyseventeen | airbnb | ✅ | ✅ | None | None |

**Traditional Template Hierarchy Usage:**
- archive.php, single.php, page.php: 21 files across traditional themes
- header.php, footer.php: 19 files
- 404.php: Present in most themes
- get_template_part() calls: 8+ instances in blogs-atairbnb alone

---

## 2. Theme Structure Patterns

### Sage MVC Architecture (29%)

**Directory Structure:**
```
kelsey/ (thekelsey-wp)
├── app/                          # Application logic (PSR-4 App\)
│   ├── Controllers/              # 9 controller files
│   │   ├── App.php              # Base controller
│   │   ├── FrontPage.php        # Homepage logic
│   │   └── SinglePost.php       # Single post logic
│   ├── setup.php                 # Theme setup hooks
│   ├── filters.php               # WordPress filters
│   ├── helpers.php               # Helper functions
│   └── admin.php                 # Admin customizations
├── resources/                    # Assets & views
│   ├── assets/                   # Source files (SCSS, JS)
│   │   ├── scripts/             # JavaScript source
│   │   ├── styles/              # SCSS source
│   │   └── build/               # webpack config
│   ├── views/                    # Blade templates
│   │   ├── layouts/             # Base layouts
│   │   ├── partials/            # Reusable components
│   │   └── *.blade.php          # Page templates
│   ├── functions.php             # Bootstrap file
│   └── style.css                 # Theme header
├── config/                       # Configuration
│   ├── assets.php                # Asset manifest
│   ├── theme.php                 # Theme config
│   └── view.php                  # Blade config
├── dist/                         # Compiled assets
├── vendor/                       # Composer dependencies
├── composer.json                 # PHP dependencies
└── package.json                  # Node dependencies
```

**Key Features:**
- **PSR-4 Autoloading:** `"App\\": "app/"` namespace
- **Laravel Components:** illuminate/support, Blade engine, Container
- **SoberWP Controller:** ~2.1.0 for MVC pattern
- **Dependency Injection:** `Container::getInstance()`
- **Template Directory Manipulation:** Views in resources/views/, functions.php in resources/

**Functions.php Pattern:**
```php
// Sage bootstrap (resources/functions.php)
use Roots\Sage\Container;
use Roots\Sage\Config;

// Autoloader check
if (!class_exists('Roots\\Sage\\Container')) {
    require_once __DIR__.'/../vendor/autoload.php';
}

// Load app files
array_map(function ($file) {
    $file = "../app/{$file}.php";
    locate_template($file, true, true);
}, ['helpers', 'setup', 'filters', 'admin']);

// Config binding
Container::getInstance()->bindIf('config', function () {
    return new Config([
        'assets' => require dirname(__DIR__).'/config/assets.php',
        'theme' => require dirname(__DIR__).'/config/theme.php',
        'view' => require dirname(__DIR__).'/config/view.php',
    ]);
}, true);
```

### Modern Traditional Architecture (21% - 3 Sage themes in airbnb)

presser, onboard, protools follow Sage structure exactly. See table above.

### Classic WordPress Architecture (50% - 7 traditional themes)

**Directory Structure:**
```
airbnbtech/ (traditional)
├── inc/                          # Code organization
│   ├── careers-setup.php         # CPT registration
│   ├── events-setup.php
│   ├── teams-setup.php
│   ├── custom-functions.php      # Helper functions
│   ├── customizer.php            # Theme Customizer
│   └── widgets/                  # Custom widgets
├── css/                          # Stylesheets
├── js/                           # JavaScript files
├── images/                       # Image assets
├── fonts/                        # Web fonts
├── functions.php                 # Main theme file
├── style.css                     # Theme header
├── header.php                    # Site header
├── footer.php                    # Site footer
├── index.php                     # Fallback template
├── archive.php                   # Archive pages
├── single.php                    # Single posts
├── page.php                      # Static pages
├── 404.php                       # Error page
└── front-page.php                # Homepage (optional)
```

**Functions.php Pattern:**
```php
// airbnbtech/functions.php
// Direct WordPress hooks, no autoloading

// Load inc/ files
require get_template_directory() . '/inc/careers-setup.php';
require get_template_directory() . '/inc/events-setup.php';
require get_template_directory() . '/inc/teams-setup.php';

// Asset loading
function site_styles() {
    wp_register_style('site-styles',
        get_template_directory_uri() . '/css/styles.css',
        array(), '1.0', 'all');
    wp_enqueue_style('site-styles');
}
add_action('wp_enqueue_scripts', 'site_styles');

// Theme setup
add_theme_support('automatic-feed-links');
add_post_type_support('page', 'excerpt');

// Custom functions
function excerpt_limit($wordstring, $word_limit) {
    $words = explode(' ', $wordstring, ($word_limit + 1));
    if (count($words) > $word_limit) {
        array_pop($words);
        return implode(' ', $words) . '...';
    }
    return implode(' ', $words);
}
```

**inc/ Directory Organization:**
- careers-setup.php, events-setup.php, teams-setup.php: CPT registration
- custom-functions.php: Helper functions
- customizer.php: Theme Customizer API
- widgets/: Custom widget classes
- template-tags.php: Reusable template functions
- template-functions.php: Complex template logic

---

## 3. Templating Engines

### Blade Templates (29% of themes)

**Total Files:** 348 Blade templates across 4 themes

**Distribution:**
- presser: 128 files (largest - complex content site)
- kelsey: 114 files
- onboard: 53 files
- protools: 53 files

**Blade Template Structure (kelsey example):**
```
resources/views/
├── layouts/
│   ├── app.blade.php             # Base layout
│   └── base.blade.php
├── partials/
│   ├── header.blade.php
│   ├── footer.blade.php
│   ├── sidebar.blade.php
│   └── content-*.blade.php       # Content partials
├── blocks/                       # Gutenberg blocks
│   ├── block.blade.php           # Base block
│   ├── core-image.blade.php      # Core block overrides
│   ├── thekelsey-slideshow.blade.php
│   └── thekelsey-event-template.blade.php
├── front-page.blade.php          # Homepage
├── index.blade.php               # Main loop
├── 404.blade.php                 # Error page
├── template-*.blade.php          # Page templates
│   ├── template-learn-center.blade.php
│   ├── template-projects.blade.php
│   └── template-stories.blade.php
```

**Blade Syntax Patterns:**
```blade
{{-- kelsey/resources/views/layouts/app.blade.php --}}
<!doctype html>
<html {!! get_language_attributes() !!}>
  @include('partials.head')
  <body @php(body_class())>
    @php(do_action('get_header'))
    @include('partials.header')

    <div class="wrap container" role="document">
      <div class="content">
        <main class="main">
          @yield('content')
        </main>
        @if (App\display_sidebar())
          <aside class="sidebar">
            @include('partials.sidebar')
          </aside>
        @endif
      </div>
    </div>

    @php(do_action('get_footer'))
    @include('partials.footer')
    @php(wp_footer())
  </body>
</html>
```

**Blade Directives Usage:**
- `@extends()`: Layout inheritance
- `@section()` / `@yield()`: Content sections
- `@include()`: Partial templates
- `@if` / `@else` / `@endif`: Conditionals
- `@foreach` / `@endforeach`: Loops
- `@php()`: PHP execution
- `{!! !!}`: Unescaped output (WordPress hooks)
- `{{ }}`: Escaped output

### Traditional PHP Templates (71% of themes)

**Classic Template Hierarchy:**
```php
// airbnbtech/archive.php
<?php get_header(); ?>

<div class="container">
  <?php if (have_posts()) : ?>
    <h1><?php the_archive_title(); ?></h1>

    <?php while (have_posts()) : the_post(); ?>
      <?php get_template_part('content', get_post_format()); ?>
    <?php endwhile; ?>

    <?php the_posts_navigation(); ?>
  <?php else : ?>
    <?php get_template_part('content', 'none'); ?>
  <?php endif; ?>
</div>

<?php get_footer(); ?>
```

**Template Parts Pattern:**
```php
// blogs-atairbnb uses get_template_part() 8 times
get_template_part('content', 'page');
get_template_part('content', get_post_format());
get_template_part('searchform');
```

**Header/Footer Includes:**
```php
// Standard pattern
<?php get_header(); ?>
// Template content
<?php get_sidebar(); ?>
<?php get_footer(); ?>
```

---

## 4. Code Organization

### Directory Patterns

| Pattern | Themes | Percentage | Purpose |
|---------|--------|------------|---------|
| inc/ | 7 | 50% | Traditional code organization |
| app/ | 4 | 29% | Sage MVC (controllers, setup, helpers) |
| lib/ | Many | N/A | Vendor dependencies (Composer) |
| resources/ | 4 | 29% | Sage asset & view source |
| dist/ | 4 | 29% | Compiled assets (webpack output) |
| config/ | 4 | 29% | Configuration files (Sage) |
| acf-json/ | 3 | 21% | ACF field group sync |

### inc/ Directory Pattern (50% - 7 themes)

**Common Files:**
- **careers-setup.php, events-setup.php:** CPT registration
- **custom-functions.php, hooks.php:** Helper functions
- **customizer.php:** Theme Customizer API
- **template-tags.php:** Reusable template functions
- **template-functions.php:** Complex template logic
- **widgets/:** Custom widget classes
- **back-compat.php:** WordPress version compatibility

**Example (airbnbtech):**
```php
require get_template_directory() . '/inc/careers-setup.php';
require get_template_directory() . '/inc/events-setup.php';
require get_template_directory() . '/inc/opensource-setup.php';
require get_template_directory() . '/inc/tech-priorities-setup.php';
require get_template_directory() . '/inc/teams-setup.php';
require get_template_directory() . '/inc/research-setup.php';
```

### app/ Directory Pattern (29% - 4 Sage themes)

**Standard Structure:**
- **Controllers/:** MVC controllers (9 files in kelsey)
- **setup.php:** Theme setup hooks (after_setup_theme)
- **filters.php:** WordPress filters
- **helpers.php:** Helper functions
- **admin.php:** Admin customizations

**PSR-4 Autoloading:**
```json
{
  "autoload": {
    "psr-4": {
      "App\\": "app/"
    }
  }
}
```

**Controller Pattern:**
```php
// app/Controllers/App.php
namespace App\Controllers;

use Sober\Controller\Controller;

class App extends Controller
{
    public function siteName()
    {
        return get_bloginfo('name');
    }

    public static function title()
    {
        if (is_home()) {
            return get_the_title(get_option('page_for_posts'));
        }
        if (is_archive()) {
            return get_the_archive_title();
        }
        return get_the_title();
    }
}
```

---

## 5. Asset Management

### Webpack (36% - 5 themes)

**Themes Using Webpack:**
- kelsey (thekelsey-wp)
- presser (airbnb)
- onboard (airbnb)
- protools (airbnb)
- airbnb-careers (Laravel Mix wrapper)

**Build Configuration:**
```
resources/assets/build/
├── webpack.config.js             # Main config
├── webpack.config.watch.js       # Dev watch
└── webpack.config.optimize.js    # Production
```

**package.json Scripts (kelsey):**
```json
{
  "scripts": {
    "build": "webpack --progress --config resources/assets/build/webpack.config.js",
    "build:production": "webpack --env.production --progress",
    "start": "webpack --hide-modules --watch",
    "lint": "npm run -s lint:scripts && npm run -s lint:styles",
    "lint:scripts": "eslint resources/assets/scripts",
    "lint:styles": "stylelint \"resources/assets/styles/**/*.{css,sass,scss}\""
  }
}
```

**Asset Manifest Pattern (Sage):**
```php
// config/assets.php
return [
    'manifest' => get_theme_file_path('dist/assets.json'),
    'uri' => get_theme_file_uri('dist'),
];

// Usage in setup.php
wp_enqueue_style('sage/main.css', asset_path('styles/main.css'), false, null);
wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['jquery'], null, true);
```

### Laravel Mix (7% - 1 theme)

**Theme:** airbnb-careers

**Configuration:**
```javascript
// webpack.mix.js
mix.js('src/app.js', 'dist/')
   .sass('src/app.scss', 'dist/');
```

### Gulp (7% - 1 theme)

**Theme:** pressbnb

**Configuration:**
```javascript
// gulpfile.js
gulp.task('styles', function() {
  return gulp.src('css/source/**/*.scss')
    .pipe(sass())
    .pipe(autoprefixer())
    .pipe(gulp.dest('css'));
});
```

### Manual wp_enqueue (50% - 7 themes)

**Traditional Pattern:**
```php
// airbnbtech/functions.php
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
}
add_action('wp_enqueue_scripts', 'site_scripts');
```

**No Versioning:** Manual versioning via `'1.0'` or `NULL`
**No Hashing:** No cache-busting hashes in filenames
**No Minification:** CSS/JS served unminified in production

---

## 6. Build Tools & Dependencies

### Composer (29% - 4 themes)

**All Sage themes use Composer:**

**kelsey composer.json:**
```json
{
  "require": {
    "php": ">=7.1",
    "composer/installers": "~2.0",
    "illuminate/support": "^8.0",
    "roots/sage-lib": "dev-master",
    "soberwp/controller": "~2.1.0"
  },
  "require-dev": {
    "squizlabs/php_codesniffer": "^2.8.0",
    "roots/sage-installer": "dev-master"
  }
}
```

**Key Dependencies:**
- **illuminate/support:** Laravel components (Container, Collections, etc.)
- **roots/sage-lib:** Sage core (Blade engine, Asset manifest)
- **soberwp/controller:** MVC controller layer
- **composer/installers:** WordPress-aware installer

### npm/Yarn (57% - 8 themes)

**Themes with package.json:**
- kelsey (Sage)
- presser, onboard, protools (Sage)
- airbnb-careers (Laravel Mix)
- pressbnb (Gulp)
- 2 others

**Build Dependencies (kelsey):**
```json
{
  "devDependencies": {
    "autoprefixer": "~8.2.0",
    "browser-sync": "~2.24.7",
    "browsersync-webpack-plugin": "^0.6.0",
    "webpack": "~4.6.0",
    "webpack-cli": "^3.1.2",
    "sass-loader": "^7.0.1",
    "eslint": "^5.0.0",
    "stylelint": "^9.2.0"
  }
}
```

---

## 7. ACF Integration Patterns

### ACF JSON Sync (21% - 3 themes)

**Themes with acf-json/:**
- presser: 35 field groups
- protools: 6 field groups
- pressbnb: 44 field groups (largest)

**ACF Save Point:**
```php
// Sage themes
add_filter('acf/settings/save_json', function () {
    return get_stylesheet_directory() . '/resources/acf-json';
});

add_filter('acf/settings/load_json', function ($paths) {
    $paths[] = get_stylesheet_directory() . '/resources/acf-json';
    return $paths;
});
```

**Traditional themes (pressbnb):**
```php
add_filter('acf/settings/save_json', function () {
    return get_stylesheet_directory() . '/acf-json';
});
```

---

## 8. Child Theme Pattern

**Adoption:** 1/14 themes (7%)

**Child Theme:** airbnb-olympics

```css
/*
Theme Name: Airbnb Olympics custom child theme
Template: twentyseventeen
*/
```

**Parent:** twentyseventeen (WordPress core theme)

**Rationale:** Minimal customizations without forking core theme.

---

## 9. Headless Theme Pattern

**Theme:** aleph-nothing (airbnb)

**Purpose:** Minimal theme for headless WordPress (GraphQL-only)

**Structure:**
- functions.php: 200 lines (documented in Phase 4, Domain 1)
- style.css: Theme header only
- index.php: Minimal fallback
- Page templates for admin-only pages (airlab, priority)

**No Frontend:** All rendering handled by Next.js frontend.

---

## 10. WordPress Version Requirements

### Sage Themes

**Minimum WordPress:** 4.7.0 (all Sage themes check in functions.php)

```php
if (version_compare('4.7.0', get_bloginfo('version'), '>=')) {
    $sage_error(__('You must be using WordPress 4.7.0 or greater.', 'sage'));
}
```

**Why 4.7.0:**
- Native REST API support
- Customizer selective refresh
- Template hierarchy improvements
- Header video support

### Sage PHP Requirements

**Minimum PHP:** 7.1 (all Sage themes check)

```php
if (version_compare('7.1', phpversion(), '>=')) {
    $sage_error(__('You must be using PHP 7.1 or greater.', 'sage'));
}
```

**Why PHP 7.1:**
- Laravel 8.x components require PHP 7.1+
- Nullable types, void return types
- Iterable type, multi-catch exceptions

---

## 11. Theme Support Features

### Sage Themes (100% adoption)

```php
// app/setup.php
add_theme_support('title-tag');
add_theme_support('post-thumbnails');
add_theme_support('html5', ['caption', 'comment-form', 'comment-list', 'gallery', 'search-form']);
add_theme_support('customize-selective-refresh-widgets');
add_theme_support('soil-clean-up');  // Roots Soil plugin
add_theme_support('soil-nav-walker');
add_theme_support('soil-relative-urls');
```

### Traditional Themes (common patterns)

```php
add_theme_support('automatic-feed-links');
add_post_type_support('page', 'excerpt');  // Page excerpts
register_taxonomy_for_object_type('post_tag', 'page');  // Tags on pages
```

---

## 12. Performance Optimizations

### Sage Themes

**Webpack Production Build:**
- Minification (UglifyJS, CSSNano)
- Source maps for debugging
- Cache-busting hashes in filenames
- Tree-shaking unused code
- Code splitting (vendor bundles)

**Asset Manifest:**
```json
// dist/assets.json
{
  "scripts/main.js": "scripts/main_abc123.js",
  "styles/main.css": "styles/main_xyz789.css"
}
```

**Helper Function:**
```php
function asset_path($filename) {
    $manifest = json_decode(file_get_contents('dist/assets.json'), true);
    return $manifest[$filename] ?? $filename;
}
```

### Traditional Themes

**Manual Optimizations (airbnbtech):**
```php
// Remove emoji junk
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');

// Remove version numbers (security)
remove_action('wp_head', 'wp_generator');

// Remove query strings (caching)
function cleanup_query_string($src) {
    $parts = explode('?', $src);
    return $parts[0];
}
add_filter('script_loader_src', 'cleanup_query_string', 15);
add_filter('style_loader_src', 'cleanup_query_string', 15);

// Remove REST API links (security)
remove_action('wp_head', 'rest_output_link_wp_head', 10);
```

---

## 13. Code Quality Tools

### Sage Themes (100%)

**PHPCS:**
```xml
<!-- phpcs.xml -->
<rule ref="PSR2"/>
<rule ref="WordPress"/>
```

**ESLint:**
```javascript
// .eslintrc.js
module.exports = {
  extends: ['eslint:recommended'],
  env: { browser: true, es6: true },
};
```

**Stylelint:**
```javascript
// .stylelintrc.js
module.exports = {
  extends: ['stylelint-config-standard'],
  rules: { 'at-rule-no-unknown': null },
};
```

**.editorconfig:**
```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

### Traditional Themes

**No Linting:** 0% have ESLint, Stylelint, or PHPCS
**No .editorconfig:** 0% have EditorConfig

---

## 14. Navigation Patterns

### Sage Themes

**Multiple Nav Menus:**
```php
register_nav_menus([
    'primary_navigation' => __('Primary Header Navigation', 'sage'),
    'secondary_navigation' => __('Secondary Header Navigation', 'sage'),
    'footer_navigation_1' => __('Footer Navigation 1', 'sage'),
    'footer_navigation_2' => __('Footer Navigation 2', 'sage'),
    'footer_navigation_3' => __('Footer Navigation 3', 'sage')
]);
```

**Blade Output:**
```blade
@if (has_nav_menu('primary_navigation'))
  <nav class="nav-primary">
    {!! wp_nav_menu(['theme_location' => 'primary_navigation', 'echo' => false]) !!}
  </nav>
@endif
```

### Traditional Themes

**Standard Registration:**
```php
register_nav_menus(array(
    'primary' => __('Primary Menu'),
    'footer' => __('Footer Menu')
));
```

**PHP Output:**
```php
<?php
wp_nav_menu(array(
    'theme_location' => 'primary',
    'container_class' => 'primary-menu-container'
));
?>
```

---

## 15. Gutenberg Block Integration

### kelsey (thekelsey-wp)

**Custom Block Views:** 12 Blade templates in resources/views/blocks/

**Core Block Overrides:**
- core-image.blade.php
- core-group.blade.php
- core-pullquote.blade.php

**Custom Blocks:**
- thekelsey-slideshow.blade.php
- thekelsey-slideshow-slide.blade.php
- thekelsey-vimeo-video.blade.php
- thekelsey-event-template.blade.php
- thekelsey-small-heading.blade.php
- thekelsey-event-registration-popup-link.blade.php
- thekelsey-narrow-content-section.blade.php

**Block Registration Pattern:**
```php
// app/setup.php
add_action('acf/init', function () {
    if (function_exists('acf_register_block_type')) {
        acf_register_block_type([
            'name' => 'slideshow',
            'title' => __('Slideshow'),
            'render_callback' => function ($block) {
                echo view('blocks.thekelsey-slideshow', compact('block'));
            },
        ]);
    }
});
```

---

## Summary Statistics

| Metric | Value | Percentage |
|--------|-------|------------|
| **Total Themes** | 14 | 100% |
| **Sage Framework** | 4 | 29% |
| **Traditional PHP** | 10 | 71% |
| **Blade Templates** | 348 files | N/A |
| **Composer Usage** | 4 | 29% |
| **Build Tools (webpack/Mix/Gulp)** | 8 | 57% |
| **inc/ Directory** | 7 | 50% |
| **app/ Directory (MVC)** | 4 | 29% |
| **ACF JSON Sync** | 3 | 21% |
| **Child Themes** | 1 | 7% |
| **Headless Themes** | 1 | 7% |
| **PHPCS/ESLint/Stylelint** | 4 (Sage only) | 29% |
| **.editorconfig** | 4 (Sage only) | 29% |

---

## Key Patterns for Documentation

### High Confidence (100% adoption within category)

1. **Sage MVC Structure:** All 4 Sage themes use identical app/ structure
2. **PSR-4 Autoloading:** All Sage themes use `"App\\"` namespace
3. **Blade Templating:** All Sage themes use Blade (348 total files)
4. **Webpack Build:** All Sage themes except 1 use webpack
5. **inc/ Directory:** All traditional themes with modular code use inc/
6. **Version Checks:** All Sage themes check PHP 7.1+ and WP 4.7+

### Medium Confidence (50-80% adoption)

1. **Build Tools:** 57% use webpack/Mix/Gulp
2. **inc/ Directory:** 50% organize code this way
3. **Manual wp_enqueue:** 50% use traditional asset loading

### Low Confidence / Gap Patterns (0-30% adoption)

1. **Code Quality Tools:** 29% (Sage only) - 71% have no linting
2. **Child Themes:** 7% - Underutilized pattern
3. **ACF JSON Sync:** 21% - Should be higher
4. **.editorconfig:** 29% - Critical gap for team consistency

---

## Recommendations for Standards

### Enforce (High Confidence)

1. **For New Themes:** Use Sage framework (Blade, MVC, webpack)
2. **PSR-4 Autoloading:** If using Composer, follow `App\\` namespace
3. **ACF JSON Sync:** All themes with ACF should use acf-json/
4. **Build Tools:** Use webpack for asset pipeline (cache-busting, minification)
5. **Code Quality:** Add ESLint, Stylelint, PHPCS to all themes

### Recommend (Medium Confidence)

1. **inc/ Directory:** For traditional themes, organize code in inc/
2. **Version Requirements:** Check PHP 7.4+ and WP 5.0+ minimum
3. **Theme Support:** Enable title-tag, post-thumbnails, html5, customize-selective-refresh

### Document as Options (Low Confidence)

1. **Child Themes:** When to use vs standalone theme
2. **Headless Themes:** Minimal theme pattern for GraphQL/REST only
3. **Gutenberg Blocks:** ACF block registration with Blade views

---

## Files Generated from This Analysis

**RAG-Optimized Documentation (8 files):**
1. `sage-framework-structure.md` - Sage MVC architecture (29% adoption)
2. `traditional-theme-organization.md` - inc/ directory pattern (50% adoption)
3. `blade-templating-pattern.md` - Blade vs PHP templates (348 Blade files)
4. `mvc-controllers-pattern.md` - SoberWP Controller usage (29% adoption)
5. `asset-management-strategies.md` - Webpack vs manual enqueue (57% vs 43%)
6. `build-tool-configuration.md` - webpack, Laravel Mix, Gulp patterns
7. `composer-autoloading-themes.md` - PSR-4 autoloading (29% adoption)
8. `template-hierarchy-usage.md` - WordPress template hierarchy in both paradigms

**Semgrep Rules (4 rules):**
1. `require-composer-autoload.yaml` - Detect Sage themes without vendor/autoload.php
2. `enforce-namespaced-controllers.yaml` - Require `namespace App\Controllers;` in controllers
3. `warn-manual-asset-loading.yaml` - Suggest webpack for themes with manual wp_enqueue
4. `require-blade-escaping.yaml` - Enforce `{{ }}` over `{!! !!}` except for WordPress hooks

---

**Analysis Complete:** February 12, 2026
**Next Steps:** Generate 8 documentation files + 4 Semgrep rules
**Estimated Time:** 1.5 hours for docs, 30 minutes for Semgrep rules
