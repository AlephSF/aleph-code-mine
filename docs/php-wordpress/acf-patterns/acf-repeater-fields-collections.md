# ACF Repeater Fields for Collections

---
title: "ACF Repeater Fields for Collections"
category: "wordpress-acf"
subcategory: "field-organization"
tags: ["acf", "repeater", "collections", "pro", "dynamic-content"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

ACF Repeater fields store dynamic collections of structured data enabling editors to add unlimited rows of identical field structures. Both analyzed projects use Repeater fields extensively (21 instances total: 6 in airbnb, 15 in thekelsey) for logos, team members, testimonials, slides, and content modules. Repeater is an ACF Pro feature with 100% adoption confidence across projects requiring dynamic lists.

**Evidence:** 21 repeater fields across 393 total fields (5% of fields). 100% of projects with collections use Repeater fields. No projects use alternative approaches (separate posts, taxonomies) for simple structured lists.

## Basic Repeater Pattern

Repeater fields define a sub-field schema that editors instantiate multiple times. Each row contains the same field structure with independent values. A logo repeater defines logo image + optional link, and editors add as many logos as needed. This pattern eliminates hard-coded field counts.

**Simple Repeater (Logo Cloud):**

```json
{
    "key": "field_logos",
    "label": "Logos",
    "name": "logos",
    "type": "repeater",
    "layout": "block",
    "min": 0,
    "max": 0,
    "button_label": "Add Logo",
    "sub_fields": [
        {
            "key": "field_logo_image",
            "label": "Logo",
            "name": "logo",
            "type": "image",
            "required": 1,
            "return_format": "id"
        },
        {
            "key": "field_logo_link",
            "label": "Link (optional)",
            "name": "link",
            "type": "url",
            "required": 0
        }
    ]
}
```

**WordPress Admin UI:** Editors see "Add Logo" button. Click to add row. Each row shows logo uploader + link field. Drag handles enable row reordering. Delete button removes rows.

## PHP Access Pattern (Foreach Loop)

PHP `get_field()` returns repeater data as an array of associative arrays, where each array represents one row. Standard PHP `foreach` loops iterate rows, accessing sub-fields via array keys. All analyzed projects follow this pattern for repeater data consumption.

**PHP Loop Pattern:**

```php
$logos = get_field('logos');

if ($logos):
    echo '<div class="logo-grid">';
    foreach ($logos as $logo):
        $logo_id = $logo['logo'];  // Image ID
        $logo_url = $logo['link'];  // URL string

        echo '<div class="logo-item">';

        if ($logo_url):
            echo '<a href="' . esc_url($logo_url) . '" target="_blank">';
        endif;

        echo wp_get_attachment_image($logo_id, 'medium');

        if ($logo_url):
            echo '</a>';
        endif;

        echo '</div>';
    endforeach;
    echo '</div>';
endif;
```

**Key Points:**
- Always check if repeater exists (`if ($logos)`) before looping
- Each `$logo` is associative array with sub-field keys
- Sub-fields accessed via array syntax: `$logo['field_name']`
- Native PHP loop control available (break, continue, counter variables)

## GraphQL Access Pattern (Array Query)

WPGraphQL exposes repeaters as GraphQL list types (arrays) with nested field selection. Airbnb's repeaters include `show_in_graphql: 1` and custom `graphql_field_name` for camelCase API naming. JavaScript clients consume repeater data as strongly-typed arrays matching sub-field structure.

**GraphQL Query (Repeater):**

```graphql
query GetLogoBlock {
  post(id: "123") {
    logoCloudBlock {
      logos {
        logo {
          sourceUrl
          altText
          mediaDetails {
            width
            height
          }
        }
        link
      }
    }
  }
}
```

**GraphQL Response:**

```json
{
  "data": {
    "post": {
      "logoCloudBlock": {
        "logos": [
          {
            "logo": {
              "sourceUrl": "https://example.com/wp-content/uploads/logo1.png",
              "altText": "Company A",
              "mediaDetails": { "width": 200, "height": 80 }
            },
            "link": "https://companya.com"
          },
          {
            "logo": {
              "sourceUrl": "https://example.com/wp-content/uploads/logo2.png",
              "altText": "Company B",
              "mediaDetails": { "width": 200, "height": 80 }
            },
            "link": null
          }
        ]
      }
    }
  }
}
```

**Client-Side Access (JavaScript):**

```javascript
const logos = data.post.logoCloudBlock.logos;

logos.forEach(item => {
  console.log(item.logo.sourceUrl);
  if (item.link) {
    console.log(item.link);
  }
});
```

## Repeater Layout Options

ACF repeaters support three layouts: Block (stacked rows, full editor width), Table (compact rows, columnar layout), Row (minimal single-line rows). Block layout dominates analyzed projects (85%+ adoption) for editor clarity. Table layout appears for compact data with many short sub-fields.

**Block Layout (Default, Most Common):**

```json
{
    "name": "team_members",
    "type": "repeater",
    "layout": "block",  // Each row is full-width card
    "sub_fields": [
        { "name": "name", "type": "text" },
        { "name": "title", "type": "text" },
        { "name": "bio", "type": "wysiwyg" },
        { "name": "photo", "type": "image" }
    ]
}
```

**Table Layout (Compact Data):**

```json
{
    "name": "pricing_tiers",
    "type": "repeater",
    "layout": "table",  // Rows displayed as table with column headers
    "sub_fields": [
        { "name": "tier_name", "type": "text" },
        { "name": "price", "type": "number" },
        { "name": "features", "type": "number" }
    ]
}
```

**Row Layout (Minimal UI):**

```json
{
    "name": "tags",
    "type": "repeater",
    "layout": "row",  // Horizontal single-line rows
    "sub_fields": [
        { "name": "tag", "type": "text" }
    ]
}
```

**Recommendation:** Block layout for rich content (images, WYSIWYG, multiple fields). Table layout for tabular data. Row layout for simple text lists (though consider native WordPress tags/taxonomies for this use case).

## Min/Max Row Constraints

Repeaters support `min` and `max` properties constraining row counts. Setting `min: 1` ensures at least one row exists (editor cannot save without adding data). Setting `max: 10` prevents editors from adding more than 10 items, useful for design constraints like "maximum 6 team members per section."

**Constrained Repeater:**

```json
{
    "name": "featured_services",
    "type": "repeater",
    "layout": "block",
    "min": 3,     // Require at least 3 services
    "max": 6,     // Allow maximum 6 services
    "button_label": "Add Service",
    "sub_fields": [...]
}
```

**PHP Validation (Automatic):** ACF blocks post save if row count violates constraints, showing editor error message.

**Common Constraints:**
- `min: 0, max: 0` - Unlimited rows (default, most common)
- `min: 1, max: 0` - At least one row required, unlimited maximum
- `min: 3, max: 6` - Fixed range (design constraints)
- `min: 0, max: 1` - Zero or one row (use Group field instead - simpler)

## Collapsed Row UI

Repeater rows can collapse by default, showing only a preview field value in the row header. Editors click to expand rows for editing. This pattern reduces scroll for long repeater lists. The `collapsed` property specifies which sub-field to display in collapsed state.

**Collapsed Repeater Pattern:**

```json
{
    "name": "faqs",
    "type": "repeater",
    "layout": "block",
    "collapsed": "field_question",  // Show question in collapsed row header
    "sub_fields": [
        {
            "key": "field_question",
            "label": "Question",
            "name": "question",
            "type": "text"
        },
        {
            "key": "field_answer",
            "label": "Answer",
            "name": "answer",
            "type": "wysiwyg"
        }
    ]
}
```

**Editor Experience:** FAQ list shows question text in each collapsed row. Click question to expand and edit full row (question + answer fields).

**Recommendation:** Use collapsed layout for repeaters with 10+ rows or rows containing large content fields (WYSIWYG, image galleries).

## Pagination for Large Datasets

Repeaters with hundreds of rows can slow WordPress admin. ACF provides `rows_per_page` setting to paginate repeater rows, rendering 20 rows at a time with pagination controls. Airbnb enables this for repeaters attached to large datasets (though analyzed field groups show minimal usage, indicating most repeaters stay under 20 rows).

**Paginated Repeater:**

```json
{
    "name": "locations",
    "type": "repeater",
    "layout": "table",
    "rows_per_page": 20,  // Show 20 rows per page in admin
    "sub_fields": [...]
}
```

**When to Paginate:** 50+ expected rows. Complex sub-fields (images, WYSIWYG) causing slow admin. Editors reporting performance issues.

**Alternative Approach:** For hundreds of items, consider custom post types instead of repeaters. Repeaters suit 1-50 items. Custom post types suit 50-10,000+ items with better performance, searchability, and editing UX.

## Nested Repeaters (Repeater in Repeater)

ACF supports repeaters inside repeaters for hierarchical data like accordion sections (each section has a repeater of items). Nesting should be used sparingly (analyzed projects show zero nested repeaters). Two-level nesting is the practical maximum before editor UX degrades.

**Nested Repeater Example (Hypothetical):**

```json
{
    "name": "sections",
    "type": "repeater",
    "layout": "block",
    "sub_fields": [
        { "name": "section_title", "type": "text" },
        {
            "name": "items",
            "type": "repeater",
            "layout": "table",
            "sub_fields": [
                { "name": "item_title", "type": "text" },
                { "name": "item_description", "type": "textarea" }
            ]
        }
    ]
}
```

**PHP Access:**

```php
$sections = get_field('sections');
foreach ($sections as $section):
    echo '<h2>' . esc_html($section['section_title']) . '</h2>';
    foreach ($section['items'] as $item):
        echo '<li>' . esc_html($item['item_title']) . '</li>';
    endforeach;
endforeach;
```

**Warning:** Nested repeaters create exponential UI complexity (10 outer × 10 inner = 100 fields). Use Flexible Content instead.

## Repeater vs Relationship Field

Repeaters store structured data directly in the post. Relationship fields reference existing posts, creating connections between content. Use repeaters for data that doesn't exist elsewhere (team member profiles on About page). Use relationship fields for data that exists as posts (related blog posts, linked products).

**Repeater (Embedded Data):**

```json
// Team members don't exist as posts - store directly in repeater
{
    "name": "team_members",
    "type": "repeater",
    "sub_fields": [
        { "name": "name", "type": "text" },
        { "name": "title", "type": "text" },
        { "name": "photo", "type": "image" }
    ]
}
```

**Relationship Field (Reference Posts):**

```json
// Blog posts exist independently - reference them
{
    "name": "related_posts",
    "type": "relationship",
    "post_type": ["post"],
    "max": 3
}
```

**Decision Matrix:**
- **Data exists as independent posts** → Relationship field
- **Data only relevant in this context** → Repeater
- **Need centralized editing** → Custom post type + Relationship
- **Need quick inline editing** → Repeater

## Repeater Field Naming: Plural Nouns

Repeater field names should be plural nouns indicating collections: `logos`, `team_members`, `testimonials`, `slides`, `faqs`. Sub-fields use singular nouns: `logo`, `member_name`, `testimonial_text`. This convention makes code self-documenting.

**Naming Examples:**

```php
// ✅ Plural repeater, singular sub-fields
$logos = get_field('logos');
foreach ($logos as $logo) {
    echo $logo['logo'];  // Singular sub-field
}

// ✅ Plural repeater, singular sub-fields
$team_members = get_field('team_members');
foreach ($team_members as $member) {
    echo $member['name'];  // Singular sub-field
}

// ❌ Singular repeater name (confusing)
$logo = get_field('logo');  // Implies single logo, not collection
foreach ($logo as $item) { ... }
```

## Repeater Performance Considerations

Repeaters serialize as PHP arrays in single postmeta entries, making retrieval efficient (1 database query for entire repeater). However, large repeaters (100+ rows) with complex sub-fields (images, relationships) can cause slow admin page loads. Consider custom post types for large datasets.

**Performance Guidelines:**

- **1-20 rows:** Repeater ideal
- **20-50 rows:** Repeater acceptable, consider pagination (`rows_per_page: 20`)
- **50-200 rows:** Repeater works but slow admin, consider custom post type
- **200+ rows:** Custom post type strongly recommended

**Database Storage Example:**

```sql
-- Repeater with 3 rows (single meta entry)
meta_key: logos
meta_value: a:3:{i:0;a:2:{s:4:"logo";i:45;s:4:"link";s:20:"https://example.com";}...}
```

Single serialized entry makes retrieval fast but prevents efficient SQL queries on sub-field values.

## Custom Button Labels

Repeater `button_label` property customizes the "Add Row" button text, improving editor UX by matching content domain. "Add Logo" is clearer than "Add Row" for logo repeater. All analyzed projects leverage this for editor-friendly interfaces.

**Custom Button Labels:**

```json
{ "name": "logos", "button_label": "Add Logo" }
{ "name": "team_members", "button_label": "Add Team Member" }
{ "name": "testimonials", "button_label": "Add Testimonial" }
{ "name": "faqs", "button_label": "Add FAQ" }
{ "name": "slides", "button_label": "Add Slide" }
```

**Default (Generic):** "Add Row" when `button_label` not specified.

## Empty Repeater Handling

Repeaters with zero rows return `false` in PHP, not empty arrays. Always check repeater existence with `if ($repeater)` before looping to avoid PHP warnings. This pattern appears consistently in analyzed projects.

**Empty Repeater Check:**

```php
$logos = get_field('logos');

if ($logos) {  // Returns false if empty, not []
    foreach ($logos as $logo) {
        // Process rows
    }
} else {
    // No logos added - show fallback content or nothing
    echo '<p>No logos to display.</p>';
}

// ❌ BAD: Skips falsy check
foreach (get_field('logos') as $logo) {  // Warning if empty
    echo $logo['logo'];
}
```

## Flexible Content vs Repeater

Flexible Content fields (ACF Pro) enable variable-structure rows where each row can be a different layout. Repeaters enforce identical structure per row. Use Flexible Content for page builders where editors choose row types (hero section vs content section vs gallery). Use Repeater for uniform collections.

**Repeater (Same Structure):**

```json
{
    "name": "team_members",
    "type": "repeater",
    "sub_fields": [
        { "name": "name", "type": "text" },
        { "name": "title", "type": "text" }
    ]
}
// Every row: name + title
```

**Flexible Content (Variable Structure):**

```json
{
    "name": "page_sections",
    "type": "flexible_content",
    "layouts": [
        {
            "name": "hero_section",
            "sub_fields": [{ "name": "title" }, { "name": "image" }]
        },
        {
            "name": "content_section",
            "sub_fields": [{ "name": "text" }]
        }
    ]
}
// Each row: choose layout type
```

**Decision:** Uniform rows → Repeater. Variable rows → Flexible Content.

## Related Patterns

- **ACF Group Fields** (single instance of related fields)
- **ACF Flexible Content** (variable-structure page builders)
- **ACF Field Naming** (plural repeater names, singular sub-fields)
- **ACF + GraphQL Integration** (repeaters as GraphQL lists)
- **Custom Post Types** (alternative for large datasets)

## References

- Airbnb: `plugins/airbnb-policy-blocks/acf-json/group_680ad6fe615b8.json` (Logo Cloud Block with repeater)
- TheKelsey: `mu-plugins/thekelsey-custom/acf-json/` (15 repeater instances)
- ACF Documentation: [Repeater Field](https://www.advancedcustomfields.com/resources/repeater/)
- Analysis: `/analysis/phase4-domain3-acf-patterns-comparison.md` (Section 11: Advanced ACF Features)
