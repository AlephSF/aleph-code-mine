---
title: "CSRF Protection Patterns for WordPress"
category: "wordpress-security"
subcategory: "csrf-prevention"
tags: ["csrf", "nonce", "referer", "check_admin_referer", "security"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## CSRF Protection Overview

WordPress Cross-Site Request Forgery (CSRF) protection uses nonces (number used once) + HTTP referer verification to validate request authenticity. Multi-layer CSRF protection prevents attackers from executing unauthorized actions via forged requests.

**CSRF protection layers:**
1. **Nonce verification:** Validates time-limited, user-specific token
2. **Referer verification:** Validates request origin
3. **Capability checks:** Validates user authorization

**Combined protection functions:**
- `check_admin_referer()`: Nonce + referer (124 instances)
- `check_ajax_referer()`: AJAX nonce + referer (77 instances)
- `wp_get_referer()`: Manual referer checks (16 instances)

## check_admin_referer() Pattern

WordPress check_admin_referer() combines nonce + HTTP referer verification for admin form protection. The function validates request authenticity and origin in single call.

```php
// Pattern: Admin form with combined protection
<form method="post" action="<?php echo admin_url( 'admin-post.php' ); ?>">
    <?php wp_nonce_field( 'process-settings' ); ?>
    <input type="hidden" name="action" value="process_settings" />
    <button type="submit">Save Settings</button>
</form>

// Pattern: Verify admin referer
add_action( 'admin_post_process_settings', 'process_settings_handler' );
function process_settings_handler() {
    check_admin_referer( 'process-settings' );
    // Safe to process (nonce + referer verified)
    update_option( 'site_settings', $_POST['settings'] );
    wp_safe_redirect( admin_url( 'options-general.php?updated=1' ) );
    exit;
}
```

**check_admin_referer() verification:**
1. Verifies nonce from $_REQUEST['_wpnonce']
2. Verifies HTTP referer contains admin_url()
3. Dies with error if either check fails

**Usage:** 124 instances across WordPress VIP codebase

## Combined Nonce + Referer Pattern

WordPress security best practice combines nonce verification, referer validation, and capability checks for comprehensive CSRF + authorization protection.

```php
// Pattern: Multi-layer CSRF protection
public function save_user_profile() {
    // Layer 1: Nonce verification (request authenticity)
    check_admin_referer( 'update-user-' . $user_id );

    // Layer 2: Capability check (user authorization)
    if ( ! current_user_can( 'edit_user', $user_id ) ) {
        wp_die( 'Unauthorized: Cannot edit this user' );
    }

    // Layer 3: Sanitize inputs (XSS prevention)
    $bio = wp_kses_post( $_POST['bio'] );

    // Safe to process (all layers passed)
    update_user_meta( $user_id, 'bio', $bio );
}
```

**Security layers:**
1. Nonce: Prevents CSRF attacks
2. Referer: Validates request origin
3. Capability: Prevents unauthorized access
4. Sanitization: Prevents XSS/SQL injection

## wp_get_referer() Manual Verification

WordPress wp_get_referer() retrieves HTTP referer for manual validation. Pattern enables custom referer logic beyond automatic check_admin_referer() behavior.

```php
// Pattern: Manual referer validation
$referer = wp_get_referer();
if ( ! $referer || false === strpos( $referer, admin_url() ) ) {
    wp_die( 'Invalid referer: Request must originate from admin panel' );
}

// Pattern: Specific page referer check
$referer = wp_get_referer();
$expected_page = admin_url( 'options-general.php' );
if ( 0 !== strpos( $referer, $expected_page ) ) {
    wp_die( 'Invalid referer: Must submit from settings page' );
}
```

**Usage:** 16 instances across WordPress VIP codebase

## Origin Header Verification

WordPress CORS (Cross-Origin Resource Sharing) protection validates HTTP Origin header for AJAX requests from different domains.

```php
// Pattern: Origin header validation
$origin = isset( $_SERVER['HTTP_ORIGIN'] ) ? $_SERVER['HTTP_ORIGIN'] : '';
$allowed_origins = array(
    'https://example.com',
    'https://staging.example.com',
);

if ( ! in_array( $origin, $allowed_origins, true ) ) {
    wp_die( 'CORS violation: Invalid origin' );
}

header( 'Access-Control-Allow-Origin: ' . $origin );
header( 'Access-Control-Allow-Credentials: true' );
```

**Usage:** 1 instance across WordPress VIP codebase (low adoption, opportunity for improvement)
