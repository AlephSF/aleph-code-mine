---
title: "SQL Security Patterns with WordPress wpdb"
category: "wordpress-security"
subcategory: "sql-injection-prevention"
tags: ["sql-injection", "wpdb", "prepare", "esc_sql", "database-security"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## WordPress wpdb Security Overview

WordPress wpdb object provides SQL injection protection through prepared statements ($wpdb->prepare). Prepared statements use placeholders (%s, %d, %f) for user inputs, preventing malicious SQL code execution.

**Core SQL security functions:**
- `$wpdb->prepare()`: Prepared statements (291 instances, 69% of queries)
- `esc_sql()`: Manual SQL escaping (60 instances)
- `$wpdb->esc_like()`: LIKE clause escaping (15 instances)

**Critical security gap:** 127 unprepared queries detected (31% of total, SQL injection risk)

**Critical rule:** Always use $wpdb->prepare() for custom SQL queries with user inputs.

## $wpdb->prepare() Pattern

WordPress $wpdb->prepare() creates parameterized queries with type-safe placeholders. The method prevents SQL injection by escaping and quoting parameters.

```php
// Pattern: Prepared SELECT query
$term = $wpdb->get_row( $wpdb->prepare(
    "SELECT t.*, tt.*
     FROM $wpdb->terms AS t
     INNER JOIN $wpdb->term_taxonomy AS tt ON t.term_id = tt.term_id
     WHERE tt.term_taxonomy_id = %d
     LIMIT 1",
    $term_id
) );

// Pattern: Prepared query with LIKE clause
$post_meta_infos = $wpdb->get_results( $wpdb->prepare(
    "SELECT a.ID AS id, a.post_title AS title, b.meta_value AS sku
     FROM {$wpdb->posts} AS a
     INNER JOIN {$wpdb->postmeta} AS b ON a.ID = b.post_id
     WHERE b.meta_key = '_sku' AND b.meta_value LIKE %s",
    '%' . $wpdb->esc_like( $query ) . '%'
) );

// Pattern: Prepared UPDATE query
$wpdb->query( $wpdb->prepare(
    "UPDATE {$wpdb->term_taxonomy}
     SET count = %d
     WHERE term_taxonomy_id = %d",
    $new_count,
    $term_taxonomy_id
) );
```

**Placeholder types:**
- `%d`: Integer (e.g., post IDs, user IDs)
- `%f`: Float (e.g., prices, ratings)
- `%s`: String (e.g., titles, content)

**Usage:** 291 instances (89.7% in airbnb)

## SQL Injection Prevention

WordPress prepared statements prevent SQL injection by separating SQL logic from data. Placeholders ensure user inputs cannot modify query structure.

**SQL injection attack example:**
```php
// ❌ Vulnerable: Direct input concatenation
$post_id = $_GET['id'];
$post = $wpdb->get_row( "SELECT * FROM {$wpdb->posts} WHERE ID = {$post_id}" );
// Attack input: "1 OR 1=1" returns all posts!

// ✅ Secure: Prepared statement
$post_id = absint( $_GET['id'] );
$post = $wpdb->get_row( $wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE ID = %d",
    $post_id
) );
// Attack input neutralized: Treated as integer
```

**Attack vectors prevented:**
- Union-based injection
- Boolean-based blind injection
- Time-based blind injection
- Error-based injection
- Stacked queries

## LIKE Clause Escaping

WordPress $wpdb->esc_like() escapes LIKE wildcards (%, _) in user inputs for search queries. Pattern prevents LIKE clause injection where % and _ have special SQL meaning.

```php
// Pattern: Escape LIKE clause wildcards
$search = '%' . $wpdb->esc_like( $user_input ) . '%';
$results = $wpdb->get_results( $wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE post_title LIKE %s",
    $search
) );

// Pattern: Prefix search (starts with)
$search = $wpdb->esc_like( $user_input ) . '%';
$results = $wpdb->get_results( $wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE post_name LIKE %s",
    $search
) );

// Pattern: Suffix search (ends with)
$search = '%' . $wpdb->esc_like( $user_input );
$results = $wpdb->get_results( $wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE post_content LIKE %s",
    $search
) );
```

**What esc_like() escapes:**
- `%` → `\%` (wildcard)
- `_` → `\_` (single character wildcard)
- `\` → `\\` (escape character)

**Usage:** 15 instances across WordPress VIP codebase

## esc_sql() for Non-Prepared Contexts

WordPress esc_sql() manually escapes strings for SQL queries in contexts where prepare() cannot be used (e.g., IN clauses, dynamic table names). Use esc_sql() sparingly—prepare() is safer.

```php
// Pattern: esc_sql() for IN clause
$post_ids = array_map( 'absint', $_POST['post_ids'] );
$ids_string = implode( ',', $post_ids );
$posts = $wpdb->get_results(
    "SELECT * FROM {$wpdb->posts}
     WHERE ID IN ({$ids_string})"
);

// Pattern: esc_sql() for dynamic column names (use with extreme caution)
$orderby = sanitize_key( $_GET['orderby'] );
$allowed_columns = array( 'post_date', 'post_title', 'comment_count' );
if ( ! in_array( $orderby, $allowed_columns, true ) ) {
    $orderby = 'post_date';
}
$posts = $wpdb->get_results(
    "SELECT * FROM {$wpdb->posts}
     ORDER BY " . esc_sql( $orderby ) . " DESC"
);
```

**esc_sql() limitations:**
- Does not add quotes (manual quoting required)
- Does not validate data types
- Easier to misuse than prepare()

**Usage:** 60 instances across WordPress VIP codebase

**Prefer prepare() over esc_sql():**
```php
// ❌ Acceptable but not ideal: esc_sql()
$name = esc_sql( $_POST['name'] );
$wpdb->query( "INSERT INTO {$wpdb->prefix}custom_table (name) VALUES ('{$name}')" );

// ✅ Better: prepare()
$wpdb->query( $wpdb->prepare(
    "INSERT INTO {$wpdb->prefix}custom_table (name) VALUES (%s)",
    $_POST['name']
) );
```

## Unprepared Query Anti-Pattern

WordPress security critical gap: 127 unprepared $wpdb->query() calls detected (31% of total queries). Unprepared queries with user inputs create SQL injection vulnerabilities.

```php
// ❌ Critical vulnerability: Unprepared query with user input
$category = $_POST['category'];
$wpdb->query( "DELETE FROM {$wpdb->postmeta} WHERE meta_key = '{$category}'" );
// Attack input: "' OR '1'='1" deletes ALL postmeta!

// ✅ Secure: Prepared statement
$category = sanitize_text_field( $_POST['category'] );
$wpdb->query( $wpdb->prepare(
    "DELETE FROM {$wpdb->postmeta} WHERE meta_key = %s",
    $category
) );
```

**Impact of unprepared queries:**
- Data theft (SELECT injection)
- Data modification (UPDATE injection)
- Data deletion (DELETE injection)
- Privilege escalation (INSERT into wp_users)
- Complete database compromise

## WordPress Query Alternatives

WordPress provides query abstraction functions that automatically use prepared statements. Prefer WordPress functions over direct SQL for common operations.

**Prefer WordPress functions:**
```php
// ✅ WordPress function (automatically prepared)
$post = get_post( $post_id );
$posts = get_posts( array('post_type' => 'page') );
$meta = get_post_meta( $post_id, $meta_key, true );

// ❌ Direct SQL (requires manual prepare)
$post = $wpdb->get_row( $wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE ID = %d",
    $post_id
) );
```

**WordPress query functions (prepared internally):**
- `get_post()`, `get_posts()`: Post queries
- `get_user_by()`, `get_users()`: User queries
- `get_term_by()`, `get_terms()`: Taxonomy queries
- `get_post_meta()`, `update_post_meta()`: Post meta
- `get_option()`, `update_option()`: Options
- `wp_insert_post()`, `wp_update_post()`: Post operations
