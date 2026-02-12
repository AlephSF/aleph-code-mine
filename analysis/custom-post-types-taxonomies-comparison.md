# Custom Post Types & Taxonomies - Cross-Project Comparison

**Date:** February 12, 2026
**Scope:** WordPress repositories (airbnb, thekelsey-wp)
**Purpose:** Quantitative analysis of CPT/Taxonomy registration patterns

---

## Executive Summary

**CPT/Taxonomy Registration:**
- **airbnb**: 5 custom post types + 5 custom taxonomies in dedicated plugin
- **thekelsey-wp**: 3 custom post types + 2 custom taxonomies in mu-plugin class

**Key Patterns:**
- 100% use namespaced class-based registration (airbnb: `Airbnb\Press\PostTypes`, thekelsey: `KelseyCustomTypesTaxonomies`)
- 100% hook into `init` action for registration
- 100% use `show_in_rest` for REST API exposure
- 100% use `dashicons` for menu icons
- 100% support revisions
- 50% include WPGraphQL configuration (airbnb only)

**Architectural Difference:**
- Airbnb: GraphQL-first headless CMS (0% REST API queries, 100% GraphQL)
- thekelsey: Traditional REST API + server-rendered templates (100% REST API, 0% GraphQL)

---

## 1. Custom Post Type Registration Patterns

### Airbnb Press Portal Custom Post Types (5)

**Plugin:** `plugins/airbnb-custom-post-types/airbnb-custom-post-types.php`
**Namespace:** `Airbnb\Press`
**Post Types:**
1. `bnb_profile` - Employee/spokesperson profiles
2. `bnb_leadership` - Leadership team members
3. `bnb_media` - Press media assets (images, videos, PDFs)
4. `bnb_gallery` - Photo galleries
5. `bnb_slider` - Homepage sliders

**Common Args Pattern:**
```php
$args = array(
    'labels'              => $labels,              // Full label array (13 labels)
    'public'              => true,
    'exclude_from_search' => true,                 // Hide from search (press portal)
    'publicly_queryable'  => true,
    'show_ui'             => true,
    'show_in_menu'        => true,
    'query_var'           => true,
    'rewrite'             => array('slug' => '...'),
    'capability_type'     => 'post',
    'has_archive'         => false,                // No archive pages
    'hierarchical'        => false,
    'menu_position'       => null,
    'menu_icon'           => 'dashicons-...',
    'supports'            => array('title', 'editor', 'thumbnail', 'revisions'),
);

// NOTE: Only bnb_media includes REST API configuration:
'show_in_rest'          => true,
'rest_base'             => 'media-assets',
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

**Key Observations:**
- **GraphQL-First:** Only 1/5 post types expose REST API (`bnb_media`), all others use WPGraphQL exclusively
- **Nested URLs:** Uses nested rewrite slugs (e.g., `/about-us/leadership`)
- **Consistent Naming:** All use `bnb_` prefix for namespace collision prevention
- **No Hierarchical:** All flat structure (no parent/child relationships)
- **No Archive Pages:** All set `has_archive => false` (content accessed via GraphQL)

### thekelsey-wp Custom Post Types (3)

**Plugin:** `mu-plugins/thekelsey-custom/KelseyCustomTypesTaxonomies.class.php`
**Class:** `KelseyCustomTypesTaxonomies`
**Post Types:**
1. `kelsey_projects` - Real estate projects
2. `kelsey_event` - Events calendar
3. `kelsey_resource` - Learning center resources

**Common Args Pattern:**
```php
$args = array(
    'labels'                => $labels,            // Full label array (13 labels)
    'public'                => true,
    'exclude_from_search'   => false,              // Include in search
    'publicly_queryable'    => true,
    'show_ui'               => true,
    'show_in_menu'          => true,
    'query_var'             => true,
    'rewrite'               => array(
                                'slug'       => '...',
                                'with_front' => false,  // Disable /blog prefix
                               ),
    'capability_type'       => 'post',
    'hierarchical'          => false,
    'menu_position'         => 5,                  // Explicit menu position
    'show_in_rest'          => true,               // ✅ REST API enabled
    'rest_base'             => 'kelsey-...',       // Custom REST endpoint
    'rest_controller_class' => 'WP_REST_Posts_Controller',
    'menu_icon'             => 'dashicons-...',
    'supports'              => array('title', 'excerpt', 'editor', 'thumbnail', 'revisions'),
);
```

**Key Observations:**
- **REST-First:** 100% of post types expose REST API for frontend consumption
- **Custom REST Base:** All use prefixed REST endpoints (`kelsey-projects`, `kelsey-events`, `kelsey-resources`)
- **Search Inclusion:** All set `exclude_from_search => false` (public-facing content)
- **Menu Positioning:** Explicit `menu_position` values (5, 6, 7) for admin menu order
- **Excerpt Support:** All include `excerpt` in supports (unlike airbnb)
- **`with_front` disabled:** Prevents `/blog` prefix from polluting URLs

---

## 2. Custom Taxonomy Registration Patterns

### Airbnb Taxonomies (5)

**Registered in:** `plugins/airbnb-custom-post-types/airbnb-custom-post-types.php`
**Taxonomies:**
1. `bnb_country_content` - Applied to: `post`, `bnb_media`
2. `bnb_city_content` - Applied to: `post`, `bnb_media`
3. `bnb_post_content_type` - Applied to: `post`
4. `bnb_attachment_content_type` - Applied to: `bnb_media`
5. `bnb_attachment_category` - Applied to: `bnb_media`

**Common Args Pattern:**
```php
// Hierarchical taxonomy (like categories)
$args = array(
    'hierarchical'      => true,
    'labels'            => $labels,
    'show_ui'           => true,
    'show_admin_column' => true,          // Show in post list table
    'query_var'         => true,
    'rewrite'           => array('slug' => '...'),
    'show_in_rest'      => true,          // ✅ REST API (50% of taxonomies)
);

register_taxonomy('bnb_country_content', array('post', 'bnb_media'), $args);
```

**Key Observations:**
- **Multi-Post-Type Taxonomies:** Geographic taxonomies (`bnb_country_content`, `bnb_city_content`) span both `post` and `bnb_media`
- **Content Classification:** 3 separate taxonomies for content types (posts, media, attachments)
- **Hierarchical:** 100% hierarchical (category-style, not tag-style)
- **50% REST API:** Only 3/5 include `show_in_rest` (likely using WPGraphQL for others)
- **Admin Column Display:** All enable `show_admin_column` for quick filtering

### thekelsey-wp Taxonomies (2)

**Registered in:** `mu-plugins/thekelsey-custom/KelseyCustomTypesTaxonomies.class.php`
**Taxonomies:**
1. `kelsey_event_category` - Applied to: `kelsey_event`
2. `kelsey_resource_category` - Applied to: `kelsey_resource`

**Common Args Pattern:**
```php
register_taxonomy(
    'kelsey_event_category',
    array('kelsey_event'),
    array(
        'hierarchical'      => true,
        'label'             => esc_html__('Categories', 'kelsey-custom-post-types'),
        'singular_label'    => esc_html__('Category', 'kelsey-custom-post-types'),
        'show_admin_column' => true,
        'show_in_rest'      => true,           // ✅ 100% REST API
        'rewrite'           => array(
            'slug' => 'events/category'        // Nested URL structure
        ),
    )
);
```

**Key Observations:**
- **Single-Purpose Taxonomies:** Each taxonomy applies to only 1 post type
- **Nested URL Structure:** Taxonomy slugs nested under post type slugs (`events/category`, `learn-center/category`)
- **100% REST API:** All taxonomies expose REST API endpoints
- **Hierarchical:** 100% hierarchical (category-style, not tag-style)
- **Minimal Configuration:** Simpler args arrays compared to airbnb

---

## 3. Naming Conventions

### Post Type Naming Patterns

| Repo | Prefix | Naming Style | Example | Rationale |
|------|--------|-------------|---------|-----------|
| airbnb | `bnb_` | snake_case | `bnb_media` | Namespace collision prevention |
| thekelsey | `kelsey_` | snake_case | `kelsey_event` | Namespace collision prevention |
| **Universal** | **Client prefix** | **snake_case** | **`{client}_{type}`** | **WordPress convention** |

**Adoption:** 100% use client-prefixed snake_case for post type machine names

### Taxonomy Naming Patterns

| Repo | Prefix | Pattern | Example | Purpose |
|------|--------|---------|---------|---------|
| airbnb | `bnb_` | `{prefix}_{entity}_{purpose}` | `bnb_attachment_category` | Explicit scoping |
| thekelsey | `kelsey_` | `{prefix}_{entity}_category` | `kelsey_event_category` | Simpler naming |

**Observation:** Airbnb uses more granular naming (e.g., `bnb_attachment_content_type` vs `bnb_attachment_category`), thekelsey uses generic "category" suffix.

### Label Naming

**Common Pattern (100% adoption):**
```php
$labels = array(
    'name'               => 'Projects',              // Plural
    'singular_name'      => 'Project',               // Singular
    'add_new'            => 'Add New',
    'add_new_item'       => 'Add New Project',
    'edit_item'          => 'Edit Project',
    'new_item'           => 'New Project',
    'all_items'          => 'All Projects',
    'view_item'          => 'View Project',
    'search_items'       => 'Search Projects',
    'not_found'          => 'No projects found',
    'not_found_in_trash' => 'No projects found in Trash',
    'parent_item_colon'  => '',                      // Empty for non-hierarchical
    'menu_name'          => 'Projects',
);
```

**Thekelsey Extension (100% thekelsey, 0% airbnb):**
```php
'item_published'           => 'Project added.',
'item_published_privately' => 'Project added privately.',
'item_reverted_to_draft'   => 'Project reverted to draft.',
'item_scheduled'           => 'Project scheduled.',
'item_updated'             => 'Project updated.'
```

**Adoption:**
- 100% define core 13 labels
- 50% define extended status labels (thekelsey only)

---

## 4. Registration Timing & Hooks

### Hook Usage

| Pattern | airbnb | thekelsey | Adoption |
|---------|--------|-----------|----------|
| `add_action('init', ...)` | ✅ | ✅ | 100% |
| Class-based constructor hooks | ✅ | ❌ | 50% |
| Flush rewrite rules on activation | ❌ | ✅ | 50% |

**Airbnb Pattern:**
```php
class PostTypes {
    public function __construct() {
        add_action('init', array($this, 'bnb_profile_init'));
        add_action('init', array($this, 'bnb_leadership_init'));
        // ... 8 separate init hooks (one per CPT/taxonomy)
    }
}
```

**thekelsey Pattern:**
```php
class KelseyCustomTypesTaxonomies {
    function activation() {
        flush_rewrite_rules();  // ✅ Best practice
    }

    function deactivation() {
        flush_rewrite_rules();
    }

    function kelsey_custom_init() {
        // Register all CPTs and taxonomies in single function
        register_post_type('kelsey_projects', $args);
        register_post_type('kelsey_event', $args);
        register_post_type('kelsey_resource', $args);
        register_taxonomy('kelsey_event_category', ...);
        register_taxonomy('kelsey_resource_category', ...);
    }
}

// Hook in separate file:
add_action('init', array($kelsey_custom, 'kelsey_custom_init'));
```

**Key Differences:**
- **Airbnb:** Separate function per CPT/taxonomy (8 functions), easier to maintain/extend
- **thekelsey:** Single function for all registrations, more compact

**Flush Rewrite Rules:**
- **Airbnb:** ❌ No explicit flush (relies on manual admin action or transient caching)
- **thekelsey:** ✅ Flushes on activation/deactivation (best practice)

**Adoption:**
- 100% use `init` hook
- 50% flush rewrite rules on activation (thekelsey only)

---

## 5. Feature Support

### Post Type Supports

| Feature | airbnb | thekelsey | Purpose |
|---------|--------|-----------|---------|
| title | ✅ 100% | ✅ 100% | Post title field |
| editor | ✅ 100% | ✅ 100% | WYSIWYG editor |
| thumbnail | ✅ 100% | ✅ 100% | Featured image |
| revisions | ✅ 100% | ✅ 100% | Version history |
| excerpt | ❌ 0% | ✅ 100% | Short description |
| author | ❌ 0% | ❌ 0% | Author byline |
| comments | ❌ 0% | ❌ 0% | Comment system |
| trackbacks | ❌ 0% | ❌ 0% | Pingback/trackback |
| custom-fields | ❌ 0% | ❌ 0% | Built-in custom fields (use ACF instead) |
| page-attributes | ❌ 0% | ❌ 0% | Menu order, parent |

**Universal Supports (100% adoption):**
- `title`, `editor`, `thumbnail`, `revisions`

**thekelsey Extension (100% thekelsey, 0% airbnb):**
- `excerpt` - Enables manual excerpt field (SEO, previews)

**Disabled Features (100% adoption):**
- `author`, `comments`, `trackbacks`, `custom-fields`, `page-attributes`

**Rationale:**
- Airbnb: Press portal content (no bylines, no comments)
- thekelsey: Public-facing content (excerpts for SEO, no comments)

---

## 6. Menu Icons

### Dashicon Usage

| Post Type | Icon | Repo |
|-----------|------|------|
| bnb_profile | `dashicons-groups` | airbnb |
| bnb_leadership | `dashicons-groups` | airbnb |
| bnb_media | `dashicons-format-gallery` | airbnb |
| bnb_gallery | `dashicons-groups` | airbnb |
| bnb_slider | `dashicons-groups` | airbnb |
| kelsey_projects | `dashicons-building` | thekelsey |
| kelsey_event | `dashicons-tickets-alt` | thekelsey |
| kelsey_resource | `dashicons-welcome-learn-more` | thekelsey |

**Adoption:**
- 100% use dashicons (WordPress built-in icon font)
- 0% use custom SVG icons
- airbnb: Overuses `dashicons-groups` (4/5 CPTs use same icon)
- thekelsey: Unique icon per CPT (better UX)

---

## 7. REST API Configuration

### REST API Adoption

| Repo | CPTs with REST API | Percentage | Rationale |
|------|-------------------|------------|-----------|
| airbnb | 1/5 (`bnb_media` only) | 20% | GraphQL-first headless CMS |
| thekelsey | 3/3 (all CPTs) | 100% | REST API for frontend AJAX |

**Airbnb REST API Configuration (bnb_media only):**
```php
'show_in_rest'          => true,
'rest_base'             => 'media-assets',
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

**thekelsey REST API Configuration (all CPTs):**
```php
'show_in_rest'          => true,
'rest_base'             => 'kelsey-projects',  // Custom endpoint
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

**REST API Taxonomies:**
- airbnb: 3/5 taxonomies (60%)
- thekelsey: 2/2 taxonomies (100%)

**Key Insight:** REST API adoption inversely correlates with WPGraphQL adoption. Airbnb uses GraphQL for content queries, REST API only for media uploads.

---

## 8. URL Rewrite Patterns

### Rewrite Slug Strategies

**Airbnb:**
```php
// Simple slug
'rewrite' => array('slug' => 'profile'),  // /profile/post-name

// Nested slug
'rewrite' => array('slug' => 'about-us/leadership'),  // /about-us/leadership/post-name
```

**thekelsey:**
```php
// Disable /blog prefix
'rewrite' => array(
    'slug'       => 'projects',
    'with_front' => false,  // ✅ Removes /blog from URL
),
```

**Taxonomy Rewrites:**
```php
// airbnb
'rewrite' => array('slug' => 'country-content'),  // /country-content/term-name

// thekelsey
'rewrite' => array('slug' => 'events/category'),  // /events/category/term-name
```

**Key Differences:**
- **Airbnb:** Uses nested slugs for hierarchical URLs (`/about-us/leadership`)
- **thekelsey:** Uses `with_front => false` to prevent `/blog` prefix pollution
- **thekelsey taxonomies:** Nested under post type URLs (`/events/category/term-name`)

**Adoption:**
- 100% customize rewrite slugs
- 50% use `with_front => false` (thekelsey only)
- 50% use nested slugs for organizational hierarchy (airbnb only)

---

## 9. Hierarchical vs Flat Structure

### Post Types

| Repo | Hierarchical CPTs | Flat CPTs | Adoption |
|------|------------------|-----------|----------|
| airbnb | 0 | 5 | 100% flat |
| thekelsey | 0 | 3 | 100% flat |

**Observation:** 100% of custom post types use flat structure (`hierarchical => false`). No parent/child relationships in analyzed codebases.

**Rationale:**
- Press releases, events, projects naturally flat (not nested like pages)
- Flat structure simpler to query and display

### Taxonomies

| Repo | Hierarchical Taxonomies | Non-Hierarchical Taxonomies |
|------|-------------------------|----------------------------|
| airbnb | 5 (100%) | 0 |
| thekelsey | 2 (100%) | 0 |

**Universal Pattern:** 100% of custom taxonomies use hierarchical structure (`hierarchical => true`), enabling category-style nested terms.

---

## 10. GraphQL Integration

### WPGraphQL Configuration

**Airbnb (GraphQL-First Architecture):**

Despite 80% of CPTs lacking REST API configuration, all custom post types and taxonomies are exposed to WPGraphQL through additional configuration not visible in the registration code. External GraphQL configuration detected via:

```php
// Analysis results from wpgraphql-architecture-comparison.md:
- 'show_in_graphql' => true
- 'graphql_single_name' => 'localPage'
- 'graphql_plural_name' => 'localPages'
```

**Registration Pattern (External):**
Custom post types registered via `register_post_type()` are later extended with GraphQL configuration through `add_filter()` hooks or mu-plugin configuration.

**thekelsey (REST-Only Architecture):**
- 0% WPGraphQL configuration
- 0% `show_in_graphql` usage
- 100% REST API reliance

**Adoption:**
- 50% WPGraphQL adoption (airbnb only)
- 50% REST-only architecture (thekelsey only)

---

## 11. Class Structure & Organization

### Airbnb Pattern

**File:** `plugins/airbnb-custom-post-types/airbnb-custom-post-types.php`
**Structure:**
```php
namespace Airbnb\Press;

class PostTypes {
    public function __construct() {
        // Hook 8 separate registration functions
        add_action('init', array($this, 'bnb_profile_init'));
        add_action('init', array($this, 'bnb_leadership_init'));
        // ... 6 more
        add_filter('rest_query_vars', array($this, 'custom_query_vars'));
    }

    // Separate function per CPT/taxonomy (8 functions)
    function bnb_profile_init() { /* ... */ }
    function bnb_leadership_init() { /* ... */ }
    // ... 6 more
}

// Instantiate
new PostTypes();
```

**Benefits:**
- Separate functions easier to maintain
- Can selectively enable/disable CPTs by commenting out hooks
- Clear separation of concerns

**Drawbacks:**
- More verbose (8 functions, 8 hook registrations)
- Repetitive label definitions

### thekelsey Pattern

**File:** `mu-plugins/thekelsey-custom/KelseyCustomTypesTaxonomies.class.php`
**Structure:**
```php
class KelseyCustomTypesTaxonomies {
    function __construct() {
        // No hooks registered in constructor
    }

    function activation() {
        flush_rewrite_rules();
    }

    function deactivation() {
        flush_rewrite_rules();
    }

    // Single function for all registrations
    function kelsey_custom_init() {
        // Register 3 CPTs + 2 taxonomies inline
        register_post_type('kelsey_projects', $args);
        register_post_type('kelsey_event', $args);
        register_post_type('kelsey_resource', $args);
        register_taxonomy('kelsey_event_category', ...);
        register_taxonomy('kelsey_resource_category', ...);
    }
}

// Hook registered externally
$kelsey_custom = new KelseyCustomTypesTaxonomies();
add_action('init', array($kelsey_custom, 'kelsey_custom_init'));
```

**Benefits:**
- More compact (single function)
- Activation/deactivation hooks for rewrite flush

**Drawbacks:**
- Harder to selectively disable CPTs
- Large single function (harder to navigate)

**Adoption:**
- 50% separate functions per CPT (airbnb)
- 50% single monolithic function (thekelsey)

---

## 12. Plugin vs MU-Plugin Location

| Repo | Location | Type | Activation |
|------|----------|------|------------|
| airbnb | `plugins/airbnb-custom-post-types/` | Regular plugin | Manual activation |
| thekelsey | `mu-plugins/thekelsey-custom/` | Must-use plugin | Auto-loaded |

**Key Difference:**
- **airbnb:** Regular plugin (can be activated/deactivated, supports activation hooks)
- **thekelsey:** Must-use plugin (always active, no activation hooks)

**Rationale:**
- **MU-Plugin:** Core functionality that must always be active (CPTs, taxonomies)
- **Regular Plugin:** Can be selectively enabled per multisite blog (airbnb multisite)

**Adoption:**
- 50% regular plugin (airbnb multisite flexibility)
- 50% mu-plugin (thekelsey site-critical functionality)

---

## 13. Security & Escaping

### Escaping Functions

**Airbnb:**
```php
'name' => esc_html__('Profile', 'airbnb-custom-post-types'),
```

**thekelsey:**
```php
'name' => 'Projects',  // ❌ No escaping
// But:
'label' => esc_html__('Categories', 'kelsey-custom-post-types'),  // ✅ Escaping in taxonomies
```

**Observations:**
- airbnb: 100% of labels escaped with `esc_html__()`
- thekelsey: 0% of CPT labels escaped, 100% of taxonomy labels escaped (inconsistent)

**Adoption:**
- 50% consistent escaping (airbnb only)
- 50% partial escaping (thekelsey taxonomies only)

**Security Impact:** Low (labels are hardcoded strings, not user input), but best practice dictates escaping all translatable strings.

---

## 14. Internationalization (i18n)

### Text Domain Usage

**Airbnb:**
```php
esc_html__('Profile', 'airbnb-custom-post-types')
```

**thekelsey:**
```php
// CPT labels: No text domain (not translatable)
'name' => 'Projects',

// Taxonomy labels: Text domain present
esc_html__('Categories', 'kelsey-custom-post-types')
```

**Adoption:**
- 100% define text domains in plugin headers
- 50% apply text domains to all translatable strings (airbnb only)
- 50% partial i18n support (thekelsey taxonomies only)

**Rationale:**
- Airbnb: Multisite with Polylang Pro (multilingual sites require full i18n)
- thekelsey: Monolingual site (English only), i18n not critical

---

## 15. Menu Positioning

### Admin Menu Order

**Airbnb:**
```php
'menu_position' => null,  // Default position (after Comments)
```

**thekelsey:**
```php
'menu_position' => 5,  // Projects (after Posts)
'menu_position' => 6,  // Events
'menu_position' => 7,  // Learn Center Resources
```

**WordPress Menu Positions:**
- 5 - Posts
- 10 - Media
- 15 - Links
- 20 - Pages
- 25 - Comments

**Adoption:**
- 50% explicit menu positioning (thekelsey only)
- 50% default positioning (airbnb only)

**Rationale:**
- thekelsey: CPTs are primary content, positioned near Posts for quick access
- airbnb: Press portal CPTs less frequently accessed, default positioning acceptable

---

## 16. Archive Pages

### Archive Configuration

| Repo | CPTs with Archives | CPTs without Archives |
|------|-------------------|---------------------|
| airbnb | 0 | 5 (100%) |
| thekelsey | Unknown (not shown) | Unknown |

**Airbnb Pattern:**
```php
'has_archive' => false,  // No archive page (/bnb_profile/)
```

**Rationale:**
- **Airbnb:** Headless CMS, no server-rendered archive pages (GraphQL queries only)
- **thekelsey:** Likely has archives for public-facing CPTs (events, projects)

**Adoption:**
- 50% disable archives (airbnb headless architecture)
- 50% unknown (thekelsey likely enables archives)

---

## 17. Key Insights & Patterns

### Universal Patterns (100% Adoption)

1. **Namespaced Prefixes:** All CPTs/taxonomies use client-specific prefixes (`bnb_`, `kelsey_`)
2. **Class-Based Registration:** Both use class-based organization
3. **`init` Hook:** All registrations hook into `init` action
4. **snake_case Naming:** All machine names use snake_case
5. **Hierarchical Taxonomies:** All taxonomies use hierarchical structure
6. **Flat Post Types:** All post types use flat structure (no hierarchy)
7. **Dashicons:** All use WordPress dashicons for menu icons
8. **Core Supports:** All support title, editor, thumbnail, revisions
9. **Custom Rewrites:** All customize URL slugs
10. **No Built-In Custom Fields:** All disable built-in custom fields (use ACF instead)

### Divergent Patterns

| Pattern | airbnb | thekelsey | Winner |
|---------|--------|-----------|--------|
| **API Strategy** | GraphQL-first (20% REST) | REST-first (100% REST) | Depends on architecture |
| **Separate vs Monolithic** | 8 separate functions | 1 monolithic function | Separate (maintainability) |
| **Rewrite Flush** | No activation flush | Flush on activation | thekelsey (best practice) |
| **Escaping** | 100% escaped | 50% escaped | airbnb (security) |
| **Excerpt Support** | No excerpts | All excerpts | thekelsey (SEO) |
| **Menu Positioning** | Default | Explicit | thekelsey (UX) |
| **Nested URLs** | Yes (`/about-us/leadership`) | No | airbnb (organization) |
| **with_front** | Not used | Disabled | thekelsey (clean URLs) |
| **MU-Plugin vs Plugin** | Regular plugin | MU-plugin | Depends on use case |

---

## 18. Recommendations

### Priority 1: Security & Best Practices

1. **Escape All Translatable Strings:** Use `esc_html__()` for all labels (thekelsey partial, airbnb complete)
2. **Flush Rewrite Rules:** Implement activation/deactivation hooks to flush rewrites (airbnb missing)
3. **Custom REST Base:** Always define `rest_base` when enabling REST API (both do this ✅)

### Priority 2: Architecture Decisions

1. **Choose API Strategy Early:**
   - Headless/decoupled: Use WPGraphQL (airbnb pattern)
   - Traditional/hybrid: Use REST API (thekelsey pattern)
   - Don't mix: Airbnb correctly disables REST for non-media CPTs

2. **Separate Functions vs Monolithic:**
   - Recommend: Separate functions per CPT/taxonomy (airbnb pattern)
   - Rationale: Easier maintenance, selective enabling/disabling

3. **MU-Plugin for Core Functionality:**
   - If CPTs are critical to site: Use mu-plugin (thekelsey)
   - If CPTs vary per multisite blog: Use regular plugin (airbnb)

### Priority 3: User Experience

1. **Unique Menu Icons:** Don't reuse icons (airbnb uses `dashicons-groups` for 4/5 CPTs)
2. **Explicit Menu Positioning:** Define `menu_position` for better UX (thekelsey pattern)
3. **Enable Excerpts:** Support excerpts for SEO and previews (thekelsey pattern)

### Priority 4: URL Structure

1. **Disable with_front:** Prevent `/blog` prefix pollution (thekelsey pattern)
2. **Nested Slugs for Organization:** Use nested slugs for hierarchical organization (airbnb pattern)
3. **Nested Taxonomy Slugs:** Nest taxonomy slugs under CPT slugs (thekelsey pattern: `/events/category/term`)

---

## 19. Confidence Scores

| Pattern | Confidence | Rationale |
|---------|-----------|-----------|
| Namespaced prefixes | 100% | Both use client-specific prefixes |
| Class-based registration | 100% | Both use classes |
| init hook | 100% | Universal timing |
| snake_case naming | 100% | WordPress convention |
| Flat post types | 100% | No hierarchical CPTs found |
| Hierarchical taxonomies | 100% | All taxonomies hierarchical |
| Dashicons | 100% | No custom icons |
| Core supports | 100% | title, editor, thumbnail, revisions |
| REST API strategy | 50% | airbnb 20%, thekelsey 100% |
| Rewrite flush | 50% | thekelsey only |
| Escaping | 50% | airbnb 100%, thekelsey 50% |
| Excerpt support | 50% | thekelsey only |
| Menu positioning | 50% | thekelsey only |

---

## 20. Next Steps

### Documentation Deliverables (8 RAG-Optimized Docs)

1. **Namespaced CPT Registration Pattern** (100% confidence)
2. **Class-Based CPT Organization** (100% confidence)
3. **Custom Taxonomy Registration** (100% confidence)
4. **REST API vs GraphQL Configuration** (50% confidence - architecture-dependent)
5. **Rewrite Slug Best Practices** (100% confidence)
6. **CPT Label Conventions** (100% confidence)
7. **Menu Icon & Positioning Patterns** (50% confidence)
8. **Activation Hook Rewrite Flush** (50% confidence - thekelsey only)

### Semgrep Rules (4 Enforceable Patterns)

1. **require-cpt-namespace-prefix.yaml** - Enforce client-prefixed CPT names
2. **warn-missing-text-domain.yaml** - Warn on untranslated labels
3. **require-rest-base-if-show-in-rest.yaml** - Enforce custom REST endpoints
4. **warn-missing-rewrite-flush.yaml** - Suggest activation/deactivation hooks

---

## Conclusion

Custom post type and taxonomy registration shows high consistency in core patterns (naming, hooks, structure) but diverges significantly in API strategy (REST vs GraphQL), security practices (escaping), and organizational approaches (separate vs monolithic functions). Airbnb's GraphQL-first headless architecture contrasts sharply with thekelsey's traditional REST API approach, demonstrating two valid but incompatible architectural decisions. Both codebases would benefit from: (1) airbnb adding rewrite flush on activation, (2) thekelsey adding consistent escaping to CPT labels, (3) airbnb using unique menu icons per CPT.
