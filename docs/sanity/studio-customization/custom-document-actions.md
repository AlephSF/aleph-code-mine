---
title: "Custom Document Actions"
category: "studio-customization"
subcategory: "workflows"
tags: ["sanity", "actions", "publish", "workflows", "automation"]
stack: "sanity"
priority: "medium"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-13"
---

## Overview

Custom document actions in Sanity Studio modify or replace default publish, unpublish, delete, and duplicate actions with custom workflows. Document actions enable auto-slug generation, hierarchical path calculation, pre-publish validation, and workflow restrictions. Only 33% of analyzed projects use custom actions (kariusdx v2 only).

## Document Actions Resolver (v2 API)

Sanity v2 uses "parts" system to override document actions. Document actions resolver receives `props` object with document metadata and returns array of action components.

**Configuration:**

```json
// sanity.json (v2 only)
{
  "parts": [
    {
      "implements": "part:@sanity/base/document-actions/resolver",
      "path": "./schemas/documentActions.js"
    }
  ]
}
```

**Resolver:**

```javascript
// schemas/documentActions.js
import defaultResolve, { PublishAction } from 'part:@sanity/base/document-actions'
import SetSlugAndPublishAction from './actions/setSlugAndPublishAction.js'

export default function useDocumentActions(props) {
  return defaultResolve(props).map((Action) =>
    Action === PublishAction ? SetSlugAndPublishAction : Action
  )
}
```

Kariusdx replaces default `PublishAction` with `SetSlugAndPublishAction` for all document types. Custom action runs before publish to auto-generate slugs and calculate hierarchical paths.

**Note:** v2 document actions API is deprecated in v3+. V3+ uses `defineConfig({ document: { actions: ... } })`.

## Auto-Slug on Publish

Kariusdx implements custom publish action that auto-generates slug from title if not manually set.

**Custom Publish Action:**

```javascript
// schemas/actions/setSlugAndPublishAction.js
import { useState } from 'react'
import { useDocumentOperation, useValidationStatus } from '@sanity/react-hooks'

export default function SetSlugAndPublishAction(props) {
  const { isValidating, markers } = useValidationStatus(props.id, props.type)
  const { patch, publish } = useDocumentOperation(props.id, props.type)
  const [isPublishing, setIsPublishing] = useState(false)

  return {
    disabled: isValidating || markers.length > 0,
    label: isPublishing ? 'Publishing...' : 'Publish',
    onHandle: async () => {
      setIsPublishing(true)

      const slug = props.draft.slug?.current ||
        props.draft.title?.toLowerCase().replace(/\s+/g, '-').slice(0, 200)

      if (slug) {
        patch.execute([{ set: { slug: { _type: 'slug', current: slug } } }])
      }

      publish.execute()
      props.onComplete()
    },
  }
}
```

**Key Features:**
- Validation check before enabling publish
- Auto-generates slug from title (lowercase, hyphenated)
- Patches slug field before publishing

## Hierarchical Path Calculation

Kariusdx extends auto-slug to calculate full paths for hierarchical page structures and update all descendants.

**Path Calculation Logic:**

```javascript
if (props.type === 'page') {
  const parentPage = await client.fetch('*[_id == $id][0]', {
    id: props.draft.parentPage?._ref || ''
  })

  const ancestorPath = parentPage?.pagePath || parentPage?.slug?.current
  const fullPath = `${ancestorPath ? ancestorPath + '/' : '/'}${slug}`

  patch.execute([{
    set: {
      slug: { _type: 'slug', current: slug },
      pagePath: fullPath,
    },
  }])

  await updateChildPagePaths(props.id, fullPath, parentPage?._id)
}
```

**Path Examples:**
- `/about` + `team` → `/about/team`
- `/about/team` + `engineering` → `/about/team/engineering`

## Recursive Child Path Updates

Function recursively updates all descendant page paths when parent changes:

```javascript
const updateChildPagePaths = async (basePageId, basePagePath, parentPageId) => {
  const { relatedPages } = await client.fetch(
    '*[_type=="page" && _id == $id][0]{ _id, "relatedPages": *[_type=="page" && references(^._id)] }',
    { id: basePageId }
  )

  const childPages = relatedPages?.filter((p) => p._id !== parentPageId)

  if (childPages?.length > 0) {
    await Promise.all(childPages.map((child) => {
      const newPath = `${basePagePath}/${child.slug.current}`
      return client.patch(child._id).set({ pagePath: newPath }).commit()
        .then(() => updateChildPagePaths(child._id, newPath, basePageId))
    }))
  }
}
```

Pattern recursively updates grandchildren and great-grandchildren.

## Custom Actions for Singletons

Kariusdx also prevents unpublishing singleton documents (siteSettings, navigation). Pattern ensures global settings remain published.

**Singleton Action Filter:**

```javascript
import { UnpublishAction } from 'part:@sanity/base/document-actions'

export default function useDocumentActions(props) {
  if (['siteSettings', 'navigation'].includes(props.type)) {
    return defaultResolve(props).filter((Action) => Action !== UnpublishAction)
  }
  return defaultResolve(props)
}
```

Singletons have Publish and Delete actions but no Unpublish action. Content editors must keep singletons published to prevent frontend errors.

## Action Hook Dependencies

Custom actions use `@sanity/react-hooks` for document operations and validation status.

**Key Hooks:**

```javascript
import { useDocumentOperation, useValidationStatus } from '@sanity/react-hooks'

const { patch, publish } = useDocumentOperation(props.id, props.type)
const { isValidating, markers } = useValidationStatus(props.id, props.type)
```

**useDocumentOperation:**
- `patch` - Modifies draft document fields
- `publish` - Publishes draft to production
- `unpublish` - Unpublishes published document
- `delete` - Deletes document
- `duplicate` - Duplicates document
- `restore` - Restores previous version

**useValidationStatus:**
- `isValidating` - Boolean indicating if validation is running
- `markers` - Array of validation errors/warnings

Check `markers.length === 0` before enabling publish action.

## When to Use Custom Actions

**Use custom actions for:**

- Auto-generating slugs from titles
- Calculating hierarchical paths from parent references
- Pre-publish validation beyond schema rules
- Preventing unpublish on critical documents
- Custom workflows (approval, scheduling, notifications)
- Multi-document updates (updating children when parent changes)

**Don't use custom actions for:**

- Simple field transformations (use input components instead)
- Validation that can be expressed in schema rules
- Post-publish webhooks (use Sanity webhooks API instead)
- Frontend-only logic (handle in Next.js)

Helix and ripplecom use default actions. No custom actions needed for simple content models.

## Migration to v3+

Kariusdx uses v2 document actions API via "parts" system. Migrating to v3+ requires rewriting actions with modern API.

**v2 (Deprecated):**

```json
{
  "parts": [
    {
      "implements": "part:@sanity/base/document-actions/resolver",
      "path": "./schemas/documentActions.js"
    }
  ]
}
```

**v3+ (Modern):**

```typescript
import { defineConfig } from 'sanity'

export default defineConfig({
  document: {
    actions: (prev, context) => {
      if (context.schemaType === 'page') {
        return prev.map((action) =>
          action.action === 'publish' ? customPublishAction : action
        )
      }
      return prev
    },
  },
})
```

V3+ document actions use functional API instead of React components. Hook-based logic (useState, useEffect) must be refactored to promise-based async functions.

## Alternative: Initial Value Templates

Simple slug auto-generation can use initial value templates instead of custom actions.

**Initial Value Template:**

```typescript
// schemaTypes/documents/page.ts
export default defineType({
  name: 'page',
  type: 'document',
  initialValue: () => ({
    slug: {
      _type: 'slug',
      current: '',
    },
  }),
  fields: [
    {
      name: 'title',
      type: 'string',
    },
    {
      name: 'slug',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 200,
      },
    },
  ],
})
```

Built-in slug field `options.source` auto-generates from title. Simpler than custom action for flat content structures without hierarchical paths.

## Anti-Patterns

**Anti-Pattern 1: Synchronous publish**

```javascript
// ❌ BAD: Doesn't wait for patch to complete
onHandle: () => {
  patch.execute([{ set: { slug } }])
  publish.execute() // Publishes before slug is set
}

// ✅ GOOD: Awaits patch before publishing
onHandle: async () => {
  await patch.execute([{ set: { slug } }])
  publish.execute()
}
```

**Anti-Pattern 2: No validation check**

```javascript
// ❌ BAD: Allows publishing invalid documents
return {
  disabled: false,
  onHandle: () => publish.execute(),
}

// ✅ GOOD: Checks validation before enabling
const { markers } = useValidationStatus(props.id, props.type)
return {
  disabled: markers.length > 0,
  onHandle: () => publish.execute(),
}
```

**Anti-Pattern 3: Unhandled async errors**

```javascript
// ❌ BAD: Silent failures
await updateChildPagePaths(props.id, fullPath, parentPageId)

// ✅ GOOD: Catches and logs errors
try {
  await updateChildPagePaths(props.id, fullPath, parentPageId)
} catch (error) {
  console.error('Failed to update child paths:', error)
  // Optionally: Show toast notification to user
}
```

## Related Patterns

- **singleton-document-management.md** - Preventing unpublish on singletons
- **desk-structure-customization.md** - Custom document views with actions
- **preview-configuration.md** - Pre-publish preview with custom actions

## References

- Kariusdx: `schemas/documentActions.js` (v2 action resolver)
- Kariusdx: `schemas/actions/setSlugAndPublishAction.js` (auto-slug + hierarchical paths)
- Sanity v2 Docs: Document Actions API (deprecated)
- Sanity v3+ Docs: Document Actions API (modern)
