---
title: "Type Guards for Runtime Type Safety"
category: "typescript-conventions"
subcategory: "type-safety"
tags: ["typescript", "type-guards", "runtime-validation", "type-narrowing", "is-predicate"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

# Type Guards for Runtime Type Safety

## Standard

Type guards are functions that perform runtime type checking and narrow TypeScript types using the `is` predicate. Use type guards instead of type assertions for API responses, external data, and unknown values to maintain both compile-time and runtime type safety.

```typescript
// ✅ Type guard provides runtime safety
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    typeof (value as any).id === 'string' &&
    typeof (value as any).name === 'string'
  )
}

function handleData(data: unknown) {
  if (isUser(data)) {
    console.log(data.name)  // Type narrowed to User, runtime validated
  }
}

// ❌ Type assertion bypasses runtime safety
function handleDataUnsafe(data: unknown) {
  const user = data as User
  console.log(user.name)  // Runtime error if data isn't User
}
```

**Source Evidence:**
- helix-dot-com-next: 0 type guard implementations
- kariusdx-next: 0 type guard implementations
- policy-node: 0 type guard implementations
- **Total: 0% adoption (gap pattern, best practice missing)**

## Why Type Guards Are Missing

None of the three Next.js projects implement type guards despite extensive API parsing, JSON deserialization, and external data handling. Projects rely on type assertions instead, creating runtime error risks when data doesn't match expected shapes.

Policy-node uses 70 type assertions for API responses and JSON parsing but no type guards, missing opportunities for runtime validation. Helix and kariusdx also parse Sanity CMS data without type guards, assuming data matches expected types.

This gap represents a significant opportunity to improve runtime safety across all projects by introducing type guards at API boundaries and data transformation points.

## Basic Type Guard Pattern

Type guards are functions that return `value is Type` predicates. TypeScript uses these predicates to narrow types in if statements and conditional branches.

```typescript
// ✅ Basic type guard for object shape
interface User {
  id: string
  name: string
  email: string
}

function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    'email' in value &&
    typeof (value as Record<string, unknown>).id === 'string' &&
    typeof (value as Record<string, unknown>).name === 'string' &&
    typeof (value as Record<string, unknown>).email === 'string'
  )
}

// Usage with type narrowing
function processUserData(data: unknown) {
  if (isUser(data)) {
    // data is now typed as User
    console.log(`User: ${data.name} (${data.email})`)
  } else {
    console.error('Invalid user data')
  }
}
```

The `is` predicate tells TypeScript that when the function returns true, the value can be treated as the specified type in the truthy branch.

## Type Guards for API Responses

API responses are the primary use case for type guards. Replace type assertions with type guards to validate response shapes before using them.

```typescript
// ❌ Current pattern (type assertion, no validation)
async function fetchMunicipalities(): Promise<Municipality[]> {
  const response = await fetch('/api/municipalities')
  const data = await response.json()
  return processApiData(data) as IPolicyApiMunicipalityData[]
}

// ✅ Improved pattern (type guard with validation)
interface Municipality {
  slug: string
  name: string
  state: string | null
}

function isMunicipalityArray(value: unknown): value is Municipality[] {
  return (
    Array.isArray(value) &&
    value.every(item =>
      typeof item === 'object' &&
      item !== null &&
      typeof item.slug === 'string' &&
      typeof item.name === 'string' &&
      (item.state === null || typeof item.state === 'string')
    )
  )
}

async function fetchMunicipalities(): Promise<Municipality[]> {
  const response = await fetch('/api/municipalities')
  const data = await response.json()

  if (!isMunicipalityArray(data)) {
    throw new Error('Invalid municipality data from API')
  }

  return data  // Type is Municipality[] after guard
}
```

This pattern catches malformed API responses at runtime and provides clear error messages instead of cryptic runtime errors later in the application.

## Type Guards for Discriminated Unions

Type guards work especially well with discriminated unions, checking the discriminator field to narrow to specific union members.

```typescript
// ✅ Type guard for discriminated union
type APIResponse =
  | { status: 'success'; data: User[] }
  | { status: 'error'; error: string }
  | { status: 'loading' }

function isSuccessResponse(response: APIResponse): response is { status: 'success'; data: User[] } {
  return response.status === 'success'
}

function isErrorResponse(response: APIResponse): response is { status: 'error'; error: string } {
  return response.status === 'error'
}

function handleResponse(response: APIResponse) {
  if (isSuccessResponse(response)) {
    response.data.forEach(user => console.log(user.name))
  } else if (isErrorResponse(response)) {
    console.error(response.error)
  } else {
    console.log('Loading...')
  }
}
```

Type guards make discriminated union handling more explicit and reusable compared to inline discriminator checks.

## Type Guards for Nullable Values

Type guards can check for null and undefined, providing clearer intent than inline checks and enabling reuse.

```typescript
// ✅ Type guard for non-null values
function isNonNull<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined
}

// Usage in array filtering
const users: (User | null)[] = await fetchUsers()
const validUsers = users.filter(isNonNull)  // Type: User[]

// Usage in conditionals
const config = getConfig()
if (isNonNull(config.apiKey)) {
  initializeAPI(config.apiKey)  // Type narrowed to string
}
```

The `isNonNull` guard is reusable across the codebase and provides better IntelliSense than inline checks.

## Type Guards with Validation Libraries

Combine type guards with validation libraries like Zod for comprehensive runtime validation with automatic type inference.

```typescript
// ✅ Zod schema with type inference
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  age: z.number().optional()
})

type User = z.infer<typeof UserSchema>

function isUser(value: unknown): value is User {
  return UserSchema.safeParse(value).success
}

// Or use Zod's parse directly
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  const data = await response.json()
  return UserSchema.parse(data)  // Throws on invalid data
}
```

Zod provides both runtime validation and type inference, eliminating the need for manual type guard implementations for complex types.

## Type Guards for Sanity CMS Data

Sanity CMS responses have complex, nested structures with nullable fields. Type guards can validate these structures before use.

```typescript
// ✅ Type guard for Sanity content blocks
interface TextBlock {
  _type: 'text'
  content: string
}

interface ImageBlock {
  _type: 'image'
  url: string
  alt: string
}

type ContentBlock = TextBlock | ImageBlock

function isTextBlock(block: unknown): block is TextBlock {
  return (
    typeof block === 'object' &&
    block !== null &&
    (block as any)._type === 'text' &&
    typeof (block as any).content === 'string'
  )
}

function isImageBlock(block: unknown): block is ImageBlock {
  return (
    typeof block === 'object' &&
    block !== null &&
    (block as any)._type === 'image' &&
    typeof (block as any).url === 'string' &&
    typeof (block as any).alt === 'string'
  )
}

function renderBlock(block: unknown) {
  if (isTextBlock(block)) {
    return <p>{block.content}</p>
  } else if (isImageBlock(block)) {
    return <img src={block.url} alt={block.alt} />
  }
  return null  // Unknown block type
}
```

Type guards make Sanity data handling safer and more explicit than assuming data matches expected types.

## Implementing Type Guards Across Projects

To add type guards to the existing codebases, start with API boundaries and high-risk assertion points:

**Priority 1 - API Responses:**
Replace assertions in `processApiData()` calls with type guards that validate response structure.

**Priority 2 - JSON Parsing:**
Add type guards for `JSON.parse()` calls that currently use assertions.

**Priority 3 - Locale/String Narrowing:**
Convert locale assertions like `lang as Locale` to type guards that validate against locale enum.

**Priority 4 - Sanity CMS Data:**
Add type guards for common Sanity block types and content structures.

```typescript
// Current pattern in policy-node (unsafe)
const transformedResponse = processApiData(responseData) as IPolicyApiMunicipalityData[]

// Improved pattern with type guard
function isMunicipalityData(value: unknown): value is IPolicyApiMunicipalityData[] {
  return Array.isArray(value) && value.every(/* validation logic */)
}

const transformedResponse = processApiData(responseData)
if (!isMunicipalityData(transformedResponse)) {
  throw new Error('Invalid municipality data structure')
}
// Now safely use transformedResponse
```

## Performance Considerations

Type guards add runtime overhead for validation checks. For performance-critical paths, consider:
1. Validate once at API boundaries, not on every access
2. Cache validation results for repeated checks
3. Use simpler guards for hot paths (discriminator-only checks)
4. Skip guards for internal data that's already validated

```typescript
// ✅ Validate once at boundary
const users = await fetchUsers()
if (!isUserArray(users)) {
  throw new Error('Invalid user data')
}

// ✅ Use validated data throughout app without re-validating
users.forEach(user => {
  renderUserCard(user)  // No validation needed, already checked
})
```

## Related Patterns

- **Type Assertions Sparingly**: Use type guards instead of assertions
- **Runtime Validation**: Combine with Zod/Yup for complex validation
- **Optional vs Nullable**: Type guards help narrow nullable unions
- **Discriminated Unions**: Type guards enable safe union handling
