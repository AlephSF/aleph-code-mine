#!/usr/bin/env python3
"""Analyze sections in a markdown file and show which exceed character limits."""

import re
import sys
from pathlib import Path

MAX_LENGTH = 1500

def analyze_file(file_path):
    """Analyze a single file and show section details."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by ## headings
    sections = re.split(r'\n## ', content)

    print(f"\n{'='*80}")
    print(f"File: {file_path}")
    print(f"{'='*80}\n")

    violations = 0
    total_sections = 0

    for i, section in enumerate(sections[1:], 1):  # Skip before first ##
        section_content = '## ' + section
        section_lines = section_content.split('\n')
        section_title = section_lines[0] if section_lines else f"Section {i}"
        section_length = len(section_content)

        if section_length > MAX_LENGTH:
            violations += 1
            print(f"❌ {section_title}")
            print(f"   Length: {section_length} chars ({section_length - MAX_LENGTH} over limit)")

            # Count subsections
            subsections = section_content.count('\n### ')
            code_blocks = section_content.count('```')
            print(f"   Subsections: {subsections}, Code blocks: {code_blocks // 2}")
            print()

        total_sections += 1

    print(f"\nSummary: {violations}/{total_sections} sections exceed {MAX_LENGTH} chars")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python section-analyzer.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    analyze_file(file_path)
