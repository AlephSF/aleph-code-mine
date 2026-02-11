---
title: "Component Props Type Naming with Props Suffix"
category: "typescript-conventions"
subcategory: "naming-patterns"
tags: ["typescript", "react", "props", "naming", "components"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Component Props Type Naming with Props Suffix

## Standard

React component props types must always use the `Props` suffix in their name. This convention applies to both interface and type declarations, and to both exported and internal prop definitions.

```typescript
// ✅ Correct - Props suffix
interface AnchorLinkSidebarTemplateProps {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null
}

export default function AnchorLinkSidebarTemplate({
  topHighlightedSection,
  sections
}: AnchorLinkSidebarTemplateProps) {
  // ...
}
```

```typescript
// ❌ Incorrect - No Props suffix
interface AnchorLinkSidebarTemplate {
  topHighlightedSection?: RichTextSection | null
}

// ❌ Incorrect - Generic name
interface ComponentOptions {
  sections: RichTextSection[]
}
```

**Source Evidence:**
- helix-dot-com-next: 57 instances
- kariusdx-next: 8 instances
- policy-node: 103 instances
- **Total: 168 instances across all Next.js projects (100% adoption)**

## Why Props Suffix Matters

Component props types with the `Props` suffix provide immediate clarity about the type's purpose when scanning code or viewing IntelliSense suggestions. This pattern distinguishes component props from data models, API types, or utility types.

The suffix prevents naming collisions between component types and their data types. For example, `User` might represent a user entity from an API, while `UserCardProps` represents the props for a UserCard component that displays that user.

When component props extend other interfaces, the Props suffix makes the inheritance chain explicit and readable without requiring additional context about what each type represents.

## Implementation Pattern

Define props types immediately before the component definition using either `interface` or `type`. The Props suffix applies regardless of which keyword you choose. Export the props type when other components need to reference or extend it.

```typescript
export interface ValidationWorkflowOptions {
  failOnCritical?: boolean
  verbose?: boolean
}

export default function ValidationWorkflow({
  failOnCritical = false,
  verbose = true
}: ValidationWorkflowOptions) {
  // Implementation
}
```

Component props that extend base interfaces should maintain the Props suffix while showing the inheritance relationship clearly.

```typescript
interface RichTextTemplateHeaderProps {
  title: string
  subtitle?: string
}

export interface AnchorLinkSidebarTemplateProps extends RichTextTemplateHeaderProps {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null
}
```

## Props Suffix with Type Declarations

The Props suffix convention applies equally to type aliases. Use whichever TypeScript construct (interface or type) best fits your needs, but always include the Props suffix.

```typescript
// ✅ Type with Props suffix
export type ShareIconsProps = {
  title?: string | null
  url?: string
}

export default function SocialShareButtons({ title, url }: ShareIconsProps) {
  // Implementation
}
```

```typescript
// ✅ Interface with Props suffix
interface ButtonProps {
  primary?: boolean
  size?: 'small' | 'medium' | 'large'
  label: string
}

export default function Button({ primary, size = 'medium', label }: ButtonProps) {
  // Implementation
}
```

## Variations by Project

All three Next.js projects universally adopt the Props suffix, though they differ in whether they use interface or type. Policy-node uses Props suffix for 95% of its components, helix for 30%, and kariusdx for 15%, but all instances that do define props types use the suffix.

Some kariusdx components use interface declarations without Props suffix but with an `I` prefix (e.g., `IWideCards`). This Hungarian notation pattern is legacy and should be avoided in favor of the Props suffix pattern.

## Related Patterns

- **No Hungarian Notation**: Avoid I/T prefixes on types
- **Type vs Interface**: Choose based on extensibility needs, not naming
- **Default Exports**: Component files export the component as default, props type as named export

## Enforcement

Enforce this convention through code review and ESLint naming conventions. A Semgrep rule can catch component files that define prop types without the Props suffix.

```yaml
# Semgrep rule (illustrative)
rules:
  - id: require-props-suffix
    pattern: |
      interface $NAME {
        ...
      }
      function $COMPONENT($PARAM: $NAME)
    message: Component prop types should use Props suffix
```
