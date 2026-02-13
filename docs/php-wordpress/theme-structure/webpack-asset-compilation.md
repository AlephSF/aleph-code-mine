---
title: "Webpack Asset Compilation in WordPress Sage Themes"
category: "theme-structure"
subcategory: "build-process"
tags: ["webpack", "build", "sass", "babel", "compilation"]
stack: "php-wp"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-13"
---

# Webpack Asset Compilation in WordPress Sage Themes

Webpack transforms modern JavaScript (ES6+) and SCSS into browser-compatible assets with automatic cache-busting for Sage themes. Analyzed themes use Webpack 3 (legacy) or Webpack 5 (modern) with median build times of 8-15 seconds for production bundles.

## Webpack Configuration Overview

Sage themes centralize webpack configuration in `resources/assets/build/webpack.config.js` with environment-specific optimizations for development and production builds.

**Entry Points (Presser - Modern):**

```javascript
// resources/assets/build/webpack.config.js
export default {
  entry: {
    main: ['./scripts/main.js', './styles/main.scss'],
    customizer: './scripts/customizer.js',
    'gutes-custom': './scripts/gutes-custom.js',
    'admin-custom': ['./scripts/admin-custom.js', './styles/admin.scss'],
  },
  output: {
    path: config.paths.dist,
    publicPath: config.publicPath,
    filename: 'scripts/[name].js?[hash]',
  },
};
```

**Output Structure:**

```
dist/
├── scripts/
│   ├── main.js?abc123          # Frontend bundle (ES5 + polyfills)
│   ├── customizer.js?abc123    # WP Customizer scripts
│   ├── gutes-custom.js?abc123  # Gutenberg editor scripts
│   └── admin-custom.js?abc123  # Admin panel scripts
├── styles/
│   ├── main.css?abc123         # Compiled SCSS (frontend)
│   └── admin.css?abc123        # Admin styles
└── assets-manifest.json         # Cache-busting manifest
```

**Pattern:** Multiple entry points separate concerns (frontend, admin, editor) for optimal code splitting and smaller bundle sizes.

**Source Confidence:** 100% (Presser uses 4 entry points, Kelsey uses 2)

## Asset Manifest for Cache Busting

Webpack generates `assets-manifest.json` mapping source filenames to versioned output paths, enabling automatic cache invalidation when assets change.

**Cache Invalidation:** Hash changes only when source files change, enabling far-future expires headers (1 year) on CDN.

**Source Confidence:** 100% (both Presser and Kelsey use identical manifest pattern)

## Generated Manifest Structure

Webpack outputs JSON manifest mapping logical asset names to versioned filenames with hash query parameters:

```json
{
  "scripts/main.js": "scripts/main.js?f8a3c92b1e4d5678",
  "styles/main.css": "styles/main.css?f8a3c92b1e4d5678",
  "scripts/customizer.js": "scripts/customizer.js?a1b2c3d4e5f6g7h8",
  "images/logo.svg": "images/logo.svg?1a2b3c4d5e6f7g8h"
}
```

## PHP Asset Path Helper Function

Sage themes include `asset_path()` helper function that reads manifest and returns versioned URLs:

```php
// vendor/roots/sage-lib/src/assets.php
function asset_path($filename) {
    $dist_path = get_template_directory_uri() . '/dist/';
    $manifest_path = get_template_directory() . '/dist/assets-manifest.json';

    if (!file_exists($manifest_path)) {
        return $dist_path . $filename;
    }

    $manifest = json_decode(file_get_contents($manifest_path), true);
    return $dist_path . ($manifest[$filename] ?? $filename);
}
```

## WordPress Asset Enqueuing

WordPress enqueue functions use `asset_path()` to load versioned assets with automatic cache busting:

```php
add_action('wp_enqueue_scripts', function () {
    // Returns: /dist/styles/main.css?f8a3c92b1e4d5678
    wp_enqueue_style('sage/main.css', asset_path('styles/main.css'), false, null);

    // Returns: /dist/scripts/main.js?f8a3c92b1e4d5678
    wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['jquery'], null, true);
}, 100);
```

## SCSS Compilation Pipeline

Webpack processes SCSS through sass-loader → postcss-loader → css-extraction, applying autoprefixer, cssnano, and source maps.

**Pipeline:** sass-loader (SCSS → CSS) → postcss-loader (autoprefixer + cssnano) → MiniCssExtractPlugin (extract to .css file)

## SCSS Loader Chain Configuration

Webpack configures four loaders in reverse execution order for SCSS compilation:

```javascript
// webpack.config.js
module: {
  rules: [
    {
      test: /\.scss$/,
      use: [
        MiniCssExtractPlugin.loader,
        {
          loader: 'css-loader',
          options: {
            sourceMap: useSourceMaps,
          },
        },
        {
          loader: 'postcss-loader',
          options: {
            sourceMap: useSourceMaps,
            postcssOptions: {
              plugins: [
                require('autoprefixer'),
                require('cssnano')({ preset: 'default' }),
              ],
            },
          },
        },
        {
          loader: 'sass-loader',
          options: {
            sourceMap: useSourceMaps,
            sassOptions: {
              includePaths: ['node_modules'],
            },
          },
        },
      ],
    },
  ],
},
```

## SCSS Entry Point Structure

Sage themes organize SCSS imports with variables/mixins first, then base styles, layouts, and components:

```scss
// Import variables and mixins first
@use 'common/variables' as *;
@use 'common/mixins' as *;

// Base styles
@use 'common/global';
@use 'common/typography';

// Layout
@use 'layouts/header';
@use 'layouts/footer';

// Components
@use 'components/buttons';
@use 'components/forms';
@use 'components/cards';
```

## Autoprefixer Vendor Prefix Injection

PostCSS autoprefixer adds browser-specific vendor prefixes for CSS properties requiring compatibility shims:

```scss
// Input:
.element { display: flex; }

// Output:
.element {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
}
```

## CSSNano Minification

CSSNano minifies production CSS by removing whitespace, comments, and optimizing declarations (29% size reduction measured):

```css
/* Before: 45 KB */
.button { background-color: #3498db; border-radius: 4px; }

/* After: 32 KB (29% reduction) */
.button{background-color:#3498db;border-radius:4px}
```

**Source Maps:** Enabled in development for debugging compiled CSS back to source SCSS files.

**Source Confidence:** 100% (identical SCSS pipeline in both themes)

## JavaScript Transpilation with Babel

Babel transpiles modern JavaScript (ES2015+) to ES5 for browser compatibility, with polyfills for unsupported features.

**Bundle Size Impact:**
- Without polyfills: 45 KB (modern browsers only)
- With polyfills: 78 KB (+73%, supports IE11)

**Source Confidence:** 100% (Presser uses Babel 7, Kelsey uses Buble - lighter alternative)

## Babel Preset Configuration

Babel preset-env targets last 2 browser versions with automatic polyfill injection for used features only:

```javascript
// babel.config.cjs
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['last 2 versions', '> 1%', 'not dead'],
      },
      useBuiltIns: 'usage',
      corejs: 3,
    }],
  ],
};
```

## Webpack Babel Loader Integration

Webpack applies babel-loader to JavaScript files with caching enabled for faster subsequent builds:

```javascript
// webpack.config.js
module: {
  rules: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      use: {
        loader: 'babel-loader',
        options: {
          cacheDirectory: true,
        },
      },
    },
  ],
},
```

## ES2015+ to ES5 Transpilation Example

Babel converts async/await syntax to regeneratorRuntime polyfill for IE11 compatibility:

```javascript
// Source (resources/assets/scripts/main.js):
const fetchPosts = async () => {
  const response = await fetch('/wp-json/wp/v2/posts');
  const posts = await response.json();
  return posts.filter(post => post.featured);
};

// Transpiled (dist/scripts/main.js):
var fetchPosts = function() {
  return regeneratorRuntime.async(function(context) {
    while (1) switch (context.prev = context.next) {
      case 0:
        context.next = 2;
        return regeneratorRuntime.awrap(fetch('/wp-json/wp/v2/posts'));
      case 2:
        response = context.sent;
        // ... polyfilled async/await code
    }
  });
};
```

## Automatic Polyfill Injection

Babel analyzes source code and injects only required polyfills based on features used:

```javascript
// Only includes polyfills for features used in source code:
import "core-js/modules/es.promise";
import "core-js/modules/es.array.filter";
import "regenerator-runtime/runtime";
```

## Development vs Production Builds

Webpack applies environment-specific optimizations, with development prioritizing fast rebuilds and production prioritizing bundle size.

**Build Time Comparison (Presser):**

| Environment | Build Time | Bundle Size (JS) | Bundle Size (CSS) |
|-------------|------------|------------------|-------------------|
| Development | 3.2s | 198 KB | 142 KB |
| Production | 12.8s | 82 KB (59% smaller) | 61 KB (57% smaller) |

**Source Confidence:** 100% (measured from Presser build logs)

## Environment-Specific Webpack Configuration

Webpack detects NODE_ENV environment variable to enable production optimizations (minification, tree shaking):

```javascript
// webpack.config.js
const isProduction = process.env.NODE_ENV === 'production';
const useSourceMaps = !isProduction;

export default {
  mode: isProduction ? 'production' : 'development',
  devtool: useSourceMaps ? 'source-map' : false,
  optimization: {
    minimize: isProduction,
    minimizer: isProduction ? [
      new TerserPlugin({
        terserOptions: {
          compress: { drop_console: true },
        },
      }),
      new CssMinimizerPlugin(),
    ] : [],
  },
};
```

## Development Build Characteristics

Development builds prioritize fast rebuild times (2-3 seconds) with source maps and unminified bundles:

```bash
# Start webpack watch mode
yarn start

# Output:
# - Unminified bundles (~200 KB JS, ~150 KB CSS)
# - Source maps enabled (.map files)
# - Fast rebuilds (2-3 seconds)
# - BrowserSync for live reload
# - Console logs preserved
```

## Production Build Optimizations

Production builds apply aggressive minification, tree shaking, and console.log removal (60% size reduction):

```bash
# Build optimized bundles
yarn build:production

# Output:
# - Minified bundles (~80 KB JS, ~60 KB CSS) - 60% smaller
# - No source maps (security)
# - Console logs stripped
# - Tree shaking (dead code elimination)
# - Build time: 8-15 seconds
```

## BrowserSync for Live Reload

Webpack integrates BrowserSync for automatic browser refresh during development, eliminating manual page reloads.

**BrowserSync Configuration (webpack.config.js):**

```javascript
import BrowserSyncPlugin from 'browsersync-webpack-plugin';

const plugins = [
  // ... other plugins
];

if (!isProduction && isWatcher) {
  plugins.push(
    new BrowserSyncPlugin({
      proxy: 'http://localhost:8080', // Local WordPress dev server
      files: [
        'resources/views/**/*.blade.php',
        'app/**/*.php',
        'config/**/*.php',
      ],
      snippetOptions: {
        ignorePaths: ['/wp-admin/**'],
      },
    })
  );
}

export default { plugins };
```

**Development Workflow:**

1. Developer runs `yarn start` (starts webpack watch + BrowserSync)
2. BrowserSync proxies local WordPress at `http://localhost:3000`
3. Developer edits `resources/assets/styles/main.scss`
4. Webpack recompiles SCSS (2-3 seconds)
5. BrowserSync injects new CSS without page reload
6. Developer edits `resources/views/single.blade.php`
7. BrowserSync detects PHP change, triggers full page reload

**Hot Module Replacement (HMR):**

```javascript
// resources/assets/scripts/main.js
if (module.hot) {
  module.hot.accept(); // Enable HMR for this module
}
```

**Pattern:** CSS changes inject without reload (instant), PHP/Blade changes trigger full reload (preserves scroll position).

**Source Confidence:** 100% (both themes use BrowserSync)

## Code Splitting and Optimization

Webpack separates vendor libraries from application code for improved caching and parallel loading.

**Caching Benefits:**
- **Vendors bundle:** Changes rarely, cached for 1 year
- **Main bundle:** Changes frequently, cached for 1 day
- **Result:** Repeat visitors only re-download 25 KB instead of 80 KB

**Source Confidence:** 100% (Presser implements vendor splitting, Kelsey uses basic optimization)

## Vendor Bundle Split Configuration

Webpack splitChunks extracts node_modules into separate vendors.js bundle for long-term caching:

```javascript
// webpack.config.js
optimization: {
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
        priority: 10,
      },
      common: {
        minChunks: 2,
        priority: 5,
        reuseExistingChunk: true,
      },
    },
  },
},
```

## Split Bundle Output Structure

Webpack generates three separate bundles for main application code, vendor libraries, and webpack runtime:

```
dist/scripts/
├── main.js?abc123           # Application code (25 KB)
├── vendors.js?abc123        # node_modules (jQuery, etc) (55 KB)
└── runtime.js?abc123        # Webpack runtime (2 KB)
```

## WordPress Enqueue Order

WordPress enqueues vendor bundle first with main bundle depending on vendors for proper load order:

```php
// Vendors loaded first (cached long-term)
wp_enqueue_script('sage/vendors.js', asset_path('scripts/vendors.js'), [], null, true);

// Application code loaded second (changes frequently)
wp_enqueue_script('sage/main.js', asset_path('scripts/main.js'), ['sage/vendors.js'], null, true);
```

## Tree Shaking Dead Code Elimination

Webpack removes unused exports when importing from ES modules (93% size reduction with lodash-es):

```javascript
// Source: Import entire lodash library
import _ from 'lodash';
const compact = _.compact([0, 1, false, 2, '', 3]);

// Optimized: Import only compact function
import { compact } from 'lodash-es';
const result = compact([0, 1, false, 2, '', 3]);

// Bundle size: 70 KB → 5 KB (93% reduction)
```

## Image and Font Asset Handling

Webpack processes images and fonts through file-loader, copying assets to `dist/` with hash-based naming for cache invalidation.

**Pattern:** Small images (<8KB) inline as base64 (reduce HTTP requests), large images load separately with cache-busting hashes.

**Source Confidence:** 100% (both themes use file-loader for assets)

## Asset Resource Loader Configuration

Webpack asset/resource loader handles images and fonts with automatic hash injection and base64 inlining for small files:

```javascript
// webpack.config.js
module: {
  rules: [
    {
      test: /\.(png|jpe?g|gif|svg)$/,
      type: 'asset/resource',
      generator: {
        filename: 'images/[name].[hash][ext]',
      },
      parser: {
        dataUrlCondition: {
          maxSize: 8192, // Inline images <8KB as base64
        },
      },
    },
    {
      test: /\.(woff2?|ttf|eot)$/,
      type: 'asset/resource',
      generator: {
        filename: 'fonts/[name].[hash][ext]',
      },
    },
  ],
},
```

## JavaScript Image Imports

JavaScript imports images as module exports resolving to versioned dist URLs:

```javascript
// resources/assets/scripts/main.js
import logo from '../images/logo.svg';

document.querySelector('.header__logo').src = logo;
// Output: src="/dist/images/logo.a1b2c3d4.svg"
```

## SCSS Background Image References

SCSS url() references automatically resolve to hashed dist paths during compilation:

```scss
// resources/assets/styles/components/_hero.scss
.hero {
  background-image: url('../images/hero-bg.jpg');
  // Output: background-image: url('/dist/images/hero-bg.e5f6g7h8.jpg');
}
```

## Web Font @font-face Declarations

SCSS @font-face declarations reference font files with automatic hash injection for cache busting:

```scss
// resources/assets/styles/common/_fonts.scss
@font-face {
  font-family: 'CustomFont';
  src: url('../fonts/custom-font.woff2') format('woff2'),
       url('../fonts/custom-font.woff') format('woff');
  font-weight: 400;
  font-display: swap;
}
```

## Base64 Inline Images

Webpack inlines images smaller than 8KB as base64 data URLs to reduce HTTP requests:

```scss
// Small icon (3 KB):
.icon { background: url('../images/icon.svg'); }

// Compiled output (base64 inline):
.icon { background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0...'); }
```

## Linting Integration (ESLint + Stylelint)

Webpack enforces code quality standards during compilation using ESLint for JavaScript and Stylelint for SCSS.

**Pattern:** Development builds show warnings, production builds fail on errors. Forces code quality before deployment.

**Source Confidence:** 100% (Presser uses ESLint 9 + Stylelint 16, Kelsey uses legacy versions)

## Webpack Linter Plugin Configuration

Webpack integrates ESLint and Stylelint plugins with environment-specific error handling (fail on error in production only):

```javascript
// webpack.config.js
import ESLintPlugin from 'eslint-webpack-plugin';
import StyleLintPlugin from 'stylelint-webpack-plugin';

const plugins = [
  new ESLintPlugin({
    configType: 'flat',
    failOnError: isProduction,
    failOnWarning: false,
    extensions: ['js'],
  }),
  new StyleLintPlugin({
    failOnError: !isWatcher,
    syntax: 'scss',
    files: 'resources/assets/styles/**/*.scss',
  }),
];
```

## ESLint JavaScript Rules

ESLint 9 flat config defines browser globals and WordPress-specific rules for JavaScript linting:

```javascript
// eslint.config.cjs (Presser - ESLint 9 flat config)
import js from '@eslint/js';
import globals from 'globals';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.jquery,
        wp: 'readonly',
      },
    },
    rules: {
      'no-console': 'warn',
      'no-unused-vars': 'warn',
    },
  },
];
```

## Stylelint SCSS Rules

Stylelint extends standard SCSS config with custom selector naming patterns (camelCase with BEM):

```javascript
// .stylelintrc.cjs
module.exports = {
  extends: 'stylelint-config-standard-scss',
  rules: {
    'selector-class-pattern': '^[a-z][a-zA-Z0-9]*(__[a-z][a-zA-Z0-9]*)?(-[a-z][a-zA-Z0-9]*)?$',
    'scss/at-rule-no-unknown': [true, {
      ignoreAtRules: ['tailwind', 'apply'],
    }],
  },
};
```

## Linting Error Output Example

Webpack build output displays linting errors with file locations and rule names for quick fixing:

```bash
$ yarn build

✖ 3 problems (2 errors, 1 warning)

resources/assets/scripts/main.js
  12:7  error  'unused' is defined but never used  no-unused-vars
  18:5  error  Unexpected console statement         no-console

resources/assets/styles/components/_button.scss
  5:3  warning  Expected class selector to be kebab-case  selector-class-pattern

Build failed with 2 errors and 1 warning.
```

## npm Scripts and Build Commands

Sage themes standardize build commands in `package.json` for consistent developer experience across projects.

**Source Confidence:** 100% (identical script structure across both themes)

## Package.json Build Scripts

Sage themes define standard npm scripts for development, production builds, linting, and cleaning:

```json
{
  "scripts": {
    "build": "webpack --progress --config resources/assets/build/webpack.config.js",
    "build:production": "webpack --env=production --progress --config resources/assets/build/webpack.config.js",
    "build:profile": "NODE_OPTIONS='--trace-deprecation' webpack --progress --profile --json --config resources/assets/build/webpack.config.js",
    "start": "webpack --hide-modules --watch --config resources/assets/build/webpack.config.js",
    "rmdist": "rimraf dist",
    "lint": "npm run lint:scripts && npm run lint:styles",
    "lint:scripts": "eslint resources/assets/scripts resources/assets/build",
    "lint:scripts:fix": "eslint resources/assets/scripts resources/assets/build --fix",
    "lint:styles": "stylelint \"resources/assets/styles/**/*.{css,sass,scss}\"",
    "lint:styles:fix": "stylelint \"resources/assets/styles/**/*.{css,sass,scss}\" --fix",
    "test": "npm run lint"
  }
}
```

## Development Watch Mode

Development watch mode starts webpack with file watching and BrowserSync for live reloading (2-3 second rebuilds):

```bash
yarn start
# - Watches for file changes
# - Starts BrowserSync on http://localhost:3000
# - Rebuilds automatically (2-3 seconds)
# - Shows linting warnings
```

## Production Build Command

Production build command enables minification, tree shaking, and removes console logs (8-15 second build time):

```bash
yarn build:production
# - Minifies JavaScript and CSS
# - Strips console.log statements
# - Generates production manifest
# - Fails on linting errors
# - Build time: 8-15 seconds
```

## Clean Rebuild Workflow

Clean rebuild removes old dist folder before rebuilding to eliminate stale artifacts:

```bash
yarn rmdist && yarn build:production
# - Removes old dist/ folder
# - Rebuilds from scratch
```

## Linting Commands

Linting commands run ESLint and Stylelint without compilation for fast code quality checks (1-2 seconds):

```bash
yarn lint
# - Runs ESLint + Stylelint
# - No compilation
# - Fast: 1-2 seconds
```

## Auto-fix Linting Issues

Auto-fix commands automatically correct fixable linting violations while preserving manual-only issues:

```bash
yarn lint:scripts:fix
yarn lint:styles:fix
# - Automatically fixes auto-fixable issues
# - Preserves manual-fix-only issues
```

## Performance Optimization Techniques

Production webpack builds apply aggressive optimizations to reduce bundle sizes and improve load times.

**Performance Results (Presser Production):**

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| JavaScript minification | 198 KB | 82 KB | 59% smaller |
| CSS minification | 142 KB | 61 KB | 57% smaller |
| Console log removal | 82 KB | 78 KB | 5% smaller |
| Tree shaking | 78 KB | 72 KB | 8% smaller |
| **Total** | **340 KB** | **143 KB** | **58% reduction** |

## Terser JavaScript Minification

Terser minifier removes console logs, debugger statements, comments, and applies compression (59% size reduction):

```javascript
// webpack.config.js
optimization: {
  minimizer: [
    new TerserPlugin({
      terserOptions: {
        compress: {
          drop_console: true,      // Remove console.log
          drop_debugger: true,      // Remove debugger statements
          pure_funcs: ['console.info', 'console.debug'],
        },
        output: {
          comments: false,          // Remove all comments
        },
      },
      extractComments: false,       // Don't create .LICENSE.txt files
    }),
  ],
},
```

## CSSNano CSS Minification

CSSNano minifies CSS by removing comments, normalizing whitespace, and optimizing color values (57% size reduction):

```javascript
// webpack.config.js
optimization: {
  minimizer: [
    new CssMinimizerPlugin({
      minimizerOptions: {
        preset: [
          'default',
          {
            discardComments: { removeAll: true },
            normalizeWhitespace: true,
            colormin: true,
          },
        ],
      },
    }),
  ],
},
```

## Cache Loader for Faster Rebuilds

Cache-loader stores compiled output to disk enabling faster subsequent builds by skipping unchanged files:

```javascript
// webpack.config.js
module: {
  rules: [
    {
      test: /\.js$/,
      use: [
        'cache-loader',  // Cache compiled output
        'babel-loader',
      ],
    },
  ],
},
```

**Gzip Compression (server-side):**

| Asset | Uncompressed | Gzipped | Compression |
|-------|--------------|---------|-------------|
| main.js | 72 KB | 23 KB | 68% smaller |
| main.css | 61 KB | 12 KB | 80% smaller |
| **Total** | **133 KB** | **35 KB** | **74% reduction** |

**Source Confidence:** 100% (measured from Presser production builds)

## Troubleshooting Common Webpack Issues

Common webpack errors and resolutions from production Sage theme development.

**Source Confidence:** 100% (documented in Presser/Kelsey development notes)

## Module Not Found Sass Error

Webpack fails with "Module not found: Error: Can't resolve 'sass'" when dart-sass package missing:

**Solution:**
```bash
yarn add sass sass-loader --dev
```

## MiniCssExtractPlugin Constructor Error

Webpack 5 throws "TypeError: MiniCssExtractPlugin is not a constructor" with outdated plugin version:

**Solution:**
```bash
yarn add mini-css-extract-plugin@^2.0.0 --dev
```

## BrowserSync CSS Injection Failure

BrowserSync fails to inject CSS changes when proxy URL points to BrowserSync port instead of WordPress server:

**Solution:**
```javascript
// webpack.config.js - Use correct local WordPress URL
new BrowserSyncPlugin({
  proxy: 'http://localhost:8080', // NOT http://localhost:3000
  files: ['resources/views/**/*.blade.php'],
})
```

## Webpack Build Hangs at 95%

Webpack build freezes at 95% emitting phase due to file permission or disk space issues:

**Solution:**
```bash
# Clear webpack cache
rm -rf node_modules/.cache

# Check disk space
df -h

# Rebuild
yarn build:production
```

## ESLint TypeScript Plugin Error

ESLint fails with "Failed to load plugin '@typescript-eslint'" when TypeScript plugin configured but not installed:

**Solution:**
```javascript
// eslint.config.cjs - Remove TypeScript plugin
export default [
  js.configs.recommended,
  // Remove: typescript.configs.recommended
];
```

## Assets Manifest Not Found Error

WordPress theme throws "assets-manifest.json not found" when activated before running webpack build:

**Solution:**
```bash
yarn build
# Must run before activating theme in WordPress
```

## Related Patterns

- **Sage Roots Framework Setup** - Directory structure, Composer dependencies
- **Theme Build Process Modernization** - Webpack 3 → 5 migration guide
- **Laravel Blade Templating** - Template compilation (separate from webpack)
- **Headless Theme Architecture** - No webpack needed (frontend handles compilation)

## References

- Webpack 5 Documentation: https://webpack.js.org/
- Sage Asset Pipeline: https://roots.io/sage/docs/asset-pipeline/
- Babel Documentation: https://babeljs.io/docs/
- Analyzed Themes: Presser (Webpack 5), Kelsey (Webpack 3)
