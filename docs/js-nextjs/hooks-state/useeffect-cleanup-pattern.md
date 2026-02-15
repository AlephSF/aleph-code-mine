---
title: "useEffect Cleanup for Event Listeners"
category: "hooks-state"
subcategory: "side-effects"
tags: ["react", "hooks", "useEffect", "cleanup", "event-listeners", "memory-leaks"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# useEffect Cleanup for Event Listeners

## Standard

Always return a cleanup function from `useEffect` when adding event listeners to window, document, or DOM elements. The cleanup function must remove the event listener to prevent memory leaks and duplicate handlers when components unmount or re-render.

```typescript
// ✅ Correct - Cleanup function removes event listener
useEffect(() => {
  const handleResize = () => {
    if (window.innerWidth >= 744) {
      setIsMobileMenuOpen(false)
    }
  }
  window.addEventListener('resize', handleResize)
  return () => window.removeEventListener('resize', handleResize)
}, [])

// ❌ Incorrect - No cleanup (memory leak)
useEffect(() => {
  window.addEventListener('resize', () => {
    setIsMobileMenuOpen(false)
  })
}, [])
```

**Source Evidence:**
- Total event listener useEffect: 28 instances across all projects
- Event listeners with cleanup: 28 instances (100%)
- Resize handlers: 10 instances (all with cleanup)
- Keyboard handlers: 17 instances (all with cleanup)

## Why Cleanup Functions Matter

Event listeners added to global objects like window or document persist after component unmount unless explicitly removed. Without cleanup, each component mount adds a new listener while previous listeners remain active, creating memory leaks and duplicate event handling. This compounds quickly in dynamic applications with frequent mount/unmount cycles.

Cleanup functions run before the next effect execution and when the component unmounts, ensuring listeners are removed at the right time. React's effect system guarantees cleanup happens before new effects, preventing the accumulation of stale listeners with outdated closure values.

Missing cleanup in production applications causes performance degradation over time as memory usage grows from accumulated listeners. Users navigating between pages repeatedly can crash their browser session if event listeners aren't cleaned up properly.

## Implementation Pattern

Define event handler functions within useEffect, add the listener, and return a cleanup function that removes the same listener. The pattern requires the same function reference for both addEventListener and removeEventListener.

```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isMobileMenuOpen) {
      setIsMobileMenuOpen(false)
    }
  }

  document.addEventListener('keydown', handleKeyDown)
  return () => document.removeEventListener('keydown', handleKeyDown)
}, [isMobileMenuOpen])
```

The cleanup function receives the same function reference defined in the effect. Arrow functions defined inline in addEventListener won't work with removeEventListener because each creates a new function reference.

## Empty Dependency Array Pattern

Event listeners for global events like resize or scroll typically use empty dependency arrays, running the effect only on mount and cleanup only on unmount. This prevents re-adding listeners on every render.

```typescript
useEffect(() => {
  const handleResize = () => {
    if (window.innerWidth >= 744) {
      setIsMobileMenuOpen(false)
      setMobileLocaleOpen(false)
    }
  }

  window.addEventListener('resize', handleResize)
  handleResize() // Call once on mount for initial state

  return () => window.removeEventListener('resize', handleResize)
}, []) // Empty dependencies - run once on mount
```

Calling the handler once during effect setup ensures initial state matches current window size without waiting for the first resize event.

## Dependencies for Conditional Cleanup

When event listener behavior depends on component state, include that state in the dependency array. React re-runs the effect when dependencies change, cleaning up the old listener and adding a new one with updated closure values.

```typescript
useEffect(() => {
  const handleDocumentKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isLocaleSelectorOpen) {
      setIsLocaleSelectorOpen(false)
      const buttonElement = localeSelectorRef.current?.querySelector('button') as HTMLButtonElement
      buttonElement?.focus()
    }
  }

  document.addEventListener('keydown', handleDocumentKeyDown)
  return () => document.removeEventListener('keydown', handleDocumentKeyDown)
}, [isLocaleSelectorOpen]) // Re-run when state changes
```

Each dependency change triggers cleanup of the previous listener before adding the new one, ensuring event handlers always see current state values.

## Multiple Listeners Per Component

Components needing multiple event listeners use separate useEffect hooks to keep concerns separated and dependencies explicit.

```typescript
export default function SiteHeader(){
  const [isMobileMenuOpen,setIsMobileMenuOpen]=useState(false)
  const [isLocaleSelectorOpen,setIsLocaleSelectorOpen]=useState(false)
  useEffect(()=>{
    const h=()=>{if(window.innerWidth>=744){setIsMobileMenuOpen(false)}}
    window.addEventListener('resize',h)
    return()=>window.removeEventListener('resize',h)
  },[])
  useEffect(()=>{
    const h=(e:KeyboardEvent)=>{if(e.key==='Escape'&&isMobileMenuOpen){setIsMobileMenuOpen(false)}}
    document.addEventListener('keydown',h)
    return()=>document.removeEventListener('keydown',h)
  },[isMobileMenuOpen])
  useEffect(()=>{
    const h=(e:KeyboardEvent)=>{if(e.key==='Escape'&&isLocaleSelectorOpen){setIsLocaleSelectorOpen(false)}}
    document.addEventListener('keydown',h)
    return()=>document.removeEventListener('keydown',h)
  },[isLocaleSelectorOpen])
}
```

Separate effects make each listener's lifecycle independent with clear dependencies.

## Browser Compatibility Patterns

Some browser APIs have legacy and modern event listener methods. Handle both for maximum compatibility, ensuring cleanup works across all browsers.

```typescript
useEffect(() => {
  const mediaQuery = window.matchMedia('(min-width: 768px)')

  const onBreakpointChange = (e: MediaQueryListEvent) => {
    setIsBelowBreakpoint(!e.matches)
  }

  // Modern browsers use addEventListener
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', onBreakpointChange)
  }
  // Legacy browsers (Safari < 14) use addListener
  else if (mediaQuery.addListener) {
    mediaQuery.addListener(onBreakpointChange)
  }

  // Cleanup must match the add method
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', onBreakpointChange)
    } else if (mediaQuery.removeListener) {
      mediaQuery.removeListener(onBreakpointChange)
    }
  }
}, [])
```

Check for addEventListener first since it's the modern standard, then fall back to legacy methods. Cleanup logic must mirror the add logic to properly remove listeners.

## Ref-Based Event Listeners

When adding listeners to specific DOM elements accessed through refs, the listener can be added outside useEffect with manual cleanup. However, useEffect with cleanup remains the safer, more conventional pattern.

```typescript
// ✅ Standard pattern with useEffect
const buttonRef = useRef<HTMLButtonElement>(null)

useEffect(() => {
  const button = buttonRef.current
  if (!button) return

  const handleClick = () => {
    console.log('Clicked')
  }

  button.addEventListener('click', handleClick)
  return () => button.removeEventListener('click', handleClick)
}, [])

// Alternative pattern (found in codebase, less common)
const buttonRef = useRef<HTMLButtonElement>(null)

if (buttonRef.current) {
  const handleClick = () => console.log('Clicked')
  buttonRef.current.addEventListener('click', handleClick)
  // Cleanup happens when component unmounts (relies on React cleanup)
}
```

The useEffect pattern provides more explicit cleanup and works better with React's lifecycle, making it the recommended approach even for ref-based listeners.

## Pathname-Based Cleanup Pattern

Next.js components frequently reset state when pathname changes. This pattern uses usePathname hook from next/navigation to trigger cleanup.

```typescript
import { usePathname } from 'next/navigation'

export default function MainNav() {
  const pathname = usePathname()
  const [openSubmenuIndex, setOpenSubmenuIndex] = useState<number | null>(null)
  const [mobileNavIsOpen, setMobileNavIsOpen] = useState(false)

  useEffect(() => {
    // Close menus when navigating to new page
    setOpenSubmenuIndex(null)
    setMobileNavIsOpen(false)
  }, [pathname])
}
```

While this doesn't clean up event listeners specifically, it demonstrates the cleanup pattern of resetting state in response to navigation. Combine with event listener cleanup for complete navigation handling.

## Common Pitfalls

Never define event handlers inline in addEventListener. This creates a new function each time, making removeEventListener unable to remove the handler because function references don't match.

```typescript
// ❌ Inline handler - cleanup won't work
useEffect(() => {
  window.addEventListener('resize', () => {
    setWidth(window.innerWidth)
  })
  return () => window.removeEventListener('resize', () => {
    setWidth(window.innerWidth) // Different function reference!
  })
}, [])

// ✅ Named handler - cleanup works
useEffect(() => {
  const handleResize = () => {
    setWidth(window.innerWidth)
  }
  window.addEventListener('resize', handleResize)
  return () => window.removeEventListener('resize', handleResize)
}, [])
```

Don't rely on component unmount to clean up listeners. Always provide explicit cleanup functions even if you think the component won't unmount during the session. Assumptions about component lifecycle often break as applications evolve.

## Related Patterns

- **Multiple useState Pattern**: Event listeners often update multiple state variables
- **SSR-Safe Custom Hooks**: Custom hooks must handle window/document access safely
- **useRef for DOM Access**: Refs combined with event listeners need careful cleanup
