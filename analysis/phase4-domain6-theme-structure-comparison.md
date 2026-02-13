# Phase 4, Domain 6: Theme Structure & Organization - Cross-Project Comparison

**Analysis Date:** February 12, 2026
**Analyzed Themes:** 3 (Presser, Aleph Nothing, Kelsey)
**Focus:** Sage Roots patterns + Headless architecture
**Total Documentation Files Planned:** 8
**Total Semgrep Rules Planned:** 4

---

## Executive Summary

Analyzed three WordPress themes representing different architectural approaches:
- **Presser** (Airbnb newsroom): Modern Sage 9+ with Webpack 5, Node 20+, 85 Blade templates
- **Aleph Nothing** (Airbnb impact/headless): Minimal headless theme, 45 lines PHP, GraphQL-first
- **Kelsey** (The Kelsey): Traditional Sage 9 with Webpack 3, Node 8+, 114 Blade templates

**Key Finding:** 100% adoption of Sage Roots framework for traditional themes, with divergent build tooling maturity. Headless theme reduces codebase by 99.5% (45 lines vs 2,006 lines).

---

## 1. Framework & Architecture

### Sage Roots Adoption

| Theme | Framework | Version | Architecture |
|-------|-----------|---------|--------------|
| **Presser** | Sage Roots | 9+ | Traditional Blade |
| **Aleph Nothing** | None | N/A | Headless (GraphQL) |
| **Kelsey** | Sage Roots | 9 | Traditional Blade |

**Pattern:** 67% Sage Roots adoption (2/3 themes)
**Confidence:** 100% for traditional themes, 0% for headless

### Directory Structure (Sage Themes)

```
theme-root/
├── app/                    # PHP business logic (PSR-4 autoloaded)
│   ├── Controllers/        # Blade view controllers
│   ├── setup.php          # Theme setup hooks
│   ├── filters.php        # WordPress filters
│   ├── helpers.php        # Helper functions
│   └── admin.php          # Admin customizations
├── config/                # Configuration files
│   ├── assets.php         # Asset manifest config
│   ├── theme.php          # Theme support config
│   └── view.php           # Blade view config
├── resources/             # Theme root (WordPress sees this)
│   ├── assets/            # Source assets (pre-compilation)
│   │   ├── scripts/       # JavaScript source
│   │   └── styles/        # SCSS source
│   ├── views/             # Blade templates
│   │   ├── layouts/       # Layout templates
│   │   ├── partials/      # Reusable components
│   │   └── blocks/        # ACF/Gutenberg blocks
│   ├── functions.php      # Theme entry point
│   ├── index.php          # Required WordPress file
│   └── style.css          # Theme header (required)
├── dist/                  # Compiled assets (webpack output)
│   ├── scripts/           # Compiled JS bundles
│   ├── styles/            # Compiled CSS
│   └── assets-manifest.json  # Asset versioning map
├── vendor/                # Composer dependencies
├── composer.json          # PHP dependencies
└── package.json           # Node dependencies
```

**Pattern Confidence:** 100% for Sage themes

---

## 2. Build Tooling Comparison

### Presser (Modern Stack)

**Node Version:** 20+
**Build System:** Webpack 5
**Package Manager:** Yarn

**Key Dependencies:**
- **Webpack 5.96.1** (ESM, modern loaders)
- **Babel 7.26.0** (ES2015+ transpilation)
- **ESLint 9.15.0** (flat config)
- **Stylelint 16.11.0** (modern SCSS linting)
- **PostCSS 8.4.49** (Autoprefixer, CSSNano)
- **Sass 1.81.0** (dart-sass, modern @use)
- **MiniCssExtractPlugin 2.9.2** (CSS extraction)
- **TerserPlugin 5.3.10** (JS minification)
- **Preact 8.3.1** (React compatibility layer)

**npm Scripts:**
```json
{
  "build": "webpack --progress",
  "build:production": "webpack --env=production",
  "start": "webpack --watch",
  "lint": "npm run lint:scripts && npm run lint:styles",
  "test": "npm run lint"
}
```

**Webpack Entry Points:**
- `main.js` + `main.scss` → Main bundle
- `customizer.js` → WordPress Customizer
- `gutes-custom.js` → Gutenberg editor
- `admin-custom.js` + `admin.scss` → Admin styles

**Build Features:**
- ✅ Source maps (development)
- ✅ Hot module replacement (BrowserSync)
- ✅ Asset manifest with cache busting (`?hash`)
- ✅ Image optimization (imagemin-webpack-plugin)
- ✅ ESLint + Stylelint (fail on error in production)
- ✅ Preact/React aliasing (smaller bundle size)
- ✅ jQuery externalized (uses WordPress's jQuery)

### Kelsey (Legacy Stack)

**Node Version:** 8+
**Build System:** Webpack 3
**Package Manager:** Yarn

**Key Dependencies:**
- **Webpack 3.10.0** (legacy)
- **Node-Sass** (aliased to dart-sass 1.49.10)
- **ESLint 4.19.1** (legacy config)
- **Stylelint 8.4.0** (legacy)
- **ExtractTextWebpackPlugin 3.0.2** (replaced by MiniCssExtractPlugin in Webpack 4+)
- **UglifyJsWebpackPlugin 1.3.0** (replaced by TerserPlugin in Webpack 5+)
- **Buble Loader 0.4.1** (lightweight transpiler, less features than Babel)

**npm Scripts:**
```json
{
  "build": "webpack --progress",
  "build:production": "webpack --env.production",
  "start": "webpack --hide-modules --watch",
  "lint": "npm run lint:scripts && npm run lint:styles",
  "test": "npm run lint"
}
```

**Build Features:**
- ✅ Source maps (development)
- ✅ BrowserSync
- ✅ Asset manifest
- ⚠️ Legacy ExtractTextPlugin (deprecated)
- ⚠️ UglifyJS (slower than Terser)
- ⚠️ Buble (limited ES2015+ support vs Babel)

### Aleph Nothing (No Build)

**Build System:** None
**Compiled Assets:** None
**Node Dependencies:** None

**Pattern:** Headless themes require zero build tooling - all logic handled by frontend app (Next.js)

---

## 3. Code Volume Comparison

### Lines of Code

| Theme | PHP Files | PHP LOC | JS Files | SCSS Files | Blade Templates | Total Complexity |
|-------|-----------|---------|----------|------------|-----------------|------------------|
| **Presser** | 13 | 2,006 | 49 | 89 | 85 | High |
| **Aleph Nothing** | 4 | 45 | 0 | 0 | 0 | Minimal |
| **Kelsey** | 11 | 393 | 19 | 77 | 114 | Medium |

**Key Insight:** Headless theme reduces codebase by **99.5%** (45 lines vs 2,006 in Presser)

### app/ Directory Breakdown

**Presser (2,006 LOC):**
- `setup.php`: ~311 lines (theme support, enqueue, localization)
- `custom.php`: ~1,037 lines (custom functions, ACF logic)
- `filters.php`: ~244 lines (WordPress filters)
- `helpers.php`: ~178 lines (utility functions)
- `admin.php`: ~94 lines (admin customizations)
- `ajaxLoadMorePosts.php`: ~77 lines (AJAX handlers)
- `Controllers/`: 9 controller files (Blade view data)

**Kelsey (393 LOC):**
- Simpler implementation, fewer customizations
- Similar file structure but less complex logic

**Aleph Nothing (43 LOC):**
- `functions.php`: 43 lines
  - Post thumbnail support (3 post types)
  - VIP Block Data API filter (wpautop for ACF WYSIWYG)
  - GraphQL term description filter (wpautop)
- `index.php`: 2 lines (silence is golden comment)
- 2 page templates: Empty files with template headers only

---

## 4. Laravel Blade Templating

### Template Organization

**Presser (85 templates):**
```
resources/views/
├── layouts/
│   ├── app.blade.php           # Main layout wrapper
│   └── blocks.blade.php        # Block editor layout
├── partials/
│   ├── header.blade.php        # Site header
│   ├── footer.blade.php        # Site footer
│   ├── sidebar.blade.php       # Sidebar
│   └── content-*.blade.php     # Post type content
├── blocks/                     # ACF/Gutenberg blocks
│   ├── acf/                    # ACF block templates
│   └── presser-*.blade.php     # Custom blocks
├── archive-*.blade.php         # Archive templates
├── single-*.blade.php          # Single post templates
├── page-*.blade.php            # Page templates
├── template-*.blade.php        # Custom page templates
├── index.blade.php             # Fallback template
└── 404.blade.php               # 404 error page
```

**Kelsey (114 templates):**
- More granular template breakdown (114 vs 85)
- Similar structure but more specialized templates

### Blade Syntax Examples

**Data Passing (Controller Pattern):**
```php
// app/Controllers/FrontPage.php
namespace App\Controllers;
use Sober\Controller\Controller;

class FrontPage extends Controller
{
    public function hero()
    {
        return get_field('hero_section');
    }

    public function featuredPosts()
    {
        return new WP_Query(['post_type' => 'post', 'posts_per_page' => 3]);
    }
}
```

**Blade Template Usage:**
```blade
{{-- resources/views/front-page.blade.php --}}
@extends('layouts.app')

@section('content')
  <section class="hero">
    <h1>{{ $hero['title'] }}</h1>
    <p>{{ $hero['description'] }}</p>
  </section>

  <section class="posts">
    @if($featuredPosts->have_posts())
      @while($featuredPosts->the_post())
        @php($featuredPosts->the_post())
        @include('partials.content-post')
      @endwhile
    @endif
  </section>
@endsection
```

**Pattern Confidence:** 100% for Sage themes

---

## 5. Asset Management

### Enqueueing Pattern (Sage)

**Location:** `app/setup.php`

```php
namespace App;

add_action('wp_enqueue_scripts', function () {
    // Enqueue compiled CSS from webpack manifest
    wp_enqueue_style('sage/main.css', asset_path('styles/main.css'), false, null);

    // Enqueue compiled JS from webpack manifest
    wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['jquery'], null, true);

    // Pass PHP data to JavaScript
    wp_localize_script('sage/main.js', 'ajaxGlobals', [
        'ajaxurl' => admin_url('admin-ajax.php'),
        'restUrl' => get_rest_url(),
        'currentLang' => function_exists('pll_current_language') ? pll_current_language() : false,
    ]);
}, 100);
```

**asset_path() Helper:**
- Reads `dist/assets-manifest.json` (generated by webpack)
- Returns versioned asset path with cache-busting hash
- Example: `styles/main.css?abc123def456`

### Webpack Asset Manifest

**Generated File:** `dist/assets-manifest.json`

```json
{
  "scripts/main.js": "scripts/main.js?f8a3c92b1e4d5678",
  "styles/main.css": "styles/main.css?f8a3c92b1e4d5678",
  "scripts/customizer.js": "scripts/customizer.js?f8a3c92b1e4d5678"
}
```

**Pattern Confidence:** 100% for Sage themes

---

## 6. Composer Dependencies (Sage Themes)

### Shared Dependencies (100% adoption)

Both Presser and Kelsey use identical Composer setup:

```json
{
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
    "squizlabs/php_codesniffer": "^2.8.0",
    "roots/sage-installer": "dev-master"
  }
}
```

**Key Packages:**
- **illuminate/support**: Laravel's Collection, Str, Arr helpers
- **roots/sage-lib**: Sage core functionality (asset manifest, Blade integration)
- **soberwp/controller**: Blade template controller pattern (pass data to views)
- **composer/installers**: WordPress-specific installation paths

**Pattern Confidence:** 100% for Sage themes

---

## 7. Headless Theme Architecture

### Minimal Requirements (Aleph Nothing)

**Required Files (3 total):**
1. **style.css** - Theme header (WordPress requirement)
2. **index.php** - Fallback template (WordPress requirement)
3. **functions.php** - Theme setup and GraphQL enhancements

### functions.php Responsibilities

```php
<?php
// 1. Theme Support
function policy_theme_setup() {
    add_theme_support('post-thumbnails', ['page', 'post', 'plc_airlab_posts']);
}
add_action('after_setup_theme', 'policy_theme_setup');

// 2. VIP Block Data API Filter (wpautop for ACF WYSIWYG)
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, ...) {
    // Apply wpautop to WYSIWYG fields in block data
    // Ensures proper paragraph formatting for headless consumption
    return $sourced_block;
}, 10, 4);

// 3. GraphQL Term Description Filter (wpautop)
add_filter('graphql_resolve_field', function($result, $source, ...) {
    // Format term descriptions for GraphQL responses
    if ($field_key === 'description' && $source instanceof \WPGraphQL\Model\Term) {
        return wpautop($result);
    }
    return $result;
}, 10, 9);
```

**Pattern:** Headless themes focus on data formatting for API consumption, not presentation logic.

**Pattern Confidence:** 100% (only headless theme analyzed, but pattern is well-established)

---

## 8. Build Process Maturity

### Presser (Modern - 2025)

**Strengths:**
- ✅ Webpack 5 with ESM support
- ✅ Modern ESLint 9 (flat config)
- ✅ Stylelint 16 with SCSS support
- ✅ Dart Sass 1.81.0 (modern @use/@forward)
- ✅ Node 20+ requirement
- ✅ Preact for smaller bundle sizes
- ✅ TerserPlugin for modern JS minification
- ✅ MiniCssExtractPlugin (current standard)

**Webpack Config Features:**
- Hot Module Replacement (HMR) via BrowserSync
- Multiple entry points (main, admin, customizer, Gutenberg)
- Asset manifest with random hash per build
- Configurable source maps
- Image optimization (imagemin-webpack-plugin)
- PostCSS pipeline (autoprefixer, cssnano)

### Kelsey (Legacy - 2022)

**Limitations:**
- ⚠️ Webpack 3 (missing features: mode, optimization.splitChunks, tree shaking improvements)
- ⚠️ Node 8+ (deprecated, security risks)
- ⚠️ ExtractTextPlugin (deprecated in Webpack 4+)
- ⚠️ UglifyJS (slower, less efficient than Terser)
- ⚠️ Buble transpiler (limited ES2015+ support vs Babel)
- ⚠️ Legacy ESLint/Stylelint configs

**Migration Needed:** Kelsey theme requires modernization to Webpack 5+ stack.

### Aleph Nothing (No Build)

**Philosophy:** Headless WordPress = backend only. Frontend (Next.js) handles all asset compilation.

**Pattern Confidence:** 100%

---

## 9. Template Hierarchy Customization

### Sage Theme Hierarchy (Modified)

Sage overrides WordPress template hierarchy to use `resources/views/` as the template directory:

**WordPress Default:**
```
wp-content/themes/sage/
├── index.php
├── single.php
├── archive.php
└── ...
```

**Sage Modified:**
```
wp-content/themes/sage/resources/
├── functions.php       # Entry point (WordPress sees this)
├── index.php          # Required fallback
└── views/             # Actual templates (Sage redirects here)
    ├── index.blade.php
    ├── single.blade.php
    └── ...
```

**Implementation (resources/functions.php):**
```php
array_map(
    'add_filter',
    ['theme_file_path', 'theme_file_uri', 'parent_theme_file_path', 'parent_theme_file_uri'],
    array_fill(0, 4, 'dirname')
);
```

**Effect:**
- `get_template_directory()` → `/themes/sage/resources`
- `locate_template()` → `/themes/sage/resources/views`

**Pattern Confidence:** 100% for Sage themes

---

## 10. Quantitative Summary

| Metric | Presser | Aleph Nothing | Kelsey |
|--------|---------|---------------|--------|
| **Framework** | Sage 9+ | None | Sage 9 |
| **PHP Files** | 13 | 4 | 11 |
| **PHP LOC** | 2,006 | 45 | 393 |
| **JS Files** | 49 | 0 | 19 |
| **SCSS Files** | 89 | 0 | 77 |
| **Blade Templates** | 85 | 0 | 114 |
| **Build System** | Webpack 5 | None | Webpack 3 |
| **Node Version** | 20+ | N/A | 8+ |
| **Composer Deps** | 6 | 0 | 6 |
| **npm Deps (dev)** | 58 | 0 | 29 |
| **npm Deps (prod)** | 7 | 0 | 4 |
| **Modernization** | ✅ Current | N/A | ⚠️ Legacy |

---

## 11. Critical Patterns Identified

### Universal Patterns (100% adoption where applicable)

1. **Sage Roots for Traditional Themes**: Both Presser and Kelsey use Sage (100%)
2. **PSR-4 Autoloading**: `App\` namespace for theme logic (100% Sage)
3. **Laravel Blade Templating**: `.blade.php` templates (100% Sage)
4. **Webpack Asset Compilation**: Both Sage themes use webpack (100%)
5. **Composer for PHP Dependencies**: All use composer (100% Sage)
6. **Asset Manifest Pattern**: `asset_path()` helper + `assets-manifest.json` (100% Sage)
7. **Controller Pattern**: SoberWP Controller for Blade data (100% Sage)
8. **Minimal Headless Theme**: Aleph Nothing proves 45-line viability (100% headless)

### Divergent Patterns

1. **Build Tooling Maturity**: Presser modern (Webpack 5), Kelsey legacy (Webpack 3)
2. **Node Version Requirements**: Presser 20+, Kelsey 8+ (12 major versions behind)
3. **Template Granularity**: Kelsey 114 templates, Presser 85 (34% more granular)
4. **JavaScript Dependencies**: Presser 65 packages, Kelsey 33 packages
5. **PHP Complexity**: Presser 2,006 LOC, Kelsey 393 LOC (410% more complex)

### Critical Gaps

1. **Kelsey Modernization**: Webpack 3 → 5, Node 8 → 20, ExtractTextPlugin → MiniCssExtractPlugin
2. **No Testing Infrastructure**: Zero unit tests in any theme (0% adoption)
3. **No TypeScript**: All JavaScript is plain ES6+ (0% TypeScript adoption)

---

## 12. Recommendations for Documentation

### High Priority Docs (8 planned)

1. **Sage Roots Framework Setup** (100% confidence)
   - PSR-4 autoloading pattern
   - Directory structure requirements
   - Composer dependency setup

2. **Laravel Blade Templating in WordPress** (100% confidence)
   - Template hierarchy with Blade
   - Controller pattern for view data
   - Blade syntax vs PHP templates

3. **Headless Theme Architecture** (100% confidence)
   - Minimal file requirements
   - GraphQL data formatting
   - Admin-only WordPress setup

4. **Webpack Asset Compilation** (100% confidence)
   - Modern webpack 5 config
   - Asset manifest pattern
   - Entry point organization

5. **Theme Build Process Modernization** (67% confidence)
   - Webpack 3 → 5 migration
   - Node version upgrades
   - Deprecated plugin replacements

6. **Theme vs MU-Plugins Separation** (observational)
   - When to use theme vs mu-plugins
   - Code organization best practices

7. **Composer Autoloading in Themes** (100% confidence)
   - PSR-4 namespace setup
   - Required Sage dependencies

8. **Template Directory Customization** (100% confidence)
   - Sage's view directory override
   - WordPress template hierarchy hooks

### Medium Priority Semgrep Rules (4 planned)

1. **Enforce Theme Header Requirements** - Detect missing style.css headers
2. **Warn on Direct wp_enqueue in Templates** - Enforce app/setup.php pattern
3. **Require PSR-4 Autoload Namespace** - Detect missing composer.json autoload
4. **Warn on Legacy Webpack Plugins** - Detect ExtractTextPlugin, UglifyJsPlugin

---

## Next Steps

1. ✅ Complete cross-theme comparison analysis (THIS DOCUMENT)
2. ⏳ Generate 8 RAG-optimized documentation files
3. ⏳ Generate 4 Semgrep enforcement rules
4. ⏳ Move to Phase 4, Domain 7: Multisite Patterns
5. ⏳ Move to Phase 4, Domain 8: Block Development

**Estimated Time Remaining:** 1.5 hours (docs + Semgrep rules)
