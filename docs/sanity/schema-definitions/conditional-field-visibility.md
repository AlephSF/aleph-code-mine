---
title: "Conditional Field Visibility (hidden)"
category: "sanity"
subcategory: "schema-definitions"
tags: ["sanity", "schema", "hidden", "conditional", "dynamic-fields", "ux"]
stack: "sanity"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Conditional Field Visibility (hidden)

## Overview

Sanity's `hidden` property dynamically shows or hides schema fields based on document state, reducing editor cognitive load by displaying only relevant fields. This pattern has 59% adoption across analyzed repositories with 100% consistent syntax. Conditional visibility is most commonly used to hide optional fields until a boolean toggle enables them.

## Pattern Adoption

**Adoption Rate:** 59% (87 of 147 schemas)

- **Ripplecom (v4)**: 52 instances (67% of schemas)
- **Kariusdx (v2)**: 34 instances (53% of schemas)
- **Helix (v3)**: 1 instance (20% of schemas)

**Total:** 87 conditional visibility rules across 147 schemas

## Basic Pattern: Boolean Toggle

### Hide Field Until Toggle Enabled

The most common pattern hides a field until a boolean field is set to true.

```javascript
// helix-dot-com-sanity/schemas/documents/blogPost.js
export default {
  name: 'blogPost',
  type: 'document',
  fields: [
    {
      name: 'showHeroSubheader',
      type: 'boolean',
      title: 'Edit Hero Subheader field',
      initialValue: false,
      group: 'mainContent',
    },
    {
      name: 'subheader',
      type: 'array',
      title: 'Subheader',
      group: 'mainContent',
      of: [{ type: 'block' }],
      hidden: ({ document }) => !document?.showHeroSubheader, // ← Hide until toggle is true
    },
  ],
}
```

**How It Works:**
1. Editor sees `showHeroSubheader` checkbox
2. Checkbox is unchecked by default (`initialValue: false`)
3. `subheader` field is hidden while checkbox is unchecked
4. When checkbox is checked, `subheader` field appears

### Multiple Fields Controlled by Single Toggle

One toggle can show/hide multiple related fields simultaneously.

```javascript
export default {
  name: 'page',
  type: 'document',
  fields: [
    {
      name: 'enableCustomHero',
      type: 'boolean',
      title: 'Enable Custom Hero',
      initialValue: false,
    },
    {
      name: 'heroTitle',
      type: 'string',
      title: 'Hero Title',
      hidden: ({ document }) => !document?.enableCustomHero,
    },
    {
      name: 'heroSubtitle',
      type: 'text',
      title: 'Hero Subtitle',
      hidden: ({ document }) => !document?.enableCustomHero,
    },
    {
      name: 'heroImage',
      type: 'image',
      title: 'Hero Image',
      hidden: ({ document }) => !document?.enableCustomHero,
    },
  ],
}
```

## Conditional Visibility Based on Field Values

### Hide Fields Based on Slug/ID

Kariusdx uses slug values to hide fields on specific pages.

```javascript
// kariusdx-sanity/schemas/documents/page.js
export default {
  name: 'page',
  fields: [
    {
      name: 'slug',
      type: 'slug',
      title: 'Slug',
    },
    {
      name: 'heroImage',
      type: 'image',
      title: 'Hero Image',
      hidden: ({ document }) => document?.slug?.current == 'mobile-app',
      // ↑ Hide hero image on mobile-app page
    },
    {
      name: 'altTitle',
      type: 'string',
      title: 'Alternate Title',
      hidden: ({ document }) => document?.slug?.current == 'mobile-app',
    },
  ],
}
```

**Use Case:** Special pages (homepage, landing pages) may need different field configurations.

### Hide Fields Based on Select/Radio Values

Fields can be hidden based on selection values.

```typescript
// Example: Different fields for internal vs external links
export default defineType({
  name: "link",
  type: "object",
  fields: [
    defineField({
      name: "linkType",
      type: "string",
      title: "Link Type",
      options: {
        list: [
          { title: "Internal", value: "internal" },
          { title: "External", value: "external" },
        ],
      },
      initialValue: "internal",
    }),
    defineField({
      name: "internalLink",
      type: "reference",
      title: "Internal Page",
      to: [{ type: "page" }],
      hidden: ({ parent }) => parent?.linkType !== "internal",
      // ↑ Show only when linkType is "internal"
    }),
    defineField({
      name: "externalUrl",
      type: "url",
      title: "External URL",
      hidden: ({ parent }) => parent?.linkType !== "external",
      // ↑ Show only when linkType is "external"
    }),
  ],
})
```

## Context Objects: document vs parent

### Document Context (Top-Level Fields)

Use `{ document }` to access sibling fields at the document root level.

```typescript
{
  name: 'heroImage',
  type: 'image',
  hidden: ({ document }) => !document?.enableHero,
  //       ↑ document = entire document data
}
```

### Parent Context (Nested Object Fields)

Use `{ parent }` to access sibling fields within the same object.

```typescript
export default defineType({
  name: "button",
  type: "object",
  fields: [
    defineField({
      name: "variant",
      type: "string",
      options: {
        list: ["primary", "secondary", "custom"],
      },
    }),
    defineField({
      name: "customColor",
      type: "color",
      hidden: ({ parent }) => parent?.variant !== "custom",
      //       ↑ parent = the button object data
    }),
  ],
})
```

### Array Item Context

When hiding fields in array items, use `{ parent }` for the array item data.

```typescript
{
  name: 'items',
  type: 'array',
  of: [
    {
      type: 'object',
      fields: [
        {
          name: 'type',
          type: 'string',
          options: {
            list: ['text', 'image', 'video'],
          },
        },
        {
          name: 'videoUrl',
          type: 'url',
          hidden: ({ parent }) => parent?.type !== 'video',
          //       ↑ parent = current array item
        },
      ],
    },
  ],
}
```

## Complex Conditional Logic

### Multiple Conditions (AND Logic)

Hide a field only when multiple conditions are met.

```typescript
defineField({
  name: "advancedSettings",
  type: "object",
  hidden: ({ document }) => {
    const isAdmin = document?.author?.role === "admin"
    const isPublished = document?.status === "published"

    // Show only for admin users AND published documents
    return !(isAdmin && isPublished)
  },
})
```

### Multiple Conditions (OR Logic)

Hide a field if any condition is true.

```typescript
defineField({
  name: "editWarning",
  type: "string",
  hidden: ({ document }) => {
    const isDraft = document?._id?.startsWith('drafts.')
    const isUnpublished = !document?.publishedAt

    // Hide on drafts OR unpublished documents
    return isDraft || isUnpublished
  },
})
```

### Inverted Logic (Show When Condition False)

Sometimes it's clearer to express "show when X is false" than "hide when X is true".

```typescript
// Option 1: Hide when false
hidden: ({ document }) => !document?.showAdvanced

// Option 2: Hide when true (inverted logic)
hidden: ({ document }) => document?.hideAdvanced === true
```

## Performance Considerations

### Memoization for Complex Logic

Complex conditional logic should be efficient to avoid re-renders.

```typescript
// ❌ Bad: Creates new array every render
hidden: ({ document }) => {
  const hiddenSlugs = ['home', 'about', 'contact'] // ← New array every time
  return hiddenSlugs.includes(document?.slug?.current)
}

// ✅ Good: Direct comparison
hidden: ({ document }) => {
  const slug = document?.slug?.current
  return slug === 'home' || slug === 'about' || slug === 'contact'
}
```

### Avoid Heavy Computations

The `hidden` function runs on every keystroke; avoid expensive operations.

```typescript
// ❌ Bad: Heavy computation on every render
hidden: ({ document }) => {
  const content = document?.content || []
  const wordCount = content
    .map(block => block.children?.map(child => child.text).join(' '))
    .join(' ')
    .split(/\s+/)
    .length
  return wordCount < 500 // Expensive calculation
}

// ✅ Good: Simple property check
hidden: ({ document }) => !document?.enableAdvanced
```

## Validation with Hidden Fields

### Hidden Fields and Required Validation

Hidden fields bypass validation by default.

```typescript
defineField({
  name: "externalUrl",
  type: "url",
  validation: (Rule) => Rule.required(), // Only enforced when visible
  hidden: ({ parent }) => parent?.linkType !== "external",
})
```

**Behavior:** Sanity automatically disables required validation for hidden fields.

### Conditional Required Validation

For explicit control, use conditional validation.

```typescript
defineField({
  name: "externalUrl",
  type: "url",
  validation: (Rule) =>
    Rule.custom((value, context) => {
      const linkType = context.parent?.linkType

      if (linkType === "external" && !value) {
        return "External URL is required when link type is external"
      }

      return true
    }),
  hidden: ({ parent }) => parent?.linkType !== "external",
})
```

## Common Use Cases

### Feature Flags

Toggle experimental or premium features on/off per document.

```typescript
fields: [
  defineField({
    name: "enableBetaFeatures",
    type: "boolean",
    title: "Enable Beta Features",
    initialValue: false,
  }),
  defineField({
    name: "betaWidget",
    type: "object",
    title: "Beta Widget Configuration",
    hidden: ({ document }) => !document?.enableBetaFeatures,
  }),
]
```

### Localization

Show/hide locale-specific fields based on selected language.

```typescript
fields: [
  defineField({
    name: "language",
    type: "string",
    options: {
      list: ["en", "es", "fr"],
    },
  }),
  defineField({
    name: "spanishTitle",
    type: "string",
    title: "Título (Español)",
    hidden: ({ document }) => document?.language !== "es",
  }),
  defineField({
    name: "frenchTitle",
    type: "string",
    title: "Titre (Français)",
    hidden: ({ document }) => document?.language !== "fr",
  }),
]
```

### Progressive Disclosure

Reveal advanced options only when basic setup is complete.

```typescript
fields: [
  defineField({
    name: "title",
    type: "string",
    validation: (Rule) => Rule.required(),
  }),
  defineField({
    name: "content",
    type: "text",
    validation: (Rule) => Rule.required(),
  }),
  defineField({
    name: "advancedOptions",
    type: "object",
    hidden: ({ document }) => {
      // Show only when required fields are filled
      return !document?.title || !document?.content
    },
  }),
]
```

## Anti-Patterns

### Hiding Required Fields by Default

Don't hide required fields unless there's a clear path to make them visible.

**❌ Bad: Required field hidden by default**
```typescript
{
  name: 'requiredField',
  type: 'string',
  validation: (Rule) => Rule.required(),
  hidden: ({ document }) => !document?.showAdvanced, // Hard to discover
}
```

**✅ Good: Optional field hidden by default**
```typescript
{
  name: 'optionalField',
  type: 'string',
  hidden: ({ document }) => !document?.showAdvanced, // OK - it's optional
}
```

### Overusing Conditional Visibility

Too many hidden fields create confusion about what's available.

**❌ Bad: Half the fields are hidden**
```typescript
fields: [
  { name: 'field1', hidden: ({ document }) => /* ... */ },
  { name: 'field2', hidden: ({ document }) => /* ... */ },
  { name: 'field3', hidden: ({ document }) => /* ... */ },
  { name: 'field4', hidden: ({ document }) => /* ... */ },
  { name: 'field5', hidden: ({ document }) => /* ... */ },
  // Editors never know what fields exist
]
```

**✅ Good: Selective use for truly optional features**
```typescript
fields: [
  { name: 'title' }, // Always visible
  { name: 'content' }, // Always visible
  { name: 'slug' }, // Always visible
  { name: 'seo' }, // Always visible
  { name: 'advancedOptions', hidden: ({ document }) => !document?.showAdvanced }, // Optional
]
```

### Complex Multi-Level Nesting

Avoid hiding fields based on deeply nested conditions.

**❌ Bad: Complex nested logic**
```typescript
hidden: ({ document }) =>
  !document?.settings?.features?.advanced?.experimental?.enabled
```

**✅ Good: Flatten structure or use direct flags**
```typescript
hidden: ({ document }) => !document?.enableExperimental
```

## Implementation Checklist

- [ ] Use `hidden` for optional features toggled by boolean fields
- [ ] Use `{ document }` for document-level field access
- [ ] Use `{ parent }` for nested object field access
- [ ] Pair `hidden` with `initialValue` on toggle fields
- [ ] Avoid hiding required fields by default
- [ ] Keep conditional logic simple (avoid heavy computations)
- [ ] Test hidden field behavior: toggle on/off, verify validation
- [ ] Document why fields are hidden in code comments

## Related Patterns

- **Initial Values**: Pair `hidden` with `initialValue` for toggle fields
- **Validation Rules**: Hidden fields bypass required validation
- **Field Groups**: `hidden` works independently of field group assignment
- **Conditional Validation**: Use custom validation for conditional requirements

## References

- Ripplecom (v4): 52 instances (67% of schemas)
- Kariusdx (v2): 34 instances (53% of schemas, page-specific hiding common)
- Helix (v3): 1 instance (boolean toggle pattern)
- Sanity Conditional Fields: https://www.sanity.io/docs/conditional-fields
