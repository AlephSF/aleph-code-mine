---
title: "ACF Field Naming Conventions: snake_case for PHP, camelCase for GraphQL"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "naming-conventions", "snake-case", "camel-case", "graphql", "code-standards"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Advanced Custom Fields (ACF) field naming conventions follow PHP snake_case standards for database storage and template access, with optional camelCase conversion for GraphQL API exposure. Proper naming improves code readability, prevents collisions, and enables clean API interfaces.

WordPress projects analyzed show 100% adoption of snake_case for PHP field names (393 fields analyzed) and 100% camelCase for GraphQL field names when WPGraphQL integration is enabled (192 GraphQL-exposed fields).

## PHP Field Name Pattern: snake_case

ACF field names in PHP use lowercase letters with underscores separating words. Field names become post meta keys in the database.

### Standard snake_case Examples

```php
// Good: Descriptive, lowercase, underscores
'municipality_id'
'economic_impact'
'gdp_contribution'
'total_tax_generated'
'hosting_not_primary_occupation'
'publication_date'
'apply_to_descendants'
'inherit_from_parent'

// Bad: CamelCase, PascalCase, or spaces
'municipalityId'      // Wrong: JavaScript convention, not PHP
'Municipality_ID'     // Wrong: PascalCase components
'municipality id'     // Wrong: Spaces not allowed
```

### Template Access Pattern

```php
// snake_case field names in get_field() calls
$municipality = get_field('municipality_id');
$impact = get_field('economic_impact');
$gdp = get_field('gdp_contribution');
$tax = get_field('total_tax_generated');

// Blade templates (Sage framework)
@php
  $social_links = get_field('social_media_links', 'option');
@endphp
{{ get_field('facebook_url', 'option') }}
```

## GraphQL Field Name Pattern: camelCase

When exposing ACF fields to WPGraphQL, field names convert to camelCase for JavaScript/GraphQL conventions.

### Automatic Conversion

ACF's `show_in_graphql` setting auto-converts snake_case to camelCase:

```json
{
  "name": "municipality_id",
  "type": "number",
  "show_in_graphql": 1,
  "graphql_field_name": "municipalityId"
}
```

**Conversion Rules:**
- `municipality_id` → `municipalityId`
- `economic_impact` → `economicImpact`
- `gdp_contribution` → `gdpContribution`
- `apply_to_descendants` → `applyToDescendants`

### Manual Semantic Naming

Custom `graphql_field_name` values override auto-conversion for better API semantics:

```json
{
  "name": "stat_suffix",
  "type": "text",
  "show_in_graphql": 1,
  "graphql_field_name": "quantity"
}
```

**Semantic Examples:**
- `stat_suffix` (PHP) → `quantity` (GraphQL): More descriptive API name
- `additional_stat_suffix` (PHP) → `additionalSymbol` (GraphQL): Clarifies purpose
- `stat_suffix_full_form` (PHP) → `quantityFullForm` (GraphQL): Maintains clarity

### GraphQL Query Example

```graphql
query GetLogoCloudBlock {
  logoCloudBlock {
    logos {
      logo {
        sourceUrl
        altText
      }
      link
    }
  }
}
```

Field names in GraphQL response:
- `logos` (from PHP `logos`)
- `logo` (from PHP `logo`)
- `link` (from PHP `link`)
- `sourceUrl` (WordPress standard image field)
- `altText` (WordPress standard image field)

## Field Name Length Guidelines

ACF field names should be concise but descriptive. Avoid abbreviations unless universally understood.

### Length Recommendations

```php
// Good: 15-30 characters, full words
'municipality_search_query'   // 27 chars, clear meaning
'hosting_not_primary_occupation'  // 35 chars, descriptive
'gdp_contribution'  // 17 chars, standard abbreviation

// Acceptable: Short names for simple fields
'stat'       // 4 chars, clear in context
'link'       // 4 chars, universal meaning
'logo'       // 4 chars, universal meaning
'title'      // 5 chars, universal meaning

// Avoid: Overly verbose
'municipality_search_query_input_field_value'  // 48 chars, redundant
```

## Context Prefixing Pattern

Some projects use prefixes to group related fields within a page template context.

### Template-Specific Prefix Pattern

```json
// Template: template-about.blade.php
{
  "fields": [
    {
      "name": "ta_title",
      "label": "TA Title"
    },
    {
      "name": "ta_text",
      "label": "TA Text"
    },
    {
      "name": "ta_link",
      "label": "TA Link"
    },
    {
      "name": "ta_aside_image",
      "label": "TA Aside Image"
    }
  ]
}
```

**Prefix:** `ta_` = "Text and Aside" (template context)

**Rationale:**
- Prevents field name collisions across templates
- Groups related fields alphabetically in admin
- Clarifies field scope when viewing post meta

**Confidence:** 50% adoption (1 of 2 projects). Modern pattern favors descriptive names without abbreviations.

## Service Integration Prefixes

Fields integrating with third-party services use service name prefixes for clarity.

### Third-Party Service Pattern

```php
// Funraise donation platform
'funraise_form_id'

// Vimeo video platform
'vimeo_url'
'vimeo_id'

// Social media platforms
'facebook_url'
'twitter_url'
'instagram_url'
'linkedin_url'
```

**Benefits:**
- Immediately identifies external dependency
- Groups service fields together
- Prevents confusion with generic fields (e.g., `form_id` vs `funraise_form_id`)

## Reserved Word Avoidance

ACF field names should avoid PHP reserved words and WordPress core field names to prevent conflicts.

### Reserved Words to Avoid

```php
// PHP reserved words (partial list)
'class'      // Use 'css_class' or 'item_class'
'function'   // Use 'callback' or 'handler'
'return'     // Use 'return_value' or 'result'
'array'      // Use 'items' or 'list'

// WordPress core post fields
'post_title'     // Use 'custom_title' or 'override_title'
'post_content'   // Use 'custom_content' or 'additional_content'
'post_excerpt'   // Use 'custom_excerpt' or 'summary'
'post_author'    // Use 'custom_author' or 'byline'
```

## Database Meta Key Format

ACF stores field values as post meta with the field name as the meta key. Understanding this helps with direct database queries.

### Meta Key Storage

```php
// Field name
"name": "municipality_id"

// Database storage (wp_postmeta table)
meta_key: "municipality_id"
meta_value: "12345"

// Additional ACF meta key for field key reference
meta_key: "_municipality_id"
meta_value: "field_67f5a8c3d2e1b"
```

**Note:** ACF creates two meta entries:
1. `{field_name}` → Actual field value
2. `_{field_name}` → Field key reference (for ACF internal use)

## Naming Pattern Comparison: Airbnb vs thekelsey

### Airbnb Pattern (Descriptive, No Prefixes)

```php
// Field group: Logo Cloud Block
'logos'           // Repeater field
'logo'            // Image sub-field
'link'            // URL sub-field

// Field group: Stat Block
'stat'
'stat_suffix'
'stat_suffix_full_form'
'additional_stat_suffix'

// Field group: Municipality Search
'municipality_id'
'apply_to_descendants'
'inherit_from_parent'
```

**Characteristics:**
- Descriptive, self-documenting names
- No abbreviations except standard terms (e.g., `id`, `url`)
- Context from field group title, not field name prefix

### thekelsey Pattern (Context Prefixes)

```php
// Field group: Text and Aside (template-about.blade.php)
'ta_title'         // ta_ = Text and Aside
'ta_text'
'ta_link'
'ta_aside_image'
'ta_aside_text'

// Field group: Social Media (options page)
'facebook_url'     // Service-specific prefix
'twitter_url'
'instagram_url'
'linkedin_url'
'vimeo_url'
```

**Characteristics:**
- Template-specific prefixes for scoping
- Service prefixes for third-party integrations
- More concise individual field names

## Field Label vs Field Name

ACF field labels are human-readable admin labels, while field names are technical identifiers.

### Label vs Name Pattern

```json
{
  "label": "Economic Impact Metric",
  "name": "economic_impact",
  "type": "number"
}
```

**Guidelines:**
- **Label:** Title case, spaces allowed, descriptive for editors
- **Name:** snake_case, programmatic, used in `get_field()` calls

**Example Pairs:**
- Label: "Municipality ID" → Name: `municipality_id`
- Label: "Apply to Descendants?" → Name: `apply_to_descendants`
- Label: "GDP Contribution ($B)" → Name: `gdp_contribution`
- Label: "Publication Date" → Name: `publication_date`

## Validation Rules

ACF field names must meet specific requirements for database and code compatibility.

### Technical Constraints

```php
// Valid characters
'municipality_id_2024'   // Letters, numbers, underscores

// Invalid characters
'municipality-id'        // Hyphens not allowed
'municipality.id'        // Dots not allowed
'municipality id'        // Spaces not allowed
'municipality/id'        // Slashes not allowed

// Length constraint
// Max 64 characters (MySQL post_meta.meta_key limit)
'very_long_field_name_that_exceeds_database_limits_and_fails'  // 68 chars: too long
```

## CLI Naming Conventions

When generating ACF field groups via WP-CLI or programmatic registration, use consistent naming patterns.

### Programmatic Registration Example

```php
acf_add_local_field_group(array(
  'key' => 'group_social_media',
  'title' => 'Social Media Links',
  'fields' => array(
    array(
      'key' => 'field_facebook_url',
      'label' => 'Facebook URL',
      'name' => 'facebook_url',  // snake_case
      'type' => 'url',
    ),
    array(
      'key' => 'field_twitter_url',
      'label' => 'Twitter URL',
      'name' => 'twitter_url',  // snake_case
      'type' => 'url',
    ),
  ),
  'location' => array(
    array(
      array(
        'param' => 'options_page',
        'operator' => '==',
        'value' => 'acf-options-social-media',
      ),
    ),
  ),
));
```

## Common Mistakes

**Inconsistent Casing:**
```php
// Bad: Mixed casing
'Municipality_ID'
'municipalityID'
'MunicipalityId'

// Good: Consistent snake_case
'municipality_id'
```

**Non-Descriptive Names:**
```php
// Bad: Unclear abbreviations
'ta_t'   // What does 't' mean?
'sm_lnk' // Social media link? Too cryptic

// Good: Descriptive
'ta_title'
'social_media_link'
```

**GraphQL Name Collisions:**
```php
// Bad: GraphQL name matches WordPress core field
"graphql_field_name": "title"  // Conflicts with post.title

// Good: Namespaced or prefixed
"graphql_field_name": "customTitle"
```

## Related Patterns

- **ACF JSON Storage:** Field names appear in JSON files and diffs
- **WPGraphQL Integration:** GraphQL requires camelCase field names
- **ACF Blocks:** Block field names should match block naming (e.g., `logo-cloud-block` → `logos` field)
- **Database Queries:** Field names become meta_key values for direct queries

**Source Projects:** airbnb (166 fields, 100% snake_case), thekelsey-wp (227 fields, 100% snake_case, 50% use context prefixes)
