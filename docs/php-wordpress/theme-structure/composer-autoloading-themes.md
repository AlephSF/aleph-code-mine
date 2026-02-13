---
title: "Composer PSR-4 Autoloading for WordPress Themes"
category: "theme-structure"
subcategory: "dependency-management"
tags: ["composer", "psr-4", "autoloading", "dependencies", "namespaces"]
stack: "php-wp"
priority: "medium"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "29%"
last_updated: "2026-02-12"
---

# Composer PSR-4 Autoloading for WordPress Themes

## Overview

Composer autoloading eliminates manual `require` statements by mapping namespaces to directories. **29% of analyzed themes** (4 of 14) use Composer with PSR-4 autoloading: all Sage framework themes (kelsey, presser, onboard, protools).

PSR-4 maps `App\Controllers\FrontPage` class to `app/Controllers/FrontPage.php` file automatically. Composer generates `vendor/autoload.php` that loads classes on demand.

**Key Benefits:**
- No manual `require` statements
- Namespace organization (`App\Controllers`, `App\Models`)
- Dependency management (Laravel components, plugins)
- Autoloading standards (PSR-4 specification)

## Composer Configuration

### composer.json Structure

```json
{
  "name": "roots/sage",
  "type": "wordpress-theme",
  "license": "MIT",
  "autoload": {
    "psr-4": {
      "App\\": "app/"
    }
  },
  "require": {
    "php": ">=7.1",
    "composer/installers": "~2.0",
    "illuminate/support": "^8.0",
    "roots/sage-lib": "dev-master",
    "soberwp/controller": "~2.1.0"
  },
  "require-dev": {
    "squizlabs/php_codesniffer": "^2.8.0"
  }
}
```

**Key Fields:**
- `autoload.psr-4`: Maps `App\` namespace to `app/` directory
- `require`: Production dependencies (Laravel, Sage lib, Controller)
- `require-dev`: Development dependencies (PHPCS)

### Installation

```bash
cd themes/sage
composer install
```

**Result:** Creates `vendor/` directory with:
- `vendor/autoload.php`: Autoloader entry point
- `vendor/composer/`: Autoload maps
- `vendor/{package}/`: Installed dependencies

## PSR-4 Autoloading

PSR-4 standard maps fully qualified class names to file paths based on namespace hierarchy.

### Mapping Rules

| Fully Qualified Class Name | File Path |
|----------------------------|-----------|
| `App\Controllers\FrontPage` | `app/Controllers/FrontPage.php` |
| `App\Controllers\App` | `app/Controllers/App.php` |
| `App\Models\Post` | `app/Models/Post.php` |
| `App\Utils\Helper` | `app/Utils/Helper.php` |

**Formula:** `{namespace}\{class}` → `{base_dir}/{class}.php`
- Base namespace: `App\`
- Base directory: `app/`
- Separator: `\` → `/`

### Example Class (app/Controllers/FrontPage.php)

```php
<?php

namespace App\Controllers;

use Sober\Controller\Controller;

class FrontPage extends Controller
{
    public function featuredPosts()
    {
        return get_posts(['numberposts' => 3]);
    }
}
```

**No require needed:** Composer autoloader loads class when referenced:

```php
// Autoloader loads App\Controllers\FrontPage from app/Controllers/FrontPage.php
$controller = new App\Controllers\FrontPage();
```

## Bootstrap (resources/functions.php)

Theme bootstrap loads Composer autoloader before using any namespaced classes.

```php
<?php

use Roots\Sage\Container;
use Roots\Sage\Config;

/**
 * Load Composer autoloader
 */
if (!class_exists('Roots\\Sage\\Container')) {
    if (!file_exists($composer = __DIR__.'/../vendor/autoload.php')) {
        wp_die('You must run <code>composer install</code> from Sage directory.');
    }
    require_once $composer;
}

/**
 * Load app files (now autoloaded via PSR-4)
 */
array_map(function ($file) {
    $file = "../app/{$file}.php";
    locate_template($file, true, true);
}, ['helpers', 'setup', 'filters', 'admin']);
```

**Error Handling:** Checks for `vendor/autoload.php`, shows error if missing (prevents "Class not found" fatal errors).

## Dependencies

Sage themes require Laravel components and specialized packages managed via Composer.

### Core Dependencies

```json
{
  "require": {
    "illuminate/support": "^8.0",
    "roots/sage-lib": "dev-master",
    "soberwp/controller": "~2.1.0"
  }
}
```

**illuminate/support:**
- Laravel Container (dependency injection)
- Collections (array manipulation)
- Helper functions (array_get, collect, etc.)

**roots/sage-lib:**
- Blade template engine
- Asset manifest loader
- Config loader

**soberwp/controller:**
- MVC controller layer
- Automatic variable binding to templates

### Development Dependencies

```json
{
  "require-dev": {
    "squizlabs/php_codesniffer": "^2.8.0",
    "roots/sage-installer": "dev-master"
  }
}
```

**Not loaded in production:** `require-dev` packages excluded when running `composer install --no-dev` on production server.

## Namespace Organization

PSR-4 enables organized code structure with namespaces matching directory hierarchy.

### Directory Structure

```
app/
├── Controllers/              # App\Controllers
│   ├── App.php              # App\Controllers\App
│   ├── FrontPage.php        # App\Controllers\FrontPage
│   └── SinglePost.php       # App\Controllers\SinglePost
├── Models/                   # App\Models (if used)
│   └── Post.php             # App\Models\Post
├── Utils/                    # App\Utils
│   └── Helper.php           # App\Utils\Helper
├── setup.php                 # Functions (no namespace)
├── filters.php               # Functions (no namespace)
└── helpers.php               # Functions (no namespace)
```

**Namespace Examples:**

```php
// app/Controllers/FrontPage.php
namespace App\Controllers;

class FrontPage { }

// app/Models/Post.php
namespace App\Models;

class Post { }

// app/Utils/Helper.php
namespace App\Utils;

class Helper { }
```

## Using Autoloaded Classes

### With Full Namespace

```php
$controller = new \App\Controllers\FrontPage();
$helper = new \App\Utils\Helper();
```

### With use Statement

```php
use App\Controllers\FrontPage;
use App\Utils\Helper;

$controller = new FrontPage();
$helper = new Helper();
```

### In Blade Templates

```blade
<h1>{{ App\title() }}</h1>

{{ App\Utils\Helper::formatDate($date) }}
```

## When to Use Composer Autoloading

**Use Composer When:**
- Using Sage framework (required)
- Need dependency management (Laravel components)
- Building MVC theme (Controllers, Models)
- Team familiar with modern PHP (namespaces, PSR-4)

**Use Manual require When:**
- Traditional theme (no namespaces)
- Simple site (<20 files)
- Team unfamiliar with Composer
- Hosting lacks Composer support

**Analyzed Adoption:** 29% of themes use Composer (4 of 14), all Sage framework.

## Related Patterns

- **Sage Framework:** See `sage-framework-structure.md` for full Composer setup
- **MVC Controllers:** See `mvc-controllers-pattern.md` for namespace usage

## References

- **PSR-4:** https://www.php-fig.org/psr/psr-4/
- **Composer:** https://getcomposer.org/
- **Sage Composer:** https://roots.io/sage/docs/composer/
