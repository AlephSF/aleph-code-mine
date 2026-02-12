# WordPress GraphQL Implementation Comparison

**Date:** February 12, 2026
**Repos Analyzed:** airbnb (impact site), thekelsey-wp
**Purpose:** Quantify WPGraphQL adoption and patterns for Phase 4 Domain 1

---

## GraphQL Adoption Summary

| Metric | Airbnb (Impact Site) | Thekelsey-WP | Pattern |
|--------|---------------------|--------------|---------|
| **GraphQL Implementation** | ✅ Full WPGraphQL stack | ❌ None | 50% adoption |
| **`show_in_graphql` usage** | 124 instances | 0 | Airbnb only |
| **`register_graphql` calls** | 362 instances | 0 | Airbnb only |
| **GraphQL filters/actions** | 65 hooks | 0 | Airbnb only |
| **GraphQL plugins** | 4 plugins | 0 | Airbnb only |
| **ACF field groups** | 23 groups | 20+ groups | Both use ACF |
| **ACF GraphQL fields** | 193 custom names | 0 | Airbnb only |
| **GraphQL security** | ✅ Query limits | N/A | Airbnb only |

---

## Airbnb WPGraphQL Stack

### Core GraphQL Plugins (4)
1. **wpgraphql-acf** - Exposes ACF fields to GraphQL (v2.0+)
2. **wp-graphql-polylang** - Multilingual GraphQL queries
3. **wp-graphql-tax-query** - Advanced taxonomy filtering
4. **add-wpgraphql-seo** - Yoast SEO field exposure

### Custom Implementations
- **graphql-security.php** (mu-plugin) - DoS prevention
- **vip-decoupled-bundle** (mu-plugin) - Headless utilities
- **airbnb-policy-blocks** - 27 custom blocks with GraphQL exposure
- **airbnb-policy-custom-mods** - CPT/taxonomy registration with GraphQL

---

## CPT Registration Patterns

### Airbnb Pattern (show_in_graphql)
```php
$args = array(
  'show_in_rest'        => true,
  'show_in_graphql'     => true,           // Enable GraphQL
  'graphql_single_name' => 'localPage',    // Singular (camelCase)
  'graphql_plural_name' => 'localPages',   // Plural (camelCase)
  // ... other args
);
register_post_type( 'plc_local_pages', $args );
```

**Custom Post Types with GraphQL:**
- `plc_local_pages` → localPage/localPages
- `plc_airlab_posts` → airLabPost/airLabPosts
- Block patterns (via filter)

**Source Confidence:** 100% (all CPTs in impact site use this pattern)

### Thekelsey Pattern
- Uses traditional `show_in_rest` for WordPress REST API
- No GraphQL exposure
- CPTs: Projects, Events, Resources (REST only)

---

## ACF GraphQL Configuration

### Field-Level Configuration
Each ACF field in airbnb has:
```json
{
  "show_in_graphql": 1,
  "graphql_field_name": "quantity",
  "graphql_description": "",
  "graphql_non_null": 0
}
```

### Field Group-Level Configuration
```json
{
  "show_in_graphql": 1,
  "graphql_field_name": "statBlock",
  "map_graphql_types_from_location_rules": 0,
  "graphql_types": ""
}
```

**Statistics:**
- 23 ACF field groups in airbnb-policy-blocks
- 193 fields with custom GraphQL field names
- 100% adoption of camelCase naming

**Examples:**
- `stat_suffix` → `quantity` (semantic renaming)
- `stat_suffix_full_form` → `quantityFullForm` (accessibility)
- `additional_stat_suffix` → `additionalSymbol`

---

## Custom GraphQL Field Registration

### Pattern: register_graphql_field()
```php
add_action( 'graphql_register_types', function() {
  register_graphql_field('ContentNode', 'seo', [
    'type' => 'PostTypeSEO',
    'description' => __('The Yoast SEO data', 'wp-graphql-yoast-seo'),
    'resolve' => function ($post, $args, $context) {
      return wp_gql_seo_get_post_type_graphql_fields($post, $args, $context);
    },
  ]);
});
```

**Usage in Airbnb:**
- 362 `register_graphql_field/type` calls
- Used by: add-wpgraphql-seo, wp-graphql-polylang, custom plugins
- Extends: RootQuery, ContentNode, User, taxonomies

---

## Polylang GraphQL Integration

### Language Query Parameters
```php
register_graphql_fields('RootQueryToContentNodeConnectionWhereArgs', [
  'language' => [
    'type' => 'LanguageCodeFilterEnum',
    'description' => 'Filter content nodes by language code',
  ],
  'languages' => [
    'type' => ['list_of' => ['non_null' => 'LanguageCodeEnum']],
    'description' => 'Filter by one or more languages',
  ],
]);
```

### Language Setting on Mutations
```php
function __action_graphql_post_object_mutation_update_additional_data(
  $post_id, $input, $post_type_object, $mutation_name
) {
  if (isset($input['language'])) {
    pll_set_post_language($post_id, $input['language']);
  }
}
```

**Known Issue (Documented in Code):**
- wp-graphql-polylang requires manual patch for hyphenated language codes (en-au)
- Fix: Replace hyphens with underscores in language enum generation
- GitHub issue: https://github.com/valu-digital/wp-graphql-polylang/issues/80

---

## GraphQL Security Implementation

### Query Size Limit (graphql-security.php)
```php
$max_size = apply_filters( 'airbnb_graphql_max_query_size', 10000 ); // 10KB
if ( strlen( $query ) > $max_size ) {
  throw new \GraphQL\Error\UserError(
    sprintf( 'Query exceeds maximum size of %d bytes.', $max_size )
  );
}
```

### Field Deduplication (DoS Prevention)
```php
// Converts "posts posts posts" into single occurrence
$data['query'] = preg_replace( '/\b(\w+)(\s+\1)+\b/', '$1', $query );
```

### Query Complexity Validation
```php
add_filter( 'graphql_validation_rules', function( $rules ) {
  $max_complexity = apply_filters( 'airbnb_graphql_max_complexity', 500 );
  $rules['query_complexity'] = new QueryComplexity( $max_complexity );
  return $rules;
} );
```

**Limits:**
- Max query size: 10KB
- Max complexity: 500
- Field deduplication: Automated

---

## Headless Theme Pattern

### Aleph Nothing Theme (44 lines total)
**files:**
- style.css (8 lines) - Theme registration only
- functions.php (44 lines) - GraphQL filters only
- index.php (minimal) - Empty template
- 2 page templates (minimal)

**functions.php Purpose:**
1. Add theme support for post thumbnails
2. Apply wpautop to WYSIWYG fields in VIP Block Data API
3. Apply wpautop to term descriptions in GraphQL

**No Template Files** - 100% headless, frontend in separate Next.js app

---

## Taxonomy GraphQL Exposure

### Issue Identified
Airbnb taxonomies (plc_local_pages_category, plc_local_pages_tag) do NOT have:
- `show_in_graphql` set
- `graphql_single_name` set
- `graphql_plural_name` set

**This is likely a gap** - taxonomies should be exposed if CPTs are exposed.

---

## Key Findings

### Universal Patterns (Airbnb)
1. **CPT GraphQL Args** - All CPTs use show_in_graphql with singular/plural names
2. **ACF Field Naming** - 100% camelCase GraphQL field names
3. **Security First** - Query limits implemented before GraphQL adoption
4. **Multisite Conditional** - Decoupled bundle loaded only for site #20
5. **Plugin-Based Config** - Zero theme dependencies

### Gap Patterns
1. **Thekelsey-WP** - No GraphQL implementation (opportunity for migration)
2. **Taxonomy Exposure** - Missing show_in_graphql on taxonomies
3. **Polylang Patch** - Requires manual fix for hyphenated language codes

### De Facto Standards (Where Applied)
- show_in_graphql + graphql_single_name + graphql_plural_name (100%)
- camelCase GraphQL field names (100%)
- Query size limit: 10KB (100%)
- Query complexity limit: 500 (100%)
- ACF JSON version control (100%)

---

## Recommendations for Documentation

### High Priority Docs
1. **CPT/Taxonomy GraphQL Registration** - show_in_graphql pattern
2. **ACF Field GraphQL Configuration** - Field and group settings
3. **GraphQL Security Patterns** - Query limits and deduplication
4. **Polylang GraphQL Integration** - Language filtering and mutations
5. **Custom GraphQL Field Registration** - register_graphql_field pattern
6. **Minimal Headless Theme** - Aleph Nothing theme as exemplar
7. **VIP Block Data API Filters** - wpautop and data transformation
8. **Conditional Plugin Loading** - Multisite blog_id pattern

### Medium Priority
9. **GraphQL Query Optimization** - Complexity management
10. **ACF JSON Version Control** - acf-json directory pattern
11. **Custom GraphQL Types** - register_graphql_type pattern
12. **GraphQL Debugging** - Available tools and techniques

---

## Next Steps

1. Write 8 RAG-optimized docs based on high/medium priority list
2. Create 4 PHPCS/custom rules:
   - Require show_in_graphql on public CPTs
   - Enforce graphql_single_name/plural_name naming convention
   - Warn on taxonomies without GraphQL exposure
   - Require query size/complexity limits
3. Document Polylang patch requirement
4. Recommend Thekelsey-WP GraphQL migration path
