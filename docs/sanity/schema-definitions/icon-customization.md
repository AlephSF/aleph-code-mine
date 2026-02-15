---
title: "Icon Customization for Schema Types"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "icons", "ux", "studio", "react-icons", "sanity-icons"]
stack: "sanity"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-13"
---

# Icon Customization for Schema Types

## Overview

Sanity allows custom icons for document and object types to improve visual navigation in the Studio sidebar and document lists. Icon usage is a de facto standard with 82% adoption across analyzed repositories. Icon packages differ by Sanity version: v2 projects use `react-icons`, while v3+ projects use `@sanity/icons`.

## Pattern Adoption

**Adoption Rate:** 67% (2 of 3 repositories)

**Icon Density:**
- **Kariusdx (v2)**: 70 icons across 64 schemas = **109% (1.09 per schema)**
- **Ripplecom (v4)**: 51 icons across 78 schemas = **65% of schemas**
- **Helix (v3)**: 0 icons (uses default Sanity icons)

**Total:** 121 icon customizations across 147 schemas = **82% adoption**


## Sanity v2: react-icons Library

Kariusdx (v2.30.0) uses the `react-icons` library for icon customization.

```javascript
// kariusdx-sanity/schemas/documents/page.js
import React from 'react'
import { CgFileDocument } from 'react-icons/cg'

export default {
  name: 'page',
  type: 'document',
  title: 'Page',
  icon: CgFileDocument, // ← React component from react-icons
  fields: [/* ... */],
}
```

**Common react-icons Imports:**
```javascript
import { CgFileDocument } from 'react-icons/cg'  // Carbon icons
import { FaRegNewspaper } from 'react-icons/fa'   // Font Awesome
import { IoCalendarOutline } from 'react-icons/io5' // Ionicons
import { BsPerson } from 'react-icons/bs'         // Bootstrap icons
import { MdSettings } from 'react-icons/md'       // Material Design
```

## Sanity v3+: @sanity/icons Package

Ripplecom (v4.3.0) uses the official `@sanity/icons` package designed for Sanity Studio.

```typescript
// ripplecom-nextjs/apps/sanity-studio/schemaTypes/documents/blogPost.ts
import { DocumentTextIcon } from "@sanity/icons"
import { defineType } from "sanity"

export default defineType({
  name: "blogPost",
  title: "Blog Post",
  type: "document",
  icon: DocumentTextIcon, // ← Official Sanity icon component
  fields: [/* ... */],
})
```

**Common @sanity/icons Imports:**
```typescript
import { DocumentTextIcon } from "@sanity/icons"
import { CalendarIcon } from "@sanity/icons"
import { UserIcon } from "@sanity/icons"
import { CogIcon } from "@sanity/icons"
import { ImageIcon } from "@sanity/icons"
import { TagIcon } from "@sanity/icons"
```


## Page/Document Icons

Standard page and document types typically use document-related icons.

```javascript
// Kariusdx v2 - Pages
import { CgFileDocument } from 'react-icons/cg'

export default {
  name: 'page',
  icon: CgFileDocument,
  // ...
}
```

```typescript
// Ripplecom v4 - Blog Posts
import { DocumentTextIcon } from "@sanity/icons"

export default defineType({
  name: "blogPost",
  icon: DocumentTextIcon,
  // ...
})
```

## Content Type Icons

Different content types use semantically appropriate icons.

```javascript
// News/Press Releases (Kariusdx v2)
import { FaRegNewspaper } from 'react-icons/fa'

export default {
  name: 'news',
  icon: FaRegNewspaper,
  // ...
}
```

```typescript
// Events (Ripplecom v4)
import { CalendarIcon } from "@sanity/icons"

export default defineType({
  name: "event",
  icon: CalendarIcon,
  // ...
})
```

## People/Staff Icons

Person-related schemas use user or people icons.

```javascript
// Staff (Kariusdx v2)
import { BsPerson } from 'react-icons/bs'

export default {
  name: 'staff',
  icon: BsPerson,
  // ...
}
```

```typescript
// People (Ripplecom v4)
import { UserIcon } from "@sanity/icons"

export default defineType({
  name: "person",
  icon: UserIcon,
  // ...
})
```

## Media Content Icons

Media-related schemas use appropriate visual icons.

```javascript
// Video (Kariusdx v2)
import { IoVideocamOutline } from 'react-icons/io5'

export default {
  name: 'video',
  icon: IoVideocamOutline,
  // ...
}
```

```typescript
// Case Study (Ripplecom v4)
import { DocumentsIcon } from "@sanity/icons"

export default defineType({
  name: "caseStudy",
  icon: DocumentsIcon,
  // ...
})
```


## Component/Block Icons

Builder blocks and components use component-specific icons.

```javascript
// Button Component (Kariusdx v2)
import { CgPushChevronRight } from 'react-icons/cg'

export default {
  name: 'button',
  type: 'object',
  icon: CgPushChevronRight,
  // ...
}
```

```typescript
// CTA Card (Ripplecom v4)
import { BlockContentIcon } from "@sanity/icons"

export default defineType({
  name: "ctaCard",
  type: "object",
  icon: BlockContentIcon,
  // ...
})
```

## Configuration Icons

Settings and configuration objects use gear or settings icons.

```javascript
// Site Settings (Kariusdx v2)
import { MdSettings } from 'react-icons/md'

export default {
  name: 'siteSettings',
  icon: MdSettings,
  // ...
}
```

```typescript
// Navigation (Ripplecom v4)
import { MenuIcon } from "@sanity/icons"

export default defineType({
  name: "navigation",
  icon: MenuIcon,
  // ...
})
```


## Semantic Matching

Choose icons that visually represent the content type's purpose.

**Good Semantic Matches:**
- **Page/Document**: `DocumentTextIcon`, `CgFileDocument`
- **Blog Post**: `DocumentTextIcon`, `FaRegNewspaper`
- **Event**: `CalendarIcon`, `IoCalendarOutline`
- **Person/Staff**: `UserIcon`, `BsPerson`
- **Settings**: `CogIcon`, `MdSettings`
- **Category/Tag**: `TagIcon`, `FaTag`
- **Media**: `ImageIcon`, `IoVideocamOutline`

## Consistent Icon Style

Use icons from the same library/style throughout your project.

**❌ Bad: Mixed icon styles**
```javascript
// Mixing Carbon, Font Awesome, and Material Design inconsistently
import { CgFileDocument } from 'react-icons/cg'
import { FaBeer } from 'react-icons/fa'
import { MdSettings } from 'react-icons/md'
```

**✅ Good: Consistent icon family**
```typescript
// All icons from @sanity/icons (v3+)
import { DocumentTextIcon } from "@sanity/icons"
import { CalendarIcon } from "@sanity/icons"
import { UserIcon } from "@sanity/icons"
```

## Visual Hierarchy

Use simpler icons for common types, more distinctive icons for special types.

```typescript
// Common types: Simple, recognizable icons
const page = defineType({
  name: "page",
  icon: DocumentTextIcon, // Simple document icon
})

const blogPost = defineType({
  name: "blogPost",
  icon: DocumentTextIcon, // Same as page (both are documents)
})

// Special types: Distinctive icons
const redirect = defineType({
  name: "redirect",
  icon: LinkRemovedIcon, // Unique icon for redirects
})

const leadGeneration = defineType({
  name: "leadGeneration",
  icon: UserIcon, // Distinctive for lead capture
})
```


## Installing react-icons (Sanity v2)

```bash
npm install react-icons
```

```javascript
// Import from appropriate icon family
import { CgFileDocument } from 'react-icons/cg'      // Carbon
import { FaRegNewspaper } from 'react-icons/fa'      // Font Awesome
import { IoCalendarOutline } from 'react-icons/io5'  // Ionicons
import { BsPerson } from 'react-icons/bs'            // Bootstrap
import { MdSettings } from 'react-icons/md'          // Material Design
```

## Using @sanity/icons (Sanity v3+)

The `@sanity/icons` package comes pre-installed with Sanity v3+.

```typescript
// Direct import from @sanity/icons
import {
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  CogIcon,
  ImageIcon,
  TagIcon,
} from "@sanity/icons"
```


## Using Custom SVG Components

Custom SVG icons can be used as React components.

```typescript
// Custom icon component
const CustomLogoIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L2 7v10l10 5 10-5V7l-10-5z" stroke="currentColor" strokeWidth="2" />
  </svg>
)

export default defineType({
  name: "customType",
  icon: CustomLogoIcon,
  // ...
})
```

## SVG Icon Best Practices

Custom SVG icons should follow Sanity Studio's design system.

**Requirements:**
- Use `currentColor` for stroke/fill (inherits Studio theme colors)
- Set `viewBox="0 0 24 24"` for consistent sizing
- Keep SVG simple (avoid complex gradients or filters)
- Use `fill="none"` with `stroke="currentColor"` for outline icons

```typescript
// ✅ Good: Theme-aware SVG icon
const GoodIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path d="..." stroke="currentColor" strokeWidth="2" />
  </svg>
)

// ❌ Bad: Hard-coded colors
const BadIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="..." fill="#3366FF" /> {/* Won't adapt to dark mode */}
  </svg>
)
```


## Improved Navigation

Icons provide visual landmarks in the Studio sidebar, making navigation faster.

**Without Icons:**
```
☐ Page
☐ Blog Post
☐ Event
☐ Person
☐ Category
```

**With Icons:**
```
📄 Page
📰 Blog Post
📅 Event
👤 Person
🏷️ Category
```

## Faster Content Type Recognition

Editors can quickly identify content types in lists and search results.

```typescript
// Document list with icons provides instant visual recognition
[Icon] Page: Home
[Icon] Page: About Us
[Icon] Blog Post: New Feature Launch
[Icon] Event: 2026 Conference
[Icon] Person: John Doe
```

## Brand Consistency

Custom icons can reinforce brand identity throughout the Studio.

```typescript
// Brand-specific icons for company schema types
const companyPage = defineType({
  name: "companyPage",
  icon: CompanyLogoIcon, // Custom SVG with company branding
})
```


## Overusing Distinctive Icons

Every schema doesn't need a unique icon; related types should share icons.

**❌ Bad: Every type has unique icon**
```typescript
// Too many different icons for similar content types
const blogPost = { icon: NewspaperIcon }
const article = { icon: DocumentIcon }
const story = { icon: BookIcon }
const post = { icon: PenIcon }
```

**✅ Good: Related types share icons**
```typescript
// All written content uses same icon
const blogPost = { icon: DocumentTextIcon }
const article = { icon: DocumentTextIcon }
const story = { icon: DocumentTextIcon }
```

## Using Emoji as Icons

Emoji don't scale consistently and break accessibility.

**❌ Bad: Emoji as icon**
```typescript
const page = {
  icon: () => <span>📄</span>, // Inconsistent rendering
}
```

**✅ Good: Proper icon component**
```typescript
const page = {
  icon: DocumentTextIcon, // Scales properly
}
```

## Missing Icons on Important Types

Skip icons only on rarely-used object types, not primary document types.

**❌ Bad: No icon on main document type**
```typescript
const blogPost = {
  name: "blogPost",
  // Missing icon - harder to find in sidebar
}
```

**✅ Good: Icon on all document types**
```typescript
const blogPost = {
  name: "blogPost",
  icon: DocumentTextIcon, // Easy to spot
}
```

## Implementation Checklist

- [ ] Install icon library: `@sanity/icons` (v3+) or `react-icons` (v2)
- [ ] Add icons to all document types (page, blogPost, event, etc.)
- [ ] Add icons to frequently-used object types (components, blocks)
- [ ] Use consistent icon family/style throughout project
- [ ] Choose semantically appropriate icons
- [ ] Test icon visibility in both light and dark Studio themes
- [ ] Verify icons display correctly in sidebar and document lists

## Related Patterns

- **Preview Configuration**: Icons appear in previews alongside title/subtitle
- **Field Groups**: Icons only appear at schema level, not on field groups
- **Conditional Fields**: Icons don't change based on document state

## References

- Kariusdx (v2): 70 icons using `react-icons` (1.09 per schema)
- Ripplecom (v4): 51 icons using `@sanity/icons` (65% of schemas)
- Helix (v3): 0 custom icons (uses Sanity defaults)
- @sanity/icons Gallery: https://www.sanity.io/docs/icons
- react-icons Library: https://react-icons.github.io/react-icons/
