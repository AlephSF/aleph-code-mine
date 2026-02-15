---
title: "SVG Component Pattern"
category: "component-patterns"
subcategory: "icons"
tags: ["svg", "icons", "arrow-functions", "file-organization"]
stack: "js-nextjs"
priority: "medium"
audience: "frontend"
complexity: "beginner"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

## SVG Component File Location

SVG icon components live in a dedicated `svgs/` directory within the main components folder. The `svgs/` folder follows the same folder-per-component structure as regular components. All three analyzed codebases maintain this pattern across 70+ SVG components. SVG components are treated as first-class components with the same folder structure, barrel exports, and naming conventions as regular components.

```
components/
├── Button/
├── TwoUp/
└── svgs/
    ├── ArrowRight/
    │   ├── ArrowRight.tsx
    │   └── index.ts
    ├── Download/
    │   ├── Download.tsx
    │   └── index.ts
    └── Logo/
        ├── Logo.tsx
        └── index.ts
```

SVG components import the same way as any other component:

```typescript
import ArrowRight from '../svgs/ArrowRight'
import Download from '../svgs/Download'
```

## SVG Component Structure

SVG components use arrow function syntax with explicit `JSX.Element` return type annotation and bottom default export. SVG components contain the raw SVG markup copied from design tools like Figma or Illustrator. Components accept minimal or no props beyond optional `className` for style customization.

```typescript
const ArrowRight = (): JSX.Element => (
  <svg width='15' height='16' viewBox='0 0 15 16' fill='none' xmlns='http://www.w3.org/2000/svg'>
    <path d='M14.7071 8.70711C15.0976 8.31658 15.0976 7.68342 14.7071 7.29289L8.34315 0.928932C7.95262 0.538408 7.31946 0.538408 6.92893 0.928932C6.53841 1.31946 6.53841 1.95262 6.92893 2.34315L12.5858 8L6.92893 13.6569C6.53841 14.0474 6.53841 14.6805 6.92893 15.0711C7.31946 15.4616 7.95262 15.4616 8.34315 15.0711L14.7071 8.70711ZM0 9H14V7H0V9Z' fill='#3F4C77' />
  </svg>
)

export default ArrowRight
```

Arrow functions with implicit returns keep SVG components concise. The entire SVG markup appears inline without intermediate variables or logic.

## ClassName Prop Convention

SVG components accept optional `className` prop for external styling control. Applies to root `<svg>` element.

```typescript
type IconProps={className?:string}
const Download=({className}:IconProps):JSX.Element=>(
  <svg className={className} width='24' height='24' viewBox='0 0 24 24' fill='none'>
    <path d='M12 16L7 11L8.4 9.6L11 12.2V4H13V12.2L15.6 9.6L17 11L12 16Z' fill='currentColor'/>
  </svg>
)
export default Download
```

Usage:

```typescript
import Download from '../svgs/Download'
import styles from './Button.module.scss'
export default function Button({download}:ButtonProps){
  return(<button>{download&&<Download className={styles.icon}/>}Download</button>)
}
```

**CurrentColor for fill control:** SVG paths use `fill='currentColor'` to inherit parent text color. Enables customization through CSS `color` property instead of hardcoding fills. Icons adapt to theme changes/hover states automatically.

```typescript
const Icon=():JSX.Element=>(
  <svg width='24' height='24' viewBox='0 0 24 24'>
    <path d='M...' fill='currentColor'/>
  </svg>
)
```

Parent CSS controls icon color:

```scss
.button{color:blue;}
.button:hover{color:darkblue;}
```
