# Kariusdx Sanity Studio - Structural Analysis

## Project Overview

**Name:** Darkblue Lark (Karius Project)  
**Sanity Version:** v2.30.0  
**Purpose:** Headless CMS for Karius DX diagnostic testing platform  
**Project ID:** nj4jfuv6  
**Dataset:** production (staging in development)

---

## Code Metrics

- **Schema Files:** 64 JS files
- **Total LOC:** 4,270 lines
- **Document Types:** 11
- **Builder Blocks:** 22 reusable content sections
- **Object Types:** 23 reusable objects
- **Custom Fields:** 8

---

## Document Types (11 Total)

1. **page** - Main content pages with page builder, SEO, hero section, FAQs
2. **news** - News/press articles with featured image
3. **pressRelease** - Press releases with SEO pane
4. **clinicalEvidence** - Complex domain-specific schema (study/trial/abstract/article/case)
5. **pathogen** - Microbiology taxonomy (Bacteria, Fungi, Viruses, etc.)
6. **staff** - Team member profiles with headshot and bio
7. **video** - Video content with SEO
8. **event** - Event management
9. **navigation** - Navigation tree structure
10. **navigationMenu** - Menu configuration
11. **siteSettings** - Global site config (social, footer, announcements)

---

## Builder Blocks (22)

**Layout:** pageSection, columns, imageColumnsCard  
**Content:** richText, button, styledLink, horizontalRule  
**Media:** imageCarousel, imageTextCarousel, imageTextLockup  
**Data:** stats, wideCards, processCards, comparisonSection, diagnosisComparison  
**Domain-Specific:** staffGrid, pathogenList, clinicalApplications, jobPostings, resourceContentGrid  
**Integrations:** hubspotForm, wistiaEmbed, googleMapsEmbed

---

## Schema Organization Approach

**Modular Architecture:**
- Centralized imports in schema.js (140 lines)
- Separated concerns: documents, builderBlocks, objects, fields, globals
- Reusable object and field types prevent duplication
- Groups within documents organize related fields

**Validation Strategy:**
- Field-level `.required()` rules
- Custom validation for conditional fields
- Unique value validation
- HTML ID validation (no spaces)

**Conditional Field Logic:**
- `hidden()` functions based on parent/sibling values
- Dynamic field visibility based on document type

---

## Custom Components & Plugins

**Custom Components:** logo.js - Inline Karius SVG logo

**Custom Plugins:** CustomDefaultLayout, Desk Structure Plugin

**Panes & Views:** Iframe preview, SEO Tools pane (Yoast-like), Form view

---

## Architectural Decisions

1. **Hierarchical Page Structure** - Parent-child relationships, automatic path generation
2. **Content Modeling for Domain Specificity** - Clinical evidence with conditional fields
3. **Preview & Production Integration** - TOTP-based preview URLs (hourly rotation)
4. **Custom Action System** - SetSlugAndPublishAction handles slug generation and cascading updates
5. **SEO-First Approach** - Dedicated SEO object with canonical URL, OpenGraph, meta
6. **Color System & Branding** - 22 brand colors with React components
7. **Medical Domain Optimization** - Clinical evidence taxonomy, pathogen classification

---

**Summary:** Complex, production-ready Sanity v2 Studio with 64 schemas (4,270 LOC) tailored for medical/diagnostic domain. Features hierarchical pages, 22 content blocks, custom preview system with TOTP security, comprehensive clinical evidence taxonomy, and SEO-first approach. Highly specialized for medical content management.
