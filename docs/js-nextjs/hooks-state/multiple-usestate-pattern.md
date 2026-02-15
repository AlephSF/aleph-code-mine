---
title: "Multiple useState Over Single State Object"
category: "hooks-state"
subcategory: "state-management"
tags: ["react", "hooks", "useState", "state-management", "best-practices"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Multiple useState Over Single State Object

## Standard

Use multiple `useState` calls for independent pieces of state rather than combining them into a single state object. Each state variable that updates independently should have its own `useState` declaration, even when components manage many pieces of state.

```typescript
// ✅ Correct - Multiple useState for independent state
const [jobData, setJobData] = useState<JobsTeam[]>([])
const [filteredJobData, setFilteredJobData] = useState<JobsTeam[]>([])
const [locations, setLocations] = useState<string[]>([])
const [locationFilter, setLocationFilter] = useState('')

// ❌ Incorrect - Single object combining all state
const [state, setState] = useState({
  jobData: [],
  filteredJobData: [],
  locations: [],
  locationFilter: ''
})
```

**Source Evidence:**
- ClinicalData component: 11 separate useState calls
- PathogenList component: 7 separate useState calls
- JobPostings component: 8 separate useState calls
- **Total: 0 instances of single state objects across all projects (100% adoption of multiple useState)**

## Why Multiple useState

Multiple `useState` calls create simpler, more maintainable components compared to single state objects. Each piece of state has its own setter function, eliminating the need for spread operators or merge logic when updating values. This pattern aligns with React hooks philosophy of granular, focused state management.

Independent state variables make component logic easier to understand. Each useState declaration explicitly shows what state the component manages, and updates to one piece of state don't require knowledge of other state structure. This clarity benefits both initial development and long-term maintenance.

React 18's automatic batching optimizes multiple setState calls within the same event handler into a single re-render, eliminating historical performance concerns about multiple useState declarations. The pattern performs as efficiently as single state objects while providing better developer experience.

## Implementation Pattern

Declare each piece of state with its own useState call at component top level. Group related declarations for readability, maintain separate setters for each value.

```typescript
export default function JobPostings({ headline, content }: JobPostingsProps) {
  // Data state
  const [jobData, setJobData] = useState<JobsTeam[]>([])
  const [filteredJobData, setFilteredJobData] = useState<JobsTeam[]>([])

  // Filter options state
  const [locations, setLocations] = useState<string[]>([])
  const [teams, setTeams] = useState<string[]>([])
  const [workTypes, setWorkTypes] = useState<string[]>([])

  // Active filter state
  const [locationFilter, setLocationFilter] = useState('')
  const [teamFilter, setTeamFilter] = useState('')
  const [workTypeFilter, setWorkTypeFilter] = useState('')

  // UI state
  const [isLoading, setIsLoading] = useState(false)

  // Implementation
}
```

Each setter function updates only its corresponding state. No spread operators or object merging required, reducing cognitive load and potential bugs from forgetting to spread previous state.

```typescript
// ✅ Simple, direct state updates
const handleLocationChange = (location: string) => {
  setLocationFilter(location)
}

const handleTeamChange = (team: string) => {
  setTeamFilter(team)
}

// ❌ Complex updates with single state object
const handleLocationChange = (location: string) => {
  setState(prev => ({ ...prev, locationFilter: location }))
}
```

## When State Updates Are Independent

Use separate useState when state variables update independently - changes to one variable don't require knowledge of other variables' values. This independence indicates they should be separate state declarations.

```typescript
// ✅ Independent state variables
const [mobileNavIsOpen, setMobileNavIsOpen] = useState(false)
const [openSubmenuIndex, setOpenSubmenuIndex] = useState<number | null>(null)
const [hoveredSubmenuIndex, setHoveredSubmenuIndex] = useState<number | null>(null)

// Each updates independently based on user interaction
const handleMobileToggle = () => setMobileNavIsOpen(!mobileNavIsOpen)
const handleSubmenuClick = (index: number) => setOpenSubmenuIndex(index)
const handleSubmenuHover = (index: number) => setHoveredSubmenuIndex(index)
```

Even when components have 7-11 pieces of state (as seen in PathogenList and ClinicalData components), keep them separate if they update independently. The pattern scales well to complex components.

## Grouping Related State Declarations

While maintaining separate useState calls, group related declarations together for code organization. This grouping aids readability without sacrificing the benefits of independent state.

```typescript
export default function ClinicalData({ clinicalEvidence }: Props) {
  // Display mode state
  const [showKeyPubs, setShowKeyPubs] = useState<boolean>(true)
  const [activeType, setActiveType] = useState<TActiveType>(null)

  // Search and filter state
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [results, setResults] = useState<ClinicalEvidenceDocs | undefined>(undefined)
  const [activeStudyFilters, setActiveStudyFilters] = useState<TActiveStudyFilters>([])
  const [openFilterGroups, setOpenFilterGroups] = useState<TOpenFilterGroups>([])

  // Mobile UI state
  const [mobileSomeFiltersHidden, setMobileSomeFiltersHidden] = useState<boolean>(true)
  const [mobileFilterMenuIsOpen, setMobileFilterMenuIsOpen] = useState<boolean>(false)

  // Results context state
  const [resultsContext, setResultsContext] = useState<string>('')

  // Implementation
}
```

Comments separating groups of state help future maintainers understand component organization without requiring single state objects.

## When Not to Use Multiple useState

If state variables always update together and their values are interdependent, consider whether they represent a single logical concept that should be managed together. However, even then, the codebase pattern strongly favors multiple useState over state objects.

```typescript
// Borderline case - coordinates that always update together
// ⚠️ Could be single object, but pattern still uses multiple useState
const [x, setX] = useState(0)
const [y, setY] = useState(0)

const handleMove = (newX: number, newY: number) => {
  setX(newX)  // React 18 batches these into single render
  setY(newY)
}

// Alternative (not used in codebases)
const [position, setPosition] = useState({ x: 0, y: 0 })
```

For true state machines with complex transitions between states, consider useReducer instead of either multiple useState or single state object. However, the analyzed projects show zero useReducer usage, preferring multiple useState even for complex state.

## Updating Multiple Related State Values

When multiple state values must update based on a single event, call their setters in sequence. React 18 automatically batches these updates into a single re-render.

```typescript
const pathname = usePathname()

useEffect(() => {
  // Multiple setters called, but batched into single render
  setOpenSubmenuIndex(null)
  setMobileNavIsOpen(false)
  setHoveredSubmenuIndex(null)
}, [pathname])
```

Batching happens automatically in event handlers, useEffect, and async functions. No special API required - just call setters normally.

## Pattern Benefits

**Simpler code:** No spread operators, no object merging, no partial updates
**Clearer intent:** Each state variable explicitly declared and visible
**Better IntelliSense:** IDE autocomplete works better with discrete variables
**Easier refactoring:** Move state to custom hooks or lift to parent independently
**Reduced bugs:** Can't forget to spread previous state or accidentally overwrite values
**Better performance:** React 18 batches updates automatically, no performance penalty

## Related Patterns

- **useState Type Annotations**: Type each useState appropriately
- **useReducer for Complex State**: When state transitions are complex
- **Custom Hooks**: Extract related useState calls into custom hooks
- **useEffect Dependencies**: Each state variable can be dependency
