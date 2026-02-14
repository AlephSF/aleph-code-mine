---
title: "Nonce Verification Patterns for WordPress CSRF Prevention"
category: "wordpress-security"
subcategory: "csrf-prevention"
tags: ["nonce", "csrf", "wp_verify_nonce", "check_ajax_referer", "security"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## WordPress Nonce Overview

WordPress nonces (Number Used Once) prevent Cross-Site Request Forgery (CSRF) attacks by validating that form submissions and AJAX requests originate from authenticated users on the site. Nonces are time-limited, user-specific tokens that expire after 12-24 hours.

**Core nonce functions:**
- `wp_create_nonce()`: Generate nonce (142 instances)
- `wp_verify_nonce()`: Verify nonce (119 instances)
- `check_ajax_referer()`: AJAX nonce verification (77 instances)
- `check_admin_referer()`: Admin form nonce verification (124 instances)

**Total nonce operations:** 462 across WordPress VIP codebase (94.2% in airbnb)

**Critical rule:** All state-changing operations (POST, PUT, DELETE) require nonce verification.

## wp_create_nonce() + wp_verify_nonce() Pattern

WordPress nonces use action-based verification. `wp_create_nonce()` generates token for specific action, `wp_verify_nonce()` validates token matches action and user.

```php
// Pattern: Create nonce for form
<form method="post">
    <input type="hidden"
           name="fieldmanager-<?php echo $this->fm->name; ?>-nonce"
           value="<?php echo wp_create_nonce( 'fieldmanager-save-' . $this->fm->name ); ?>" />
    <!-- Form fields -->
    <button type="submit">Save</button>
</form>

// Pattern: Verify nonce on form submission
public function save_page_form() {
    $nonce_field = 'fieldmanager-' . $this->fm->name . '-nonce';
    $nonce_action = 'fieldmanager-save-' . $this->fm->name;

    if ( ! wp_verify_nonce( $_POST[$nonce_field], $nonce_action ) ) {
        $this->fm->_unauthorized_access( __( 'Nonce validation failed', 'fieldmanager' ) );
        return;
    }

    // Safe to process form (nonce verified)
    $this->fm->save_fields( $post_id, $_POST );
}
```

**Nonce characteristics:**
- **User-specific:** Different users generate different nonces for same action
- **Time-limited:** Expires after 12-24 hours (default)
- **Action-specific:** Nonce for 'delete-post' won't validate for 'update-post'

**Usage:** 142 creates + 119 verifications across WordPress VIP codebase

## Nonce Naming Conventions

WordPress nonce naming follows consistent patterns for field names and action names. Consistent naming improves code readability and prevents action collision.

**Naming pattern:**
- **Field name:** `{context}-{identifier}-nonce`
- **Action name:** `{context}-{action}-{identifier}`

```php
// Pattern: Field manager nonces
$nonce_field = 'fieldmanager-' . $this->fm->name . '-nonce';
$nonce_action = 'fieldmanager-save-' . $this->fm->name;

// Example: Field manager post_meta
// Field: fieldmanager-post_meta-nonce
// Action: fieldmanager-save-post_meta

// Pattern: Custom settings page
$nonce_field = 'settings-page-nonce';
$nonce_action = 'update-settings-page';

// Pattern: Delete post action
$nonce_field = 'delete-post-' . $post_id . '-nonce';
$nonce_action = 'delete-post-' . $post_id;
```

**Benefits:**
- Prevents action name collisions
- Self-documenting code
- Consistent error messages
- Easy debugging

## check_ajax_referer() Pattern

WordPress AJAX requests use `check_ajax_referer()` for automatic nonce verification with die-on-failure behavior. The function verifies nonce and terminates request if validation fails.

```php
// Frontend: Create AJAX nonce
wp_localize_script( 'my-ajax-script', 'myAjax', array(
    'ajaxurl' => admin_url( 'admin-ajax.php' ),
    'nonce'   => wp_create_nonce( 'my-ajax-action' ),
) );

// JavaScript: Send nonce with AJAX request
jQuery.post(
    myAjax.ajaxurl,
    {
        action: 'my_ajax_handler',
        nonce: myAjax.nonce,
        data: formData
    },
    function(response) {
        console.log(response);
    }
);

// Backend: Verify AJAX nonce
add_action( 'wp_ajax_my_ajax_handler', 'my_ajax_handler' );
function my_ajax_handler() {
    check_ajax_referer( 'my-ajax-action', 'nonce' );

    // Safe to process AJAX request (nonce verified)
    $result = process_ajax_data( $_POST['data'] );
    wp_send_json_success( $result );
}
```

**check_ajax_referer() parameters:**
- **$action:** Nonce action name (e.g., 'my-ajax-action')
- **$query_arg:** $_REQUEST key containing nonce (default: '_ajax_nonce')
- **$die:** Whether to die on failure (default: true)

**Usage:** 77 instances across WordPress VIP codebase

**Auto-termination behavior:**
```php
// Nonce verification fails:
check_ajax_referer( 'my-ajax-action', 'nonce' );
// Output: -1 (dies immediately)
```

## check_admin_referer() Pattern

WordPress admin forms use `check_admin_referer()` for combined nonce + HTTP referer verification. The function ensures requests originate from site admin pages.

```php
// Pattern: Create admin referer nonce
<form method="post" action="<?php echo admin_url( 'admin-post.php' ); ?>">
    <?php wp_nonce_field( 'process-settings' ); ?>
    <input type="hidden" name="action" value="process_settings" />
    <!-- Form fields -->
    <button type="submit">Save Settings</button>
</form>

// Pattern: Verify admin referer
add_action( 'admin_post_process_settings', 'process_settings_handler' );
function process_settings_handler() {
    check_admin_referer( 'process-settings' );

    // Safe to process settings (nonce + referer verified)
    update_option( 'site_settings', $_POST['settings'] );

    wp_safe_redirect( admin_url( 'options-general.php?updated=1' ) );
    exit;
}
```

**check_admin_referer() verification:**
1. Verifies nonce from `$_REQUEST['_wpnonce']`
2. Verifies HTTP referer contains admin_url()
3. Dies with error if either check fails

**Usage:** 124 instances across WordPress VIP codebase

**wp_nonce_field() helper:**
```php
// wp_nonce_field() generates hidden input automatically
<?php wp_nonce_field( 'my-action', 'my-nonce-field' ); ?>
// Outputs: <input type="hidden" name="my-nonce-field" value="..." />
```

## wp_verify_nonce() with wp_unslash()

WordPress automatically adds slashes to $_POST/$_GET (legacy magic quotes). Nonce verification requires unslashing before sanitization.

```php
// Pattern: Unslash + sanitize before nonce verification
public function ajax_dismiss_promo() {
    // Verify nonce
    if ( ! isset( $_POST['nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['nonce'] ) ), self::AJAX_ACTION ) ) {
        wp_send_json_error( [ 'message' => __( 'Invalid nonce', 'simple-history' ) ], 403 );
    }

    // Process AJAX request (nonce verified)
    update_user_meta( get_current_user_id(), 'dismissed_promo', true );
    wp_send_json_success();
}
```

**Order of operations:**
1. `wp_unslash()`: Remove magic quotes slashes
2. `sanitize_text_field()`: Clean nonce value
3. `wp_verify_nonce()`: Validate against action

## Nonce URL Parameters

WordPress nonces can be added to URLs for GET request protection (delete links, status toggles). URL nonces use `wp_create_nonce()` + `wp_nonce_url()` helpers.

```php
// Pattern: Create nonce URL
$delete_url = wp_nonce_url(
    admin_url( 'admin-post.php?action=delete_post&post_id=' . $post_id ),
    'delete-post-' . $post_id,
    'nonce'
);

echo '<a href="' . esc_url( $delete_url ) . '">Delete Post</a>';
// Outputs: .../admin-post.php?action=delete_post&post_id=123&nonce=abc123...

// Pattern: Verify nonce from URL
add_action( 'admin_post_delete_post', 'delete_post_handler' );
function delete_post_handler() {
    $post_id = absint( $_GET['post_id'] );
    $nonce = sanitize_text_field( $_GET['nonce'] );

    if ( ! wp_verify_nonce( $nonce, 'delete-post-' . $post_id ) ) {
        wp_die( 'Invalid nonce' );
    }

    wp_delete_post( $post_id );
    wp_safe_redirect( admin_url( 'edit.php?deleted=1' ) );
    exit;
}
```

**wp_nonce_url() parameters:**
- **$actionurl:** Base URL
- **$action:** Nonce action name
- **$name:** URL parameter name (default: '_wpnonce')

## Nonce Lifetime Configuration

WordPress nonce lifetime defaults to 12-24 hours (two ticks). Custom nonce lifetimes use `nonce_life` filter for long-form edits or quick-expiring tokens.

```php
// Pattern: Extend nonce lifetime to 7 days
add_filter( 'nonce_life', function() {
    return 7 * DAY_IN_SECONDS; // 7 days
} );

// Pattern: Shorten nonce lifetime to 1 hour
add_filter( 'nonce_life', function() {
    return HOUR_IN_SECONDS; // 1 hour
} );

// Pattern: Context-specific nonce lifetime
add_filter( 'nonce_life', function( $life ) {
    if ( isset( $_POST['long_form'] ) ) {
        return 2 * DAY_IN_SECONDS; // 2 days for long forms
    }
    return $life; // Default for other nonces
} );
```

**Default nonce lifetime:**
- **Tick 1:** 0-12 hours (from creation)
- **Tick 2:** 12-24 hours (grace period)
- **Expired:** After 24 hours

## Nonce Verification Return Values

WordPress `wp_verify_nonce()` returns false (invalid) or tick number (valid). Advanced patterns use tick number for strict validation or time-based logic.

```php
// Pattern: Standard verification (false or truthy)
if ( ! wp_verify_nonce( $_POST['nonce'], 'my-action' ) ) {
    wp_die( 'Nonce verification failed' );
}

// Pattern: Strict verification (only tick 1)
$tick = wp_verify_nonce( $_POST['nonce'], 'my-action' );
if ( 1 !== $tick ) {
    wp_die( 'Nonce expired or invalid' );
}

// Pattern: Allow tick 1 or 2
$tick = wp_verify_nonce( $_POST['nonce'], 'my-action' );
if ( ! in_array( $tick, array( 1, 2 ), true ) ) {
    wp_die( 'Nonce verification failed' );
}
```

**Return values:**
- **false:** Invalid nonce (wrong action, expired, tampered)
- **1:** Valid (tick 1, created 0-12 hours ago)
- **2:** Valid (tick 2, created 12-24 hours ago, grace period)

## Nonce + Capability Check Pattern

WordPress security combines nonce verification (request authenticity) with capability checks (user authorization). Layered security prevents CSRF and unauthorized access.

```php
// Pattern: Nonce + capability check
public function save_user_profile() {
    // Layer 1: Verify nonce (CSRF protection)
    if ( ! wp_verify_nonce( $_POST['user-nonce'], 'update-user-' . $user_id ) ) {
        wp_die( 'Nonce verification failed' );
    }

    // Layer 2: Check capability (authorization)
    if ( ! current_user_can( 'edit_user', $user_id ) ) {
        wp_die( 'Unauthorized: Cannot edit this user' );
    }

    // Safe to process (nonce verified + user authorized)
    update_user_meta( $user_id, 'bio', wp_kses_post( $_POST['bio'] ) );
}
```

**Security layers:**
1. **Nonce verification:** Prevents CSRF attacks
2. **Capability check:** Prevents unauthorized access
3. **Input sanitization:** Prevents XSS/SQL injection

## REST API Nonce Pattern

WordPress REST API requests use nonce authentication for logged-in users. REST nonces use special action 'wp_rest' and X-WP-Nonce header.

```php
// Frontend: Create REST API nonce
wp_localize_script( 'my-rest-script', 'wpApiSettings', array(
    'root'  => esc_url_raw( rest_url() ),
    'nonce' => wp_create_nonce( 'wp_rest' ),
) );

// JavaScript: Send nonce with REST request
fetch( wpApiSettings.root + 'myplugin/v1/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': wpApiSettings.nonce
    },
    body: JSON.stringify( { data: formData } )
} );

// Backend: Nonce automatically verified by REST API
add_action( 'rest_api_init', function() {
    register_rest_route( 'myplugin/v1', '/data', array(
        'methods'             => 'POST',
        'callback'            => 'process_rest_data',
        'permission_callback' => function() {
            return current_user_can( 'edit_posts' );
        }
    ) );
} );
```

**REST API nonce verification:**
- Automatic for logged-in users
- Validates X-WP-Nonce header
- Combines with permission_callback for authorization

## Nonce Anti-Patterns

WordPress nonce security requires proper creation, transmission, and verification. Anti-patterns bypass CSRF protection or break functionality.

### Anti-Pattern: Missing Nonce Verification

```php
// ❌ No nonce verification (CSRF vulnerability)
add_action( 'admin_post_delete_post', 'delete_post_handler' );
function delete_post_handler() {
    wp_delete_post( $_POST['post_id'] );
}

// ✅ Correct: Verify nonce
add_action( 'admin_post_delete_post', 'delete_post_handler' );
function delete_post_handler() {
    check_admin_referer( 'delete-post-' . $_POST['post_id'] );
    wp_delete_post( absint( $_POST['post_id'] ) );
}
```

### Anti-Pattern: Generic Nonce Actions

```php
// ❌ Generic action (collision risk)
$nonce = wp_create_nonce( 'save' );

// ✅ Correct: Specific action
$nonce = wp_create_nonce( 'save-settings-page' );
```

### Anti-Pattern: Reusing Nonces

```php
// ❌ Reuse nonce across forms
$nonce = wp_create_nonce( 'form-action' );
echo '<input name="nonce1" value="' . $nonce . '" />';
echo '<input name="nonce2" value="' . $nonce . '" />';

// ✅ Correct: Unique nonce per action
$nonce1 = wp_create_nonce( 'action-1' );
$nonce2 = wp_create_nonce( 'action-2' );
```

### Anti-Pattern: Client-Side Nonce Generation

```php
// ❌ Never generate nonces in JavaScript

// ✅ Correct: Generate server-side, pass to JavaScript
wp_localize_script( 'my-script', 'myData', array(
    'nonce' => wp_create_nonce( 'my-action' ),
) );
```
