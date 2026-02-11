---
title: "Context vs Props Drilling Decision Guide"
category: "hooks-state"
subcategory: "state-management"
tags: ["react", "context", "props-drilling", "useContext", "state-management"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "1%"
last_updated: "2026-02-11"
---

# Context vs Props Drilling Decision Guide

## Standard

Prefer props drilling over React Context for most component communication. Use Context only for truly global values accessed by many components (theme, i18n, authentication). Current projects avoid Context almost entirely (1 instance across 3 projects), demonstrating that props drilling handles most state sharing needs effectively.

```typescript
// ✅ Current pattern - props drilling (recommended for most cases)
export default function Layout({ theme }: { theme: Theme }) {
  return (
    <div>
      <Header theme={theme} />
      <MainContent theme={theme} />
    </div>
  )
}

// ⚠️ Context - only for truly global state
const ThemeContext = createContext<Theme>(defaultTheme)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light')
  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
}
```

**Source Evidence:**
- Context providers: 1 (TranslationContext in policy-node only)
- useContext calls: 2 total (99% avoidance)
- Props drilling: Universal pattern across all components
- **Pattern: 99% props, 1% context**

## Why Context Is Rarely Needed

Projects demonstrate that props drilling handles most state sharing effectively. Component trees aren't deeply nested enough to make prop drilling burdensome, and explicit prop passing makes data flow visible and traceable.

Next.js patterns reduce context needs through server components, layouts, and route-level data fetching. Global state requirements (theme, auth) can often be handled through server-side sessions or URL parameters rather than client-side context.

The single context instance (TranslationContext in policy-node) exists because translation data is needed across many components at different tree levels, making it the rare legitimate use case for context.

## When Props Drilling Is Better

Use props drilling when:
- Data flows through 2-3 component levels
- Parent components use the data (not just passing through)
- Data flow should be explicit and traceable
- Components are not deeply nested

```typescript
// ✅ Props drilling for shallow trees (2-3 levels)
function App() {
  const [user, setUser] = useState<User | null>(null)
  return <Dashboard user={user} onUserUpdate={setUser} />
}

function Dashboard({ user, onUserUpdate }: DashboardProps) {
  return (
    <div>
      <UserProfile user={user} />
      <UserSettings user={user} onUpdate={onUserUpdate} />
    </div>
  )
}

function UserProfile({ user }: { user: User | null }) {
  return <div>{user?.name}</div>
}
```

Benefits: Easy to understand, refactor, and test. No hidden dependencies or implicit data flow.

## When to Use Context

Use Context when data is:
- **Truly global**: Needed by many components across the app
- **Stable**: Changes infrequently (theme, i18n, auth)
- **Deep access**: Components 4+ levels deep need the data
- **Not parent-managed**: Parent components don't use the data themselves

```typescript
// ✅ Legitimate context usage (i18n translations)
// policy-node/src/context/TranslationContext.tsx
interface Translation {
  language: { slug: string }
  alternateLanguage?: { slug: string }
}

interface TranslationContextType {
  availableTranslations: Translation[]
  setAvailableTranslations: (translations: Translation[]) => void
}

const TranslationContext = createContext<TranslationContextType>({
  availableTranslations: [],
  setAvailableTranslations: () => {},
})

export function TranslationProvider({ children }: { children: ReactNode }) {
  const [availableTranslations, setAvailableTranslations] = useState<Translation[]>([])

  const value = useMemo(
    () => ({ availableTranslations, setAvailableTranslations }),
    [availableTranslations]
  )

  return <TranslationContext.Provider value={value}>{children}</TranslationContext.Provider>
}

export function useTranslation() {
  return useContext(TranslationContext)
}
```

This pattern works because translations are:
- Needed globally by navigation, content, and UI components
- Set once at app initialization
- Accessed from deeply nested components
- Not modified by parent components

## Context Performance Considerations

Context updates cause all consuming components to re-render, regardless of which context value they use. For frequently changing state, context can hurt performance.

```typescript
// ❌ Performance issue - frequent updates
const UserContext = createContext({ user: null, notifications: [] })

function App() {
  const [user, setUser] = useState(null)
  const [notifications, setNotifications] = useState([])

  // Every notification update re-renders ALL context consumers
  useEffect(() => {
    const interval = setInterval(() => {
      fetchNotifications().then(setNotifications)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <UserContext.Provider value={{ user, notifications }}>
      <Dashboard /> {/* Re-renders every 5s even if only uses user */}
    </UserContext.Provider>
  )
}

// ✅ Better - split contexts or use props
const UserContext = createContext(null)
const NotificationContext = createContext([])
// Now components only subscribe to what they need
```

Split frequently-changing values into separate contexts to limit re-render scope.

## Context with useMemo for Value Stability

Always wrap context provider values in `useMemo` to prevent unnecessary re-renders from object reference changes.

```typescript
// ✅ Memoized context value (policy-node pattern)
export function TranslationProvider({ children }: { children: ReactNode }) {
  const [availableTranslations, setAvailableTranslations] = useState<Translation[]>([])

  const value = useMemo(
    () => ({ availableTranslations, setAvailableTranslations }),
    [availableTranslations]
  )

  return <TranslationContext.Provider value={value}>{children}</TranslationContext.Provider>
}

// ❌ Unmemoized value - new object every render
export function BadProvider({ children }: { children: ReactNode }) {
  const [translations, setTranslations] = useState<Translation[]>([])

  // New object reference on every render!
  return (
    <TranslationContext.Provider value={{ translations, setTranslations }}>
      {children}
    </TranslationContext.Provider>
  )
}
```

Without `useMemo`, the provider creates a new object on every render, triggering re-renders in all consumers even when values didn't change.

## Custom Hook for Context Consumption

Provide a custom hook that wraps `useContext` for better error messages and type safety.

```typescript
export function useTranslation() {
  const context = useContext(TranslationContext)
  if (context === undefined) {
    throw new Error('useTranslation must be used within TranslationProvider')
  }
  return context
}

// Usage in components
function MyComponent() {
  const { availableTranslations } = useTranslation()
  // ...
}
```

The custom hook ensures consumers are wrapped in the provider and provides helpful error messages when they aren't.

## Next.js Server Components Reduce Context Needs

Next.js App Router's server components eliminate many traditional context use cases by fetching data at the server level and passing as props.

```typescript
// ✅ Server component pattern (no context needed)
// app/layout.tsx
export default async function Layout({ children }: { children: ReactNode }) {
  const translations = await fetchTranslations()
  return (
    <html>
      <body>
        <Header translations={translations} />
        {children}
      </body>
    </html>
  )
}

// ❌ Old pattern with context
'use client'
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <TranslationProvider>
      <Header />
      {children}
    </TranslationProvider>
  )
}
```

Server components fetch data once and pass as props, avoiding the need for client-side global state management.

## When to Refactor Props to Context

Consider context when:
- Props drill through 5+ component levels
- Many components (10+) need the same data
- Components in between don't use the data (pure passthrough)
- Data is stable and changes infrequently

Don't refactor to context just because:
- Props drilling feels "messy" (it's explicit and traceable)
- You have 2-3 levels of passing
- Data changes frequently
- Only a few components need the data

## Decision Tree

**Use Props Drilling When:**
- 1-3 component levels deep
- Parent uses or transforms the data
- Explicit data flow is valuable
- Data changes frequently
- Small number of consumers

**Use Context When:**
- 4+ component levels deep
- Many components need the data
- Parents don't use the data
- Data is stable (theme, i18n, auth)
- Truly application-wide state

**Current Projects:** 99% props drilling, showing it handles most cases effectively.

## Related Patterns

- **Multiple useState**: Props can pass multiple state values
- **useReducer**: Context can wrap reducer for global state
- **Server Components**: Next.js patterns reduce context needs
