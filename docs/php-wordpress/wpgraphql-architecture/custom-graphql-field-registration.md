---
title: "Custom GraphQL Field and Type Registration"
category: "wpgraphql-architecture"
subcategory: "schema-extension"
tags: ["wpgraphql", "register-graphql-field", "custom-types", "schema-extension"]
stack: "php-wordpress"
priority: "medium"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WPGraphQL schema extends through `register_graphql_field()` and `register_graphql_type()` functions called within `graphql_register_types` action hook. Custom field registration adds computed fields, external API data, or third-party plugin integration to existing GraphQL types without modifying core plugin code. Airbnb Policy site registers 362 custom GraphQL fields across post types, taxonomies, and root query, exposing Yoast SEO metadata, Polylang language relationships, and custom business logic through strongly-typed GraphQL schema. Field resolvers execute during query processing, enabling dynamic data fetching from WordPress meta tables, external APIs, or complex calculations.

## register_graphql_field() Pattern

Custom fields attach to existing GraphQL types through `register_graphql_field()` function providing type name, field name, and configuration array.

### Basic Field Registration
```php
add_action('graphql_register_types', function() {
  register_graphql_field('Post', 'customField', [
    'type' => 'String',
    'description' => 'Custom computed field on posts',
    'resolve' => function($post, $args, $context, $info) {
      return get_post_meta($post->databaseId, 'custom_meta_key', true);
    },
  ]);
});
```

**Configuration Keys:**
- `type` (string|array): GraphQL type (String, Int, Boolean, custom type)
- `description` (string): Schema documentation
- `resolve` (callable): Function returning field value
- `args` (array): Optional input arguments for field

**Resolver Parameters:**
- `$post`: Source object (post, term, user, etc.)
- `$args`: Field arguments passed in query
- `$context`: AppContext with current user, loader instances
- `$info`: ResolveInfo with field metadata

**Source:** wp-graphql-yoast-seo plugin pattern (airbnb/plugins/add-wpgraphql-seo/)

## Extending ContentNode Interface

ContentNode interface covers all post types, enabling single field registration affecting posts, pages, and custom post types.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('ContentNode', 'estimatedReadTime', [
    'type' => 'Int',
    'description' => 'Estimated read time in minutes',
    'resolve' => function($post) {
      $content = strip_tags($post->content);
      $word_count = str_word_count($content);
      return max(1, ceil($word_count / 200)); // 200 words/minute
    },
  ]);
});
```

**Result:** Field appears on all content types:
```graphql
query GetPostReadTime {
  post(id: "123", idType: DATABASE_ID) {
    title
    estimatedReadTime  # Available on Post
  }

  page(id: "456", idType: DATABASE_ID) {
    title
    estimatedReadTime  # Available on Page
  }

  localPage(id: "789", idType: DATABASE_ID) {
    title
    estimatedReadTime  # Available on custom CPT
  }
}
```

**Use Case:** Add fields to all content without registering per post type

**Source Confidence:** 100% - WPGraphQL ContentNode interface pattern

## RootQuery Field Registration

Custom root query fields enable global data access, settings pages, external API integration, or aggregated data queries.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('RootQuery', 'siteSettings', [
    'type' => 'SiteSettings',
    'description' => 'Global site configuration',
    'resolve' => function() {
      return [
        'footerCopyright' => get_option('site_footer_copyright'),
        'contactEmail' => get_option('admin_email'),
        'socialLinks' => get_option('social_media_links'),
      ];
    },
  ]);
});
```

**Query Usage:**
```graphql
query GetSiteSettings {
  siteSettings {
    footerCopyright
    contactEmail
    socialLinks {
      facebook
      twitter
    }
  }
}
```

**Common Use Cases:**
- ACF Options Pages → GraphQL
- Theme mod settings exposure
- External API aggregation
- Feature flags configuration

**Source:** add-wpgraphql-seo implements RootQuery.seo field (airbnb/plugins/add-wpgraphql-seo/wp-graphql-yoast-seo.php lines 104-112)

## Field Resolvers with Arguments

Custom fields accept input arguments enabling filtered, paginated, or configurable data queries.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('Post', 'relatedPosts', [
    'type' => ['list_of' => 'Post'],
    'description' => 'Related posts by category',
    'args' => [
      'limit' => [
        'type' => 'Int',
        'description' => 'Number of related posts',
        'defaultValue' => 5,
      ],
    ],
    'resolve' => function($post, $args) {
      $categories = wp_get_post_categories($post->databaseId);

      $related = get_posts([
        'category__in' => $categories,
        'post__not_in' => [$post->databaseId],
        'posts_per_page' => $args['limit'],
      ]);

      return $related;
    },
  ]);
});
```

**Query with Arguments:**
```graphql
query GetRelatedPosts {
  post(id: "123", idType: DATABASE_ID) {
    title
    relatedPosts(limit: 3) {
      title
      excerpt
    }
  }
}
```

**Source:** Standard WPGraphQL field argument pattern

## Computed Fields from External APIs

Resolvers fetch data from external services, third-party APIs, or microservices during GraphQL query execution.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('Post', 'githubStars', [
    'type' => 'Int',
    'description' => 'GitHub stars for repository linked in post',
    'resolve' => function($post) {
      $repo_url = get_post_meta($post->databaseId, 'github_repo', true);

      if (empty($repo_url)) {
        return null;
      }

      // Extract owner/repo from URL
      preg_match('/github\.com\/([^\/]+)\/([^\/]+)/', $repo_url, $matches);

      if (count($matches) < 3) {
        return null;
      }

      $owner = $matches[1];
      $repo = $matches[2];

      // Fetch from GitHub API (with caching)
      $cache_key = "gh_stars_{$owner}_{$repo}";
      $stars = get_transient($cache_key);

      if (false === $stars) {
        $response = wp_remote_get("https://api.github.com/repos/{$owner}/{$repo}");

        if (!is_wp_error($response)) {
          $body = json_decode(wp_remote_retrieve_body($response), true);
          $stars = $body['stargazers_count'] ?? 0;
          set_transient($cache_key, $stars, HOUR_IN_SECONDS);
        }
      }

      return (int) $stars;
    },
  ]);
});
```

**Performance Considerations:**
- Use WordPress transients for caching
- Implement timeout handling
- Return null for API failures
- Consider DataLoader pattern for batch queries

## Custom Object Types

Complex custom fields require custom GraphQL object types registered via `register_graphql_object_type()`.

```php
add_action('graphql_register_types', function() {
  // Register custom type
  register_graphql_object_type('SeoMetadata', [
    'description' => 'SEO metadata for posts',
    'fields' => [
      'title' => ['type' => 'String'],
      'description' => ['type' => 'String'],
      'canonical' => ['type' => 'String'],
      'robots' => ['type' => ['list_of' => 'String']],
    ],
  ]);

  // Use custom type in field
  register_graphql_field('ContentNode', 'seo', [
    'type' => 'SeoMetadata',
    'description' => 'Yoast SEO metadata',
    'resolve' => function($post) {
      return [
        'title' => get_post_meta($post->databaseId, '_yoast_wpseo_title', true),
        'description' => get_post_meta($post->databaseId, '_yoast_wpseo_metadesc', true),
        'canonical' => get_post_meta($post->databaseId, '_yoast_wpseo_canonical', true),
        'robots' => explode(',', get_post_meta($post->databaseId, '_yoast_wpseo_meta-robots-noindex', true)),
      ];
    },
  ]);
});
```

**Query Result:**
```graphql
query GetSeoMetadata {
  post(id: "123", idType: DATABASE_ID) {
    title
    seo {
      title
      description
      canonical
      robots
    }
  }
}
```

**Source:** wp-graphql-yoast-seo implements SEO types (airbnb/plugins/add-wpgraphql-seo/)

## Extending Taxonomy Terms

Custom fields on taxonomy terms expose term metadata, computed values, or external relationships.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('Category', 'postCount', [
    'type' => 'Int',
    'description' => 'Number of published posts in category',
    'resolve' => function($term) {
      return $term->count; // WordPress maintains this automatically
    },
  ]);

  register_graphql_field('Category', 'featuredImage', [
    'type' => 'MediaItem',
    'description' => 'Category featured image from ACF',
    'resolve' => function($term, $args, $context) {
      $image_id = get_term_meta($term->term_id, 'featured_image', true);

      if (!$image_id) {
        return null;
      }

      return $context->get_loader('post')->load_deferred($image_id);
    },
  ]);
});
```

**DataLoader Pattern:** Use `$context->get_loader()` to batch database queries preventing N+1 problems

## Boolean Primary Taxonomy Flag

Yoast SEO's primary category feature requires custom GraphQL field checking term against post's primary category meta.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('PostToTermNodeConnection', 'isPrimary', [
    'type' => 'Boolean',
    'description' => 'Whether this term is the Yoast SEO primary category',
    'resolve' => function($item, $args, $context) {
      $post_id = $item['source']->ID;
      $term_id = $item['node']->term_id;
      $taxonomy = $item['node']->taxonomy;

      $primary_term_id = get_post_meta($post_id, "_yoast_wpseo_primary_{$taxonomy}", true);

      return (int) $primary_term_id === (int) $term_id;
    },
  ]);
});
```

**Query Usage:**
```graphql
query GetPrimaryCategory {
  post(id: "123", idType: DATABASE_ID) {
    categories {
      nodes {
        name
        isPrimary  # true for one category
      }
    }
  }
}
```

**Source:** add-wpgraphql-seo/wp-graphql-yoast-seo.php (airbnb implementation)

## User Field Extensions

Custom user fields expose profile data, computed statistics, or external account connections.

```php
add_action('graphql_register_types', function() {
  register_graphql_field('User', 'seo', [
    'type' => 'SEOUser',
    'description' => 'User SEO metadata from Yoast',
    'resolve' => function($user) {
      // Check if user has published posts
      if (!YoastSEO()->meta->for_author($user->userId)) {
        return null;
      }

      return [
        'title' => get_the_author_meta('wpseo_title', $user->userId),
        'metaDescription' => get_the_author_meta('wpseo_metadesc', $user->userId),
      ];
    },
  ]);

  register_graphql_field('User', 'postCount', [
    'type' => 'Int',
    'resolve' => function($user) {
      return count_user_posts($user->userId, 'post', true);
    },
  ]);
});
```

**Source:** wp-graphql-yoast-seo user SEO fields (airbnb/plugins/add-wpgraphql-seo/)

## Interface Field Registration

Fields registered on GraphQL interfaces automatically appear on all implementing types.

```php
add_action('graphql_register_types', function() {
  // Add field to NodeWithTitle interface
  register_graphql_field('NodeWithTitle', 'seo', [
    'type' => 'PostTypeSEO',
    'description' => 'SEO metadata for any content with title',
    'resolve' => function($post, $args, $context) {
      return get_yoast_seo_data($post->databaseId);
    },
  ]);
});
```

**Affected Types:**
- Post (implements NodeWithTitle)
- Page (implements NodeWithTitle)
- Custom post types (implement NodeWithTitle)
- MediaItem (implements NodeWithTitle)

**Benefit:** Single registration affects multiple post types, reducing code duplication

**Source:** add-wpgraphql-seo uses NodeWithTitle pattern

## Common Field Registration Errors

### Error: Field Not Appearing in Schema
**Cause:** Action hook runs too late
```php
// ❌ Wrong: Runs after GraphQL initializes schema
add_action('init', function() {
  add_action('graphql_register_types', function() {
    register_graphql_field('Post', 'customField', [...]);
  });
});

// ✅ Correct: Direct registration
add_action('graphql_register_types', function() {
  register_graphql_field('Post', 'customField', [...]);
});
```

### Error: Resolver Returns Wrong Type
**Cause:** Type mismatch between declared and returned
```php
// ❌ Wrong: Declares Int, returns String
register_graphql_field('Post', 'viewCount', [
  'type' => 'Int',
  'resolve' => fn($post) => get_post_meta($post->databaseId, 'views', true),
  // Returns string from meta, should cast to int
]);

// ✅ Correct: Cast to declared type
register_graphql_field('Post', 'viewCount', [
  'type' => 'Int',
  'resolve' => fn($post) => (int) get_post_meta($post->databaseId, 'views', true),
]);
```

### Error: N+1 Query Problem
**Cause:** Resolver queries database per item
```php
// ❌ Bad: 100 posts = 100 database queries
register_graphql_field('Post', 'author', [
  'type' => 'User',
  'resolve' => function($post) {
    return get_user_by('id', $post->post_author); // N+1 problem
  },
]);

// ✅ Good: Use DataLoader
register_graphql_field('Post', 'author', [
  'type' => 'User',
  'resolve' => function($post, $args, $context) {
    return $context->get_loader('user')->load_deferred($post->post_author);
  },
]);
```

**DataLoader Benefits:**
- Batches queries automatically
- Deduplicates identical requests
- Caches within single request

## Testing Custom Fields

### Introspection Query
```graphql
{
  __type(name: "Post") {
    fields {
      name
      type {
        name
        kind
      }
    }
  }
}
```

**Expected:** Custom field appears in Post type fields list

### Field Query Test
```graphql
query TestCustomField {
  post(id: "123", idType: DATABASE_ID) {
    title
    customField
    estimatedReadTime
  }
}
```

**Verification:** Custom fields return expected data without errors

### Argument Validation Test
```graphql
query TestFieldArgs {
  post(id: "123", idType: DATABASE_ID) {
    relatedPosts(limit: 3) {
      title
    }
    tooMany: relatedPosts(limit: 100) {
      title
    }
  }
}
```

**Check:** Arguments control query behavior correctly
