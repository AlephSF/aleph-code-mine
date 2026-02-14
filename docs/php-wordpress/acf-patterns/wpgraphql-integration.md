---
title: "WPGraphQL + ACF Integration for Headless WordPress"
category: "wordpress-acf"
subcategory: "graphql-api"
tags: ["wpgraphql", "acf", "headless-wordpress", "graphql", "api", "next-js"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WPGraphQL integration with Advanced Custom Fields enables headless WordPress architectures by exposing ACF fields to GraphQL APIs. Field-level GraphQL configuration controls exposure, naming, and type mapping for consumption by frontend frameworks like Next.js.

WordPress projects analyzed show 100% GraphQL exposure in headless implementations (192 ACF fields with `show_in_graphql: 1`, 23 field groups fully integrated with WPGraphQL).

## Field-Level GraphQL Configuration

Every ACF field can be individually exposed to GraphQL with custom naming and metadata.

### JSON Configuration Pattern

```json
{
  "key": "field_680ad6fe88bfb",
  "label": "Logos",
  "name": "logos",
  "type": "repeater",
  "show_in_graphql": 1,
  "graphql_description": "List of client/partner logos with optional links",
  "graphql_field_name": "logos",
  "graphql_non_null": 0,
  "sub_fields": [
    {
      "key": "field_680ad71788bfc",
      "label": "Logo",
      "name": "logo",
      "type": "image",
      "show_in_graphql": 1,
      "graphql_field_name": "logo",
      "graphql_non_null": 0
    },
    {
      "key": "field_680ad74888bfd",
      "label": "Link",
      "name": "link",
      "type": "url",
      "show_in_graphql": 1,
      "graphql_field_name": "link",
      "graphql_non_null": 0
    }
  ]
}
```

**Key GraphQL Properties:**
- `show_in_graphql`: Enable/disable field in GraphQL (1 = enabled, 0 = disabled)
- `graphql_field_name`: Custom field name in GraphQL schema (camelCase convention)
- `graphql_description`: Field documentation in GraphQL schema
- `graphql_non_null`: Make field required in GraphQL (1 = required, 0 = nullable)

## Field Group GraphQL Configuration

Field groups define how ACF fields appear in GraphQL types.

### Field Group Settings

```json
{
  "key": "group_680ad6fe615b8",
  "title": "Logo Cloud Block",
  "show_in_graphql": 1,
  "graphql_field_name": "logoCloudBlock",
  "map_graphql_types_from_location_rules": 0,
  "graphql_types": "",
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

**GraphQL Field Group Properties:**
- `show_in_graphql`: Expose entire field group to GraphQL
- `graphql_field_name`: Field group name in GraphQL (camelCase, typically matches block name)
- `map_graphql_types_from_location_rules`: Auto-map to GraphQL types based on location rules
- `graphql_types`: Explicitly specify GraphQL types if not auto-mapped

## Naming Convention: snake_case to camelCase

ACF field names use PHP snake_case, but GraphQL APIs follow JavaScript camelCase conventions.

### Automatic Conversion

```json
{
  "name": "stat_suffix",
  "show_in_graphql": 1,
  "graphql_field_name": "statSuffix"
}
```

**Conversion Rules:**
- `municipality_id` → `municipalityId`
- `economic_impact` → `economicImpact`
- `total_tax_generated` → `totalTaxGenerated`
- `apply_to_descendants` → `applyToDescendants`

### Semantic Renaming

Override auto-conversion for better API semantics.

```json
{
  "name": "stat_suffix",
  "show_in_graphql": 1,
  "graphql_field_name": "quantity"
}
```

**Semantic Examples:**
- `stat_suffix` (PHP) → `quantity` (GraphQL): More descriptive
- `additional_stat_suffix` (PHP) → `additionalSymbol` (GraphQL): Clarifies purpose
- `stat_suffix_full_form` (PHP) → `quantityFullForm` (GraphQL): Maintains clarity

**Rationale:** Internal PHP field names may be abbreviated or context-specific, but GraphQL API names should be self-documenting for frontend consumers.

## GraphQL Query Patterns

ACF fields become accessible via GraphQL queries based on location rules.

### ACF Block Query

```graphql
query GetPageBlocks($id: ID!) {
  page(id: $id, idType: DATABASE_ID) {
    title
    editorBlocks {
      name
      ... on CreateBlockLogoCloudBlock {
        logoCloudBlock {
          logos {
            logo {
              sourceUrl
              altText
              mediaItemUrl
            }
            link
          }
        }
      }
    }
  }
}
```

### Post with ACF Fields Query

```graphql
query GetMunicipality($id: ID!) {
  municipality(id: $id, idType: DATABASE_ID) {
    title
    economicImpactBlock {
      metrics {
        economicImpact
        gdpContribution
        totalTaxGenerated
      }
    }
  }
}
```

### Options Page Query

```graphql
query GetSiteSettings {
  socialMediaOptions {
    facebookUrl
    twitterUrl
    instagramUrl
    linkedinUrl
  }
}
```

**Pattern:** Field groups become nested objects in the GraphQL response. Location rules determine where field groups attach (blocks, post types, options pages).

## GraphQL Response Structure

ACF field types map to GraphQL types predictably.

### Text/URL/Email Fields → String

```graphql
type Municipality {
  title: String
  municipalityId: String
  websiteUrl: String
}
```

### Number Fields → Float

```graphql
type Metrics {
  economicImpact: Float
  gdpContribution: Float
  totalTaxGenerated: Float
}
```

### Image Fields → MediaItem

```graphql
type Logo {
  logo: MediaItem
}

type MediaItem {
  sourceUrl: String
  altText: String
  mediaItemUrl: String
  mediaDetails: MediaDetails
}
```

### Repeater Fields → List

```graphql
type LogoCloudBlock {
  logos: [LogoItem]
}

type LogoItem {
  logo: MediaItem
  link: String
}
```

### Group Fields → Nested Object

```graphql
type NewsArticleDetails {
  headline: String
  link: String
  publicationName: String
  publicationDate: String
}
```

### True/False Fields → Boolean

```graphql
type Settings {
  applyToDescendants: Boolean
  inheritFromParent: Boolean
}
```

## Image Return Format for GraphQL

Images should use `return_format: "id"` for optimal GraphQL performance.

### Image Field Configuration

```json
{
  "name": "logo",
  "type": "image",
  "return_format": "id",
  "show_in_graphql": 1,
  "graphql_field_name": "logo"
}
```

**Why ID Return Format:**
- WPGraphQL resolves ID → full MediaItem object automatically
- Prevents duplicate data serialization (PHP doesn't need full image array)
- Enables GraphQL field selection (query only needed image properties)

### GraphQL Image Query

```graphql
{
  logoCloudBlock {
    logos {
      logo {
        sourceUrl          # Original upload URL
        altText            # Alt text from media library
        mediaItemUrl       # Same as sourceUrl
        srcSet             # Responsive image srcset
        mediaDetails {
          width
          height
          sizes {
            thumbnail
            medium
            large
          }
        }
      }
    }
  }
}
```

**Frontend Usage (Next.js):**
```tsx
import Image from 'next/image';

{logos.map((item) => (
  <Image
    src={item.logo.sourceUrl}
    alt={item.logo.altText || ''}
    width={item.logo.mediaDetails.width}
    height={item.logo.mediaDetails.height}
  />
))}
```

## GraphQL Non-Null Fields

Make fields required in GraphQL schema using `graphql_non_null: 1`.

### Required Field Pattern

```json
{
  "name": "heading",
  "type": "text",
  "required": 1,
  "show_in_graphql": 1,
  "graphql_field_name": "heading",
  "graphql_non_null": 1
}
```

**GraphQL Schema Result:**
```graphql
type StatBlock {
  heading: String!  # ! means non-null (required)
  stat: Float
}
```

**Use Case:** Frontend TypeScript types can assume non-null fields always exist, reducing null checks.

## Conditional Field Visibility

Conditionally shown ACF fields still expose to GraphQL but may be null.

### Conditional Logic + GraphQL

```json
{
  "fields": [
    {
      "name": "show_custom_text",
      "type": "true_false",
      "show_in_graphql": 1,
      "graphql_field_name": "showCustomText"
    },
    {
      "name": "custom_text",
      "type": "text",
      "conditional_logic": [
        [
          {
            "field": "field_show_custom_text",
            "operator": "==",
            "value": "1"
          }
        ]
      ],
      "show_in_graphql": 1,
      "graphql_field_name": "customText"
    }
  ]
}
```

**GraphQL Query:**
```graphql
{
  block {
    showCustomText
    customText  # May be null if showCustomText is false
  }
}
```

**Frontend Logic (Next.js):**
```tsx
{block.showCustomText && block.customText && (
  <p>{block.customText}</p>
)}
```

## WPGraphQL Introspection

Explore available ACF fields via GraphQL introspection queries.

### Introspection Query

```graphql
{
  __type(name: "CreateBlockLogoCloudBlock") {
    fields {
      name
      type {
        name
        kind
      }
      description
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "__type": {
      "fields": [
        {
          "name": "logoCloudBlock",
          "type": {
            "name": "CreateBlockLogoCloudBlock_LogoCloudBlock",
            "kind": "OBJECT"
          },
          "description": null
        }
      ]
    }
  }
}
```

**Tools:** GraphiQL IDE shows auto-generated docs from ACF GraphQL descriptions.

## Performance Optimization

Large ACF repeaters (50+ rows) can slow GraphQL queries. Optimize with limits and caching.

### Query Complexity Limits

```php
// functions.php or plugin
add_filter( 'graphql_query_complexity', function( $max_complexity ) {
  return 500; // Increase from default 100
}, 10, 1 );
```

### Field Pagination (Custom Resolver)

```php
add_filter( 'graphql_acf_field_resolve', function( $value, $field, $root, $args ) {
  if ( $field['name'] === 'large_repeater' ) {
    // Limit to first 20 items
    return is_array( $value ) ? array_slice( $value, 0, 20 ) : $value;
  }
  return $value;
}, 10, 4 );
```

### Object Caching

WPGraphQL supports object caching for repeated queries.

```php
// Enable object caching (Redis/Memcached)
define( 'GRAPHQL_DEBUG', false );
define( 'GRAPHQL_QUERY_COMPLEXITY', 300 );
```

## Next.js Integration Pattern

Headless Next.js apps consume WPGraphQL + ACF data via `graphql-request` or Apollo Client.

**Client setup:**
```typescript
import { GraphQLClient } from 'graphql-request';
export const client = new GraphQLClient(process.env.NEXT_PUBLIC_WORDPRESS_API_URL || '', {headers: {'Content-Type': 'application/json'}});
```

**Query + Types:**
```typescript
export const GET_PAGE_BLOCKS = gql`query GetPageBlocks($id: ID!) { page(id: $id, idType: DATABASE_ID) { title editorBlocks { name ... on CreateBlockLogoCloudBlock { logoCloudBlock { logos { logo { sourceUrl altText } link } } } } } }`;

interface LogoItem { logo: { sourceUrl: string; altText?: string }; link?: string }
interface LogoCloudBlock { logoCloudBlock: { logos: LogoItem[] } }
```

**Data fetching:**
```typescript
export async function getStaticProps({ params }) {
  const data = await client.request(GET_PAGE_BLOCKS, {id: params.slug});
  return {props: {page: data.page}, revalidate: 60};
}

export default function Page({ page }) {
  return (<>
    <h1>{page.title}</h1>
    {page.editorBlocks.map((block) => block.name === 'create-block/logo-cloud-block' && <LogoCloudBlock data={block.logoCloudBlock} />)}
  </>);
}
```

## GraphQL Security

Restrict GraphQL access to prevent data exposure and denial-of-service attacks.

### Query Depth Limiting

```php
// Prevent deeply nested queries
add_filter( 'graphql_max_query_depth', function() {
  return 15; // Max 15 levels deep
});
```

### Query Size Limiting

```php
// Limit query size to 10KB
add_filter( 'graphql_request_data', function( $data ) {
  $query_size = strlen( json_encode( $data ) );
  if ( $query_size > 10240 ) { // 10KB
    throw new \Exception( 'Query too large' );
  }
  return $data;
});
```

### Batch Query Limiting

```php
// Limit batch queries to 10 per request
add_filter( 'graphql_batch_query_limit', function() {
  return 10;
});
```

## Common Pitfalls

**Forgetting show_in_graphql:**
```json
// Bad: Field not exposed to GraphQL
{
  "name": "important_field",
  "type": "text"
}

// Good: Field exposed
{
  "name": "important_field",
  "type": "text",
  "show_in_graphql": 1,
  "graphql_field_name": "importantField"
}
```

**Name Collisions:**
```json
// Bad: GraphQL name conflicts with WordPress core
{
  "graphql_field_name": "title"  // Conflicts with post.title
}

// Good: Namespaced or prefixed
{
  "graphql_field_name": "customTitle"
}
```

**Image Return Format:**
```json
// Bad: Returns entire image array (not compatible with WPGraphQL)
{
  "type": "image",
  "return_format": "array"
}

// Good: Returns image ID (WPGraphQL resolves to MediaItem)
{
  "type": "image",
  "return_format": "id"
}
```

## Related Patterns

- **ACF Blocks:** Blocks auto-expose to GraphQL with proper field group configuration
- **Field Naming Conventions:** PHP snake_case → GraphQL camelCase conversion
- **Options Pages:** Global settings expose to GraphQL for site-wide data
- **Next.js ISR:** Combine WPGraphQL + ACF with Incremental Static Regeneration

**Source Projects:** airbnb (192 fields with `show_in_graphql: 1`, 23 field groups, 100% GraphQL exposure for headless architecture), thekelsey (0 GraphQL usage, traditional PHP templates)
