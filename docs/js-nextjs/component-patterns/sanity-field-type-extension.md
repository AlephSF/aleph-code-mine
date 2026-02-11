---
title: "Sanity Field Type Extension Pattern"
category: "component-patterns"
subcategory: "cms-integration"
tags: ["sanity-cms", "type-extension", "page-builder", "cms-blocks"]
stack: "js-nextjs"
priority: "low"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

## Pattern Overview

Next.js components integrated with Sanity CMS use a dual-type pattern where component props have a corresponding "Field" type that extends the base props with CMS metadata. Field types add `_key` and `_type` properties required by Sanity's Portable Text and block content systems. This pattern appears in helix-dot-com-next (100% of Sanity-integrated components) but not in other codebases. The pattern enables components to work both as standalone React components and as CMS content blocks.

Components define two types:
- `ComponentNameProps` - Pure React component props
- `ComponentNameField` - CMS integration type extending base props

```typescript
export interface TwoUpProps {
  image?: ImageField
  title?: string
  text?: RichTextType
  imageAlignment: 'left' | 'right'
}

export interface TwoUpField extends TwoUpProps {
  _key: string
  _type: 'twoUp'
}
```

Component implementation uses the base props type, while page builder systems use the Field type.

## Type Extension Structure

### Base Props Type

Base props define the component's functional properties without CMS-specific fields. Base props types export independently for reuse in other components or testing utilities.

```typescript
export interface AccordionProps {
  header?: string
  subheader?: string
  accordionStyle?: 'headerLeft' | 'centered' | 'withImages'
  items: AccordionItemField[]
  theme?: 'dark' | 'light'
}
```

### Field Type Extension

Field types extend base props and add Sanity-required metadata. The `_key` property uniquely identifies the block within a document. The `_type` property maps to the Sanity schema type name for the block. Field types may include additional CMS-specific properties like `hideSection` flags.

```typescript
export interface AccordionField extends AccordionProps {
  hideSection: boolean | null
  _key: string
  _type: 'accordion'
}
```

The `_type` value must match the Sanity schema definition name exactly:

```typescript
// Sanity schema definition
export default {
  name: 'accordion',
  type: 'object',
  title: 'Accordion',
  fields: [
    // field definitions
  ]
}
```

## Usage in Page Builders

Page builder components receive arrays of Field types from Sanity's data layer and map them to component instances. The page builder spreads Field props to component props, passing through both base props and CMS metadata.

```typescript
type PageComponentsProps = {
  blocks: ComponentField[]
}

export default function PageComponents({ blocks }: PageComponentsProps) {
  return (
    <>
      {blocks.map((block) => {
        if (block._type === 'twoUp') {
          return <TwoUp key={block._key} {...block} />
        }
        if (block._type === 'accordion') {
          return <Accordion key={block._key} {...block} />
        }
        return null
      })}
    </>
  )
}
```

Component implementation accepts base props type, ignoring CMS metadata fields:

```typescript
export default function TwoUp({
  image,
  title,
  text,
  imageAlignment,
}: TwoUpProps) {
  // _key and _type are not used in component logic
  return (
    <section>
      {image && <Image src={image.url} alt={image.altText} />}
      {title && <h2>{title}</h2>}
    </section>
  )
}
```

## When to Use This Pattern

Use Field type extensions when:
- Components integrate with Sanity CMS block content
- Components appear in page builders or flexible content sections
- Sanity's Portable Text renderer processes component data
- CMS editors configure component instances in Sanity Studio

Skip this pattern when:
- Components are purely presentational without CMS integration
- Components are not configured through Sanity (layout components, navigation, headers)
- Working with non-Sanity CMS systems
- Building static pages without CMS content

Codebases without Sanity integration (kariusdx-next, policy-node) do not use this pattern. Only helix-dot-com-next with Sanity integration requires Field type extensions.
