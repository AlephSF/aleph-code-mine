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

## Testing Custom React Hooks in Next.js

Custom hooks encapsulate reusable stateful logic and side effects. Testing hooks verifies state updates, effect cleanup, dependency handling, and SSR-safe initialization. Testing Library's `renderHook` utility renders hooks in isolation without requiring wrapper components. SSR-safe hooks (100% pattern in analyzed codebases) require tests validating window/document checks and mount tracking.

### Why Test Custom Hooks Separately

Custom hooks contain business logic that should be tested independently of UI components. Testing hooks in isolation produces faster, more focused tests than testing through components. Helix-dot-com-next and policy-node have 4 SSR-safe custom hooks with zero tests. Hook bugs affect all components importing the hook. Source confidence: 0% (no custom hook tests exist in analyzed codebases).

### Testing Library's renderHook Utility

Testing Library's `renderHook` function renders hooks in test components and provides utilities for triggering re-renders and accessing hook return values. Install Testing Library React if not already present: `npm install -D @testing-library/react`. The `renderHook` API works identically for synchronous and asynchronous hooks.

#### Basic Hook Testing Pattern

```typescript
// useCounter.test.ts
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('initializes with default value 0', () => {
    const { result } = renderHook(() => useCounter())

    expect(result.current.count).toBe(0)
  })

  it('initializes with custom initial value', () => {
    const { result } = renderHook(() => useCounter(10))

    expect(result.current.count).toBe(10)
  })

  it('increments count when increment is called', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.increment()
    })

    expect(result.current.count).toBe(1)
  })

  it('decrements count when decrement is called', () => {
    const { result } = renderHook(() => useCounter(5))

    act(() => {
      result.current.decrement()
    })

    expect(result.current.count).toBe(4)
  })
})
```

`renderHook` accepts callback returning the hook. Access hook return value via `result.current`. Wrap state updates in `act()` to ensure React processes updates before assertions. Test initial state, state transitions, and boundary conditions (zero, negative values, large numbers).

### Testing SSR-Safe Custom Hooks

SSR-safe hooks check for window/document existence before accessing browser APIs. All 4 custom hooks in analyzed codebases follow this pattern. Tests must verify hooks work in both SSR environment (no window) and client environment (window exists).

#### Testing useWindowSize Hook

```typescript
// useWindowSize.test.ts
import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useWindowSize } from './useWindowSize'

describe('useWindowSize - SSR safety', () => {
  it('returns default size during SSR (no window)', () => {
    // Simulate SSR by deleting window
    const originalWindow = global.window
    delete (global as any).window

    const { result } = renderHook(() => useWindowSize())

    expect(result.current.width).toBe(0)
    expect(result.current.height).toBe(0)

    // Restore window
    global.window = originalWindow
  })

  it('returns actual window size on client', () => {
    // Mock window.innerWidth/innerHeight
    Object.defineProperty(window, 'innerWidth', { value: 1024, writable: true })
    Object.defineProperty(window, 'innerHeight', { value: 768, writable: true })

    const { result } = renderHook(() => useWindowSize())

    expect(result.current.width).toBe(1024)
    expect(result.current.height).toBe(768)
  })
})

describe('useWindowSize - resize listener', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('updates size on window resize', async () => {
    Object.defineProperty(window, 'innerWidth', { value: 1024, writable: true })
    Object.defineProperty(window, 'innerHeight', { value: 768, writable: true })

    const { result } = renderHook(() => useWindowSize())

    expect(result.current.width).toBe(1024)

    // Simulate resize
    act(() => {
      Object.defineProperty(window, 'innerWidth', { value: 1280, writable: true })
      window.dispatchEvent(new Event('resize'))
    })

    await waitFor(() => {
      expect(result.current.width).toBe(1280)
    })
  })

  it('cleans up resize listener on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

    const { unmount } = renderHook(() => useWindowSize())

    unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))
  })
})
```

Test SSR safety by deleting global.window temporarily. Mock window properties with `Object.defineProperty`. Dispatch synthetic resize events with `window.dispatchEvent(new Event('resize'))`. Verify cleanup with `removeEventListenerSpy` to prevent memory leaks.

### Testing Hooks with Async Effects

Hooks fetching data or performing async operations require `waitFor` for assertions. Testing Library's `waitFor` retries assertions until they pass or timeout, handling async state updates gracefully.

#### Testing useLocalStorage Hook

```typescript
// useLocalStorage.test.ts
import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { useLocalStorage } from './useLocalStorage'

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('initializes with default value when key does not exist', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'))

    expect(result.current[0]).toBe('default')
  })

  it('initializes with stored value when key exists', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'))

    const { result } = renderHook(() => useLocalStorage('test-key', 'default'))

    expect(result.current[0]).toBe('stored-value')
  })

  it('updates localStorage when setValue is called', async () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))

    act(() => {
      result.current[1]('updated')
    })

    await waitFor(() => {
      expect(localStorage.getItem('test-key')).toBe(JSON.stringify('updated'))
      expect(result.current[0]).toBe('updated')
    })
  })

  it('handles localStorage quota exceeded error', async () => {
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      .mockImplementation(() => {
        throw new DOMException('Quota exceeded', 'QuotaExceededError')
      })

    const { result } = renderHook(() => useLocalStorage('test-key', 'value'))

    act(() => {
      result.current[1]('large-data')
    })

    // Value should not update on error
    await waitFor(() => {
      expect(result.current[0]).toBe('value')
    })

    setItemSpy.mockRestore()
  })
})
```

Clear localStorage before each test with `beforeEach(() => localStorage.clear())`. Mock localStorage methods to test error handling (quota exceeded, access denied). Use `waitFor` for async assertions after state updates. Test both success and failure paths.

### Testing Hooks with Dependencies

Hooks often depend on props, context, or external values. Test hooks with different dependencies to verify re-execution logic. Testing Library's `rerender` function updates hook dependencies and triggers re-renders.

#### Testing useFetch Hook with Dependencies

```typescript
// useFetch.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useFetch } from './useFetch'

global.fetch = vi.fn()

describe('useFetch', () => {
  it('fetches data on mount', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' }),
    })

    const { result } = renderHook(() => useFetch('/api/test'))

    // Initial loading state
    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBe(null)

    // Wait for fetch to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.data).toEqual({ data: 'test' })
    })
  })

  it('refetches when URL changes', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'first' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'second' }),
      })

    const { result, rerender } = renderHook(
      ({ url }) => useFetch(url),
      { initialProps: { url: '/api/first' } }
    )

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'first' })
    })

    // Change URL dependency
    rerender({ url: '/api/second' })

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'second' })
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('sets error state on fetch failure', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useFetch('/api/test'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.error).toEqual(new Error('Network error'))
      expect(result.current.data).toBe(null)
    })
  })
})
```

Mock global.fetch with chained `mockResolvedValueOnce` for multiple calls. Use `rerender` to update hook props and trigger dependency re-execution. Test loading states, success states, and error states. Verify fetch is called correct number of times.

### Testing Hooks with Context

Hooks consuming React Context require wrapping in context provider during tests. Testing Library's `wrapper` option provides context automatically for every render.

#### Testing Hook with Context

```typescript
// useTheme.test.ts
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ThemeProvider, useTheme } from './ThemeContext'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
)

describe('useTheme', () => {
  it('provides default theme value', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })

    expect(result.current.theme).toBe('light')
  })

  it('toggles theme between light and dark', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })

    expect(result.current.theme).toBe('light')

    act(() => {
      result.current.toggleTheme()
    })

    expect(result.current.theme).toBe('dark')

    act(() => {
      result.current.toggleTheme()
    })

    expect(result.current.theme).toBe('light')
  })
})
```

Define wrapper component providing context. Pass `wrapper` option to `renderHook`. Wrapper is applied to every render and rerender automatically. Test context state initialization and mutations through context API.

### Testing Hook Cleanup and Memory Leaks

Hooks registering event listeners, timers, or subscriptions must clean up on unmount. Test cleanup by verifying removeEventListener, clearInterval, or unsubscribe are called. Memory leaks occur when cleanup is missing.

#### Testing Hook Cleanup

```typescript
// useInterval.test.ts
import { renderHook } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useInterval } from './useInterval'

describe('useInterval - cleanup', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls callback on interval', () => {
    const callback = vi.fn()
    renderHook(() => useInterval(callback, 1000))

    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(2)
  })

  it('clears interval on unmount', () => {
    const callback = vi.fn()
    const { unmount } = renderHook(() => useInterval(callback, 1000))

    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    unmount()

    vi.advanceTimersByTime(2000)
    expect(callback).toHaveBeenCalledTimes(1)  // No additional calls after unmount
  })

  it('updates interval when delay changes', () => {
    const callback = vi.fn()
    const { rerender } = renderHook(
      ({ delay }) => useInterval(callback, delay),
      { initialProps: { delay: 1000 } }
    )

    vi.advanceTimersByTime(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    rerender({ delay: 500 })

    vi.advanceTimersByTime(500)
    expect(callback).toHaveBeenCalledTimes(2)
  })
})
```

Use `vi.useFakeTimers()` to control time in tests. Advance time with `vi.advanceTimersByTime()`. Verify callback stops after unmount (cleanup executed). Test dependency changes trigger cleanup and re-initialization.

## Custom Hook Testing Coverage Goals

**Critical hooks (data fetching, auth state):** 90%+ coverage
**Standard hooks (local storage, media queries):** 70-80% coverage
**Simple hooks (state wrappers, formatters):** 50-60% coverage

Analyzed codebases have 4 SSR-safe custom hooks requiring estimated 15-20 tests total. Cover initialization, state updates, cleanup, SSR safety, and error handling for each hook.
