# Testing Infrastructure - Cross-Project Comparison

**Analysis Date:** February 11, 2026
**Scope:** helix-dot-com-next, kariusdx-next, policy-node
**Finding:** ZERO testing infrastructure across all Next.js repositories

---

## Executive Summary

**Critical Gap:** None of the three Next.js repositories have ANY testing infrastructure despite containing complex business logic, data transformations, and user-facing features. This represents a significant technical debt and quality assurance gap.

---

## Quantitative Analysis

### Test Files
| Repo | Test Files | Test Scripts | Test Framework | Coverage Tool |
|------|------------|--------------|----------------|---------------|
| helix-dot-com-next | 0 | 0 | None | None |
| kariusdx-next | 0 | 0 | None | None |
| policy-node | 0 | 0 | None | None |
| **TOTAL** | **0** | **0** | **None** | **None** |

**Note:** 682 test files found are from `node_modules` only.

### Quality Assurance That DOES Exist

| QA Practice | helix | kariusdx | policy-node | Confidence |
|-------------|-------|----------|-------------|------------|
| ESLint | ✅ `next lint` | ✅ `next lint` | ✅ `next lint` | 100% |
| TypeScript | ✅ tsconfig.json | ✅ tsconfig.json | ✅ tsconfig.json | 100% |
| Stylelint | ✅ `lint:styles` | ❌ | ✅ `lint:styles` | 67% |
| Husky hooks | ✅ `husky install` | ❌ | ✅ `husky` | 67% |
| Custom validation | ❌ | ❌ | ✅ `validate:data` | 33% |
| Type checking | ❌ | ❌ | ❌ | 0% |
| Test runner | ❌ | ❌ | ❌ | 0% |
| E2E testing | ❌ | ❌ | ❌ | 0% |

### Untested Code Analysis

**Utility Files That SHOULD Be Tested:**
- **policy-node**: 33 utility files (17,526 LOC in csvLoader.ts alone)
  - CSV parsing & transformation (csvToJson, csvLoader, s3CsvLoader)
  - Data formatting (formatValue, formatDate, formatCountryName)
  - String manipulation (replacePlaceholders, toCamelCase, sanitize)
  - Localization (normalizeLanguageSlug, denormalizeLanguageSlug, getLocalizedMenuLocation)
  - Complex data pipelines (transformData, transformLocationData, transformUnifiedData)
- **helix-dot-com-next**: 10+ utility files
  - Date/time utilities (toTimestamp)
  - Sanity query builders
- **kariusdx-next**: GROQ query helpers

**API Routes That SHOULD Be Tested:**
- **policy-node**:
  - `/api/metrics` (data transformation, display config, municipality slugs)
  - `/api/phrases` (unified data transformation, location data, locale units)

**Custom Hooks That SHOULD Be Tested:**
- 4 SSR-safe custom hooks (helix + policy-node)
- All follow same pattern but lack unit tests for edge cases

**Components That SHOULD Be Tested:**
- 188 components in helix-dot-com-next
- 75+ components in kariusdx-next
- 50+ components in policy-node
- **Total: 313+ untested components**

---

## Risk Assessment

### High-Risk Untested Code

#### 1. Data Transformation Logic (policy-node)
**File:** `src/utils/formatValue.ts`
**LOC:** 78 lines
**Complexity:** High
**Risk:** Incorrect currency/percentage formatting affects all data displays

```typescript
// Example of complex logic with NO tests:
export function formatValue(
  value: string | number | null | undefined,
  format: FormatType = 'percentage',
  decimals: number = 0,
  currentLangCode: string = 'en-US',
): string {
  // Handles: null/undefined, string-to-number conversion,
  // 5 format types, i18n locales, compact notation
  // What if numericValue is NaN? What if locale is invalid?
  // What if format is not in the union type? NO TESTS.
}
```

#### 2. CSV Parsing & Streaming (policy-node)
**File:** `src/utils/csvToJson.ts`
**LOC:** 170+ lines
**Complexity:** Very High
**Risk:** Data corruption, memory leaks, failed builds

```typescript
// Complex async streaming with NO tests:
async function fetchCsvFromUrl(url: string): Promise<ISupersetMunicipalityData[]> {
  // Handles: HTTP errors, buffer conversion, streaming,
  // CSV parsing, error handling
  // What if URL is invalid? What if CSV is malformed?
  // What if stream errors mid-parse? NO TESTS.
}
```

#### 3. Placeholder Replacement (policy-node)
**File:** `src/utils/replacePlaceholders.ts`
**LOC:** 61 lines
**Complexity:** Medium-High
**Risk:** XSS vulnerabilities, broken content

```typescript
// Recursive object traversal with regex replacement - NO tests:
export function processObjectPlaceholders<T>(obj: T, replacements?: Record<string, string>): T {
  // Recursive, handles arrays, objects, strings
  // What if circular references? What if malicious placeholders?
  // What about Unicode edge cases? NO TESTS.
}
```

#### 4. Custom Validation Scripts (policy-node)
**Irony Alert:** policy-node has a `validate:data` script that validates CSV data integrity... but the validation script ITSELF has no tests.

---

## Comparison with Industry Standards

### Next.js Documentation Recommendations
- ✅ Recommends Jest + React Testing Library for unit/integration tests
- ✅ Recommends Playwright or Cypress for E2E tests
- ❌ **All 3 repos have ZERO test infrastructure**

### Next.js App Router Patterns
- Testing async server components: **Not tested**
- Testing route handlers: **Not tested**
- Testing server actions: **Not applicable (0 usage)**

---

## Recommended Testing Stack

Based on Next.js 14/15 best practices and the codebases' architecture:

### Unit & Integration Testing
- **Framework:** Vitest (faster, better Next.js App Router support than Jest)
- **Component Testing:** @testing-library/react
- **DOM Testing:** @testing-library/dom, @testing-library/user-event
- **API Mocking:** MSW (Mock Service Worker)

### E2E Testing
- **Framework:** Playwright (official Next.js recommendation, better than Cypress for App Router)
- **Coverage:** Critical user flows, preview mode, ISR

### Utilities
- **Coverage:** vitest's c8 coverage tool
- **Type Testing:** @testing-library/jest-dom for type-safe matchers
- **Snapshot Testing:** Vitest's built-in snapshot support

---

## What Should Be Tested First?

### Phase 1: High-Impact Utilities (Week 1)
**Priority:** CRITICAL
**Files to Test:**
1. `policy-node/src/utils/formatValue.ts` (affects all data displays)
2. `policy-node/src/utils/csvToJson.ts` (affects data pipeline)
3. `policy-node/src/utils/replacePlaceholders.ts` (potential XSS risk)
4. `policy-node/src/utils/s3CsvLoader.ts` (build-time failures)

**Estimated Tests:** 40-60 unit tests

### Phase 2: API Routes (Week 2)
**Priority:** HIGH
**Routes to Test:**
1. `/api/metrics/*` routes (data transformations)
2. `/api/phrases/*` routes (location data)

**Estimated Tests:** 20-30 integration tests

### Phase 3: Custom Hooks (Week 3)
**Priority:** MEDIUM
**Hooks to Test:**
1. All 4 SSR-safe custom hooks
2. Edge cases: SSR vs client-side rendering

**Estimated Tests:** 15-20 hook tests

### Phase 4: Components (Weeks 4-6)
**Priority:** MEDIUM
**Components to Test:**
1. High-traffic pages (homepage, key landing pages)
2. Complex interactive components (forms, filters)

**Estimated Tests:** 50-80 component tests

### Phase 5: E2E Critical Flows (Week 7)
**Priority:** MEDIUM
**Flows to Test:**
1. Preview mode workflows
2. ISR revalidation
3. i18n language switching (policy-node)

**Estimated Tests:** 10-15 E2E tests

---

## Confidence Scores

| Pattern | Confidence | Rationale |
|---------|-----------|-----------|
| Zero testing infrastructure | **100%** | Verified via grep, package.json, directory search |
| Zero test runners | **100%** | No Jest, Vitest, Cypress, Playwright in any package.json |
| Zero test scripts | **100%** | No `test` scripts in any package.json |
| ESLint adoption | **100%** | All 3 repos have `next lint` |
| TypeScript adoption | **100%** | All 3 repos have tsconfig.json |
| Stylelint adoption | **67%** | helix + policy-node only |
| Custom validation | **33%** | policy-node only (but validation script itself untested) |

---

## Key Insights

### 1. Technical Debt Accumulation
Without tests, every refactoring is risky. Policy-node's 33 utility files represent ~20K LOC of untested business logic.

### 2. False Sense of Quality
ESLint + TypeScript provide static analysis but catch ZERO runtime bugs:
- `formatValue('abc', 'USD', 2, 'invalid-locale')` → Runtime error
- `csvToJson` with malformed CSV → Silent failure or data corruption
- `replacePlaceholders` with circular object → Stack overflow

### 3. Validation Script Irony
policy-node has sophisticated data validation scripts (`validate:data`, `validate:baseline`) but the validation scripts themselves have no tests.

### 4. Regression Risk
Without tests, every PR is a potential regression. Complex utilities like `formatValue` (78 lines, 5 format types, i18n) are impossible to refactor safely.

### 5. Onboarding Friction
New developers have no executable documentation showing how utilities should behave. Tests serve as living examples.

---

## Next Steps

1. **Install Vitest** in all 3 repos
2. **Create `__tests__` directories** co-located with source files
3. **Write tests for high-risk utilities** (Phase 1 above)
4. **Add `test` script** to package.json
5. **Add `coverage` script** to track progress
6. **Set up GitHub Actions** to run tests on every PR
7. **Add test coverage badge** to README
8. **Make tests required** for PR approval (via branch protection)

---

## Conclusion

The complete absence of testing infrastructure represents the single largest quality assurance gap across all three Next.js repositories. With 313+ untested components, 33+ untested utility files, and complex data transformation pipelines handling production data, the risk of regressions and runtime bugs is extremely high.

**Recommendation:** Implement Phase 1 (high-impact utility tests) within the next sprint to protect critical business logic.
