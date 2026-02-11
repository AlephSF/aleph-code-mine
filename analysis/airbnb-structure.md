# Airbnb WordPress VIP Multisite - Structural Analysis

## Project Overview

**Type:** WordPress VIP Go Multisite (8+ production sites)  
**Sites:** Newsroom, Tech Blog, Careers, Real Estate, Admin Dashboard, Olympics, DLS Blog, Policy  
**Repository:** GitHub (wpcomvip organization)  
**Target WP Version:** 6.7+ (PHP 8.1-8.2)

---

## Code Metrics

- **PHP Files:** 12,526
- **JavaScript Files:** 26,157
- **Total Size:** ~150MB+ (excluding node_modules)
- **Themes:** 14 (custom + stock)
- **Plugins:** 50 (mix of custom, premium, open-source)

---

## Custom Themes (14)

**Primary Active:**
1. **presser** (Newsroom) - Roots Sage, Webpack 5, Preact, Three.js, Lottie
2. **airbnbtech** (Tech Blog) - Traditional PHP functions.php
3. **airbnb-careers** (Careers) - Custom blocks
4. **a4re** - Real estate
5. **protools** - Admin tools
6. **onboard** - Onboarding
7. **Other specialized themes** - Olympics, DLS blog, rentals

---

## Key Plugins (50)

**Custom:**
- airbnb-policy-blocks (12 custom + 15 ACF blocks)
- airbnb-custom-post-types (6+ post types)
- presser-custom-mods (5.6MB with Symfony)
- Gutenberg block plugins (careers, press, protools, rkv)

**Premium:**
- Advanced Custom Fields Pro (24MB)
- Polylang Pro (5.4MB) - i18n
- FacetwP (1.3MB) - Search
- WPBakery JS Composer (21MB)
- Yoast SEO (18MB)

**Editor:** Edit-Flow (2.3MB), fieldmanager

**API:** wpgraphql-acf, vip-block-data-api, wp-graphql-polylang

**Integrations:** Google Site Kit, Onelogin SAML SSO, Greenhouse Jobs API

---

## Must-Use Plugins

1. **plugin-loader.php** - Conditional plugin loading by blog_id
2. **graphql-security.php** - DoS prevention (10KB query limit, 500 complexity max)
3. **disable-yoast-author-indexer.php** - Performance optimization
4. **decoupled-bundle-loader.php** - Headless frontend support
5. **vip-decoupled-bundle/** - Headless CMS utilities
6. **vipgo-helper.php** - VIP Go platform utilities

---

## Configuration & Standards

**PHPCS Configuration:**
- Standards: WordPress VIP Minimum + VIP Go + PSR2
- Indentation: 4-space tabs
- Line Length: No hard limit
- Scans: themes/airbnbtech, themes/presser

**Build Tools:**
- Webpack 5 (presser theme)
- wp-scripts (policy-blocks)
- npm/yarn with 1080+ packages

---

## Notable Architectural Decisions

1. **Multisite Organization** - Single codebase serves 8+ sites with branch-per-environment
2. **Headless/Decoupled Support** - vip-decoupled-bundle + GraphQL API
3. **GraphQL-First Architecture** - Query size/complexity protection, wpgraphql + ACF
4. **Sage Framework** - Modern PHP with namespaces, Blade templating, Controllers
5. **ACF for Content** - ACF Pro with JSON storage, site-specific blocks
6. **Premium Plugin Stack** - ACF Pro, Polylang Pro, FacetwP, Yoast SEO
7. **Language/Translation** - 215+ language directories, Polylang Pro
8. **Security Hardening** - VIP Code Sniffer, GraphQL limits, SAML SSO
9. **Content Syndication** - Facebook Instant Articles, Twitter API
10. **Development Workflow** - VIP Lando locally, multi-branch deployment (develop → staging, master → production)

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **CMS** | WordPress VIP Go Multisite 6.7+ |
| **PHP** | 8.1-8.2 |
| **Primary Theme** | Roots Sage (presser) |
| **Template Engine** | Blade (Laravel) |
| **JS Build** | Webpack 5, Babel 7 |
| **CSS** | SCSS → PostCSS |
| **JS Framework** | Preact (presser) |
| **Content Fields** | ACF Pro + Fieldmanager |
| **API** | GraphQL (WP GraphQL) + REST |
| **SEO** | Yoast SEO |
| **Multilingual** | Polylang Pro |
| **Search** | FacetwP |
| **Page Builder** | Gutenberg + WPBakery (legacy) |
| **Auth** | Onelogin SAML SSO |
| **Code Standards** | PHPCS (VIP WordPress) + ESLint + StyleLint |

---

**Summary:** Large-scale WordPress VIP Go multisite (8+ production sites) with 14 custom themes, 50 plugins, GraphQL-first headless architecture, Sage framework with Blade templating, Webpack 5 build system, Polylang Pro for i18n, and comprehensive security hardening. Serves Airbnb Newsroom, Tech Blog, Careers, and multiple specialized sites from single codebase.
