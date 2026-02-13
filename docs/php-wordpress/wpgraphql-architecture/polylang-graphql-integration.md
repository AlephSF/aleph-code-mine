---
title: "Polylang GraphQL Integration for Multilingual Content"
category: "wpgraphql-architecture"
subcategory: "multilingual"
tags: ["wpgraphql", "polylang", "multilingual", "i18n", "translations"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "advanced"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## Overview

Polylang Pro integrates with WPGraphQL through the wp-graphql-polylang plugin, exposing language-specific content queries and mutations via GraphQL API. Plugin registers `language` and `languages` query parameters on all post type connections, enabling headless frontends to filter content by language code without REST API requests. Airbnb Policy site serves 215+ language directories through GraphQL queries that return translated post data, taxonomy terms, and ACF field values based on language parameter, eliminating need for separate API endpoints per language. Integration requires manual patch for hyphenated language codes (en-au, pt-br) that violate GraphQL naming constraints.

## Language Query Parameters

wp-graphql-polylang automatically adds language filtering to all GraphQL post type queries through connection where args.

### Single Language Filter
```graphql
query GetEnglishPosts {
  posts(where: {language: EN}) {
    nodes {
      id
      title
      content
      language {
        code
        name
      }
    }
  }
}
```

### Multiple Language Filter
```graphql
query GetMultilingualPosts {
  posts(where: {languages: [EN, ES, FR]}) {
    nodes {
      id
      title
      language {
        code
      }
    }
  }
}
```

**Generated Schema:**
```graphql
input RootQueryToPostConnectionWhereArgs {
  language: LanguageCodeFilterEnum
  languages: [LanguageCodeEnum!]
  # ... other where args
}

enum LanguageCodeFilterEnum {
  ALL
  EN
  ES
  FR
  # ... all configured languages
}
```

**Source:** airbnb/plugins/wp-graphql-polylang/src/PostObject.php (lines 64-79)

## Language Field on Content Types

All GraphQL content types receive language field exposing post's current language metadata.

```graphql
type Post {
  id: ID!
  title: String
  content: String
  language: Language!
  translations: [Post]
  # ... other fields
}

type Language {
  code: LanguageCodeEnum!
  locale: String!
  name: String!
  slug: String!
  defaultLanguage: Boolean
}
```

### Query Post with Language
```graphql
query GetPostLanguage {
  post(id: "cG9zdDoxMjM=") {
    title
    language {
      code      # EN
      locale    # en_US
      name      # English
    }
  }
}
```

**Language Object Fields:**
- `code`: GraphQL enum value (EN, ES, FR)
- `locale`: WordPress locale (en_US, es_ES)
- `name`: Human-readable name
- `slug`: URL slug for language switcher
- `defaultLanguage`: Boolean indicating site default

**Source:** wp-graphql-polylang registers Language type automatically

## Translation Relationships

wp-graphql-polylang exposes translation relationships enabling language switcher functionality in headless frontends.

```graphql
query GetPostWithTranslations {
  post(id: "cG9zdDoxMjM=", idType: DATABASE_ID) {
    databaseId
    title
    language {
      code
    }
    translations {
      databaseId
      title
      language {
        code
        name
      }
      uri
    }
  }
}
```

**Response Structure:**
```json
{
  "data": {
    "post": {
      "databaseId": 123,
      "title": "Hello World",
      "language": {"code": "EN"},
      "translations": [
        {
          "databaseId": 124,
          "title": "Hola Mundo",
          "language": {"code": "ES", "name": "Español"},
          "uri": "/es/hello-world"
        },
        {
          "databaseId": 125,
          "title": "Bonjour le monde",
          "language": {"code": "FR", "name": "Français"},
          "uri": "/fr/hello-world"
        }
      ]
    }
  }
}
```

**Use Case:** Build language switcher dropdown showing available translations with localized URLs

## Language Mutations

GraphQL mutations support language assignment when creating or updating posts through `language` input field.

### Create Post in Specific Language
```graphql
mutation CreateSpanishPost {
  createPost(
    input: {
      title: "Nuevo Post"
      content: "Contenido en español"
      language: ES
      status: PUBLISH
    }
  ) {
    post {
      id
      title
      language {
        code
      }
    }
  }
}
```

### Update Post Language
```graphql
mutation ChangePostLanguage {
  updatePost(
    input: {
      id: "cG9zdDoxMjM="
      language: FR
    }
  ) {
    post {
      id
      language {
        code
      }
    }
  }
}
```

**Implementation Pattern:**
```php
function __action_graphql_post_object_mutation_update_additional_data(
  $post_id, $input, $post_type_object, $mutation_name
) {
  if (isset($input['language'])) {
    pll_set_post_language($post_id, $input['language']);
  } elseif (substr($mutation_name, 0, 6) === 'create') {
    // Set default language on create if not specified
    pll_set_post_language($post_id, pll_default_language());
  }
}
```

**Source:** wp-graphql-polylang/src/PostObject.php (lines 52-66)

## Hyphenated Language Code Patch

wp-graphql-polylang v1.0-1.2 contains bug preventing hyphenated language codes from working in GraphQL due to enum naming constraints.

### The Problem
```graphql
# Polylang language code: en-au
# GraphQL enum generated: EN-AU (INVALID)
# Error: Names must only contain [_a-zA-Z0-9] but "EN-AU" does not.
```

### Required Manual Patch
```php
// File: wp-content/plugins/wp-graphql-polylang/src/PolylangTypes.php
// Function: PolylangTypes::__action_graphql_register_types()

// ❌ Original code (line ~45):
$language_codes[strtoupper($lang)] = $lang;

// ✅ Fixed code:
$language_codes[strtoupper(str_replace('-', '_', $lang))] = $lang;
```

**Result:**
```graphql
# Before patch: EN-AU (invalid GraphQL enum)
# After patch:  EN_AU (valid GraphQL enum)

query GetAustralianEnglish {
  posts(where: {language: EN_AU}) {
    nodes {
      title
    }
  }
}
```

**Affected Languages:**
- en-au → EN_AU
- en-gb → EN_GB
- pt-br → PT_BR
- zh-cn → ZH_CN
- Any hyphenated language code

**Tracking:** GitHub issue https://github.com/valu-digital/wp-graphql-polylang/issues/80

**Source:** airbnb/plugins/airbnb-policy-custom-mods/airbnb-policy-custom-mods.php (lines 19-30, documented in code comments)

## ACF Field Translation

ACF fields respect Polylang translation settings when exposed to GraphQL, returning language-specific values.

### ACF Translation Configuration
```json
{
  "key": "field_hero_title",
  "label": "Hero Title",
  "name": "hero_title",
  "type": "text",
  "translations": "translate",
  "show_in_graphql": 1,
  "graphql_field_name": "heroTitle"
}
```

**Translation Options:**
- `"translate"` - Different value per language
- `"copy_once"` - Copied on translation creation, then independent
- `null` - Same value across all languages

### Query Translated ACF Fields
```graphql
query GetTranslatedHero($lang: LanguageCodeEnum!) {
  pages(where: {language: $lang}, first: 1) {
    nodes {
      title
      heroFields {
        heroTitle    # Returns translated value
        heroSubtitle
      }
    }
  }
}
```

**Variables:**
```json
{"lang": "ES"}
```

**Response:** Returns Spanish ACF field values if `translations: "translate"` configured

## Taxonomy Term Translation

Polylang translates taxonomy terms (categories, tags, custom taxonomies) with GraphQL exposing term relationships per language.

```graphql
query GetCategoriesInSpanish {
  categories(where: {language: ES}) {
    nodes {
      id
      name
      slug
      language {
        code
      }
      translations {
        name
        slug
        language {
          code
        }
      }
    }
  }
}
```

**Term Translation Behavior:**
- Terms must be manually translated in Polylang UI
- Each language gets separate term_id
- GraphQL queries return only terms matching language filter
- `translations` field shows equivalent terms in other languages

**Use Case:** Navigation menus, category filters, tag clouds localized per language

## Root Query Language Filtering

All content types automatically receive language filtering without additional configuration.

```php
// Automatically registered by wp-graphql-polylang
register_graphql_fields('RootQueryToContentNodeConnectionWhereArgs', [
  'language' => [
    'type' => 'LanguageCodeFilterEnum',
    'description' => 'Filter content nodes by language code',
  ],
  'languages' => [
    'type' => ['list_of' => ['non_null' => 'LanguageCodeEnum']],
    'description' => 'Filter content nodes by one or more languages',
  ],
]);
```

**Applied To:**
- Posts: `posts(where: {language: EN})`
- Pages: `pages(where: {language: FR})`
- Custom Post Types: `localPages(where: {language: ES})`
- Media: `mediaItems(where: {language: DE})`
- All CPTs with `pll_is_translated_post_type() === true`

**Source:** wp-graphql-polylang/src/PostObject.php (lines 69-91)

## Default Language Behavior

Queries without language parameter return content in site default language configured in Polylang settings.

```graphql
# No language specified
query GetDefaultLanguagePosts {
  posts(first: 10) {
    nodes {
      title
      language {
        code
        defaultLanguage  # true for default language
      }
    }
  }
}
```

**Default Language Detection:**
```php
$default_lang = pll_default_language(); // Returns: 'en', 'es', etc.

// Query automatically filters to default if no language specified
// Equivalent to: posts(where: {language: EN})
```

**Configuration Location:** WordPress Admin → Languages → Settings → Default Language

## Menu Localization

Polylang localizes WordPress menus with wp-graphql-polylang exposing menu items per language.

```graphql
query GetLocalizedMenu($lang: LanguageCodeEnum!) {
  menu(id: "primary", idType: SLUG) {
    menuItems(where: {language: $lang}) {
      nodes {
        id
        label
        url
        path
        language {
          code
        }
      }
    }
  }
}
```

**Menu Behavior:**
- Menus themselves are language-agnostic
- Menu items (links) are language-specific
- Same menu slug contains different items per language
- GraphQL filters menu items by language parameter

**Source:** wp-graphql-polylang/src/MenuItem.php

## String Translations (Polylang Strings)

Polylang's string translation feature for theme/plugin strings NOT automatically exposed to GraphQL.

### Register Translatable Strings
```php
// Register strings for translation
pll_register_string('footer_copyright', 'Copyright 2026 Company Name');
pll_register_string('contact_cta', 'Contact Us Today');
```

### Custom GraphQL Field for Strings
```php
// Must manually expose strings to GraphQL
add_action('graphql_register_types', function() {
  register_graphql_field('RootQuery', 'translatedStrings', [
    'type' => 'TranslatedStrings',
    'resolve' => function($source, $args, $context) {
      $lang = $args['language'] ?? pll_current_language();

      return [
        'footerCopyright' => pll__('footer_copyright', $lang),
        'contactCta' => pll__('contact_cta', $lang),
      ];
    },
  ]);
});
```

**Note:** Requires custom GraphQL type registration, not handled by wp-graphql-polylang out-of-box

**Source:** airbnb/plugins/wp-graphql-polylang/src/StringsTranslations.php (reference implementation)

## Common Integration Issues

### Issue: Language Enum Not Appearing
**Cause:** Post type not registered with Polylang
```php
// ❌ Missing: Post type not translated
register_post_type('plc_local_pages', $args);
// Polylang doesn't know to translate this CPT

// ✅ Fixed: Register with Polylang
register_post_type('plc_local_pages', $args);
pll_register_post_type('plc_local_pages');
```

### Issue: GraphQL Returns All Languages
**Cause:** Missing language parameter in query
```graphql
# ❌ Returns posts in all languages mixed
query GetPosts {
  posts {
    nodes { title }
  }
}

# ✅ Filters to specific language
query GetEnglishPosts {
  posts(where: {language: EN}) {
    nodes { title }
  }
}
```

### Issue: Hyphenated Language Code Error
**Symptom:** `GraphQLError: Names must only contain [_a-zA-Z0-9] but "EN-AU" does not`

**Fix:** Apply manual patch to PolylangTypes.php (see Hyphenated Language Code Patch section above)

### Issue: ACF Fields Not Translated
**Cause:** ACF field translation setting not configured
```json
// ❌ Field not set to translate
{
  "name": "hero_title",
  "translations": null  // Not translated
}

// ✅ Field configured for translation
{
  "name": "hero_title",
  "translations": "translate"
}
```

## Testing Multilingual Queries

### Test Language Filtering
```graphql
query TestLanguageFilter {
  allLanguages: posts(first: 3) {
    nodes {
      title
      language { code }
    }
  }

  englishOnly: posts(first: 3, where: {language: EN}) {
    nodes {
      title
      language { code }
    }
  }

  multiLanguage: posts(first: 3, where: {languages: [ES, FR]}) {
    nodes {
      title
      language { code }
    }
  }
}
```

### Test Translation Relationships
```graphql
query TestTranslations {
  post(id: "123", idType: DATABASE_ID) {
    title
    language { code }
    translations {
      title
      language { code }
      uri
    }
  }
}
```

**Expected:** Original post + translated versions with localized URIs

### Test Menu Localization
```graphql
query TestMenuTranslation {
  englishMenu: menu(id: "primary", idType: SLUG) {
    menuItems(where: {language: EN}) {
      nodes { label }
    }
  }

  spanishMenu: menu(id: "primary", idType: SLUG) {
    menuItems(where: {language: ES}) {
      nodes { label }
    }
  }
}
```

**Verification:** English and Spanish menus return different labels for same menu location
