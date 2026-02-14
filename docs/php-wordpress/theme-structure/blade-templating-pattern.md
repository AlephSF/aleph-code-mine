---
title: "Blade Templating Engine for WordPress Themes"
category: "theme-structure"
subcategory: "templating"
tags: ["blade", "laravel", "templating", "sage", "inheritance", "components"]
stack: "php-wp"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "29%"
last_updated: "2026-02-13"
---

# Blade Templating Engine for WordPress Themes

## Overview

Blade templating engine (Laravel) brings template inheritance, component reusability, and cleaner syntax to WordPress themes via Sage framework. **348 total Blade templates** analyzed across 4 Sage themes (thekelsey: 114, presser: 128, onboard: 53, protools: 53), demonstrating significant adoption for content-heavy sites.

Blade compiles to optimized PHP and caches compiled output in `wp-content/uploads/cache/`, eliminating template compilation overhead on subsequent page loads. First-time compilation adds ~50-100ms latency, subsequent renders use cached PHP with zero overhead.

**Key Benefits:**
- Template inheritance (`@extends`, `@section`, `@yield`)
- Automatic output escaping (XSS prevention via `{{ }}`)
- Clean syntax (no `<?php ?>` tags)
- Component partials (`@include`)
- Control structures (`@if`, `@foreach`, `@while`)
- WordPress integration via `{!! !!}` for hooks

## Directory Structure

Blade templates organized in `resources/views/` with subdirectories for layouts, partials, and blocks. File extension `.blade.php` signals Blade compilation vs standard `.php` templates.

```
resources/views/
├── layouts/
│   ├── app.blade.php             # Base layout
│   └── base.blade.php            # Alternative base
├── partials/
│   ├── header.blade.php          # Header component
│   ├── footer.blade.php          # Footer component
│   ├── sidebar.blade.php         # Sidebar
│   ├── breadcrumbs.blade.php    # Breadcrumbs
│   └── content-*.blade.php       # Content components
├── blocks/                       # Gutenberg blocks
│   ├── block.blade.php           # Base block
│   ├── core-image.blade.php      # Core overrides
│   └── custom-*.blade.php        # Custom blocks
├── front-page.blade.php          # Homepage
├── index.blade.php               # Main loop
├── single.blade.php              # Single post
├── page.blade.php                # Static page
├── archive.blade.php             # Archive
├── search.blade.php              # Search results
├── 404.blade.php                 # Error page
└── template-*.blade.php          # Custom page templates
```

**WordPress Template Hierarchy:** Blade files follow same hierarchy as traditional PHP templates. WordPress resolves `front-page.blade.php` same as `front-page.php`.

## Template Inheritance

Blade's most powerful feature - define base layout once, extend in child templates via `@extends` and `@section` directives. Eliminates duplicate header/footer code across templates.

## Base Layout (resources/views/layouts/app.blade.php)

```blade
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

**Key Directives:**
- `{!! get_language_attributes() !!}`: Unescaped output for WordPress hooks
- `@include('partials.head')`: Include partial template
- `@php(body_class())`: Execute PHP function
- `@yield('content')`: Content injection point
- `@if (App\display_sidebar())`: Conditional sidebar

## Child Template (resources/views/front-page.blade.php)

```blade
@extends('layouts.app')

@section('content')
  <section class="hero">
    <h1>{{ $siteName }}</h1>
    <p>{{ $siteDescription }}</p>
  </section>

  @if($featuredPosts)
    <section class="featured-posts">
      <h2>Featured Articles</h2>

      <div class="posts-grid">
        @foreach($featuredPosts as $post)
          <article class="post-card">
            @if(has_post_thumbnail($post))
              <div class="thumbnail">
                {!! get_the_post_thumbnail($post, 'medium') !!}
              </div>
            @endif

            <h3>
              <a href="{{ get_permalink($post) }}">
                {{ get_the_title($post) }}
              </a>
            </h3>

            <div class="excerpt">
              {{ wp_trim_words(get_the_excerpt($post), 25) }}
            </div>

            <a href="{{ get_permalink($post) }}" class="read-more">
              Read More &rarr;
            </a>
          </article>
        @endforeach
      </div>
    </section>
  @endif

  @include('partials.cta')
@endsection
```

**Template Variables:** `$featuredPosts`, `$siteName`, `$siteDescription` provided by `App\Controllers\FrontPage` controller (MVC pattern).

## Output Escaping

Blade automatically escapes output via `{{ }}` syntax, preventing XSS attacks. Use `{!! !!}` **only** for trusted WordPress hooks and HTML output.

## Escaped Output (Default - XSS Safe)

```blade
{{-- Automatic escaping with {{ }} --}}
<h1>{{ get_the_title() }}</h1>
<!-- Renders: <h1>Post &amp; Title</h1> -->

<div class="author">{{ get_the_author() }}</div>
<!-- Renders: <div class="author">John &lt;script&gt;</div> -->

<a href="{{ get_permalink() }}">{{ $linkText }}</a>
<!-- All variables and functions auto-escaped -->
```

**Escaping Functions Applied:**
- Strings: `htmlspecialchars($value, ENT_QUOTES, 'UTF-8', false)`
- Objects with `__toString()`: Same escaping
- Already escaped: No double-escaping

## Unescaped Output (Trusted HTML Only)

```blade
{{-- Unescaped output with {!! !!} - USE CAREFULLY --}}

{!! get_the_content() !!}
<!-- Post content contains HTML, don't escape -->

{!! wp_nav_menu(['theme_location' => 'primary', 'echo' => false]) !!}
<!-- WordPress menus contain HTML markup -->

{!! get_the_post_thumbnail($post, 'large') !!}
<!-- Thumbnail HTML includes <img> tag -->

@php(do_action('wp_head'))
<!-- WordPress hooks output HTML, use @php() not {!! !!} -->
```

**Security Rule:** Use `{!! !!}` **only** for:
1. WordPress core functions returning trusted HTML
2. Content from `wp_kses_post()` or similar sanitization
3. Verified safe HTML from developers (not user input)

**Never use `{!! !!}` for:**
- User input (comments, post titles from untrusted sources)
- Database values without sanitization
- `$_GET`, `$_POST`, `$_REQUEST` variables
- External API responses

## Control Structures

Blade provides clean control structure syntax without `<?php ?>` tags. All PHP control structures available via `@directive` syntax.

## Conditionals

```blade
@if($featuredImage)
  <img src="{{ $featuredImage }}" alt="{{ $imageAlt }}">
@elseif($fallbackImage)
  <img src="{{ $fallbackImage }}" alt="Fallback">
@else
  <div class="no-image-placeholder"></div>
@endif

@unless($hideAuthor)
  <span class="author">By {{ $authorName }}</span>
@endunless

@isset($metadata)
  <div class="metadata">{{ $metadata }}</div>
@endisset

@empty($posts)
  <p>No posts found.</p>
@endempty

{{-- PHP function conditionals --}}
@if(is_front_page())
  <h1>Welcome to {{ bloginfo('name') }}</h1>
@endif

@if(has_post_thumbnail())
  {!! get_the_post_thumbnail('large') !!}
@endif
```

## Loops

```blade
{{-- Array/collection loops --}}
@foreach($posts as $post)
  <article>
    <h2>{{ get_the_title($post) }}</h2>
  </article>
@endforeach

{{-- Loop with index --}}
@foreach($items as $index => $item)
  <li class="{{ $loop->first ? 'first' : '' }} {{ $loop->last ? 'last' : '' }}">
    {{ $index }}. {{ $item }}
  </li>
@endforeach

{{-- WordPress Loop --}}
@while(have_posts())
  @php(the_post())

  <article @php(post_class())>
    <h2>
      <a href="{{ the_permalink() }}">
        {{ the_title() }}
      </a>
    </h2>

    {!! the_content() !!}
  </article>
@endwhile

{{-- For loop --}}
@for($i = 0; $i < 5; $i++)
  <div class="item-{{ $i }}">Item {{ $i }}</div>
@endfor

{{-- Loop variable ($loop) --}}
@foreach($posts as $post)
  @if($loop->first)
    <div class="first-post featured">
  @elseif($loop->last)
    <div class="last-post">
  @else
    <div class="post">
  @endif

    <!-- Post content -->

    </div>

  @if($loop->remaining === 3)
    <div class="ad-break">Advertisement</div>
  @endif
@endforeach
```

**$loop Variable Properties:**
- `$loop->index`: Current iteration (0-indexed)
- `$loop->iteration`: Current iteration (1-indexed)
- `$loop->remaining`: Iterations remaining
- `$loop->count`: Total items
- `$loop->first`: First iteration (bool)
- `$loop->last`: Last iteration (bool)
- `$loop->even`: Even iteration (bool)
- `$loop->odd`: Odd iteration (bool)
- `$loop->depth`: Nesting level
- `$loop->parent`: Parent loop variable (nested loops)

## Component Partials

Break templates into reusable partials via `@include` directive. Partials receive all variables from parent scope plus additional data via second parameter.

## Header Partial (resources/views/partials/header.blade.php)

```blade
<header class="site-header">
  <div class="container">
    <div class="header-inner">

      <div class="site-branding">
        @if(has_custom_logo())
          {!! get_custom_logo() !!}
        @else
          <a href="{{ home_url('/') }}" class="site-title">
            {{ get_bloginfo('name') }}
          </a>
        @endif
      </div>

      @if(has_nav_menu('primary_navigation'))
        <nav class="primary-navigation" aria-label="Primary Navigation">
          {!! wp_nav_menu([
            'theme_location' => 'primary_navigation',
            'container' => false,
            'menu_class' => 'nav-menu',
            'echo' => false
          ]) !!}
        </nav>
      @endif

      <div class="header-actions">
        @include('partials.search-form')

        @if($ctaUrl)
          <a href="{{ $ctaUrl }}" class="btn btn-primary">
            {{ $ctaText }}
          </a>
        @endif
      </div>

    </div>
  </div>
</header>
```

**Usage in Layout:**
```blade
@include('partials.header')
```

## Content Partial with Data (resources/views/partials/post-card.blade.php)

```blade
<article class="post-card {{ $cardClass ?? '' }}">
  @if($showThumbnail && has_post_thumbnail($post))
    <div class="thumbnail">
      <a href="{{ get_permalink($post) }}">
        {!! get_the_post_thumbnail($post, $thumbnailSize ?? 'medium') !!}
      </a>
    </div>
  @endif

  <div class="post-info">
    <h3 class="post-title">
      <a href="{{ get_permalink($post) }}">{{ get_the_title($post) }}</a>
    </h3>

    @if($showMeta)
      <div class="post-meta">
        <span class="date">{{ get_the_date('', $post) }}</span>
        <span class="author">By {{ get_the_author_meta('display_name', $post->post_author) }}</span>
      </div>
    @endif

    @if($showExcerpt)
      <div class="excerpt">{{ wp_trim_words(get_the_excerpt($post), $excerptLength ?? 25) }}</div>
    @endif

    <a href="{{ get_permalink($post) }}" class="read-more">{{ $readMoreText ?? 'Read More' }} &rarr;</a>
  </div>
</article>
```

**Usage with Custom Data:**
```blade
@foreach($posts as $post)
  @include('partials.post-card', [
    'post' => $post,
    'showThumbnail' => true,
    'thumbnailSize' => 'large',
    'excerptLength' => 30,
    'cardClass' => 'featured'
  ])
@endforeach
```

**Variable Scoping:** Partials inherit all parent variables. Pass additional data via second parameter (array). Use `{{ $var ?? 'default' }}` for optional variables.

## WordPress Integration

Blade integrates with WordPress template hierarchy, hooks, and functions via special syntax for unescaped output and PHP execution.

## WordPress Hooks

```blade
{{-- wp_head() and wp_footer() hooks --}}
<html>
<head>
  <meta charset="{{ bloginfo('charset') }}">
  @php(wp_head())
</head>
<body @php(body_class())>

  @php(do_action('get_header'))

  <!-- Template content -->

  @php(do_action('get_footer'))
  @php(wp_footer())
</body>
</html>
```

**Why `@php()` not `{!! !!}`:** Hooks output directly to buffer, don't return values. `@php(wp_head())` executes function, `{!! wp_head() !!}` would try to escape null return value.

## WordPress Functions

```blade
{{-- Escaped output (safe) --}}
{{ bloginfo('name') }}
{{ get_the_title() }}
{{ get_the_date() }}
{{ get_the_author() }}

{{-- Unescaped HTML (WordPress core functions) --}}
{!! get_the_content() !!}
{!! get_the_post_thumbnail('large') !!}
{!! wp_nav_menu(['echo' => false]) !!}

{{-- Functions in conditionals --}}
@if(is_front_page())
  <h1>Homepage</h1>
@endif

@if(has_post_thumbnail())
  {!! the_post_thumbnail('large') !!}
@endif

@if(comments_open())
  @include('partials.comments')
@endif

{{-- Functions in loops --}}
@while(have_posts())
  @php(the_post())
  @include('partials.content', ['post_type' => get_post_type()])
@endwhile
```

## Custom PHP

```blade
{{-- Inline PHP --}}
@php
  $categories = get_the_category();
  $primary_cat = !empty($categories) ? $categories[0] : null;
@endphp

@if($primary_cat)
  <span class="category">{{ $primary_cat->name }}</span>
@endif

{{-- Multi-line PHP blocks --}}
@php
  $args = [
    'post_type' => 'post',
    'posts_per_page' => 3,
    'meta_key' => 'featured',
    'meta_value' => '1',
  ];

  $featured_posts = new WP_Query($args);
@endphp

@if($featured_posts->have_posts())
  <div class="featured-posts">
    @while($featured_posts->have_posts())
      @php($featured_posts->the_post())
      @include('partials.post-card')
    @endwhile
    @php(wp_reset_postdata())
  </div>
@endif
```

**Best Practice:** Move complex PHP logic to Controllers (`app/Controllers/`), not templates. Templates should receive data from controllers, not query database directly.

## Gutenberg Block Integration

Blade templates for custom Gutenberg blocks registered via ACF `acf_register_block_type()` with Blade render callback.

## Block Registration (app/setup.php)

```php
add_action('acf/init', function () {
    if (function_exists('acf_register_block_type')) {
        acf_register_block_type([
            'name' => 'slideshow',
            'title' => __('Slideshow', 'sage'),
            'description' => __('Custom slideshow block', 'sage'),
            'category' => 'formatting',
            'icon' => 'images-alt2',
            'keywords' => ['slideshow', 'slider', 'carousel'],
            'supports' => [
                'align' => ['wide', 'full'],
                'mode' => true,
            ],
            'render_callback' => function ($block, $content = '', $is_preview = false) {
                echo view('blocks.thekelsey-slideshow', [
                    'block' => $block,
                    'is_preview' => $is_preview,
                ]);
            },
        ]);
    }
});
```

## Block Template (resources/views/blocks/thekelsey-slideshow.blade.php)

```blade
<div class="slideshow-block {{ $block['className'] ?? '' }}" id="{{ $block['id'] }}">
  @if($is_preview)
    <div class="block-preview"><p>Slideshow Block Preview</p></div>
  @else
    @php($slides = get_field('slides'))

    @if($slides)
      <div class="slideshow-container" data-autoplay="{{ get_field('autoplay') ? 'true' : 'false' }}">
        @foreach($slides as $index => $slide)
          <div class="slide {{ $loop->first ? 'active' : '' }}">
            @if($slide['image'])
              <img src="{{ $slide['image']['url'] }}" alt="{{ $slide['image']['alt'] ?? '' }}">
            @endif

            @if($slide['caption'])
              <div class="slide-caption">{!! $slide['caption'] !!}</div>
            @endif
          </div>
        @endforeach

        @if(count($slides) > 1)
          <button class="prev" aria-label="Previous slide">&larr;</button>
          <button class="next" aria-label="Next slide">&rarr;</button>

          <div class="dots">
            @foreach($slides as $index => $slide)
              <button class="dot {{ $loop->first ? 'active' : '' }}" data-index="{{ $index }}" aria-label="Go to slide {{ $index + 1 }}"></button>
            @endforeach
          </div>
        @endif
      </div>
    @endif
  @endif
</div>
```

**Analyzed Blocks:** kelsey theme has 12 custom block Blade templates (core-image, core-group, core-pullquote, 9 custom blocks).

## Custom Page Templates

Create custom page templates with `Template Name:` comment in Blade file. WordPress detects and shows in Page Attributes dropdown.

## Template with Blade Syntax (resources/views/template-fullwidth.blade.php)

```blade
{{--
  Template Name: Full Width
  Template Post Type: page
--}}

@extends('layouts.app')

@section('content')
  @while(have_posts()) @php(the_post())

    <article @php(post_class('fullwidth-page'))>

      <header class="entry-header">
        <h1 class="entry-title">{{ get_the_title() }}</h1>

        @if($subtitle = get_field('page_subtitle'))
          <p class="subtitle">{{ $subtitle }}</p>
        @endif
      </header>

      @if(has_post_thumbnail())
        <div class="featured-image">
          {!! get_the_post_thumbnail(null, 'full') !!}
        </div>
      @endif

      <div class="entry-content">
        {!! get_the_content() !!}
      </div>

      @if($ctaSections = get_field('cta_sections'))
        <div class="cta-sections">
          @foreach($ctaSections as $section)
            <div class="cta-section">
              <h2>{{ $section['heading'] }}</h2>
              <p>{{ $section['text'] }}</p>
              <a href="{{ $section['link']['url'] }}" class="btn btn-primary">
                {{ $section['link']['title'] }}
              </a>
            </div>
          @endforeach
        </div>
      @endif

    </article>

  @endwhile
@endsection
```

**Template Comment Syntax:**
- `Template Name:` Required (appears in dropdown)
- `Template Post Type:` Optional (restrict to post types)
- Comments use `{{-- --}}` not `/* */`

## Compilation and Caching

Blade compiles templates to optimized PHP on first render, caches compiled output. Subsequent renders use cached PHP with zero compilation overhead.

## Compilation Process

1. **First Request:** `front-page.blade.php` → PHP compilation → Cache storage → Execute → Render
2. **Subsequent Requests:** Read cached PHP → Execute → Render (no compilation)
3. **Template Change:** Detect modification → Recompile → Update cache → Execute

**Cache Location:** `wp-content/uploads/cache/` (configurable in `config/view.php`)

**Compiled Example:**

**Original Blade:**
```blade
<h1>{{ $title }}</h1>
@if($showDate)
  <time>{{ $date }}</time>
@endif
```

**Compiled PHP:**
```php
<h1><?php echo e($title); ?></h1>
<?php if($showDate): ?>
  <time><?php echo e($date); ?></time>
<?php endif; ?>
```

**Performance:**
- First render: +50-100ms (compilation overhead)
- Cached renders: 0ms overhead (identical to hand-written PHP)
- Memory: Minimal (compiled PHP stored on disk)

## Cache Clearing

**Automatic:** Template file modification timestamp triggers recompilation
**Manual:** Delete `wp-content/uploads/cache/` contents
**Programmatic:**
```php
// Clear Blade cache
app('view')->flush();
```

## Comparison: Blade vs Traditional PHP

| Feature | Blade | Traditional PHP |
|---------|-------|-----------------|
| Template Inheritance | `@extends`, `@section`, `@yield` | None (duplicate header/footer) |
| Auto-Escaping | `{{ }}` escapes automatically | Manual `esc_html()`, `esc_attr()` |
| Syntax | Clean (`@if`, `@foreach`) | Verbose (`<?php if(): ?>`) |
| Partials | `@include('partial')` | `get_template_part('partial')` |
| Components | Reusable with data passing | Limited reusability |
| Conditionals | `@if`, `@unless`, `@isset` | `<?php if(): ?>`, `<?php endif; ?>` |
| Loops | `@foreach`, `@while`, `$loop` | `<?php foreach(): ?>`, manual index |
| Performance | Compiled + cached (0ms overhead) | Direct execution |
| Learning Curve | 2-5 days (Laravel syntax) | 0 days (standard PHP) |
| Setup Time | +4 hours (Composer, webpack) | 0 hours |
| File Extension | `.blade.php` | `.php` |

**Analyzed Adoption:** 29% of themes use Blade (348 total files), 71% use traditional PHP templates.

## When to Use Blade vs Traditional PHP

**Use Blade When:**
- Content-heavy site with template reuse (50+ templates)
- Need template inheritance (shared layouts)
- Team familiar with Laravel/Blade syntax
- Want automatic XSS protection via `{{ }}`
- Building component library with partials
- Using Sage framework (includes Blade)

**Use Traditional PHP When:**
- Simple blog or marketing site (10-20 templates)
- Team unfamiliar with Blade/Laravel
- Client needs to edit templates directly (no compilation)
- Plugin compatibility issues
- No Composer/build tools in workflow

**Analyzed Distribution:** 29% Blade (4 themes with 348 files), 71% traditional PHP.

## Related Patterns

- **Sage Framework:** See `sage-framework-structure.md` for full Sage setup
- **MVC Controllers:** See `mvc-controllers-pattern.md` for data layer
- **Traditional Templates:** See `traditional-theme-organization.md` for PHP alternative
- **Template Hierarchy:** See `template-hierarchy-usage.md` for WordPress resolution

## Common Pitfalls

**1. Mixing escaped and unescaped:**
```blade
<!-- Wrong - WordPress hook needs {!! !!} -->
{{ wp_nav_menu(['echo' => false]) }}

<!-- Correct -->
{!! wp_nav_menu(['echo' => false]) !!}
```

**2. Forgetting @php() for hooks:**
```blade
<!-- Wrong - wp_head() outputs directly -->
{!! wp_head() !!}

<!-- Correct - no return value to escape -->
@php(wp_head())
```

**3. Using <?php ?> tags:**
```blade
<!-- Wrong - not Blade syntax -->
<?php if (have_posts()): ?>

<!-- Correct - Blade directive -->
@if(have_posts())
```

**4. Not compiling templates:**
Blade files don't work without Sage framework (no compilation).
**Fix:** Use Sage, or stick with traditional `.php` templates.

**5. Confusing variable scope:**
```blade
<!-- $post available in parent, not in partial -->
@include('partials.post-card')

<!-- Pass $post explicitly -->
@include('partials.post-card', ['post' => $post])
```

## References

- **Laravel Blade Docs:** https://laravel.com/docs/8.x/blade
- **Sage Blade Integration:** https://roots.io/sage/docs/blade-templates/
- **WordPress Template Hierarchy:** https://developer.wordpress.org/themes/basics/template-hierarchy/
