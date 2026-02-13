# ACF + WPGraphQL Integration

---
title: "ACF + WPGraphQL Integration"
category: "wordpress-acf"
subcategory: "graphql-api"
tags: ["acf", "wpgraphql", "graphql", "headless", "api", "camelcase"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WPGraphQL for ACF exposes Advanced Custom Fields through GraphQL APIs, enabling headless WordPress architectures where frontend applications consume ACF data via GraphQL queries. Airbnb demonstrates complete integration with 192 GraphQL-enabled fields (100% of field groups), custom camelCase field names, and structured block data queries. TheKelsey uses traditional PHP rendering without GraphQL (0% integration).

**Evidence:** 192 fields with `show_in_graphql: 1` in airbnb. 0 fields with GraphQL in thekelsey. 100% confidence pattern for headless architectures.

## Enabling GraphQL for Field Groups

ACF field groups expose to GraphQL via `show_in_graphql` property set to `1` (true). Field groups without this property remain hidden from GraphQL schema. Additionally, `graphql_field_name` defines the field group's GraphQL query root, typically matching field group title in camelCase.

**Field Group GraphQL Configuration:**

```json
{
    "key": "group_680ad6fe615b8",
    "title": "Logo Cloud Block",
    "fields": [...],
    "show_in_graphql": 1,
    "graphql_field_name": "logoCloudBlock",
    "map_graphql_types_from_location_rules": 0,
    "graphql_types": ""
}
```

**Result:** Field group appears in GraphQL schema as `logoCloudBlock` field on relevant post types or blocks.

## Enabling GraphQL for Individual Fields

Each field within GraphQL-enabled field groups requires its own `show_in_graphql: 1` property. Fields without this property remain hidden even if parent field group is exposed. This granular control allows selective field exposure for security or API design.

**Field-Level GraphQL Configuration:**

```json
{
    "key": "field_680ad6fe88bfb",
    "label": "Logos",
    "name": "logos",
    "type": "repeater",
    "show_in_graphql": 1,
    "graphql_field_name": "logos",
    "graphql_non_null": 0,
    "sub_fields": [
        {
            "key": "field_680ad71788bfc",
            "label": "Logo",
            "name": "logo",
            "type": "image",
            "show_in_graphql": 1,
            "graphql_field_name": "logo"
        },
        {
            "key": "field_680ad74888bfd",
            "label": "Link (optional)",
            "name": "link",
            "type": "url",
            "show_in_graphql": 1,
            "graphql_field_name": "link"
        }
    ]
}
```

**Granular Control Example:**

```json
{
    "name": "internal_notes",
    "type": "textarea",
    "show_in_graphql": 0  // Hidden from API (admin-only field)
}
```

## camelCase Field Naming Convention

GraphQL follows JavaScript naming conventions using camelCase. ACF fields use snake_case for PHP compatibility. WPGraphQL for ACF bridges this via `graphql_field_name` property, allowing explicit camelCase naming while maintaining snake_case PHP field names.

**Dual Naming Pattern:**

```json
{
    "name": "apply_to_descendants",        // PHP: snake_case
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
{
  post(id: "123") {
    statBlock {
      applyToDescendants  # camelCase
    }
  }
}
```

**Convention:** First word lowercase, subsequent words capitalize first letter, remove underscores.

## Semantic Field Renaming for APIs

Headless architectures enable field name improvements at the API boundary without changing backend PHP code. Airbnb renames several fields for clearer GraphQL semantics: `stat_suffix` becomes `quantity`, `additional_stat_suffix` becomes `additionalSymbol`. PHP uses original names; JavaScript clients use improved names.

**Semantic Rename Examples:**

```json
// Generic PHP name → Semantic GraphQL name
{
    "name": "stat_suffix",
    "graphql_field_name": "quantity"
}

// Verbose PHP name → Concise GraphQL name
{
    "name": "stat_suffix_full_form",
    "graphql_field_name": "quantityFullForm"
}

// Technical PHP name → Descriptive GraphQL name
{
    "name": "additional_stat_suffix",
    "graphql_field_name": "additionalSymbol"
}
```

**Benefit:** Decouples database schema from API design. Backend maintains stability, frontend consumes modern API.

## Block-Based GraphQL Queries

ACF fields attached to Gutenberg blocks via location rules expose as block attributes in GraphQL. WPGraphQL queries blocks as arrays with ACF fields nested within each block instance. Airbnb uses 15 custom ACF blocks all exposed to GraphQL.

**Block Query Pattern:**

```graphql
query GetPageBlocks {
  page(id: "123") {
    blocks {
      name
      ... on CreateBlockLogoCloudBlock {
        attributes {
          data {
            logos {
              logo {
                sourceUrl
                altText
              }
              link
            }
          }
        }
      }
    }
  }
}
```

**Response Structure:**

```json
{
  "data": {
    "page": {
      "blocks": [
        {
          "name": "create-block/logo-cloud-block",
          "attributes": {
            "data": {
              "logos": [
                {
                  "logo": {
                    "sourceUrl": "https://example.com/logo1.png",
                    "altText": "Company A"
                  },
                  "link": "https://companya.com"
                },
                {
                  "logo": {
                    "sourceUrl": "https://example.com/logo2.png",
                    "altText": "Company B"
                  },
                  "link": null
                }
              ]
            }
          }
        }
      ]
    }
  }
}
```

## Post-Level ACF Queries

ACF fields attached to post types via location rules expose at post level in GraphQL. Field groups become nested objects under the post, with field group's `graphql_field_name` as the object key.

**Post-Level Query:**

```graphql
query GetPost {
  post(id: "123") {
    id
    title
    content
    statBlock {  # ACF field group
      metrics {
        economicImpact {
          gdpContribution
          hide
        }
      }
    }
  }
}
```

**PHP Equivalent:**

```php
$post_id = 123;
$metrics = get_field('metrics', $post_id);
$gdp = $metrics['economic_impact']['gdp_contribution'];
```

## Options Page GraphQL Exposure

ACF options pages expose at GraphQL root query level, accessible without post context. Options page fields become top-level queries, ideal for site-wide settings consumed by frontend applications.

**Options Page Query:**

```graphql
query GetSiteSettings {
  optionsSocialMedia {
    facebookUrl
    twitterUrl
    instagramUrl
  }

  optionsGlobalModules {
    globalCta {
      title
      buttonText
      link
    }
  }
}
```

**PHP Equivalent:**

```php
$facebook = get_field('facebook_url', 'option');
$twitter = get_field('twitter_url', 'option');
$instagram = get_field('instagram_url', 'option');
```

**Configuration:**

```json
{
    "title": "Social Media Options",
    "show_in_graphql": 1,
    "graphql_field_name": "optionsSocialMedia",
    "location": [
        [{
            "param": "options_page",
            "operator": "==",
            "value": "social-media"
        }]
    ]
}
```

## Image Field Return Formats

ACF image fields support three return formats: Image ID (integer), Image URL (string), or Image Object (array). For GraphQL APIs, Image ID format is optimal, as WPGraphQL resolves media items to full MediaItem objects with all metadata (URL, alt text, dimensions, srcset).

**Image ID Return Format (GraphQL-Optimized):**

```json
{
    "name": "logo",
    "type": "image",
    "return_format": "id",  // Returns integer, WPGraphQL resolves to MediaItem
    "show_in_graphql": 1,
    "graphql_field_name": "logo"
}
```

**GraphQL Query (Image as MediaItem):**

```graphql
{
  post(id: "123") {
    logoCloudBlock {
      logos {
        logo {
          id
          sourceUrl
          altText
          mediaDetails {
            width
            height
          }
          srcSet
        }
      }
    }
  }
}
```

**Airbnb Pattern:** 85% of image fields use `return_format: "id"` for GraphQL efficiency. Traditional PHP sites use `return_format: "array"` for direct access to image metadata.

## Repeater Fields as GraphQL Lists

ACF repeater fields expose as GraphQL list types (arrays) with strongly-typed sub-field structure. JavaScript clients iterate arrays with native `.map()` or `.forEach()`, treating repeater data as standard JSON arrays.

**Repeater GraphQL Schema:**

```graphql
type LogoCloudBlock {
  logos: [Logo]  # List of Logo objects
}

type Logo {
  logo: MediaItem
  link: String
}
```

**Client-Side Usage (React Example):**

```javascript
const LogoCloud = ({ data }) => {
  const logos = data.logoCloudBlock.logos;

  return (
    <div className="logo-grid">
      {logos.map((item, index) => (
        <div key={index} className="logo-item">
          {item.link ? (
            <a href={item.link} target="_blank" rel="noopener noreferrer">
              <img src={item.logo.sourceUrl} alt={item.logo.altText} />
            </a>
          ) : (
            <img src={item.logo.sourceUrl} alt={item.logo.altText} />
          )}
        </div>
      ))}
    </div>
  );
};
```

## Group Fields as Nested Objects

ACF group fields expose as nested objects in GraphQL, mirroring JSON structure. Multi-level group nesting translates directly to GraphQL object nesting, creating clean hierarchical queries.

**Group Field Schema:**

```graphql
type StatBlock {
  metrics: Metrics
}

type Metrics {
  economicImpact: EconomicImpact
  hostMetrics: HostMetrics
}

type EconomicImpact {
  gdpContribution: String
  hide: Boolean
  applyToDescendants: Boolean
}
```

**GraphQL Query (Nested Groups):**

```graphql
{
  post(id: "123") {
    statBlock {
      metrics {
        economicImpact {
          gdpContribution
          hide
        }
        hostMetrics {
          hostingNotPrimaryOccupation
        }
      }
    }
  }
}
```

## Conditional Logic and GraphQL

ACF conditional logic (show/hide fields based on other field values) is editor-side only and does not affect GraphQL schema. Fields with conditional logic still expose to GraphQL regardless of visibility state. Frontend applications receive all fields and must implement their own conditional rendering if needed.

**ACF Conditional Logic:**

```json
{
    "name": "show_announcement",
    "type": "true_false"
},
{
    "name": "announcement_text",
    "type": "textarea",
    "conditional_logic": [
        [{
            "field": "field_show_announcement",
            "operator": "==",
            "value": "1"
        }]
    ],
    "show_in_graphql": 1
}
```

**GraphQL Schema (Both Fields Present):**

```graphql
type StatBlock {
  showAnnouncement: Boolean
  announcementText: String  # Always present, even if hidden in editor
}
```

**Frontend Conditional Rendering:**

```javascript
const Announcement = ({ data }) => {
  const { showAnnouncement, announcementText } = data.statBlock;

  if (!showAnnouncement) return null;  // Frontend conditional logic

  return <div className="announcement">{announcementText}</div>;
};
```

## graphql_non_null Property

ACF fields support `graphql_non_null` property marking fields as required in GraphQL schema (cannot return null). This provides type safety for frontend applications, ensuring critical fields always have values.

**Non-Null Field:**

```json
{
    "name": "title",
    "type": "text",
    "required": 1,  // ACF editor validation
    "show_in_graphql": 1,
    "graphql_non_null": 1  // GraphQL schema constraint
}
```

**GraphQL Schema:**

```graphql
type HeroSection {
  title: String!  # Exclamation mark = non-null
  subtitle: String
}
```

**TypeScript Type Generation:**

```typescript
interface HeroSection {
  title: string;      // Required (non-null)
  subtitle?: string;  // Optional (nullable)
}
```

**Recommendation:** Use sparingly. Only mark fields as non-null if they are truly always present and non-empty. Null fields are safer default.

## Flexible Content in GraphQL

ACF Flexible Content fields expose as GraphQL union types, where each layout becomes a distinct type. Frontend applications query all possible layouts with inline fragments, receiving only the selected layout's data.

**Flexible Content Pattern (Hypothetical):**

```json
{
    "name": "page_sections",
    "type": "flexible_content",
    "show_in_graphql": 1,
    "graphql_field_name": "pageSections",
    "layouts": [
        {
            "name": "hero_section",
            "show_in_graphql": 1,
            "graphql_field_name": "heroSection",
            "sub_fields": [...]
        },
        {
            "name": "content_section",
            "show_in_graphql": 1,
            "graphql_field_name": "contentSection",
            "sub_fields": [...]
        }
    ]
}
```

**GraphQL Query (Union Types):**

```graphql
{
  page(id: "123") {
    pageSections {
      __typename
      ... on Page_Pagesections_PageSections_HeroSection {
        title
        backgroundImage {
          sourceUrl
        }
      }
      ... on Page_Pagesections_PageSections_ContentSection {
        text
      }
    }
  }
}
```

## Clone Fields and GraphQL

ACF clone fields (DRY field definitions) expose to GraphQL based on their `show_in_graphql` property in the original field definition. Cloned fields inherit GraphQL configuration from source, maintaining consistency across field groups.

**Clone Field GraphQL:**

```json
{
    "name": "seo_settings",
    "type": "clone",
    "clone": ["group_seo_fields"],  // References another field group
    "show_in_graphql": 1
}
```

**Result:** All fields from `group_seo_fields` appear in GraphQL schema at clone location, with their original GraphQL field names.

## Performance Considerations

GraphQL queries fetch only requested fields, avoiding over-fetching inherent in REST APIs. However, deeply nested queries with repeaters and image fields can trigger N+1 query problems. WPGraphQL implements DataLoader pattern for batching, but complex ACF structures with multiple repeaters require query optimization.

**Optimized Query (Specific Fields):**

```graphql
{
  posts {
    nodes {
      title
      featuredImage {
        node {
          sourceUrl
        }
      }
    }
  }
}
```

**Avoid Over-Nesting:**

```graphql
# ❌ BAD: 3 levels of repeaters
{
  posts {
    nodes {
      sections {  # Repeater
        items {   # Nested repeater
          subitems {  # Nested nested repeater (slow)
            data
          }
        }
      }
    }
  }
}
```

**Recommendation:** Limit nesting to 2 levels. Use pagination for large repeater datasets.

## Security: Hiding Sensitive Fields

Not all ACF fields should expose to public GraphQL API. Internal notes, admin-only flags, and sensitive configuration must set `show_in_graphql: 0` to remain hidden. Airbnb demonstrates selective exposure, keeping private fields in WordPress admin only.

**Public vs Private Fields:**

```json
// ✅ Public field (API-exposed)
{
    "name": "team_member_name",
    "type": "text",
    "show_in_graphql": 1
}

// ✅ Private field (admin-only)
{
    "name": "internal_notes",
    "type": "textarea",
    "show_in_graphql": 0
}

// ✅ Private field (no GraphQL properties)
{
    "name": "admin_flags",
    "type": "checkbox"
    // show_in_graphql omitted = defaults to 0 (hidden)
}
```

## Common Pitfalls

Missing `show_in_graphql: 1` on field groups or individual fields causes unexpected null results. Forgetting `graphql_field_name` generates auto-names that may not match expected camelCase conventions. Using wrong image return format (`array` instead of `id`) prevents MediaItem resolution. Exposing sensitive fields to public API creates security risks.

**Anti-Patterns:**

```json
// ❌ Field group exposed, but fields not exposed (all fields return null)
{
    "show_in_graphql": 1,
    "fields": [
        {
            "name": "title",
            "show_in_graphql": 0  // Forgot to enable
        }
    ]
}

// ❌ Missing custom GraphQL field name (auto-generated may not match expected)
{
    "name": "stat_suffix_full_form",
    "show_in_graphql": 1
    // graphql_field_name auto-generated as "statSuffixFullForm" - may not match frontend expectations
}

// ❌ Wrong image return format for GraphQL
{
    "name": "logo",
    "type": "image",
    "return_format": "array",  // Should be "id" for GraphQL
    "show_in_graphql": 1
}
```

## Related Patterns

- **ACF Field Naming Conventions** (snake_case PHP, camelCase GraphQL)
- **ACF JSON Storage** (field definitions in version control)
- **ACF Blocks** (Gutenberg blocks with GraphQL-exposed data)
- **WPGraphQL** (base GraphQL layer for WordPress)
- **Headless WordPress Architecture** (decoupled frontend/backend)

## References

- Airbnb: `plugins/airbnb-policy-blocks/acf-json/` (192 GraphQL-enabled fields across 136 JSON files)
- WPGraphQL for ACF: [Documentation](https://www.wpgraphql.com/acf/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 4: GraphQL Integration, Section 13: WPGraphQL Integration)
