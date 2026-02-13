---
title: "ACF JSON Storage with Custom Save/Load Points"
category: "wordpress-acf"
subcategory: "field-management"
tags: ["acf", "json-storage", "version-control", "git", "custom-paths"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Advanced Custom Fields (ACF) JSON storage enables version control of field groups by saving definitions as JSON files. Custom save/load points allow organizing ACF JSON files within plugins or mu-plugins instead of the theme directory, improving portability and maintainability.

WordPress projects analyzed show 100% adoption of custom JSON save/load points (165 field groups across 7 custom locations).

## Custom Save Point Configuration

ACF save points determine where field group JSON files are stored when edited in the WordPress admin.

### Plugin-Based Save Point Pattern

```php
// plugins/airbnb-policy-blocks/airbnb-policy-blocks.php
function acf_json_save_point() {
  $path = plugin_dir_path(__FILE__) . 'acf-json';
  return $path;
};
add_filter('acf/settings/save_json', 'acf_json_save_point');
```

**Benefits:**
- Field groups colocated with plugin functionality
- Atomic deploys: plugin + ACF config together
- Multisite safe: plugins can be network-activated with consistent ACF config

### MU-Plugin Save Point Pattern

```php
// mu-plugins/thekelsey-custom/thekelsey-custom.php
function acf_json_save_point( $path ) {
    $path = __DIR__ . '/acf-json';
    return $path;
}
add_filter('acf/settings/save_json', __NAMESPACE__ . '\\acf_json_save_point');
```

**Benefits:**
- Must-use plugins auto-activate: field groups always available
- Namespace safety: `__NAMESPACE__` prefix prevents function collisions
- `__DIR__` instead of `plugin_dir_path()` for cleaner mu-plugin code

## Custom Load Point Configuration

Load points tell ACF where to find JSON files. Multiple load paths can be registered to merge field groups from different locations.

### Single Path Load Pattern

```php
function acf_json_load_point( $paths ) {
  // Unset default ACF load path (theme directory)
  unset($paths[0]);

  // Add custom path
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json';

  return $paths;
};
add_filter('acf/settings/load_json', 'acf_json_load_point');
```

**Key Detail:** `unset($paths[0])` removes the default theme-based load path (`wp-content/themes/your-theme/acf-json`).

### Multi-Location Load Pattern

```php
function acf_json_load_point( $paths ) {
  // Keep default path (theme directory)
  // Add plugin path
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json';

  // Add mu-plugin path
  $paths[] = WP_CONTENT_DIR . '/mu-plugins/custom/acf-json';

  return $paths;
}
add_filter('acf/settings/load_json', 'acf_json_load_point');
```

**Use Case:** Load ACF configs from multiple sources (e.g., theme base fields + plugin-specific fields + multisite overrides).

## Directory Structure

ACF requires the `acf-json/` subfolder to exist. Field group files are named `group_{key}.json`.

### Example Plugin Structure

```
plugins/
  airbnb-policy-blocks/
    acf-json/
      group_680ad6fe615b8.json  ← Logo Cloud Block fields
      group_67afe69c6c17a.json  ← Featured Post Block fields
      group_676086739eefd.json  ← External News Block fields
    src/
      logo-cloud-block/
        block.json
        edit.js
        save.js
    airbnb-policy-blocks.php  ← Save/load hooks registered here
```

### Example MU-Plugin Structure

```
mu-plugins/
  thekelsey-custom/
    acf-json/
      group_5f91b18180b23.json  ← Text and Aside fields
      group_5f92614100be4.json  ← Event Registration fields
    thekelsey-custom.php  ← Save/load hooks registered here
    KelseyCustomTypesTaxonomies.class.php
```

## JSON File Naming Convention

ACF auto-generates filenames based on field group keys. Do not rename these files.

**Format:** `group_{field_group_key}.json`

**Example Keys:**
- `group_680ad6fe615b8` → Timestamp-based unique key (2024+)
- `group_5f91b18180b23` → Timestamp-based unique key (pre-2024)

**Warning:** Changing the filename breaks ACF's sync detection. Always let ACF manage file names.

## Git Workflow

ACF JSON files should be committed to version control. Field group edits in admin trigger file writes.

### Recommended .gitignore Pattern

```gitignore
# Commit ACF JSON files
!/plugins/*/acf-json/
!/mu-plugins/*/acf-json/
!/themes/*/acf-json/

# But ignore temp files
*.acf-backup
```

**Best Practice:** Review ACF JSON diffs before committing. Field group changes are highly readable in JSON format.

### Merge Conflict Resolution

ACF JSON conflicts occur when two developers edit the same field group. Resolve by:

1. Accept both changes locally
2. Load WordPress admin
3. ACF shows "Sync available" notice
4. Click "Sync" to import JSON → database
5. Field group now contains merged changes
6. Re-save field group to regenerate canonical JSON
7. Commit resolved JSON

## Multisite Configuration

WordPress VIP multisite deployments (8+ sites) benefit from conditional loading based on `blog_id`.

### Site-Specific ACF JSON

```php
function acf_json_save_point() {
  $blog_id = get_current_blog_id();
  return plugin_dir_path(__FILE__) . "acf-json/site-{$blog_id}";
};
add_filter('acf/settings/save_json', 'acf_json_save_point');

function acf_json_load_point( $paths ) {
  $blog_id = get_current_blog_id();

  // Load network-wide fields
  $paths[] = plugin_dir_path(__FILE__) . 'acf-json/network';

  // Load site-specific fields
  $paths[] = plugin_dir_path(__FILE__) . "acf-json/site-{$blog_id}";

  return $paths;
}
add_filter('acf/settings/load_json', 'acf_json_load_point');
```

**Structure:**
```
acf-json/
  network/          ← Shared across all sites
  site-1/           ← Site ID 1 overrides
  site-2/           ← Site ID 2 overrides
```

## Performance Considerations

JSON loading happens on every WordPress admin page load. Large field group collections can slow admin.

**Measured Performance (165 field groups):**
- JSON file count: 165 files
- Average file size: 3-8 KB
- Total storage: ~825 KB
- Load time impact: <50ms on modern hosting

**Optimization:** If managing 500+ field groups, consider:
- Splitting into multiple plugins
- Lazy-loading field groups via location rules
- Using ACF's local field group registration instead of JSON for rarely-edited fields

## Verification

Confirm ACF JSON is working correctly:

1. **Test Save:** Edit any field group → Save → Check `acf-json/` for updated timestamp
2. **Test Load:** Delete field group from database → ACF shows "Sync available" notice
3. **Test Git:** `git diff` shows readable JSON changes after field edits

**Expected Output (Save Success):**
```bash
$ ls -la plugins/airbnb-policy-blocks/acf-json/
-rw-r--r--  1 user  staff  5234 Feb 12 10:23 group_680ad6fe615b8.json
```

## Common Pitfalls

**Missing Directory:** If `acf-json/` folder doesn't exist, ACF silently falls back to default location. Create directory before registering filters.

**Incorrect Path:** `plugin_dir_path(__FILE__)` must be called from the main plugin file, not an included file. Use global variable if needed.

**No Unset:** Forgetting `unset($paths[0])` loads field groups from both theme AND custom location, causing duplicates.

**Permissions:** Ensure `acf-json/` is writable by web server (755 directory, 644 files for security).

## Related Patterns

- **ACF Blocks Registration:** Use plugin-based ACF JSON for block-specific field groups
- **WPGraphQL Integration:** JSON-stored field groups auto-expose `show_in_graphql` settings
- **VIP Deployment:** Custom save points prevent theme-coupled ACF config

**Source Projects:** airbnb (7 custom locations, 136 files), thekelsey-wp (1 mu-plugin location, 29 files)
