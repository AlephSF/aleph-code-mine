---
title: "GraphQL Security Patterns for WordPress VIP Headless Sites"
category: "wordpress-vip"
subcategory: "security"
tags: ["graphql", "security", "dos-protection", "wpgraphql", "rate-limiting"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## GraphQL DoS Attack Vectors

WordPress headless sites using WPGraphQL are vulnerable to denial-of-service attacks via large queries, deeply nested queries, field duplication attacks, and complex resolver chains. GraphQL's flexibility allows attackers to request expensive operations in a single query, overwhelming server resources.

**Common attack patterns:**
1. **Field Duplication DoS:** Repeating same field 1000+ times (`posts posts posts...`)
2. **Large Query DoS:** Sending 1MB+ query strings to exhaust memory
3. **Complex Query DoS:** Deeply nested queries with high resolver cost
4. **Resolver Amplification:** Requesting N+1 queries via nested relationships

```graphql
# Attack example: Field duplication
query {
  posts posts posts posts posts posts posts posts posts posts
  posts posts posts posts posts posts posts posts posts posts
  # ... repeated 1000+ times
}

# Attack example: Deep nesting
query {
  posts {
    author {
      posts {
        author {
          posts {
            # ... 50+ levels deep
          }
        }
      }
    }
  }
}
```

## Multi-Layer GraphQL Security Pattern

WordPress VIP headless deployments implement multi-layer GraphQL security with query size limits (pre-parse), field deduplication (request data phase), and complexity limits (validation phase). Layered defenses catch different attack vectors at appropriate execution stages.

**Security layers:**
1. **Layer 1:** Query size limiting (10KB max) - blocks large payloads early
2. **Layer 2:** Field deduplication - neutralizes repetition attacks
3. **Layer 3:** Query complexity limiting (500 max) - prevents expensive resolvers

**Execution order:**
```
HTTP Request → Layer 1 (size) → Layer 2 (dedupe) → Layer 3 (complexity) → Resolvers
```

## Layer 1: Query Size Limiting

WordPress VIP uses `graphql_request_data` filter (priority 1) to enforce maximum query size before GraphQL parsing. Hard limits prevent memory exhaustion from multi-megabyte payloads.

```php
// client-mu-plugins/graphql-security.php
<?php
add_filter( 'graphql_request_data', function( $data ) {
    if ( empty( $data['query'] ) ) {
        return $data;
    }

    $query = $data['query'];

    // Hard limit: 10KB max query size
    $max_size = apply_filters( 'airbnb_graphql_max_query_size', 10000 );
    if ( strlen( $query ) > $max_size ) {
        throw new \GraphQL\Error\UserError(
            sprintf( 'Query exceeds maximum size of %d bytes.', $max_size )
        );
    }

    return $data;
}, 1 ); // Priority 1 = run very early
```

**Security metrics:**
- Max query size: 10,000 bytes (10KB)
- Execution phase: Pre-parse (before GraphQL processing)
- Attack mitigation: Large payload DoS

**Recommended limits:**
- **Development:** 50KB (accommodate introspection queries)
- **Production:** 10KB (typical queries <5KB)
- **Public APIs:** 5KB (tightest security)

## Layer 2: Field Deduplication

WordPress VIP uses regex deduplication to neutralize field duplication attacks before GraphQL parsing. The pattern collapses repeated adjacent field names (`posts posts posts` → `posts`), rendering repetition attacks ineffective.

```php
// client-mu-plugins/graphql-security.php
<?php
add_filter( 'graphql_request_data', function( $data ) {
    if ( empty( $data['query'] ) ) {
        return $data;
    }

    $query = $data['query'];

    // Dedupe repeated adjacent field names (neutralize field duplication attack)
    // "posts posts posts" → "posts"
    $data['query'] = preg_replace( '/\b(\w+)(\s+\1)+\b/', '$1', $query );

    return $data;
}, 1 );
```

**Regex explanation:**
- `\b`: Word boundary
- `(\w+)`: Capture field name (group 1)
- `(\s+\1)+`: Match one or more repetitions of same field
- `$1`: Replace with single instance

**Attack mitigation:**
```graphql
# Before deduplication (attack)
query {
  posts posts posts posts posts
}

# After deduplication (safe)
query {
  posts
}
```

## Layer 3: Query Complexity Limiting

WordPress VIP uses GraphQL's `QueryComplexity` validation rule to limit resolver execution cost. Complexity scoring assigns point values to fields based on resolver expense, rejecting queries exceeding thresholds.

```php
// client-mu-plugins/graphql-security.php
<?php
use GraphQL\Validator\Rules\QueryComplexity;

add_filter( 'graphql_validation_rules', function( $rules ) {
    $max_complexity = apply_filters( 'airbnb_graphql_max_complexity', 500 );
    $rules['query_complexity'] = new QueryComplexity( $max_complexity );
    return $rules;
} );
```

**Complexity calculation:**
- **Simple fields:** 1 point (post title, author name)
- **List fields:** 1 point × list size (posts with first: 10 = 10 points)
- **Nested fields:** Multiplied (posts → author → posts = exponential)

**Example complexity scoring:**
```graphql
# Query complexity: ~50 points
query {
  posts(first: 10) {        # 10 points (list of 10)
    title                   # 10 × 1 = 10 points
    author {                # 10 × 1 = 10 points
      name                  # 10 × 1 = 10 points
    }
  }
}

# Total: 10 + 10 + 10 + 10 = 40 points (within 500 limit)
```

## Filterable Security Thresholds

WordPress VIP implements filterable GraphQL security thresholds for per-site customization. Filters allow adjusting limits based on site traffic, server capacity, or attack patterns without modifying core security code.

```php
// Default limits (client-mu-plugins/graphql-security.php)
$max_size = apply_filters( 'airbnb_graphql_max_query_size', 10000 );
$max_complexity = apply_filters( 'airbnb_graphql_max_complexity', 500 );

// Override in theme or separate MU-plugin
add_filter( 'airbnb_graphql_max_query_size', function() {
    return 5000; // Tighter limit for public API
} );

add_filter( 'airbnb_graphql_max_complexity', function() {
    return 1000; // Higher limit for authenticated users
} );
```

**Use cases for custom limits:**
- Increase complexity for internal admin GraphQL
- Decrease size for public-facing APIs
- Environment-specific limits (development vs production)
- Per-blog_id limits in multisite

### Conditional Limits by User Role

```php
add_filter( 'airbnb_graphql_max_complexity', function( $default ) {
    if ( is_user_logged_in() && current_user_can('edit_posts') ) {
        return 2000; // Higher limit for editors
    }
    return $default; // 500 for public
} );
```

## GraphQL Error Handling

WordPress VIP GraphQL security layers throw `\GraphQL\Error\UserError` exceptions for policy violations. User errors return HTTP 200 with structured error messages, distinguishing from server errors (HTTP 500).

```php
// Throw user error for policy violation
throw new \GraphQL\Error\UserError(
    sprintf( 'Query exceeds maximum size of %d bytes.', $max_size )
);
```

**Error response:**
```json
{
  "errors": [
    {
      "message": "Query exceeds maximum size of 10000 bytes.",
      "extensions": {
        "category": "user"
      }
    }
  ],
  "data": null
}
```

**HTTP status:** 200 (GraphQL spec requires 200 for user errors)

**Alternative: Validation errors**
```json
{
  "errors": [
    {
      "message": "Max query complexity should be 500 but got 750.",
      "extensions": {
        "category": "graphql"
      }
    }
  ]
}
```

## Attack Pattern Detection Logging

WordPress VIP headless sites log GraphQL security violations for attack pattern analysis. Logging captures query size, complexity, client IP, and user agent for threat intelligence.

```php
// Enhanced security with logging
add_filter( 'graphql_request_data', function( $data ) {
    if ( empty( $data['query'] ) ) {
        return $data;
    }

    $query = $data['query'];
    $size = strlen( $query );
    $max_size = apply_filters( 'airbnb_graphql_max_query_size', 10000 );

    if ( $size > $max_size ) {
        // Log attack attempt
        error_log( sprintf(
            'GraphQL query size violation: %d bytes from %s (User-Agent: %s)',
            $size,
            $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
        ) );

        throw new \GraphQL\Error\UserError(
            sprintf( 'Query exceeds maximum size of %d bytes.', $max_size )
        );
    }

    return $data;
}, 1 );
```

**Logged data:**
- Query size (bytes)
- Client IP address
- User agent string
- Timestamp (via error_log)

## GraphQL Rate Limiting (Advanced Pattern)

WordPress VIP advanced deployments add rate limiting based on client IP or authenticated user to prevent sustained DoS attacks. Rate limiting uses transients or object cache for request counting.

```php
// Rate limiting by IP address (100 requests per minute)
add_action( 'graphql_before_resolve_field', function() {
    static $checked = false;
    if ( $checked ) return;
    $checked = true;

    $client_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $cache_key = 'graphql_rate_limit_' . md5( $client_ip );

    $request_count = wp_cache_get( $cache_key );
    if ( false === $request_count ) {
        $request_count = 0;
    }

    $request_count++;
    wp_cache_set( $cache_key, $request_count, '', 60 ); // 60 seconds TTL

    if ( $request_count > 100 ) {
        throw new \GraphQL\Error\UserError(
            'Rate limit exceeded. Maximum 100 requests per minute.'
        );
    }
}, 1 );
```

**Rate limit strategies:**
- **IP-based:** 100-1000 requests/minute (public APIs)
- **User-based:** 500-5000 requests/minute (authenticated)
- **Token-based:** 10000+ requests/minute (internal services)

## GraphQL Introspection Control

WordPress VIP production GraphQL endpoints disable introspection queries to prevent schema enumeration by attackers. Introspection enables attackers to discover all available fields, mutations, and relationships.

```php
// Disable introspection in production
add_filter( 'graphql_introspection_enabled', function( $enabled ) {
    if ( defined('VIP_GO_ENV') && 'production' === VIP_GO_ENV ) {
        return false; // Disable introspection
    }
    return $enabled; // Enable in development
} );
```

**Introspection query example:**
```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      fields {
        name
      }
    }
  }
}
```

**Security trade-off:**
- **Enabled:** Easier development (schema discovery)
- **Disabled:** Prevents attackers from enumerating schema

## Client MU-Plugin for GraphQL Security

WordPress VIP centralizes GraphQL security in dedicated `graphql-security.php` client MU-plugin. Consolidates all defenses in single file.

```php
// client-mu-plugins/graphql-security.php
<?php
add_filter('graphql_request_data',function($data){
  if(empty($data['query'])){return $data;}
  $max=apply_filters('airbnb_graphql_max_query_size',10000);
  if(strlen($data['query'])>$max){throw new \GraphQL\Error\UserError(sprintf('Query exceeds %d bytes.',$max));}
  $data['query']=preg_replace('/\b(\w+)(\s+\1)+\b/','$1',$data['query']);
  return $data;
},1);
use GraphQL\Validator\Rules\QueryComplexity;
add_filter('graphql_validation_rules',function($rules){
  $max=apply_filters('airbnb_graphql_max_complexity',500);
  $rules['query_complexity']=new QueryComplexity($max);
  return $rules;
});
add_filter('graphql_introspection_enabled',function($enabled){
  if(defined('VIP_GO_ENV')&&'production'===VIP_GO_ENV){return false;}
  return $enabled;
});
```

**File location:** `/client-mu-plugins/graphql-security.php`
**Loading:** Auto-loaded (top-level client MU-plugin)
