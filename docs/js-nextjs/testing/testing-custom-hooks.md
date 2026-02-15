---
title: "Testing Custom React Hooks in Next.js"
category: "testing"
subcategory: "hooks-testing"
tags: ["custom-hooks", "testing-library", "react-hooks", "ssr-safe", "use-effect"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Testing Overview

Custom hooks encapsulate reusable stateful logic and side effects. Testing hooks verifies state updates, effect cleanup, dependency handling, SSR-safe initialization. Testing Library's `renderHook` utility renders hooks in isolation without wrapper components. SSR-safe hooks (100% pattern in analyzed codebases) require tests validating window/document checks and mount tracking.

## Why Test Hooks Separately

Custom hooks contain business logic tested independently of UI components. Testing hooks in isolation produces faster, more focused tests than testing through components. Helix-dot-com-next and policy-node have 4 SSR-safe custom hooks with zero tests. Hook bugs affect all components importing the hook. Source confidence: 0% (no custom hook tests exist in analyzed codebases).

## renderHook Utility Basics

Testing Library's `renderHook` renders hooks in test components and provides utilities for triggering re-renders and accessing hook return values. Install with: `npm install -D @testing-library/react`. The `renderHook` API works identically for sync and async hooks.

## Basic Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('initializes with default value 0', () => {
    const {result} = renderHook(() => useCounter())
    expect(result.current.count).toBe(0)
  })

  it('initializes with custom initial value', () => {
    const {result} = renderHook(() => useCounter(10))
    expect(result.current.count).toBe(10)
  })

  it('increments count when increment is called', () => {
    const {result} = renderHook(() => useCounter())
    act(() => {result.current.increment()})
    expect(result.current.count).toBe(1)
  })

  it('decrements count when decrement is called', () => {
    const {result} = renderHook(() => useCounter(5))
    act(() => {result.current.decrement()})
    expect(result.current.count).toBe(4)
  })
})
```

`renderHook` accepts callback returning the hook. Access hook return value via `result.current`. Wrap state updates in `act()` to ensure React processes updates before assertions.

## Testing SSR-Safe Hooks

SSR-safe hooks check for window/document existence before accessing browser APIs. Tests verify hooks work in SSR and client environments.

```typescript
import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useWindowSize } from './useWindowSize'

describe('useWindowSize', () => {
  it('returns default during SSR', () => {
    const o = global.window
    delete (global as any).window
    const {result:r} = renderHook(() => useWindowSize())
    expect(r.current.width).toBe(0)
    global.window = o
  })

  it('returns window size', () => {
    Object.defineProperty(window,'innerWidth',{value:1024,writable:true})
    const {result:r} = renderHook(() => useWindowSize())
    expect(r.current.width).toBe(1024)
  })

  it('updates on resize', async () => {
    Object.defineProperty(window,'innerWidth',{value:1024,writable:true})
    const {result:r} = renderHook(() => useWindowSize())
    act(() => {Object.defineProperty(window,'innerWidth',{value:1280,writable:true});window.dispatchEvent(new Event('resize'))})
    await waitFor(() => expect(r.current.width).toBe(1280))
  })

  it('cleans up listener', () => {
    const s = vi.spyOn(window,'removeEventListener')
    const {unmount:u} = renderHook(() => useWindowSize())
    u()
    expect(s).toHaveBeenCalledWith('resize',expect.any(Function))
  })
})
```

Test SSR safety by deleting global.window. Mock window properties.

## Testing useLocalStorage Hook

Hooks performing async operations require `waitFor` for assertions.

```typescript
import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { useLocalStorage } from './useLocalStorage'

describe('useLocalStorage', () => {
  beforeEach(() => localStorage.clear())

  it('initializes with default', () => {
    const {result:r} = renderHook(() => useLocalStorage('k','def'))
    expect(r.current[0]).toBe('def')
  })

  it('initializes with stored', () => {
    localStorage.setItem('k',JSON.stringify('stored'))
    const {result:r} = renderHook(() => useLocalStorage('k','def'))
    expect(r.current[0]).toBe('stored')
  })

  it('updates localStorage', async () => {
    const {result:r} = renderHook(() => useLocalStorage('k','init'))
    act(() => r.current[1]('upd'))
    await waitFor(() => {
      expect(localStorage.getItem('k')).toBe(JSON.stringify('upd'))
      expect(r.current[0]).toBe('upd')
    })
  })

  it('handles quota error', async () => {
    const s = vi.spyOn(Storage.prototype,'setItem').mockImplementation(() => {throw new DOMException('Quota','QuotaExceededError')})
    const {result:r} = renderHook(() => useLocalStorage('k','v'))
    act(() => r.current[1]('lg'))
    await waitFor(() => expect(r.current[0]).toBe('v'))
    s.mockRestore()
  })
})
```

Clear localStorage before tests. Mock methods to test error handling.

## Testing useFetch Hook

Hooks with dependencies need tests verifying re-execution logic.

```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useFetch } from './useFetch'

global.fetch = vi.fn()

describe('useFetch', () => {
  it('fetches on mount', async () => {
    global.fetch.mockResolvedValueOnce({ok:true,json:async () => ({d:'t'})})
    const {result:r} = renderHook(() => useFetch('/t'))
    expect(r.current.loading).toBe(true)
    await waitFor(() => {
      expect(r.current.loading).toBe(false)
      expect(r.current.data).toEqual({d:'t'})
    })
  })

  it('refetches when URL changes', async () => {
    global.fetch.mockResolvedValueOnce({ok:true,json:async () => ({d:'1'})}).mockResolvedValueOnce({ok:true,json:async () => ({d:'2'})})
    const {result:r,rerender:rr} = renderHook(({url}) => useFetch(url), {initialProps:{url:'/1'}})
    await waitFor(() => expect(r.current.data).toEqual({d:'1'}))
    rr({url:'/2'})
    await waitFor(() => expect(r.current.data).toEqual({d:'2'}))
    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('sets error on failure', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Net'))
    const {result:r} = renderHook(() => useFetch('/t'))
    await waitFor(() => {
      expect(r.current.loading).toBe(false)
      expect(r.current.error).toEqual(new Error('Net'))
    })
  })
})
```

Mock global.fetch with chained `mockResolvedValueOnce`.

## Testing Hooks with Context

Hooks consuming React Context require wrapping in context provider during tests. Testing Library's `wrapper` option provides context automatically for every render.

```typescript
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ThemeProvider, useTheme } from './ThemeContext'

const wrapper = ({children}: {children: React.ReactNode}) => (<ThemeProvider>{children}</ThemeProvider>)

describe('useTheme', () => {
  it('provides default theme', () => {
    const {result} = renderHook(() => useTheme(), {wrapper})
    expect(result.current.theme).toBe('light')
  })

  it('toggles theme', () => {
    const {result} = renderHook(() => useTheme(), {wrapper})
    act(() => {result.current.toggleTheme()})
    expect(result.current.theme).toBe('dark')
    act(() => {result.current.toggleTheme()})
    expect(result.current.theme).toBe('light')
  })

  it('throws error when used outside provider', () => {
    expect(() => renderHook(() => useTheme())).toThrow('useTheme must be used within ThemeProvider')
  })
})
```

Create wrapper component providing context. Pass wrapper to `renderHook` via options. Test default values, updates, and error when provider missing.

## Testing Hook Cleanup

Hooks with side effects must clean up on unmount to prevent memory leaks. Test cleanup by calling `unmount()` and verifying event listeners, timers, and subscriptions are removed.

```typescript
import { renderHook } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useInterval } from './useInterval'

describe('useInterval cleanup', () => {
  it('clears interval on unmount', () => {
    vi.useFakeTimers()
    const callback = vi.fn()
    const {unmount} = renderHook(() => useInterval(callback, 1000))
    expect(callback).toHaveBeenCalledTimes(0)
    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(1)
    unmount()
    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(1)
    vi.useRealTimers()
  })

  it('clears interval when delay changes', () => {
    vi.useFakeTimers()
    const c = vi.fn()
    const {rerender} = renderHook(({delay}) => useInterval(c, delay), {initialProps:{delay:1000}})
    vi.advanceTimersByTime(1000)
    expect(c).toHaveBeenCalledTimes(1)
    rerender({delay:2000})
    vi.advanceTimersByTime(1000)
    expect(c).toHaveBeenCalledTimes(1)
    vi.advanceTimersByTime(1000)
    expect(c).toHaveBeenCalledTimes(2)
    vi.useRealTimers()
  })
})
```

Use `vi.useFakeTimers()` to control time. Advance timers with `vi.advanceTimersByTime()`. Verify cleanup prevents further callbacks after unmount.

## Hook Testing Summary

**Unit test custom hooks for:**
- State initialization and updates
- Effect execution and cleanup
- Dependency re-execution
- SSR safety (window/document checks)
- Error handling

Helix-dot-com-next and policy-node's 4 SSR-safe hooks require estimated 12-16 unit tests covering initialization, browser API access, cleanup, and error states.
## Custom Hook Testing Coverage Goals

**Critical hooks (data fetching, auth state):** 90%+ coverage
**Standard hooks (local storage, media queries):** 70-80% coverage
**Simple hooks (state wrappers, formatters):** 50-60% coverage

Analyzed codebases have 4 SSR-safe custom hooks requiring estimated 15-20 tests total. Cover initialization, state updates, cleanup, SSR safety, and error handling for each hook.
