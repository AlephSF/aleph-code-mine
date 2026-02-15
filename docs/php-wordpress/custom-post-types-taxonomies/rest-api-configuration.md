---
title: "Custom Post Type REST API Configuration"
category: "custom-post-types-taxonomies"
subcategory: "rest-api"
tags: ["wordpress", "rest-api", "custom-post-types", "show-in-rest", "graphql"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "50%"
last_updated: "2026-02-12"
---

## Pattern Overview

WordPress REST API exposure for custom post types requires explicit configuration through `show_in_rest`, `rest_base`, and `rest_controller_class` arguments in `register_post_type()`. Analyzed codebases demonstrate divergent API strategies: Airbnb GraphQL-first architecture enables REST API for only 20% of CPTs (1/5), while The Kelsey traditional architecture enables REST for 100% of CPTs (3/3). This pattern reflects fundamental architectural decisions between headless decoupled CMS (GraphQL queries) versus traditional server-rendered themes with AJAX enhancement (REST API).

**The Kelsey universal REST pattern (100% adoption):**
```php
'show_in_rest'          => true,
'rest_base'             => 'kelsey-projects',
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

**Airbnb selective REST pattern (20% adoption - media uploads only):**
```php
// bnb_media: Only CPT with REST API enabled
'show_in_rest'          => true,
'rest_base'             => 'media-assets',
'rest_controller_class' => 'WP_REST_Posts_Controller',

// bnb_profile, bnb_leadership, bnb_gallery, bnb_slider: No REST API
// (GraphQL-only via WPGraphQL plugin)
```

REST API adoption correlates inversely with WPGraphQL adoption, indicating mutually exclusive API strategies rather than complementary approaches.

## Basic REST API Configuration

WordPress REST API defaults to disabled for custom post types. Enabling requires three arguments: `show_in_rest` (boolean flag), `rest_base` (endpoint slug), and optionally `rest_controller_class` (controller class name).

```php
<?php
$args = array(
    'labels'         => $labels,
    'public'         => true,
    'show_in_rest'   => true,  // Enable REST API
    'rest_base'      => 'kelsey-events',  // Custom endpoint name
    'rest_controller_class' => 'WP_REST_Posts_Controller',  // Controller class
    'supports'       => array('title', 'editor', 'excerpt', 'thumbnail'),
);

register_post_type('kelsey_event', $args);
```

**Resulting REST endpoints:**
- Collection: `GET /wp-json/wp/v2/kelsey-events`
- Single item: `GET /wp-json/wp/v2/kelsey-events/{id}`
- Create: `POST /wp-json/wp/v2/kelsey-events`
- Update: `PUT /wp-json/wp/v2/kelsey-events/{id}`
- Delete: `DELETE /wp-json/wp/v2/kelsey-events/{id}`

**Endpoint features:**
- Pagination via `?per_page=10&page=2`
- Filtering via `?filter[taxonomy]=term`
- Embedding via `?_embed` (loads related data)
- Field selection via `?_fields=id,title,excerpt`

Without `show_in_rest`, CPT remains inaccessible to REST API, Block Editor (Gutenberg), and JavaScript frontends relying on `wp.apiFetch()`.

## Custom REST Base Naming

The `rest_base` argument defines URL endpoint segment, enabling clean API URLs independent of internal CPT machine names. Analyzed codebases show 100% custom rest_base definition when REST API enabled.

**The Kelsey naming pattern:**
```php
// Machine name: kelsey_projects
// REST base:    kelsey-projects
register_post_type('kelsey_projects', array(
    'rest_base' => 'kelsey-projects',  // Hyphenated instead of underscored
));

// URL: /wp-json/wp/v2/kelsey-projects (not /wp-json/wp/v2/kelsey_projects)
```

**Airbnb naming pattern:**
```php
// Machine name: bnb_media
// REST base:    media-assets (semantic descriptor)
register_post_type('bnb_media', array(
    'rest_base' => 'media-assets',  // Describes content type, not internal name
));

// URL: /wp-json/wp/v2/media-assets
```

**Naming conventions:**
- Use hyphens instead of underscores (URL-safe, SEO-friendly)
- Plural form for collection semantics (`events` not `event`)
- Semantic names matching frontend terminology
- Remove client prefix for cleaner public API (internal: `kelsey_event`, public: `events`)

Default `rest_base` falls back to CPT machine name if unspecified, resulting in underscored URLs (`/wp-json/wp/v2/kelsey_event`). Analyzed codebases avoid this by always defining explicit `rest_base`.

## Block Editor (Gutenberg) Integration

WordPress Block Editor requires REST API-enabled post types to function. The `show_in_rest` argument determines whether CPT appears in Block Editor or forces Classic Editor.

```php
<?php
$args = array(
    'show_in_rest' => true,  // ✅ Enables Block Editor
    'supports'     => array('title', 'editor', 'custom-fields'),
    'show_in_menu' => true,
);

register_post_type('kelsey_resource', $args);
```

**Block Editor features requiring REST API:**
- Block insertion and manipulation
- Sidebar panels (categories, featured image)
- Autosave and revisions
- Real-time collaboration (future)
- Block patterns and reusable blocks

**Without REST API:**
CPT falls back to Classic Editor (TinyMCE), preventing use of modern block-based content creation. The Kelsey demonstrates 100% REST API adoption to leverage Block Editor across all CPTs.

**Airbnb headless strategy:**
Airbnb disables REST API for content-focused CPTs (`bnb_profile`, `bnb_leadership`) because content managed via traditional WordPress admin UI does not require Block Editor. Content consumed via GraphQL by Next.js frontend, not displayed in WordPress themes. Only `bnb_media` enables REST API for media library uploads via AJAX.

## REST Controller Customization

WordPress provides `WP_REST_Posts_Controller` default controller for standard CRUD operations. Custom controllers extend functionality for specialized requirements (custom endpoints, authentication, rate limiting).

```php
<?php
// Standard controller (100% of analyzed codebases)
$args = array(
    'show_in_rest'          => true,
    'rest_controller_class' => 'WP_REST_Posts_Controller',
);

// Custom controller example (not found in analyzed codebases)
class Custom_Events_Controller extends WP_REST_Posts_Controller {
    public function get_items($request) {
        // Add custom filtering logic
        $items = parent::get_items($request);

        // Filter by event date
        if ($request['future_only']) {
            $items = array_filter($items, function($item) {
                return strtotime($item['acf']['event_date']) > time();
            });
        }

        return $items;
    }
}

$args = array(
    'show_in_rest'          => true,
    'rest_controller_class' => 'Custom_Events_Controller',
);
```

Analyzed codebases show 0% custom controller usage, relying entirely on WordPress default `WP_REST_Posts_Controller`. This indicates standard CRUD operations sufficient for analyzed use cases, with custom logic implemented via GraphQL resolvers (Airbnb) or client-side filtering (The Kelsey).

## REST API vs GraphQL Architecture Decision

**The Kelsey: REST API-First Architecture (100% CPTs REST-enabled)**

*Use cases:*
- AJAX-enhanced server-rendered pages
- Block Editor content creation
- Mobile app API consumption
- Third-party integrations via REST

*Trade-offs:*
- Multiple HTTP requests for related data (over-fetching)
- No strongly-typed schema
- Limited query flexibility
- Standard WordPress authentication

**Airbnb: GraphQL-First Architecture (20% CPTs REST-enabled)**

*Use cases:*
- Headless Next.js frontend
- Single GraphQL query for nested data
- Strongly-typed schema via GraphQL SDL
- Optimized for decoupled architecture

*Trade-offs:*
- Requires WPGraphQL plugin
- Steeper learning curve (GraphQL syntax)
- Cannot use Block Editor for GraphQL-only CPTs
- Custom resolver complexity for relationships

**Hybrid approach (Airbnb pattern):**
REST API enabled for media uploads (bnb_media), GraphQL for content queries (bnb_profile, bnb_leadership). Separates write operations (REST uploads) from read operations (GraphQL queries).

## REST API Field Registration

Custom fields exposed to REST API via `register_rest_field()` function, extending default post schema with ACF fields, computed properties, or external API data.

```php
<?php
function register_event_rest_fields(){
register_rest_field('kelsey_event','event_date',array('get_callback'=>function($p){return function_exists('get_field')?get_field('date',$p['id']):null;},'schema'=>array('description'=>'Event date from ACF','type'=>'string','format'=>'date-time')));
register_rest_field('kelsey_event','funraise_id',array('get_callback'=>function($p){return function_exists('get_field')?get_field('funraise_id',$p['id']):null;},'schema'=>array('description'=>'Funraise ID','type'=>'string')));
}
add_action('rest_api_init','register_event_rest_fields');
```

**REST response with custom fields:**
```json
{"id":123,"title":{"rendered":"Annual Conference 2026"},"event_date":"2026-06-15T09:00:00","funraise_id":"evt_abc123"}
```

ACF field registration enables frontend JavaScript to access custom fields without separate meta queries, reducing HTTP request count and simplifying client code.

## REST API Permissions and Capabilities

Custom post types inherit capability checks from `capability_type` argument, determining REST API access control (read, create, edit, delete permissions).

```php
<?php
$args = array(
    'capability_type' => 'post',  // Uses standard post capabilities
    'show_in_rest'    => true,
);

// Capabilities mapped automatically:
// - edit_post
// - delete_post
// - publish_posts
// - edit_others_posts
```

**Custom capability type:**
```php
<?php
$args = array(
    'capability_type' => 'event',  // Custom capability namespace
    'map_meta_cap'    => true,
    'show_in_rest'    => true,
);

// Custom capabilities:
// - edit_event
// - delete_event
// - publish_events
// - edit_others_events
```

Analyzed codebases show 100% usage of `capability_type => 'post'`, leveraging WordPress default permission system. No custom capability types observed, indicating standard Editor/Author/Contributor role permissions sufficient for analyzed content workflows.

## Anti-Patterns to Avoid

**1. Enabling REST for GraphQL-only CPTs:**
```php
// Bad: Unnecessary REST endpoint exposure
$args = array(
    'show_in_rest'       => true,  // Unused (only using GraphQL)
    'show_in_graphql'    => true,
    'graphql_single_name' => 'profile',
);

// Good: REST disabled for GraphQL-only CPTs
$args = array(
    'show_in_rest'       => false,
    'show_in_graphql'    => true,
    'graphql_single_name' => 'profile',
);
```

**2. Using CPT machine name as rest_base:**
```php
// Bad: Exposes internal naming (underscores, prefixes)
'rest_base' => 'kelsey_event',

// Good: Clean semantic endpoint
'rest_base' => 'events',
```

**3. Forgetting custom field registration:**
```php
// Bad: ACF fields invisible to REST API
register_post_type('event', array('show_in_rest' => true));

// Good: Register custom fields
add_action('rest_api_init', 'register_event_custom_fields');
```

## References

- WordPress REST API Handbook - https://developer.wordpress.org/rest-api/
- register_post_type() REST arguments - https://developer.wordpress.org/reference/functions/register_post_type/#rest-api
- register_rest_field() - https://developer.wordpress.org/reference/functions/register_rest_field/
- WPGraphQL Documentation - https://www.wpgraphql.com/docs/intro

**Source:** Airbnb 20% REST adoption (GraphQL-first), The Kelsey 100% REST adoption (traditional architecture). Pattern confidence: 50% (architecture-dependent decision).
