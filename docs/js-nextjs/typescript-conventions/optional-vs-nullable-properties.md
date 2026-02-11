---
title: "Optional vs Nullable Property Patterns"
category: "typescript-conventions"
subcategory: "type-safety"
tags: ["typescript", "optional", "nullable", "undefined", "null"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Optional vs Nullable Property Patterns

## Standard

TypeScript provides two distinct ways to indicate that a property might be absent: optional properties (`?:`) and nullable types (`| null`). These patterns have different semantics and should be used based on whether the property can be missing entirely versus explicitly set to null.

```typescript
// ✅ Optional property - may be absent from object
interface ValidationWorkflowOptions {
  failOnCritical?: boolean  // Property might not exist
  verbose?: boolean
}

// ✅ Nullable property - must be present, can be null
interface AnchorLinkSidebarTemplateProps {
  topHighlightedSection: RichTextSection | null  // Must be present
  sections: RichTextSection[] | null
}

// ⚠️ Both optional AND nullable - common in Sanity CMS data
interface MainNavCTALink {
  title?: string | null  // Can be missing OR explicitly null
  url?: LinkField | null
}
```

**Source Evidence:**
- Total optional properties (`?:`): 2,213 across all projects
- helix-dot-com-next: ~700 instances
- kariusdx-next: ~200 instances
- policy-node: ~1,300 instances

## Optional Properties Pattern

Optional properties use the `?:` syntax to indicate that a property may not exist on the object at all. Runtime checks with `in` operator or property access will reflect whether the property was provided. This pattern works best for component props with default values or configuration objects where omitted values have clear defaults.

```typescript
interface ButtonProps {
  primary?: boolean
  size?: 'small' | 'medium' | 'large'
  label: string  // Required property
}

export default function Button({
  primary = false,     // Default for optional prop
  size = 'medium',     // Default for optional prop
  label                // Required, no default
}: ButtonProps) {
  // Implementation
}
```

Optional properties are type-narrowed to `T | undefined`, not just `T`. Access them with optional chaining or provide defaults to avoid undefined checks throughout your component.

```typescript
// ✅ Optional chaining
const hasSection = props.topSection?.content

// ✅ Default parameter
function ValidationWorkflow({ verbose = true }: ValidationWorkflowOptions) {
  if (verbose) {
    console.log('Running validation...')
  }
}

// ❌ Unnecessary undefined union
interface BadProps {
  size?: 'small' | 'medium' | undefined  // Redundant - ?:  already includes undefined
}
```

## Nullable Properties Pattern

Nullable properties use explicit `| null` union types to indicate that the property must be present on the object but its value can be null. This pattern appears frequently in Sanity CMS responses where fields are queried but may have null values in the content.

```typescript
interface ResourceTeaser {
  title: string
  description: string | null  // Must be queried, but may be null
  image: ImageField | null
  tags: string[] | null
}

function ResourceCard({ title, description, image, tags }: ResourceTeaser) {
  // Explicit null checks required
  if (description === null) {
    return <div>{title}</div>
  }

  return (
    <div>
      <h3>{title}</h3>
      <p>{description}</p>
      {image && <img src={image.url} />}
      {tags && <TagList tags={tags} />}
    </div>
  )
}
```

Nullable properties force explicit null handling at compile time. TypeScript will error if you access nullable properties without checking for null first, preventing runtime null reference errors.

## Combined Optional and Nullable Pattern

Sanity CMS data and API responses frequently use both optional and nullable together (`?: T | null`). This pattern indicates that the property might be missing from the response AND might explicitly be null when present.

```typescript
// Common in Sanity query results
type FooterNavigation = {
  navigationSections?: {
    navigationLinks?: {
      title?: string | null
      url?: string | null
    }[] | null
  }[] | null
}

function FooterNav({ navigationSections }: FooterNavigation) {
  // Multiple levels of optional chaining required
  return (
    <nav>
      {navigationSections?.map(section =>
        section.navigationLinks?.map(link =>
          link.title && link.url ? (
            <a href={link.url}>{link.title}</a>
          ) : null
        )
      )}
    </nav>
  )
}
```

This combined pattern requires careful null/undefined checking with optional chaining and nullish coalescing. The pattern is verbose but accurately reflects the reality of CMS data where fields can be unconfigured (undefined) or intentionally empty (null).

## Decision Tree for Optional vs Nullable

Choose optional properties (`?:`) when:
- Component props have sensible default values
- Configuration objects where omitted keys have defaults
- Internal type definitions where absence has clear meaning
- TypeScript will error if property is accessed without optional chaining

Choose nullable types (`| null`) when:
- API responses where null is semantically different from undefined
- Sanity CMS fields that may be queried but empty
- Database fields that can be NULL
- You need to distinguish "not provided" from "explicitly empty"

Combine both (`?: T | null`) when:
- Working with Sanity CMS or GraphQL responses
- Optional API fields that can also be explicitly null
- Nested objects where intermediate levels might be missing

## Avoid Redundant Undefined Unions

Never explicitly add `| undefined` to optional properties. The `?:` syntax already includes undefined in the property's type. Adding it explicitly is redundant and creates noise in type definitions.

```typescript
// ❌ Redundant undefined
interface BadProps {
  size?: 'small' | 'medium' | undefined
  title?: string | undefined
}

// ✅ Correct - ?:  already includes undefined
interface GoodProps {
  size?: 'small' | 'medium'
  title?: string
}
```

## Null Checking Patterns

Use optional chaining (`?.`) for optional properties and explicit null checks for nullable properties. Combine both when handling Sanity data with optional nullable properties.

```typescript
interface PageData {
  hero?: HeroSection
  content: ContentSection | null
  footer?: FooterSection | null
}

function Page({ hero, content, footer }: PageData) {
  // ✅ Optional chaining for optional property
  const heroTitle = hero?.title

  // ✅ Explicit null check for nullable property
  if (content === null) {
    return <ErrorState />
  }

  // ✅ Combined checking for optional nullable
  const footerLinks = footer?.links ?? []

  return (
    <div>
      {hero && <Hero {...hero} />}
      <Content {...content} />
      {footer && <Footer {...footer} />}
    </div>
  )
}
```

## Related Patterns

- **Props Naming Convention**: Props types should use Props suffix
- **Type Guards**: Use type guards for complex null/undefined narrowing
- **Nullish Coalescing**: Use `??` operator for default values with null/undefined
