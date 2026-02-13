---
title: "PHPCS WordPress VIP Configuration"
category: "wordpress-security"
subcategory: "code-standards"
tags: ["phpcs", "vip", "code-quality", "wordpress-vip-minimum", "psr2"]
stack: "php-wp"
priority: "high"
audience: "backend"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-12"
---

## PHP CodeSniffer for WordPress VIP

WordPress VIP projects use PHP_CodeSniffer (PHPCS) with WordPressVIPMinimum and WordPress-VIP-Go rulesets for automated code standard enforcement. PHPCS validates security patterns, coding style, performance optimizations, and VIP platform compatibility before deployment.

**Required rulesets:**
- **WordPressVIPMinimum:** VIP-specific security and performance rules
- **WordPress-VIP-Go:** VIP Go platform rules
- **PSR2:** PHP-FIG coding standard (with WordPress modifications)

**Configuration file:** `phpcs.xml` (repository root)

```xml
<?xml version="1.0"?>
<ruleset name="Aleph-WP-Standards">
	<description>PHP_CodeSniffer standard for WordPress and Sage. VIP Ready.</description>

	<rule ref="WordPressVIPMinimum">
		<exclude name="WordPressVIPMinimum.Files.IncludingFile.IncludingFile" />
	</rule>

	<rule ref="WordPress-VIP-Go" />

	<rule ref="PSR2">
		<exclude name="Generic.WhiteSpace.DisallowTabIndent"/>
	</rule>
</ruleset>
```

## WordPressVIPMinimum Ruleset

WordPressVIPMinimum enforces VIP-specific code quality, security, and performance standards. The ruleset detects disallowed functions, uncached queries, security vulnerabilities, and performance anti-patterns.

**Common WordPressVIPMinimum rules:**
- **DisallowedFunctions:** Detects `eval()`, `file_get_contents()` (remote), `curl_exec()`, `session_start()`
- **UncachedDBQueries:** Warns on `get_posts()` without cache integration
- **DirectDatabaseQuery:** Requires `$wpdb->prepare()` for custom SQL
- **CacheValueOverride:** Detects object cache manipulation
- **SlowDBQueries:** Warns on `post__not_in`, `tax_query` with large arrays

```php
// ❌ Disallowed: file_get_contents for remote URLs
$response = file_get_contents( 'https://api.example.com/data' );

// ✅ VIP-safe alternative
$response = wpcom_vip_file_get_contents( 'https://api.example.com/data' );

// ❌ Disallowed: eval() usage
eval( $user_code ); // Critical security risk!

// ✅ Alternative: Use WordPress hooks/filters
apply_filters( 'custom_filter', $data );
```

## WordPress-VIP-Go Ruleset

WordPress-VIP-Go ruleset enforces VIP Go platform compatibility, including caching strategies, file system restrictions, and VIP helper function usage.

**Common WordPress-VIP-Go rules:**
- **FileSystemWritesDisallow:** Prevent file writes (uploads handled by VIP platform)
- **VIPRestrictedFunctions:** Enforce VIP helper functions (wpcom_vip_*, vip_safe_*)
- **SessionsUsage:** Disallow `session_start()` (incompatible with Varnish)
- **RestrictedPatternsDetect:** Detect problematic code patterns
- **AlwaysReturnDetect:** Ensure functions return values

```php
// ❌ Disallowed: Direct file writes
file_put_contents( '/tmp/cache.txt', $data );

// ✅ VIP alternative: Use object cache
wp_cache_set( 'cache_key', $data, 'group', 3600 );

// ❌ Disallowed: session_start()
session_start();
$_SESSION['user_id'] = $user_id;

// ✅ VIP alternative: Use transients
set_transient( 'user_session_' . $user_id, $session_data, 3600 );
```

## PSR2 with WordPress Modifications

WordPress VIP combines PSR-2 coding standard with WordPress-specific tab indentation and brace style modifications. The hybrid approach maintains PSR-2 structural benefits while respecting WordPress conventions.

**WordPress modifications to PSR-2:**
- **Tab indentation:** 4-space width tabs (not spaces)
- **K&R brace style:** Opening brace on same line for functions
- **Class braces:** Opening brace on same line
- **Namespace imports:** Relaxed spacing after `use` statements

```xml
<rule ref="PSR2">
	<exclude name="Generic.WhiteSpace.DisallowTabIndent"/>
	<exclude name="PSR2.Classes.ClassDeclaration.OpenBraceNewLine"/>
</rule>

<rule ref="Generic.WhiteSpace.DisallowSpaceIndent"/>

<rule ref="Generic.WhiteSpace.ScopeIndent">
	<properties>
		<property name="indent" value="4"/>
		<property name="tabIndent" value="true"/>
	</properties>
</rule>

<rule ref="Generic.Functions.OpeningFunctionBraceKernighanRitchie"/>
<rule ref="Generic.Classes.OpeningBraceSameLine"/>
```

**Coding style example:**
```php
// ✅ WordPress VIP style: K&R braces, tabs
class MyClass {
	public function myFunction() {
		if ( $condition ) {
			return true;
		}
		return false;
	}
}
```

## PHPCS Configuration Structure

WordPress VIP `phpcs.xml` specifies scan targets, exclusion patterns, argument flags, and ruleset customizations. Configuration scans only custom code, excluding vendor libraries, node_modules, and WordPress core.

```xml
<ruleset name="Aleph-WP-Standards">
	<description>PHP_CodeSniffer standard for WordPress and Sage. VIP Ready.</description>

	<config name="warning-severity" value="5" />

	<!-- Scan these files -->
	<file>themes/custom-theme</file>
	<file>client-mu-plugins</file>

	<!-- CLI arguments -->
	<arg value="-colors"/>
	<arg name="extensions" value="php"/>
	<arg value="s"/> <!-- Show sniff codes -->
	<arg value="p"/> <!-- Show progress -->

	<!-- Exclusions -->
	<exclude-pattern>*/node_modules/*</exclude-pattern>
	<exclude-pattern>*/vendor/*</exclude-pattern>
	<exclude-pattern>*/uploads/*</exclude-pattern>
	<exclude-pattern>plugins/*</exclude-pattern>
</ruleset>
```

**Configuration sections:**
- `<file>`: Directories to scan (custom themes, mu-plugins)
- `<arg>`: CLI flags (colors, progress, sniff codes)
- `<exclude-pattern>`: Ignored directories (vendor, node_modules)
- `<rule>`: Active rulesets and overrides

## Blade Template Exclusions

WordPress VIP projects using Laravel Blade templates exclude `resources/views/` from strict PHPCS rules. Blade syntax conflicts with PHP formatting rules, requiring targeted exclusions.

```xml
<!-- Allow php files without any PHP in them -->
<rule ref="Internal.NoCodeFound">
  <exclude-pattern>*/resources/views/*</exclude-pattern>
</rule>

<!-- Allow braces on same line for named functions -->
<rule ref="Squiz.Functions.MultiLineFunctionDeclaration.BraceOnSameLine">
  <exclude-pattern>*/resources/views/*</exclude-pattern>
</rule>

<!-- Allow multiple PHP statements in the same line -->
<rule ref="Generic.Formatting.DisallowMultipleStatements.SameLine">
  <exclude-pattern>*/resources/views/*</exclude-pattern>
</rule>

<!-- Allow PHP closing tags -->
<rule ref="PSR2.Files.ClosingTag.NotAllowed">
  <exclude-pattern>*/resources/views/*</exclude-pattern>
</rule>
```

**Blade template patterns:**
```blade
{{-- Blade templates use different syntax --}}
@if($condition)
    <div>{{ $variable }}</div>
@endif

@foreach($items as $item)
    <p>{{ $item->name }}</p>
@endforeach
```

## Running PHPCS Validation

WordPress VIP projects run PHPCS validation locally (pre-commit) and in CI/CD pipelines (pre-deployment). Validation catches security vulnerabilities, coding standard violations, and VIP incompatibilities.

```bash
# Run PHPCS on all configured files
vendor/bin/phpcs

# Run PHPCS on specific directory
vendor/bin/phpcs themes/custom-theme/

# Run PHPCS with detailed output
vendor/bin/phpcs -v themes/custom-theme/

# Run PHPCS with progress indicator
vendor/bin/phpcs -p themes/custom-theme/

# Auto-fix violations where possible
vendor/bin/phpcbf themes/custom-theme/
```

**CI/CD integration:**
```yaml
# .github/workflows/phpcs.yml
name: PHPCS
on: [push, pull_request]
jobs:
  phpcs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: composer install
      - name: Run PHPCS
        run: vendor/bin/phpcs
```

## PHPCS Exclusion Patterns

WordPress VIP `phpcs.xml` excludes specific rules for third-party code, legacy patterns, and framework-specific requirements. Targeted exclusions prevent false positives without disabling entire rulesets.

```xml
<!-- Exclude specific sniff from ruleset -->
<rule ref="WordPressVIPMinimum">
	<exclude name="WordPressVIPMinimum.Files.IncludingFile.IncludingFile" />
	<exclude name="Generic.Formatting.MultipleStatementAlignment.IncorrectWarning" />
	<exclude name="WordPress.Arrays.MultipleStatementAlignment.DoubleArrowNotAligned" />
</rule>

<!-- Exclude entire directories from all rules -->
<exclude-pattern>client-mu-plugins/plugin-loader.php</exclude-pattern>
<exclude-pattern>vip-config/vip-config.php</exclude-pattern>
```

**Common exclusions:**
- `plugin-loader.php`: Conditional plugin loading bypasses include rules
- `vip-config.php`: Early bootstrap excludes WordPress function usage
- `vendor/`: Third-party libraries (own coding standards)

## Severity Levels and Warnings

WordPress VIP PHPCS configuration uses warning severity levels to prioritize violations. Errors block deployment, warnings require review, and info messages provide suggestions.

```xml
<!-- Set warning severity threshold (1-8) -->
<config name="warning-severity" value="5" />

<!-- Allow warnings below severity 5 to pass -->
```

**Severity levels:**
- **8-10:** Errors (block deployment)
- **5-7:** Warnings (require review)
- **1-4:** Info (suggestions)

**Example violations:**
```php
// Error (severity 10): eval() usage
eval( $code ); // WordPressVIPMinimum.Functions.RestrictedFunctions.eval_eval

// Warning (severity 6): Uncached query
get_posts( array('posts_per_page' => 100) ); // WordPressVIPMinimum.Performance.NoPaging

// Info (severity 3): Alignment preference
$array = array(
    'key1'    => 'value1',
    'key2' => 'value2', // Generic.Formatting.MultipleStatementAlignment
);
```

## VIP Code Review Integration

WordPress VIP automated code review runs PHPCS during pull request creation, blocking merges for critical violations. Integration catches security issues, performance anti-patterns, and VIP incompatibilities before production deployment.

**VIP Code Review workflow:**
1. Developer creates pull request
2. VIP Code Review runs PHPCS automatically
3. Violations appear as PR comments
4. Critical errors block merge
5. Developer fixes violations, re-runs review

**Example PR comment:**
```
FILE: themes/custom-theme/functions.php
----------------------------------------------
LINE 42: ERROR: eval() is highly discouraged, extremely dangerous,
         and slow to execute. (WordPressVIPMinimum.Functions.RestrictedFunctions.eval_eval)
```

## PHPCS IDE Integration

WordPress VIP developers integrate PHPCS with IDEs (VSCode, PHPStorm) for real-time violation feedback. IDE integration shows violations inline, provides quick fixes, and enforces standards during development.

**VSCode integration (phpcs extension):**
```json
{
  "phpcs.enable": true,
  "phpcs.standard": "phpcs.xml",
  "phpcs.showWarnings": true,
  "phpcs.showSources": true
}
```

**PHPStorm integration:**
```
Settings → PHP → Quality Tools → PHP_CodeSniffer
- Configuration: Browse to /vendor/bin/phpcs
- Coding standard: Custom → Browse to phpcs.xml
- Show warnings: Enabled
```

**Real-time feedback:**
- Red underline: Errors
- Yellow underline: Warnings
- Tooltip: Violation message + sniff code
