#!/usr/bin/env python3
"""
RAG Documentation Validator

Validates markdown documentation files against the RAG quality specification.
Checks frontmatter, section lengths, structural issues, and naming conventions.

Usage:
    python validate.py [--docs-dir PATH] [--json output.json] [--verbose]
"""

import os
import re
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


# Validation constants
MAX_SECTION_LENGTH = 1500
STUB_LINE_COUNT = 80
OVERSIZED_LINE_COUNT = 600
CODE_BLOCK_LONG_THRESHOLD = 10

# Enum values for frontmatter validation
VALID_STACKS = {'js-nextjs', 'sanity', 'php-wp', 'cross-stack'}
VALID_PRIORITIES = {'high', 'medium', 'low'}
VALID_AUDIENCES = {'frontend', 'backend', 'fullstack'}
VALID_COMPLEXITIES = {'beginner', 'intermediate', 'advanced'}
VALID_DOC_TYPES = {'standard', 'guide', 'reference', 'decision'}

# Pronoun patterns to detect at section starts
PRONOUN_PATTERN = re.compile(r'^(It|This|These|They|That|We)\s', re.MULTILINE)

# Required frontmatter fields
REQUIRED_FRONTMATTER = [
    'title', 'category', 'subcategory', 'tags', 'stack',
    'priority', 'audience', 'complexity', 'doc_type',
    'source_confidence', 'last_updated'
]


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    level: str  # FAIL, WARN, INFO
    check: str
    message: str
    line_number: Optional[int] = None
    details: Optional[str] = None


@dataclass
class FileValidationResult:
    """Results for a single file."""
    file_path: str
    relative_path: str
    line_count: int
    issues: List[ValidationIssue]

    @property
    def has_failures(self) -> bool:
        return any(issue.level == 'FAIL' for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.level == 'WARN' for issue in self.issues)

    @property
    def failure_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == 'FAIL')

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == 'WARN')


class DocumentValidator:
    """Validates markdown documents against RAG quality specifications."""

    def __init__(self, docs_root: Path, verbose: bool = False):
        self.docs_root = docs_root
        self.verbose = verbose
        self.results: List[FileValidationResult] = []

    def validate_all(self) -> List[FileValidationResult]:
        """Validate all markdown files in the docs directory."""
        md_files = list(self.docs_root.glob('**/*.md'))

        if self.verbose:
            print(f"Found {len(md_files)} markdown files to validate")

        for md_file in sorted(md_files):
            result = self.validate_file(md_file)
            self.results.append(result)

            if self.verbose and result.issues:
                self._print_file_result(result)

        return self.results

    def validate_file(self, file_path: Path) -> FileValidationResult:
        """Validate a single markdown file."""
        issues = []
        relative_path = str(file_path.relative_to(self.docs_root))

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            issues.append(ValidationIssue(
                level='FAIL',
                check='file_read',
                message=f'Failed to read file: {str(e)}'
            ))
            return FileValidationResult(
                file_path=str(file_path),
                relative_path=relative_path,
                line_count=0,
                issues=issues
            )

        line_count = len(lines)

        # Run all validation checks
        self._check_frontmatter(content, lines, issues)
        self._check_sections(content, issues)
        self._check_structural(content, lines, file_path, issues)

        return FileValidationResult(
            file_path=str(file_path),
            relative_path=relative_path,
            line_count=line_count,
            issues=issues
        )

    def _check_frontmatter(self, content: str, lines: List[str], issues: List[ValidationIssue]):
        """Validate frontmatter (11 checks)."""
        # Check if file starts with frontmatter
        if not content.startswith('---'):
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_start',
                message='File must start with "---" (frontmatter delimiter)',
                line_number=1
            ))
            return

        # Check for H1 before frontmatter (common error)
        if lines and lines[0].startswith('# '):
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_h1_before',
                message='File has H1 heading before frontmatter (remove the H1 line)',
                line_number=1
            ))
            return

        # Extract frontmatter
        try:
            # Find second --- delimiter
            second_delim = content.find('---', 3)
            if second_delim == -1:
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_end',
                    message='Frontmatter not properly closed (missing second "---")'
                ))
                return

            frontmatter_text = content[3:second_delim].strip()
            frontmatter = yaml.safe_load(frontmatter_text)

            if not isinstance(frontmatter, dict):
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_parse',
                    message='Frontmatter did not parse to a dictionary'
                ))
                return

        except yaml.YAMLError as e:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_parse',
                message=f'Frontmatter YAML parse error: {str(e)}'
            ))
            return

        # Check required fields
        missing_fields = [field for field in REQUIRED_FRONTMATTER if field not in frontmatter]
        if missing_fields:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_required_fields',
                message=f'Missing required frontmatter fields: {", ".join(missing_fields)}'
            ))

        # Validate enum fields
        if 'stack' in frontmatter and frontmatter['stack'] not in VALID_STACKS:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_stack',
                message=f'Invalid stack value: "{frontmatter["stack"]}". Must be one of: {", ".join(VALID_STACKS)}'
            ))

        if 'priority' in frontmatter and frontmatter['priority'] not in VALID_PRIORITIES:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_priority',
                message=f'Invalid priority value: "{frontmatter["priority"]}". Must be one of: {", ".join(VALID_PRIORITIES)}'
            ))

        if 'audience' in frontmatter and frontmatter['audience'] not in VALID_AUDIENCES:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_audience',
                message=f'Invalid audience value: "{frontmatter["audience"]}". Must be one of: {", ".join(VALID_AUDIENCES)}'
            ))

        if 'complexity' in frontmatter and frontmatter['complexity'] not in VALID_COMPLEXITIES:
            issues.append(ValidationIssue(
                level='FAIL',
                check='frontmatter_complexity',
                message=f'Invalid complexity value: "{frontmatter["complexity"]}". Must be one of: {", ".join(VALID_COMPLEXITIES)}'
            ))

        # Validate source_confidence format
        if 'source_confidence' in frontmatter:
            confidence = str(frontmatter['source_confidence'])
            if not re.match(r'^\d+%$', confidence):
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_confidence',
                    message=f'Invalid source_confidence format: "{confidence}". Must match pattern: \\d+%'
                ))

        # Validate last_updated is a date
        if 'last_updated' in frontmatter:
            try:
                date_str = str(frontmatter['last_updated'])
                datetime.fromisoformat(date_str)
            except ValueError:
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_date',
                    message=f'Invalid last_updated date: "{frontmatter["last_updated"]}". Must be ISO format (YYYY-MM-DD)'
                ))

        # Validate tags is a non-empty list
        if 'tags' in frontmatter:
            tags = frontmatter['tags']
            if not isinstance(tags, list):
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_tags',
                    message=f'Tags must be a list, got: {type(tags).__name__}'
                ))
            elif len(tags) == 0:
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='frontmatter_tags',
                    message='Tags list must not be empty'
                ))

    def _check_sections(self, content: str, issues: List[ValidationIssue]):
        """Validate section-level requirements (6 checks)."""
        # Split content into sections by ## headings
        sections = re.split(r'\n## ', content)

        # Check if at least one ## section exists
        if len(sections) < 2:  # First "section" is before first ##
            issues.append(ValidationIssue(
                level='WARN',
                check='sections_exist',
                message='No ## sections found in document'
            ))
            return

        # Skip the first split (before first ##, contains frontmatter)
        for i, section in enumerate(sections[1:], 1):
            section_content = '## ' + section
            section_lines = section_content.split('\n')
            section_title = section_lines[0] if section_lines else f"Section {i}"

            # Check section length (max 1500 chars)
            section_length = len(section_content)
            if section_length > MAX_SECTION_LENGTH:
                issues.append(ValidationIssue(
                    level='FAIL',
                    check='section_length',
                    message=f'Section "{section_title}" exceeds {MAX_SECTION_LENGTH} characters ({section_length} chars)',
                    details=section_title
                ))

            # Check if section starts with pronoun
            # Extract first sentence after the heading
            section_text = '\n'.join(section_lines[1:]).strip()
            if section_text:
                first_sentence = section_text.split('\n')[0].strip()
                if PRONOUN_PATTERN.match(first_sentence):
                    issues.append(ValidationIssue(
                        level='FAIL',
                        check='section_pronoun',
                        message=f'Section "{section_title}" starts with pronoun',
                        details=f'First sentence: "{first_sentence[:100]}..."'
                    ))

            # Check for code blocks >10 lines without their own ### subsection
            self._check_code_blocks_in_section(section_content, section_title, issues)

        # Check for bare code blocks (no preceding prose)
        self._check_bare_code_blocks(content, issues)

        # Check heading hierarchy
        self._check_heading_hierarchy(content, issues)

    def _check_code_blocks_in_section(self, section: str, section_title: str, issues: List[ValidationIssue]):
        """Check if long code blocks have their own ### subsection."""
        # Find all code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', section)

        for code_block in code_blocks:
            lines_in_block = code_block.count('\n')

            if lines_in_block > CODE_BLOCK_LONG_THRESHOLD:
                # Check if there's a ### heading immediately before this code block
                code_block_pos = section.find(code_block)
                before_code = section[:code_block_pos].strip()

                # Check last 200 chars for a ### heading
                recent_text = before_code[-200:] if len(before_code) > 200 else before_code
                if not re.search(r'\n### ', recent_text):
                    issues.append(ValidationIssue(
                        level='WARN',
                        check='code_block_subsection',
                        message=f'Code block with {lines_in_block} lines should have its own ### subsection',
                        details=f'In section: "{section_title}"'
                    ))

    def _check_bare_code_blocks(self, content: str, issues: List[ValidationIssue]):
        """Check for code blocks without preceding prose."""
        # This is a simplified check - looks for ``` right after headings
        pattern = r'(#{2,4}[^\n]+\n)\s*```'
        matches = re.finditer(pattern, content)

        for match in matches:
            heading = match.group(1).strip()
            issues.append(ValidationIssue(
                level='WARN',
                check='bare_code_block',
                message=f'Code block immediately follows heading without prose',
                details=f'After: "{heading}"'
            ))

    def _check_heading_hierarchy(self, content: str, issues: List[ValidationIssue]):
        """Check that heading hierarchy is not skipped."""
        lines = content.split('\n')
        prev_level = 1  # Start after # (H1 title)

        for line_num, line in enumerate(lines, 1):
            if line.startswith('#'):
                # Count heading level
                level = len(re.match(r'^#+', line).group())

                # Check if we skipped a level
                if level > prev_level + 1:
                    issues.append(ValidationIssue(
                        level='WARN',
                        check='heading_hierarchy',
                        message=f'Heading hierarchy skip detected: went from {"#" * prev_level} to {"#" * level}',
                        line_number=line_num,
                        details=line.strip()
                    ))

                prev_level = level

    def _check_structural(self, content: str, lines: List[str], file_path: Path, issues: List[ValidationIssue]):
        """Validate structural requirements (4 checks)."""
        # Check line count classification
        line_count = len(lines)

        if line_count < STUB_LINE_COUNT:
            issues.append(ValidationIssue(
                level='WARN',
                check='stub_file',
                message=f'File is classified as stub ({line_count} lines, threshold: {STUB_LINE_COUNT})'
            ))
        elif line_count > OVERSIZED_LINE_COUNT:
            issues.append(ValidationIssue(
                level='INFO',
                check='oversized_file',
                message=f'File is classified as oversized ({line_count} lines, threshold: {OVERSIZED_LINE_COUNT})'
            ))

        # Check filename is lowercase-kebab-case
        filename = file_path.stem  # Without extension
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', filename):
            issues.append(ValidationIssue(
                level='FAIL',
                check='filename_convention',
                message=f'Filename "{filename}" is not lowercase-kebab-case'
            ))

        # Check for trailing newline
        if content and not content.endswith('\n'):
            issues.append(ValidationIssue(
                level='WARN',
                check='trailing_newline',
                message='File does not end with a newline'
            ))

    def _print_file_result(self, result: FileValidationResult):
        """Print validation results for a single file."""
        status = '❌ FAIL' if result.has_failures else '⚠️  WARN' if result.has_warnings else '✅ PASS'
        print(f"\n{status} {result.relative_path} ({result.line_count} lines)")

        for issue in result.issues:
            icon = '❌' if issue.level == 'FAIL' else '⚠️ ' if issue.level == 'WARN' else 'ℹ️ '
            location = f" [line {issue.line_number}]" if issue.line_number else ""
            print(f"  {icon} {issue.check}{location}: {issue.message}")
            if issue.details and self.verbose:
                print(f"     → {issue.details}")

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report."""
        total_files = len(self.results)
        files_with_failures = sum(1 for r in self.results if r.has_failures)
        files_with_warnings = sum(1 for r in self.results if r.has_warnings)
        total_failures = sum(r.failure_count for r in self.results)
        total_warnings = sum(r.warning_count for r in self.results)

        # Group by check type
        failures_by_check = defaultdict(int)
        warnings_by_check = defaultdict(int)

        for result in self.results:
            for issue in result.issues:
                if issue.level == 'FAIL':
                    failures_by_check[issue.check] += 1
                elif issue.level == 'WARN':
                    warnings_by_check[issue.check] += 1

        # Find duplicate basenames
        basename_map = defaultdict(list)
        for result in self.results:
            basename = Path(result.file_path).name
            basename_map[basename].append(result.relative_path)

        duplicates = {k: v for k, v in basename_map.items() if len(v) > 1}

        return {
            'summary': {
                'total_files': total_files,
                'files_with_failures': files_with_failures,
                'files_with_warnings': files_with_warnings,
                'files_passing': total_files - files_with_failures - files_with_warnings,
                'total_failures': total_failures,
                'total_warnings': total_warnings,
                'duplicate_basenames': len(duplicates)
            },
            'failures_by_check': dict(failures_by_check),
            'warnings_by_check': dict(warnings_by_check),
            'duplicate_basenames': duplicates,
            'files': [
                {
                    'path': r.relative_path,
                    'line_count': r.line_count,
                    'failures': r.failure_count,
                    'warnings': r.warning_count,
                    'issues': [asdict(issue) for issue in r.issues]
                }
                for r in self.results
            ]
        }

    def print_summary(self):
        """Print summary of validation results."""
        report = self.generate_report()
        summary = report['summary']

        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        print(f"\nFiles validated: {summary['total_files']}")
        print(f"  ✅ Passing:     {summary['files_passing']}")
        print(f"  ⚠️  Warnings:    {summary['files_with_warnings']}")
        print(f"  ❌ Failures:    {summary['files_with_failures']}")

        print(f"\nTotal issues:")
        print(f"  ❌ Failures:    {summary['total_failures']}")
        print(f"  ⚠️  Warnings:    {summary['total_warnings']}")

        if report['failures_by_check']:
            print(f"\nTop failure types:")
            sorted_failures = sorted(report['failures_by_check'].items(), key=lambda x: x[1], reverse=True)
            for check, count in sorted_failures[:10]:
                print(f"  • {check}: {count}")

        if report['warnings_by_check']:
            print(f"\nTop warning types:")
            sorted_warnings = sorted(report['warnings_by_check'].items(), key=lambda x: x[1], reverse=True)
            for check, count in sorted_warnings[:10]:
                print(f"  • {check}: {count}")

        if report['duplicate_basenames']:
            print(f"\n⚠️  Found {len(report['duplicate_basenames'])} duplicate basenames:")
            for basename, paths in list(report['duplicate_basenames'].items())[:5]:
                print(f"  • {basename}:")
                for path in paths:
                    print(f"    - {path}")
            if len(report['duplicate_basenames']) > 5:
                print(f"  ... and {len(report['duplicate_basenames']) - 5} more")

        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate RAG documentation files')
    parser.add_argument(
        '--docs-dir',
        default='../../docs',
        help='Path to docs directory (default: ../../docs)'
    )
    parser.add_argument(
        '--json',
        help='Output JSON report to file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for each file'
    )

    args = parser.parse_args()

    # Resolve docs directory
    script_dir = Path(__file__).parent
    docs_dir = (script_dir / args.docs_dir).resolve()

    if not docs_dir.exists():
        print(f"Error: Docs directory not found: {docs_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Validating documentation in: {docs_dir}")

    # Run validation
    validator = DocumentValidator(docs_dir, verbose=args.verbose)
    validator.validate_all()

    # Print summary
    validator.print_summary()

    # Save JSON report if requested
    if args.json:
        report = validator.generate_report()
        json_path = Path(args.json)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report saved to: {json_path}")

    # Exit with error code if there are failures
    has_failures = any(r.has_failures for r in validator.results)
    sys.exit(1 if has_failures else 0)


if __name__ == '__main__':
    main()
