---
title: "Output Escaping Patterns for WordPress XSS Prevention"
category: "wordpress-security"
subcategory: "xss-prevention"
tags: ["escaping", "xss", "esc_html", "esc_attr", "esc_url", "wp_kses"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Output Escaping Overview

WordPress output escaping prevents Cross-Site Scripting (XSS) attacks by encoding user-generated content before HTML rendering. Escaping converts dangerous characters (`<`, `>`, `"`, `'`) to HTML entities, preventing malicious scripts from executing in browsers.

**Core escaping functions:**
- `esc_html()`: HTML context (2,105 instances)
- `esc_attr()`: HTML attribute context (2,105 instances)
- `esc_url()`: URL context (1,121 instances)
- `wp_kses()`: Rich HTML with allowed tags (126 instances)
- `wp_kses_post()`: Post content HTML (384 instances)

**Total escaping calls:** 5,841 across WordPress VIP codebase (94.5% in airbnb)

**Critical rule:** Always escape output. Trust no data—not even your own database records.

## esc_html() for HTML Context

WordPress `esc_html()` escapes text output in HTML body context, converting `<`, `>`, `&`, `"`, `'` to HTML entities. The function prevents script injection while preserving display text integrity.

```php
// Pattern: Escape dynamic text in HTML
echo '<p>' . esc_html( $user_input ) . '</p>';

// Pattern: Escape translated strings with variables
echo esc_html( sprintf(
    __( 'Tried to alter %s %d through field "%s", which user is not permitted to edit.', 'fieldmanager' ),
    $post_type_obj->name,
    $value,
    $field->name
) );

// Pattern: Escape post title
<h1><?php echo esc_html( get_the_title() ); ?></h1>

// Pattern: Escape user meta
<p>Name: <?php echo esc_html( get_user_meta( $user_id, 'display_name', true ) ); ?></p>
```

**What esc_html() escapes:**
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#039;`

**Usage:** 2,105 instances (94.1% in airbnb)

**XSS attack prevented:**
```php
// Attacker input: <script>alert('XSS')</script>
$user_input = $_POST['comment'];

// ❌ Without escaping: Script executes!
echo '<p>' . $user_input . '</p>';
// Output: <p><script>alert('XSS')</script></p>

// ✅ With escaping: Script displayed as text
echo '<p>' . esc_html( $user_input ) . '</p>';
// Output: <p>&lt;script&gt;alert('XSS')&lt;/script&gt;</p>
```

## esc_attr() for HTML Attribute Context

WordPress `esc_attr()` escapes text output in HTML attribute context (class, id, data-*, etc.). The function prevents attribute injection and JavaScript event handlers from executing.

```php
// Pattern: Escape CSS class attribute
<div class="<?php echo esc_attr( $css_class ); ?>">

// Pattern: Escape data attribute
<div data-field-id="<?php echo esc_attr( $field_id ); ?>"
     data-field-name="<?php echo esc_attr( $field_name ); ?>">

// Pattern: Escape input value
<input type="text"
       name="user_name"
       value="<?php echo esc_attr( $user_name ); ?>" />

// Pattern: Escape title attribute
<a href="#" title="<?php echo esc_attr( $link_title ); ?>">
    <?php echo esc_html( $link_text ); ?>
</a>
```

**Usage:** 2,105 instances (94.6% in airbnb)

**XSS attack prevented:**
```php
// Attacker input: " onclick="alert('XSS')
$user_class = $_POST['custom_class'];

// ❌ Without escaping: JavaScript executes!
<div class="<?php echo $user_class; ?>">
// Output: <div class="" onclick="alert('XSS')">

// ✅ With escaping: Attribute value escaped
<div class="<?php echo esc_attr( $user_class ); ?>">
// Output: <div class="&quot; onclick=&quot;alert('XSS')">
```

## esc_url() for URL Context

WordPress `esc_url()` validates and escapes URLs, removing invalid protocols, JavaScript execution, and malicious URL patterns. The function ensures href and src attributes contain safe, clickable URLs.

```php
// Pattern: Escape anchor href
<a href="<?php echo esc_url( $redirect_url ); ?>">
    <?php echo esc_html( $link_text ); ?>
</a>

// Pattern: Escape image src
<img src="<?php echo esc_url( $image_url ); ?>"
     alt="<?php echo esc_attr( $image_alt ); ?>" />

// Pattern: Escape form action
<form action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>"
      method="post">

// Pattern: Escape redirect URL
wp_safe_redirect( esc_url_raw( $_POST['redirect_to'] ) );
```

**What esc_url() does:**
- Validates URL format
- Removes invalid protocols (javascript:, data:, vbscript:)
- Encodes special characters
- Adds http:// if protocol missing

**Usage:** 1,121 instances (94.2% in airbnb)

**XSS attack prevented:**
```php
// Attacker input: javascript:alert('XSS')
$redirect = $_POST['redirect_url'];

// ❌ Without escaping: JavaScript executes on click!
<a href="<?php echo $redirect; ?>">Click</a>
// Output: <a href="javascript:alert('XSS')">Click</a>

// ✅ With escaping: Invalid protocol removed
<a href="<?php echo esc_url( $redirect ); ?>">Click</a>
// Output: <a href="">Click</a>
```

## wp_kses() for Rich HTML

WordPress `wp_kses()` allows limited HTML tags while stripping dangerous elements (script, iframe, etc.). The function enables rich text formatting (bold, italic, links) while preventing XSS attacks.

```php
// Pattern: Allow specific HTML tags
$allowed_html = array(
    'a' => array(
        'href' => array(),
        'title' => array(),
        'class' => array(),
    ),
    'strong' => array(),
    'em' => array(),
    'p' => array(),
    'br' => array(),
);

$safe_html = wp_kses( $user_input, $allowed_html );
echo $safe_html; // Safe: Only allowed tags render

// Pattern: Use predefined allowed tags
$safe_html = wp_kses( $user_input, wp_kses_allowed_html( 'post' ) );

// Pattern: Allow no HTML (strip all tags)
$plain_text = wp_kses( $user_input, array() );
```

**Common allowed tag sets:**
- `wp_kses_allowed_html( 'post' )`: Post content tags (p, a, strong, em, ul, ol, li, img)
- `wp_kses_allowed_html( 'comment' )`: Comment tags (a, strong, em, code)
- Custom array: Specific tags for use case

**Usage:** 126 instances across WordPress VIP codebase

**XSS attack prevented:**
```php
// User input: <p>Hello <script>alert('XSS')</script> <strong>World</strong></p>

// ❌ Without filtering: Script executes!
echo $user_input;

// ✅ With wp_kses: Script removed, safe tags preserved
echo wp_kses( $user_input, wp_kses_allowed_html( 'post' ) );
// Output: <p>Hello  <strong>World</strong></p>
```

## wp_kses_post() for Post Content

WordPress `wp_kses_post()` escapes post content (post_content, post_excerpt) by allowing safe HTML tags used in WordPress editor. The function is wp_kses() with predefined 'post' allowed tags.

```php
// Pattern: Escape post content
$description = wp_kses_post( $post->post_content );
echo $description; // Safe: <p>, <strong>, <em>, <img>, <a>, etc. allowed

// Pattern: Escape user-submitted rich content
$bio = wp_kses_post( $_POST['user_bio'] );
update_user_meta( $user_id, 'bio', $bio );

// Pattern: Escape ACF wysiwyg field
$content = get_field( 'page_content' );
echo wp_kses_post( $content );
```

**Allowed tags in wp_kses_post():**
- Text formatting: `<p>`, `<strong>`, `<em>`, `<code>`, `<pre>`
- Lists: `<ul>`, `<ol>`, `<li>`
- Links: `<a>` (with href, title)
- Images: `<img>` (with src, alt, width, height)
- Headings: `<h1>` through `<h6>`
- Tables: `<table>`, `<tr>`, `<td>`, `<th>`

**Usage:** 384 instances across WordPress VIP codebase

## Escaping Context Selection

WordPress escaping function selection depends on output context (HTML body, attribute, URL, JavaScript). Wrong context escaping creates XSS vulnerabilities or breaks functionality.

**Context selection guide:**

| Context | Function | Example |
|---------|----------|---------|
| HTML body | `esc_html()` | `<p><?php echo esc_html( $text ); ?></p>` |
| HTML attribute | `esc_attr()` | `<div class="<?php echo esc_attr( $class ); ?>">` |
| URL/href | `esc_url()` | `<a href="<?php echo esc_url( $url ); ?>">` |
| Rich HTML | `wp_kses_post()` | `<?php echo wp_kses_post( $content ); ?>` |
| JavaScript | `wp_json_encode()` | `var data = <?php echo wp_json_encode( $data ); ?>;` |
| CSS | `esc_attr()` + validation | `style="color:<?php echo esc_attr( $color ); ?>"` |

```php
// ✅ Correct context escaping
<div class="<?php echo esc_attr( $class ); ?>">
    <h2><?php echo esc_html( $title ); ?></h2>
    <p><?php echo wp_kses_post( $content ); ?></p>
    <a href="<?php echo esc_url( $link ); ?>">Read More</a>
</div>

// ❌ Wrong context escaping
<div class="<?php echo esc_html( $class ); ?>">  <!-- Wrong: Use esc_attr() -->
    <a href="<?php echo esc_html( $link ); ?>">  <!-- Wrong: Use esc_url() -->
        <?php echo esc_url( $title ); ?>         <!-- Wrong: Use esc_html() -->
    </a>
</div>
```

## Translation + Escaping Pattern

WordPress combines translation functions (`__()`, `_e()`) with escaping functions using `esc_html__()`, `esc_html_e()`, `esc_attr__()`, etc. Combined functions translate and escape in single call.

```php
// Pattern: Translate + escape for HTML
echo esc_html__( 'Hello World', 'text-domain' );

// Pattern: Translate + escape + echo
esc_html_e( 'Submit Form', 'text-domain' );

// Pattern: Translate + escape for attribute
<input type="submit"
       value="<?php echo esc_attr__( 'Submit', 'text-domain' ); ?>" />

// Pattern: Translate with sprintf + escape
echo esc_html( sprintf(
    __( 'User %s has %d posts.', 'text-domain' ),
    $user_name,
    $post_count
) );
```

**Combined functions:**
- `esc_html__()`: Translate + escape HTML
- `esc_html_e()`: Translate + escape HTML + echo
- `esc_attr__()`: Translate + escape attribute
- `esc_attr_e()`: Translate + escape attribute + echo
- `esc_html_x()`: Translate with context + escape

## Late Escaping Principle

WordPress late escaping principle: Escape output as late as possible (immediately before echo), not during storage or processing. Early escaping causes double-escaping and breaks editing workflows.

```php
// ✅ Correct: Late escaping (at output)
$user_name = $_POST['name']; // Sanitize but don't escape
update_user_meta( $user_id, 'name', $user_name );

// Later, at output:
echo '<p>' . esc_html( get_user_meta( $user_id, 'name', true ) ) . '</p>';

// ❌ Wrong: Early escaping (at storage)
$user_name = esc_html( $_POST['name'] );
update_user_meta( $user_id, 'name', $user_name );
// Database stores: John &amp; Jane
// Output double-escapes: John &amp;amp; Jane
```

**Late escaping benefits:**
- Prevents double-escaping
- Preserves data integrity in database
- Enables context-appropriate escaping
- Simplifies data editing

## esc_url_raw() vs esc_url()

WordPress provides `esc_url_raw()` for database storage and `esc_url()` for HTML output. The functions differ in ampersand encoding for HTML context.

```php
// Pattern: Use esc_url_raw() for database storage
$redirect_url = esc_url_raw( $_POST['redirect_to'] );
update_option( 'redirect_url', $redirect_url );

// Pattern: Use esc_url() for HTML output
$redirect_url = get_option( 'redirect_url' );
echo '<a href="' . esc_url( $redirect_url ) . '">Redirect</a>';

// Pattern: Use esc_url_raw() for wp_redirect()
wp_redirect( esc_url_raw( $_POST['redirect_to'] ) );
exit;
```

**Difference:**
- `esc_url_raw()`: Preserves `&` (database, redirects, APIs)
- `esc_url()`: Converts `&` to `&amp;` (HTML output)

**Example:**
```php
$url = 'https://example.com/?foo=1&bar=2';

echo esc_url_raw( $url );
// Output: https://example.com/?foo=1&bar=2

echo esc_url( $url );
// Output: https://example.com/?foo=1&amp;bar=2
```

## wp_kses_allowed_html() Modification

WordPress allows modifying `wp_kses_allowed_html()` via filters for custom HTML requirements. Pattern adds allowed tags, attributes, or protocols for specific use cases.

```php
// Pattern: Add custom allowed tags
add_filter( 'wp_kses_allowed_html', function( $allowed, $context ) {
    if ( 'post' === $context ) {
        // Allow iframe for YouTube embeds
        $allowed['iframe'] = array(
            'src'             => true,
            'width'           => true,
            'height'          => true,
            'frameborder'     => true,
            'allowfullscreen' => true,
        );

        // Allow video tag
        $allowed['video'] = array(
            'src'      => true,
            'controls' => true,
            'width'    => true,
            'height'   => true,
        );
    }

    return $allowed;
}, 10, 2 );
```

**Usage:** 11 instances of custom kses filters across WordPress VIP codebase

## Escaping Anti-Patterns

WordPress output escaping requires consistent application across all dynamic content. Common anti-patterns create XSS vulnerabilities by bypassing or incorrectly applying escaping.

### Anti-Pattern: No Escaping

```php
// ❌ Critical: No escaping (XSS vulnerability!)
echo '<p>' . $user_input . '</p>';
echo '<div class="' . $css_class . '">';

// ✅ Correct: Escape all output
echo '<p>' . esc_html( $user_input ) . '</p>';
echo '<div class="' . esc_attr( $css_class ) . '">';
```

### Anti-Pattern: Wrong Context

```php
// ❌ Wrong: esc_html() in URL context
<a href="<?php echo esc_html( $url ); ?>">

// ✅ Correct: esc_url() in URL context
<a href="<?php echo esc_url( $url ); ?>">
```

### Anti-Pattern: Double Escaping

```php
// ❌ Wrong: Double escaping
$escaped_text = esc_html( $user_input );
update_post_meta( $post_id, 'text', $escaped_text );
echo esc_html( get_post_meta( $post_id, 'text', true ) ); // Double escaped!

// ✅ Correct: Escape only at output
update_post_meta( $post_id, 'text', $user_input );
echo esc_html( get_post_meta( $post_id, 'text', true ) );
```

### Anti-Pattern: Trust Database Data

```php
// ❌ Wrong: Assume database data is safe
echo '<p>' . get_post_meta( $post_id, 'user_input', true ) . '</p>';

// ✅ Correct: Escape database data (could be compromised)
echo '<p>' . esc_html( get_post_meta( $post_id, 'user_input', true ) ) . '</p>';
```
