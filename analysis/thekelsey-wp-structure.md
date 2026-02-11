# The Kelsey WordPress Site - Structural Analysis

## Project Overview

**Site Name:** The Kelsey (thekelsey.org)  
**Project Type:** Bedrock-based WordPress Site  
**Base Framework:** Bedrock (Roots modern WordPress development stack)  
**Theme:** Sage 9 with Blade templating

---

## Code Metrics

- **Total Project Size:** 318 MB
- **PHP Lines:** 352,025 LOC
- **JavaScript Lines:** 247,359 LOC
- **Theme Size:** 270 MB (built assets + node_modules)
- **Custom Components:** 60+ Blade partials
- **Page Templates:** 16 custom templates
- **Custom Post Types:** 3 (Projects, Events, Resources)
- **Custom Gutenberg Blocks:** 15+
- **ACF Field Groups:** 20+

---

## Custom Themes

### Kelsey Theme (Sage 9)

**Tech Stack:**
- Blade templating (Laravel-based)
- Webpack 3.x with BrowserSync
- SCSS with CSS modules
- PSR-4 autoloading
- Controller pattern for data passing

**Structure:**
- app/ - PHP theme logic (Controllers)
- resources/ - Assets, views (Blade templates), functions
- dist/ - Compiled assets
- 16 custom page templates
- 9 custom block templates

---

## Must-Use Plugins

1. **The Kelsey Custom Plugin** - Custom post types, taxonomies, ACF integration
2. **The Kelsey Blocks** - Custom Gutenberg blocks (cgb-scripts)
3. **Advanced Custom Fields Pro** - Premium field management
4. **Bedrock Autoloader** - Roots utility for plugin loading
5. **Disallow Indexing** - Security utility

---

## Configuration Patterns

**Environment Management:**
- .env file (not in repo)
- WP_ENV (production/development/edge)
- GCP Cache integration (Redis-like)
- S3/GCP storage for assets

**Coding Standards:**
- PHPCS: PSR-2 standard
- Theme PSR-2 with Blade-specific relaxations
- VIP-compliant code

---

## Notable Architectural Decisions

1. **Bedrock Foundation** - Modern WordPress dev structure, separates core from app code
2. **Sage 9 Theme** - Laravel Blade templating, MVC-inspired controllers
3. **Must-Use Plugins Strategy** - ACF Pro + custom code in mu-plugins
4. **Custom Post Types** - Projects, Events, Resources with REST API
5. **ACF Field Organization** - JSON-based field groups (version controlled)
6. **Block-First CMS** - 15+ custom Gutenberg blocks
7. **Third-Party Integration** - Funraise (donations), Yoast SEO, Contact Form 7
8. **Multi-Environment Setup** - Production, edge (staging), development
9. **Responsive Image Strategy** - 18 custom image sizes
10. **CSS-in-JS Free** - Sage/Webpack-based Sass compilation

---

**Summary:** Sophisticated Bedrock-based WordPress with Sage 9 theme (352,025 LOC PHP), Blade templating, Webpack build system, 3 custom post types, 16 page templates, 15+ Gutenberg blocks, and ACF Pro for flexible content. Modern WordPress development practices with proper separation of concerns and multi-environment support.
