"""
Checksum validation checks for MirrorDNA Standard.

Validates artifact integrity through SHA-256 checksums.
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import sys

# Add parent directory to path to import checksum module
sys.path.insert(0, str(Path(__file__).parent.parent))
from checksum import verify_file_with_embedded_checksum, calculate_file_checksum


def check_checksum_compliance(
    manifest: Dict[str, Any],
    profile: Dict[str, Any] = None,
    sidecar: Dict[str, Any] = None,
    manifest_path: str = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Check checksum compliance for artifacts.

    Validates that artifacts with embedded checksums match their actual content.

    Args:
        manifest: Project manifest data
        profile: Continuity profile data (optional)
        sidecar: Sidecar metadata (optional)
        manifest_path: Path to manifest file (for checksum verification)

    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []
    compliance_level = manifest.get('mirrorDNA_compliance_level', '')

    # Level 2+ should have checksum validation
    if compliance_level in ['level_2_continuity_aware', 'level_3_vault_backed_sovereign']:
        # Check if sidecar has checksum
        if sidecar and 'checksum_sha256' in sidecar:
            # If sidecar references a file, verify it
            if 'file' in sidecar and manifest_path:
                # Calculate path to referenced file
                manifest_dir = Path(manifest_path).parent if manifest_path else Path('.')
                artifact_path = manifest_dir / sidecar['file']

                if artifact_path.exists():
                    expected_checksum = sidecar['checksum_sha256']
                    try:
                        actual_checksum = calculate_file_checksum(str(artifact_path), skip_frontmatter=True)
                        if actual_checksum.lower() != expected_checksum.lower():
                            errors.append(
                                f"Checksum mismatch for {sidecar['file']}:\n"
                                f"  Expected: {expected_checksum}\n"
                                f"  Actual:   {actual_checksum}"
                            )
                    except Exception as e:
                        errors.append(f"Error verifying checksum for {sidecar['file']}: {e}")
                else:
                    warnings.append(f"Sidecar references file '{sidecar['file']}' but file not found")
        else:
            # Level 2+ without sidecar checksum
            if compliance_level == 'level_3_vault_backed_sovereign':
                warnings.append("Level 3 should include checksum verification via sidecar")
            elif compliance_level == 'level_2_continuity_aware':
                warnings.append("Level 2 should consider checksum verification via sidecar")

    # Trust-by-Design layer requires checksums
    if manifest.get('layers', {}).get('trustByDesign'):
        if not sidecar or 'checksum_sha256' not in sidecar:
            warnings.append("Trust-by-Design layer should include checksum validation")

    passed = len(errors) == 0
    return passed, errors, warnings


def verify_artifact_checksum(artifact_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Verify an artifact's embedded checksum.

    Args:
        artifact_path: Path to artifact file

    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []

    is_valid, checksum, error = verify_file_with_embedded_checksum(artifact_path)

    if checksum is None:
        warnings.append(f"No checksum_sha256 found in {artifact_path}")
    elif not is_valid:
        errors.append(f"Checksum verification failed for {artifact_path}: {error}")

    passed = len(errors) == 0
    return passed, errors, warnings


def check_sidecar_checksum(sidecar: Dict[str, Any], sidecar_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Verify that a sidecar file references a valid checksum.

    Args:
        sidecar: Sidecar metadata
        sidecar_path: Path to sidecar file

    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []

    # Check if sidecar has checksum field
    if 'checksum_sha256' not in sidecar:
        errors.append("Sidecar missing required 'checksum_sha256' field")
        return False, errors, warnings

    # Check if sidecar references a file
    if 'file' not in sidecar:
        warnings.append("Sidecar has checksum but no 'file' field to verify against")
        return True, errors, warnings

    # Try to find the referenced file
    sidecar_dir = Path(sidecar_path).parent
    referenced_file = sidecar_dir / sidecar['file']

    if not referenced_file.exists():
        errors.append(f"Sidecar references file '{sidecar['file']}' but file not found")
        return False, errors, warnings

    # Verify checksum
    expected_checksum = sidecar['checksum_sha256']
    try:
        actual_checksum = calculate_file_checksum(str(referenced_file), skip_frontmatter=True)
        if actual_checksum.lower() != expected_checksum.lower():
            errors.append(
                f"Checksum mismatch for {sidecar['file']}:\n"
                f"  Expected (from sidecar): {expected_checksum}\n"
                f"  Actual (from file):      {actual_checksum}\n"
                f"  File may have been modified since sidecar was created"
            )
            return False, errors, warnings
    except Exception as e:
        errors.append(f"Error calculating checksum for {sidecar['file']}: {e}")
        return False, errors, warnings

    # Success
    passed = len(errors) == 0
    return passed, errors, warnings
