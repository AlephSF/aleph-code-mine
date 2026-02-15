---
title: "useEffect Dependency Array Patterns"
category: "hooks-state"
subcategory: "side-effects"
tags: ["react", "hooks", "useEffect", "dependencies", "best-practices"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# useEffect Dependency Array Patterns

## Standard

Always include all values from component scope that the effect uses in the dependency array. Use empty arrays `[]` for effects that should run once on mount. Separate effects by concern rather than combining multiple side effects in one useEffect with complex dependencies.

```typescript
// ✅ Correct - all dependencies included
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isModalOpen) {
      setIsModalOpen(false)
    }
  }
  document.addEventListener('keydown', handleKeyDown)
  return () => document.removeEventListener('keydown', handleKeyDown)
}, [isModalOpen]) // isModalOpen is used, so it's in dependencies

// ✅ Empty dependencies for mount-only effect
useEffect(() => {
  fetchInitialData().then(setData)
}, [])

// ❌ Missing dependencies
useEffect(() => {
  if (isModalOpen) { // Used but not in deps!
    document.body.style.overflow = 'hidden'
  }
}, [])
```

**Source Evidence:**
- useEffect instances: 92 across all projects
- Pathname-based effects: 14 instances
- Event listener effects: 28 instances
- Empty dependency arrays: Common for mount-only effects
- **Pattern: Explicit dependencies, separated concerns**

## Empty Dependency Array Pattern

Use empty dependency arrays `[]` for effects that should run only once when the component mounts. This pattern appears frequently for initial data fetching, one-time event listener setup, and mount-time initialization.

```typescript
// ✅ Run once on mount
useEffect(() => {
  const handleResize = () => {
    setWidth(window.innerWidth)
  }
  window.addEventListener('resize', handleResize)
  handleResize() // Call immediately

  return () => window.removeEventListener('resize', handleResize)
}, []) // Empty - never re-run

// ✅ Fetch data on mount
useEffect(() => {
  fetchInitialData().then(setData)
}, [])
```

Empty arrays tell React the effect has no external dependencies - it doesn't use any props, state, or derived values that could change. The effect runs once and cleanup (if provided) runs only on unmount.

## Pathname-Based Dependencies

Next.js components frequently use `usePathname()` to reset state when navigation occurs. This pattern appears in 14 instances across the projects.

```typescript
import { usePathname } from 'next/navigation'

export default function MainNav() {
  const pathname = usePathname()
  const [openSubmenuIndex, setOpenSubmenuIndex] = useState<number | null>(null)
  const [mobileNavIsOpen, setMobileNavIsOpen] = useState(false)

  // Reset UI state on navigation
  useEffect(() => {
    setOpenSubmenuIndex(null)
    setMobileNavIsOpen(false)
  }, [pathname]) // Re-run when pathname changes
}
```

This pattern ensures menus close and UI resets when users navigate to new pages, preventing stale UI state across route changes.

## Separating Effects by Concern

Components with multiple side effects use separate useEffect hooks rather than combining logic. Makes dependency management clearer.

```typescript
// policy-node SiteHeader
export default function SiteHeader(){
  const pathname=usePathname()
  const [isMobileMenuOpen,setIsMobileMenuOpen]=useState(false)
  const [isLocaleSelectorOpen,setIsLocaleSelectorOpen]=useState(false)
  useEffect(()=>{handleNavigation()},[pathname])
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
  useEffect(()=>{
    const h=()=>{if(window.innerWidth>=744){setIsMobileMenuOpen(false)}}
    window.addEventListener('resize',h)
    return()=>window.removeEventListener('resize',h)
  },[])
}
```

Each effect has clear, independent dependencies. Combining would create dependency array nightmare.

## Function Dependencies

When effects use functions from component scope, those functions must be in dependencies. This often requires useCallback to stabilize function references.

```typescript
// ⚠️ Function dependency pattern
function Component({ userId }: Props) {
  const fetchUser = async () => {
    const data = await api.getUser(userId)
    setUser(data)
  }

  useEffect(() => {
    fetchUser() // Uses fetchUser, so it should be in deps
  }, [fetchUser]) // But fetchUser is new every render!

  // ✅ Better - useCallback to stabilize reference
  const fetchUser = useCallback(async () => {
    const data = await api.getUser(userId)
    setUser(data)
  }, [userId])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  // ✅ Best - inline the function
  useEffect(() => {
    async function fetchUser() {
      const data = await api.getUser(userId)
      setUser(data)
    }
    fetchUser()
  }, [userId]) // Only userId in deps
}
```

Inlining functions in useEffect avoids the useCallback requirement and makes dependencies clearer.

## Object and Array Dependencies

Objects and arrays in dependencies create new references on every render, causing effects to re-run unnecessarily. Extract primitive values or use useMemo for stability.

```typescript
// ❌ Object dependency - new reference every render
useEffect(() => {
  fetchData(filters) // filters: { category, location }
}, [filters]) // Runs every render even if values unchanged

// ✅ Extract primitive dependencies
useEffect(() => {
  fetchData({ category, location })
}, [category, location]) // Only re-run when actual values change

// ⚠️ Array dependency - same issue
useEffect(() => {
  processItems(selectedIds)
}, [selectedIds]) // If selectedIds is array, new reference each render

// ✅ Stringify for comparison (if appropriate)
useEffect(() => {
  processItems(selectedIds)
}, [JSON.stringify(selectedIds)])
// Or better: manage IDs as comma-separated string state
```

Primitive dependencies (strings, numbers, booleans) compare by value, while objects/arrays compare by reference.

## ESLint Exhaustive Deps Rule

Enable `react-hooks/exhaustive-deps` ESLint rule to catch missing dependencies. The rule analyzes effect code and warns when values from component scope aren't in the dependency array.

```typescript
// ESLint will warn
useEffect(() => {
  if (isOpen) { // isOpen used but not in deps
    doSomething()
  }
}, []) // Warning: React Hook useEffect has a missing dependency: 'isOpen'

// Fix by adding dependency
useEffect(() => {
  if (isOpen) {
    doSomething()
  }
}, [isOpen])
```

Projects use `// eslint-disable-next-line react-hooks/exhaustive-deps` sparingly when intentionally omitting dependencies, documenting the decision explicitly.

## When to Disable the Deps Rule

Disable exhaustive-deps warnings only when:
- Effect intentionally runs only on mount (empty deps)
- Setter functions from useState (stable references)
- Refs from useRef (stable references)
- Values from context that don't trigger re-renders

```typescript
// ✅ Disable for mount-only effect
useEffect(() => {
  // Run once on mount, even though uses gridBreakpointUpMatch
  setIsBelowBreakpoint(gridBreakpointUpMatch && !gridBreakpointUpMatch.matches)
  setIsComponentMounted(true)
}, []) // eslint-disable-line react-hooks/exhaustive-deps

// ✅ Setters are stable, don't need in deps
const [count, setCount] = useState(0)

useEffect(() => {
  const interval = setInterval(() => {
    setCount(c => c + 1) // setCount is stable, not in deps
  }, 1000)
  return () => clearInterval(interval)
}, [])
```

Document why dependencies are omitted with comments explaining the intentional choice.

## Ref Dependencies

Refs from useRef don't need to be in dependency arrays because ref objects maintain stable identity across renders. However, ref.current values can change.

```typescript
const buttonRef = useRef<HTMLButtonElement>(null)

// ✅ Ref not in dependencies (stable)
useEffect(() => {
  const button = buttonRef.current
  if (button) {
    button.focus()
  }
}, []) // buttonRef omitted, stable reference

// ⚠️ Accessing ref.current in dependency check
useEffect(() => {
  if (buttonRef.current) {
    // ...
  }
}, [buttonRef.current]) // Don't do this - current can change without triggering re-render
```

Refs are escape hatches from React's reactivity system. Changes to ref.current don't cause re-renders and shouldn't be dependencies.

## Related Patterns

- **useEffect Cleanup**: Every effect with listeners needs cleanup
- **Multiple useState**: Effects often depend on specific state variables
- **useCallback Guidelines**: Function dependencies may need useCallback
