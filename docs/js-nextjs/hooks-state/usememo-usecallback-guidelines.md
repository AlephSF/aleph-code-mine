---
title: "useMemo and useCallback Usage Guidelines"
category: "hooks-state"
subcategory: "performance"
tags: ["react", "hooks", "useMemo", "useCallback", "performance", "optimization"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# useMemo and useCallback Usage Guidelines

## Standard

Use `useMemo` and `useCallback` sparingly, only for expensive computations or when callback stability is required for child component optimization. Projects show minimal usage (20 useMemo, 13 useCallback across all code), with helix avoiding them entirely. Default to not using these hooks unless profiling shows a performance issue.

```typescript
// ✅ Appropriate useMemo - expensive computation
const sortedAndFilteredItems = useMemo(() => {
  return items
    .filter(item => item.category === activeCategory)
    .sort((a, b) => a.name.localeCompare(b.name))
}, [items, activeCategory])

// ✅ Appropriate useCallback - stable reference for memoized child
const handleItemClick = useCallback((id: string) => {
  setSelectedId(id)
  trackEvent('item_click', { id })
}, [])

// ❌ Unnecessary useMemo - simple value
const fullName = useMemo(() => `${firstName} ${lastName}`, [firstName, lastName])

// ❌ Unnecessary useCallback - no memoized children
const handleClick = useCallback(() => setCount(c => c + 1), [])
```

**Source Evidence:**
- useMemo usage: 20 instances (helix: 0, kariusdx: 10, policy-node: 10)
- useCallback usage: 13 instances (helix: 2, kariusdx: 3, policy-node: 8)
- **Pattern: Minimal usage, avoid premature optimization**

## Why Minimal Usage Is Correct

Helix project demonstrates that applications perform well without useMemo or useCallback. The overhead of memoization (memory for cached values, comparison logic) often exceeds the cost of recomputing simple values or recreating callback functions.

React is already highly optimized for component re-renders. Most components render quickly enough that memoization provides negligible benefit. Premature optimization with these hooks adds complexity, reduces code readability, and can actually harm performance if dependency arrays are incorrect.

The pattern of minimal usage aligns with React team guidance: profile first, optimize only proven bottlenecks. Kariusdx and policy-node use these hooks sparingly for specific cases, not as default practice.

## When to Use useMemo

Use `useMemo` only when:
- Computation is provably expensive (loops over large arrays, complex calculations)
- Computation result is used in dependency arrays of other hooks
- Profiling shows the computation causes performance issues

```typescript
// ✅ Expensive computation worth memoizing
const expensiveValue = useMemo(() => {
  return largeDataset
    .map(item => complexTransform(item))
    .filter(item => item.score > threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, 100)
}, [largeDataset, threshold])

// ✅ Value used in dependency array
const memoizedValue = useMemo(() => computeValue(data), [data])

useEffect(() => {
  // memoizedValue in dependencies - useMemo prevents unnecessary effects
  doSomething(memoizedValue)
}, [memoizedValue])

// ❌ Simple string concatenation - not expensive
const greeting = useMemo(() => `Hello, ${name}!`, [name])

// ❌ Object creation - usually not expensive enough to memo
const config = useMemo(() => ({ theme, fontSize }), [theme, fontSize])
```

Don't assume computation is expensive - profile to verify. Simple operations like array filters on small datasets or object creation are cheaper than memoization overhead.

## When to Use useCallback

Use `useCallback` when:
- Passing callbacks to memoized child components wrapped in React.memo
- Callback is a dependency of useEffect or useMemo
- Creating event handlers in loops (to maintain stable references)

```typescript
// ✅ Callback for memoized child component
const MemoizedChild = React.memo(ChildComponent)

function Parent() {
  const handleClick = useCallback((id: string) => {
    // Handler logic
  }, [])

  return <MemoizedChild onClick={handleClick} />
}

// ✅ Callback in useEffect dependencies
const fetchData = useCallback(async () => {
  const data = await api.fetch(params)
  setData(data)
}, [params])

useEffect(() => {
  fetchData()
}, [fetchData])

// ❌ No memoized children - useCallback unnecessary
function Parent() {
  const handleClick = useCallback(() => setCount(c => c + 1), [])
  return <button onClick={handleClick}>Click</button>
}
```

Without React.memo on child components, new callback references don't cause performance issues. Child components re-render anyway when parent re-renders.

## Context Provider Pattern

Policy-node's only significant useMemo usage is in context providers, which is appropriate - prevents all context consumers from re-rendering when provider re-renders.

```typescript
// ✅ useMemo for context value (policy-node pattern)
export function TranslationProvider({ children }: { children: ReactNode }) {
  const [availableTranslations, setAvailableTranslations] = useState<Translation[]>([])

  const value = useMemo(
    () => ({ availableTranslations, setAvailableTranslations }),
    [availableTranslations]
  )

  return <TranslationContext.Provider value={value}>{children}</TranslationContext.Provider>
}
```

Without useMemo, the provider creates a new object reference on every render, causing all consumers to re-render even when values haven't changed. This is one of the few legitimate useMemo use cases.

## Helix's Zero useMemo Approach

Helix project has zero useMemo usage, showing that most applications don't need memoization for good performance. Their components render efficiently without any memoization hooks.

```typescript
// Helix pattern - no useMemo needed
function JobPostings({ jobs }: JobPostingsProps) {
  const [locationFilter, setLocationFilter] = useState('')
  const [teamFilter, setTeamFilter] = useState('')

  // Recalculated on every render - still fast
  const filteredJobs = jobs
    .filter(job => !locationFilter || job.location === locationFilter)
    .filter(job => !teamFilter || job.team === teamFilter)

  return <JobList jobs={filteredJobs} />
}
```

For typical dataset sizes (hundreds of items), filter/map operations are fast enough to run on every render without performance impact.

## When Memoization Hurts Performance

Incorrect or overzealous memoization can reduce performance by:
- **Memory overhead**: Storing cached values consumes memory
- **Comparison cost**: Checking dependencies on every render has overhead
- **Wrong dependencies**: Missing dependencies cause stale closures and bugs

```typescript
// ❌ Memoization costs more than it saves
const simpleValue = useMemo(() => a + b, [a, b])
// Cost: Create array, compare arrays, store result
// Benefit: Saved one addition operation

// ✅ Just compute it
const simpleValue = a + b
// Cost: One addition
// Benefit: Simple, readable, no memory overhead
```

React's diffing algorithm is already optimized. Adding memoization on top can create double-overhead without benefits.

## Profiling Before Optimizing

Use React DevTools Profiler to identify slow components before adding memoization. Look for:
- Components that render frequently (many commits)
- Components with long render times (milliseconds, not microseconds)
- Components that cause cascade re-renders

```typescript
// Steps to profile:
// 1. Open React DevTools Profiler
// 2. Record interaction
// 3. Identify slow components (yellow/red in flamegraph)
// 4. Add memoization ONLY to proven bottlenecks
// 5. Profile again to verify improvement
```

Most components show render times under 1ms, where memoization overhead exceeds computation cost.

## Dependency Array Guidelines

When using useMemo or useCallback, ensure dependency arrays are complete and correct. Missing dependencies cause stale closures and bugs.

```typescript
// ❌ Missing dependency - stale closure
const handleSubmit = useCallback(() => {
  api.submit({ name, email }) // name and email not in deps!
}, [])

// ✅ Complete dependencies
const handleSubmit = useCallback(() => {
  api.submit({ name, email })
}, [name, email])

// ✅ Or omit useCallback entirely if not needed
const handleSubmit = () => {
  api.submit({ name, email })
}
```

ESLint's `react-hooks/exhaustive-deps` rule catches missing dependencies, but overly complex dependency management is a code smell suggesting memoization isn't appropriate.

## Alternatives to Memoization

Consider these alternatives before reaching for useMemo/useCallback:

**Move expensive computations outside components:**
```typescript
// ❌ Memoize inside component
function Component({ data }) {
  const processed = useMemo(() => expensiveProcess(data), [data])
  // ...
}

// ✅ Process before passing as prop
function Parent() {
  const processed = expensiveProcess(data)
  return <Component data={processed} />
}
```

**Use server components for data processing:**
```typescript
// ✅ Server component does expensive work once
export default async function DataDisplay() {
  const processed = await fetchAndProcess() // Runs on server
  return <ClientComponent data={processed} />
}
```

**Restructure component tree to limit re-renders:**
```typescript
// ❌ Parent re-renders cause expensive child re-renders
function Parent() {
  const [count, setCount] = useState(0)
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>{count}</button>
      <ExpensiveComponent data={data} /> {/* Re-renders on count change */}
    </div>
  )
}

// ✅ Isolate changing state
function Parent() {
  return (
    <div>
      <Counter /> {/* Only this re-renders */}
      <ExpensiveComponent data={data} />
    </div>
  )
}
```

## Related Patterns

- **Multiple useState**: Simpler than useMemo for derived state
- **useEffect Dependencies**: Similar dependency array concerns
- **React.memo**: useCallback is only useful with React.memo children
