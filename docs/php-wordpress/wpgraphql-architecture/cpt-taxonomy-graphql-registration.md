---
title: "Custom Post Type and Taxonomy GraphQL Registration"
category: "wpgraphql-architecture"
subcategory: "cpt-registration"
tags: ["wpgraphql", "custom-post-types", "taxonomy", "graphql-exposure", "headless-wp"]
stack: "php-wordpress"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Custom post types and taxonomies in headless WordPress require explicit GraphQL exposure configuration through three registration arguments: `show_in_graphql`, `graphql_single_name`, and `graphql_plural_name`. WPGraphQL reads these arguments during type registration and automatically generates GraphQL schema entries, queries, and mutations for the post type. Without proper configuration, custom content types remain invisible to GraphQL clients, breaking headless frontend applications that depend on the API.

## Standard Registration Pattern

WordPress custom post type registration for GraphQL-enabled headless applications follows a consistent three-argument pattern alongside standard REST API configuration.

```php
function register_headless_cpt() {
  $args = array(
    'public'              => true,
    'show_in_rest'        => true,
    'rest_base'           => 'local_pages',
    'show_in_graphql'     => true,           // Enable GraphQL exposure
    'graphql_single_name' => 'localPage',    // Singular type (camelCase)
    'graphql_plural_name' => 'localPages',   // Plural type (camelCase)
    'supports'            => array('title', 'editor', 'custom-fields'),
  );

  register_post_type('plc_local_pages', $args);
}
add_action('init', 'register_headless_cpt');
```

**Key Requirements:**
- `show_in_graphql` must be boolean `true`
- GraphQL names use camelCase convention
- Singular name for individual queries (localPage)
- Plural name for collection queries (localPages)

**Source:** airbnb/plugins/airbnb-policy-custom-mods/airbnb-policy-custom-mods.php (100% of CPTs follow pattern)

## Naming Conventions for GraphQL Types

GraphQL type names must follow strict camelCase convention with semantic clarity for frontend developers consuming the API.

### Correct Naming Patterns
```php
// Good: Clear, camelCase, semantically meaningful
'graphql_single_name' => 'localPage',      // Query: localPage(id: "123")
'graphql_plural_name' => 'localPages',     // Query: localPages(first: 10)

'graphql_single_name' => 'airLabPost',     // Query: airLabPost(id: "456")
'graphql_plural_name' => 'airLabPosts',    // Query: airLabPosts(where: {...})

'graphql_single_name' => 'blockPattern',
'graphql_plural_name' => 'blockPatterns',
```

### Incorrect Naming Patterns
```php
// Bad: snake_case (not GraphQL convention)
'graphql_single_name' => 'local_page',
'graphql_plural_name' => 'local_pages',

// Bad: PascalCase for field names (reserved for types)
'graphql_single_name' => 'LocalPage',

// Bad: Inconsistent pluralization
'graphql_single_name' => 'localPage',
'graphql_plural_name' => 'localPagesList',  // Should be localPages
```

**Rationale:** GraphQL schema conventions use camelCase for field names and PascalCase for type names. WPGraphQL automatically converts the provided names to proper type names internally.

## Taxonomy Registration for GraphQL

Taxonomies require identical GraphQL configuration arguments but often get overlooked during implementation, creating incomplete API coverage.

```php
function register_headless_taxonomy() {
  $args = array(
    'hierarchical'        => true,
    'public'              => true,
    'show_in_rest'        => true,
    'show_in_graphql'     => true,
    'graphql_single_name' => 'localCategory',
    'graphql_plural_name' => 'localCategories',
  );

  register_taxonomy('plc_local_category', 'plc_local_pages', $args);
}
add_action('init', 'register_headless_taxonomy');
```

**Common Gap:** Analyzed codebase showed CPTs with GraphQL exposure but taxonomies missing `show_in_graphql` configuration. This prevents taxonomy filtering in GraphQL queries despite taxonomies being registered for REST API.

## Generated GraphQL Schema

WPGraphQL automatically generates comprehensive schema entries when registration includes proper GraphQL arguments.

### Root Query Fields (Automatic)
```graphql
type RootQuery {
  # Singular query (by ID, slug, URI)
  localPage(
    id: ID
    idType: LocalPageIdType
  ): LocalPage

  # Collection query with filtering
  localPages(
    first: Int
    after: String
    where: RootQueryToLocalPageConnectionWhereArgs
  ): RootQueryToLocalPageConnection
}
```

### Generated Type Definition
```graphql
type LocalPage implements Node & ContentNode {
  id: ID!
  databaseId: Int!
  title: String
  content: String
  slug: String
  # ... additional fields from 'supports' array
  # ... ACF fields if wpgraphql-acf plugin active
}
```

### Taxonomy Integration
```graphql
type LocalPage {
  # Taxonomy relationship automatically added
  localCategories(
    first: Int
    where: LocalPageToLocalCategoryConnectionWhereArgs
  ): LocalPageToLocalCategoryConnection
}
```

**Source Confidence:** 100% - WPGraphQL v1.0+ automatically generates these schema entries

## Multisite Conditional Registration

WordPress VIP multisite environments require conditional GraphQL exposure based on site context to prevent unnecessary schema bloat.

```php
add_filter('register_post_type_args', function($args, $post_type) {
  // Only enable GraphQL for policy/impact site (blog_id 20)
  if (get_current_blog_id() !== 20) {
    return $args;
  }

  if ($post_type === 'custom_patterns') {
    $args['show_in_graphql'] = true;
    $args['graphql_single_name'] = 'blockPattern';
    $args['graphql_plural_name'] = 'blockPatterns';
  }

  return $args;
}, 10, 2);
```

**Use Case:** Large multisites serving both traditional and headless sites selectively enable GraphQL per site to:
- Reduce schema complexity
- Improve GraphQL introspection performance
- Prevent unauthorized data access across sites
- Maintain separate API surfaces per site

**Source:** airbnb/client-mu-plugins/decoupled-bundle-loader.php (conditional loading pattern)

## Common Registration Errors

### Missing Plural Name
```php
// Incomplete: Missing plural name
$args = array(
  'show_in_graphql'     => true,
  'graphql_single_name' => 'localPage',
  // Missing: 'graphql_plural_name' => 'localPages',
);
```

**Result:** WPGraphQL generates default plural name by adding "s" (e.g., "localPages"), but may produce incorrect pluralization ("personS" instead of "people").

### Inconsistent REST and GraphQL Naming
```php
// Inconsistent: REST and GraphQL names don't align
$args = array(
  'rest_base'           => 'local_pages',      // snake_case
  'graphql_single_name' => 'locationPage',     // Different terminology
);
```

**Better Approach:** Maintain naming consistency across APIs:
```php
$args = array(
  'rest_base'           => 'local_pages',
  'graphql_single_name' => 'localPage',   // Aligned terminology
);
```

### GraphQL Without REST API
```php
// Invalid: GraphQL requires REST API foundation
$args = array(
  'show_in_rest'        => false,         // REST disabled
  'show_in_graphql'     => true,          // GraphQL enabled
);
```

**Fix:** WPGraphQL requires `show_in_rest` to be `true` for GraphQL exposure to function correctly. Always enable REST API when enabling GraphQL.

## Validation and Testing

### Confirm GraphQL Exposure
```bash
# WP-CLI: List GraphQL-enabled post types
wp graphql list post-types

# Expected output includes:
# plc_local_pages (localPage/localPages)
# plc_airlab_posts (airLabPost/airLabPosts)
```

### GraphQL Introspection Query
```graphql
query CheckPostTypeRegistration {
  __type(name: "LocalPage") {
    name
    kind
    fields {
      name
      type {
        name
      }
    }
  }
}
```

**Expected Response:** Type definition with all registered fields including title, content, custom fields, and taxonomy relationships.

### Test Query
```graphql
query TestLocalPages {
  localPages(first: 5) {
    nodes {
      id
      databaseId
      title
      slug
    }
  }
}
```

**Verification Points:**
- Query executes without errors
- Returns expected post data
- Respects query arguments (first, after, where)
- Includes proper pagination cursors

**Source:** Standard WPGraphQL testing methodology
