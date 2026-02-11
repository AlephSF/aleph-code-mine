---
title: "When to Use useReducer Over Multiple useState"
category: "hooks-state"
subcategory: "state-management"
tags: ["react", "hooks", "useReducer", "useState", "state-machines", "complex-state"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

# When to Use useReducer Over Multiple useState

## Standard

Use `useReducer` when component state involves complex transitions, interdependent updates, or state machine logic. Current projects use multiple `useState` exclusively (0 useReducer instances), but complex components with 7-11 state variables would benefit from reducer patterns for predictable state transitions.

```typescript
// Current pattern - multiple useState for complex state
const [searchTerm, setSearchTerm] = useState<string>('')
const [results, setResults] = useState<Item[]>([])
const [activeFilters, setActiveFilters] = useState<Filter[]>([])
const [isLoading, setIsLoading] = useState<boolean>(false)
const [error, setError] = useState<string | null>(null)

// Recommended for complex state - useReducer
type State = {
  searchTerm: string
  results: Item[]
  activeFilters: Filter[]
  isLoading: boolean
  error: string | null
}

type Action =
  | { type: 'SEARCH_START'; payload: string }
  | { type: 'SEARCH_SUCCESS'; payload: Item[] }
  | { type: 'SEARCH_ERROR'; payload: string }
  | { type: 'ADD_FILTER'; payload: Filter }

const [state, dispatch] = useReducer(reducer, initialState)
```

**Source Evidence:**
- useReducer usage: 0 instances across all projects (100% avoidance)
- Complex components with 7-11 useState calls: 15+ components
- **Gap: No reducer patterns despite complex state management needs**

## Why useReducer Wasn't Adopted

Projects avoid useReducer in favor of multiple useState calls, even in complex components. This choice stems from team preference for simpler, more explicit patterns where each state piece has its own setter. The pattern works but creates components with many state variables and update logic scattered across handlers.

Components like ClinicalData (11 useState calls) and PathogenList (7 useState calls) manage complex filtering and search state without reducers. Updates happen through individual setters, making state transitions less predictable than reducer actions.

The absence of useReducer suggests either (1) team unfamiliarity with the pattern, (2) conscious decision that useState is sufficient, or (3) no perceived benefit for current complexity levels. As components grow more complex, reducer patterns become increasingly valuable.

## When useReducer Is Better Than Multiple useState

Use `useReducer` when multiple state variables update together in coordinated ways, forming logical state transitions. Reducers excel at:

**Complex state transitions:**
```typescript
// Multiple related updates that should happen atomically
function handleSearchSubmit(term: string) {
  setSearchTerm(term)
  setIsLoading(true)
  setError(null)
  setResults([])
  setActivePage(1)
}

// Better with reducer - atomic state transition
dispatch({ type: 'SEARCH_START', payload: term })
```

**State machines with defined transitions:**
```typescript
// Form wizard with step transitions
type WizardState = {
  step: 1 | 2 | 3 | 4
  formData: FormData
  errors: ValidationErrors
  canProceed: boolean
}

// Reducer ensures valid state transitions
function reducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'NEXT_STEP':
      // Only advance if current step is valid
      return state.canProceed
        ? { ...state, step: (state.step + 1) as WizardState['step'] }
        : state
  }
}
```

**Interdependent state updates:**
```typescript
// State where one update affects multiple values
type FilterState = {
  category: string | null
  subcategory: string | null
  items: Item[]
  filteredItems: Item[]
}

// Changing category resets subcategory and updates both item lists
function reducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_CATEGORY':
      return {
        ...state,
        category: action.payload,
        subcategory: null, // Reset dependent state
        filteredItems: filterByCategory(state.items, action.payload)
      }
  }
}
```

## useReducer vs Multiple useState Decision Tree

**Use multiple useState when:**
- State pieces update independently
- Updates are simple assignments (no complex logic)
- State doesn't form a state machine
- Component has fewer than 5-7 state variables

**Use useReducer when:**
- Multiple state variables update together atomically
- State transitions follow predictable patterns (state machine)
- Complex update logic that needs testing independently
- Component has 8+ interdependent state variables

**Current projects:** All components use multiple useState regardless of complexity. This works but reduces predictability for complex state.

## Real-World Example: Refactoring ClinicalData

The ClinicalData component manages 11 state variables for search, filtering, and UI state. This is a prime candidate for useReducer:

```typescript
// Current pattern (kariusdx-next)
const [showKeyPubs, setShowKeyPubs] = useState<boolean>(true)
const [searchTerm, setSearchTerm] = useState<string>('')
const [results, setResults] = useState<ClinicalEvidenceDocs | undefined>(undefined)
const [activeStudyFilters, setActiveStudyFilters] = useState<TActiveStudyFilters>([])
const [openFilterGroups, setOpenFilterGroups] = useState<TOpenFilterGroups>([])
const [activeType, setActiveType] = useState<TActiveType>(null)
const [mobileSomeFiltersHidden, setMobileSomeFiltersHidden] = useState<boolean>(true)
const [mobileFilterMenuIsOpen, setMobileFilterMenuIsOpen] = useState<boolean>(false)
const [resultsContext, setResultsContext] = useState<string>('')

// Recommended pattern with useReducer
type State = {
  view: 'keyPubs' | 'allPubs'
  search: {
    term: string
    results: ClinicalEvidenceDocs | undefined
    context: string
  }
  filters: {
    active: TActiveStudyFilters
    openGroups: TOpenFilterGroups
    activeType: TActiveType
  }
  mobile: {
    someFiltersHidden: boolean
    filterMenuOpen: boolean
  }
}

type Action =
  | { type: 'TOGGLE_VIEW' }
  | { type: 'SEARCH'; payload: string }
  | { type: 'ADD_FILTER'; payload: Filter }
  | { type: 'TOGGLE_MOBILE_MENU' }

const [state, dispatch] = useReducer(clinicalDataReducer, initialState)
```

Benefits: Centralized state logic, predictable transitions, easier testing, atomic updates.

## TypeScript Patterns for useReducer

Define state and action types explicitly. Use discriminated unions for actions to enable exhaustive checking in reducers.

```typescript
// State type
type State = {
  status: 'idle' | 'loading' | 'success' | 'error'
  data: Item[] | null
  error: string | null
}

// Discriminated union for actions
type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: Item[] }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'RESET' }

// Reducer with exhaustive checking
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, status: 'loading', error: null }
    case 'FETCH_SUCCESS':
      return { status: 'success', data: action.payload, error: null }
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.payload }
    case 'RESET':
      return initialState
    default:
      // TypeScript ensures all cases handled
      const _exhaustive: never = action
      return state
  }
}
```

Discriminated unions ensure TypeScript catches missing action types and provides autocomplete for action payloads.

## Immer for Immutable Updates

Complex reducers benefit from Immer library for simpler immutable updates without spread operators.

```typescript
import { useImmerReducer } from 'use-immer'

const [state, dispatch] = useImmerReducer((draft: State, action: Action) => {
  switch (action.type) {
    case 'ADD_FILTER':
      // Mutate draft directly, Immer handles immutability
      draft.filters.active.push(action.payload)
      draft.results = filterResults(draft.items, draft.filters.active)
      break
    case 'REMOVE_FILTER':
      const index = draft.filters.active.findIndex(f => f.id === action.payload)
      draft.filters.active.splice(index, 1)
      draft.results = filterResults(draft.items, draft.filters.active)
      break
  }
}, initialState)
```

Immer reduces boilerplate for nested state updates while maintaining immutability guarantees.

## Testing Reducers Independently

Reducers are pure functions, making them easy to test in isolation without component rendering.

```typescript
import { describe, it, expect } from 'vitest'

describe('clinicalDataReducer', () => {
  it('transitions to loading state on FETCH_START', () => {
    const state = { status: 'idle', data: null, error: null }
    const action = { type: 'FETCH_START' }

    const newState = reducer(state, action)

    expect(newState.status).toBe('loading')
    expect(newState.error).toBe(null)
  })

  it('stores data and clears error on FETCH_SUCCESS', () => {
    const state = { status: 'loading', data: null, error: 'prev error' }
    const action = { type: 'FETCH_SUCCESS', payload: [item1, item2] }

    const newState = reducer(state, action)

    expect(newState.status).toBe('success')
    expect(newState.data).toEqual([item1, item2])
    expect(newState.error).toBe(null)
  })
})
```

Testing reducers independently validates state transition logic without UI complexity.

## Related Patterns

- **Multiple useState Pattern**: Current approach, works for simple independent state
- **Context for Global State**: useReducer pairs well with context for app-wide state
- **TypeScript Union Types**: Action types use discriminated unions
