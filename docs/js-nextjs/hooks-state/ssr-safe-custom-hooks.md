---
title: "SSR-Safe Custom Hooks for Next.js"
category: "hooks-state"
subcategory: "custom-hooks"
tags: ["react", "hooks", "custom-hooks", "ssr", "nextjs", "hydration"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# SSR-Safe Custom Hooks for Next.js

## Standard

Custom hooks in Next.js must handle server-side rendering safely by checking for browser APIs before accessing them and tracking component mount state to avoid hydration mismatches. Return values as tuple arrays with `as const` for proper TypeScript inference.

```typescript
// ✅ SSR-safe custom hook
const useIsBelowBreakpoint = (gridBreakpointUp = '768px'): readonly [boolean] => {
  const gridBreakpointUpMatch = typeof window !== 'undefined' &&
    window.matchMedia(`(min-width: ${gridBreakpointUp})`)

  const [isBelowBreakpoint, setIsBelowBreakpoint] = useState(false)
  const [isComponentMounted, setIsComponentMounted] = useState(false)

  useEffect(() => {
    setIsBelowBreakpoint(gridBreakpointUpMatch && !gridBreakpointUpMatch.matches)
    setIsComponentMounted(true)
  }, [])

  return [isBelowBreakpoint] as const
}

// ❌ Not SSR-safe - window access causes server error
const useWindowWidth = () => {
  const [width, setWidth] = useState(window.innerWidth) // Crashes on server
  return width
}
```

**Source Evidence:**
- Custom hooks found: 4 total (helix: 2, kariusdx: 2, policy-node: 0)
- SSR-safe patterns: 4/4 (100%)
- Tuple return with `as const`: 4/4 (100%)
- Component mount tracking: 4/4 (100%)

## Window API Safety Check

Browser APIs like window, document, navigator, and localStorage don't exist during server-side rendering. Check `typeof window !== 'undefined'` before accessing these APIs to prevent server errors.

```typescript
const useIsBelowBreakpoint = (breakpoint = '768px'): readonly [boolean] => {
  // ✅ Safe check before window access
  const mediaQuery = typeof window !== 'undefined' &&
    window.matchMedia(`(min-width: ${breakpoint})`)

  const [isBelowBreakpoint, setIsBelowBreakpoint] = useState(false)

  useEffect(() => {
    // Only runs client-side, safe to use mediaQuery
    if (mediaQuery) {
      setIsBelowBreakpoint(!mediaQuery.matches)
    }
  }, [])

  return [isBelowBreakpoint] as const
}
```

The check returns false on server, allowing the hook to run without crashing. Client-side code inside useEffect can safely use the API since effects only run in the browser.

## Component Mount Tracking

Track whether the component has mounted to avoid hydration mismatches where server-rendered HTML differs from initial client render. Initialize state optimistically on server, then update after mount.

```typescript
const useHeaderHeight = () => {
  const [headerHeight, setHeaderHeight] = useState(172) // Default for SSR
  const [isComponentMounted, setIsComponentMounted] = useState(false)

  useEffect(() => {
    // Only runs client-side after mount
    const currentHeight = document.getElementById('siteHeader')?.offsetHeight
    if (currentHeight) {
      setHeaderHeight(currentHeight)
    }
    setIsComponentMounted(true)
  }, [])

  return [headerHeight] as const
}
```

Default state value (172) matches server render. Client updates to actual value after mount, avoiding React hydration warnings. The isComponentMounted flag can gate conditional rendering if needed.

## Tuple Return with as const

Return arrays from custom hooks using `as const` assertion for proper TypeScript tuple inference. This gives consumers fixed-length arrays with specific types per position, matching useState's return type pattern.

```typescript
// ✅ Tuple return with as const
const useIsBelowBreakpoint = (breakpoint = '768px'): readonly [boolean] => {
  const [isBelowBreakpoint, setIsBelowBreakpoint] = useState(false)
  // ...
  return [isBelowBreakpoint] as const
}

// Consumer gets tuple, not array
const [isMobile] = useIsBelowBreakpoint('768px') // Type: boolean

// ❌ Without as const
const useIsBelowBreakpoint = (breakpoint = '768px'): boolean[] => {
  // ...
  return [isBelowBreakpoint]
}

// Consumer gets array, loses tuple semantics
const [isMobile] = useIsBelowBreakpoint('768px') // Type: boolean[]
```

The readonly tuple type prevents accidental mutation and documents that the hook returns a fixed structure. This pattern matches React's built-in hooks like useState.

## Event Listener Setup Pattern

Custom hooks that add event listeners must set them up inside useEffect for SSR safety and proper cleanup. Event listener setup outside useEffect runs during render, which happens on both server and client.

```typescript
const useIsMobile = (breakpoint = '769px'): readonly [boolean] => {
  const mediaQuery = typeof window !== 'undefined' &&
    window.matchMedia(`(min-width: ${breakpoint})`)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    if (mediaQuery) {
      setIsMobile(!mediaQuery.matches)
    }
  }, [])

  // ⚠️ Event listener setup outside useEffect (codebase pattern)
  if (mediaQuery) {
    const onBreakpointChange = (e: MediaQueryListEvent) => {
      setIsMobile(!e.matches)
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', onBreakpointChange)
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(onBreakpointChange)
    }
  }

  return [isMobile] as const
}
```

While this pattern works (the if(mediaQuery) check prevents server errors), best practice moves listener setup into useEffect with cleanup for better lifecycle management.

## Improved Pattern with useEffect Cleanup

Refactor the event listener pattern to use useEffect with proper cleanup, ensuring listeners are removed on unmount and re-added when dependencies change.

```typescript
const useMediaQuery = (query: string): readonly [boolean] => {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia(query)
    setMatches(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setMatches(e.matches)
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange)
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange)
      } else if (mediaQuery.removeListener) {
        mediaQuery.removeListener(handleChange)
      }
    }
  }, [query])

  return [matches] as const
}
```

This improved pattern keeps all window access inside useEffect (server-safe), adds cleanup, and properly handles dependency changes.

## Browser Compatibility in Custom Hooks

Support both modern and legacy browser APIs for maximum compatibility, especially for media queries where Safari < 14 uses deprecated methods.

```typescript
const useBreakpoint = (minWidth = '768px'): readonly [boolean] => {
  const [isAbove, setIsAbove] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia(`(min-width: ${minWidth})`)
    setIsAbove(mq.matches)

    const onChange = (e: MediaQueryListEvent) => setIsAbove(e.matches)

    // Modern: addEventListener
    if (mq.addEventListener) {
      mq.addEventListener('change', onChange)
      return () => mq.removeEventListener('change', onChange)
    }
    // Legacy: addListener
    else if (mq.addListener) {
      mq.addListener(onChange)
      return () => mq.removeListener?.(onChange)
    }
  }, [minWidth])

  return [isAbove] as const
}
```

Check for modern methods first, fall back to legacy. Cleanup must mirror the setup method used.

## DOM Measurement Hooks

Hooks measuring DOM element properties must wait for client-side mount and handle element absence safely.

```typescript
const useHeaderHeight = (): readonly [number] => {
  const [headerHeight, setHeaderHeight] = useState(172)

  useEffect(() => {
    function getHeaderHeight() {
      const header = document.getElementById('siteHeader')
      if (header) {
        setHeaderHeight(header.offsetHeight)
      }
    }

    window.addEventListener('resize', getHeaderHeight)
    getHeaderHeight() // Measure immediately

    return () => window.removeEventListener('resize', getHeaderHeight)
  }, [])

  return [headerHeight] as const
}
```

Optional chaining (`header?.offsetHeight`) or explicit if checks prevent errors when elements don't exist. Sensible defaults (172) provide fallback values for server render and edge cases.

## Custom Hook File Organization

Place custom hooks in a dedicated `/hooks` directory at the app root or feature level. Export as default to match component export patterns.

```typescript
// app/(frontend)/hooks/useIsBelowBreakpoint.ts
import { useEffect, useState } from 'react'

const useIsBelowBreakpoint = (gridBreakpointUp = '768px'): readonly [boolean] => {
  // Implementation
}

export default useIsBelowBreakpoint

// Usage in components
import useIsBelowBreakpoint from '@/hooks/useIsBelowBreakpoint'

export default function MyComponent() {
  const [isMobile] = useIsBelowBreakpoint('768px')
  // ...
}
```

File names match hook names with camelCase, making imports clear and autocomplete-friendly.

## When to Create Custom Hooks

Extract custom hooks when logic with hooks is reused across multiple components. The analyzed projects have only 4 custom hooks for window/DOM utilities, suggesting low adoption of custom hook patterns despite potential reuse opportunities.

Create custom hooks for:
- Window/document event listeners used in multiple components
- Media query logic for responsive behavior
- DOM measurement and observation
- Data fetching patterns (not currently abstracted)
- Form handling logic (not currently abstracted)

## Gap Analysis

The projects show minimal custom hook usage despite opportunities:
- No custom hooks for data fetching (repeated fetch patterns across components)
- No form handling hooks (repeated form state patterns)
- No animation/transition hooks
- No local storage hooks

This represents a significant opportunity to reduce code duplication through custom hook abstractions.

## Related Patterns

- **useEffect Cleanup**: Custom hooks with event listeners need cleanup
- **Multiple useState**: Custom hooks can encapsulate multiple useState calls
- **Type Annotations**: TypeScript typing for custom hook parameters and returns
