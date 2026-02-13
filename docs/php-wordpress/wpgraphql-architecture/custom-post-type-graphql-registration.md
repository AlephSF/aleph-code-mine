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

WordPress custom post type classes implement GraphQL support through protected properties that control GraphQL exposure. Airbnb's production `Base` abstract class defines `$show_in_graphql` (boolean), `$graphql_single_name` (string), and `$graphql_plural_name` (string) properties, with `show_in_graphql` defaulting to false for opt-in security.

### Property Declarations

```php
<?php
namespace RKV\Utilities\Post_Type;

abstract class Base {
    /**
     * Post type name (e.g., 'project', 'event', 'resource').
     *
     * @var string
     */
    protected $post_type_name;

    /**
     * Show in GraphQL schema.
     * Default: false (opt-in)
     *
     * @var bool
     */
    protected $show_in_graphql = false;

    /**
     * GraphQL single name (e.g., 'Project', 'Event', 'Resource').
     * Used for queries like: project(id: "123")
     *
     * @var string
     */
    protected $graphql_single_name = '';

    /**
     * GraphQL plural name (e.g., 'Projects', 'Events', 'Resources').
     * Used for queries like: projects(first: 10)
     *
     * @var string
     */
    protected $graphql_plural_name = '';

    /**
     * Post type registration args (merged with defaults).
     *
     * @var array
     */
    protected $post_type_args = [];
}
```

**Why This Pattern:**
- Explicit opt-in prevents accidental GraphQL exposure
- Consistent naming enforces GraphQL conventions
- Child classes override properties in `initialize_post_type()`
- Base class validates required properties before registration

## Hook Registration Pattern

WordPress custom post types register GraphQL fields through the `graphql_register_types` action hook. Airbnb's production base class hooks `register_graphql_fields()` method in constructor at priority 10, allowing child classes to override the empty method stub and add custom field definitions when GraphQL is enabled.

### Constructor Hook Setup

```php
<?php
public function __construct() {
    // Validate post type name exists
    if ( empty( $this->post_type_name ) ) {
        return;
    }

    // Check opt-in/opt-out filters
    if ( ! $this->do_post_type() ) {
        return;
    }

    // Initialize child class properties
    $this->initialize_post_type();

    // Register WordPress post type
    $this->create_post_type();

    // Hook: Register custom fields (Fieldmanager)
    add_action( "fm_post_{$this->post_type_name}", [ $this, 'add_custom_fields' ] );

    // Hook: Register REST API fields
    add_action( 'rest_api_init', [ $this, 'register_rest_fields' ] );

    // Hook: Register GraphQL fields
    add_action( 'graphql_register_types', [ $this, 'register_graphql_fields' ] );

    // Hook: Permalink customization (optional)
    add_filter( 'post_type_link', [ $this, 'remove_slug' ], 10, 2 );
    add_action( 'pre_get_posts', [ $this, 'add_post_names_to_main_query' ] );
}

/**
 * Template method: Child classes override to register GraphQL fields.
 * Empty by default (no-op if not overridden).
 */
public function register_graphql_fields() {}
```

**Hook Characteristics:**
- Priority: 10 (default)
- Timing: After WPGraphQL plugin loads
- Execution: Once per request (WordPress init phase)
- Dependency: Requires WPGraphQL plugin active

**Why Empty Stub:**
- Not all post types need custom GraphQL fields
- ACF fields auto-register via wpgraphql-acf plugin
- Child classes only override if custom logic needed
- No performance penalty for unused hooks

## Default Args Pattern

WordPress custom post types merge GraphQL configuration into registration args when opt-in properties are set. Airbnb's production pattern conditionally adds `show_in_graphql`, `graphql_single_name`, and `graphql_plural_name` to default args only when all three properties are non-empty, preventing invalid GraphQL registrations and ensuring schema consistency.

### Args Merging Logic

```php
<?php
/**
 * Get default post type registration args.
 * Merges with child class $post_type_args property.
 *
 * @return array Default args with optional GraphQL config.
 */
protected function get_default_post_type_args() {
    $default_args = [
        'hierarchical'        => false,
        'public'              => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_admin_bar'   => true,
        'show_in_nav_menus'   => false,
        'can_export'          => true,
        'exclude_from_search' => true,
        'publicly_queryable'  => true,
        'capability_type'     => 'post',
        'show_in_rest'        => true, // Required for Gutenberg
    ];

    // Conditional GraphQL configuration
    if (
        $this->show_in_graphql &&
        ! empty( $this->graphql_single_name ) &&
        ! empty( $this->graphql_plural_name )
    ) {
        $default_args['show_in_graphql']     = true;
        $default_args['graphql_single_name'] = $this->graphql_single_name;
        $default_args['graphql_plural_name'] = $this->graphql_plural_name;
    }

    return $default_args;
}

/**
 * Create and register the post type.
 * Called in constructor after initialize_post_type().
 */
protected function create_post_type() {
    $default_args = $this->get_default_post_type_args();

    // Child class args override defaults (wp_parse_args merging)
    $this->post_type_args = wp_parse_args( $this->post_type_args, $default_args );

    if ( ! empty( $this->post_type_args ) ) {
        register_post_type( $this->post_type_name, $this->post_type_args );
    }
}
```

**Validation Logic:**
- All three GraphQL properties must be set
- Empty string check prevents partial configuration
- Boolean `show_in_graphql` must be true
- Fails silently if conditions not met (GraphQL simply disabled)

**Why This Matters:**
- WPGraphQL requires both singular and plural names
- Missing names cause GraphQL schema errors
- Partial configuration worse than no configuration
- Explicit validation prevents runtime errors

## Child Class Implementation

WordPress custom post type classes extend the abstract base and configure GraphQL exposure through property initialization. Airbnb's production pattern implements `initialize_post_type()` method to set `$show_in_graphql`, `$graphql_single_name`, and `$graphql_plural_name` properties before post type registration, with optional `register_graphql_fields()` override for custom field definitions.

### Example: Project Post Type

```php
<?php
namespace Your_Theme\Post_Types;

use RKV\Utilities\Post_Type\Base;

class Project extends Base {
    /**
     * Initialize post type properties.
     * Called before register_post_type() in parent constructor.
     */
    protected function initialize_post_type() {
        // Required: Post type name
        $this->post_type_name = 'project';

        // GraphQL configuration (opt-in)
        $this->show_in_graphql     = true;
        $this->graphql_single_name = 'Project';  // Query: project(id: "123")
        $this->graphql_plural_name = 'Projects'; // Query: projects(first: 10)

        // Custom registration args
        $this->post_type_args = [
            'labels' => [
                'name'          => __( 'Projects', 'your-theme' ),
                'singular_name' => __( 'Project', 'your-theme' ),
            ],
            'menu_icon'   => 'dashicons-portfolio',
            'supports'    => [ 'title', 'editor', 'thumbnail', 'excerpt' ],
            'has_archive' => true,
            'rewrite'     => [ 'slug' => 'projects' ],
        ];
    }

    /**
     * Override: Register custom GraphQL fields.
     * Optional - only needed for custom fields beyond ACF.
     */
    public function register_graphql_fields() {
        // Example: Add computed field
        register_graphql_field( 'Project', 'projectUrl', [
            'type'        => 'String',
            'description' => 'Absolute URL to project page',
            'resolve'     => function( $post ) {
                return get_permalink( $post->ID );
            },
        ] );

        // Example: Add custom connection
        register_graphql_connection( [
            'fromType'      => 'Project',
            'toType'        => 'User',
            'fromFieldName' => 'contributors',
            'resolve'       => function( $source, $args, $context, $info ) {
                // Custom query to get project contributors
                $user_ids = get_post_meta( $source->ID, 'contributors', true );
                return $context->get_loader( 'user' )->load_many( $user_ids );
            },
        ] );
    }

    /**
     * Override: Add custom fields (Fieldmanager/ACF).
     * ACF fields auto-register to GraphQL via wpgraphql-acf plugin.
     */
    public function add_custom_fields() {
        // Fieldmanager example (if using Fieldmanager instead of ACF)
        $fm = new \Fieldmanager_Group( [
            'name'     => 'project_details',
            'children' => [
                'start_date' => new \Fieldmanager_Datepicker( 'Start Date' ),
                'end_date'   => new \Fieldmanager_Datepicker( 'End Date' ),
                'client'     => new \Fieldmanager_TextField( 'Client Name' ),
            ],
        ] );
        $fm->add_meta_box( 'Project Details', 'project' );
    }
}
```

**GraphQL Schema Result:**

```graphql
type Project {
  id: ID!
  databaseId: Int!
  title: String
  content: String
  excerpt: String
  featuredImage: MediaItem
  projectUrl: String # Custom field
  contributors: [User] # Custom connection

  # ACF fields auto-registered by wpgraphql-acf:
  projectDetails: Project_Projectdetails
}

type Project_Projectdetails {
  startDate: String
  endDate: String
  client: String
}

type RootQuery {
  project(id: ID!): Project
  projects(
    first: Int
    after: String
    where: RootQueryToProjectConnectionWhereArgs
  ): RootQueryToProjectConnection
}
```

## Registration Activation

WordPress custom post type GraphQL registrations activate through instantiation during WordPress init hook. Airbnb's production pattern instantiates post type classes in theme `functions.php` or plugin initialization, with constructor handling all hook registrations including `graphql_register_types`, ensuring GraphQL fields register after WPGraphQL plugin loads.

### Theme Integration Pattern

```php
<?php
// wp-content/themes/your-theme/functions.php

namespace Your_Theme;

/**
 * Autoload post type classes.
 * Recommended: Use Composer PSR-4 autoloading.
 */
spl_autoload_register( function( $class ) {
    if ( strpos( $class, __NAMESPACE__ . '\\Post_Types\\' ) === 0 ) {
        $file = str_replace( '\\', '/', $class );
        $file = str_replace( __NAMESPACE__ . '/Post_Types/', '', $file );
        require_once __DIR__ . '/inc/post-types/' . $file . '.php';
    }
} );

/**
 * Initialize post types on WordPress init hook.
 * Priority: 10 (default) - After WPGraphQL plugin loads.
 */
add_action( 'init', function() {
    // Instantiate each post type class
    new Post_Types\Project();
    new Post_Types\Event();
    new Post_Types\Resource();
}, 10 );
```

**Why init Hook:**
- WPGraphQL plugin loads on `plugins_loaded` (priority 10)
- Post types must register on `init` hook (WordPress requirement)
- `graphql_register_types` fires after `init` (WPGraphQL timing)
- Ensures correct dependency order

### Plugin Integration Pattern

```php
<?php
/**
 * Plugin Name: Custom Post Types
 * Description: Project, Event, Resource post types with GraphQL
 * Version: 1.0.0
 * Requires Plugins: wp-graphql, advanced-custom-fields-pro
 */

namespace Your_Plugin;

/**
 * Plugin initialization on plugins_loaded.
 * Ensures dependency checks before post type registration.
 */
add_action( 'plugins_loaded', function() {
    // Dependency check: WPGraphQL
    if ( ! class_exists( 'WPGraphQL' ) ) {
        add_action( 'admin_notices', function() {
            echo '<div class="notice notice-error"><p>';
            echo 'Custom Post Types plugin requires WPGraphQL plugin.';
            echo '</p></div>';
        } );
        return;
    }

    // Dependency check: ACF Pro
    if ( ! function_exists( 'acf_add_local_field_group' ) ) {
        add_action( 'admin_notices', function() {
            echo '<div class="notice notice-warning"><p>';
            echo 'Custom Post Types: ACF Pro recommended for custom fields.';
            echo '</p></div>';
        } );
    }

    // Initialize post types
    add_action( 'init', function() {
        new Post_Types\Project();
        new Post_Types\Event();
        new Post_Types\Resource();
    }, 10 );
}, 20 ); // Priority 20: After WPGraphQL loads (priority 10)
```

## Naming Conventions

WordPress GraphQL post type names follow PascalCase singular/plural conventions for schema consistency. Airbnb's production pattern uses `$graphql_single_name` for node queries (e.g., `Project`, `Event`) and `$graphql_plural_name` for list queries (e.g., `Projects`, `Events`), matching GraphQL naming standards and ensuring compatibility with WPGraphQL relay connections.

### Case Sensitivity Rules

**GraphQL Schema (Type Names):**
- Single: PascalCase, singular form (`Project`, `TeamMember`, `PressRelease`)
- Plural: PascalCase, plural form (`Projects`, `TeamMembers`, `PressReleases`)
- Acronyms: Uppercase (`SEOMetadata`, `APIEndpoint`, `PDFDocument`)

**WordPress Database (post_type):**
- Lowercase, underscores (`project`, `team_member`, `press_release`)
- Maximum: 20 characters (WordPress limitation)
- No uppercase (WordPress restriction)

**URL Slugs (Permalinks):**
- Lowercase, hyphens (`/projects/`, `/team-members/`, `/press-releases/`)
- Configured via `rewrite` arg

### Naming Pattern Examples

```php
<?php
// Example 1: Simple post type
$this->post_type_name      = 'project';           // Database
$this->graphql_single_name = 'Project';           // GraphQL: project(id)
$this->graphql_plural_name = 'Projects';          // GraphQL: projects()
$this->post_type_args['rewrite'] = [ 'slug' => 'projects' ]; // URL: /projects/

// Example 2: Multi-word post type
$this->post_type_name      = 'team_member';       // Database: team_member
$this->graphql_single_name = 'TeamMember';        // GraphQL: teamMember(id)
$this->graphql_plural_name = 'TeamMembers';       // GraphQL: teamMembers()
$this->post_type_args['rewrite'] = [ 'slug' => 'team' ]; // URL: /team/

// Example 3: Acronym post type
$this->post_type_name      = 'faq';               // Database: faq
$this->graphql_single_name = 'FAQ';               // GraphQL: faq(id)
$this->graphql_plural_name = 'FAQs';              // GraphQL: faqs()
$this->post_type_args['rewrite'] = [ 'slug' => 'faq' ]; // URL: /faq/

// Example 4: Irregular plural
$this->post_type_name      = 'person';            // Database: person
$this->graphql_single_name = 'Person';            // GraphQL: person(id)
$this->graphql_plural_name = 'People';            // GraphQL: people() (NOT Persons)
```

**Generated GraphQL Queries:**

```graphql
# Single node query (by ID or database ID)
query GetProject {
  project(id: "cG9zdDoxMjM=") {  # Base64-encoded relay ID
    title
  }
  projectBy(projectId: 123) {     # Direct database ID
    title
  }
}

# List query (connections)
query GetProjects {
  projects(first: 10, where: { status: PUBLISH }) {
    edges {
      node {
        title
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Opt-In Security Pattern

WordPress GraphQL post type exposure requires explicit opt-in to prevent accidental schema pollution. Airbnb's production base class defaults `$show_in_graphql` to false, requiring child classes to explicitly set true in `initialize_post_type()`, protecting private post types from GraphQL access while allowing granular control per post type.

### Security Rationale

**Default Hidden (Secure by Default):**
- Private post types (drafts, internal content) never exposed
- Development post types (test data, staging content) excluded
- Legacy post types (deprecated types) hidden from schema
- Accidental registration prevented (explicit opt-in required)

**Explicit Opt-In Required:**
- Developer must set `$show_in_graphql = true`
- Developer must set both GraphQL names
- Missing names prevent registration (validation check)
- Intentional decision documented in code

### Opt-In Filter Pattern

```php
<?php
/**
 * Check opt-in status before registering post type.
 * Called in constructor before create_post_type().
 *
 * @return bool True if post type should be registered.
 */
protected function do_post_type() {
    // Opt-in pattern (default for most post types)
    if ( $this->opt_in ) {
        // Filter allows child themes to enable post type
        $opted_in = apply_filters(
            "rkv_optin_post_type_{$this->post_type_name}",
            false // Default: disabled
        );
        return $opted_in;
    }

    // Opt-out pattern (rare - for must-have post types)
    else {
        // Filter allows child themes to disable post type
        $opted_out = apply_filters(
            "rkv_optout_post_type_{$this->post_type_name}",
            false // Default: enabled
        );
        return ! $opted_out;
    }
}
```

**Child Theme Control:**

```php
<?php
// Enable Project post type in child theme
add_filter( 'rkv_optin_post_type_project', '__return_true' );

// Disable Event post type (if opt-out pattern used)
add_filter( 'rkv_optout_post_type_event', '__return_true' );
```

### GraphQL Schema Impact

**Without Opt-In (Default):**
```graphql
type RootQuery {
  # No project queries available
}
```

**With Opt-In:**
```graphql
type RootQuery {
  project(id: ID!): Project
  projectBy(projectId: Int!): Project
  projects(first: Int, after: String): RootQueryToProjectConnection
}
```

## Production Checklist

WordPress GraphQL custom post type implementations require systematic property configuration and testing. Follow this checklist to match Airbnb's production pattern for enterprise WPGraphQL post type registrations.

### Pre-Registration Checklist

- [ ] **Base class extends RKV\Utilities\Post_Type\Base**
- [ ] **`initialize_post_type()` method implemented**
- [ ] **`$post_type_name` set (lowercase, underscores, ≤20 chars)**
- [ ] **`$show_in_graphql = true` if GraphQL exposure intended**
- [ ] **`$graphql_single_name` set (PascalCase singular)**
- [ ] **`$graphql_plural_name` set (PascalCase plural)**
- [ ] **Both GraphQL names match WordPress conventions**
- [ ] **ACF field groups configured (if using wpgraphql-acf)**
- [ ] **Dependency check: WPGraphQL plugin active**

### Testing Checklist

- [ ] **GraphQL schema includes post type (use GraphiQL introspection)**
- [ ] **Single node query works: `project(id: "...")`**
- [ ] **List query works: `projects(first: 10)`**
- [ ] **ACF fields appear in GraphQL schema**
- [ ] **Custom fields registered (if `register_graphql_fields()` overridden)**
- [ ] **Pagination works (pageInfo, hasNextPage, endCursor)**
- [ ] **Filtering works (where args)**
- [ ] **Security: Private posts not exposed**
- [ ] **Performance: N+1 query prevention (use WPGraphQL Smart Cache)**

### GraphiQL Test Query

```graphql
# Test single node query
query TestSingleProject {
  project(id: "cG9zdDoxMjM=") {
    id
    databaseId
    title
    content
    featuredImage {
      sourceUrl
    }
  }
}

# Test list query with pagination
query TestProjectsList {
  projects(first: 5, after: null) {
    edges {
      node {
        id
        title
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# Test where args filtering
query TestProjectsFiltering {
  projects(
    first: 10
    where: {
      status: PUBLISH
      orderby: { field: DATE, order: DESC }
    }
  ) {
    nodes {
      title
      date
    }
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
