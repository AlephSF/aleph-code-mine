---
title: "Custom Branding and Theming"
category: "studio-customization"
subcategory: "branding"
tags: ["sanity", "branding", "theming", "css", "logo", "customization"]
stack: "sanity"
priority: "low"
audience: "backend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

## Overview

Sanity Studio custom branding replaces default Sanity logo and colors with client branding. Branding customization includes custom logo, CSS variable overrides, and custom root layouts. Only 33% of analyzed projects use custom branding (kariusdx v2 only).

## Custom Logo (v2 Parts System)

Sanity v2 uses "parts" system to replace default Sanity logo with client logo SVG.

**Configuration:**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/brand-logo",
      "path": "./components/logo.js"
    }
  ]
}
```

**Logo Component:**

```javascript
// components/logo.js
import React from 'react'

const logo = () => (
  <svg width="781" height="174" viewBox="0 0 781 174" fill="none">
    <g clipPath="url(#clip0)">
      <path d="M676.74 98.02C664.41 93.67..." fill="#212944"/>
      <path d="M424.8 49.96C418.93 50.06..." fill="#212944"/>
      {/* ...full logo paths */}
    </g>
  </svg>
)

export default logo
```

Kariusdx uses full-width Karius logo (781×174px) with brand colors (#212944 primary, #cc4e13 secondary). Logo appears in Studio navbar and login screen.

**Logo Requirements:**

- Export React component (not just SVG string)
- Inline SVG (not external image file)
- Recommended: Single color or duo-tone
- Optimize: Remove unnecessary paths and groups

**V3+ Logo Configuration:**

V2 parts system is deprecated in v3+. V3+ projects should use `studio.logo` configuration:

```typescript
import { defineConfig } from 'sanity'
import Logo from './components/Logo'

export default defineConfig({
  studio: {
    logo: Logo,
  },
})
```

## CSS Variable Overrides

Sanity Studio theming uses CSS variables for colors, spacing, and typography. Override variables to match client brand guidelines.

**Configuration (v2):**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/theme/variables/override-style",
      "path": "variableOverrides.css"
    }
  ]
}
```

**Variable Overrides:**

```css
/* variableOverrides.css */
:root {
    --brand-primary: #212944;
    --brand-secondary: #cc4e13;
    --brand-tertiary: #0d7479;
    --brand-gray: #9ea1a5;
    --brand-gray-light: #f5f5f5;
    --main-navigation-color: var(--brand-gray-light);
}

:global([data-ui='Navbar']) {
    border-bottom: 1px var(--brand-gray) solid;
}

:global([data-testid='text-style--h1']),
:global([data-testid='text-style--h2']),
:global([data-testid='text-style--h3']),
:global([data-testid='text-style--h4']),
:global([data-testid='text-style--h5']),
:global([data-testid='text-style--h6']) {
    font-size: 1rem !important;
}
```

Kariusdx defines 5 brand colors and overrides navbar border color. Font size override normalizes heading sizes to 1rem (design system requirement).

**Common Override Targets:**

| Target | Purpose | Kariusdx Value |
|--------|---------|----------------|
| `--brand-primary` | Primary brand color | #212944 |
| `--brand-secondary` | Accent color | #cc4e13 |
| `--main-navigation-color` | Navbar background | #f5f5f5 |
| `--card-bg-color` | Card backgrounds | (not overridden) |
| `--text-color` | Body text color | (not overridden) |

**V3+ CSS Overrides:**

V3+ projects should use global CSS file imported in `sanity.config.ts`:

```typescript
import './styles/studio-overrides.css'

export default defineConfig({
  // ... configuration
})
```

## Custom Root Layout

Sanity v2 allows replacing entire Studio root layout component for custom UI chrome (banners, tutorials, analytics).

**Configuration (v2):**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/root",
      "path": "plugins/sanity-plugin-tutorial/CustomDefaultLayout"
    }
  ]
}
```

**Custom Layout:**

```javascript
// plugins/sanity-plugin-tutorial/CustomDefaultLayout.js
import React from 'react'
import StudioRoot from 'part:@sanity/default-layout/root'
import { useCurrentUser } from '@sanity/base/hooks'
import GetStartedTutorial from './GetStartedTutorial'

export default function CustomDefaultLayout() {
  const { value } = useCurrentUser()
  const showTutorial = (value?.roles || []).length > 0

  return (
    <>
      {showTutorial && <GetStartedTutorial />}
      <StudioRoot />
    </>
  )
}
```

Kariusdx adds `GetStartedTutorial` component above default Studio layout. Tutorial shows role-based onboarding for new content editors.

**Use Cases for Custom Layouts:**

- Onboarding tutorials for new users
- Global banners (maintenance notices, announcements)
- Analytics tracking (page views, document edits)
- Custom authentication flows
- Feature flagging UI

**V3+ Custom Layouts:**

V3+ removes parts system. Custom layouts must be implemented via plugin APIs or Studio chrome configuration.

## Font Customization

Sanity Studio uses Inter font by default. Override font family with CSS variables.

**Custom Font:**

```css
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

:root {
    --font-family-sans-serif: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body,
input,
textarea,
select,
button {
    font-family: var(--font-family-sans-serif);
}
```

Import web font and override `--font-family-sans-serif` variable. Apply to all text elements for consistency.

**Monospace Font Override:**

```css
:root {
    --font-family-monospace: 'JetBrains Mono', 'Courier New', monospace;
}

code,
pre {
    font-family: var(--font-family-monospace);
}
```

Override code editor font separately from UI font.

## Favicon Customization

Replace default Sanity favicon with client favicon.

**Static Asset (v2):**

```
project-root/
├── static/
│   ├── favicon.ico
│   └── favicon.png
```

Place favicon files in `static/` directory. Sanity automatically serves static assets.

**HTML Meta Tags (v3+):**

```typescript
// sanity.config.ts
export default defineConfig({
  icon: () => <img src="/static/favicon.png" />,
})
```

## When to Use Custom Branding

**Use custom branding when:**

- Client requires white-label CMS (no Sanity branding visible)
- Content editors are external stakeholders (agency clients)
- Studio matches client design system
- Project has strict brand guidelines

**Skip custom branding when:**

- Studio used by internal team only
- Team familiar with Sanity branding (faster onboarding)
- No specific brand guidelines
- Maintenance overhead not justified

Helix and ripplecom use default Sanity branding. Kariusdx uses full brand customization for external client use.

## Branding Maintenance Cost

**Low Maintenance:**
- Custom logo (update when brand changes)
- Color variable overrides (static values)

**Medium Maintenance:**
- CSS overrides (may break with Sanity updates)
- Font customization (web font CDN reliability)

**High Maintenance:**
- Custom root layouts (requires testing with each Sanity version)
- Custom authentication flows (security implications)

Balance branding value against maintenance cost. Most projects only need logo + color overrides.

## Migration from v2 to v3+

Kariusdx uses v2 parts system for branding. Migrating to v3+ requires converting parts to modern API.

**V2 Parts (Deprecated):**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/brand-logo",
      "path": "./components/logo.js"
    },
    {
      "implements": "part:@sanity/base/theme/variables/override-style",
      "path": "variableOverrides.css"
    },
    {
      "implements": "part:@sanity/base/root",
      "path": "plugins/CustomDefaultLayout"
    }
  ]
}
```

**V3+ Modern API:**

```typescript
import Logo from './components/Logo'
import './styles/studio-overrides.css'

export default defineConfig({
  studio: {
    logo: Logo,
  },
  // Custom layout requires plugin API or Studio chrome
})
```

## Anti-Patterns

**Anti-Pattern 1: Overriding core UI structure**

```css
/* ❌ BAD: Breaks Studio UX */
[data-ui='Navbar'] {
    display: none !important;
}

/* ❌ BAD: Hides critical buttons */
button[aria-label='Publish'] {
    visibility: hidden;
}
```

Override colors and spacing, not structure or functionality.

**Anti-Pattern 2: Targeting internal class names**

```css
/* ❌ BAD: Internal class names change between versions */
.sc-abc123 {
    background: red;
}

/* ✅ GOOD: Target stable data attributes */
[data-ui='Navbar'] {
    background: var(--brand-primary);
}
```

Use `data-ui` and `data-testid` attributes, not generated class names.

**Anti-Pattern 3: Massive logo files**

```javascript
// ❌ BAD: 500KB SVG with unnecessary detail
const logo = () => <svg>{/* 10,000 lines of paths */}</svg>

// ✅ GOOD: Optimized 5KB SVG
const logo = () => <svg>{/* 50 lines of paths */}</svg>
```

Optimize SVG with SVGO before embedding.

## Related Patterns

- **desk-structure-customization.md** - Icons for desk structure items
- **plugin-ecosystem-patterns.md** - Plugin-based customization
- **custom-document-actions.md** - Custom workflows

## References

- Kariusdx: `components/logo.js` (custom logo SVG)
- Kariusdx: `variableOverrides.css` (brand color overrides)
- Kariusdx: `plugins/sanity-plugin-tutorial/CustomDefaultLayout.js` (tutorial overlay)
- Sanity v2 Docs: Parts System (deprecated)
- Sanity v3 Docs: Studio Configuration
