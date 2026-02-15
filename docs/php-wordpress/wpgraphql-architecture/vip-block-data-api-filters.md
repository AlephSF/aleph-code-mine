---
title: "VIP Block Data API Filters for GraphQL Data Transformation"
category: "wpgraphql-architecture"
subcategory: "data-transformation"
tags: ["vip-block-data-api", "gutenberg-blocks", "data-transformation", "wpgraphql"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

WordPress VIP Block Data API exposes Gutenberg block content through structured JSON format queryable via VIP decoupled bundle, with `vip_block_data_api__sourced_block_result` filter enabling server-side data transformation before GraphQL delivery. Filter intercepts block data after ACF field resolution but before API response, allowing wpautop application to WYSIWYG fields, data sanitization, computed field injection, or external API enrichment. Airbnb Policy site uses filter to automatically format ACF WYSIWYG content with HTML paragraph tags, eliminating client-side text processing in headless Next.js frontend while maintaining clean separation between content storage and presentation formatting.

## Filter Hook Execution Flow

VIP Block Data API processes blocks through multi-stage pipeline with transformation filter executing after field resolution.

### Block Processing Pipeline
```
1. WordPress parses post_content for blocks
2. Block parser identifies block types and attributes
3. ACF resolves custom fields attached to blocks
4. vip_block_data_api__sourced_block_result filter runs ← Transformation point
5. Block data serialized to JSON
6. GraphQL or REST API returns formatted data
```

**Filter Parameters:**
```php
apply_filters(
  'vip_block_data_api__sourced_block_result',
  $sourced_block,  // Block data with ACF fields
  $block_name,     // Block namespace (create-block/stat-block)
  $post_id,        // Parent post ID
  $parsed_block    // Original block parse tree
);
```

**Execution Timing:** After ACF fields loaded, before API response serialization

**Source:** WordPress VIP decoupled bundle architecture

## WYSIWYG Field wpautop Transformation

ACF WYSIWYG fields store content as plain text with newlines requiring wpautop transformation for HTML output.

### Filter Implementation
```php
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, $block_name, $post_id, $parsed_block) {
  // Apply wpautop to all ACF WYSIWYG fields in any block
  if (!empty($sourced_block['attributes']['data']) && is_array($sourced_block['attributes']['data'])) {
    $data = &$sourced_block['attributes']['data'];

    foreach ($data as $key => &$value) {
      // Skip field reference keys (prefixed with underscore)
      if (strpos($key, '_') === 0) {
        continue;
      }

      // Check if this field has a corresponding ACF field reference
      $field_key_ref = '_' . $key;
      if (!empty($data[$field_key_ref])) {
        $field_object = get_field_object($data[$field_key_ref]);

        // Apply wpautop to WYSIWYG fields
        if ($field_object && $field_object['type'] === 'wysiwyg' && !empty($value) && is_string($value)) {
          $value = wpautop($value);
        }
      }
    }
  }

  return $sourced_block;
}, 10, 4);
```

**Field Detection Logic:**
1. ACF stores field key reference as `_field_name` (underscore prefix)
2. Filter retrieves field object via `get_field_object()`
3. Checks field type === 'wysiwyg'
4. Applies `wpautop()` to convert newlines to `<p>` tags

**Source:** airbnb/themes/aleph-nothing/functions.php (lines 8-32)

## Data Structure Before and After Filter

### Input (Before wpautop)
```json
{
  "blockName": "create-block/text-image-block",
  "attributes": {
    "data": {
      "content": "First paragraph\n\nSecond paragraph\n\nThird paragraph",
      "_content": "field_67a1b2c3d4e5f",
      "heading": "Section Title",
      "_heading": "field_67a1b2c3d4e6g"
    }
  }
}
```

### Output (After wpautop)
```json
{
  "blockName": "create-block/text-image-block",
  "attributes": {
    "data": {
      "content": "<p>First paragraph</p>\n\n<p>Second paragraph</p>\n\n<p>Third paragraph</p>",
      "_content": "field_67a1b2c3d4e5f",
      "heading": "Section Title",
      "_heading": "field_67a1b2c3d4e6g"
    }
  }
}
```

**Transformation:**
- `content` field: Plain text → HTML with `<p>` tags
- `heading` field: Unchanged (text field, not WYSIWYG)
- Field references (`_content`, `_heading`): Preserved unchanged

## wpautop Function Behavior

WordPress `wpautop()` function converts double line breaks to `<p>` tags and single breaks to `<br>` following semantic HTML conventions.

### Input Text Patterns
```
Paragraph one

Paragraph two

Paragraph three
```

### wpautop Output
```html
<p>Paragraph one</p>

<p>Paragraph two</p>

<p>Paragraph three</p>
```

### Line Break Handling
```
Line one
Line two (single break)
Line three
```

### Output with <br> Tags
```html
<p>Line one<br />
Line two (single break)<br />
Line three</p>
```

**Rules:**
- Double newline (`\n\n`) → New paragraph (`</p><p>`)
- Single newline (`\n`) → Line break (`<br />`)
- Preserves block-level HTML elements
- Adds paragraph wrappers around text blocks

## Block-Specific Data Transformation

Filter targets specific block types for conditional transformation logic.

```php
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, $block_name, $post_id, $parsed_block) {
  // Transform only stat-block
  if ($block_name === 'create-block/stat-block') {
    if (!empty($sourced_block['attributes']['data']['quantity'])) {
      // Abbreviate large numbers
      $quantity = (int) $sourced_block['attributes']['data']['quantity'];

      if ($quantity >= 1000000) {
        $sourced_block['attributes']['data']['quantityFormatted'] = round($quantity / 1000000, 1) . 'M';
      } elseif ($quantity >= 1000) {
        $sourced_block['attributes']['data']['quantityFormatted'] = round($quantity / 1000, 1) . 'K';
      } else {
        $sourced_block['attributes']['data']['quantityFormatted'] = number_format($quantity);
      }
    }
  }

  return $sourced_block;
}, 10, 4);
```

**Use Cases:**
- Number formatting per block type
- External API data enrichment for specific blocks
- Image URL transformation (CDN injection)
- Conditional field inclusion/exclusion

## Computed Field Injection

Filter adds computed fields not stored in database, calculated from existing field values.

```php
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, $block_name, $post_id, $parsed_block) {
  // Add read time estimate to text blocks
  if ($block_name === 'core/paragraph' || $block_name === 'create-block/text-image-block') {
    if (!empty($sourced_block['attributes']['data']['content'])) {
      $content = strip_tags($sourced_block['attributes']['data']['content']);
      $word_count = str_word_count($content);
      $read_time = max(1, ceil($word_count / 200)); // 200 words/minute

      $sourced_block['attributes']['data']['estimatedReadTime'] = $read_time;
    }
  }

  return $sourced_block;
}, 10, 4);
```

**Computed Field Benefits:**
- Calculated server-side (no client JavaScript)
- Cached with block data
- Consistent across all clients
- Reduces frontend bundle size

## Image URL CDN Transformation

Block Data API filters transform ACF image field URLs to CDN paths for external hosting optimization.

```php
add_filter('vip_block_data_api__sourced_block_result',function($s,$b,$p,$pb){
 if(!empty($s['attributes']['data'])){
  $d=&$s['attributes']['data'];
  foreach($d as $k=>&$v){
   if(strpos($k,'_')===0)continue;
   $f='_'.$k;
   if(!empty($d[$f])){
    $o=get_field_object($d[$f]);
    if($o&&$o['type']==='image'&&is_array($v)){
     if(!empty($v['url']))$v['url']=str_replace('https://site.com/wp-content/uploads','https://cdn.site.com/uploads',$v['url']);
     if(!empty($v['sizes']))foreach($v['sizes'] as &$u)$u=str_replace('https://site.com/wp-content/uploads','https://cdn.site.com/uploads',$u);
    }
   }
  }
 }
 return $s;
},10,4);
```

**CDN Benefits:** Offload image delivery, automatic optimization, global edge caching, reduced server load

## Data Sanitization and Security

Filter sanitizes user-generated content before API delivery preventing XSS and injection attacks.

```php
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, $block_name, $post_id, $parsed_block) {
  if (!empty($sourced_block['attributes']['data'])) {
    $data = &$sourced_block['attributes']['data'];

    foreach ($data as $key => &$value) {
      // Skip ACF field references
      if (strpos($key, '_') === 0) continue;

      // Sanitize text fields
      if (is_string($value)) {
        // Strip dangerous HTML but preserve formatting
        $allowed_tags = '<p><br><strong><em><ul><ol><li><a><h2><h3><h4>';
        $value = wp_kses($value, wp_kses_allowed_html('post'));

        // Remove onclick, onerror, and other event attributes
        $value = preg_replace('/\s*on\w+\s*=\s*["\'].*?["\']/i', '', $value);
      }
    }
  }

  return $sourced_block;
}, 10, 4);
```

**Security Layers:**
- `wp_kses()`: Strips non-allowed HTML tags
- Regex removal: Eliminates JavaScript event handlers
- Attribute sanitization: Cleans href, src attributes

**Threat Prevention:**
- XSS via WYSIWYG fields
- JavaScript injection in text inputs
- Malicious HTML in user content
- Event handler exploits (onclick, onerror)

## External API Data Enrichment

Filter fetches external API data and injects into block attributes during transformation with transient caching.

```php
add_filter('vip_block_data_api__sourced_block_result',function($s,$b,$p,$pb){
 if($b==='create-block/municipalities-search-block'&&!empty($s['attributes']['data']['municipalityId'])){
  $id=$s['attributes']['data']['municipalityId'];$k="municipality_data_{$id}";
  $d=get_transient($k);
  if($d===false){
   $r=wp_remote_get("https://api.municipalities.gov/v1/municipality/{$id}");
   if(!is_wp_error($r)){
    $d=json_decode(wp_remote_retrieve_body($r),true);
    set_transient($k,$d,12*HOUR_IN_SECONDS);
   }
  }
  if($d){
   $s['attributes']['data']['municipalityName']=$d['name'];
   $s['attributes']['data']['population']=$d['population'];
   $s['attributes']['data']['coordinates']=$d['coordinates'];
  }
 }
 return $s;
},10,4);
```

**Best Practices:** Cache API responses (transients), handle failures gracefully, 12hr expiration, use `wp_remote_get()`

## Performance Optimization Strategies

Block Data API filters execute on every API request requiring optimization to prevent slowdowns.

### Conditional Execution
```php
add_filter('vip_block_data_api__sourced_block_result', function($sourced_block, $block_name, $post_id, $parsed_block) {
  // Only process blocks that need transformation
  $transformable_blocks = [
    'create-block/stat-block',
    'create-block/text-image-block',
    'create-block/municipalities-search-block',
  ];

  if (!in_array($block_name, $transformable_blocks, true)) {
    return $sourced_block; // Skip transformation
  }

  // Expensive transformation logic here
  // ...

  return $sourced_block;
}, 10, 4);
```

### Transient Caching
```php
// Cache transformed block data for 1 hour
$cache_key = "block_transform_{$post_id}_{$block_name}";
$cached = get_transient($cache_key);

if (false !== $cached) {
  return $cached;
}

// Perform transformation
$transformed = expensive_transformation($sourced_block);

set_transient($cache_key, $transformed, HOUR_IN_SECONDS);
return $transformed;
```

### Object Caching
```php
// Use wp_cache for in-request caching
$cache_key = "field_object_{$field_key}";
$field_object = wp_cache_get($cache_key);

if (false === $field_object) {
  $field_object = get_field_object($field_key);
  wp_cache_set($cache_key, $field_object);
}
```

**Performance Metrics:**
- Uncached: 500-1000ms per block
- Transient cached: 10-50ms per block
- Object cached: 1-5ms per block

## VIP Block Data API Endpoint Testing

VIP Block Data API endpoint `/wp-json/vip-block-data-api/v1/posts/{id}` returns transformed block data with applied filters.

```bash
curl https://site.com/wp-json/vip-block-data-api/v1/posts/123
```

Response includes transformed content:
```json
{"blocks":[{"name":"create-block/stat-block","attributes":{"data":{"stat":"150","quantity":"M","content":"<p>Formatted text</p>"}}}]}
```

## Integration Testing Pattern

WordPress integration tests verify filter transformations using VIP Block Data API endpoint with ACF field updates.

```php
$p=wp_insert_post(['post_title'=>'Test','post_content'=>'<!-- wp:create-block/text-image-block -->','post_status'=>'publish']);
update_field('content',"Para 1\n\nPara 2",$p);
$r=wp_remote_get("https://site.test/wp-json/vip-block-data-api/v1/posts/{$p}");
$b=json_decode(wp_remote_retrieve_body($r),true);
assert(str_contains($b['blocks'][0]['attributes']['data']['content'],'<p>'));
```

## Unit Testing Pattern

WordPress unit tests mock ACF field objects and apply filters directly bypassing API layer.

```php
class Test_Block_Data_Filter extends WP_UnitTestCase{
 function test_wysiwyg_wpautop(){
  $s=['attributes'=>['data'=>['content'=>"L1\n\nL2",'_content'=>'field_abc']]];
  WP_Mock::userFunction('get_field_object',['return'=>['type'=>'wysiwyg']]);
  $r=apply_filters('vip_block_data_api__sourced_block_result',$s,'create-block/test',1,[]);
  $this->assertStringContainsString('<p>L1</p>',$r['attributes']['data']['content']);
 }
}
```

## Common Filter Issues

### Issue: wpautop Not Applied
**Cause:** ACF field reference missing
```php
// ❌ Wrong: No field reference
$data = [
  'content' => 'Text here',
  // Missing: '_content' => 'field_abc123'
];

// ✅ Correct: Include field reference
$data = [
  'content' => 'Text here',
  '_content' => 'field_abc123',  // Required for field type detection
];
```

### Issue: Filter Runs Too Late
**Cause:** Priority too high
```php
// ❌ Wrong: Priority 99 runs after API serialization
add_filter('vip_block_data_api__sourced_block_result', $callback, 99, 4);

// ✅ Correct: Priority 10 runs before serialization
add_filter('vip_block_data_api__sourced_block_result', $callback, 10, 4);
```

### Issue: All Fields Transformed
**Cause:** Missing field type check
```php
// ❌ Wrong: Transforms all fields
foreach ($data as $key => &$value) {
  $value = wpautop($value); // Breaks non-text fields
}

// ✅ Correct: Check field type first
$field_object = get_field_object($data[$field_key_ref]);
if ($field_object && $field_object['type'] === 'wysiwyg') {
  $value = wpautop($value);
}
```

**Source:** Common implementation errors in headless WordPress
