# ACF Field Naming Conventions

---
title: "ACF Field Naming Conventions"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "naming-conventions", "snake-case", "camelcase", "graphql", "prefixes"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF field naming follows strict conventions based on architecture type. Traditional PHP-based WordPress sites use snake_case exclusively for field names matching WordPress core conventions. Headless WordPress sites with GraphQL APIs maintain snake_case for PHP but add custom camelCase GraphQL field names for JavaScript consumption. Both patterns prioritize descriptive, full-word names avoiding abbreviations.

**Evidence:** 393 fields analyzed (166 airbnb + 227 thekelsey). 100% PHP fields use snake_case. 100% of GraphQL-exposed fields (192 in airbnb) use camelCase via custom `graphql_field_name` properties.

## PHP Field Name Convention: snake_case

WordPress ACF field names in PHP contexts use lowercase snake_case (`word_word_word`) matching WordPress core database and function naming patterns. This convention applies to the `name` property in ACF field definitions, which becomes the meta key in the WordPress postmeta table. All analyzed projects follow this pattern without exception.

**Standard Pattern:**

```php
// TheKelsey ACF JSON (group_5f91b18180b23.json)
{
    "key": "field_5f91b1c904c83",
    "label": "TA Title",
    "name": "ta_title",  // snake_case
    "type": "text"
}
```

**Rationale:** WordPress stores custom fields as postmeta with meta_key matching the ACF field name. snake_case ensures compatibility with WordPress core, database conventions, and ACF's `get_field()` function expectations.

## Descriptive Full-Word Names (No Abbreviations)

Airbnb field names use complete, descriptive words avoiding abbreviations, improving code readability and reducing ambiguity. Field names like `municipality_id`, `economic_impact`, `gdp_contribution`, and `hosting_not_primary_occupation` communicate intent without requiring context. This pattern trades brevity for clarity.

**Airbnb Examples (Complete Words):**

```php
municipality_id                    // NOT muni_id
economic_impact                    // NOT econ_impact
gdp_contribution                   // Acceptable: GDP is standard acronym
total_tax_generated                // NOT tot_tax_gen
hosting_not_primary_occupation     // NOT hosting_not_primary_occ
stat_suffix_full_form              // Full words, even if long
apply_to_descendants               // NOT apply_to_desc
inherit_from_parent                // NOT inherit_from_par
```

**Why This Works:** Field names appear in code frequently. `get_field('municipality_id')` is self-documenting. `get_field('muni_id')` requires developer to remember what "muni" means.

## Context Prefixes for Template-Specific Fields (TheKelsey Pattern)

TheKelsey prefixes field names with abbreviated context identifiers when field groups attach to specific page templates. The "Text and Aside" template uses `ta_` prefix for all fields (`ta_title`, `ta_text`, `ta_link`, `ta_aside_image`), preventing naming conflicts when multiple templates define similar field concepts like "title" or "text".

**Context Prefix Pattern:**

```php
// Text and Aside template (group_5f91b18180b23.json)
{
    "fields": [
        { "name": "ta_title" },         // TA = Text and Aside
        { "name": "ta_text" },
        { "name": "ta_link" },
        { "name": "ta_aside_image" },
        { "name": "ta_aside_text" }
    ],
    "location": [
        [{
            "param": "post_template",
            "operator": "==",
            "value": "views/template-about.blade.php"
        }]
    ]
}
```

**When to Use Prefixes:**

- ✅ Template-specific fields that might conflict with global fields
- ✅ Multiple templates in same post type with overlapping field concepts
- ✅ Options pages with multiple sections (e.g., `social_facebook_url`, `social_twitter_url`)

**When to Avoid Prefixes:**

- ❌ Custom post types (post type name provides context: `event_date` not needed, just `date`)
- ❌ Single-use field groups with no conflict risk
- ❌ Block-based fields (block name provides context)

## Service/Integration Prefixes

Both projects prefix field names with third-party service identifiers when fields store service-specific data. Examples include `funraise_form_id` (fundraising platform), `vimeo_id` (video hosting), `flourish_` (data visualization). This pattern clarifies field purpose and prevents conflicts with generic names like `form_id` or `video_id`.

**Service Prefix Examples:**

```php
// TheKelsey examples
funraise_form_id          // Funraise fundraising platform
vimeo_id                  // Vimeo video ID
vimeo_url                 // Vimeo video URL

// Airbnb examples (inferred from patterns)
municipality_id           // Internal service/taxonomy
```

**Pattern:** `{service}_{descriptor}` where service is lowercase, no spaces, and descriptor uses snake_case.

## GraphQL Field Naming: camelCase

Headless WordPress with WPGraphQL requires ACF fields to expose GraphQL-friendly names following JavaScript conventions. ACF's `graphql_field_name` property overrides default snake_case with camelCase, aligning with GraphQL specification and JavaScript best practices. Airbnb implements this pattern consistently across all 192 GraphQL-exposed fields.

**Dual Naming Pattern:**

```json
// ACF JSON field definition (airbnb)
{
    "key": "field_123",
    "label": "Apply to Descendants",
    "name": "apply_to_descendants",          // PHP: snake_case
    "type": "true_false",
    "show_in_graphql": 1,
    "graphql_field_name": "applyToDescendants"  // GraphQL: camelCase
}
```

**PHP Usage:**

```php
$apply = get_field('apply_to_descendants', $post_id);  // snake_case
```

**GraphQL Query:**

```graphql
query {
  post(id: "123") {
    statBlock {
      applyToDescendants  # camelCase
    }
  }
}
```

## Snake_case to CamelCase Transformation Rules

ACF fields exposed to GraphQL convert snake_case PHP names to camelCase programmatically. First word remains lowercase, subsequent words capitalize first letter. Underscores are removed. Airbnb applies this transformation manually via `graphql_field_name` property rather than relying on automatic conversion for precise control.

**Transformation Examples:**

```
PHP (snake_case)           →  GraphQL (camelCase)
apply_to_descendants       →  applyToDescendants
inherit_from_parent        →  inheritFromParent
economic_impact            →  economicImpact
gdp_contribution           →  gdpContribution
total_tax_generated        →  totalTaxGenerated
hosting_not_primary_occ... →  hostingNotPrimaryOccupation
stat_suffix_full_form      →  quantityFullForm  (semantic rename)
additional_stat_suffix     →  additionalSymbol   (semantic rename)
```

**Note:** Airbnb occasionally deviates from pure snake_case→camelCase for semantic clarity (e.g., `stat_suffix` → `quantity` rather than `statSuffix`).

## Semantic Renaming for GraphQL APIs

Headless architectures enable field name improvements at the API boundary without breaking backend code. Airbnb renames several PHP fields for clearer GraphQL semantics: `stat_suffix` becomes `quantity`, `additional_stat_suffix` becomes `additionalSymbol`. PHP code continues using original snake_case names while JavaScript clients consume improved camelCase names.

**Semantic Rename Examples:**

```json
// Before: Generic name
{
    "name": "stat_suffix",
    "graphql_field_name": "statSuffix"  // Direct translation
}

// After: Semantic name
{
    "name": "stat_suffix",              // PHP unchanged
    "graphql_field_name": "quantity"    // GraphQL improved
}

// Before: Verbose name
{
    "name": "stat_suffix_full_form",
    "graphql_field_name": "statSuffixFullForm"  // Direct translation
}

// After: Semantic name
{
    "name": "stat_suffix_full_form",            // PHP unchanged
    "graphql_field_name": "quantityFullForm"    // GraphQL improved
}

// Before: Technical name
{
    "name": "additional_stat_suffix",
    "graphql_field_name": "additionalStatSuffix"  // Direct translation
}

// After: Semantic name
{
    "name": "additional_stat_suffix",             // PHP unchanged
    "graphql_field_name": "additionalSymbol"      // GraphQL improved
}
```

**Why This Works:** Decouples database schema (PHP field names) from API design (GraphQL field names). Backend can maintain legacy naming while frontend consumes clean, modern API.

## Field Label vs Field Name

ACF separates human-readable labels from machine-readable names. Labels appear in WordPress admin and can include spaces, punctuation, and mixed case. Names are code identifiers following strict conventions. Developers must configure both properties appropriately for their contexts.

**Label vs Name Examples:**

```json
{
    "label": "Apply to Descendants",        // Human-readable (UI)
    "name": "apply_to_descendants",         // Machine-readable (PHP)
    "graphql_field_name": "applyToDescendants"  // API-readable (GraphQL)
}

{
    "label": "TA Title",                    // Human-readable (abbreviation OK)
    "name": "ta_title",                     // Machine-readable
}

{
    "label": "Funraise Form ID",            // Human-readable (proper case)
    "name": "funraise_form_id",             // Machine-readable (lowercase)
}
```

**Best Practice:** Labels can be verbose and descriptive for editor clarity. Names should be concise but unambiguous for code readability.

## Avoiding Name Collisions

ACF field names must be unique within their scope but can collide across different field groups if location rules overlap. Template-specific prefixes (TheKelsey pattern) prevent collisions. Block-specific fields (Airbnb pattern) naturally avoid collisions since block names provide namespacing. Global fields shared across post types require careful naming to prevent conflicts.

**Collision Scenarios:**

```php
// ❌ COLLISION RISK: Two templates, generic names
// Template A
{ "name": "title" }    // Conflicts with Template B

// Template B
{ "name": "title" }    // Conflicts with Template A

// ✅ COLLISION AVOIDED: Prefixed names
// Template A (Text and Aside)
{ "name": "ta_title" }

// Template B (Campaign Highlight)
{ "name": "ch_title" }
```

**Safe Scopes (No Prefix Needed):**

- Custom Post Types (post type name provides implicit namespace)
- ACF Blocks (block name provides implicit namespace)
- Single-use templates (no conflict possible)

## Reserved Name Avoidance

ACF field names must avoid WordPress reserved postmeta keys and common global variable names. Names like `post_title`, `post_content`, `user_id`, `term_id`, or `data` risk conflicts with WordPress core or plugins. All analyzed projects avoid these collisions.

**Reserved Names to Avoid:**

```php
// ❌ WordPress Core Conflicts
post_title, post_content, post_excerpt, post_status
ID, post_id, page_id, attachment_id
user_id, user_login, user_email
term_id, taxonomy
menu, sidebar, widget

// ❌ Common Global Conflicts
data, value, content, text (too generic)
name, type, status (too generic)
```

**Safe Alternative Patterns:**

```php
// ✅ Contextualized Names
event_title         (not post_title)
event_description   (not post_content)
author_bio          (not user_bio)
feature_text        (not text)
module_type         (not type)
```

## Group Field Naming

ACF group fields organize related sub-fields under a parent namespace. Group names should describe the conceptual container, and sub-field names can be shorter since the group provides context. Airbnb uses groups extensively (`metrics`, `economic_impact`, `host_metrics`) for nested data structures.

**Group Field Pattern:**

```json
{
    "name": "metrics",        // Group name (singular noun)
    "type": "group",
    "sub_fields": [
        {
            "name": "economic_impact",  // No prefix needed, group provides context
            "type": "group",
            "sub_fields": [
                { "name": "gdp_contribution" },  // Not metrics_gdp_contribution
                { "name": "hide" },              // Short name OK in nested context
                { "name": "apply_to_descendants" }
            ]
        },
        {
            "name": "host_metrics",
            "type": "group",
            "sub_fields": [
                { "name": "hosting_not_primary_occupation" },
                { "name": "hide" }
            ]
        }
    ]
}
```

**PHP Access:**

```php
$gdp = get_field('metrics')['economic_impact']['gdp_contribution'];
// OR with ACF sub-field syntax
$gdp = get_field('metrics_economic_impact_gdp_contribution');
```

**GraphQL Access:**

```graphql
query {
  post(id: "123") {
    statBlock {
      metrics {
        economicImpact {
          gdpContribution
        }
      }
    }
  }
}
```

## Repeater and Flexible Content Field Naming

Repeater field names are typically plural nouns indicating collections (`logos`, `slides`, `testimonials`). Sub-fields within repeaters use singular nouns or descriptive names without repeating the parent field name. Flexible Content field names describe the layout concept, and sub-layouts use singular nouns.

**Repeater Pattern:**

```json
{
    "name": "logos",          // Plural: Collection of logos
    "type": "repeater",
    "sub_fields": [
        { "name": "logo" },   // Singular: One logo image
        { "name": "link" }    // Singular: One link URL
    ]
}
```

**Access Pattern:**

```php
$logos = get_field('logos');  // Returns array
foreach ($logos as $logo_item) {
    $img = $logo_item['logo'];
    $url = $logo_item['link'];
}
```

**Flexible Content Pattern:**

```json
{
    "name": "page_sections",    // Plural: Collection of sections
    "type": "flexible_content",
    "layouts": [
        {
            "name": "hero_section",  // Singular: One hero layout
            "sub_fields": [...]
        },
        {
            "name": "content_section",  // Singular: One content layout
            "sub_fields": [...]
        }
    ]
}
```

## Boolean Field Naming

True/False (boolean) fields use positive phrasing with verbs or adjectives: `show_announcement`, `apply_to_descendants`, `inherit_from_parent`, `hide`. Airbnb heavily uses boolean fields (61 instances) for conditional logic, favoring explicit names over negative phrasing.

**Boolean Naming Patterns:**

```php
// ✅ Positive phrasing (preferred)
show_announcement      // if (show_announcement) display it
apply_to_descendants   // if (apply_to_descendants) recurse
inherit_from_parent    // if (inherit_from_parent) use parent value
hide                   // if (hide) hide element (short context-dependent name)

// ❌ Negative phrasing (avoid - confusing logic)
hide_announcement      // if (!hide_announcement) display - double negative
dont_apply             // if (!dont_apply) apply - double negative
```

**GraphQL Boolean Names:**

```
show_announcement  →  showAnnouncement
apply_to_descendants  →  applyToDescendants
inherit_from_parent  →  inheritFromParent
```

## Cross-Architecture Summary

Traditional WordPress sites use snake_case exclusively, while headless WordPress with GraphQL maintains snake_case for PHP but adds camelCase for GraphQL. Both architectures prioritize descriptive full-word names, avoid abbreviations, and use prefixes strategically to prevent naming collisions. Field names serve as long-term API contracts requiring careful consideration.

**PHP-Only Architecture (TheKelsey):**

- Field name = final identifier
- snake_case throughout codebase
- Context prefixes for template-specific fields
- Service prefixes for integrations

**Headless/GraphQL Architecture (Airbnb):**

- Field name = PHP identifier (snake_case)
- GraphQL field name = API identifier (camelCase)
- Semantic renaming opportunities at API boundary
- No prefixes (blocks provide namespacing)

## Common Pitfalls

Inconsistent naming conventions across field groups create maintenance burden. Abbreviated field names reduce code readability. Generic names without context cause collisions. Missing GraphQL field names in headless sites result in snake_case leaking into JavaScript code. All these pitfalls are avoidable through upfront naming strategy.

**Anti-Patterns:**

- ❌ Mixing snake_case and camelCase in PHP field names
- ❌ Using abbreviations (`muni_id` instead of `municipality_id`)
- ❌ Generic names without context (`title`, `text`, `image`)
- ❌ Reserved name usage (`post_title`, `data`, `content`)
- ❌ GraphQL fields without explicit `graphql_field_name` (relies on auto-conversion)
- ❌ Negative boolean phrasing (`dont_show`, `hide_element`)

## Related Patterns

- **ACF JSON Storage** (field definitions in version control)
- **ACF + GraphQL Integration** (WPGraphQL exposure)
- **ACF Group Fields** (nested organization)
- **ACF Location Rules** (field group scoping)

## References

- Airbnb ACF JSON: `plugins/airbnb-policy-blocks/acf-json/group_*.json` (136 files)
- TheKelsey ACF JSON: `mu-plugins/thekelsey-custom/acf-json/group_*.json` (29 files)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 7: Field Naming Conventions)
