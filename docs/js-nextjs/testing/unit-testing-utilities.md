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

## Unit Testing Utility Functions in Next.js

Utility functions represent the highest-value testing target due to their pure, deterministic nature and widespread usage across applications. Functions like data formatters, string manipulators, and parsers require comprehensive test coverage because bugs multiply across every component that imports them. Unit tests for utilities run in milliseconds and provide immediate feedback during development.

### High-Value Testing Target: formatValue.ts

Policy-node's `formatValue.ts` utility (78 lines) formats numbers as percentages, currencies, or raw values with i18n localization. The function handles five format types (`percentage`, `USD`, `CAD`, `AUD`, `EUR`, `GBP`, `raw`), multiple locales (`en-US`, `fr`, `it`, `es`), and edge cases (null, undefined, NaN, string-to-number conversion). Without tests, changes to this function risk breaking all financial data displays across the application. Source confidence: 0% (no tests exist for this critical utility).

#### Testing All Format Types

```typescript
// formatValue.test.ts
import { describe, it, expect } from 'vitest'
import { formatValue } from '@/utils/formatValue'

describe('formatValue - percentage format', () => {
  it('converts decimal to percentage with 0 decimals', () => {
    expect(formatValue(0.1234, 'percentage', 0)).toBe('12%')
  })

  it('converts decimal to percentage with 2 decimals', () => {
    expect(formatValue(0.1234, 'percentage', 2)).toBe('12.34%')
  })

  it('handles large percentages with compact notation', () => {
    expect(formatValue(12.34, 'percentage', 0)).toBe('1.2K%')
  })
})

describe('formatValue - currency format', () => {
  it('formats USD with default locale', () => {
    expect(formatValue(1234.56, 'USD', 2)).toMatch(/\$1(\.|,)2K/)
  })

  it('formats EUR with compact notation', () => {
    expect(formatValue(1234.56, 'EUR', 0)).toMatch(/€1(\.|,)2K/)
  })
})
```

Tests use `describe` blocks to group related test cases by format type. Each `it` block tests one specific behavior. Compact notation (`1.2K%`) varies by locale, so tests use regex matching for flexibility. Tests verify both typical inputs (0.1234) and edge cases (large numbers triggering compact notation).

### Testing Edge Cases and Error Handling

Robust utility functions handle invalid inputs gracefully. `formatValue` must handle null, undefined, NaN, non-numeric strings, and invalid format types. Tests document these edge cases explicitly, preventing regressions when refactoring error handling logic.

#### Edge Case Test Coverage

```typescript
describe('formatValue - edge cases', () => {
  it('returns empty string for null', () => {
    expect(formatValue(null, 'percentage')).toBe('')
  })

  it('returns empty string for undefined', () => {
    expect(formatValue(undefined, 'USD')).toBe('')
  })

  it('returns original string for non-numeric input', () => {
    expect(formatValue('invalid', 'percentage')).toBe('invalid')
  })

  it('handles string numbers by converting to numeric', () => {
    expect(formatValue('0.5', 'percentage', 0)).toBe('50%')
  })

  it('uses default format when format parameter is missing', () => {
    expect(formatValue(0.5)).toBe('50%')  // Default: percentage
  })
})
```

Edge case tests prevent runtime errors in production. A missing null check causes `TypeError: Cannot read property 'toLocaleString' of null`. Tests catch these failures during development, not in production. Each edge case test represents a real-world scenario encountered in production data.

### Testing Internationalization (i18n) Logic

Utilities handling localization require tests for each supported locale. Policy-node's `formatValue` supports four locales (`EN-US`, `FR`, `IT`, `ES`) with locale-specific rounding phrases (`+{number}` vs `+ de {number}`). Tests verify currency symbols, decimal separators, and thousand separators differ across locales.

#### Locale-Specific Tests

```typescript
describe('formatValue - localization', () => {
  it('uses English rounding phrase for EN-US locale', () => {
    expect(formatValue(1500, 'raw', 0, 'en-US')).toContain('2K+')
  })

  it('uses French rounding phrase for FR locale', () => {
    expect(formatValue(1500, 'raw', 0, 'fr')).toContain('+ de')
  })

  it('handles invalid locale by falling back to EN-US', () => {
    expect(formatValue(1500, 'raw', 0, 'invalid')).toContain('2K+')
  })

  it('formats EUR differently in FR vs IT locales', () => {
    const frResult = formatValue(1234.56, 'EUR', 2, 'fr')
    const itResult = formatValue(1234.56, 'EUR', 2, 'it')
    expect(frResult).not.toBe(itResult)  // Different separators
  })
})
```

Locale tests verify i18n logic without requiring manual testing in different languages. Tests document supported locales explicitly, preventing accidental breakage when adding new languages. Fallback behavior tests ensure application doesn't crash with unsupported locales.

### Testing Complex String Manipulation: replacePlaceholders

Policy-node's `replacePlaceholders.ts` utility performs regex-based placeholder replacement with recursive object traversal. The function handles two placeholder syntaxes (`%{key}` and `{{key}}`), quote normalization, and nested object structures. Regex edge cases (special characters, Unicode, empty keys) require thorough test coverage. Source confidence: 0% (no tests exist despite XSS risk).

#### Regex and Recursion Tests

```typescript
// replacePlaceholders.test.ts
import { replacePlaceholders, processObjectPlaceholders } from '@/utils/replacePlaceholders'

describe('replacePlaceholders - basic substitution', () => {
  it('replaces %{key} placeholders', () => {
    const result = replacePlaceholders('Hello %{name}', { name: 'World' })
    expect(result).toBe('Hello World')
  })

  it('replaces {{key}} placeholders', () => {
    const result = replacePlaceholders('Hello {{name}}', { name: 'World' })
    expect(result).toBe('Hello World')
  })

  it('removes placeholders without replacements', () => {
    const result = replacePlaceholders('Hello %{name}')
    expect(result).toBe('Hello ')
  })
})

describe('replacePlaceholders - quote normalization', () => {
  it('converts curly quotes to straight quotes', () => {
    const result = replacePlaceholders('"test" and 'test'')
    expect(result).toBe('"test" and \'test\'')
  })

  it('fixes doubled quotes in HTML attributes', () => {
    const result = replacePlaceholders('value=""+>')
    expect(result).toBe('value=">')
  })
})

describe('processObjectPlaceholders - recursion', () => {
  it('processes nested objects recursively', () => {
    const input = { a: '%{x}', b: { c: '%{y}' } }
    const result = processObjectPlaceholders(input, { x: '1', y: '2' })
    expect(result).toEqual({ a: '1', b: { c: '2' } })
  })

  it('processes arrays recursively', () => {
    const input = ['%{a}', '%{b}']
    const result = processObjectPlaceholders(input, { a: '1', b: '2' })
    expect(result).toEqual(['1', '2'])
  })
})
```

Regex tests verify both placeholder syntaxes work correctly. Quote normalization tests prevent XSS vulnerabilities from curly quotes in user input. Recursive tests ensure deeply nested objects are processed completely. Each test case represents a real data structure from WordPress ACF fields or Sanity documents.

### Testing CSV Parsing: csvToJson

Policy-node's `csvToJson.ts` utility (170+ lines) handles async streaming, HTTP errors, buffer conversion, and CSV parsing. The function must handle malformed CSVs, network timeouts, and encoding issues. Unit tests mock HTTP responses to test error handling without real network requests. Source confidence: 0% (no tests for critical build-time utility).

#### Mocking HTTP with Vitest

```typescript
// csvToJson.test.ts
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { fetchCsvFromUrl } from '@/utils/csvToJson'

// Mock global fetch
global.fetch = vi.fn()

describe('fetchCsvFromUrl - success cases', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('parses valid CSV data', async () => {
    const mockCsv = 'name,age\nAlice,30\nBob,25'
    global.fetch.mockResolvedValue({
      ok: true,
      arrayBuffer: async () => Buffer.from(mockCsv),
    })

    const result = await fetchCsvFromUrl('http://example.com/data.csv')

    expect(result).toEqual([
      { name: 'Alice', age: '30' },
      { name: 'Bob', age: '25' },
    ])
  })
})

describe('fetchCsvFromUrl - error cases', () => {
  it('throws error for HTTP 404', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 404 })

    await expect(fetchCsvFromUrl('http://example.com/missing.csv'))
      .rejects.toThrow('HTTP error! Status: 404')
  })

  it('throws error for network failure', async () => {
    global.fetch.mockRejectedValue(new Error('Network error'))

    await expect(fetchCsvFromUrl('http://example.com/data.csv'))
      .rejects.toThrow('Failed to fetch or parse CSV: Network error')
  })
})
```

Vitest's `vi.fn()` creates mock functions that track calls and return values. `beforeEach` clears mocks between tests to prevent test pollution. Async tests use `await expect(...).rejects.toThrow()` for promise rejection assertions. Mocking avoids real HTTP requests, making tests fast (milliseconds) and reliable (no network dependencies).

### Test File Organization

Co-locate test files with source files using `__tests__` directories or `.test.ts` suffix. Policy-node structure:

```
src/utils/
  formatValue.ts
  formatValue.test.ts       # Co-located test
  csvToJson.ts
  __tests__/
    csvToJson.test.ts       # Directory-based test
```

Co-located tests improve discoverability and ensure tests are updated when source files change. Vitest automatically discovers files matching `*.test.ts`, `*.spec.ts`, or files in `__tests__` directories. No explicit test file imports required.

## Coverage Goals for Utilities

**High-risk utilities (formatValue, csvToJson, replacePlaceholders):** 90%+ coverage
**Medium-risk utilities (date formatters, slug generators):** 70-80% coverage
**Low-risk utilities (simple string helpers):** 50-60% coverage

Policy-node's 33 utility files require estimated 40-60 unit tests total. High-value targets (formatValue, csvToJson, s3CsvLoader) account for 20-30 tests alone. Start with highest-risk utilities and expand coverage incrementally.
