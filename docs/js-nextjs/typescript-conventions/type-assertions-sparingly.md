---
title: "Use Type Assertions Sparingly"
category: "typescript-conventions"
subcategory: "type-safety"
tags: ["typescript", "type-assertions", "as", "type-safety", "runtime-validation"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Use Type Assertions Sparingly

## Standard

Type assertions with the `as` keyword bypass TypeScript's type checking and should be used sparingly. Prefer type guards, runtime validation, and proper typing over assertions. Use assertions only when you have runtime guarantees that TypeScript cannot infer, such as API parsing, JSON deserialization, or framework-specific patterns.

```typescript
// ✅ Type assertion for API parsing with runtime guarantee
const transformedResponse = processApiData(responseData) as IPolicyApiMunicipalityData[]

// ✅ Type assertion for locale narrowing with validation
const locale = (lang || 'en-us') as Locale

// ❌ Type assertion without runtime guarantee
const user = apiResponse as User  // No validation - runtime error risk
```

**Source Evidence:**
- helix-dot-com-next: 7 type assertions (0.05 per 100 LOC)
- kariusdx-next: 5 type assertions (0.08 per 100 LOC)
- policy-node: 70 type assertions (0.48 per 100 LOC)
- **Total: 82 assertions (policy-node uses 6-10x more than other projects)**

## When Type Assertions Are Acceptable

Type assertions are acceptable when TypeScript cannot infer types that you know to be correct from runtime context. Common valid scenarios include API parsing after validation, JSON deserialization, and narrowing string literals to specific types.

```typescript
// ✅ JSON parsing with known shape
const content = fs.readFileSync(inputPath, 'utf-8')
return JSON.parse(content) as DataMetrics

// ✅ Locale narrowing from validated string
const locale = (lang || 'en-us') as Locale

// ✅ API response after transformation
const transformedMunicipalities = processApiData(responseData) as IPolicyApiMunicipalityData[]
const municipalities = transformedMunicipalities.map(createViewModel)
```

These patterns appear throughout policy-node's data pipeline where external data is validated and transformed before being asserted to application types. The assertions document the transformation contract without re-implementing type checking that already happened at runtime.

## Assertions After Runtime Validation

Type assertions become safe after runtime validation confirms the data shape. Combine Zod, Yup, or custom validation with assertions to maintain type safety.

```typescript
// ✅ Assertion after validation
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email()
})

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  const data = await response.json()

  // Validate at runtime
  const validated = UserSchema.parse(data)

  // Safe assertion after validation
  return validated as User
}

// ❌ Assertion without validation (unsafe)
async function fetchUserUnsafe(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return await response.json() as User  // Runtime error risk
}
```

Runtime validation libraries like Zod provide type inference, potentially eliminating the need for assertions entirely by deriving types from schemas.

## Prefer Type Guards Over Assertions

Type guards provide runtime checking with type narrowing, eliminating the need for assertions while maintaining type safety.

```typescript
// ✅ Type guard (preferred)
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    'email' in value
  )
}

function handleData(data: unknown) {
  if (isUser(data)) {
    console.log(data.name)  // Type narrowed to User
  }
}

// ❌ Type assertion (bypass type checking)
function handleDataUnsafe(data: unknown) {
  const user = data as User
  console.log(user.name)  // Runtime error if data isn't User
}
```

Policy-node has zero type guard implementations despite heavy API and JSON parsing, relying entirely on assertions. This is a gap - type guards would improve runtime safety.

## Assertions for Conditional Type Inference

Complex generic types sometimes require assertions to help TypeScript's type inference, especially with conditional types and template literal types.

```typescript
// ✅ Assertion for conditional type
function detectChange<T extends number | string>(
  previous: T,
  current: T
): MetricChange<T> {
  const delta = (current - previous) as T extends number ? number : never
  const percentageChange = calculatePercentageChange(previous, current)

  return {
    delta,
    percentageChange,
    severity: 'info' as ValidationSeverity
  } as MetricChange<T>
}
```

These assertions help TypeScript understand type-level computations that are correct but too complex for inference. Document why the assertion is needed with a comment.

## Literal Type Narrowing

Assertions commonly narrow generic strings to specific literal types when the value is validated or constrained by runtime logic.

```typescript
// ✅ Literal narrowing with runtime guarantee
if (absPercentChange >= thresholds.critical && thresholds.critical > 0) {
  severity = 'critical' as ValidationSeverity
} else if (absPercentChange >= thresholds.warning) {
  severity = 'warning' as ValidationSeverity
} else {
  severity = 'info' as ValidationSeverity
}

// ✅ Locale narrowing from validated input
const locale = (lang || 'en-us') as Locale
```

This pattern is safe when the runtime logic guarantees the value matches the asserted type. The assertion documents the contract without duplicating the validation logic.

## Assertions for Third-Party Library Interop

Sometimes third-party libraries have incomplete or incorrect type definitions. Assertions can work around these limitations, but document the reason with a comment.

```typescript
// ✅ Assertion with explanation comment
// Sanity returns _type as string, but we know it's a specific literal
const blockType = block._type as 'text' | 'image' | 'video'

// ✅ Working around incomplete library types
const configValue = process.env.CONFIG as Record<string, unknown>
```

Consider contributing type fixes upstream or using module augmentation instead of scattering assertions throughout your codebase.

## Anti-Patterns to Avoid

Never use double assertions to force incompatible types. This bypasses all type safety and is a code smell indicating architectural issues.

```typescript
// ❌ Double assertion (extremely unsafe)
const user = someValue as unknown as User

// ❌ Assertion to any (defeats TypeScript)
const data = apiResponse as any

// ❌ Assertion instead of proper typing
function getUser(): User {
  return JSON.parse(localStorage.getItem('user')!) as User
}
```

Avoid assertions in place of proper return type annotations or generic constraints. Fix the types rather than asserting.

```typescript
// ❌ Assertion instead of proper return type
function processData(data: unknown) {
  return validate(data) as ProcessedData
}

// ✅ Proper return type with validation
function processData(data: unknown): ProcessedData | null {
  if (isProcessedData(data)) {
    return data
  }
  return null
}
```

## Policy-Node Heavy Assertion Usage

Policy-node uses assertions 6-10x more frequently than helix or kariusdx, primarily for:
1. API response parsing: `processApiData(responseData) as IPolicyApiMunicipalityData[]`
2. Locale narrowing: `(lang || 'en-us') as Locale`
3. JSON parsing: `JSON.parse(content) as DataMetrics`
4. Record value access: `(muni as Record<string, unknown>)[field]`

This pattern works for policy-node's data pipeline where transformation functions provide implicit validation, but other projects achieve similar results with less assertion usage, suggesting policy-node could benefit from more explicit type guards.

```typescript
// Policy-node pattern (heavy assertions)
const transformedResponse = processApiData(responseData) as IPolicyApiMunicipalityData[]
const languagePhrases = allPhrases[lang as Locale]
const localeData = phrases[locale] as Record<string, unknown> | undefined

// Alternative pattern with type guards (more explicit)
function isIPolicyApiMunicipalityData(data: unknown): data is IPolicyApiMunicipalityData {
  return Array.isArray(data) && data.every(item => /* validation */)
}

if (isIPolicyApiMunicipalityData(transformedResponse)) {
  // Use with confidence
}
```

## Recommended Practices

1. **Validate then assert**: Always validate data before asserting types
2. **Prefer type guards**: Use `is` predicates for reusable type checking
3. **Document assertions**: Explain why TypeScript cannot infer the type
4. **Avoid double assertions**: Never use `as unknown as T`
5. **Use validation libraries**: Zod, Yup, or io-ts for complex validations
6. **Limit assertion scope**: Assert at API boundaries, not throughout application

## Related Patterns

- **Type Guards**: Prefer custom type guards over assertions
- **Runtime Validation**: Use Zod/Yup for API response validation
- **Record Type for Dictionaries**: Often combined with unknown and assertions
