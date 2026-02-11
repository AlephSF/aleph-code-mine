---
title: "Avoid Hungarian Notation in Type Names"
category: "typescript-conventions"
subcategory: "naming-patterns"
tags: ["typescript", "naming", "interfaces", "types", "anti-pattern"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "91%"
last_updated: "2026-02-11"
---

# Avoid Hungarian Notation in Type Names

## Standard

TypeScript type and interface names should not use Hungarian notation prefixes like `I` for interfaces or `T` for types. Use descriptive names that clearly communicate the type's purpose without encoding its keyword in the name.

```typescript
// ✅ Correct - Descriptive name, no prefix
interface PressRelease {
  title: string
  slug: Slug
  publishedDate: string
}

type PressReleaseList = PressRelease[]

// ❌ Incorrect - Hungarian notation
interface IPressRelease {
  title: string
}

type TPressReleaseDocs = IPressRelease[]
```

**Source Evidence:**
- helix-dot-com-next: 0 instances of I/T prefixes (0%)
- policy-node: 0 instances of I/T prefixes (0%)
- kariusdx-next: 24 I-prefixed interfaces, 14 T-prefixed types (legacy)
- **Total: 345 types without prefixes vs 38 with prefixes (91% no-prefix adoption)**

## Why Avoid Hungarian Notation

Hungarian notation prefixes encode type metadata in the name itself, which TypeScript's type system already provides. The `I` or `T` prefix adds no semantic value and creates visual noise when reading code. Modern IDEs show type information on hover, making prefixes redundant.

Type prefixes create unnecessary coupling between the name and the keyword used to define it. If you refactor an interface to a type (or vice versa), you must rename it everywhere to maintain consistency, even though the semantic meaning hasn't changed.

Hungarian notation is a legacy pattern from languages like C++ and early C# where interfaces needed visual distinction from classes. TypeScript has no such requirement - the type system distinguishes interfaces from other constructs automatically.

## Descriptive Names Over Prefixes

Use names that describe what the type represents, not how it's implemented. Focus on domain concepts and business logic rather than TypeScript syntax.

```typescript
// ✅ Descriptive names convey purpose
interface User {
  id: string
  name: string
  email: string
}

type UserRole = 'admin' | 'editor' | 'viewer'

interface UserPermissions {
  canEdit: boolean
  canDelete: boolean
}

// ❌ Prefixes add noise, no additional meaning
interface IUser {
  id: string
}

type TUserRole = 'admin' | 'editor' | 'viewer'

interface IUserPermissions {
  canEdit: boolean
}
```

When type names might collide with variable names or component names, add a descriptive suffix like `Data`, `Props`, `Config`, or `Response` rather than a generic prefix.

```typescript
// ✅ Descriptive suffix disambiguates
interface UserProps {
  user: User
  onUpdate: (user: User) => void
}

type UserSearchResponse = {
  users: User[]
  total: number
}

// ❌ Prefix doesn't clarify relationship
interface IUserProps {
  user: IUser
}

type TUserSearchResponse = {
  users: IUser[]
}
```

## Legacy Pattern in Kariusdx

The kariusdx-next codebase uses I/T prefixes extensively due to legacy conventions. This pattern should not be extended to new code and should be gradually refactored out during maintenance.

```typescript
// Kariusdx legacy pattern (avoid in new code)
export interface IPressRelease extends IDocumentBuiltIn, ISinglePressReleasePage {
  title: string
  slug: Slug
  publishedDate: string
}

export type TPressReleaseDocs = IPressRelease[]

// Modern pattern (use for new code)
export interface PressRelease extends DocumentBuiltIn, SinglePressReleasePage {
  title: string
  slug: Slug
  publishedDate: string
}

export type PressReleaseList = PressRelease[]
```

Helix and policy-node projects have zero instances of I/T prefixes, demonstrating that modern TypeScript codebases universally avoid this pattern.

## Interface vs Type Without Prefixes

Without Hungarian notation, the choice between `interface` and `type` becomes purely technical, based on the type's structure and needs rather than arbitrary naming conventions.

Use `interface` when:
- Defining object shapes that might be extended
- Creating contracts for classes or objects
- You need declaration merging (rare in modern code)

Use `type` when:
- Creating union types or intersections
- Using mapped types, conditional types, or utility types
- Defining type aliases for primitives or complex compositions

```typescript
// ✅ Interface for extensible object shapes
interface BaseProps {
  className?: string
}

interface ButtonProps extends BaseProps {
  label: string
  onClick: () => void
}

// ✅ Type for unions and compositions
type ButtonVariant = 'primary' | 'secondary' | 'danger'

type ButtonSize = 'small' | 'medium' | 'large'

type ButtonConfig = {
  variant: ButtonVariant
  size: ButtonSize
}
```

The type keyword appears before the name in both cases, making prefixes completely redundant for distinguishing types from interfaces in code.

## Refactoring Legacy I/T Prefixes

When updating kariusdx code or migrating patterns between projects, remove I/T prefixes systematically. Use IDE refactoring tools to rename types throughout the codebase, updating all imports and usages.

```typescript
// Before (legacy)
import { IPressRelease, TPressReleaseDocs } from '@/types/pressRelease'

function PressReleaseList({ releases }: { releases: TPressReleaseDocs }) {
  return releases.map((release: IPressRelease) => (
    <div key={release._id}>{release.title}</div>
  ))
}

// After (refactored)
import { PressRelease, PressReleaseList } from '@/types/pressRelease'

function PressReleaseListView({ releases }: { releases: PressReleaseList }) {
  return releases.map((release: PressRelease) => (
    <div key={release._id}>{release.title}</div>
  ))
}
```

## Related Patterns

- **Props Naming Convention**: Use Props suffix for component props
- **Type vs Interface Decision Tree**: Choose based on structure, not naming
- **Descriptive Type Names**: Names should reflect domain concepts

## Enforcement

Enforce this standard through:
- ESLint rule: `@typescript-eslint/naming-convention` with no I/T prefix patterns
- Code review: Flag new I/T prefixed types
- Semgrep rule: Detect interface I[A-Z] and type T[A-Z] patterns

```yaml
# Semgrep rule
rules:
  - id: no-interface-i-prefix
    pattern: interface I$NAME
    message: Avoid I prefix on interfaces - use descriptive names
    severity: WARNING
```
