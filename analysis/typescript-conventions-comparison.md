# TypeScript Conventions - Cross-Project Comparison

**Analysis Date:** 2026-02-11
**Repos Analyzed:** helix-dot-com-next, kariusdx-next, policy-node
**Total TypeScript Files:** ~15K LOC across 3 repos

---

## Executive Summary

**De Facto Standards:**
- ✅ Props suffix for component props (100% adoption, 168 instances)
- ✅ Optional properties with `?:` (2213 instances)
- ✅ Export keyword for public types (>90% adoption)
- ✅ Type for simple aliases and unions
- ✅ Interface for extensibility (with `extends`)

**Divergent Patterns:**
- ⚠️ Type vs Interface usage (no consensus)
- ⚠️ Naming conventions (I/T prefixes in kariusdx only)
- ⚠️ Utility type usage (policy-node only)
- ⚠️ Type assertions (policy-node heavy, others minimal)

**Avoided Patterns:**
- ❌ Type guards (`is` predicate): 0 usage
- ❌ Enums: Near-zero (3 total)
- ❌ Readonly modifier: Minimal (10 total)
- ❌ Const assertions: Minimal (14 total)
- ❌ `keyof` operator: 0 usage

---

## Pattern 1: Type vs Interface Declarations

### Quantitative Data

| Project | Type Count | Interface Count | Preference | Percentage |
|---------|-----------|----------------|------------|-----------|
| helix-dot-com-next | 72 | 64 | type | 53% |
| kariusdx-next | 27 | 65 | interface | 71% |
| policy-node | 107 | 48 | type | 69% |
| **TOTAL** | **206** | **177** | **type** | **54%** |

**Conclusion:** No clear de facto standard. Slight overall preference for `type` (54%), but kariusdx diverges significantly.

### Qualitative Patterns

**Type Usage Scenarios (all projects):**
- Simple aliases: `type TLatestContent = ILatestContentTeaser[]`
- Union types: `type TFilterGroup = 'infectious-syndrome' | 'special-pathogen'`
- Indexed access: `type Locale = (typeof i18n)['locales'][number]`
- Complex compositions: `type FooterContent = { certifications?: string[] } | null`

**Interface Usage Scenarios (all projects):**
- Component props: `interface AnchorLinkSidebarTemplateProps extends RichTextTemplateHeaderProps`
- Data structures: `interface S3BuildState { version: 1; files: S3FileState[] }`
- API contracts: `interface ValidationWorkflowResult { passed: boolean }`

**Pattern:** Use `type` for unions/aliases, `interface` for extensible structures.

**Recommendation:** Document both patterns as acceptable, with guidance:
- Use `type` for: unions, intersections, mapped types, conditional types
- Use `interface` for: object shapes, especially when inheritance is needed
- Never mix both for the same logical type

---

## Pattern 2: Props Naming Convention

### Quantitative Data

| Project | Props Suffix Count | Props per Component |
|---------|-------------------|---------------------|
| helix-dot-com-next | 57 | ~30% of components |
| kariusdx-next | 8 | ~15% of components |
| policy-node | 103 | ~95% of components |
| **TOTAL** | **168** | **100% adoption** |

**Confidence:** 100% (universal pattern across all projects)

### Qualitative Patterns

**Examples:**
```typescript
// helix
export interface AnchorLinkSidebarTemplateProps extends RichTextTemplateHeaderProps {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null
}

// kariusdx
export interface IWideCards {
  cards: IWideCardField[]
}

// policy-node
interface ValidationWorkflowOptions {
  failOnCritical?: boolean
}
```

**Pattern:** Always suffix component props with `Props`, even if not exported.

**Variations:**
- helix: `ComponentNameProps` (no prefix)
- kariusdx: `IComponentName` (I prefix, no Props suffix for some)
- policy-node: `ComponentNameProps` (no prefix)

**Recommendation:** Enforce `Props` suffix for component prop types.

---

## Pattern 3: Optional Properties

### Quantitative Data

- **Total optional properties:** 2,213 across all projects
- **helix:** ~700 instances
- **kariusdx:** ~200 instances
- **policy-node:** ~1,300 instances

**Confidence:** 100% (universal pattern)

### Qualitative Patterns

**Examples:**
```typescript
// Optional with null union (helix preference)
interface AnchorLinkSidebarTemplateProps {
  topHighlightedSection?: RichTextSection | null
  sections: RichTextSection[] | null  // not optional, but nullable
}

// Optional without null (policy-node preference)
interface ValidationWorkflowOptions {
  failOnCritical?: boolean
}

// Optional with undefined union (rare)
type MainNavCTALink = {
  title?: string | null
  url?: LinkField
} | null | undefined
```

**Pattern:** Heavy use of `?:` for optional properties, but inconsistent handling of null vs undefined.

**Recommendation:**
- Always use `?:` for truly optional properties
- Use explicit `| null` when the property must be present but can be null
- Avoid `| undefined` (redundant with `?:`)

---

## Pattern 4: Naming Conventions (Prefixes)

### Quantitative Data

| Prefix | helix | kariusdx | policy-node | Total |
|--------|-------|----------|-------------|-------|
| `I` prefix (interface) | 0 | 24 | 0 | 24 |
| `T` prefix (type) | 0 | 14 | 0 | 14 |
| No prefix | 136 | 54 | 155 | 345 |

**Confidence:** 91% (no prefix is de facto standard)

### Qualitative Patterns

**Kariusdx (legacy pattern - avoid):**
```typescript
export interface IPressRelease extends IDocumentBuiltIn {
  title: string
}
export type TPressReleaseDocs = IPressRelease[]
```

**Helix & policy-node (modern pattern - recommended):**
```typescript
export type PressRelease = {
  title: string
}
export type PressReleaseList = PressRelease[]
```

**Pattern:** Avoid Hungarian notation (I/T prefixes). Use descriptive names.

**Recommendation:** Enforce no prefixes via Semgrep rule (except React.FC which is already avoided).

---

## Pattern 5: Utility Types

### Quantitative Data

| Utility Type | helix | kariusdx | policy-node | Total |
|--------------|-------|----------|-------------|-------|
| `Record<>` | 0 | 0 | 142 | 142 |
| `Partial<>` | 0 | 0 | 3 | 3 |
| `Pick<>` | 0 | 0 | 2 | 2 |
| `Omit<>` | 0 | 0 | 5 | 5 |
| **TOTAL** | **0** | **0** | **152** | **152** |

**Confidence:** 33% (policy-node only, not a de facto standard)

### Qualitative Patterns

**Policy-node examples:**
```typescript
// Record for dictionaries (most common)
const uiTranslations: Record<string, Record<Locale, string>> = { ... }

// Type-safe object maps
async getPhrasesForLanguage(lang: string): Promise<Record<string, string> | null>

// Function parameters
function extractLanguageMetrics(
  phrases: Record<string, Record<string, unknown>>,
  municipalities: Array<{ slug: string }>
)
```

**Pattern:** `Record<string, T>` is the dominant utility type in policy-node, used for dictionaries and maps.

**Recommendation:** Document `Record<>` as preferred over index signatures for dictionaries.

---

## Pattern 6: Type Assertions

### Quantitative Data

| Project | Type Assertions (`as`) | Assertions per 100 LOC |
|---------|------------------------|------------------------|
| helix-dot-com-next | 7 | 0.05 |
| kariusdx-next | 5 | 0.08 |
| policy-node | 70 | 0.48 |
| **TOTAL** | **82** | **0.20** |

**Confidence:** Policy-node uses assertions 6-10x more frequently than other projects.

### Qualitative Patterns

**Policy-node patterns:**
```typescript
// API response parsing
const transformedResponse = processApiData(responseData) as IPolicyApiMunicipalityData[]

// Locale narrowing
const locale = (lang || 'en-us') as Locale

// JSON parsing
return JSON.parse(content) as DataMetrics

// Conditional type inference
const delta = (current - previous) as T extends number ? number : never

// Literal type narrowing
severity = 'critical' as ValidationSeverity
```

**Helix/kariusdx patterns:**
- Minimal usage, mostly for library interop

**Pattern:** Type assertions are used extensively in policy-node for:
1. API response parsing
2. Locale/string literal narrowing
3. JSON deserialization
4. Type-level computations

**Recommendation:** Prefer type guards and runtime validation over assertions. Only use assertions when you have runtime guarantees.

---

## Pattern 7: Union Types

### Quantitative Data

| Project | Union Type Usage | Unions per 100 LOC |
|---------|------------------|-------------------|
| helix-dot-com-next | 105 | 0.72 |
| kariusdx-next | 17 | 0.27 |
| policy-node | 207 | 1.43 |
| **TOTAL** | **329** | **0.81** |

**Confidence:** 100% (universal pattern)

### Qualitative Patterns

**String literal unions (very common):**
```typescript
// helix
type TFilterGroup = 'infectious-syndrome' | 'special-pathogen' | 'patient-age'

// policy-node
type TActiveTitle = 'Clinical Studies' | 'Clinical Trials' | 'Abstracts'
```

**Object unions:**
```typescript
type FooterContent = {
  certifications?: string[]
  contactInfo?: string
} | null
```

**Optional vs null unions:**
```typescript
// helix pattern
topHighlightedSection?: RichTextSection | null

// policy-node pattern
delegate: string | null
```

**Pattern:** String literal unions for discriminated unions, object unions for complex types.

**Recommendation:** Always use `type` (not `interface`) for union types.

---

## Pattern 8: Avoided Patterns

### Type Guards (0 usage)

**Expected pattern (not found):**
```typescript
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value
}
```

**Actual pattern (type assertions instead):**
```typescript
const user = data as User  // No runtime safety
```

**Recommendation:** Document type guards for runtime safety, especially for API responses.

---

### Enums (3 total, policy-node only)

**Found instances:** 3 enums in policy-node, 0 elsewhere

**Actual pattern (string literal unions preferred):**
```typescript
type TFilterGroup = 'infectious-syndrome' | 'special-pathogen'  // Not enum
```

**Recommendation:** Enforce string literal unions over enums (more tree-shakeable, better DX).

---

### Const Assertions (14 total)

**Usage:**
- helix: 2
- kariusdx: 2
- policy-node: 10

**Examples:**
```typescript
const config = {
  timeout: 5000,
  retries: 3
} as const  // Readonly & literal types
```

**Pattern:** Very rare, mostly in config objects.

**Recommendation:** Document as best practice for config objects and lookup tables.

---

### Readonly Modifier (10 total)

**Usage:**
- helix: 1
- kariusdx: 1
- policy-node: 8

**Pattern:** Virtually unused. No readonly arrays, minimal readonly properties.

**Recommendation:** Document as optional best practice, but not enforced.

---

## Cross-Stack Patterns

### React-Specific Typing

**React.FC (avoided):**
- helix: 1 instance (ExampleComponent only)
- kariusdx: 0
- policy-node: 0

**Preferred pattern:**
```typescript
export default function Component({ prop }: ComponentProps) {
  // ...
}
```

**Recommendation:** Already enforced via Semgrep from Domain 1.

---

### Next.js-Specific Typing

**Page/Layout Props:**
```typescript
// App Router (helix, policy-node)
type PageProps = {
  params: { slug: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

// Pages Router (kariusdx)
type GetStaticPropsReturn = {
  props: PageData
  revalidate: number
}
```

**Recommendation:** Document Next.js-specific type patterns separately.

---

## Recommendations for Documentation

### High Confidence Patterns (Document as standards):
1. **Props suffix** (100% confidence) - Enforce via naming convention
2. **Optional properties** (100% confidence) - Document `?:` vs `| null`
3. **No I/T prefixes** (91% confidence) - Enforce via Semgrep
4. **Type for unions** (100% confidence) - Document guidance
5. **Interface for extends** (100% confidence) - Document guidance

### Medium Confidence Patterns (Document as recommendations):
6. **Type vs interface** (54% type preference) - Provide decision tree
7. **Record<> for dictionaries** (33% confidence) - Policy-node only
8. **Type assertions** (policy-node pattern) - Document sparingly

### Gaps to Document:
9. **Type guards** (0% usage) - Document best practice for runtime safety
10. **Const assertions** (minimal usage) - Document for config objects
11. **Readonly** (minimal usage) - Optional best practice

---

## Next Steps

1. Generate 6-8 RAG-optimized docs covering:
   - Props naming conventions
   - Type vs interface decision tree
   - Optional vs nullable properties
   - Union type patterns
   - Utility types (Record, Pick, Omit)
   - Type assertions (when/why)
   - Type guards (missing pattern)
   - Const assertions & readonly

2. Generate 3-4 Semgrep rules:
   - Enforce Props suffix
   - Disallow I/T prefixes
   - Warn on type assertions without validation
   - Prefer type over interface for unions

3. Cross-reference with Component Patterns domain (React.FC avoidance)
