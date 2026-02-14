---
title: "Input Sanitization Patterns for WordPress"
category: "wordpress-security"
subcategory: "data-validation"
tags: ["sanitization", "input-validation", "xss-prevention", "sql-injection", "security"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Input Sanitization Overview

WordPress input sanitization removes malicious code, invalid characters, and unexpected data formats from user inputs before processing or storage. Sanitization prevents SQL injection, XSS attacks, and code injection vulnerabilities by normalizing $_POST, $_GET, and $_REQUEST data.

**Core sanitization functions:**
- `sanitize_text_field()`: Text inputs, $_POST/$_GET (385 instances)
- `sanitize_email()`: Email addresses (5 instances)
- `sanitize_key()`: Array keys, slugs (157 instances)
- `sanitize_title()`: Post titles, slugs (76 instances)

**Critical rule:** Always sanitize user inputs before database operations, logic decisions, or HTML output.

## sanitize_text_field() Pattern

WordPress `sanitize_text_field()` removes tags, strips line breaks, and trims whitespace from text inputs. The function sanitizes $_POST/$_GET form fields, AJAX parameters, and query string values.

```php
// Pattern: Sanitize $_POST data before use
$search_term = sanitize_text_field( $_POST['fm_autocomplete_search'] );
$items = $this->get_items_for_ajax( $search_term );

// Pattern: Sanitize context/subcontext from AJAX requests
$subcontext = !empty( $_POST['fm_subcontext'] )
    ? sanitize_text_field( $_POST['fm_subcontext'] )
    : null;

$calculated_context = array(
    sanitize_text_field( $_POST['fm_context'] ),
    $subcontext
);

// Pattern: Sanitize inline-save (Quick Edit) post type
if ( 'edit-post' === $_POST['screen'] && 'inline-save' === $_POST['action'] ) {
    $calculated_context = array(
        'quickedit',
        sanitize_text_field( $_POST['post_type'] )
    );
}
```

**What sanitize_text_field() removes:**
- HTML tags (`<script>`, `<iframe>`, etc.)
- Line breaks (`\n`, `\r`)
- Leading/trailing whitespace
- Null bytes (`\0`)

**Usage:** 385 instances across WordPress VIP codebase (97.7% in airbnb)

## sanitize_email() Pattern

WordPress `sanitize_email()` validates and sanitizes email addresses, removing illegal characters and validating format. The function ensures email inputs match RFC standards before storage or email delivery.

```php
// Pattern: Sanitize email input
$user_email = sanitize_email( $_POST['user_email'] );
if ( ! is_email( $user_email ) ) {
    wp_die( 'Invalid email address' );
}

// Pattern: Sanitize email before wp_mail()
$to = sanitize_email( $_POST['contact_email'] );
wp_mail( $to, $subject, $message );

// Pattern: Sanitize email before user creation
$user_data = array(
    'user_login' => sanitize_user( $_POST['username'] ),
    'user_email' => sanitize_email( $_POST['email'] ),
    'user_pass'  => $_POST['password'], // Never sanitize passwords!
);
wp_insert_user( $user_data );
```

**What sanitize_email() removes:**
- Whitespace
- Illegal email characters
- Multiple @ symbols
- Invalid domain characters

**Usage:** 5 instances across WordPress VIP codebase

## sanitize_key() Pattern

WordPress `sanitize_key()` sanitizes slugs, array keys, and option names by converting to lowercase, removing special characters, and replacing spaces with dashes. The function ensures keys work in URLs, databases, and option storage.

```php
// Pattern: Sanitize option key
$option_key = sanitize_key( $_POST['option_name'] );
update_option( $option_key, $value );

// Pattern: Sanitize transient key
$cache_key = sanitize_key( 'user_data_' . $_POST['user_id'] );
set_transient( $cache_key, $data, 3600 );

// Pattern: Sanitize array key for dynamic data
$field_key = sanitize_key( $_POST['field_name'] );
$field_values[ $field_key ] = $_POST['field_value'];

// Pattern: Sanitize slug for custom taxonomy
$term_slug = sanitize_key( $_POST['term_name'] );
wp_insert_term( $_POST['term_name'], $taxonomy, array('slug' => $term_slug) );
```

**What sanitize_key() does:**
- Converts to lowercase
- Replaces spaces with dashes
- Removes special characters
- Limits to alphanumeric + dash + underscore

**Usage:** 157 instances across WordPress VIP codebase

## sanitize_title() Pattern

WordPress `sanitize_title()` sanitizes post titles, category names, and custom slugs for URL compatibility. The function converts titles to lowercase, replaces spaces with hyphens, and removes special characters.

```php
// Pattern: Sanitize custom slug
$post_slug = sanitize_title( $_POST['custom_slug'] );
wp_update_post( array(
    'ID'        => $post_id,
    'post_name' => $post_slug,
) );

// Pattern: Sanitize term slug
$term_slug = sanitize_title( $_POST['category_name'] );
wp_insert_term( $_POST['category_name'], 'category', array(
    'slug' => $term_slug,
) );

// Pattern: Generate filename from title
$filename = sanitize_title( $_POST['document_title'] ) . '.pdf';
```

**What sanitize_title() does:**
- Converts to lowercase
- Replaces spaces with hyphens
- Removes accented characters (ü → u)
- Removes special characters
- Limits to alphanumeric + dash

**Usage:** 76 instances across WordPress VIP codebase

## Sanitization Function Selection

WordPress provides specialized sanitization functions for different data types. Correct function selection prevents over-sanitization (data loss) and under-sanitization (security vulnerabilities).

**Selection guide:**
- **Text inputs:** `sanitize_text_field()` (names, addresses)
- **Multi-line text:** `sanitize_textarea_field()` (descriptions)
- **Emails:** `sanitize_email()` (email addresses)
- **URLs:** `esc_url_raw()` (URLs without display encoding)
- **Filenames:** `sanitize_file_name()` (upload filenames)
- **Keys/slugs:** `sanitize_key()` (option keys, transient keys)
- **Titles:** `sanitize_title()` (post slugs, term slugs)
- **HTML:** `wp_kses()` or `wp_kses_post()` (rich text)
- **Usernames:** `sanitize_user()` (login usernames)
- **Meta keys:** `sanitize_meta()` (post meta, user meta)

```php
// ✅ Correct function selection
$name = sanitize_text_field( $_POST['name'] );
$bio = sanitize_textarea_field( $_POST['bio'] );
$email = sanitize_email( $_POST['email'] );
$website = esc_url_raw( $_POST['website'] );
$slug = sanitize_key( $_POST['slug'] );
$rich_content = wp_kses_post( $_POST['content'] );

// ❌ Wrong function selection
$email = sanitize_text_field( $_POST['email'] );     // Use sanitize_email()
$html = sanitize_text_field( $_POST['content'] );    // Strips HTML (data loss)
$url = sanitize_text_field( $_POST['website'] );     // Use esc_url_raw()
```

## $_POST/$_GET Sanitization Pattern

WordPress best practice sanitizes $_POST and $_GET immediately after access, before variable assignment or logic decisions. Early sanitization prevents unsanitized data from propagating through codebase.

```php
// ✅ Best practice: Sanitize immediately
$post_type = sanitize_text_field( $_POST['post_type'] );
$taxonomy = sanitize_text_field( $_POST['taxonomy'] );

if ( $post_type === 'page' ) {
    process_page( $post_type );
}

// ❌ Anti-pattern: Sanitize late (unsanitized data in logic)
if ( $_POST['post_type'] === 'page' ) { // Unsanitized!
    $post_type = sanitize_text_field( $_POST['post_type'] );
    process_page( $post_type );
}

// ❌ Anti-pattern: Never sanitize
$post_type = $_POST['post_type']; // Critical security issue!
process_page( $post_type );
```

**Critical security gap:** 677 instances of direct $_POST usage without sanitization detected across codebase.

## Sanitization + Validation Pattern

WordPress security combines sanitization (cleaning data) with validation (rejecting invalid data). Sanitization normalizes input, validation ensures business logic requirements.

```php
// Pattern: Sanitize then validate
$user_id = absint( $_POST['user_id'] ); // Sanitize: Convert to positive integer
if ( ! $user_id || ! user_can( $user_id, 'edit_posts' ) ) {
    wp_die( 'Invalid user or insufficient permissions' );
}

// Pattern: Sanitize email then validate format
$email = sanitize_email( $_POST['email'] );
if ( ! is_email( $email ) ) {
    wp_send_json_error( 'Invalid email format' );
}

// Pattern: Sanitize then check against whitelist
$post_status = sanitize_key( $_POST['status'] );
$allowed_statuses = array('publish', 'draft', 'pending');
if ( ! in_array( $post_status, $allowed_statuses, true ) ) {
    wp_die( 'Invalid post status' );
}
```

**Validation functions:**
- `is_email()`: Validate email format
- `absint()`: Convert to positive integer
- `in_array( $value, $whitelist, true )`: Whitelist validation
- `preg_match()`: Regex validation

## wp_unslash() for Magic Quotes

WordPress `wp_unslash()` strips slashes added by legacy magic quotes settings. Modern WordPress automatically applies slashes to $_POST/$_GET/$_REQUEST; sanitization functions expect unslashed data.

```php
// Pattern: Unslash before sanitization
$nonce = wp_unslash( $_POST['nonce'] );
if ( ! wp_verify_nonce( sanitize_text_field( $nonce ), 'my-action' ) ) {
    wp_die( 'Nonce verification failed' );
}

// Pattern: Unslash nested POST data
$data = wp_unslash( $_POST['form_data'] );
$name = sanitize_text_field( $data['name'] );
$email = sanitize_email( $data['email'] );

// Pattern: Combined unslash + sanitize
$search = sanitize_text_field( wp_unslash( $_POST['search'] ) );
```

**When to use wp_unslash():**
- Before nonce verification
- Before JSON decoding
- Before exact string matching
- For nested $_POST arrays

## Array Input Sanitization

WordPress sanitizes array inputs by mapping sanitization functions over array values. Pattern prevents unsanitized data in $_POST arrays (checkboxes, multi-selects).

```php
// Pattern: Sanitize array of text fields
$selected_ids = array_map( 'absint', $_POST['selected_ids'] );
foreach ( $selected_ids as $id ) {
    // $id is now sanitized integer
}

// Pattern: Sanitize array of post types
$post_types = array_map( 'sanitize_key', $_POST['post_types'] );
if ( in_array( 'page', $post_types, true ) ) {
    // Process pages
}

// Pattern: Sanitize associative array
$form_data = array();
foreach ( $_POST['fields'] as $key => $value ) {
    $form_data[ sanitize_key( $key ) ] = sanitize_text_field( $value );
}
```

**Common array sanitization:**
- `array_map( 'absint', $array )`: Integer arrays (IDs)
- `array_map( 'sanitize_text_field', $array )`: Text arrays
- `array_map( 'sanitize_key', $array )`: Key/slug arrays

## Password Handling (Never Sanitize!)

WordPress password inputs must NEVER be sanitized. Sanitization removes special characters users intentionally include for password strength. Hash passwords without modification.

```php
// ✅ Correct: Hash password without sanitization
$password = $_POST['password']; // Do NOT sanitize!
$hashed = wp_hash_password( $password );

// ❌ WRONG: Sanitizing password removes special characters
$password = sanitize_text_field( $_POST['password'] ); // Breaks passwords!
$hashed = wp_hash_password( $password );

// ✅ Correct: User creation with unsanitized password
$user_data = array(
    'user_login' => sanitize_user( $_POST['username'] ),
    'user_email' => sanitize_email( $_POST['email'] ),
    'user_pass'  => $_POST['password'], // Never sanitize!
);
wp_insert_user( $user_data );
```

**Never sanitize:**
- Passwords
- Password hashes
- Cryptographic tokens
- Binary data

## Sanitization Anti-Patterns

WordPress security requires consistent sanitization across all user inputs. Common anti-patterns bypass sanitization, introducing SQL injection and XSS vulnerabilities.

### Anti-Pattern: Direct Superglobal Access

```php
// ❌ Critical issue: Direct $_POST usage
$user_id = $_POST['user_id'];
$post = get_post( $user_id ); // SQL injection risk!

// ✅ Correct: Sanitize before use
$user_id = absint( $_POST['user_id'] );
$post = get_post( $user_id );
```

### Anti-Pattern: Conditional Sanitization

```php
// ❌ Wrong: Sanitization inside conditional
if ( isset( $_POST['email'] ) ) {
    $email = sanitize_email( $_POST['email'] );
}
// $email may be unset or unsanitized!

// ✅ Correct: Sanitize with fallback
$email = isset( $_POST['email'] )
    ? sanitize_email( $_POST['email'] )
    : '';
```

### Anti-Pattern: Sanitize After Use

```php
// ❌ Wrong: Logic uses unsanitized data
if ( $_POST['action'] === 'delete' ) { // Unsanitized!
    $action = sanitize_key( $_POST['action'] );
}

// ✅ Correct: Sanitize before logic
$action = sanitize_key( $_POST['action'] );
if ( $action === 'delete' ) {
    // Process deletion
}
```
