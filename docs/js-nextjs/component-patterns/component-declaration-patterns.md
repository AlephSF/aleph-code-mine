---
title: "Component Declaration Patterns"
category: "component-patterns"
subcategory: "typescript"
tags: ["function-declaration", "arrow-function", "async", "return-types"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "55%"
last_updated: "2026-02-11"
---

## Comparison Matrix

Component declaration style varies across codebases with no single dominant pattern. Each approach has specific use cases where it excels. The table below shows patterns observed across three Next.js repositories:

| Pattern | Adoption | Best For | Repos Using |
|---------|----------|----------|-------------|
| Function declaration | 45% | Server components, async components | helix (v14), policy-node (v15) |
| Arrow function + bottom export | 40% | Simple components, SVG components | kariusdx (v12) |
| Arrow function + inline export | 15% | Small utility components | All repos (SVGs) |

Universal rule: Never use `React.FC` or `React.FunctionComponent`. All analyzed repos (100% of files) avoid these deprecated type helpers.

## Function Declarations for Async Server Components

Function declarations work best for React Server Components (RSC) that fetch data or perform async operations. Async components require function declaration syntax to use the `async` keyword properly. Modern Next.js App Router applications (v14+) default to server components and use function declarations extensively.

```typescript
type PageProps = {
  page: PageByUriOrId
  currentLanguage: TLanguage
}

export default async function Page({
  page, currentLanguage,
}: PageProps) {
  const blockPatterns = await getBlockPatternsOptimized(currentLanguage.code)

  return (
    <article>
      <PageComponents blocks={blockPatterns} />
    </article>
  )
}
```

Function declarations also work well for regular synchronous server components:

```typescript
export default function Button({ text, link }: ButtonProps) {
  return (
    <Link href={link}>{text}</Link>
  )
}
```

## Arrow Functions with Bottom Export

Arrow functions combined with bottom exports are common in Pages Router applications (Next.js 12-13) and client components. This pattern works well when explicit return type annotations are desired or when the component needs specific TypeScript types like `JSX.Element`.

```typescript
const Button = ({
  text, link, theme = 'default', handleClick,
}: IButton): JSX.Element => (
  link ? (
    <Link href={link}>{text}</Link>
  ) : (
    <button onClick={handleClick}>{text}</button>
  )
)

export default Button
```

Arrow functions enable concise implicit returns for simple components with minimal logic.

## Arrow Functions for SVG Components

SVG icon components universally use arrow function syntax with explicit `JSX.Element` return type annotation. SVG components are simple presentational components that benefit from concise arrow function syntax.

```typescript
const ArrowRight = (): JSX.Element => (
  <svg width='15' height='16' viewBox='0 0 15 16' fill='none'>
    <path d='M14.7071 8.70711C15.0976 8.31658...' fill='#3F4C77' />
  </svg>
)

export default ArrowRight
```

SVG components rarely accept props beyond optional `className`, making arrow functions with implicit returns ideal.

## Never Use React.FC

All three codebases (100% of 443 component files) avoid `React.FC` and `React.FunctionComponent` type helpers. These utilities were deprecated from React TypeScript best practices due to issues with children typing, default props, and generic components. Modern TypeScript with explicit props types provides better type safety and clarity.

```typescript
// Deprecated pattern - never use
const Button: React.FC<ButtonProps> = ({ text }) => {
  return <button>{text}</button>
}

// Correct pattern - explicit props typing
function Button({ text }: ButtonProps) {
  return <button>{text}</button>
}
```
