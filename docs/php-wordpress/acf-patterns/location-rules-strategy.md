---
title: "ACF Location Rules Strategy: Blocks vs Templates"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "location-rules", "blocks", "templates", "architecture", "field-groups"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF location rules determine where field groups appear in the WordPress admin. Architecture choice (headless blocks vs traditional templates) dictates location rule strategy, impacting content editor experience and API structure.

WordPress projects analyzed show 100% architecture-driven location rule patterns: headless implementations use block-based rules (44% of rules), traditional implementations use template-based rules (75% of rules).

## Block-Based Location Rules (Headless)

Modern headless WordPress implementations attach ACF fields to Gutenberg blocks for structured content editing and GraphQL exposure.

### Block Location Rule Pattern

```json
{
  "key": "group_680ad6fe615b8",
  "title": "Logo Cloud Block",
  "fields": [
    {
      "name": "logos",
      "type": "repeater"
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
  ]
}
```

**Key Properties:**
- `param: "block"`: Target Gutenberg block type
- `operator: "=="`: Exact match required
- `value`: Full block name from block.json (includes namespace)

**Block Name Format:** `{namespace}/{block-slug}` (e.g., `create-block/logo-cloud-block`, `acf/testimonial-block`)

### Real-World Block Examples (airbnb)

```
Block-based location rules (15 ACF blocks):
- create-block/all-posts-teaser-grid-block
- create-block/city-portal-block
- create-block/external-news-block
- create-block/faq-block
- create-block/featured-post-block
- create-block/home-page-hero-block
- create-block/logo-cloud-block
- create-block/municipalities-search-block
- create-block/people-grid-block
- create-block/policy-toolkit-block
- create-block/post-teaser-grid-block
- create-block/priorities-block
- create-block/public-policy-priorities-block
- create-block/stat-block
- create-block/text-image-block
```

**Pattern:** One field group per block (granular organization).

## Template-Based Location Rules (Traditional)

Traditional WordPress themes attach ACF fields to page templates for template-specific content editing.

### Template Location Rule Pattern

```json
{
  "key": "group_5f91b18180b23",
  "title": "Text and Aside",
  "fields": [
    {
      "name": "ta_title",
      "type": "text"
    }
  ],
  "location": [
    [
      {
        "param": "post_template",
        "operator": "==",
        "value": "views/template-about.blade.php"
      }
    ]
  ]
}
```

**Key Properties:**
- `param: "post_template"` or `"page_template"`: Target template files
- `value`: Template filename with path (relative to theme root)

**Template Path Formats:**
- Sage/Blade: `views/template-about.blade.php`
- Standard PHP: `template-about.php`
- Subfolder: `templates/template-about.php`

### Real-World Template Examples (thekelsey)

```
Template-based location rules (30+ templates):
- views/template-about.blade.php
- views/template-partnership.blade.php
- views/template-donate.blade.php
- views/template-get-involved.blade.php
- views/template-advocacy.blade.php
- views/template-events.blade.php
- views/template-faqs.blade.php
- views/front-page.blade.php
- views/template-form.blade.php
- views/template-stories.blade.php
- views/template-projects.blade.php
- views/template-learn-center.blade.php
```

**Pattern:** Fields grouped by template context (one field group per template or logical section).

## Post Type Location Rules

Attach fields to all posts of a specific custom post type.

### Post Type Rule Pattern

```json
{
  "location": [
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "bnb_policy"
      }
    ]
  ]
}
```

**Use Cases:**
- Custom post type metadata (e.g., `bnb_policy`, `bnb_municipality`)
- Universal fields for all posts of a type (e.g., SEO fields, featured image override)

### Post Type Examples

```
Common post types:
- bnb_policy (Airbnb policy documents)
- bnb_municipality (Municipality data)
- bnb_leadership (Team members)
- bnb_launch (Product launches)
- kelsey_event (Events calendar)
- kelsey_resource (Downloadable resources)
```

## Options Page Location Rules

Attach fields to ACF options pages for site-wide settings.

### Options Page Rule Pattern

```json
{
  "location": [
    [
      {
        "param": "options_page",
        "operator": "==",
        "value": "acf-options-social-media"
      }
    ]
  ]
}
```

**Value Format:** `acf-options-{menu_slug}`

**Common Options Pages:**
- `acf-options-social-media`: Social media links
- `acf-options-global-modules`: Reusable content blocks
- `acf-options-theme-settings`: Theme-wide configuration
- `acf-options-footer`: Footer settings

## Taxonomy Location Rules

Attach fields to taxonomy term edit screens.

### Taxonomy Rule Pattern

```json
{
  "location": [
    [
      {
        "param": "taxonomy",
        "operator": "==",
        "value": "category"
      }
    ]
  ]
}
```

**Use Cases:**
- Category/tag meta (e.g., category icon, featured image)
- Custom taxonomy metadata

**Taxonomy Examples:**
- `category`: Standard WordPress categories
- `post_tag`: Standard WordPress tags
- `bnb_policy_category`: Custom policy taxonomy

## Compound Location Rules (AND Logic)

Combine multiple conditions using AND logic (all conditions must match).

### Compound Rule Pattern

```json
{
  "location": [
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "page"
      },
      {
        "param": "page_template",
        "operator": "==",
        "value": "template-landing.php"
      }
    ]
  ]
}
```

**Logic:** Fields appear only on pages using `template-landing.php`.

**Use Cases:**
- Template-specific fields within a post type
- User role + post type combinations
- Page parent + template combinations

## Multiple Location Rules (OR Logic)

Create alternative location rule sets using OR logic (any set can match).

### OR Logic Pattern

```json
{
  "location": [
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "page"
      }
    ],
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "post"
      }
    ]
  ]
}
```

**Logic:** Fields appear on pages OR posts.

**Use Cases:**
- Reusable field groups across multiple post types
- Fields on multiple templates
- Multiple options pages sharing fields

## Page Type Location Rules

Target specific page types (front page, posts page, 404 page).

### Page Type Rule Pattern

```json
{
  "location": [
    [
      {
        "param": "page_type",
        "operator": "==",
        "value": "front_page"
      }
    ]
  ]
}
```

**Page Type Values:**
- `front_page`: Homepage (Settings → Reading)
- `posts_page`: Blog page (Settings → Reading)
- `top_level`: Top-level pages (no parent)
- `parent`: Pages with children
- `child`: Pages with a parent

## Architecture Comparison

### Headless (Block-Centric)

**Location Rule Distribution (airbnb):**
```
block:          15 (44%)  ← Dominant pattern
options_page:    8 (24%)
post_type:       6 (18%)
page_template:   3 (9%)
taxonomy:        1 (3%)
page_type:       1 (3%)
```

**Characteristics:**
- 44% of rules attach to Gutenberg blocks
- One field group per block (granular)
- GraphQL-friendly (structured content)
- Editor experience: Insert blocks, configure via sidebar

**When to Use:**
- Headless WordPress (Next.js, Nuxt.js)
- Structured content modeling
- API-first architecture
- Reusable content components

### Traditional (Template-Centric)

**Location Rule Distribution (thekelsey):**
```
post_template:  20 (50%)  ← Dominant pattern
page_template:  10 (25%)
post_type:       5 (13%)
options_page:    4 (10%)
page:            1 (3%)
```

**Characteristics:**
- 75% of rules attach to page/post templates
- Fields grouped by template context
- PHP template integration (`get_field()` in templates)
- Editor experience: Select template, edit fields below content

**When to Use:**
- Traditional WordPress themes
- Template-driven architecture
- Sage/Blade frameworks
- Monolithic WordPress sites

## Conditional Display within Location Rules

Location rules support AND/NOT logic via operator changes.

### Negative Match Pattern

```json
{
  "location": [
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "page"
      },
      {
        "param": "page_template",
        "operator": "!=",
        "value": "default"
      }
    ]
  ]
}
```

**Logic:** Show on pages NOT using the default template.

**Operators:**
- `==`: Equals (positive match)
- `!=`: Not equals (negative match)

## Location Rule Priority

When multiple field groups match the same location, display order is controlled.

### Menu Order Property

```json
{
  "key": "group_primary",
  "title": "Primary Settings",
  "menu_order": 0,
  "location": [
    [
      {
        "param": "post_type",
        "operator": "==",
        "value": "page"
      }
    ]
  ]
}
```

**Order Values:**
- `0`: Displays first (highest priority)
- `10`: Displays second
- `20`: Displays third
- `100`: Displays last (lowest priority)

**Use Case:** Show SEO fields at top (`menu_order: 0`), advanced settings at bottom (`menu_order: 100`).

## Best Practices

### Granular Field Groups (Blocks)

```
✅ Good: One field group per block
- group_logo_cloud → create-block/logo-cloud-block
- group_faq → create-block/faq-block
- group_stat → create-block/stat-block

❌ Bad: One field group for all blocks
- group_all_blocks → create-block/* (overly broad)
```

**Benefits:**
- Easier maintenance (changes isolated to single block)
- Better GraphQL types (one type per block)
- Clearer admin experience

### Reusable Field Groups (Templates)

```
✅ Good: Shared field group across related templates
- group_hero → template-landing.php, template-about.php

❌ Bad: Duplicate field groups per template
- group_landing_hero → template-landing.php
- group_about_hero → template-about.php (same fields)
```

**Pattern:** Use OR logic for reusable field groups.

### Descriptive Titles

```
✅ Good: "Logo Cloud Block Fields"
✅ Good: "About Page - Text and Aside Section"

❌ Bad: "Group 1"
❌ Bad: "Fields"
```

**Rationale:** Field group title appears in admin, helps editors understand field purpose.

## Common Pitfalls

**Block Name Mismatch:**
```json
// Bad: Missing namespace
"value": "logo-cloud-block"

// Good: Full block name from block.json
"value": "create-block/logo-cloud-block"
```

**Template Path Mismatch:**
```json
// Bad: Wrong path (missing "views/")
"value": "template-about.blade.php"

// Good: Full path relative to theme root
"value": "views/template-about.blade.php"
```

**Options Page Value Format:**
```json
// Bad: Missing "acf-options-" prefix
"value": "social-media"

// Good: Full options page identifier
"value": "acf-options-social-media"
```

**Overly Broad Rules:**
```json
// Bad: Matches ALL posts (too broad)
{
  "param": "post_type",
  "operator": "==",
  "value": "post"
}

// Good: Specific template or category
{
  "param": "post_type",
  "operator": "==",
  "value": "post"
},
{
  "param": "post_category",
  "operator": "==",
  "value": "featured"
}
```

## Migration: Templates → Blocks

Converting template-based fields to block-based fields for headless migration.

### Before (Template-Based)

```json
{
  "title": "Hero Section Fields",
  "location": [
    [
      {
        "param": "page_template",
        "operator": "==",
        "value": "template-landing.php"
      }
    ]
  ]
}
```

### After (Block-Based)

```json
{
  "title": "Hero Block Fields",
  "location": [
    [
      {
        "param": "block",
        "operator": "==",
        "value": "create-block/hero-block"
      }
    ]
  ]
}
```

**Migration Steps:**
1. Create ACF block with `block.json`
2. Duplicate template field group
3. Change location rule to block
4. Update field names for GraphQL (camelCase)
5. Add `show_in_graphql: 1` to all fields
6. Test GraphQL query
7. Migrate template content to blocks

## Related Patterns

- **ACF Blocks:** Block-based location rules require ACF block registration
- **ACF JSON Storage:** Location rules stored in JSON field group definitions
- **WPGraphQL Integration:** Block-based rules create cleaner GraphQL types
- **Options Pages:** Options page rules require `acf_add_options_page()` registration

**Source Projects:** airbnb (44% block rules, 24% options page rules, modern headless), thekelsey (75% template rules, traditional architecture)
