#!/usr/bin/env python3
"""
Remove empty section headings from markdown files.

An empty heading is a ## line that has no content before the next ## line.
"""

import os
import sys
from pathlib import Path
import re


def find_empty_headings(content: str) -> list[tuple[int, str]]:
    """Find line numbers and text of empty ## headings."""
    lines = content.split('\n')
    empty_headings = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a ## heading
        if re.match(r'^## ', line):
            # Look ahead to see if there's content before the next ## heading
            j = i + 1
            has_content = False

            # Skip blank lines
            while j < len(lines) and lines[j].strip() == '':
                j += 1

            # If the next non-blank line is another ## heading, original heading is empty
            if j < len(lines) and re.match(r'^## ', lines[j]):
                empty_headings.append((i + 1, line))  # +1 for 1-based line numbers

        i += 1

    return empty_headings


def remove_empty_headings(content: str) -> tuple[str, int]:
    """Remove empty ## headings from content. Returns (new_content, count_removed)."""
    lines = content.split('\n')
    lines_to_remove = set()

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a ## heading
        if re.match(r'^## ', line):
            # Look ahead to see if there's content before the next ## heading
            j = i + 1

            # Skip blank lines
            while j < len(lines) and lines[j].strip() == '':
                j += 1

            # If the next non-blank line is another ## heading, mark for removal
            if j < len(lines) and re.match(r'^## ', lines[j]):
                lines_to_remove.add(i)

        i += 1

    # Build new content without the empty headings
    new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

    return '\n'.join(new_lines), len(lines_to_remove)


def process_file(filepath: Path, dry_run: bool = False) -> dict:
    """Process a single file. Returns stats dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Find empty headings
    empty_headings = find_empty_headings(original_content)

    if not empty_headings:
        return {'file': str(filepath), 'empty_count': 0, 'removed': 0}

    # Remove empty headings
    new_content, removed_count = remove_empty_headings(original_content)

    result = {
        'file': str(filepath),
        'empty_count': len(empty_headings),
        'removed': removed_count,
        'empty_headings': [text for _, text in empty_headings]
    }

    # Write back if not dry run
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return result


def main():
    dry_run = '--dry-run' in sys.argv

    # Directories to process
    dirs_to_process = [
        'docs/sanity',
        'docs/php-wordpress/block-development',
        'docs/js-nextjs/data-fetching'
    ]

    # Also check for any remaining scattered files in other directories
    all_doc_dirs = [
        'docs/js-nextjs',
        'docs/php-wordpress',
        'docs/cross-stack'
    ]

    total_files = 0
    total_empty = 0
    total_removed = 0
    files_with_empty = []

    print(f"{'DRY RUN - ' if dry_run else ''}Scanning for empty headings...\n")

    # Process primary directories
    for dir_path in dirs_to_process:
        if not os.path.exists(dir_path):
            continue

        print(f"\n{'='*60}")
        print(f"Directory: {dir_path}")
        print(f"{'='*60}")

        for md_file in sorted(Path(dir_path).rglob('*.md')):
            result = process_file(md_file, dry_run)
            total_files += 1

            if result['empty_count'] > 0:
                total_empty += result['empty_count']
                total_removed += result['removed']
                files_with_empty.append(result)

                print(f"\n{result['file']}")
                print(f"  Empty headings found: {result['empty_count']}")
                for heading in result['empty_headings']:
                    print(f"    - {heading}")

    # Scan other directories for scattered files
    print(f"\n{'='*60}")
    print("Scanning other directories for scattered empty headings...")
    print(f"{'='*60}")

    for dir_path in all_doc_dirs:
        if not os.path.exists(dir_path):
            continue

        for md_file in sorted(Path(dir_path).rglob('*.md')):
            # Skip if already processed
            if any(str(md_file).startswith(d) for d in dirs_to_process):
                continue

            result = process_file(md_file, dry_run)
            total_files += 1

            if result['empty_count'] > 0:
                total_empty += result['empty_count']
                total_removed += result['removed']
                files_with_empty.append(result)

                print(f"\n{result['file']}")
                print(f"  Empty headings found: {result['empty_count']}")
                for heading in result['empty_headings']:
                    print(f"    - {heading}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files scanned: {total_files}")
    print(f"Files with empty headings: {len(files_with_empty)}")
    print(f"Total empty headings found: {total_empty}")
    print(f"Total empty headings {'would be ' if dry_run else ''}removed: {total_removed}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were modified.")
        print("Run without --dry-run to actually remove empty headings.")
    else:
        print("\n✅ All empty headings have been removed.")

    return 0 if total_empty == 0 else (1 if dry_run else 0)


if __name__ == '__main__':
    sys.exit(main())
