---
title: "Unit Testing Utility Functions in Next.js"
category: "testing"
subcategory: "unit-testing"
tags: ["vitest", "unit-tests", "utilities", "pure-functions", "test-driven-development"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "0%"
last_updated: "2026-02-11"
---

## Unit Testing Utility Functions Overview

Utility functions represent highest-value testing targets: pure functions with widespread usage across applications. Data formatters, string manipulators, and parsers need comprehensive test coverage because bugs multiply across every importing component. Unit tests for utilities run in milliseconds and provide immediate feedback. Policy-node has 33 untested utility files requiring estimated 40-60 unit tests. Source confidence: 0% (zero utility tests exist).

## Testing formatValue.ts (High-Risk Utility)

Policy-node's `formatValue.ts` (78 lines) formats numbers as percentages or currencies with i18n. Handles five format types, four locales, and edge cases (null, undefined, NaN, string conversion). Without tests, changes risk breaking all financial displays.

```typescript
import {describe,it,expect} from 'vitest'
import {formatValue as f} from '@/utils/formatValue'

describe('formatValue',()=>{
  it('converts decimal to percentage',()=>{
    expect(f(0.1234,'percentage',0)).toBe('12%')
    expect(f(0.1234,'percentage',2)).toBe('12.34%')
  })
  it('formats currency',()=>{
    expect(f(1234.56,'USD',2)).toMatch(/\$1(\.|,)2K/)
    expect(f(1234.56,'EUR',0)).toMatch(/€1(\.|,)2K/)
  })
  it('handles null/undefined',()=>{
    expect(f(null,'percentage')).toBe('')
    expect(f(undefined,'USD')).toBe('')
  })
  it('converts string numbers',()=>{
    expect(f('0.5','percentage',0)).toBe('50%')
  })
  it('returns invalid strings unchanged',()=>{
    expect(f('invalid','percentage')).toBe('invalid')
  })
})
```

`describe` blocks group related cases. Compact notation varies by locale, so tests use regex. Edge case tests prevent `TypeError: Cannot read property 'toLocaleString' of null`.

## Testing Internationalization (i18n) in formatValue

Utilities handling localization need tests for each supported locale. Policy-node's `formatValue` supports four locales with locale-specific rounding phrases (`+{number}` vs `+ de {number}`). Tests verify currency symbols, decimal separators, and thousand separators differ across locales.

```typescript
describe('formatValue - localization',()=>{
  it('uses locale-specific rounding phrases',()=>{
    expect(formatValue(1500,'raw',0,'en-US')).toContain('2K+')
    expect(formatValue(1500,'raw',0,'fr')).toContain('+ de')
  })
  it('falls back to EN-US for invalid locales',()=>{
    expect(formatValue(1500,'raw',0,'invalid')).toContain('2K+')
  })
  it('formats EUR differently per locale',()=>{
    const fr=formatValue(1234.56,'EUR',2,'fr')
    const it=formatValue(1234.56,'EUR',2,'it')
    expect(fr).not.toBe(it)
  })
})
```

Locale tests verify i18n logic without manual testing in different languages. Tests document supported locales explicitly, preventing accidental breakage when adding new languages. Fallback behavior tests ensure application doesn't crash with unsupported locales.

## Testing replacePlaceholders (Regex + Recursion)

Policy-node's `replacePlaceholders.ts` performs regex placeholder replacement with recursive traversal. Handles two syntaxes (`%{key}`, `{{key}}`), quote normalization, nested structures. Source confidence: 0% (no tests despite XSS risk).

```typescript
import {replacePlaceholders as r,processObjectPlaceholders as p} from '@/utils/replacePlaceholders'

describe('replacePlaceholders',()=>{
  it('replaces both syntaxes',()=>{
    expect(r('Hi %{name}',{name:'World'})).toBe('Hi World')
    expect(r('Hi {{name}}',{name:'World'})).toBe('Hi World')
  })
  it('removes missing placeholders',()=>{
    expect(r('Hi %{name}')).toBe('Hi ')
  })
  it('converts curly quotes',()=>{
    expect(r('"test" 'test'')).toBe('"test" \'test\'')
  })
  it('fixes doubled quotes',()=>{
    expect(r('value=""+>')).toBe('value=">')
  })
})

describe('processObjectPlaceholders',()=>{
  it('processes nested objects',()=>{
    expect(p({a:'%{x}',b:{c:'%{y}'}},{x:'1',y:'2'})).toEqual({a:'1',b:{c:'2'}})
  })
  it('processes arrays',()=>{
    expect(p(['%{a}','%{b}'],{a:'1',b:'2'})).toEqual(['1','2'])
  })
})
```

Quote normalization prevents XSS from curly quotes. Recursive tests ensure deeply nested objects (WordPress ACF, Sanity documents) are processed completely.

## Testing csvToJson (Async HTTP Mocking)

Policy-node's `csvToJson.ts` (170+ lines) handles async streaming, HTTP errors, buffer conversion, CSV parsing. Must handle malformed CSVs, network timeouts, encoding issues. Tests mock HTTP responses without real network requests. Source confidence: 0%.

```typescript
import {vi,describe,it,expect,beforeEach} from 'vitest'
import {fetchCsvFromUrl as f} from '@/utils/csvToJson'

global.fetch=vi.fn()

describe('fetchCsvFromUrl',()=>{
  beforeEach(()=>vi.clearAllMocks())

  it('parses valid CSV',async()=>{
    global.fetch.mockResolvedValue({ok:true,arrayBuffer:async()=>Buffer.from('name,age\nAlice,30\nBob,25')})
    expect(await f('http://ex.com/d.csv')).toEqual([{name:'Alice',age:'30'},{name:'Bob',age:'25'}])
  })

  it('throws for HTTP 404',async()=>{
    global.fetch.mockResolvedValue({ok:false,status:404})
    await expect(f('http://ex.com/m.csv')).rejects.toThrow('HTTP error! Status: 404')
  })

  it('throws for network failure',async()=>{
    global.fetch.mockRejectedValue(new Error('Network error'))
    await expect(f('http://ex.com/d.csv')).rejects.toThrow('Failed to fetch or parse CSV: Network error')
  })
})
```

`vi.fn()` creates mock functions tracking calls. `beforeEach` clears mocks to prevent pollution. Async tests use `await expect(...).rejects.toThrow()`. Mocking makes tests fast (milliseconds) and reliable (no network dependencies).

## Test File Organization and Discovery

Co-locate test files with source files using `__tests__` directories or `.test.ts` suffix:

```
src/utils/
  formatValue.ts
  formatValue.test.ts       # Co-located test
  csvToJson.ts
  __tests__/
    csvToJson.test.ts       # Directory-based test
```

Vitest auto-discovers files matching `*.test.ts`, `*.spec.ts`, or files in `__tests__` directories. No explicit test file imports required. Co-located tests improve discoverability and ensure tests update when source files change.

## Coverage Goals for Utilities

**High-risk utilities (formatValue, csvToJson, replacePlaceholders):** 90%+ coverage
**Medium-risk utilities (date formatters, slug generators):** 70-80% coverage
**Low-risk utilities (simple string helpers):** 50-60% coverage

Policy-node's 33 utility files require estimated 40-60 unit tests total. High-value targets (formatValue, csvToJson, s3CsvLoader) account for 20-30 tests alone. Start with highest-risk utilities and expand coverage incrementally.
