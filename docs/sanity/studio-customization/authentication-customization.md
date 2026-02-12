# Authentication Customization (SAML SSO)

---
title: "Authentication Customization (SAML SSO)"
category: "studio-customization"
subcategory: "security"
tags: ["sanity", "authentication", "saml", "sso", "okta", "security"]
stack: "sanity"
priority: "medium"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-12"
---

## Overview

Sanity Studio authentication customization enables SAML Single Sign-On (SSO) integration with enterprise identity providers (Okta, Azure AD, Google Workspace). SAML SSO centralizes user management, enforces password policies, and enables multi-factor authentication (MFA) at organizational level. Only 33% of analyzed projects use custom authentication (ripplecom v4 only).

## SAML SSO Configuration

Sanity v4+ supports SAML authentication via `createAuthStore`. Configuration requires SAML provider URL, login method selection, and optional redirect behavior.

**Basic Configuration:**

```typescript
// sanity.config.ts
import { defineConfig, createAuthStore } from 'sanity'

export default defineConfig({
  projectId: 'abc12345',
  dataset: 'production',
  auth: createAuthStore({
    projectId: 'abc12345',
    dataset: 'production',
    redirectOnSingle: false,
    mode: 'append',
    providers: [
      {
        name: 'saml',
        title: 'Ripple Okta',
        url: 'https://api.sanity.io/v2021-10-01/auth/saml/login/44054204',
      },
    ],
    loginMethod: 'dual',
  }),
})
```

Ripplecom uses Okta SAML authentication with dual login mode (SAML + email/password fallback). SAML provider URL is Sanity-hosted endpoint that redirects to Okta IdP.

**Auth Store Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `projectId` | string | Yes | Sanity project ID |
| `dataset` | string | Yes | Dataset name |
| `redirectOnSingle` | boolean | No | Auto-redirect to SSO if single provider |
| `mode` | string | No | `append` (add to default) or `replace` (override) |
| `providers` | array | Yes | Authentication provider configurations |
| `loginMethod` | string | No | `dual` (SSO + email) or `single` (SSO only) |

## SAML Provider Configuration

SAML provider configuration requires three properties: `name`, `title`, and `url`.

**Provider Object:**

```typescript
{
  name: 'saml',              // Fixed value for SAML providers
  title: 'Ripple Okta',      // Display name on login button
  url: 'https://api.sanity.io/v2021-10-01/auth/saml/login/44054204',
}
```

**SAML URL Format:**

```
https://api.sanity.io/v2021-10-01/auth/saml/login/{SAML_CONNECTION_ID}
```

`{SAML_CONNECTION_ID}` is unique identifier provided by Sanity support when SAML connection is configured. Ripplecom's connection ID is `44054204`.

**Multiple SAML Providers:**

```typescript
providers: [
  {
    name: 'saml',
    title: 'Company Okta',
    url: 'https://api.sanity.io/v2021-10-01/auth/saml/login/11111111',
  },
  {
    name: 'saml',
    title: 'Client Azure AD',
    url: 'https://api.sanity.io/v2021-10-01/auth/saml/login/22222222',
  },
]
```

Support multiple SAML providers for organizations with separate employee and contractor identity systems.

## Login Method: Dual vs Single

Login method controls whether content editors can use email/password authentication alongside SAML SSO.

**Dual Login Mode (Recommended):**

```typescript
loginMethod: 'dual'
```

Login screen shows two options:

1. **"Sign in with Ripple Okta"** button (SAML SSO)
2. **"Sign in with email"** link (traditional auth)

**Benefits:**

- Graceful degradation if SAML provider down
- Emergency access for administrators
- Onboarding flexibility (email first, SSO later)

**Use cases:** Production Studio with external contractors, staging environments, emergency access requirements.

**Single Login Mode:**

```typescript
loginMethod: 'single'
```

Login screen shows only SAML SSO button. Email/password authentication disabled.

**Benefits:**

- Enforces corporate authentication policies
- Eliminates weak password risk
- Centralized access revocation

**Use cases:** Enterprise-only Studio, strict security compliance, fully managed workforce.

Ripplecom uses dual login for flexibility. Administrators retain email/password access for emergency scenarios.

## Redirect Behavior

`redirectOnSingle` controls automatic redirect when single authentication provider configured.

**Auto-Redirect Enabled:**

```typescript
redirectOnSingle: true
```

Login screen immediately redirects to SAML provider. Content editors never see Sanity login form.

**Auto-Redirect Disabled (Ripplecom Pattern):**

```typescript
redirectOnSingle: false
```

Login screen shows SSO button. Content editors click button to initiate SAML flow. Provides visual confirmation before external redirect.

**Recommendation:** Disable auto-redirect (`false`) for dual login mode. Enable auto-redirect (`true`) for single login mode.

## Auth Store Mode

`mode` property controls whether custom auth replaces or extends default Sanity authentication.

**Append Mode (Ripplecom Pattern):**

```typescript
mode: 'append'
```

Custom auth providers added alongside default email/password authentication. Enables dual login mode.

**Replace Mode:**

```typescript
mode: 'replace'
```

Custom auth providers replace default authentication entirely. Equivalent to `loginMethod: 'single'`.

**Recommendation:** Use `append` for dual login, `replace` for single login.

## SAML Setup Process

Configuring SAML authentication requires coordination between Sanity support and identity provider administrator.

**Setup Steps:**

1. **Contact Sanity Support**
   - Request SAML configuration for project
   - Provide identity provider type (Okta, Azure AD, etc.)

2. **Sanity Creates SAML Connection**
   - Sanity support creates SAML connection
   - Returns SAML connection ID and metadata URL
   - Example metadata URL: `https://api.sanity.io/v2021-10-01/auth/saml/metadata/44054204`

3. **Configure Identity Provider**
   - Import Sanity SAML metadata into IdP
   - Set Assertion Consumer Service (ACS) URL
   - Configure attribute mappings (email, name)
   - Add authorized users/groups

4. **Test SAML Flow**
   - Attempt login via SAML button
   - Verify redirect to IdP login page
   - Confirm successful authentication
   - Check user attributes in Sanity

5. **Add SAML to Studio Config**
   - Update `sanity.config.ts` with SAML provider
   - Deploy updated Studio configuration
   - Test login with multiple users

**Timeline:** SAML setup typically takes 1-3 business days (depends on IdP administrator availability).

## User Provisioning

SAML authentication provisions Sanity users on first login. No manual user creation required.

**First Login Flow:**

1. Content editor clicks "Sign in with Ripple Okta"
2. Redirects to Okta login page
3. Editor authenticates with Okta credentials
4. Okta sends SAML assertion to Sanity
5. Sanity creates new user account (if doesn't exist)
6. Sanity grants Studio access based on project membership
7. Editor redirected to Studio dashboard

**User Attributes Mapped:**

| SAML Attribute | Sanity Field |
|----------------|--------------|
| email | email address |
| name | display name |
| sub (subject) | user ID |

Additional attributes (role, department) require custom SAML configuration—contact Sanity support.

## Role-Based Access Control

Sanity project membership controls Studio access, not SAML groups. SAML authenticates identity; Sanity authorizes access.

**Access Flow:**

1. **SAML Authentication** - IdP confirms user identity
2. **Sanity Authorization** - Sanity checks project membership
3. **Studio Access** - User granted appropriate role (administrator, editor, viewer)

**Project Roles:**

- **Administrator** - Full Studio access, schema changes, user management
- **Editor** - Content CRUD, no config changes
- **Viewer** - Read-only access

Configure roles in Sanity Manage (manage.sanity.io) → Project → Members.

## De-Provisioning Users

Removing user from IdP does not automatically remove from Sanity. De-provision manually in Sanity Manage.

**De-Provisioning Process:**

1. **Remove from IdP** - Revoke IdP access (prevents SAML login)
2. **Remove from Sanity** - Delete user in Sanity Manage → Project → Members
3. **Verify** - Attempt login (should fail)

**Recommendation:** Implement quarterly access audit to identify orphaned Sanity accounts.

## Security Considerations

**Benefits of SAML SSO:**

- **Centralized access control** - Single point of user management
- **MFA enforcement** - IdP-level multi-factor authentication
- **Password policies** - Corporate password complexity rules
- **Audit logging** - IdP tracks all authentication attempts
- **Instant revocation** - Disable IdP account to block all access

**Risks Without SSO:**

- Weak passwords (editors choose "password123")
- Shared accounts (team uses single login)
- Orphaned accounts (ex-employees retain access)
- No MFA (vulnerable to credential theft)

**Security Best Practices:**

1. Enable MFA in identity provider (required for all users)
2. Use dual login mode for emergency access
3. Rotate SAML certificates annually
4. Monitor failed login attempts
5. Audit project members quarterly

## When to Use SAML SSO

**Use SAML SSO when:**

- Organization has enterprise identity provider (Okta, Azure AD, Google Workspace)
- Team size exceeds 10 content editors
- Security compliance requires centralized authentication
- MFA enforcement needed
- External contractors access Studio

**Skip SAML SSO when:**

- Team <5 editors (management overhead exceeds benefit)
- No existing identity provider (setup cost high)
- Editors prefer password managers
- Budget constraints (SAML may require higher Sanity plan)

Helix and kariusdx use default Sanity email/password authentication. Small teams (2-4 editors) with no IdP.

## Alternative: Google/GitHub OAuth

Sanity also supports OAuth authentication with Google and GitHub. Simpler setup than SAML, but less enterprise control.

**OAuth Configuration:**

```typescript
auth: createAuthStore({
  mode: 'replace',
  providers: [
    {
      name: 'google',
      title: 'Sign in with Google',
    },
  ],
})
```

OAuth providers managed directly in Sanity Manage—no SAML setup required. Consider OAuth for small teams with Google Workspace but no Okta license.

## Cost Considerations

SAML SSO availability depends on Sanity plan tier.

**Sanity Plan Requirements:**

- **Growth Plan** - Basic email authentication only
- **Growth+ Plan** - OAuth (Google, GitHub) supported
- **Enterprise Plan** - SAML SSO supported

Verify SAML eligibility before implementing. Upgrading plans mid-project causes authentication disruption.

## Anti-Patterns

**Anti-Pattern 1: Single login mode without fallback**

```typescript
// ❌ BAD: No emergency access if IdP down
loginMethod: 'single'

// ✅ GOOD: Dual mode provides fallback
loginMethod: 'dual'
```

Always maintain administrator email/password for emergency access.

**Anti-Pattern 2: Auto-redirect with multiple providers**

```typescript
// ❌ BAD: Redirects to first provider, ignores others
redirectOnSingle: true
providers: [/* provider1 */, /* provider2 */]

// ✅ GOOD: Shows provider selection screen
redirectOnSingle: false
```

**Anti-Pattern 3: Hardcoded SAML connection ID**

```typescript
// ❌ BAD: Production ID in source control
url: 'https://api.sanity.io/v2021-10-01/auth/saml/login/44054204'

// ✅ GOOD: Environment variable
url: process.env.SANITY_STUDIO_SAML_URL || 'https://...'
```

Use different SAML connections for staging vs production environments.

## Migration Path

Migrating existing Studio from email/password to SAML requires coordinated rollout.

**Migration Steps:**

1. **Setup SAML (Weeks 1-2)**
   - Configure IdP
   - Test with pilot users
   - Verify user provisioning

2. **Enable Dual Login (Week 3)**
   - Deploy Studio with SAML + email
   - Train editors on SSO flow
   - Monitor adoption

3. **Phase Out Email Auth (Week 4+)**
   - All editors using SAML
   - Optional: Switch to single login mode
   - Maintain admin email access

**Recommendation:** Run dual login indefinitely. Disabling email auth provides no security benefit if SAML properly configured.

## Related Patterns

- **custom-branding-theming.md** - Custom login screen branding
- **desk-structure-customization.md** - Role-based desk structure
- **singleton-document-management.md** - Permission-based content access

## References

- Ripplecom: `apps/sanity-studio/sanity.config.ts` (SAML configuration)
- Sanity Docs: SAML SSO Setup
- Sanity Manage: Project → Members (user management)
- Okta: SAML Integration Guide
