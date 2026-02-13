---
title: "Build Tool Configuration: webpack, Laravel Mix, Gulp"
category: "theme-structure"
subcategory: "build-tools"
tags: ["webpack", "laravel-mix", "gulp", "build-pipeline", "compilation"]
stack: "php-wp"
priority: "medium"
audience: "frontend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "57%"
last_updated: "2026-02-12"
---

# Build Tool Configuration: webpack, Laravel Mix, Gulp

## Overview

Build tools automate asset compilation, minification, and optimization. **57% of analyzed themes** (8 of 14) use build tools: webpack (5 themes), Laravel Mix (1 theme), Gulp (1 theme), manual (1 theme).

**webpack** dominates (36% of all themes) with Sage framework adoption. **Laravel Mix** simplifies webpack config (7% adoption). **Gulp** less common (7%), older pattern being replaced by webpack.

## webpack Configuration (36% - 5 themes)

webpack bundles JavaScript, compiles SCSS, optimizes images, generates asset manifest with cache-busting hashes.

### Basic webpack.config.js

```javascript
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  mode: isProduction ? 'production' : 'development',
  entry: './resources/assets/scripts/main.js',
  output: {
    path: path.resolve(__dirname, '../../dist'),
    filename: isProduction
      ? 'scripts/main_[contenthash:8].js'
      : 'scripts/main.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'sass-loader',
        ],
      },
    ],
  },
  plugins: [
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: isProduction
        ? 'styles/main_[contenthash:8].css'
        : 'styles/main.css',
    }),
  ],
};
```

**Key Features:**
- `mode`: Production minifies automatically
- `[contenthash:8]`: 8-character hash for cache-busting
- `MiniCssExtractPlugin`: Extracts CSS to separate files
- `CleanWebpackPlugin`: Removes old builds before new build

### package.json Scripts

```json
{
  "scripts": {
    "start": "webpack --watch",
    "build": "webpack",
    "build:production": "cross-env NODE_ENV=production webpack"
  }
}
```

**Usage:**
- `yarn start`: Development watch mode
- `yarn build`: Development build (no minification)
- `yarn build:production`: Production build (minified + optimized)

## Laravel Mix (7% - 1 theme)

Laravel Mix wraps webpack with simpler API. Single configuration file (`webpack.mix.js`) replaces complex webpack config.

### webpack.mix.js Example (airbnb-careers)

```javascript
const mix = require('laravel-mix');

mix.js('src/app.js', 'dist/')
   .sass('src/app.scss', 'dist/')
   .options({
     processCssUrls: false,  // Don't process url() in CSS
   })
   .version();  // Automatic versioning

if (!mix.inProduction()) {
  mix.sourceMaps();  // Source maps in development
}
```

**Advantages:**
- Simpler API (`mix.js()` vs webpack config)
- Built-in versioning (`mix.version()`)
- Automatic BrowserSync setup
- Less configuration overhead

### package.json Scripts

```json
{
  "scripts": {
    "dev": "npm run development",
    "development": "cross-env NODE_ENV=development node_modules/webpack/bin/webpack.js --progress --config=node_modules/laravel-mix/setup/webpack.config.js",
    "watch": "npm run development -- --watch",
    "prod": "npm run production",
    "production": "cross-env NODE_ENV=production node_modules/webpack/bin/webpack.js --config=node_modules/laravel-mix/setup/webpack.config.js"
  }
}
```

## Gulp (7% - 1 theme)

Gulp task runner for asset compilation. Less common in modern themes, replaced by webpack/Mix.

### gulpfile.js Example (pressbnb)

```javascript
const gulp = require('gulp');
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const rename = require('gulp-rename');

// Compile SCSS to CSS
gulp.task('styles', function() {
  return gulp.src('css/source/**/*.scss')
    .pipe(sass({ outputStyle: 'compressed' }))
    .pipe(autoprefixer({ browsers: ['last 2 versions'] }))
    .pipe(gulp.dest('css'));
});

// Concatenate and minify JavaScript
gulp.task('scripts', function() {
  return gulp.src('js/source/**/*.js')
    .pipe(concat('scripts.js'))
    .pipe(gulp.dest('js'))
    .pipe(rename('scripts.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('js'));
});

// Watch files
gulp.task('watch', function() {
  gulp.watch('css/source/**/*.scss', ['styles']);
  gulp.watch('js/source/**/*.js', ['scripts']);
});

// Default task
gulp.task('default', ['styles', 'scripts']);
```

**Usage:**
- `gulp`: Run default task (styles + scripts)
- `gulp watch`: Watch files for changes
- `gulp styles`: Compile SCSS only
- `gulp scripts`: Compile JS only

**Limitations:**
- No tree-shaking (includes all code)
- Manual versioning (no automatic cache-busting)
- More verbose configuration than Mix

## Comparison

| Feature | webpack | Laravel Mix | Gulp |
|---------|---------|-------------|------|
| **Adoption** | 36% (5 themes) | 7% (1 theme) | 7% (1 theme) |
| **Configuration** | Complex | Simple | Medium |
| **Cache-Busting** | Automatic (`[contenthash]`) | Automatic (`mix.version()`) | Manual |
| **Tree-Shaking** | Yes | Yes (via webpack) | No |
| **Code Splitting** | Yes | Yes (via webpack) | No |
| **Learning Curve** | Steep | Gentle | Medium |
| **Build Speed** | Fast | Fast (webpack) | Slow (stream-based) |
| **Hot Reload** | Yes (BrowserSync) | Yes (built-in) | Manual (BrowserSync) |

**Recommendation:** Use Laravel Mix for new themes (simpler than webpack, same power). Use webpack if need advanced config. Avoid Gulp for new projects.

## Analyzed Distribution

**Build Tool Usage:**
- webpack: 5 themes (kelsey, presser, onboard, protools, airbnb-careers partial)
- Laravel Mix: 1 theme (airbnb-careers)
- Gulp: 1 theme (pressbnb)
- None (manual): 6 themes (traditional themes)

**Total with build tools:** 8/14 (57%)
**Total without:** 6/14 (43%)

## Related Patterns

- **Asset Management:** See `asset-management-strategies.md` for enqueue patterns
- **Sage Framework:** See `sage-framework-structure.md` for integrated webpack

## References

- **webpack:** https://webpack.js.org/
- **Laravel Mix:** https://laravel-mix.com/
- **Gulp:** https://gulpjs.com/
