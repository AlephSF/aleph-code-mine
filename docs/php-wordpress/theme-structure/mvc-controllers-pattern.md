---
title: "MVC Controllers Pattern with SoberWP for WordPress Themes"
category: "theme-structure"
subcategory: "mvc-architecture"
tags: ["mvc", "soberwp", "controller", "sage", "data-layer", "separation-of-concerns"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "29%"
last_updated: "2026-02-13"
---

# MVC Controllers Pattern with SoberWP for WordPress Themes

## Overview

MVC controllers separate business logic from presentation in WordPress themes via SoberWP Controller package. **29% of analyzed themes** (4 of 14) use MVC pattern with **9 controller files** in kelsey theme, binding controller methods to Blade templates automatically based on template hierarchy.

Controllers provide data to views without template logic, returning arrays/objects accessible as variables in Blade. Pattern prevents `WP_Query` calls and complex PHP in templates, improving testability and maintainability.

**Key Benefits:**
- Logic separation (business logic in controllers, presentation in views)
- Automatic variable binding (methods become Blade variables)
- Template hierarchy awareness (matches `front-page.blade.php` to `FrontPage` controller)
- Inheritance (base `App` controller for all templates, specific controllers override)
- Cleaner templates (no PHP queries, just Blade directives and output)

## Controller Structure

Controllers extend `Sober\Controller\Controller` base class, placed in `app/Controllers/` directory with PSR-4 `App\Controllers` namespace. Public methods automatically available as variables in corresponding Blade templates.

## Base Controller (app/Controllers/App.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class App extends Controller
{
    /**
     * Return site name for all templates
     */
    public function siteName()
    {
        return get_bloginfo('name');
    }

    /**
     * Return site description
     */
    public function siteDescription()
    {
        return get_bloginfo('description');
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

    /**
     * Calculate reading time from post content
     */
    public static function timeToRead()
    {
        $content = get_post_field('post_content');
        $content = strip_shortcodes($content);
        $content = wp_strip_all_tags($content);
        $word_count = count(preg_split('/\s+/', $content));

        // Calculate additional time for images (12s first image, 11s second, down to 3s after 10th)
        $image_count = substr_count(strtolower($content), '<img ');
        $additional_time = 0;

        for ($i = 1; $i <= $image_count; $i++) {
            $additional_time += $i >= 10 ? 3 : (13 - $i);
        }

        $wpm = 250;  // Average words per minute
        $minutes = ceil(($word_count + $additional_time * $wpm / 60) / $wpm);

        return $minutes . ' min read';
    }
}
```

**Base Controller Features:**
- Loaded for **all** templates automatically
- Provides global data (`siteName`, `siteDescription`)
- Static methods accessible without controller instance
- All child controllers inherit methods

## Template-Specific Controller (app/Controllers/FrontPage.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class FrontPage extends Controller
{
    /**
     * Get featured posts for homepage
     */
    public function featuredPosts()
    {
        return get_posts([
            'numberposts' => 3,
            'post_type' => 'post',
            'meta_key' => 'featured',
            'meta_value' => '1',
            'orderby' => 'date',
            'order' => 'DESC',
        ]);
    }

    /**
     * Get recent blog posts
     */
    public function recentPosts()
    {
        return get_posts([
            'numberposts' => 5,
            'post_type' => 'post',
            'orderby' => 'date',
            'order' => 'DESC',
        ]);
    }

    /**
     * Get testimonials
     */
    public function testimonials()
    {
        return get_posts([
            'post_type' => 'testimonial',
            'posts_per_page' => -1,
            'orderby' => 'menu_order',
            'order' => 'ASC',
        ]);
    }

    /**
     * Get call-to-action data from ACF
     */
    public function ctaSection()
    {
        return [
            'heading' => get_field('cta_heading'),
            'text' => get_field('cta_text'),
            'button_text' => get_field('cta_button_text'),
            'button_url' => get_field('cta_button_url'),
        ];
    }
}
```

**Controller Binding:**
- Filename `FrontPage.php` binds to `front-page.blade.php` template
- Public methods become Blade variables: `$featuredPosts`, `$recentPosts`, `$testimonials`, `$ctaSection`
- Methods execute once per request, results cached
- Inherits `siteName()`, `siteDescription()`, `title()` from `App` controller

## Archive Controller (app/Controllers/Archive.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class Archive extends Controller
{
    /**
     * Archive title (category, tag, post type, etc.)
     */
    public function archiveTitle()
    {
        return get_the_archive_title();
    }

    /**
     * Archive description
     */
    public function archiveDescription()
    {
        return get_the_archive_description();
    }

    /**
     * Total posts in archive
     */
    public function totalPosts()
    {
        global $wp_query;
        return $wp_query->found_posts;
    }

    /**
     * Current taxonomy term
     */
    public function currentTerm()
    {
        if (is_category() || is_tag() || is_tax()) {
            return get_queried_object();
        }

        return null;
    }

    /**
     * Get related categories (when viewing category archive)
     */
    public function relatedCategories()
    {
        if (!is_category()) {
            return [];
        }

        $current_category = get_queried_object();

        return get_categories([
            'exclude' => $current_category->term_id,
            'number' => 5,
            'orderby' => 'count',
            'order' => 'DESC',
        ]);
    }
}
```

## Single Post Controller (app/Controllers/SinglePost.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class SinglePost extends Controller
{
    /**
     * Get author data
     */
    public function authorData()
    {
        $author_id = get_the_author_meta('ID');

        return [
            'name' => get_the_author_meta('display_name'),
            'bio' => get_the_author_meta('description'),
            'avatar' => get_avatar_url($author_id, ['size' => 96]),
            'url' => get_author_posts_url($author_id),
            'post_count' => count_user_posts($author_id, 'post'),
        ];
    }

    /**
     * Get related posts by category
     */
    public function relatedPosts()
    {
        $categories = wp_get_post_categories(get_the_ID());

        if (empty($categories)) {
            return [];
        }

        return get_posts([
            'category__in' => $categories,
            'post__not_in' => [get_the_ID()],
            'posts_per_page' => 3,
            'orderby' => 'rand',
        ]);
    }

    /**
     * Get post metadata (tags, categories)
     */
    public function postMeta()
    {
        return [
            'categories' => get_the_category(),
            'tags' => get_the_tags(),
            'date' => get_the_date(),
            'modified' => get_the_modified_date(),
            'reading_time' => App::timeToRead(),
        ];
    }
}
```

## Template Hierarchy Mapping

SoberWP Controller automatically binds controllers to templates based on WordPress template hierarchy naming conventions. Converts template filename to PascalCase class name.

| Template File | Controller Class | Binding |
|---------------|------------------|---------|
| `front-page.blade.php` | `FrontPage` | Exact match |
| `single-post.blade.php` | `SinglePost` | Exact match |
| `archive.blade.php` | `Archive` | Exact match |
| `category.blade.php` | `Category` | Exact match |
| `page-about.blade.php` | `PageAbout` | Custom page template |
| `taxonomy-genre.blade.php` | `TaxonomyGenre` | Custom taxonomy |
| `index.blade.php` | `Index` | Fallback |

**Conversion Rules:**
- Hyphens → CamelCase (`front-page` → `FrontPage`)
- Underscores → CamelCase (`single_post` → `SinglePost`)
- Lowercase → PascalCase (`archive` → `Archive`)

**Controller Precedence:**
1. Specific controller (`FrontPage`)
2. Base controller (`App`) - always loaded
3. No controller - template uses global WordPress data only

## Variable Binding in Blade

Controller public methods become Blade variables accessible via `$methodName` syntax. Method names converted from camelCase to $camelCase variable.

## Controller Method → Blade Variable

```php
// app/Controllers/FrontPage.php
public function featuredPosts() {
    return get_posts(['numberposts' => 3]);
}

public function ctaSection() {
    return ['heading' => 'Get Started', 'url' => '/signup'];
}
```

**Blade Template (resources/views/front-page.blade.php):**
```blade
@extends('layouts.app')

@section('content')
  {{-- Base controller variables --}}
  <h1>{{ $siteName }}</h1>
  <p>{{ $siteDescription }}</p>

  {{-- FrontPage controller variables --}}
  @if($featuredPosts)
    <div class="featured-posts">
      @foreach($featuredPosts as $post)
        <article>
          <h2>{{ get_the_title($post) }}</h2>
        </article>
      @endforeach
    </div>
  @endif

  {{-- Array from controller --}}
  <section class="cta">
    <h2>{{ $ctaSection['heading'] }}</h2>
    <a href="{{ $ctaSection['url'] }}">Sign Up</a>
  </section>
@endsection
```

**Variable Access Rules:**
- Camel case method → camel case variable (`featuredPosts()` → `$featuredPosts`)
- Public methods only (private/protected not accessible)
- Methods execute once, results cached per request
- Static methods accessible: `{{ App\title() }}` or via base controller

## Static vs Instance Methods

Controllers support both static methods (called explicitly) and instance methods (auto-bound to variables). Use static for utility functions called from within templates, instance for data binding.

## Static Methods (Explicit Calls)

```php
// app/Controllers/App.php
public static function title()
{
    // Complex title logic...
    return $title;
}

public static function formatDate($date)
{
    return date('F j, Y', strtotime($date));
}
```

**Usage in Blade:**
```blade
<h1>{{ App\title() }}</h1>

<time>{{ App\formatDate($post->post_date) }}</time>
```

## Instance Methods (Auto-Binding)

```php
// app/Controllers/FrontPage.php
public function featuredPosts()
{
    return get_posts(['numberposts' => 3]);
}
```

**Usage in Blade:**
```blade
@foreach($featuredPosts as $post)
  <!-- Automatic binding, no function call -->
@endforeach
```

**When to Use:**
- **Instance methods:** Data fetching (posts, terms, metadata)
- **Static methods:** Utilities (formatting, calculations, called from templates)

## Advanced Controller Patterns

## Returning Collections

```php
// app/Controllers/Archive.php
public function posts()
{
    global $wp_query;

    return collect($wp_query->posts)->map(function ($post) {
        return [
            'id' => $post->ID,
            'title' => get_the_title($post),
            'excerpt' => get_the_excerpt($post),
            'permalink' => get_permalink($post),
            'thumbnail' => get_the_post_thumbnail_url($post, 'medium'),
            'author' => get_the_author_meta('display_name', $post->post_author),
            'date' => get_the_date('', $post),
            'categories' => wp_get_post_categories($post->ID, ['fields' => 'names']),
        ];
    });
}
```

**Blade Usage:**
```blade
@foreach($posts as $post)
  <article>
    <h2>{{ $post['title'] }}</h2>
    <img src="{{ $post['thumbnail'] }}" alt="{{ $post['title'] }}">
    <p>{{ $post['excerpt'] }}</p>
    <a href="{{ $post['permalink'] }}">Read More</a>
  </article>
@endforeach
```

## Conditional Data Loading

```php
// app/Controllers/Page.php
public function sidebar()
{
    // Don't load sidebar data for full-width pages
    if (is_page_template('template-fullwidth.blade.php')) {
        return null;
    }

    return get_posts([
        'post_type' => 'sidebar_widget',
        'posts_per_page' => 5,
    ]);
}
```

## Nested Data Structures

```php
// app/Controllers/FrontPage.php
public function homeData()
{
    return [
        'hero' => [
            'heading' => get_field('hero_heading'),
            'subheading' => get_field('hero_subheading'),
            'background_image' => get_field('hero_background_image'),
            'cta_button' => [
                'text' => get_field('hero_cta_text'),
                'url' => get_field('hero_cta_url'),
            ],
        ],
        'features' => collect(get_field('features'))->map(function ($feature) {
            return [
                'icon' => $feature['icon'],
                'title' => $feature['title'],
                'description' => $feature['description'],
            ];
        }),
        'testimonials' => get_posts([
            'post_type' => 'testimonial',
            'posts_per_page' => 3,
        ]),
    ];
}
```

**Blade Usage:**
```blade
<section class="hero" style="background-image: url('{{ $homeData['hero']['background_image'] }}')">
  <h1>{{ $homeData['hero']['heading'] }}</h1>
  <p>{{ $homeData['hero']['subheading'] }}</p>
  <a href="{{ $homeData['hero']['cta_button']['url'] }}">
    {{ $homeData['hero']['cta_button']['text'] }}
  </a>
</section>

<div class="features">
  @foreach($homeData['features'] as $feature)
    <div class="feature">
      <img src="{{ $feature['icon'] }}" alt="">
      <h3>{{ $feature['title'] }}</h3>
      <p>{{ $feature['description'] }}</p>
    </div>
  @endforeach
</div>
```

## Performance Considerations

Controllers execute once per request, results cached in memory. Expensive queries run once regardless of how many times variable accessed in template.

## Efficient Data Fetching

```php
// app/Controllers/Archive.php

// BAD - Executes query each time $posts accessed in template
public function posts()
{
    return new WP_Query(['posts_per_page' => 10]);
}

// GOOD - Query executes once, results cached
public function posts()
{
    global $wp_query;
    return $wp_query->posts;  // Reuse main query
}

// BETTER - Transform to usable array once
public function posts()
{
    global $wp_query;

    return array_map(function ($post) {
        return [
            'id' => $post->ID,
            'title' => get_the_title($post),
            'permalink' => get_permalink($post),
        ];
    }, $wp_query->posts);
}
```

## Lazy Loading

```php
// app/Controllers/SinglePost.php

// Heavy query - only run if needed
public function comments()
{
    if (!comments_open()) {
        return [];
    }

    return get_comments([
        'post_id' => get_the_ID(),
        'status' => 'approve',
        'hierarchical' => 'threaded',
    ]);
}
```

**Blade Usage:**
```blade
@if($comments)
  <section class="comments">
    <!-- Comments only loaded if comments_open() -->
  </section>
@endif
```

## Testing Controllers

Controllers improve testability by isolating business logic from views. Unit test controller methods without rendering templates.

## PHPUnit Test Example

```php
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Controllers\FrontPage;

class FrontPageControllerTest extends TestCase
{
    public function test_featured_posts_returns_array()
    {
        $controller = new FrontPage();
        $posts = $controller->featuredPosts();

        $this->assertIsArray($posts);
        $this->assertCount(3, $posts);
    }

    public function test_cta_section_has_required_keys()
    {
        $controller = new FrontPage();
        $cta = $controller->ctaSection();

        $this->assertArrayHasKey('heading', $cta);
        $this->assertArrayHasKey('text', $cta);
        $this->assertArrayHasKey('button_url', $cta);
    }
}
```

## Common Patterns

## Pagination

```php
// app/Controllers/Archive.php
public function pagination()
{
    global $wp_query;

    return [
        'current_page' => max(1, get_query_var('paged')),
        'total_pages' => $wp_query->max_num_pages,
        'per_page' => get_option('posts_per_page'),
        'total_posts' => $wp_query->found_posts,
    ];
}
```

## Breadcrumbs

```php
// app/Controllers/App.php (base controller)
public static function breadcrumbs()
{
    if (is_front_page()) {
        return [];
    }

    $crumbs = [['title' => 'Home', 'url' => home_url('/')]];

    if (is_category() || is_single()) {
        $categories = get_the_category();
        if (!empty($categories)) {
            $crumbs[] = [
                'title' => $categories[0]->name,
                'url' => get_category_link($categories[0]->term_id),
            ];
        }
    }

    if (is_single()) {
        $crumbs[] = ['title' => get_the_title(), 'url' => null];
    }

    return $crumbs;
}
```

## Sidebar Configuration

```php
// app/Controllers/App.php (base controller)
public static function showSidebar()
{
    return !in_array(true, [
        is_404(),
        is_front_page(),
        is_page_template('template-fullwidth.blade.php'),
    ]);
}
```

## Related Patterns

- **Sage Framework:** See `sage-framework-structure.md` for MVC setup
- **Blade Templating:** See `blade-templating-pattern.md` for view layer
- **Template Hierarchy:** See `template-hierarchy-usage.md` for binding rules

## References

- **SoberWP Controller:** https://github.com/soberwp/controller
- **Sage Controllers:** https://roots.io/sage/docs/blade-templates/#controllers
- **Laravel Collections:** https://laravel.com/docs/8.x/collections
