#!/usr/bin/env python3
"""
Markdown Checksum Auto-Updater for MirrorDNA Standard

Automatically calculates and updates SHA-256 checksums in markdown file frontmatter.
Follows MirrorDNA checksum specification: skips YAML frontmatter, hashes content only.

Usage:
  # Update checksums for all spec files
  python tools/update-md-checksums.py spec/*.md

  # Update specific file
  python tools/update-md-checksums.py spec/Compliance_Migration_Guide_v1.0.md

  # Verify only (exit 1 if mismatches found)
  python tools/update-md-checksums.py --verify spec/*.md

  # Dry run (show what would change)
  python tools/update-md-checksums.py --dry-run spec/*.md

  # Verbose output
  python tools/update-md-checksums.py -v spec/*.md
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Tuple, Optional, List

# Import checksum module from validators
sys.path.insert(0, str(Path(__file__).parent.parent))
from validators.checksum import calculate_file_checksum


def extract_frontmatter(content: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter, body, checksum_from_frontmatter)
        Returns (None, content, None) if no frontmatter found
    """
    if not content.startswith('---'):
        return None, content, None

    # Find closing ---
    end_marker = content.find('\n---', 3)
    if end_marker == -1:
        return None, content, None

    frontmatter = content[3:end_marker].strip()

    # Find content start (skip newline after closing ---)
    content_start = content.find('\n', end_marker + 4)
    if content_start == -1:
        body = ""
    else:
        body = content[content_start + 1:]

    # Extract checksum from frontmatter
    checksum = None
    for line in frontmatter.splitlines():
        if line.strip().startswith('checksum_sha256:'):
            value = line.split(':', 1)[1].strip().strip('"\'')
            if re.match(r'^[0-9a-fA-F]{64}$', value):
                checksum = value
            elif value.lower() == 'pending':
                checksum = 'pending'
            break

    return frontmatter, body, checksum


def update_frontmatter_checksum(frontmatter: str, new_checksum: str) -> str:
    """
    Update checksum_sha256 field in frontmatter.

    Args:
        frontmatter: YAML frontmatter content (without --- delimiters)
        new_checksum: New checksum value

    Returns:
        Updated frontmatter
    """
    lines = frontmatter.splitlines()
    updated_lines = []
    checksum_found = False

    for line in lines:
        if line.strip().startswith('checksum_sha256:'):
            # Update existing checksum
            updated_lines.append(f'checksum_sha256: {new_checksum}')
            checksum_found = True
        else:
            updated_lines.append(line)

    if not checksum_found:
        # Add checksum field after other metadata
        # Try to add after 'tags' or 'status' or at end
        insert_index = len(updated_lines)
        for i, line in enumerate(updated_lines):
            if line.strip().startswith('tags:') or line.strip().startswith('status:'):
                insert_index = i + 1
                break
        updated_lines.insert(insert_index, f'checksum_sha256: {new_checksum}')

    return '\n'.join(updated_lines)


def process_file(
    file_path: Path,
    verify_only: bool = False,
    dry_run: bool = False,
    verbose: bool = False
) -> Tuple[bool, str]:
    """
    Process a single markdown file.

    Args:
        file_path: Path to markdown file
        verify_only: If True, only verify checksum, don't update
        dry_run: If True, show what would change but don't write
        verbose: If True, print detailed information

    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    if not file_path.suffix.lower() == '.md':
        return False, f"Not a markdown file: {file_path}"

    # Read file
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Extract frontmatter
    frontmatter, body, old_checksum = extract_frontmatter(content)

    if frontmatter is None:
        return False, "No YAML frontmatter found"

    if old_checksum is None:
        return False, "No checksum_sha256 field in frontmatter"

    # Calculate actual checksum
    try:
        actual_checksum = calculate_file_checksum(str(file_path), skip_frontmatter=True)
    except Exception as e:
        return False, f"Error calculating checksum: {e}"

    # Check if update needed
    if old_checksum == actual_checksum:
        if verbose:
            return True, f"✓ Checksum already correct: {file_path.name}"
        return True, f"✓ {file_path.name}"

    # Checksum mismatch
    if verify_only:
        return False, (
            f"✗ Checksum mismatch: {file_path.name}\n"
            f"  Expected: {old_checksum}\n"
            f"  Actual:   {actual_checksum}"
        )

    if dry_run:
        return True, (
            f"⚠ Would update: {file_path.name}\n"
            f"  Old: {old_checksum}\n"
            f"  New: {actual_checksum}"
        )

    # Update frontmatter
    updated_frontmatter = update_frontmatter_checksum(frontmatter, actual_checksum)

    # Reconstruct file
    updated_content = f"---\n{updated_frontmatter}\n---\n{body}"

    # Write back
    try:
        file_path.write_text(updated_content, encoding='utf-8')
        return True, f"✓ Updated: {file_path.name} ({old_checksum[:8]}... → {actual_checksum[:8]}...)"
    except Exception as e:
        return False, f"Error writing file: {e}"


def main():
    parser = argparse.ArgumentParser(
        description='Markdown Checksum Auto-Updater for MirrorDNA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update all spec files
  %(prog)s spec/*.md

  # Verify checksums (CI mode)
  %(prog)s --verify spec/*.md

  # Show what would change
  %(prog)s --dry-run spec/*.md

  # Verbose output
  %(prog)s -v spec/*.md

Checksum Specification:
  - Calculated on content AFTER frontmatter (skipping --- blocks)
  - Follows MirrorDNA Standard section 9
  - Avoids circular dependency (frontmatter contains checksum field)
        """
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='Markdown files to process (supports shell globs)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify only, do not update (exit 1 if mismatches found)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without writing files'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Collect all files
    all_files = []
    for pattern in args.files:
        path = Path(pattern)
        if path.exists() and path.is_file():
            all_files.append(path)
        else:
            # Try glob pattern
            for p in Path('.').glob(pattern):
                if p.is_file():
                    all_files.append(p)

    if not all_files:
        print("No files found to process")
        return 1

    # Process files
    total = len(all_files)
    success_count = 0
    error_count = 0
    errors = []

    print(f"Processing {total} file(s)...\n")

    for file_path in sorted(all_files):
        success, message = process_file(
            file_path,
            verify_only=args.verify,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        print(message)

        if success:
            success_count += 1
        else:
            error_count += 1
            errors.append(message)

    # Summary
    print(f"\n{'='*70}")
    print(f"Summary: {success_count}/{total} succeeded, {error_count}/{total} failed")
    print(f"{'='*70}")

    if args.verify and error_count > 0:
        print("\nChecksum verification FAILED")
        return 1
    elif error_count > 0:
        print("\nSome files had errors (see above)")
        return 1
    else:
        if args.verify:
            print("\nAll checksums verified ✓")
        elif args.dry_run:
            print("\nDry run complete (no files modified)")
        else:
            print("\nAll checksums updated ✓")
        return 0


if __name__ == '__main__':
    sys.exit(main())
