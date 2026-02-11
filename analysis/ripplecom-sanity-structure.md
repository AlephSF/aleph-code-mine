# Ripplecom-Nextjs (Sanity) - Structural Analysis

## Project Overview

**Repository Location:** Sanity Studio at `/apps/sanity-studio` in monorepo  
**Monorepo Type:** Turbo-based multi-app workspace  
**Sanity Version:** 4.3.0 (latest stable)

---

## Code Metrics

- **Schema Files:** 78 across 95 TypeScript files
- **Total LOC:** ~12,974 lines (Sanity-specific only)
- **Document Types:** 16
- **Component Types:** 15 (reusable UI blocks)
- **Object Types:** 13 (embedded data structures)
- **Global Singletons:** 6 (site-wide configuration)

---

## Content Architecture

**16 Document Types:**
- Core: blogPost, caseStudy, pressRelease, page, leadGeneration, thankYouPage, event, person
- Categories: category, tag, pageSubnav, redirect
- Legacy: legacyCtaCard, legacyQuote, legacyVideo, section (Contentful migration)

**15 Component Types:**
- heroSection, ctaSection, textSection, imageSection, cardGrid, button, ctaCard
- eventCard, investmentsCard, bioModal, modalLogo, contentDetailModal, collapsibleSection, newsletterSignup, spacer

**13 Object Types:**
- seo (comprehensive meta), link (6 variants), blogMeta, publishingMeta, navigationItem/Column/Dropdown
- contactInfo, country, footerSection, hoverLayoutItem, valueProps

**6 Global Singletons:**
- homepage, navigation, footerNavigation, defaultSeo, regions, rlusdBalance

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| sanity | ^4.3.0 | Core CMS |
| @sanity/client | ^7.12.0 | API client |
| sanity-plugin-media | ^4.0.0 | Enhanced media |
| algoliasearch | ^4.24.0 | Search indexing |

---

## Notable Features

1. **Presentation Tool Integration** - Live draft preview with dynamic URL resolution
2. **Algolia Search** - Full-stack integration with batch indexing (5 content types)
3. **Link Field Polymorphism** - Single field handling 6 link types (internal/external/email/phone/file/anchor)
4. **Rich Text Composition** - Portable text supporting inline media (images, videos, quotes, buttons, code, tables, forms)
5. **Legacy Content Preservation** - 14 legacy Contentful schemas for gradual migration
6. **Multi-Environment Configuration** - Environment-aware functions for preview URLs and CORS
7. **Okta/SAML Authentication** - Enterprise SSO integration

---

## Architectural Patterns

1. **Singleton Pattern** - Document IDs for single-instance globals (no "create new")
2. **Modular Fields** - Reusable field schemas prevent duplication
3. **SEO-First** - Comprehensive SEO object in all content
4. **Type Safety** - Full TypeScript with 48KB generated types
5. **Draft Mode** - Native Next.js draft integration

---

## Integration Points

- **Search:** Algolia with full batch sync
- **Preview:** Presentation tool with location-based routing
- **Frontend:** Generated types exported to Next.js app
- **Authentication:** Okta SAML, dual-mode (email + SAML)

---

**Summary:** Sophisticated Sanity v4 studio in monorepo with 78 schemas (12,974 LOC), Algolia search integration, Presentation Tool for preview, legacy Contentful migration support, and Okta SAML authentication. Most complex Sanity implementation across all repos with polymorphic link fields and comprehensive type safety.
