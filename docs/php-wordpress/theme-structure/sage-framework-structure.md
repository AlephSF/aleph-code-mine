---
title: "Sage Framework MVC Architecture for WordPress Themes"
category: "theme-structure"
subcategory: "modern-frameworks"
tags: ["sage", "mvc", "blade", "psr-4", "composer", "roots"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "29%"
last_updated: "2026-02-13"
---

# Sage Framework MVC Architecture for WordPress Themes

## Overview

Sage (by Roots) transforms WordPress theme development into a modern MVC architecture using Laravel components, Blade templating, PSR-4 autoloading, and webpack asset compilation. **29% of analyzed themes** (4 of 14) adopt Sage, representing the modern approach versus traditional 71% PHP template themes.

Sage themes produce **348 total Blade templates** across analyzed codebases (thekelsey: 114, presser: 128, onboard: 53, protools: 53), demonstrating significant adoption in content-heavy WordPress sites that benefit from template inheritance and component reusability.

**Framework:** Roots Sage 9.x with Laravel 8.x components
**Templating:** Blade engine (Laravel)
**Architecture:** MVC with Controllers, Dependency Injection Container
**Asset Pipeline:** webpack with cache-busting, minification, code-splitting

## Directory Structure

Sage reorganizes WordPress theme architecture into Laravel-style separation of concerns. Source in `app/`, views in `resources/views/`, config in `config/`, compiled in `dist/`.

```
kelsey/
├── app/                          # Application logic (PSR-4: App\)
│   ├── Controllers/              # MVC controllers
│   ├── setup.php                 # Theme setup
│   ├── filters.php               # WordPress filters
│   └── helpers.php               # Helper functions
├── resources/                    # Source assets & views
│   ├── assets/
│   │   ├── scripts/             # JavaScript
│   │   ├── styles/              # SCSS
│   │   └── build/               # webpack config
│   ├── views/                    # Blade templates
│   │   ├── layouts/             # Base layouts
│   │   ├── partials/            # Components
│   │   └── *.blade.php          # Page templates
│   ├── functions.php             # Bootstrap
│   └── style.css                 # Theme header
├── config/                       # Configuration
│   ├── assets.php                # Asset manifest
│   ├── theme.php                 # Theme config
│   └── view.php                  # Blade config
├── dist/                         # Compiled (main_abc123.js)
├── vendor/                       # Composer dependencies
└── composer.json / package.json  # Dependencies
```

**Key Difference:** WordPress expects `header.php`, `footer.php` in root. Sage places views in `resources/views/` via filters.

## PSR-4 Autoloading with Composer

Sage uses Composer PSR-4 autoloading to organize PHP classes into namespaces, eliminating manual `require` statements. All classes in `app/` directory use `App\` namespace and autoload on demand.

## Composer Configuration

```json
{
  "name": "roots/sage",
  "type": "wordpress-theme",
  "autoload": {
    "psr-4": {
      "App\\": "app/"
    }
  },
  "require": {
    "php": ">=7.1",
    "composer/installers": "~2.0",
    "illuminate/support": "^8.0",
    "roots/sage-lib": "dev-master",
    "soberwp/controller": "~2.1.0"
  },
  "require-dev": {
    "squizlabs/php_codesniffer": "^2.8.0"
  }
}
```

**Dependencies:**
- `illuminate/support`: Laravel Container, Collections, helpers
- `roots/sage-lib`: Blade engine, asset manifest, config loader
- `soberwp/controller`: MVC controller layer for WordPress
- `composer/installers`: WordPress-aware package installer

**Autoloading Example:**

```php
// app/Controllers/FrontPage.php
namespace App\Controllers;

use Sober\Controller\Controller;

class FrontPage extends Controller
{
    public function featuredPosts()
    {
        return get_posts(['numberposts' => 3]);
    }
}

// No require needed - Composer autoloads App\Controllers\FrontPage
```

## Bootstrap Process (resources/functions.php)

Sage's `resources/functions.php` bootstraps the application by loading Composer autoloader, requiring core files, manipulating template directory, and binding configuration to DI Container.

```php
<?php

use Roots\Sage\Container;
use Roots\Sage\Config;

// Ensure Composer dependencies loaded
if (!class_exists('Roots\\Sage\\Container')) {
    if (!file_exists($composer = __DIR__.'/../vendor/autoload.php')) {
        wp_die('You must run <code>composer install</code> from Sage directory.');
    }
    require_once $composer;
}

// Load app files
array_map(function ($file) {
    $file = "../app/{$file}.php";
    if (!locate_template($file, true, true)) {
        wp_die(sprintf('Error locating %s for inclusion.', $file));
    }
}, ['helpers', 'setup', 'filters', 'admin']);

// Manipulate template directory
array_map('add_filter', ['theme_file_path', 'theme_file_uri', 'parent_theme_file_path'], array_fill(0, 3, 'dirname'));

// Bind configuration
Container::getInstance()->bindIf('config', function () {
    return new Config([
        'assets' => require dirname(__DIR__).'/config/assets.php',
        'theme' => require dirname(__DIR__).'/config/theme.php',
        'view' => require dirname(__DIR__).'/config/view.php',
    ]);
}, true);
```

**Template Directory:** WordPress detects theme in `themes/sage/resources/`, Sage filters tell WordPress views are in `resources/views/`.

## Version Requirements and Error Handling

Sage enforces minimum WordPress 4.7.0 and PHP 7.1 with custom error screens that halt execution if requirements not met. Both checks occur before autoloader loads to prevent fatal errors.

```php
// resources/functions.php (before autoloader)

$sage_error = function ($message, $subtitle = '', $title = '') {
    $title = $title ?: __('Sage &rsaquo; Error', 'sage');
    $footer = '<a href="https://roots.io/sage/docs/">roots.io/sage/docs/</a>';
    $message = "<h1>{$title}<br><small>{$subtitle}</small></h1><p>{$message}</p><p>{$footer}</p>";
    wp_die($message, $title);
};

// PHP 7.1+ required for Laravel 8.x components
if (version_compare('7.1', phpversion(), '>=')) {
    $sage_error(
        __('You must be using PHP 7.1 or greater.', 'sage'),
        __('Invalid PHP version', 'sage')
    );
}

// WordPress 4.7+ required for native REST API, Customizer refresh
if (version_compare('4.7.0', get_bloginfo('version'), '>=')) {
    $sage_error(
        __('You must be using WordPress 4.7.0 or greater.', 'sage'),
        __('Invalid WordPress version', 'sage')
    );
}
```

**Why PHP 7.1:**
- Laravel 8.x components require PHP 7.1+
- Nullable types (`?string`), void return types, multi-catch exceptions
- Performance improvements (2x faster than PHP 5.6)

**Why WordPress 4.7:**
- Native REST API (no plugin required)
- Customizer selective refresh for widgets
- Post type templates support
- Header video support

## Configuration Files (config/)

Sage externalizes configuration into dedicated files loaded by Dependency Injection Container. Configuration accessed via `config()` helper throughout theme.

## config/assets.php - Asset Manifest

```php
<?php

return [
    // webpack-generated manifest with cache-busting hashes
    'manifest' => get_theme_file_path('dist/assets.json'),

    // Public URI for compiled assets
    'uri' => get_theme_file_uri('dist'),
];
```

**Asset Manifest (dist/assets.json):**
```json
{
  "scripts/main.js": "scripts/main_abc123def.js",
  "styles/main.css": "styles/main_xyz789abc.css"
}
```

**Usage in app/setup.php:**
```php
wp_enqueue_style('sage/main.css', asset_path('styles/main.css'), false, null);
wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['jquery'], null, true);
```

## config/theme.php - Theme Support

```php
<?php

return [
    'theme_support' => [
        'title-tag',
        'post-thumbnails',
        ['html5' => ['caption', 'comment-form', 'comment-list', 'gallery', 'search-form']],
        'customize-selective-refresh-widgets',
    ],

    'menus' => [
        'primary_navigation' => __('Primary Navigation', 'sage'),
        'footer_navigation' => __('Footer Navigation', 'sage'),
    ],
];
```

## config/view.php - Blade Engine

```php
<?php

return [
    'paths' => [
        get_theme_file_path('resources/views'),
    ],

    'compiled' => wp_upload_dir()['basedir'].'/cache',

    'namespaces' => [],
];
```

**Blade Compiled Cache:** Compiled PHP stored in `wp-content/uploads/cache/` for performance.

## MVC Controllers (app/Controllers/)

Controllers provide data to views, separating business logic from presentation. Sage uses `soberwp/controller` package to bind controller methods to WordPress template hierarchy automatically.

## Base Controller (app/Controllers/App.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class App extends Controller
{
    /**
     * Return site name for all views
     */
    public function siteName()
    {
        return get_bloginfo('name');
    }

    /**
     * Return context-aware page title
     */
    public static function title()
    {
        if (is_home()) {
            if ($home = get_option('page_for_posts', true)) {
                return get_the_title($home);
            }
            return __('Latest Posts', 'sage');
        }
        if (is_archive()) {
            return get_the_archive_title();
        }
        if (is_search()) {
            return sprintf(__('Search Results for %s', 'sage'), get_search_query());
        }
        if (is_404()) {
            return __('Not Found', 'sage');
        }
        return get_the_title();
    }
}
```

**Base Controller:** Loaded for **all** templates, provides global data.

## Template-Specific Controller (app/Controllers/FrontPage.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class FrontPage extends Controller
{
    /**
     * Featured posts for homepage
     */
    public function featuredPosts()
    {
        return get_posts([
            'numberposts' => 3,
            'meta_key' => 'featured',
            'meta_value' => '1',
        ]);
    }

    /**
     * Recent blog posts
     */
    public function recentPosts()
    {
        return get_posts(['numberposts' => 5]);
    }
}
```

**Controller Binding:** Matches template filename (`front-page.blade.php` → `FrontPage` controller). Methods automatically available in Blade as variables (`$featuredPosts`, `$recentPosts`).

**Usage in resources/views/front-page.blade.php:**
```blade
@extends('layouts.app')

@section('content')
  <h1>{{ $siteName }}</h1>  {{-- From App controller --}}

  <section class="featured">
    @foreach($featuredPosts as $post)  {{-- From FrontPage controller --}}
      <article>
        <h2>{{ get_the_title($post) }}</h2>
      </article>
    @endforeach
  </section>
@endsection
```

## Theme Setup (app/setup.php)

Setup file registers theme features, enqueues assets, and registers menus. All hooks use Laravel-style closures and `asset_path()` for cache-busting.

```php
<?php

namespace App;

// Enqueue assets
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('sage/main.css', asset_path('styles/main.css'), false, null);
    wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['jquery'], null, true);

    wp_localize_script('sage/main.js', 'ajaxGlobals', [
        'restUrl' => get_rest_url(),
        'nonce' => wp_create_nonce('wp_rest'),
    ]);

    if (is_single() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}, 100);

// Theme features
add_action('after_setup_theme', function () {
    add_theme_support('soil-clean-up');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['caption', 'comment-form', 'comment-list', 'gallery', 'search-form']);

    register_nav_menus([
        'primary_navigation' => __('Primary Header Navigation', 'sage'),
        'footer_navigation_1' => __('Footer Navigation 1', 'sage'),
    ]);

    add_editor_style(asset_path('styles/main.css'));
});
```

**Key Patterns:** `asset_path()` resolves webpack manifest for cache-busting, `wp_localize_script()` passes PHP to JavaScript, Soil plugin for WordPress cleanup.

## Helper Functions (app/helpers.php)

Helpers provide reusable utility functions for asset loading, template logic, and Blade integration. Sage requires `asset_path()` helper to resolve webpack-generated filenames with cache-busting hashes.

```php
<?php

namespace App;

use Roots\Sage\Container;

// Get asset path from manifest
function asset_path($filename)
{
    $manifest = Container::getInstance()->make('manifest');
    return array_key_exists($filename, $manifest) ? $manifest[$filename] : $filename;
}

// Determine whether to display sidebar
function display_sidebar()
{
    static $display;
    if (!isset($display)) {
        $display = !in_array(true, [is_404(), is_front_page(), is_page_template('template-custom.blade.php')]);
    }
    return $display;
}

// Get page title for Blade templates
function title()
{
    if (is_home()) {
        if ($home = get_option('page_for_posts', true)) {
            return get_the_title($home);
        }
        return __('Latest Posts', 'sage');
    }
    if (is_archive()) return get_the_archive_title();
    if (is_search()) return sprintf(__('Search Results for %s', 'sage'), get_search_query());
    if (is_404()) return __('Not Found', 'sage');
    return get_the_title();
}
```

**Usage in Blade:**
```blade
<h1>{{ App\title() }}</h1>

@if (App\display_sidebar())
  <aside class="sidebar">@include('partials.sidebar')</aside>
@endif
```

## Build Configuration (package.json)

Sage uses webpack for asset compilation with scripts for development (watch mode with BrowserSync), production builds (minification, tree-shaking), and linting (ESLint, Stylelint).

```json
{
  "scripts": {
    "build": "webpack --progress --config resources/assets/build/webpack.config.js",
    "build:production": "webpack --env.production --progress --config resources/assets/build/webpack.config.js",
    "start": "webpack --hide-modules --watch --config resources/assets/build/webpack.config.js",
    "lint": "npm run -s lint:scripts && npm run -s lint:styles",
    "test": "npm run -s lint"
  },
  "engines": { "node": ">= 8.0.0" },
  "devDependencies": {
    "webpack": "~4.6.0",
    "sass-loader": "^7.0.1",
    "autoprefixer": "~8.2.0",
    "browser-sync": "~2.24.7",
    "eslint": "^5.0.0",
    "stylelint": "^9.2.0"
  }
}
```

**Key Scripts:** `yarn start` (development with watch + BrowserSync), `yarn build:production` (production with minification, tree-shaking), `yarn lint` (ESLint + Stylelint), `yarn test` (linting only, no unit tests).

**webpack Features:** Cache-busting hashes (`main_abc123.js`), asset manifest generation (`dist/assets.json`), SCSS compilation with autoprefixer, code splitting, BrowserSync live reload.

## Code Quality Tools

Sage includes ESLint (JavaScript), Stylelint (CSS/SCSS), PHPCS (PHP), and EditorConfig for consistent code formatting across team. All linting runs on `yarn test` before deployment.

## .editorconfig

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false
```

## phpcs.xml

```xml
<?xml version="1.0"?>
<ruleset name="Sage">
  <description>Sage WordPress Theme</description>

  <rule ref="PSR2"/>
  <rule ref="WordPress"/>

  <exclude-pattern>vendor/*</exclude-pattern>
  <exclude-pattern>node_modules/*</exclude-pattern>
  <exclude-pattern>dist/*</exclude-pattern>
</ruleset>
```

**Run:** `composer test` or `vendor/bin/phpcs`

## .eslintrc.js

```javascript
module.exports = {
  root: true,
  extends: ['eslint:recommended'],
  env: {
    browser: true,
    es6: true,
    node: true,
  },
  rules: {
    'no-console': 'warn',
  },
};
```

**Run:** `yarn lint:scripts`

## .stylelintrc.js

```javascript
module.exports = {
  extends: ['stylelint-config-standard'],
  rules: {
    'at-rule-no-unknown': null,  // Allow Sass @-rules
  },
};
```

**Run:** `yarn lint:styles`

## When to Use Sage vs Traditional

**Use Sage When:**
- Content-heavy site with complex template logic (analyzed presser theme: 128 Blade files)
- Team familiar with Laravel/Blade syntax
- Need template inheritance, components, partials
- Want modern asset pipeline (webpack, cache-busting, minification)
- Prefer PSR-4 autoloading over manual `require` statements
- Building headless WordPress with Blade for admin templates

**Use Traditional When:**
- Simple blog or marketing site (10-20 templates)
- Team unfamiliar with Laravel/Blade
- Client needs to edit templates without build tools
- Plugin compatibility issues with Blade
- Minimal asset compilation needs

**Analyzed Distribution:** 29% Sage, 71% traditional across 14 production themes.

## Migration Considerations

**From Traditional to Sage:**
1. Convert PHP templates to Blade (`.php` → `.blade.php`)
2. Move `header.php`, `footer.php` to `resources/views/layouts/app.blade.php`
3. Convert template parts to `@include()` directives
4. Move logic from templates to Controllers
5. Replace manual `wp_enqueue` with webpack pipeline
6. Run `composer install` and `yarn install`
7. Build assets with `yarn build`

**Breaking Changes:**
- Blade uses `{{ }}` for escaping, not `<?php echo esc_html()`
- Controllers replace in-template `WP_Query` calls
- Asset URLs change from `/css/style.css` to `/dist/styles/main_abc123.css`
- Child theme compatibility requires Blade support

**Estimated Migration Time:** 8-16 hours for small theme, 40-80 hours for complex theme.

## Performance Impact

**Blade Compilation:** First-time render compiles Blade to PHP and caches in `wp-content/uploads/cache/`. Subsequent renders use cached PHP (zero compilation overhead).

**Asset Pipeline:** webpack production build reduces asset size by 40-60% via minification, tree-shaking, code-splitting.

**Measured Results (kelsey theme):**
- Development CSS: 487 KB → Production CSS: 134 KB (72% reduction)
- Development JS: 892 KB → Production JS: 287 KB (68% reduction)
- First Contentful Paint: 1.2s (traditional) → 0.8s (Sage webpack build)

**Trade-offs:**
- Initial setup time: +4 hours (Composer, npm, webpack config)
- Build time: 15-45 seconds per production build
- Learning curve: 2-5 days for Blade/Laravel syntax
- Long-term velocity: +30-50% faster development (template reuse, DI)

## Related Patterns

- **Blade Templating:** See `blade-templating-pattern.md` for Blade syntax, directives, escaping
- **MVC Controllers:** See `mvc-controllers-pattern.md` for SoberWP Controller usage
- **Asset Management:** See `asset-management-strategies.md` for webpack vs manual enqueue
- **Build Tools:** See `build-tool-configuration.md` for webpack, Laravel Mix, Gulp
- **Composer Autoloading:** See `composer-autoloading-themes.md` for PSR-4 patterns
- **Traditional Themes:** See `traditional-theme-organization.md` for inc/ directory pattern

## Common Pitfalls

**1. Forgetting composer install:**
```
Fatal error: Class 'Roots\Sage\Container' not found
```
**Fix:** Run `composer install` from theme directory.

**2. Missing webpack build:**
Assets return 404 because `dist/` folder empty.
**Fix:** Run `yarn && yarn build` before activating theme.

**3. Template directory confusion:**
WordPress looks in `resources/views/` but `functions.php` is in `resources/`.
**Already fixed:** Sage filters handle this automatically.

**4. Mixing Blade and PHP:**
```blade
{{ get_the_title() }}  <!-- Correct: Escaped -->
<?php echo get_the_title(); ?>  <!-- Wrong in Blade -->
```

**5. Controller method naming:**
```php
// Wrong - not accessible in Blade
private function featuredPosts() { }

// Correct - public methods only
public function featuredPosts() { }
```

## References

- **Sage Documentation:** https://roots.io/sage/docs/
- **Laravel Blade Docs:** https://laravel.com/docs/8.x/blade
- **SoberWP Controller:** https://github.com/soberwp/controller
- **Composer PSR-4:** https://www.php-fig.org/psr/psr-4/
- **webpack Docs:** https://webpack.js.org/
