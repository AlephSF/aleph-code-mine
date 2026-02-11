---
title: "Record Type for Dictionary Objects"
category: "typescript-conventions"
subcategory: "utility-types"
tags: ["typescript", "record", "dictionary", "map", "utility-types"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "33%"
last_updated: "2026-02-11"
---

# Record Type for Dictionary Objects

## Standard

Use `Record<K, V>` utility type for dictionary objects and maps with string keys where the exact keys are not known at compile time. Record provides better type safety than index signatures and clearer intent than generic object types.

```typescript
// ✅ Record for translation dictionaries
const uiTranslations: Record<string, Record<Locale, string>> = {
  All: {
    'en-us': 'All',
    'es-mx': 'Todos',
    'pt-br': 'Todos'
  },
  Resources: {
    'en-us': 'Resources',
    'es-mx': 'Recursos',
    'pt-br': 'Recursos'
  }
}

// ✅ Record for dynamic key-value maps
const locationLabels: Record<string, string> = {
  'new-york': 'New York',
  'los-angeles': 'Los Angeles',
  'chicago': 'Chicago'
}
```

**Source Evidence:**
- helix-dot-com-next: 0 Record instances
- kariusdx-next: 0 Record instances
- policy-node: 142 Record instances
- **Total: 142 instances (33% adoption, policy-node only)**

## Record vs Index Signatures

Record types provide the same functionality as index signatures but with more explicit intent and better composability with other utility types.

```typescript
// ✅ Record type (preferred)
type TranslationMap = Record<string, string>

const translations: TranslationMap = {
  hello: 'Hello',
  goodbye: 'Goodbye'
}

// ⚠️ Index signature (less explicit)
type TranslationMap = {
  [key: string]: string
}
```

Record types work better with type inference and generic functions, making them more suitable for reusable utilities and library code. The policy-node project uses Record extensively in its i18n and data validation systems.

```typescript
// ✅ Generic function with Record
async function getPhrasesForLanguage(
  lang: string
): Promise<Record<string, string> | null> {
  const allPhrases = await this.getAllPhrases()
  return allPhrases[lang as Locale]
}

// ✅ Nested Records for structured translations
export const uiTranslations: Record<string, Record<Locale, string>> = {
  FilterLabel: {
    'en-us': 'Filter by:',
    'es-mx': 'Filtrar por:',
    'pt-br': 'Filtrar por:'
  }
}
```

## Record with Union Types for Keys

Record types can constrain keys to specific string literal unions, providing exhaustiveness checking and autocomplete for known keys while allowing dynamic access.

```typescript
// ✅ Record with literal union keys
type Locale = 'en-us' | 'es-mx' | 'pt-br'

type LocalizedContent = Record<Locale, string>

const content: LocalizedContent = {
  'en-us': 'Hello',
  'es-mx': 'Hola',
  'pt-br': 'Olá'
  // TypeScript error if any locale is missing
}

// ✅ Partial Record for optional keys
type PartialContent = Partial<Record<Locale, string>>

const partialContent: PartialContent = {
  'en-us': 'Hello'
  // Other locales are optional
}
```

This pattern appears frequently in policy-node's i18n system where translations must exist for all supported locales but may be partially loaded during development.

## Record for Function Returns

Record types commonly appear in function return types for API responses and data transformations that return dictionary-like objects.

```typescript
// ✅ Record in return type
function getRequiredFieldsByCategory(): Record<string, RequiredFieldDefinition[]> {
  const grouped: Record<string, RequiredFieldDefinition[]> = {}

  requiredFields.forEach(field => {
    if (!grouped[field.category]) {
      grouped[field.category] = []
    }
    grouped[field.category].push(field)
  })

  return grouped
}

// ✅ Record for metrics aggregation
function extractMetrics(data: unknown[]): Record<string, number> {
  const byCountry: Record<string, number> = {}
  const byState: Record<string, number> = {}

  // Populate dictionaries
  data.forEach(item => {
    byCountry[item.country] = (byCountry[item.country] || 0) + 1
  })

  return byCountry
}
```

Record types in return signatures communicate that the function returns a map-like object with dynamic keys, helping callers understand they need to iterate or lookup keys rather than access fixed properties.

## Record with unknown for Type-Safe Dynamic Access

When the value types are not known or vary, use `Record<string, unknown>` to maintain type safety while allowing dynamic access. This pattern appears in policy-node's data validation where API responses have heterogeneous value types.

```typescript
// ✅ Record with unknown for heterogeneous values
function extractDataQualityMetrics(
  rawData: Record<string, unknown>[],
  transformedData: Municipality[]
) {
  rawData.forEach(muni => {
    requiredFields.forEach(field => {
      const value = (muni as Record<string, unknown>)[field]
      if (value === null || value === undefined || value === '') {
        // Missing required field
      }
    })
  })
}

// ✅ Nested Record with mixed types
type LocaleData = Record<string, {
  locationLabels?: Record<string, unknown>
  phrases?: Record<string, string>
}>
```

Using `unknown` rather than `any` maintains type safety by requiring type assertions or guards before using the values, preventing accidental type errors.

## Record for Configuration Objects

Record types work well for configuration objects and option maps where keys represent configuration categories and values represent settings.

```typescript
// ✅ Record for feature flags
type FeatureFlags = Record<string, boolean>

const flags: FeatureFlags = {
  enableNewUI: true,
  enableBetaFeatures: false,
  enableAnalytics: true
}

// ✅ Record for environment-specific config
type EnvironmentConfig = Record<string, {
  apiUrl: string
  timeout: number
}>

const config: EnvironmentConfig = {
  development: { apiUrl: 'http://localhost:3000', timeout: 30000 },
  production: { apiUrl: 'https://api.example.com', timeout: 10000 }
}
```

## When Not to Use Record

Avoid Record when object shape is known and fixed. Use interface or type with explicit properties for better type checking and IntelliSense.

```typescript
// ❌ Record for known shape (too loose)
type UserData = Record<string, unknown>

const user: UserData = {
  id: '123',
  name: 'John'
}

user.email  // No type checking, no autocomplete

// ✅ Explicit interface for known shape
interface UserData {
  id: string
  name: string
  email?: string
}

const user: UserData = {
  id: '123',
  name: 'John'
}

user.email  // Type-safe, autocomplete works
```

Avoid Record for simple string-string maps where a const object with as const assertion provides better type inference.

```typescript
// ❌ Record for static mapping (no literal types)
const statusColors: Record<string, string> = {
  success: 'green',
  error: 'red',
  warning: 'yellow'
}

const color = statusColors['success']  // Type: string

// ✅ As const for literal types
const statusColors = {
  success: 'green',
  error: 'red',
  warning: 'yellow'
} as const

const color = statusColors['success']  // Type: 'green'
type Status = keyof typeof statusColors  // 'success' | 'error' | 'warning'
```

## Policy-Node Pattern: Extensive Record Usage

Policy-node uses Record extensively (142 instances) for its i18n system, data validation, and municipality data aggregation. This pattern supports its multi-locale architecture where translations and location data are dynamically keyed.

```typescript
// Real-world example from policy-node
export const uiTranslations: Record<string, Record<Locale, string>> = {
  All: { 'en-us': 'All', 'es-mx': 'Todos', 'pt-br': 'Todos' },
  ShowMore: { 'en-us': 'Show More', 'es-mx': 'Mostrar más', 'pt-br': 'Mostrar mais' }
}

async function getPhrasesForLanguage(lang: string): Promise<Record<string, string> | null> {
  const allPhrases = await this.getAllPhrases()
  const languagePhrases = allPhrases[lang as Locale]
  return languagePhrases
}
```

The pattern works well for policy-node's use case but is not universally adopted across other projects, likely because helix and kariusdx have simpler i18n needs or use different i18n libraries.

## Related Patterns

- **Type vs Interface Decision Tree**: Use type for Record definitions
- **Union Types**: Combine Record with union keys for type safety
- **Type Assertions**: Record<string, unknown> often requires assertions for value access
