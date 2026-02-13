# ACF JSON Storage for Version Control

---
title: "ACF JSON Storage for Version Control"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "json-storage", "version-control", "git", "field-groups"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Advanced Custom Fields (ACF) provides JSON storage for field group definitions, enabling version control and team collaboration. All projects analyzed store field groups as JSON files in `acf-json/` directories, synchronized automatically via custom save/load filters. This pattern eliminates manual field group exports and ensures field definitions are tracked in Git alongside code changes.

**Evidence:** 165 field groups across 2 projects (136 airbnb + 29 thekelsey), 100% using JSON storage with custom save/load points.

## Default ACF JSON Behavior

ACF Pro automatically saves field groups to JSON files when the `acf-json` directory exists in the theme root. Without custom configuration, ACF looks for `{theme-directory}/acf-json/` and loads all JSON files found. This default behavior works for single-theme projects but fails in multi-theme, plugin-based, or MU-plugin architectures.

**Limitation:** Default path assumes field groups live in the active theme, breaking when fields are defined in plugins or must-use plugins.

## Custom Save/Load Points Pattern

WordPress projects override default ACF JSON paths using `acf/settings/save_json` and `acf/settings/load_json` filters. This enables field groups to reside in plugins, MU-plugins, or child themes while maintaining automatic synchronization. Both analyzed projects implement this pattern, though with slight variations based on their architecture.

**Key Functions:**
- `add_filter('acf/settings/save_json', 'callback')` - Define where ACF writes JSON files
- `add_filter('acf/settings/load_json', 'callback')` - Define where ACF reads JSON files

## Plugin-Based JSON Storage (Airbnb Pattern)

Airbnb stores ACF field groups in a custom plugin (`airbnb-policy-blocks`), keeping field definitions separate from theme code. The plugin defines its own `acf-json/` directory and registers custom save/load points. This approach enables field groups to persist across theme changes and allows multiple plugins to maintain their own field sets.

**Implementation (Plugin Context):**

```php
// airbnb-policy-blocks.php (lines 49-61)
function acf_json_load_point() {
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json';
  return $paths;
};
add_filter('acf/settings/load_json', 'acf_json_load_point');

function acf_json_save_point() {
  $path = plugin_dir_path(__FILE__) . 'acf-json';
  return $path;
};
add_filter('acf/settings/save_json', 'acf_json_save_point');
```

**Directory Structure:**

```
plugins/
└── airbnb-policy-blocks/
    ├── acf-json/
    │   ├── group_680ad6fe615b8.json  (Logo Cloud Block)
    │   ├── group_67afe69c6c17a.json  (FAQ Block)
    │   └── [134 more JSON files]
    └── airbnb-policy-blocks.php
```

**Why Plugin-Based:**
- Field groups survive theme switches
- Multiple plugins can register separate `acf-json/` directories
- Cleaner separation of concerns (blocks + fields in one plugin)
- Easier deployment (activate plugin = instant fields)

## MU-Plugin JSON Storage (TheKelsey Pattern)

TheKelsey stores ACF field groups in a must-use plugin (`thekelsey-custom`), ensuring fields load before themes and always remain active. The MU-plugin approach guarantees field availability regardless of plugin activation states, critical for sites where field groups define core data models. This pattern uses PHP namespacing and `__DIR__` for path resolution.

**Implementation (MU-Plugin Context):**

```php
// thekelsey-custom.php (lines 79-94)
namespace Kelsey\Custom;

function acf_json_save_point( $path ) {
    $path = __DIR__ . '/acf-json';
    return $path;
}
add_filter('acf/settings/save_json', __NAMESPACE__ . '\\acf_json_save_point');

function acf_json_load_point( $paths ) {
    $paths[] = __DIR__ . '/acf-json';
    return $paths;
}
add_filter('acf/settings/load_json',  __NAMESPACE__ . '\\acf_json_load_point');
```

**Directory Structure:**

```
mu-plugins/
└── thekelsey-custom/
    ├── acf-json/
    │   ├── group_5f91b18180b23.json  (Text and Aside)
    │   ├── group_5f92614100be4.json  (Social Media)
    │   └── [27 more JSON files]
    └── thekelsey-custom.php
```

**Why MU-Plugin-Based:**
- Fields always load (MU-plugins cannot be deactivated)
- Loads before regular plugins and themes
- Suitable for core site functionality
- Simpler path resolution with `__DIR__`

## Key Implementation Differences

The two patterns differ in parameter handling and path resolution but achieve identical functionality. Airbnb uses `plugin_dir_path(__FILE__)` for dynamic path resolution in a regular plugin, returning a single path string. TheKelsey uses `__DIR__` in a namespaced MU-plugin, appending to the existing paths array.

**Save Filter Comparison:**

```php
// Airbnb: Single path return (overwrites default)
function acf_json_save_point() {
  $path = plugin_dir_path(__FILE__) . 'acf-json';
  return $path;  // No parameter, returns string
}

// TheKelsey: Parameter-aware (overwrites default)
function acf_json_save_point( $path ) {
    $path = __DIR__ . '/acf-json';
    return $path;  // Receives $path, returns string
}
```

**Load Filter Comparison:**

```php
// Airbnb: Array initialization
function acf_json_load_point() {
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json';
  return $paths;  // Creates new array
}

// TheKelsey: Array append
function acf_json_load_point( $paths ) {
    $paths[] = __DIR__ . '/acf-json';
    return $paths;  // Appends to existing array
}
```

Both approaches work identically. TheKelsey's parameter-aware syntax is more explicit, while Airbnb's approach is more concise.

## Git Integration Workflow

ACF JSON storage enables seamless Git workflows where field group changes are committed alongside code. When a developer modifies fields in the WordPress admin, ACF writes changes to JSON files immediately. The developer commits these JSON files, and teammates pull updates that sync automatically on their local environments.

**Standard Workflow:**

```bash
# 1. Developer A modifies field group in WordPress admin
# ACF automatically writes to acf-json/group_xyz.json

# 2. Developer A commits field changes
git add mu-plugins/thekelsey-custom/acf-json/
git commit -m "Add event date field to Event post type"
git push

# 3. Developer B pulls changes
git pull

# 4. ACF detects JSON changes on next admin page load
# Shows "Sync available" notice in Field Groups screen
# Developer B clicks "Sync" to import changes to database
```

**Modified Timestamp Tracking:**

```json
{
  "key": "group_5f91b18180b23",
  "title": "Text and Aside",
  "fields": [...],
  "modified": 1604004336
}
```

ACF compares `modified` timestamps in JSON files against database records to detect sync requirements.

## JSON File Naming Convention

ACF generates JSON filenames using the field group key (`group_{hash}.json`), ensuring unique identifiers that prevent naming collisions. The hash derives from the field group's creation timestamp and WordPress site URL, creating globally unique keys across environments. Human-readable field group titles appear only in the JSON content, not filenames.

**Example Filenames:**

```
group_680ad6fe615b8.json  → "Logo Cloud Block"
group_67afe69c6c17a.json  → "FAQ Block"
group_5f91b18180b23.json  → "Text and Aside"
group_5f92614100be4.json  → "Social Media Options"
```

**Why Hashes:** Prevents filename conflicts when multiple developers create field groups simultaneously, avoids issues with special characters in titles, ensures consistent naming across environments.

## Multiple JSON Directories

WordPress sites can load ACF field groups from multiple directories simultaneously by returning an array of paths in the load filter. This enables multi-plugin architectures where each plugin maintains its own field definitions. Airbnb's multisite setup demonstrates this pattern across themes and plugins.

**Multi-Path Loading Example:**

```php
function acf_json_load_multiple_paths( $paths ) {
    // Load from MU-plugin
    $paths[] = WP_CONTENT_DIR . '/mu-plugins/site-core/acf-json';

    // Load from custom plugin
    $paths[] = plugin_dir_path(__FILE__) . 'acf-json';

    // Load from parent theme
    $paths[] = get_template_directory() . '/acf-json';

    // Load from child theme (overrides)
    $paths[] = get_stylesheet_directory() . '/acf-json';

    return $paths;
}
add_filter('acf/settings/load_json', 'acf_json_load_multiple_paths');
```

**Path Priority:** Later paths in the array override earlier paths if field group keys match (child theme overrides parent theme).

## Conflict Resolution

When identical field group keys exist in multiple JSON directories, ACF loads the last path in the array, enabling child themes or site-specific plugins to override core field groups. This mechanism supports multi-site architectures where individual sites customize shared field groups without forking the base plugin.

**Override Strategy:**

```
1. Core plugin:     group_123.json (5 fields)
2. Child theme:     group_123.json (5 fields + 2 additional fields)
   → ACF loads child theme version
```

**Caveat:** Overrides are all-or-nothing. Child themes must duplicate the entire field group, not just changed fields.

## Sync Workflow in Team Environments

ACF's JSON sync workflow prevents database drift in multi-developer teams. When JSON files change via Git pull, ACF compares JSON modified timestamps against database records. Developers see "Sync available" badges in the Field Groups admin screen, indicating which groups require synchronization.

**Sync States:**

- **Green dot:** JSON and database match (in sync)
- **Red dot + "Sync available":** JSON is newer (database outdated)
- **Yellow dot + "Update available":** Database is newer (JSON outdated - rare, usually indicates manual DB changes)

**Best Practice:** Always sync after pulling JSON changes before making further field modifications. This prevents overwriting teammates' changes.

## JSON Storage Benefits

ACF JSON storage transforms field groups from database-only entities into version-controlled configuration files. This shift enables code review of field changes, rollback via Git, automated deployments, and confidence that production field groups match tested configurations. All analyzed projects leverage this pattern for reliability.

**Key Benefits:**

1. **Version Control:** Field group changes visible in Git diffs, traceable to specific commits
2. **Code Review:** Field modifications go through pull request review like code
3. **Rollback:** `git revert` instantly restores previous field configurations
4. **Deployment:** Field groups deploy with code, no manual admin work
5. **Disaster Recovery:** Field groups backed up automatically via Git
6. **Environment Parity:** Identical field groups across dev, staging, production

## Common Pitfalls

JSON storage requires discipline around sync workflows. Developers who forget to sync after pulling changes risk overwriting teammates' field modifications. Sites with multiple custom JSON paths must ensure correct load order to avoid unexpected overrides. Manual database edits bypass JSON storage, creating drift that requires manual intervention.

**Anti-Patterns:**

- ❌ Editing field groups without pulling latest JSON
- ❌ Committing JSON without testing field changes
- ❌ Ignoring "Sync available" notices
- ❌ Manually editing JSON files (use WordPress admin)
- ❌ Mixing manual exports with JSON sync

## Security Considerations

ACF JSON files contain field group configurations but no user data or sensitive content. Files should be committed to Git and deployed to production like other code. However, sites using ACF options pages for API keys or credentials must ensure those values are not serialized into JSON files (they are not by default - JSON stores field definitions, not field values).

**What JSON Contains:**
- ✅ Field group titles and keys
- ✅ Field types and settings
- ✅ Location rules
- ✅ Display options

**What JSON Does NOT Contain:**
- ❌ Field values (actual content)
- ❌ User inputs
- ❌ API keys or credentials

## Related Patterns

- **ACF Field Naming Conventions** (snake_case PHP, camelCase GraphQL)
- **ACF Options Pages** (global settings with version-controlled definitions)
- **ACF Blocks Registration** (blocks + field groups in same plugin)
- **Location Rules Strategy** (template-based vs block-based)

## References

- ACF Documentation: [Local JSON](https://www.advancedcustomfields.com/resources/local-json/)
- Airbnb: `plugins/airbnb-policy-blocks/airbnb-policy-blocks.php` (lines 49-61)
- TheKelsey: `mu-plugins/thekelsey-custom/thekelsey-custom.php` (lines 79-94)
