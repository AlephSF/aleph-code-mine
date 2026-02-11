---
title: "Props Typing Conventions"
category: "component-patterns"
subcategory: "typescript"
tags: ["typescript", "props", "type-alias", "interface", "naming-conventions"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "85%"
last_updated: "2026-02-11"
---

## Recommended Standard: Type Alias

Props definitions use type aliases with the pattern `ComponentNameProps`. Type aliases offer better support for union types, intersection types, and discriminated unions compared to interfaces. Modern Next.js codebases (like policy-node running Next.js 15) standardize on type aliases for all component props.

```typescript
type PageProps = {
  page: PageByUriOrId
  currentLanguage: TLanguage
  lang: string
  unformattedLang: string
  pagePath: string
}

export default async function Page({
  page, currentLanguage, lang, unformattedLang, pagePath,
}: PageProps) {
  // Component implementation
}
```

Type aliases enable advanced TypeScript patterns like discriminated unions for variant-based components:

```typescript
type ButtonBaseProps =
  | BrandButtonProps
  | PrimaryButtonProps
  | SecondaryButtonProps
  | SecondaryOutlineButtonProps
```

## Component Props Naming Convention

Props types follow the pattern `ComponentNameProps` where ComponentName matches the component function name exactly. Props types are colocated in the same file as the component, defined immediately before the component declaration. Exported props types use the `export type` syntax to make them available for reuse in parent components or tests.

```typescript
export type ButtonProps = {
  text: string
  link: string
  className?: string
  buttonStyle?: 'solid' | 'outline'
}

export default function Button({ text, link }: ButtonProps) {
  // Component implementation
}
```

## Interface as Acceptable Alternative

Interfaces are acceptable for simple props definitions, particularly in legacy codebases or when extending third-party types. helix-dot-com-next (Next.js 14) uses interfaces consistently across components. Interfaces work well for straightforward object shapes without unions or complex type operations.

```typescript
export interface TwoUpProps {
  image?: ImageField
  title?: string
  text?: RichTextType
  imageAlignment: 'left' | 'right'
  imagePaddingOverride?: number
}

export default function TwoUp({ image, title, text }: TwoUpProps) {
  // Component implementation
}
```

When using interfaces, follow the same naming convention: `ComponentNameProps`.

## Legacy IPrefix Pattern to Avoid

Older codebases prefix interface names with `I` (e.g., `IButton`, `IComponentProps`). This convention originates from C# and .NET but is not idiomatic in modern TypeScript. Avoid the IPrefix pattern in new code. Modern TypeScript style guides and linters discourage this pattern as unnecessary noise.

```typescript
// Legacy pattern - avoid in new code
export type IButton = {
  text: string
  link?: string
}

// Recommended pattern
export type ButtonProps = {
  text: string
  link?: string
}
```

## Exported vs Local Props

Export props types when they need to be referenced outside the component file (parent components, tests, type utilities). Keep props types local when they are only used within the component file itself. Complex components may define multiple internal types that remain unexported.

```typescript
// Exported - used by parent components
export type ButtonProps = {
  text: string
  link: string
}

// Local - internal to component
type ButtonVariant = 'solid' | 'outline'
```
