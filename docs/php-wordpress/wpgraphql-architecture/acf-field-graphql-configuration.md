---
title: "ACF Field Groups GraphQL Configuration"
category: "wpgraphql-architecture"
subcategory: "acf-integration"
tags: ["acf", "wpgraphql-acf", "graphql-fields", "custom-fields", "headless-wp"]
stack: "php-wordpress"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Advanced Custom Fields Pro integrates with WPGraphQL through the wpgraphql-acf plugin, which exposes ACF fields to the GraphQL API via JSON configuration. Each ACF field and field group requires four GraphQL-specific settings: `show_in_graphql`, `graphql_field_name`, `graphql_description`, and `graphql_non_null`. Proper configuration enables headless frontends to query custom field data through a strongly-typed GraphQL schema while maintaining semantic field names that differ from WordPress database column names. Analyzed codebase shows 193 ACF fields with custom GraphQL names across 23 field groups,demonstrating systematic API design for headless applications.

## Field-Level GraphQL Configuration

ACF Pro 6.0+ adds GraphQL configuration options to each field's settings panel, controlling API exposure and naming conventions.

### Complete Field Configuration
```json
{
  "key": "field_676086739eefd",
  "label": "Stat Suffix",
  "name": "stat_suffix",
  "type": "text",
  "show_in_graphql": 1,
  "graphql_field_name": "quantity",
  "graphql_description": "Abbreviated form of quantity",
  "graphql_non_null": 0
}
```

**Configuration Options:**
- **show_in_graphql** (`0|1`): Controls API visibility (default: 0)
- **graphql_field_name** (string): API field name, overrides PHP name
- **graphql_description** (string): Schema documentation
- **graphql_non_null** (`0|1`): Enforces non-nullable type (default: 0)

**When to Override Field Name:**
- Database field uses snake_case: `stat_suffix` → `quantity`
- Frontend needs semantic clarity: `stat_suffix_full_form` → `quantityFullForm`
- API versioning requires name stability despite backend changes

**Source:** airbnb/plugins/airbnb-policy-blocks/acf-json/*.json (193 fields analyzed)

## Field Group GraphQL Settings

Field group configuration determines how ACF data appears in the GraphQL schema and which post types receive the fields.

```json
{
  "key": "group_676086739eefd",
  "title": "Stat Block",
  "fields": [...],
  "location": [
    [{
      "param": "block",
      "operator": "==",
      "value": "create-block/stat-block"
    }]
  ],
  "show_in_graphql": 1,
  "graphql_field_name": "statBlock",
  "map_graphql_types_from_location_rules": 0,
  "graphql_types": ""
}
```

**Group Settings:**
- **show_in_graphql** (`0|1`): Exposes entire group
- **graphql_field_name** (string): Root field name in GraphQL type
- **map_graphql_types_from_location_rules** (`0|1`): Auto-attach to post types
- **graphql_types** (array): Manual post type targeting

**Result in GraphQL:**
```graphql
type CreateBlockStatBlock {
  stat: String
  quantity: String
  quantityFullForm: String
  context: String
  # Field group becomes object type
}
```

## Semantic Field Naming Strategy

Analyzed codebase demonstrates systematic renaming of database fields to create semantically meaningful API contracts.

### Database vs API Naming Examples

| Database Field Name | GraphQL Field Name | Rationale |
|---------------------|-------------------|-----------|
| `stat_suffix` | `quantity` | More semantically meaningful |
| `stat_suffix_full_form` | `quantityFullForm` | Maintains camelCase, adds clarity |
| `additional_stat_suffix` | `additionalSymbol` | Clarifies purpose (% or +) |
| `post_title` | `title` | Removes redundant prefix |

### Implementation Pattern
```json
{
  "label": "Stat Suffix Full Form",
  "name": "stat_suffix_full_form",
  "type": "text",
  "instructions": "Full form of suffix, read by screen readers",
  "show_in_graphql": 1,
  "graphql_field_name": "quantityFullForm"
}
```

**Benefits:**
- Frontend developers work with clear, semantic names
- Database schema can evolve without breaking API contract
- Field purpose obvious from GraphQL name alone
- TypeScript code generation produces readable types

**Source Confidence:** 100% - All 193 GraphQL-exposed fields use semantic naming

## ACF JSON Version Control

ACF Pro's JSON sync feature enables version control of field configurations including GraphQL settings, critical for team collaboration.

### Directory Structure
```
plugins/airbnb-policy-blocks/
├── acf-json/
│   ├── group_676086739eefd.json  # Stat Block fields
│   ├── group_67afe69c6c17a.json  # City Portal fields
│   ├── group_67cf5eb4837a9.json  # FAQ Block fields
│   └── [20 more field groups]
├── airbnb-policy-blocks.php
└── [other plugin files]
```

### Plugin Configuration
```php
// Save ACF field groups to plugin directory
function acf_json_save_point() {
  return plugin_dir_path(__FILE__) . 'acf-json';
}
add_filter('acf/settings/save_json', 'acf_json_save_point');

// Load field groups from plugin directory
function acf_json_load_point() {
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json';
  return $paths;
}
add_filter('acf/settings/load_json', 'acf_json_load_point');
```

**Workflow Benefits:**
- Git tracks all GraphQL field changes
- Pull requests show exact field configuration diffs
- Team reviews API changes before deployment
- Staging/production environments stay synchronized
- Field groups deploy with plugin code

**Source:** airbnb/plugins/airbnb-policy-blocks/airbnb-policy-blocks.php (lines 49-61)

## Field Type GraphQL Mapping

WPGraphQL-ACF automatically maps ACF field types to GraphQL scalar types with sensible defaults.

### Common Type Mappings

| ACF Field Type | GraphQL Type | Nullable Default | Notes |
|----------------|--------------|------------------|-------|
| `text` | `String` | Yes | Single-line text |
| `textarea` | `String` | Yes | Multi-line text |
| `number` | `Float` | Yes | Supports decimals |
| `true_false` | `Boolean` | Yes | Checkbox |
| `select` | `String` | Yes | Dropdown value |
| `relationship` | `[PostObjectUnion]` | Yes | Post references |
| `image` | `MediaItem` | Yes | Image object with sizes |
| `wysiwyg` | `String` | Yes | HTML content |
| `repeater` | `[AcfFieldGroupName]` | Yes | Nested objects |

### Image Field Example
```graphql
type StatBlock {
  image: MediaItem  # ACF image field
}

type MediaItem {
  id: ID!
  sourceUrl: String
  altText: String
  mediaDetails: MediaDetails
  # Includes all image sizes
}
```

**Query Usage:**
```graphql
query GetStatBlock {
  statBlock {
    image {
      sourceUrl(size: MEDIUM)
      altText
    }
  }
}
```

## Conditional Field Visibility

ACF conditional logic controls field visibility in WordPress admin but does NOT affect GraphQL schema generation.

### Admin UI Conditional Logic
```json
{
  "key": "field_conditional_example",
  "label": "Advanced Options",
  "name": "advanced_options",
  "conditional_logic": [
    [{
      "field": "field_show_advanced",
      "operator": "==",
      "value": "1"
    }]
  ],
  "show_in_graphql": 1,
  "graphql_field_name": "advancedOptions"
}
```

**GraphQL Behavior:**
- Field appears in GraphQL schema regardless of conditional logic
- Frontend receives `null` if field not visible during post edit
- GraphQL clients must handle nullable fields appropriately
- Cannot conditionally hide fields from GraphQL schema

**Design Decision:** GraphQL schemas must be static for client-side code generation. Runtime field visibility handled through nullable types.

## Block-Specific Field Groups

ACF field groups attached to custom Gutenberg blocks require block namespace in location rules.

```json
{
  "key": "group_stat_block",
  "title": "Stat Block",
  "location": [
    [{
      "param": "block",
      "operator": "==",
      "value": "create-block/stat-block"
    }]
  ],
  "show_in_graphql": 1,
  "graphql_field_name": "statBlock"
}
```

**Generated GraphQL:**
```graphql
type CreateBlockStatBlock implements AcfFieldGroup {
  fieldGroupName: String
  stat: String
  quantity: String
  quantityFullForm: String
}

type Page {
  blocks(where: {nameIn: ["create-block/stat-block"]}) {
    ... on CreateBlockStatBlock {
      attributes {
        data {
          stat
          quantity
        }
      }
    }
  }
}
```

**Pattern:** Block namespace (`create-block/`) becomes part of GraphQL type name (`CreateBlockStatBlock`)

**Source:** airbnb/plugins/airbnb-policy-blocks - 27 custom blocks with ACF field groups

## Polylang Translation Configuration

ACF fields in multilingual sites require Polylang translation settings alongside GraphQL configuration.

```json
{
  "key": "field_translated_text",
  "label": "Hero Title",
  "name": "hero_title",
  "type": "text",
  "translations": "translate",
  "pll_default_value": "",
  "show_in_graphql": 1,
  "graphql_field_name": "heroTitle"
}
```

**Translation Options:**
- `"translate"` - Field translated per language
- `"copy_once"` - Copied on translation, then independent
- `null` - Not translated, shared across languages

### GraphQL Query with Language
```graphql
query GetHeroTranslated($language: LanguageCodeEnum!) {
  pages(where: {language: $language}) {
    nodes {
      heroFields {
        heroTitle  # Returns translated value
      }
    }
  }
}
```

**Source:** Polylang Pro + wpgraphql-polylang integration (airbnb implementation)

## Common Configuration Errors

### Error: Field Not Appearing in GraphQL

**Cause 1:** Field group has `show_in_graphql: 0`
```json
{
  "title": "My Fields",
  "show_in_graphql": 0,  // ❌ Hides entire group
  "fields": [
    {
      "name": "my_field",
      "show_in_graphql": 1  // ❌ Ignored if group hidden
    }
  ]
}
```

**Fix:** Enable group-level GraphQL exposure first

**Cause 2:** Post type missing `show_in_graphql`
- ACF fields only appear on GraphQL-enabled post types
- Verify CPT has `'show_in_graphql' => true`

### Error: GraphQL Type Name Collision

**Cause:** Multiple field groups use same `graphql_field_name`
```json
// Group 1
{"graphql_field_name": "content"}
// Group 2
{"graphql_field_name": "content"}  // ❌ Collision
```

**Fix:** Use unique, descriptive names:
```json
{"graphql_field_name": "pageContent"}
{"graphql_field_name": "blockContent"}
```

### Error: Null Values Despite Required Field

**Cause:** `graphql_non_null: 1` without `required: 1`
```json
{
  "required": 0,              // Not required in WordPress
  "graphql_non_null": 1       // ❌ Claims non-null in GraphQL
}
```

**Fix:** Align GraphQL and ACF validation:
```json
{
  "required": 1,              // Required in WordPress
  "graphql_non_null": 1       // Non-null in GraphQL
}
```

## Validation and Testing

### Test Field Exposure
```graphql
{
  __type(name: "CreateBlockStatBlock") {
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

**Expected Output:**
```json
{
  "data": {
    "__type": {
      "fields": [
        {"name": "stat", "type": {"name": "String", "kind": "SCALAR"}},
        {"name": "quantity", "type": {"name": "String", "kind": "SCALAR"}},
        {"name": "quantityFullForm", "type": {"name": "String", "kind": "SCALAR"}}
      ]
    }
  }
}
```

### Test Field Data
```graphql
query TestStatBlock {
  pages(first: 1, where: {hasBlockType: "create-block/stat-block"}) {
    nodes {
      blocks {
        ... on CreateBlockStatBlock {
          attributes {
            data {
              stat
              quantity
            }
          }
        }
      }
    }
  }
}
```

**Verification:** Returns ACF field values for pages using stat-block
