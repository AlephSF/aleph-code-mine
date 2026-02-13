---
title: "Capability Check Patterns for WordPress Authorization"
category: "wordpress-security"
subcategory: "authorization"
tags: ["capabilities", "current_user_can", "user_can", "authorization", "rbac"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## WordPress Capability Checks Overview

WordPress capability checks authorize users for specific actions (edit posts, manage options, delete users). Capability verification prevents unauthorized data access, privilege escalation, and admin function abuse.

**Core capability functions:**
- `current_user_can()`: Check current user capability (574 instances)
- `user_can()`: Check specific user capability (592 instances)

**Total capability checks:** 1,166 across WordPress VIP codebase (95.5% in airbnb)

**Critical rule:** All admin functions, data modifications, and sensitive operations require capability checks.

## current_user_can() Pattern

WordPress `current_user_can()` verifies current user has specific capability before executing protected operations. The function checks against user roles (administrator, editor, author, etc.) and custom capabilities.

```php
// Pattern: Check post edit capability before modification
if ( empty( $post_type_obj->cap->edit_post ) || ! current_user_can( $post_type_obj->cap->edit_post, $value ) ) {
    wp_die( esc_html( sprintf(
        __( 'Tried to alter %s %d through field "%s", which user is not permitted to edit.', 'fieldmanager' ),
        $post_type_obj->name,
        $value,
        $field->name
    ) ) );
}

// Pattern: Check submenu page capability
if ( ! current_user_can( $this->capability ) ) {
    $this->fm->_unauthorized_access( __( 'Current user cannot edit this page', 'fieldmanager' ) );
    return;
}

// Pattern: Check term management capability
if ( ! current_user_can( $tax_obj->cap->manage_terms ) ) {
    $this->fm->_unauthorized_access( __( 'User cannot edit this term', 'fieldmanager' ) );
    return;
}
```

**Usage:** 574 instances (95.3% in airbnb)

## user_can() Pattern

WordPress `user_can()` checks capabilities for specific user ID, enabling admin actions on behalf of users or multi-user permission validation.

```php
// Pattern: Check specific user capability
if( ! user_can( $user_id, $this->capability ) ) {
    wp_die( esc_html( sprintf(
        __( 'Tried to refer to user "%s" which current user cannot edit.', 'fieldmanager' ),
        $user_id
    ) ) );
}

// Pattern: Check user profile edit capability
if ( ! current_user_can( 'edit_user', $user_id ) ) {
    $this->fm->_unauthorized_access( __( 'Current user cannot edit this user', 'fieldmanager' ) );
    return;
}
```

**Usage:** 592 instances across WordPress VIP codebase

## Dynamic Capability Checks

WordPress post types and taxonomies define custom capabilities via `cap` property. Dynamic capability checks use post type / taxonomy object capabilities for flexible permission systems.

```php
// Pattern: Use post type capability dynamically
$post_type_obj = get_post_type_object( $post_type );
if ( ! current_user_can( $post_type_obj->cap->edit_posts ) ) {
    wp_die( 'Unauthorized' );
}

// Pattern: Use taxonomy capability dynamically
$tax_obj = get_taxonomy( $taxonomy );
if ( ! current_user_can( $tax_obj->cap->manage_terms ) ) {
    wp_die( 'Unauthorized' );
}

// Pattern: Check specific post edit permission
if ( ! current_user_can( $post_type_obj->cap->edit_post, $post_id ) ) {
    wp_die( 'Cannot edit this post' );
}
```

**Dynamic capability benefits:**
- Adapts to custom post type capabilities
- Supports capability remapping (map_meta_cap)
- Portable across post types

## Common WordPress Capabilities

WordPress provides default capabilities for roles (administrator, editor, author, contributor, subscriber). Understanding capability hierarchy prevents permission bypasses.

**Post capabilities:**
- `edit_posts`: Edit own posts
- `edit_others_posts`: Edit others' posts
- `edit_published_posts`: Edit published posts
- `publish_posts`: Publish posts
- `delete_posts`: Delete own posts
- `delete_others_posts`: Delete others' posts
- `delete_published_posts`: Delete published posts
- `edit_post`: Edit specific post ID
- `delete_post`: Delete specific post ID

**Admin capabilities:**
- `manage_options`: Manage site settings (admin-only)
- `manage_categories`: Manage categories/tags
- `manage_links`: Manage links
- `upload_files`: Upload media
- `unfiltered_html`: Edit unfiltered HTML

**User capabilities:**
- `edit_users`: Edit users
- `create_users`: Create new users
- `delete_users`: Delete users
- `promote_users`: Change user roles
- `list_users`: View user list

**Capability hierarchy:**
- **Administrator:** All capabilities
- **Editor:** Edit others' posts, manage categories
- **Author:** Edit/publish own posts
- **Contributor:** Edit own unpublished posts
- **Subscriber:** Read-only access

## Capability + Nonce Pattern

WordPress security best practice combines capability checks (authorization) with nonce verification (request authenticity). Layered security prevents both CSRF attacks and unauthorized access.

```php
// Pattern: Capability + nonce verification
public function save_user_profile() {
    // Layer 1: Verify nonce (CSRF protection)
    check_admin_referer( 'update-user-' . $user_id );

    // Layer 2: Check capability (authorization)
    if ( ! current_user_can( 'edit_user', $user_id ) ) {
        wp_die( 'Unauthorized: Cannot edit this user' );
    }

    // Safe to process (nonce verified + user authorized)
    update_user_meta( $user_id, 'bio', wp_kses_post( $_POST['bio'] ) );
}
```

**Security layers:**
1. Nonce verification: Prevents CSRF
2. Capability check: Prevents unauthorized access
3. Input sanitization: Prevents XSS/SQL injection

## REST API Permission Callback

WordPress REST API uses `permission_callback` for capability-based authorization. Permission callbacks combine capability checks with custom logic for flexible API security.

```php
// Pattern: REST API with capability check
add_action( 'rest_api_init', function() {
    register_rest_route( 'myplugin/v1', '/data', array(
        'methods'             => 'POST',
        'callback'            => 'process_rest_data',
        'permission_callback' => function() {
            return current_user_can( 'edit_posts' );
        }
    ) );
} );

// Pattern: Complex permission logic
register_rest_route( 'myplugin/v1', '/users/(?P<id>\d+)', array(
    'methods'             => 'DELETE',
    'callback'            => 'delete_user',
    'permission_callback' => function( $request ) {
        $user_id = $request['id'];
        return current_user_can( 'delete_users' ) && get_current_user_id() !== $user_id;
    }
) );
```

**Permission callback rules:**
- Return `true`: Allow request
- Return `false`: Deny with 403 Forbidden
- Return `WP_Error`: Deny with custom message

## Custom Capability Registration

WordPress allows defining custom capabilities for granular permission control. Custom capabilities map to existing roles or use capability filters.

```php
// Pattern: Register custom capability on activation
register_activation_hook( __FILE__, 'add_custom_capabilities' );
function add_custom_capabilities() {
    $role = get_role( 'administrator' );
    $role->add_cap( 'manage_custom_data' );

    $editor = get_role( 'editor' );
    $editor->add_cap( 'edit_custom_data' );
}

// Pattern: Use custom capability
if ( ! current_user_can( 'manage_custom_data' ) ) {
    wp_die( 'Unauthorized' );
}

// Pattern: Map custom capability to existing capability
add_filter( 'map_meta_cap', function( $caps, $cap, $user_id, $args ) {
    if ( 'edit_custom_post' === $cap ) {
        $caps = array( 'edit_posts' );
    }
    return $caps;
}, 10, 4 );
```

## Capability Check Anti-Patterns

WordPress capability checks require placement before protected operations. Common anti-patterns allow unauthorized access or break functionality.

### Anti-Pattern: Missing Capability Check

```php
// ❌ Critical: No capability check (unauthorized access!)
add_action( 'admin_post_delete_user', 'delete_user_handler' );
function delete_user_handler() {
    wp_delete_user( $_POST['user_id'] ); // No capability check!
}

// ✅ Correct: Check capability
function delete_user_handler() {
    check_admin_referer( 'delete-user-' . $_POST['user_id'] );
    if ( ! current_user_can( 'delete_users' ) ) {
        wp_die( 'Unauthorized' );
    }
    wp_delete_user( absint( $_POST['user_id'] ) );
}
```

### Anti-Pattern: Capability Check After Action

```php
// ❌ Wrong: Check capability after modification
update_option( 'site_settings', $_POST['settings'] );
if ( ! current_user_can( 'manage_options' ) ) {
    wp_die( 'Unauthorized' ); // Too late!
}

// ✅ Correct: Check capability before modification
if ( ! current_user_can( 'manage_options' ) ) {
    wp_die( 'Unauthorized' );
}
update_option( 'site_settings', $_POST['settings'] );
```

### Anti-Pattern: Hardcoded User ID Checks

```php
// ❌ Wrong: Hardcoded user ID (brittle)
if ( get_current_user_id() === 1 ) { // Assumes user 1 is admin
    // Admin-only operation
}

// ✅ Correct: Use capability
if ( current_user_can( 'manage_options' ) ) {
    // Admin-only operation
}
```
