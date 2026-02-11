---
title: "Default Exports for Components"
category: "component-patterns"
subcategory: "exports"
tags: ["exports", "default-export", "barrel-exports", "imports"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

## Universal Default Export Standard

Next.js component files use default exports exclusively. All 443 component .tsx files across helix-dot-com-next, kariusdx-next, and policy-node follow this pattern without exception. Named exports are reserved for props types, utility functions, or subcomponents when needed. The component itself always exports as default, enabling clean barrel re-exports and simplified import syntax.

```typescript
// Button.tsx
export type ButtonProps = {
  text: string
  link: string
}

export default function Button({ text, link }: ButtonProps) {
  return <Link href={link}>{text}</Link>
}
```

## Barrel Export Re-Export Pattern

Component folders contain an `index.ts` barrel file that re-exports the default export using `export { default }` syntax. Barrel files do not rename or transform exports. The re-export maintains the default export pattern, allowing consumers to import using the folder name.

```typescript
// Button/index.ts
export { default } from './Button'
```

Import paths reference the folder, and the default export is automatically resolved:

```typescript
import Button from '@/components/Button'
import TwoUp from '@/components/TwoUp'
```

## Component Declaration Export Variants

### Inline Default Export

Components can export the function declaration inline. Inline exports are common for simple components or arrow function components.

```typescript
export default function Button({ text }: ButtonProps) {
  return <button>{text}</button>
}
```

Arrow function variant:

```typescript
const Button = ({ text }: ButtonProps): JSX.Element => (
  <button>{text}</button>
)

export default Button
```

### Bottom Default Export

Alternatively, components declare the function first and export at the bottom of the file. Bottom exports are common in files with multiple exports (component plus types or utilities) or compound components.

```typescript
function Button({ text }: ButtonProps) {
  return <button>{text}</button>
}

export default Button
```

Both patterns are acceptable. Choose based on component complexity and team preference, but maintain consistency within a codebase.

## When to Use Named Exports

Named exports appear alongside default exports for supplementary items. Props types are frequently exported to enable reuse in parent components or testing utilities. Compound components (like Button.Text and Button.Icon) export the namespace object as default.

```typescript
// Export props type for reuse
export type ButtonProps = {
  text: string
}

// Export compound component as default
const Button = {
  Text: TextButton,
  Icon: IconButton,
}

export default Button
```
