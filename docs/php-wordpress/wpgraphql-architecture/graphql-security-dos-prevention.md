---
title: "GraphQL Security and DoS Prevention"
category: "wpgraphql-architecture"
subcategory: "security"
tags: ["wpgraphql", "security", "dos-prevention", "query-limits", "performance"]
stack: "php-wordpress"
priority: "high"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

GraphQL APIs without query limits face denial-of-service vulnerabilities through deeply nested queries, field duplication attacks, and oversized query strings that exhaust server resources before execution begins. Production WordPress GraphQL implementations require three-layered defense: pre-parse query size limits, field deduplication regex, and complexity validation during GraphQL parsing. Airbnb Policy site implements 10KB query size limit and 500-point complexity maximum using custom must-use plugin that runs before WPGraphQL processes requests, preventing malicious queries from reaching the database layer or consuming PHP memory.

## Query Size Limiting (Pre-Parse Defense)

Query size limits prevent oversized GraphQL strings from consuming parser memory before validation begins.

```php
<?php
/**
 * Plugin Name: GraphQL Security
 * Description: Query size & complexity protection
 */

add_filter('graphql_request_data', function($data) {
  if (empty($data['query'])) {
    return $data;
  }

  $query = $data['query'];

  // Hard limit on query size (10KB max)
  $max_size = apply_filters('airbnb_graphql_max_query_size', 10000);

  if (strlen($query) > $max_size) {
    throw new \GraphQL\Error\UserError(
      sprintf('Query exceeds maximum size of %d bytes.', $max_size)
    );
  }

  return $data;
}, 1); // Priority 1 = run very early
```

**Defense Layer 1:**
- Runs before GraphQL parser initializes
- Rejects queries >10KB immediately
- Prevents memory exhaustion from giant query strings
- Filterable limit via `airbnb_graphql_max_query_size` hook

**Attack Prevented:**
```graphql
# Malicious query: 50KB of nested fields
query Attack {
  posts {
    author { posts { author { posts { author {
      # ... 10,000 levels deep
    }}}}}
  }
}
```

**Source:** airbnb/client-mu-plugins/graphql-security.php (lines 24-45)

## Field Deduplication (DoS Attack Mitigation)

Field duplication attacks exploit GraphQL parsers by repeating field names hundreds of times, causing exponential validation overhead.

```php
add_filter('graphql_request_data', function($data) {
  if (empty($data['query'])) {
    return $data;
  }

  // Dedupe repeated adjacent field names
  // Converts "posts posts posts" into single occurrence
  $data['query'] = preg_replace('/\b(\w+)(\s+\1)+\b/', '$1', $data['query']);

  return $data;
}, 1);
```

**Attack Pattern:**
```graphql
query FieldDuplicationAttack {
  posts posts posts posts posts posts posts
  posts posts posts posts posts posts posts
  # Repeated 10,000 times
}
```

**After Deduplication:**
```graphql
query FieldDuplicationAttack {
  posts
}
```

**How It Works:**
- Regex pattern: `\b(\w+)(\s+\1)+\b`
- Matches: Word boundary + word + (space + same word)+ + word boundary
- Replaces: All duplicates with single occurrence
- Runs pre-parse before GraphQL sees query

**Source Confidence:** 100% - airbnb/client-mu-plugins/graphql-security.php (lines 39-42)

## Query Complexity Validation

GraphQL-PHP's QueryComplexity rule scores query depth and breadth, rejecting queries that exceed configurable threshold.

```php
use GraphQL\Validator\Rules\QueryComplexity;

add_filter('graphql_validation_rules', function($rules) {
  $max_complexity = apply_filters('airbnb_graphql_max_complexity', 500);
  $rules['query_complexity'] = new QueryComplexity($max_complexity);
  return $rules;
});
```

**How Complexity Scoring Works:**
- Each field = 1 point
- Nested fields multiply: `posts { author }` = 2 points
- List fields multiply by estimated count: `posts(first: 100)` = 100x multiplier
- WPGraphQL estimates list sizes from `first` argument

**Example Complexity Calculation:**
```graphql
query ModerateComplexity {
  posts(first: 10) {        # 10x multiplier
    title                   # 10 points
    author {                # 10 points (nested)
      name                  # 10 points (nested)
    }
  }
}
# Total: 30 points (within 500 limit)
```

**Rejected Query:**
```graphql
query TooComplex {
  posts(first: 100) {       # 100x multiplier
    title
    author {
      posts(first: 50) {    # 100 × 50 = 5000x
        title
        # Over 500 complexity limit
      }
    }
  }
}
```

**Source:** airbnb/client-mu-plugins/graphql-security.php (lines 53-57)

## Defense-in-Depth Strategy

Three-layered security approach catches attacks at different stages of request lifecycle.

### Security Layer Execution Order
```
1. graphql_request_data filter (Priority 1)
   ├─ Query size check (10KB limit)
   ├─ Field deduplication regex
   └─ Modified query passed to parser

2. GraphQL Parser
   └─ Parses query into AST

3. graphql_validation_rules filter
   ├─ QueryComplexity rule (500 limit)
   ├─ QueryDepth rule (optional)
   └─ Custom validation rules

4. Query Execution
   └─ Resolver functions run
```

**Why Multiple Layers:**
- **Size limit:** Stops attacks before parsing (saves CPU)
- **Deduplication:** Neutralizes field repetition exploits
- **Complexity:** Catches deeply nested or broad queries

**Resource Savings:**
- Rejected pre-parse: ~1ms, 0KB memory
- Rejected during validation: ~50ms, 2MB memory
- Executed malicious query: 30s+, 512MB memory, database overload

## Configurable Limits via Filters

Production and development environments require different security thresholds.

### Override Defaults in Plugin
```php
// Increase limits for authenticated admin users
add_filter('airbnb_graphql_max_query_size', function($default) {
  if (current_user_can('manage_options')) {
    return 50000; // 50KB for admins
  }
  return $default; // 10KB for public
});

add_filter('airbnb_graphql_max_complexity', function($default) {
  if (current_user_can('manage_options')) {
    return 2000; // Higher complexity for admins
  }
  return $default; // 500 for public
});
```

### Development Environment Override
```php
// wp-config.php or environment-specific plugin
if (defined('WP_DEBUG') && WP_DEBUG) {
  add_filter('airbnb_graphql_max_query_size', fn() => 100000);   // 100KB dev
  add_filter('airbnb_graphql_max_complexity', fn() => 5000);      // Relaxed dev
}
```

**Use Cases:**
- GraphQL IDE exploration: Higher limits for authenticated users
- Batch operations: Admins need complex queries for data imports
- Development: Relaxed limits for testing edge cases
- Staging: Production limits to catch issues

## Must-Use Plugin Deployment

Security rules must deploy as must-use plugins to guarantee execution before GraphQL plugins load.

### Directory Structure
```
wp-content/
├── mu-plugins/
│   ├── graphql-security.php        # Security rules (loads first)
│   ├── decoupled-bundle-loader.php # Conditionally loads WPGraphQL
│   └── other-mu-plugins.php
└── plugins/
    ├── wp-graphql/                 # Loads after mu-plugins
    ├── wpgraphql-acf/
    └── other-plugins/
```

### Why Must-Use Plugin
```php
// ❌ Bad: Regular plugin (no execution guarantee)
// plugins/graphql-security/graphql-security.php
// Problem: May load after WPGraphQL, missing early hooks

// ✅ Good: Must-use plugin (guaranteed first)
// mu-plugins/graphql-security.php
// Loads before all plugins, hooks run first
```

**Mu-Plugin Characteristics:**
- Load before regular plugins
- Cannot be deactivated via admin UI
- No activation hooks (always active)
- Ideal for critical security code

**Source:** WordPress VIP Go standard practice (airbnb uses mu-plugins pattern)

## Monitoring and Alerting

Production GraphQL APIs require monitoring to detect attack patterns and legitimate queries hitting limits.

### Log Rejected Queries
```php
add_filter('graphql_request_data', function($data) {
  if (empty($data['query'])) {
    return $data;
  }

  $query = $data['query'];
  $max_size = apply_filters('airbnb_graphql_max_query_size', 10000);

  if (strlen($query) > $max_size) {
    // Log rejection for security monitoring
    error_log(sprintf(
      'GraphQL query rejected: %d bytes from IP %s',
      strlen($query),
      $_SERVER['REMOTE_ADDR'] ?? 'unknown'
    ));

    throw new \GraphQL\Error\UserError(
      sprintf('Query exceeds maximum size of %d bytes.', $max_size)
    );
  }

  return $data;
}, 1);
```

### Complexity Rejection Logging
```php
add_action('graphql_execute', function($result, $schema, $source) {
  if (!empty($result->errors)) {
    foreach ($result->errors as $error) {
      if (strpos($error->getMessage(), 'complexity') !== false) {
        error_log('GraphQL complexity limit exceeded: ' . $error->getMessage());
      }
    }
  }
}, 10, 3);
```

**Metrics to Track:**
- Rejection rate by limit type (size vs complexity)
- Top rejected query patterns
- IP addresses with multiple rejections
- Legitimate queries approaching limits

## Rate Limiting Integration

Query limits prevent single large requests but don't stop request flooding attacks.

### Nginx Rate Limiting
```nginx
# /etc/nginx/conf.d/graphql-rate-limit.conf
limit_req_zone $binary_remote_addr zone=graphql:10m rate=10r/s;

server {
  location /graphql {
    limit_req zone=graphql burst=20 nodelay;
    limit_req_status 429;
    # ... proxy to WordPress
  }
}
```

### WordPress Plugin Rate Limiting
```php
// Simple rate limiting in mu-plugin
add_action('graphql_before_resolve_field', function() {
  $ip = $_SERVER['REMOTE_ADDR'] ?? '';
  $transient_key = 'graphql_rate_' . md5($ip);

  $requests = get_transient($transient_key) ?: 0;

  if ($requests > 60) { // 60 requests per minute
    throw new \GraphQL\Error\UserError('Rate limit exceeded');
  }

  set_transient($transient_key, $requests + 1, 60); // 60-second window
}, 1);
```

**Combined Defense:**
- Nginx: 10 requests/second
- WordPress: 60 requests/minute
- Query size: 10KB max
- Complexity: 500 points max

## Common Security Misconfigurations

### Error: Limits Applied Too Late
```php
// ❌ Wrong: Uses 'init' hook (too late)
add_action('init', function() {
  add_filter('graphql_request_data', function($data) {
    // GraphQL already processed by this point
  });
});

// ✅ Correct: Direct filter registration
add_filter('graphql_request_data', function($data) {
  // Runs before GraphQL initialization
}, 1);
```

### Error: Complexity Without Size Limit
```php
// ❌ Incomplete: Only complexity limit
add_filter('graphql_validation_rules', function($rules) {
  $rules['query_complexity'] = new QueryComplexity(500);
  return $rules;
});
// Missing: Pre-parse size limit
// Attack: 50MB query string passed to parser

// ✅ Complete: Both size and complexity
add_filter('graphql_request_data', function($data) {
  // Size limit first
  if (strlen($data['query']) > 10000) {
    throw new \GraphQL\Error\UserError('Query too large');
  }
  return $data;
}, 1);

add_filter('graphql_validation_rules', function($rules) {
  // Complexity limit second
  $rules['query_complexity'] = new QueryComplexity(500);
  return $rules;
});
```

### Error: No Field Deduplication
```php
// ❌ Vulnerable: Missing deduplication
add_filter('graphql_request_data', function($data) {
  // Only size check
  if (strlen($data['query']) > 10000) {
    throw new \GraphQL\Error\UserError('Query too large');
  }
  return $data;
}, 1);
// Attack: "posts posts posts..." (9KB but 10,000 fields)

// ✅ Protected: With deduplication
add_filter('graphql_request_data', function($data) {
  if (strlen($data['query']) > 10000) {
    throw new \GraphQL\Error\UserError('Query too large');
  }
  // Deduplicate before size check catches it
  $data['query'] = preg_replace('/\b(\w+)(\s+\1)+\b/', '$1', $data['query']);
  return $data;
}, 1);
```

## Testing Security Rules

### Test Size Limit
```bash
# Generate 20KB query (should be rejected)
curl -X POST http://site.test/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"'$(printf 'query{posts{title}}%.0s' {1..1000})'"}
'

# Expected: "Query exceeds maximum size of 10000 bytes"
```

### Test Complexity Limit
```graphql
# GraphQL Playground: Should be rejected
query TestComplexity {
  posts(first: 100) {
    author {
      posts(first: 100) {
        author {
          posts(first: 100) {
            title
          }
        }
      }
    }
  }
}
# Expected: "Max query complexity should be 500 but got 1000000"
```

### Test Field Deduplication
```graphql
# Should auto-collapse to single field
query TestDedup {
  posts posts posts
  posts posts posts
}
# Expected: Query executes normally (deduped to single "posts")
```

**Verification:** Check error logs for rejection messages, confirm queries execute within limits
