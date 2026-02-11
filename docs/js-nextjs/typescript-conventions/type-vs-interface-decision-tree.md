---
title: "Type vs Interface Decision Tree"
category: "typescript-conventions"
subcategory: "type-definitions"
tags: ["typescript", "interface", "type", "decision-tree", "best-practices"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "54%"
last_updated: "2026-02-11"
---

# Type vs Interface Decision Tree

## Standard

TypeScript provides both `type` and `interface` keywords for defining types. Neither is universally better - choose based on the specific use case. Use `type` for unions, intersections, and complex type compositions. Use `interface` for object shapes that need inheritance or extension.

```typescript
// ✅ Type for unions and compositions
type FilterGroup = 'infectious-syndrome' | 'special-pathogen' | 'patient-age'

type ResourceWithMetadata = Resource & {
  lastModified: Date
  author: string
}

// ✅ Interface for extensible object shapes
interface BaseComponentProps {
  className?: string
  testId?: string
}

interface ButtonProps extends BaseComponentProps {
  label: string
  onClick: () => void
}
```

**Source Evidence:**
- Total type declarations: 206 (helix: 72, kariusdx: 27, policy-node: 107)
- Total interface declarations: 177 (helix: 64, kariusdx: 65, policy-node: 48)
- **Overall preference: 54% type, 46% interface (no strong consensus)**

## Use Type For: Unions and Aliases

Type aliases excel at creating unions, intersections, and complex type compositions. Interface cannot represent union types, making type the only choice for these scenarios.

```typescript
// ✅ Type for string literal unions
type ButtonVariant = 'primary' | 'secondary' | 'danger'

type LoadingState = 'idle' | 'loading' | 'success' | 'error'

type FilterGroup = 'infectious-syndrome' | 'special-pathogen' | 'patient-age'

// ✅ Type for object unions
type FooterContent = {
  certifications?: string[]
  contactInfo?: string
} | null

// ❌ Interface cannot represent unions
interface ButtonVariant {  // This doesn't work for union types
  // ...
}
```

Type aliases also work well for simple renaming or aliasing of existing types, especially when creating semantic names for primitive types or library types.

```typescript
// ✅ Type for aliasing
type Slug = string
type Timestamp = number
type UserId = string

type LatestContent = LatestContentTeaser[]
type PressReleaseList = PressRelease[]
```

## Use Type For: Indexed Access and Mapped Types

Type aliases support advanced TypeScript features like indexed access types, mapped types, and conditional types. These patterns appear frequently in policy-node for extracting types from configuration objects.

```typescript
// ✅ Indexed access types
const i18n = {
  locales: ['en-us', 'es-mx', 'pt-br'] as const,
  defaultLocale: 'en-us'
}

type Locale = (typeof i18n)['locales'][number]
// Type is: 'en-us' | 'es-mx' | 'pt-br'

type RawLocale = (typeof i18n)['rawLocales'][number]

// ✅ Type for Record-based dictionaries
type TranslationKeys = Record<string, Record<Locale, string>>

type LocationLabels = Record<string, string>
```

Mapped types and utility types like Pick, Omit, Partial work naturally with type aliases, though interfaces can use them via intersection.

```typescript
// ✅ Type with utility types
type UserBase = {
  id: string
  name: string
  email: string
  role: string
}

type PublicUser = Omit<UserBase, 'email' | 'role'>

type PartialUser = Partial<UserBase>
```

## Use Interface For: Extension and Inheritance

Interfaces support the `extends` keyword for clear inheritance relationships. This pattern appears consistently in component props that build on base props, especially in helix and kariusdx projects.

```typescript
// ✅ Interface with extends
interface RichTextTemplateHeaderProps {
  title: string
  subtitle?: string
  description?: string | null
}

interface AnchorLinkSidebarTemplateProps extends RichTextTemplateHeaderProps {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null
}

// ✅ Multiple interface extension
interface DocumentBuiltIn {
  _id: string
  _type: string
  _createdAt: string
}

interface PressRelease extends DocumentBuiltIn, SinglePressReleasePage {
  title: string
  slug: Slug
  publishedDate: string
}
```

While types can achieve similar results with intersections, the extends syntax is more explicit about the inheritance relationship and produces clearer error messages.

```typescript
// ⚠️ Type with intersection works but less clear intent
type AnchorLinkSidebarTemplateProps = RichTextTemplateHeaderProps & {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null
}
```

## Use Interface For: Declaration Merging

Interfaces support declaration merging, where multiple interface declarations with the same name automatically merge into a single interface. This pattern rarely appears in application code but is useful for augmenting third-party library types.

```typescript
// ✅ Interface declaration merging
interface Window {
  customAnalytics?: {
    track: (event: string) => void
  }
}

// Later in another file
interface Window {
  customFeatureFlag?: boolean
}

// Both declarations merge into one Window interface
```

Type aliases do not support declaration merging. Attempting to declare the same type twice results in a compiler error.

## Object Shapes: Either Works

For simple object shapes without unions, extensions, or advanced type features, both type and interface work equally well. Choose based on consistency with surrounding code or team preference.

```typescript
// ✅ Both acceptable for simple objects
interface S3BuildState {
  version: 1
  files: S3FileState[]
  lastBuildTime: string
}

type S3BuildState = {
  version: 1
  files: S3FileState[]
  lastBuildTime: string
}
```

Project patterns show divergence here: helix and policy-node prefer type (53-69%), while kariusdx prefers interface (71%). There is no strong technical reason for either choice in simple object cases.

## Decision Tree Summary

**Choose Type When:**
- Creating union types (string literals, object unions, etc.)
- Aliasing existing types with semantic names
- Using indexed access, mapped types, or conditional types
- Using utility types like Pick, Omit, Partial, Record
- Type composition with intersections

**Choose Interface When:**
- Defining object shapes that will be extended
- Creating component props hierarchies with extends
- Augmenting third-party types (declaration merging)
- Working in a codebase that prefers interfaces for objects

**Either Works For:**
- Simple object shapes without extension
- Component props that don't extend other props
- Data models and API response types

## Project-Specific Patterns

**Policy-node (69% type preference):**
- Heavy use of indexed access types
- Record<string, T> for dictionaries
- Union types for configuration
- Type assertions for API parsing

**Helix (53% type preference):**
- Mixed usage, slight type preference
- Type for query return types
- Interface for component props with extends

**Kariusdx (71% interface preference):**
- Interface for most object shapes (legacy pattern with I prefix)
- Type with T prefix for arrays and unions
- Interface extends used frequently

## Common Pitfalls

Never mix type and interface for the same logical construct. Pick one and use it consistently within a module or feature area.

```typescript
// ❌ Mixing type and interface confuses intent
interface UserBase {
  id: string
  name: string
}

type User = UserBase & {  // Inconsistent - should be interface extends
  email: string
}
```

Avoid using interface for union types by wrapping the union in an object. Use type directly instead.

```typescript
// ❌ Awkward interface wrapping union
interface ButtonConfig {
  variant: 'primary' | 'secondary' | 'danger'
}

// ✅ Type for the union directly
type ButtonVariant = 'primary' | 'secondary' | 'danger'

interface ButtonConfig {
  variant: ButtonVariant
}
```

## Related Patterns

- **No Hungarian Notation**: Don't prefix types with I or T
- **Union Type Patterns**: Type for all union definitions
- **Props Naming Convention**: Interface/type with Props suffix for components
