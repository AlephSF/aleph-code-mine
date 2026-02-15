---
title: "WordPress Template Hierarchy in Blade vs PHP Themes"
category: "theme-structure"
subcategory: "template-resolution"
tags: ["template-hierarchy", "blade", "php", "routing", "template-files"]
stack: "php-wp"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# WordPress Template Hierarchy in Blade vs PHP Themes

## Overview

WordPress template hierarchy determines which template file renders based on request type (post, page, archive, etc.). **100% of themes** follow WordPress template hierarchy, whether using Blade (`.blade.php`) or traditional PHP (`.php`) templates.

Template hierarchy checks files in specific order: most-specific → least-specific → `index.php/index.blade.php` fallback. Blade themes follow **identical hierarchy** as PHP themes, only file extension differs.


## Homepage

```
Hierarchy (in order checked):
1. front-page.php / front-page.blade.php
2. home.php / home.blade.php
3. index.php / index.blade.php
```

**Condition:**
- `front-page.php`: Static homepage OR blog homepage (if set in Settings → Reading)
- `home.php`: Blog posts index
- `index.php`: Ultimate fallback

## Single Post

```
Hierarchy (in order checked):
1. single-{post_type}-{slug}.php
2. single-{post_type}.php
3. single.php / single.blade.php
4. singular.php / singular.blade.php
5. index.php / index.blade.php
```

**Examples:**
- Post slug "hello-world": `single-post-hello-world.php` → `single-post.php` → `single.php`
- Custom post type "career": `single-career.php` → `single.php`

## Page

```
Hierarchy (in order checked):
1. Custom page template (Template Name: Full Width)
2. page-{slug}.php
3. page-{id}.php
4. page.php / page.blade.php
5. singular.php / singular.blade.php
6. index.php / index.blade.php
```

**Examples:**
- Page slug "about": `page-about.php` → `page.php`
- Page ID 42: `page-42.php` → `page.php`
- Full Width template: `template-fullwidth.php` (selected in Page Attributes)

## Category Archive

```
Hierarchy (in order checked):
1. category-{slug}.php
2. category-{id}.php
3. category.php / category.blade.php
4. archive.php / archive.blade.php
5. index.php / index.blade.php
```

**Examples:**
- Category slug "news": `category-news.php` → `category.php` → `archive.php`
- Category ID 6: `category-6.php` → `category.php`

## Tag Archive

```
Hierarchy (in order checked):
1. tag-{slug}.php
2. tag-{id}.php
3. tag.php / tag.blade.php
4. archive.php / archive.blade.php
5. index.php / index.blade.php
```

## Custom Taxonomy Archive

```
Hierarchy (in order checked):
1. taxonomy-{taxonomy}-{term}.php
2. taxonomy-{taxonomy}.php
3. taxonomy.php / taxonomy.blade.php
4. archive.php / archive.blade.php
5. index.php / index.blade.php
```

**Example (genre taxonomy, term "action"):**
`taxonomy-genre-action.php` → `taxonomy-genre.php` → `taxonomy.php` → `archive.php`

## Custom Post Type Archive

```
Hierarchy (in order checked):
1. archive-{post_type}.php
2. archive.php / archive.blade.php
3. index.php / index.blade.php
```

**Example (careers CPT):**
`archive-career.php` → `archive.php`

## Author Archive

```
Hierarchy (in order checked):
1. author-{nicename}.php
2. author-{id}.php
3. author.php / author.blade.php
4. archive.php / archive.blade.php
5. index.php / index.blade.php
```

## Date Archive

```
Hierarchy (in order checked):
1. date.php / date.blade.php
2. archive.php / archive.blade.php
3. index.php / index.blade.php
```

## Search Results

```
Hierarchy (in order checked):
1. search.php / search.blade.php
2. index.php / index.blade.php
```

## 404 Error

```
Hierarchy (in order checked):
1. 404.php / 404.blade.php
2. index.php / index.blade.php
```

## Attachment (Media)

```
Hierarchy (in order checked):
1. {MIME_type}.php (image.php, video.php, application.php)
2. attachment.php / attachment.blade.php
3. single.php / single.blade.php
4. singular.php / singular.blade.php
5. index.php / index.blade.php
```


## Traditional PHP Template

```php
<!-- single.php -->
<?php get_header(); ?>

<div class="container">
    <?php while (have_posts()) : the_post(); ?>

        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <h1><?php the_title(); ?></h1>
            <div class="content">
                <?php the_content(); ?>
            </div>
        </article>

    <?php endwhile; ?>
</div>

<?php get_footer(); ?>
```

## Blade Template (Equivalent)

```blade
{{-- single.blade.php --}}
@extends('layouts.app')

@section('content')
  @while(have_posts()) @php(the_post())

    <article id="post-{{ get_the_ID() }}" @php(post_class())>
      <h1>{{ get_the_title() }}</h1>
      <div class="content">
        {!! get_the_content() !!}
      </div>
    </article>

  @endwhile
@endsection
```

**Differences:**
- Blade extends base layout (`@extends`)
- Blade uses `{{ }}` for escaped output
- Blade uses `{!! !!}` for unescaped HTML
- Blade uses `@while` instead of `<?php while(): ?>`
- Blade uses `@php()` for WordPress hooks

**Hierarchy Resolution:** Identical. WordPress looks for `single.blade.php` same as `single.php`.

## Custom Page Templates

Both Blade and PHP themes use Template Name comment to register custom page templates.

## PHP Custom Template

```php
<?php
/**
 * Template Name: Full Width
 * Template Post Type: page
 */

get_header();
?>

<div class="container-fluid">
    <div class="fullwidth-content">
        <!-- Content -->
    </div>
</div>

<?php get_footer(); ?>
```

## Blade Custom Template

```blade
{{--
  Template Name: Full Width
  Template Post Type: page
--}}

@extends('layouts.app')

@section('content')
  <div class="fullwidth-content">
    <!-- Content -->
  </div>
@endsection
```

**Registration:** WordPress detects `Template Name:` comment in both `.php` and `.blade.php` files.

## Conditional Template Loading

WordPress conditional tags determine which template loads.

## Conditional Tags

| Condition | Function | Template |
|-----------|----------|----------|
| Homepage | `is_front_page()` | `front-page.php` |
| Blog Index | `is_home()` | `home.php` |
| Single Post | `is_single()` | `single.php` |
| Page | `is_page()` | `page.php` |
| Archive | `is_archive()` | `archive.php` |
| Category | `is_category()` | `category.php` |
| Tag | `is_tag()` | `tag.php` |
| Author | `is_author()` | `author.php` |
| Date | `is_date()` | `date.php` |
| Search | `is_search()` | `search.php` |
| 404 | `is_404()` | `404.php` |

**Usage in Templates:**

```php
// PHP
<?php if (is_front_page()) : ?>
    <h1><?php bloginfo('name'); ?></h1>
<?php endif; ?>

// Blade
@if(is_front_page())
  <h1>{{ bloginfo('name') }}</h1>
@endif
```

## Template Parts

Break templates into reusable parts via `get_template_part()` (PHP) or `@include()` (Blade).

## PHP Template Parts

```php
<!-- archive.php -->
<?php while (have_posts()) : the_post(); ?>

    <?php
    // Loads content-{post_type}.php or content.php
    get_template_part('content', get_post_type());
    ?>

<?php endwhile; ?>
```

## Blade Template Parts

```blade
{{-- archive.blade.php --}}
@while(have_posts()) @php(the_post())

  @include('partials.content-' . get_post_type())

@endwhile
```

## Template Hierarchy Visualization

```
Request: Single Post (ID 123, slug "hello-world", type "post")

WordPress checks in order:
1. single-post-hello-world.php ❌ Not found
2. single-post.php ❌ Not found
3. single.php ✅ Found! Load this template
4. singular.php (skipped - single.php found)
5. index.php (skipped - single.php found)
```

```
Request: Category Archive (slug "news", ID 5)

WordPress checks in order:
1. category-news.php ❌ Not found
2. category-5.php ❌ Not found
3. category.php ❌ Not found
4. archive.php ✅ Found! Load this template
5. index.php (skipped - archive.php found)
```

## When Templates Are Resolved

**Template resolution happens:**
1. WordPress parses request URL
2. Determines query type (single, archive, page, etc.)
3. Checks template hierarchy in order
4. Loads first matching template file
5. Executes template (includes header, content, footer)
6. Outputs HTML to browser

**Blade compilation happens:**
- First request: Compile `.blade.php` to PHP, cache in `wp-content/uploads/cache/`
- Subsequent requests: Use cached PHP (zero compilation overhead)

## Common Template Files

| Template | Purpose | Fallback |
|----------|---------|----------|
| `front-page.php` | Homepage | `home.php` → `index.php` |
| `home.php` | Blog index | `index.php` |
| `single.php` | Single post | `index.php` |
| `page.php` | Static page | `singular.php` → `index.php` |
| `archive.php` | Archives (category, tag, CPT) | `index.php` |
| `search.php` | Search results | `index.php` |
| `404.php` | Not found error | `index.php` |
| `index.php` | Ultimate fallback | **Required** (always present) |

**Analyzed Coverage:**
- Traditional themes: `header.php`, `footer.php`, `single.php`, `page.php`, `archive.php`, `404.php`, `index.php` (100% have these)
- Blade themes: `layouts/app.blade.php` (base), `single.blade.php`, `page.blade.php`, `archive.blade.php`, `404.php`, `index.blade.php`

## Related Patterns

- **Blade Templating:** See `blade-templating-pattern.md` for Blade syntax
- **Traditional Themes:** See `traditional-theme-organization.md` for PHP templates
- **Sage Framework:** See `sage-framework-structure.md` for Blade setup

## References

- **WordPress Template Hierarchy:** https://developer.wordpress.org/themes/basics/template-hierarchy/
- **Conditional Tags:** https://developer.wordpress.org/themes/basics/conditional-tags/
- **get_template_part:** https://developer.wordpress.org/reference/functions/get_template_part/
