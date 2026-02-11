---
title: "Folder-per-Component Structure"
category: "component-patterns"
subcategory: "file-organization"
tags: ["components", "file-structure", "barrel-exports", "organization"]
stack: "js-nextjs"
priority: "high"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

## Standard Folder Structure

Next.js components follow a strict folder-per-component pattern where each component lives in its own directory named after the component. The directory contains the component file, styles, tests, and a barrel export file. All three analyzed codebases (helix-dot-com-next, kariusdx-next, policy-node) use this pattern universally across 240+ component folders. Component folders use PascalCase naming matching the component name exactly (Button/, TwoUp/, SiteHeader/).

```
Button/
├── Button.tsx              # Component implementation
├── Button.module.scss      # Component-scoped styles
├── Button.stories.tsx      # Storybook stories (if used)
├── Button.test.tsx         # Tests (if present)
└── index.ts                # Barrel export
```

## Barrel Export Pattern

Every component folder contains an `index.ts` file that re-exports the default export from the component file. Barrel exports enable clean import paths throughout the application. Consumers import components using the folder name rather than the full file path.

```typescript
// index.ts
export { default } from './Button'
```

Imports reference the folder, not the file:

```typescript
// Correct - import from folder
import Button from '@/components/Button'

// Avoid - importing the file directly
import Button from '@/components/Button/Button'
```

## Component File Contents

The primary `.tsx` file contains the component implementation, props type definition, and default export. Component files do not import from their own index.ts barrel file. Props types are colocated in the same file as the component, defined immediately before the component declaration. Auxiliary files (styles, tests, stories) follow the same naming pattern: `ComponentName.module.scss`, `ComponentName.test.tsx`, `ComponentName.stories.tsx`.

## What Belongs in Component Folders

Component folders contain only files directly related to that specific component. Shared utilities, types used across multiple components, or subcomponents live elsewhere. Subcomponents that are only used by the parent component can optionally live in a nested folder within the parent's directory.

```
Accordion/
├── Accordion.tsx
├── Accordion.module.scss
├── index.ts
└── AccordionItem/           # Subcomponent used only by Accordion
    ├── AccordionItem.tsx
    ├── AccordionItem.module.scss
    └── index.ts
```

Icon components follow the same folder structure but typically live in a dedicated `svgs/` directory alongside other components.
