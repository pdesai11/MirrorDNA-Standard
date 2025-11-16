"""
Checksum calculation and verification for MirrorDNA artifacts.

Implements SHA-256 checksum calculation following MirrorDNA Standard requirements.
"""

import hashlib
import re
from pathlib import Path
from typing import Tuple, Optional


def calculate_file_checksum(file_path: str, skip_frontmatter: bool = True) -> str:
    """
    Calculate SHA-256 checksum of a file.

    For Markdown files with YAML frontmatter, the checksum is calculated on the
    content AFTER the frontmatter by default (following MirrorDNA convention).

    Args:
        file_path: Path to the file
        skip_frontmatter: If True, skip YAML frontmatter in .md files (default: True)

    Returns:
        64-character hexadecimal SHA-256 checksum

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_bytes()

    # For markdown files, optionally skip frontmatter
    if skip_frontmatter and file_path.endswith('.md'):
        try:
            text = content.decode('utf-8')
            # Check for YAML frontmatter (starts with ---)
            if text.startswith('---'):
                # Find the closing ---
                end_marker = text.find('\n---', 3)
                if end_marker != -1:
                    # Skip to after the closing ---
                    content_start = text.find('\n', end_marker + 4)
                    if content_start != -1:
                        # Get content after frontmatter
                        text = text[content_start + 1:]
                        content = text.encode('utf-8')
        except UnicodeDecodeError:
            # If we can't decode, use full file content
            pass

    # Calculate SHA-256
    sha256_hash = hashlib.sha256(content)
    return sha256_hash.hexdigest()


def calculate_string_checksum(content: str) -> str:
    """
    Calculate SHA-256 checksum of a string.

    Args:
        content: String content to hash

    Returns:
        64-character hexadecimal SHA-256 checksum
    """
    sha256_hash = hashlib.sha256(content.encode('utf-8'))
    return sha256_hash.hexdigest()


def verify_checksum(file_path: str, expected_checksum: str, skip_frontmatter: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Verify that a file's checksum matches the expected value.

    Args:
        file_path: Path to the file
        expected_checksum: Expected SHA-256 checksum (64 hex chars)
        skip_frontmatter: If True, skip YAML frontmatter in .md files (default: True)

    Returns:
        Tuple of (matches, error_message)
        - (True, None) if checksum matches
        - (False, error_message) if checksum doesn't match or error occurs
    """
    # Validate expected checksum format
    if not re.match(r'^[0-9a-fA-F]{64}$', expected_checksum):
        return False, f"Invalid checksum format: {expected_checksum} (must be 64 hex characters)"

    try:
        actual_checksum = calculate_file_checksum(file_path, skip_frontmatter)
    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error calculating checksum: {e}"

    if actual_checksum.lower() != expected_checksum.lower():
        return False, (
            f"Checksum mismatch:\n"
            f"  Expected: {expected_checksum}\n"
            f"  Actual:   {actual_checksum}\n"
            f"  File may have been modified"
        )

    return True, None


def extract_checksum_from_frontmatter(file_path: str) -> Optional[str]:
    """
    Extract checksum from YAML frontmatter of a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Checksum string if found, None otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        text = path.read_text(encoding='utf-8')

        # Check for YAML frontmatter
        if not text.startswith('---'):
            return None

        # Find the closing ---
        end_marker = text.find('\n---', 3)
        if end_marker == -1:
            return None

        # Extract frontmatter
        frontmatter = text[3:end_marker]

        # Look for checksum_sha256 field
        for line in frontmatter.splitlines():
            line = line.strip()
            if line.startswith('checksum_sha256:'):
                # Extract the value
                checksum = line.split(':', 1)[1].strip().strip('"\'')
                if re.match(r'^[0-9a-fA-F]{64}$', checksum):
                    return checksum

        return None
    except Exception:
        return None


def verify_file_with_embedded_checksum(file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Verify a file against its embedded checksum in frontmatter.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_valid, checksum_found, error_message)
        - (True, checksum, None) if valid
        - (False, checksum, error) if invalid or error
        - (False, None, error) if no checksum found
    """
    # Extract checksum from frontmatter
    expected_checksum = extract_checksum_from_frontmatter(file_path)

    if expected_checksum is None:
        return False, None, "No checksum_sha256 found in frontmatter"

    # Verify checksum
    is_valid, error = verify_checksum(file_path, expected_checksum, skip_frontmatter=True)

    return is_valid, expected_checksum, error


def generate_checksum_report(file_paths: list) -> dict:
    """
    Generate checksum verification report for multiple files.

    Args:
        file_paths: List of file paths to check

    Returns:
        Dictionary with verification results
    """
    report = {
        'total_files': len(file_paths),
        'verified': 0,
        'failed': 0,
        'no_checksum': 0,
        'errors': 0,
        'results': []
    }

    for file_path in file_paths:
        result = {
            'file': file_path,
            'status': 'unknown',
            'checksum': None,
            'message': None
        }

        is_valid, checksum, error = verify_file_with_embedded_checksum(file_path)

        result['checksum'] = checksum

        if checksum is None:
            result['status'] = 'no_checksum'
            result['message'] = error
            report['no_checksum'] += 1
        elif is_valid:
            result['status'] = 'verified'
            result['message'] = 'Checksum verified successfully'
            report['verified'] += 1
        else:
            result['status'] = 'failed'
            result['message'] = error
            report['failed'] += 1

        report['results'].append(result)

    return report
