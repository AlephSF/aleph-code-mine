---
title: "Union Type Patterns for Type Safety"
category: "typescript-conventions"
subcategory: "type-composition"
tags: ["typescript", "union-types", "type-safety", "discriminated-unions"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Union Type Patterns for Type Safety

## Standard

Union types combine multiple types with the `|` operator to represent values that could be one of several types. Use string literal unions for finite sets of values instead of enums. Use object unions for variant types with discriminator fields. Always define union types with the `type` keyword, never `interface`.

```typescript
// ✅ String literal unions
type FilterGroup = 'infectious-syndrome' | 'special-pathogen' | 'patient-age'

type ActiveTitle = 'Clinical Studies' | 'Clinical Trials' | 'Abstracts' | 'Articles'

// ✅ Object unions with discriminator
type FooterContent = {
  certifications?: string[]
  contactInfo?: string
  type: 'standard'
} | {
  customHTML: string
  type: 'custom'
}
```

**Source Evidence:**
- Total union type instances: 329 across all projects
- helix-dot-com-next: 105 unions (0.72 per 100 LOC)
- kariusdx-next: 17 unions (0.27 per 100 LOC)
- policy-node: 207 unions (1.43 per 100 LOC)
- **100% adoption across all projects**

## String Literal Unions Replace Enums

String literal unions provide type-safe enumeration without the runtime overhead and quirks of TypeScript enums. They compile to nothing, tree-shake perfectly, and work naturally with string values from APIs and databases.

```typescript
// ✅ String literal union (preferred)
type FilterGroup = 'infectious-syndrome' | 'special-pathogen' | 'patient-age' | 'patient-subtype'

function filterStudies(group: FilterGroup) {
  // Type-safe string comparison
  if (group === 'infectious-syndrome') {
    // TypeScript knows this is the exact string
  }
}

// ❌ Enum (avoid - only 3 instances total across all projects)
enum FilterGroup {
  InfectiousSyndrome = 'infectious-syndrome',
  SpecialPathogen = 'special-pathogen'
}
```

String literal unions work seamlessly with JSON, API responses, and database values. No reverse mapping lookup is needed, and the compiled JavaScript is just the string value itself.

```typescript
// API response with string values
const response = {
  filters: [
    { group: 'infectious-syndrome', value: 'pneumonia' },
    { group: 'patient-age', value: 'pediatric' }
  ]
}

// Type-safe access without runtime overhead
type Filter = {
  group: FilterGroup
  value: string
}

const filters: Filter[] = response.filters  // Type checks perfectly
```

## Union Types with Null and Undefined

Union types frequently combine object types with null or undefined to represent optional or nullable data, especially in Sanity CMS responses and API data.

```typescript
// ✅ Nullable unions for CMS data
type FooterContent = {
  certifications?: string[]
  contactInfo?: string
} | null

type MainNavCTALink = {
  title?: string | null
  url?: LinkField
} | null | undefined

// ✅ Optional property with nullable value
interface AnchorLinkSidebarTemplateProps {
  topHighlightedSection?: RichTextSection | null  // Can be absent OR null
  sections: RichTextSection[] | null               // Must be present, can be null
}
```

Distinguish between `| null` (explicitly set to null), `| undefined` (missing), and `?:` (optional property). Use the pattern that matches your data source's semantics.

## Discriminated Unions for Variants

Discriminated unions use a common literal property (discriminator) to distinguish between union members. TypeScript narrows the type based on the discriminator value, enabling type-safe handling of variants.

```typescript
// ✅ Discriminated union with type field
type APIResponse =
  | { status: 'success'; data: User[] }
  | { status: 'error'; error: string }
  | { status: 'loading' }

function handleResponse(response: APIResponse) {
  // TypeScript narrows type based on status
  if (response.status === 'success') {
    response.data.forEach(user => console.log(user.name))
  } else if (response.status === 'error') {
    console.error(response.error)
  }
}
```

Choose discriminator field names that clearly indicate the variant purpose. Common discriminators include `type`, `kind`, `status`, and `_type` (Sanity convention).

```typescript
// ✅ Discriminated union for component variants
type ButtonVariant =
  | { kind: 'primary'; icon?: IconName }
  | { kind: 'secondary'; outline: boolean }
  | { kind: 'link'; href: string }

function Button(props: ButtonVariant) {
  switch (props.kind) {
    case 'primary':
      return <PrimaryButton icon={props.icon} />
    case 'secondary':
      return <SecondaryButton outline={props.outline} />
    case 'link':
      return <a href={props.href}>Link</a>
  }
}
```

## Union Types for Property Values

Union types commonly define property values with finite sets of valid options, replacing magic strings and providing autocomplete in IDEs.

```typescript
// ✅ Union type for property values
type ButtonSize = 'small' | 'medium' | 'large'

type ButtonVariant = 'primary' | 'secondary' | 'danger'

interface ButtonProps {
  size?: ButtonSize
  variant?: ButtonVariant
  label: string
}

// ✅ Type-safe usage with autocomplete
<Button size="medium" variant="primary" label="Click me" />

// ❌ Type error for invalid values
<Button size="extra-large" />  // Error: Type '"extra-large"' is not assignable to type 'ButtonSize'
```

Union types for property values prevent typos and provide excellent developer experience with IntelliSense showing all valid options.

## Nested Union Types

Complex data structures sometimes require unions at multiple levels, especially when working with Sanity CMS's flexible content modeling.

```typescript
// ✅ Nested unions for flexible content
type ContentBlock =
  | { _type: 'text'; content: string }
  | { _type: 'image'; url: string; alt: string }
  | { _type: 'video'; videoId: string }
  | { _type: 'embed'; html: string }

type PageSection = {
  title: string
  blocks: ContentBlock[] | null
  layout: 'single-column' | 'two-column' | 'grid'
}

function renderSection(section: PageSection) {
  section.blocks?.forEach(block => {
    switch (block._type) {
      case 'text':
        return <p>{block.content}</p>
      case 'image':
        return <img src={block.url} alt={block.alt} />
      // TypeScript ensures all cases handled
    }
  })
}
```

TypeScript's exhaustiveness checking ensures all union variants are handled in switch statements and if/else chains, preventing runtime errors from unhandled cases.

## Array Unions vs Union of Arrays

Distinguish between arrays of union types (array items can be different types) and unions that include array types (value is either one type or an array).

```typescript
// ✅ Array of unions - each item can be different type
type MixedContent = Array<string | number | boolean>

const content: MixedContent = ['text', 42, true, 'more text']

// ✅ Union including arrays - value is one type OR an array
type SingleOrArray<T> = T | T[]

const single: SingleOrArray<string> = 'hello'
const multiple: SingleOrArray<string> = ['hello', 'world']
```

Sanity CMS and search params often use the "single or array" pattern where a field can contain one item or multiple items of the same type.

```typescript
// ✅ Next.js search params pattern
type SearchParams = {
  query?: string | string[]
  tags?: string | string[]
  page?: string
}

function parseSearchParams(params: SearchParams) {
  // Normalize to array
  const tags = Array.isArray(params.tags) ? params.tags : [params.tags].filter(Boolean)
  return tags
}
```

## Type Narrowing with Unions

TypeScript automatically narrows union types based on type guards, equality checks, and discriminator fields. Leverage this narrowing to write type-safe code without assertions.

```typescript
// ✅ Type narrowing with typeof
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase()  // TypeScript knows this is string
  } else {
    return value.toFixed(2)     // TypeScript knows this is number
  }
}

// ✅ Type narrowing with discriminated union
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string }

function handleResult<T>(result: Result<T>) {
  if (result.success) {
    console.log(result.data)   // TypeScript knows data exists
  } else {
    console.error(result.error)  // TypeScript knows error exists
  }
}
```

## Related Patterns

- **Type vs Interface Decision Tree**: Always use `type` for unions
- **No Enums**: Use string literal unions instead
- **Type Guards**: Custom guards for complex union narrowing
- **Optional vs Nullable**: Understand `| null` vs `| undefined` vs `?:`
