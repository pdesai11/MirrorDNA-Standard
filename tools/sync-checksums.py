#!/usr/bin/env python3
"""
MirrorDNA Checksum Sync Tool

Synchronizes checksums between .md frontmatter and .sidecar.json files.
Prevents checksum drift and ensures consistency across artifacts.

Usage:
  # Check for drift
  python tools/sync-checksums.py --verify

  # Sync from frontmatter to sidecar
  python tools/sync-checksums.py --source frontmatter

  # Sync from sidecar to frontmatter
  python tools/sync-checksums.py --source sidecar

  # Recalculate and sync both
  python tools/sync-checksums.py --recalculate

  # Specific files
  python tools/sync-checksums.py --files spec/*.md --recalculate

  # Dry run
  python tools/sync-checksums.py --recalculate --dry-run

Features:
  - Detects checksum drift between frontmatter and sidecar
  - Bidirectional sync (frontmatter ↔ sidecar)
  - Recalculates checksums from file content
  - Batch operations on multiple files
  - Dry-run mode
"""

import argparse
import sys
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple, List


class ChecksumMismatch:
    """Represents a checksum mismatch."""

    def __init__(self, filepath: Path, frontmatter_checksum: Optional[str],
                 sidecar_checksum: Optional[str], calculated_checksum: Optional[str]):
        self.filepath = filepath
        self.frontmatter_checksum = frontmatter_checksum
        self.sidecar_checksum = sidecar_checksum
        self.calculated_checksum = calculated_checksum

    def has_drift(self) -> bool:
        """Check if there's drift between frontmatter and sidecar."""
        if self.frontmatter_checksum and self.sidecar_checksum:
            return self.frontmatter_checksum != self.sidecar_checksum
        return False

    def is_correct(self) -> bool:
        """Check if checksums match calculated value."""
        if not self.calculated_checksum:
            return True  # Can't verify without calculated checksum

        checksums = [self.frontmatter_checksum, self.sidecar_checksum]
        checksums = [c for c in checksums if c]  # Remove None values

        return all(c == self.calculated_checksum for c in checksums)


class ChecksumSyncTool:
    """Synchronizes checksums between frontmatter and sidecar files."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.mismatches: List[ChecksumMismatch] = []

    def extract_frontmatter(self, filepath: Path) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extract YAML frontmatter from markdown file.

        Returns:
            Tuple of (frontmatter_text, checksum_value, content_after_frontmatter)
        """
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return None, None, content

        # Check for YAML frontmatter
        if not content.startswith('---\n'):
            return None, None, content

        # Find closing ---
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None, None, content

        end_pos = end_match.end() + 4
        frontmatter = content[4:end_pos - 4]
        rest = content[end_pos:]

        # Extract checksum
        checksum_match = re.search(r'^checksum_sha256:\s*(.+)$', frontmatter, re.MULTILINE)
        checksum = checksum_match.group(1).strip() if checksum_match else None

        return frontmatter, checksum, rest

    def update_frontmatter_checksum(self, filepath: Path, new_checksum: str) -> bool:
        """Update checksum in YAML frontmatter."""
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return False

        # Check for frontmatter
        if not content.startswith('---\n'):
            print(f"Warning: {filepath} has no YAML frontmatter", file=sys.stderr)
            return False

        # Find frontmatter boundaries
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return False

        end_pos = end_match.end() + 4
        frontmatter = content[4:end_pos - 4]
        rest = content[end_pos:]

        # Update or add checksum
        if re.search(r'^checksum_sha256:', frontmatter, re.MULTILINE):
            # Update existing
            updated_frontmatter = re.sub(
                r'^checksum_sha256:\s*.+$',
                f'checksum_sha256: {new_checksum}',
                frontmatter,
                flags=re.MULTILINE
            )
        else:
            # Add new (at end of frontmatter)
            updated_frontmatter = frontmatter.rstrip() + f'\nchecksum_sha256: {new_checksum}\n'

        # Reconstruct file
        updated_content = f'---\n{updated_frontmatter}---\n{rest}'

        if self.dry_run:
            print(f"[DRY RUN] Would update frontmatter in {filepath}")
            return True

        try:
            filepath.write_text(updated_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return False

    def get_sidecar_path(self, filepath: Path) -> Path:
        """Get sidecar path for a given file."""
        return filepath.with_suffix(filepath.suffix + '.sidecar.json')

    def read_sidecar_checksum(self, sidecar_path: Path) -> Optional[str]:
        """Read checksum from sidecar file."""
        if not sidecar_path.exists():
            return None

        try:
            with open(sidecar_path, 'r') as f:
                data = json.load(f)
            return data.get('checksum_sha256')
        except Exception as e:
            print(f"Error reading sidecar {sidecar_path}: {e}", file=sys.stderr)
            return None

    def update_sidecar_checksum(self, sidecar_path: Path, new_checksum: str) -> bool:
        """Update checksum in sidecar file."""
        # Read existing sidecar or create new
        if sidecar_path.exists():
            try:
                with open(sidecar_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading sidecar {sidecar_path}: {e}", file=sys.stderr)
                return False
        else:
            # Create minimal sidecar
            data = {
                "vault_id": "",
                "version": "1.0.0"
            }

        # Update checksum
        data['checksum_sha256'] = new_checksum

        if self.dry_run:
            print(f"[DRY RUN] Would update sidecar {sidecar_path}")
            return True

        try:
            with open(sidecar_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing sidecar {sidecar_path}: {e}", file=sys.stderr)
            return False

    def calculate_checksum(self, filepath: Path) -> Optional[str]:
        """Calculate SHA-256 checksum, skipping frontmatter for .md files."""
        try:
            if filepath.suffix == '.md':
                # Skip frontmatter
                content = filepath.read_text(encoding='utf-8')

                if content.startswith('---\n'):
                    # Find closing ---
                    end_match = re.search(r'\n---\n', content[4:])
                    if end_match:
                        end_pos = end_match.end() + 4
                        # Calculate checksum from content after frontmatter
                        content_to_hash = content[end_pos:].encode('utf-8')
                    else:
                        content_to_hash = content.encode('utf-8')
                else:
                    content_to_hash = content.encode('utf-8')
            else:
                # Regular file
                content_to_hash = filepath.read_bytes()

            return hashlib.sha256(content_to_hash).hexdigest()

        except Exception as e:
            print(f"Error calculating checksum for {filepath}: {e}", file=sys.stderr)
            return None

    def verify_file(self, filepath: Path) -> ChecksumMismatch:
        """Verify checksums for a file."""
        # Extract frontmatter checksum
        _, frontmatter_checksum, _ = self.extract_frontmatter(filepath)

        # Read sidecar checksum
        sidecar_path = self.get_sidecar_path(filepath)
        sidecar_checksum = self.read_sidecar_checksum(sidecar_path)

        # Calculate actual checksum
        calculated_checksum = self.calculate_checksum(filepath)

        mismatch = ChecksumMismatch(
            filepath,
            frontmatter_checksum,
            sidecar_checksum,
            calculated_checksum
        )

        return mismatch

    def sync_from_frontmatter(self, filepath: Path) -> bool:
        """Sync checksum from frontmatter to sidecar."""
        _, frontmatter_checksum, _ = self.extract_frontmatter(filepath)

        if not frontmatter_checksum:
            print(f"Warning: {filepath} has no frontmatter checksum", file=sys.stderr)
            return False

        sidecar_path = self.get_sidecar_path(filepath)
        return self.update_sidecar_checksum(sidecar_path, frontmatter_checksum)

    def sync_from_sidecar(self, filepath: Path) -> bool:
        """Sync checksum from sidecar to frontmatter."""
        sidecar_path = self.get_sidecar_path(filepath)
        sidecar_checksum = self.read_sidecar_checksum(sidecar_path)

        if not sidecar_checksum:
            print(f"Warning: {sidecar_path} has no checksum", file=sys.stderr)
            return False

        return self.update_frontmatter_checksum(filepath, sidecar_checksum)

    def recalculate_and_sync(self, filepath: Path) -> bool:
        """Recalculate checksum and update both frontmatter and sidecar."""
        calculated_checksum = self.calculate_checksum(filepath)

        if not calculated_checksum:
            return False

        # Update both
        success = True

        if filepath.suffix == '.md':
            # Has frontmatter
            if not self.update_frontmatter_checksum(filepath, calculated_checksum):
                success = False

        # Update sidecar
        sidecar_path = self.get_sidecar_path(filepath)
        if not self.update_sidecar_checksum(sidecar_path, calculated_checksum):
            success = False

        return success


def main():
    parser = argparse.ArgumentParser(
        description='Sync checksums between frontmatter and sidecar files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify checksums (detect drift)
  python tools/sync-checksums.py --verify

  # Sync from frontmatter to sidecar
  python tools/sync-checksums.py --source frontmatter

  # Sync from sidecar to frontmatter
  python tools/sync-checksums.py --source sidecar

  # Recalculate and sync both
  python tools/sync-checksums.py --recalculate

  # Specific files
  python tools/sync-checksums.py --files spec/*.md --recalculate

  # Dry run (preview changes)
  python tools/sync-checksums.py --recalculate --dry-run

Operations:
  - verify: Check for drift, don't modify
  - sync: Copy checksum from source to target
  - recalculate: Calculate fresh checksum, update both

Sources:
  - frontmatter: Use .md YAML frontmatter as source
  - sidecar: Use .sidecar.json as source
        """
    )

    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific files to process (supports glob)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify checksums (detect drift)'
    )
    parser.add_argument(
        '--source',
        choices=['frontmatter', 'sidecar'],
        help='Sync from source to other location'
    )
    parser.add_argument(
        '--recalculate',
        action='store_true',
        help='Recalculate checksums and update both'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    # Determine files to process
    if args.files:
        files = []
        for pattern in args.files:
            # Handle glob patterns
            if '*' in pattern:
                from glob import glob
                files.extend(Path(f) for f in glob(pattern))
            else:
                files.append(Path(pattern))
    else:
        # Default: scan for .md files in spec/
        spec_dir = Path('spec')
        if spec_dir.exists():
            files = list(spec_dir.glob('*.md'))
        else:
            files = []

    if not files:
        print("No files to process", file=sys.stderr)
        return 1

    print(f"Processing {len(files)} file(s)...")

    # Create tool
    tool = ChecksumSyncTool(dry_run=args.dry_run)

    # Verify mode
    if args.verify:
        print("\nVerifying checksums...\n")

        drift_count = 0
        incorrect_count = 0

        for filepath in files:
            if not filepath.exists():
                print(f"✗ {filepath}: File not found")
                continue

            mismatch = tool.verify_file(filepath)

            # Check for drift
            if mismatch.has_drift():
                drift_count += 1
                print(f"⚠️  {filepath}: DRIFT DETECTED")
                print(f"   Frontmatter: {mismatch.frontmatter_checksum or 'None'}")
                print(f"   Sidecar:     {mismatch.sidecar_checksum or 'None'}")

            # Check correctness
            elif not mismatch.is_correct():
                incorrect_count += 1
                print(f"✗ {filepath}: INCORRECT")
                print(f"   Expected: {mismatch.calculated_checksum}")
                print(f"   Found:    {mismatch.frontmatter_checksum or mismatch.sidecar_checksum}")

            else:
                print(f"✓ {filepath}: OK")

        print(f"\nSummary:")
        print(f"  Total files: {len(files)}")
        print(f"  Drift detected: {drift_count}")
        print(f"  Incorrect checksums: {incorrect_count}")

        return 1 if (drift_count > 0 or incorrect_count > 0) else 0

    # Sync mode
    elif args.source:
        print(f"\nSyncing from {args.source}...\n")

        success_count = 0

        for filepath in files:
            if not filepath.exists():
                print(f"✗ {filepath}: File not found")
                continue

            if args.source == 'frontmatter':
                success = tool.sync_from_frontmatter(filepath)
            else:  # sidecar
                success = tool.sync_from_sidecar(filepath)

            if success:
                success_count += 1
                print(f"✓ {filepath}: Synced")
            else:
                print(f"✗ {filepath}: Failed")

        print(f"\nSynced {success_count}/{len(files)} file(s)")
        return 0

    # Recalculate mode
    elif args.recalculate:
        print(f"\nRecalculating checksums...\n")

        success_count = 0

        for filepath in files:
            if not filepath.exists():
                print(f"✗ {filepath}: File not found")
                continue

            # Calculate new checksum
            calculated = tool.calculate_checksum(filepath)
            if not calculated:
                print(f"✗ {filepath}: Failed to calculate")
                continue

            # Update both
            success = tool.recalculate_and_sync(filepath)

            if success:
                success_count += 1
                checksum_short = calculated[:12]
                print(f"✓ {filepath}: Updated [{checksum_short}...]")
            else:
                print(f"✗ {filepath}: Failed to update")

        print(f"\nUpdated {success_count}/{len(files)} file(s)")
        return 0

    else:
        print("Error: Must specify --verify, --source, or --recalculate", file=sys.stderr)
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
