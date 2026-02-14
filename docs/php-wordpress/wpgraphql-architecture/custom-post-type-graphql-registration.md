---
title: "Custom Post Type GraphQL Registration Pattern"
category: "wpgraphql-architecture"
subcategory: "type-registration"
tags: ["graphql", "custom-post-types", "wordpress", "wpgraphql", "schema"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WordPress custom post types expose to WPGraphQL through explicit `show_in_graphql` configuration with singular and plural GraphQL names. Airbnb's production pattern implements opt-in GraphQL exposure via abstract base classes with protected properties `$show_in_graphql`, `$graphql_single_name`, and `$graphql_plural_name`, enabling child post type classes to register custom GraphQL fields through the `graphql_register_types` hook.

**Pattern Source:** Airbnb WordPress VIP Go (`rkv-utilities/inc/classes/Post_Type/Base.php`)
**Usage Count:** 124 `show_in_graphql` instances, 42 `graphql_single_name` instances
**Architecture:** Abstract base class with template method pattern

## Base Class Structure

WordPress custom post type classes implement GraphQL support through protected properties. Airbnb's `Base` abstract class defines `$show_in_graphql` (boolean), `$graphql_single_name`, `$graphql_plural_name` (strings), with `show_in_graphql` defaulting to false for opt-in security.

```php
<?php
namespace RKV\Utilities\Post_Type;

abstract class Base {
    protected $post_type_name; // e.g., 'project'
    protected $show_in_graphql = false; // Default: opt-in
    protected $graphql_single_name = ''; // e.g., 'Project' for project(id: "123")
    protected $graphql_plural_name = ''; // e.g., 'Projects' for projects(first: 10)
    protected $post_type_args = [];
}
```

**Why:** Explicit opt-in prevents accidental GraphQL exposure. Child classes override properties in `initialize_post_type()`. Base class validates before registration.

## Hook Registration Pattern

WordPress custom post types register GraphQL fields through `graphql_register_types` action. Airbnb's base class hooks `register_graphql_fields()` in constructor, allowing child classes to override empty method stub.

```php
<?php
public function __construct() {
    if (empty($this->post_type_name)) return;
    if (!$this->do_post_type()) return;

    $this->initialize_post_type();
    $this->create_post_type();

    add_action("fm_post_{$this->post_type_name}", [$this, 'add_custom_fields']);
    add_action('rest_api_init', [$this, 'register_rest_fields']);
    add_action('graphql_register_types', [$this, 'register_graphql_fields']); // Priority 10
    add_filter('post_type_link', [$this, 'remove_slug'], 10, 2);
}

public function register_graphql_fields() {} // Empty stub - child override optional
```

**Why Empty Stub:** Not all post types need custom GraphQL fields. ACF fields auto-register via wpgraphql-acf. No performance penalty for unused hooks.

## Default Args Pattern

WordPress custom post types merge GraphQL configuration into registration args when opt-in properties set. Airbnb's pattern conditionally adds GraphQL args only when all three properties are non-empty.

```php
<?php
protected function get_default_post_type_args() {
    $default_args = [
        'hierarchical' => false, 'public' => true, 'show_ui' => true,
        'show_in_rest' => true, // Required for Gutenberg
        'exclude_from_search' => true,
    ];

    // Conditional GraphQL config (all 3 required)
    if ($this->show_in_graphql && !empty($this->graphql_single_name) && !empty($this->graphql_plural_name)) {
        $default_args['show_in_graphql'] = true;
        $default_args['graphql_single_name'] = $this->graphql_single_name;
        $default_args['graphql_plural_name'] = $this->graphql_plural_name;
    }
    return $default_args;
}

protected function create_post_type() {
    $this->post_type_args = wp_parse_args($this->post_type_args, $this->get_default_post_type_args());
    if (!empty($this->post_type_args)) {
        register_post_type($this->post_type_name, $this->post_type_args);
    }
}
```

**Validation:** All three GraphQL properties must be set. Empty string prevents partial config. Fails silently if conditions not met. WPGraphQL requires both singular/plural names - missing names cause schema errors.

## Child Class Implementation: Basic Setup

WordPress custom post type classes extend abstract base and configure GraphQL exposure through property initialization. Airbnb's pattern implements `initialize_post_type()` to set GraphQL properties before registration.

```php
<?php
namespace Your_Theme\Post_Types;
use RKV\Utilities\Post_Type\Base;

class Project extends Base {
    protected function initialize_post_type() {
        $this->post_type_name = 'project';
        $this->show_in_graphql = true;
        $this->graphql_single_name = 'Project';  // Query: project(id: "123")
        $this->graphql_plural_name = 'Projects'; // Query: projects(first: 10)
        $this->post_type_args = [
            'labels' => ['name' => __('Projects', 'your-theme'), 'singular_name' => __('Project', 'your-theme')],
            'menu_icon' => 'dashicons-portfolio',
            'supports' => ['title', 'editor', 'thumbnail', 'excerpt'],
            'has_archive' => true,
            'rewrite' => ['slug' => 'projects'],
        ];
    }
}
```

## Child Class Implementation: Custom GraphQL Fields

WordPress post type classes override `register_graphql_fields()` to add custom fields and connections beyond ACF auto-registration.

```php
<?php
public function register_graphql_fields() {
    register_graphql_field('Project', 'projectUrl', [
        'type' => 'String', 'description' => 'Absolute URL',
        'resolve' => function($post) { return get_permalink($post->ID); },
    ]);

    register_graphql_connection([
        'fromType' => 'Project', 'toType' => 'User', 'fromFieldName' => 'contributors',
        'resolve' => function($source, $args, $context, $info) {
            $user_ids = get_post_meta($source->ID, 'contributors', true);
            return $context->get_loader('user')->load_many($user_ids);
        },
    ]);
}
```

**GraphQL Schema Result:**
```graphql
type Project {
  id: ID!
  title: String
  projectUrl: String # Custom field
  contributors: [User] # Custom connection
  projectDetails: Project_Projectdetails # ACF auto-registered
}

type RootQuery {
  project(id: ID!): Project
  projects(first: Int, where: RootQueryToProjectConnectionWhereArgs): RootQueryToProjectConnection
}
```

## Registration Activation: Theme Integration

WordPress custom post type GraphQL registrations activate through instantiation during init hook. Airbnb's pattern instantiates classes in `functions.php`.

```php
<?php
// functions.php
namespace Your_Theme;

spl_autoload_register(function($class) {
    if (strpos($class, __NAMESPACE__ . '\\Post_Types\\') === 0) {
        $file = str_replace(['\\', __NAMESPACE__ . '/Post_Types/'], ['/', ''], $class);
        require_once __DIR__ . '/inc/post-types/' . $file . '.php';
    }
});

add_action('init', function() {
    new Post_Types\Project();
    new Post_Types\Event();
    new Post_Types\Resource();
}, 10);
```

**Why init Hook:** WPGraphQL loads on `plugins_loaded` (priority 10), post types register on `init`, `graphql_register_types` fires after `init`.

## Registration Activation: Plugin Integration

WordPress plugins check dependencies before registering, ensuring WPGraphQL availability.

```php
<?php
/**
 * Plugin Name: Custom Post Types
 * Requires Plugins: wp-graphql, advanced-custom-fields-pro
 */
namespace Your_Plugin;

add_action('plugins_loaded', function() {
    if (!class_exists('WPGraphQL')) {
        add_action('admin_notices', function() {
            echo '<div class="notice notice-error"><p>Requires WPGraphQL plugin.</p></div>';
        });
        return;
    }

    add_action('init', function() {
        new Post_Types\Project();
        new Post_Types\Event();
    }, 10);
}, 20); // Priority 20: After WPGraphQL
```

## Naming Conventions: Case Rules

WordPress GraphQL post type names follow PascalCase singular/plural conventions. Airbnb's pattern uses `$graphql_single_name` for node queries, `$graphql_plural_name` for list queries.

**GraphQL Schema:** PascalCase singular/plural (`Project`/`Projects`, `TeamMember`/`TeamMembers`, `SEOMetadata`)
**WordPress Database:** Lowercase, underscores, max 20 chars (`project`, `team_member`, `press_release`)
**URL Slugs:** Lowercase, hyphens (`/projects/`, `/team-members/`)

## Naming Conventions: Implementation Examples

WordPress post type naming maps database names to GraphQL schema names with case transformations.

```php
<?php
// Simple: project → Project
$this->post_type_name = 'project'; $this->graphql_single_name = 'Project'; $this->graphql_plural_name = 'Projects';
$this->post_type_args['rewrite'] = ['slug' => 'projects'];

// Multi-word: team_member → TeamMember
$this->post_type_name = 'team_member'; $this->graphql_single_name = 'TeamMember'; $this->graphql_plural_name = 'TeamMembers';
$this->post_type_args['rewrite'] = ['slug' => 'team'];

// Acronym: faq → FAQ
$this->post_type_name = 'faq'; $this->graphql_single_name = 'FAQ'; $this->graphql_plural_name = 'FAQs';

// Irregular plural: person → People (NOT Persons)
$this->post_type_name = 'person'; $this->graphql_single_name = 'Person'; $this->graphql_plural_name = 'People';
```

**Generated Queries:**
```graphql
query { project(id: "cG9zdDoxMjM=") { title } }
query { projects(first: 10) { edges { node { title } } } }
```

## Opt-In Security Pattern

WordPress GraphQL post type exposure requires explicit opt-in to prevent accidental schema pollution. Airbnb's production base class defaults `$show_in_graphql` to false, requiring child classes to explicitly set true in `initialize_post_type()`, protecting private post types from GraphQL access while allowing granular control per post type.

**Default Hidden (Secure by Default):**
- Private/development/legacy post types never exposed to GraphQL
- Accidental registration prevented through explicit opt-in requirement
- Child classes must set `$show_in_graphql = true`
- Both GraphQL names required (missing names prevent registration)

**Security Benefits:**
- Private post types (drafts, internal content) remain hidden
- Development post types (test data, staging) excluded from schema
- Intentional decision documented in code through explicit configuration

## Opt-In Filter Pattern

WordPress custom post types control GraphQL exposure through `do_post_type()` filter method. Airbnb's base class checks `$opt_in` property and applies filters enabling child themes to enable/disable post types without code changes.

```php
<?php
protected function do_post_type() {
    if ($this->opt_in) {
        return apply_filters("rkv_optin_post_type_{$this->post_type_name}", false); // Default: disabled
    }
    return !apply_filters("rkv_optout_post_type_{$this->post_type_name}", false); // Default: enabled
}
```

**Child Theme Control:**
```php
<?php
add_filter('rkv_optin_post_type_project', '__return_true'); // Enable post type
add_filter('rkv_optout_post_type_event', '__return_true'); // Disable post type
```

**GraphQL Schema Impact:**

Without opt-in, no GraphQL queries available. With opt-in enabled, WPGraphQL generates `project(id: ID!)`, `projectBy(projectId: Int!)`, and `projects(first: Int, after: String)` queries automatically.

## Production Checklist

WordPress GraphQL custom post type implementations require systematic property configuration and testing to match Airbnb's production pattern.

**Pre-Registration:**
- [ ] Base class extends `RKV\Utilities\Post_Type\Base` with `initialize_post_type()` implemented
- [ ] `$post_type_name` set (lowercase, underscores, ≤20 chars)
- [ ] GraphQL properties configured: `$show_in_graphql = true`, `$graphql_single_name` (PascalCase), `$graphql_plural_name` (PascalCase)
- [ ] ACF field groups configured (if using wpgraphql-acf)
- [ ] WPGraphQL plugin dependency verified

**Testing:**
- [ ] GraphQL schema includes post type (GraphiQL introspection)
- [ ] Node queries work: `project(id: "...")`, `projects(first: 10)`
- [ ] ACF fields and custom fields appear in schema
- [ ] Pagination works (pageInfo, hasNextPage, endCursor)
- [ ] Filtering works (where args with status, orderby)
- [ ] Private posts not exposed, N+1 query prevention enabled

**GraphiQL Test Query:**
```graphql
query TestProject {
  project(id: "cG9zdDoxMjM=") { id title }
  projects(first: 5, where: {status: PUBLISH}) {
    edges { node { title } cursor }
    pageInfo { hasNextPage endCursor }
  }
}
```

## References

**Airbnb Implementation:**
- File: `plugins/rkv-utilities/inc/classes/Post_Type/Base.php`
- Lines: 42-60 (property declarations), 85-111 (constructor hooks), 218-256 (default args)
- Usage: 124 `show_in_graphql` instances, 42 `graphql_single_name` instances

**WordPress Documentation:**
- `register_post_type()`: https://developer.wordpress.org/reference/functions/register_post_type/
- Post type args: https://developer.wordpress.org/reference/functions/register_post_type/#parameters

**WPGraphQL Documentation:**
- Post type config: https://www.wpgraphql.com/docs/custom-post-types/
- Schema customization: https://www.wpgraphql.com/docs/wpgraphql-schema/

**Related Plugins:**
- WPGraphQL for ACF: https://github.com/wp-graphql/wpgraphql-acf
- WPGraphQL Smart Cache: https://github.com/wp-graphql/wpgraphql-smart-cache

**Pattern Benefits:**
- Opt-in security prevents accidental exposure
- Consistent naming across 42+ post type implementations
- Abstract base class enforces standards
- Template method pattern enables extensibility
