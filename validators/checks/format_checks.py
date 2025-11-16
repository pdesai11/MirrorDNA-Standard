"""
Format validation checks for MirrorDNA Standard canonical identifiers.

Validates VaultID and GlyphSig format compliance.
"""

import re
from typing import Dict, Any, List, Tuple, Optional


# VaultID pattern: AMOS://Component/Artifact/Version
# Example: AMOS://MirrorDNA/Standard/v1.0
VAULTID_PATTERN = re.compile(
    r'^AMOS://[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*(/v\d+(?:\.\d+)*)?$'
)

# GlyphSig component pattern: ⟡⟦KEYWORD⟧
# Full pattern: one or more glyphs separated by ' · '
GLYPH_COMPONENT_PATTERN = re.compile(r'⟡⟦[A-Z0-9_-]+⟧')
GLYPHSIG_PATTERN = re.compile(r'^⟡⟦[A-Z0-9_-]+⟧(?:\s*·\s*⟡⟦[A-Z0-9_-]+⟧)*$')


def validate_vaultid(vault_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate VaultID format.

    Args:
        vault_id: VaultID string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_vaultid("AMOS://MirrorDNA/Standard/v1.0")
        (True, None)
        >>> validate_vaultid("INVALID://Format")
        (False, "VaultID must start with 'AMOS://'")
    """
    if not vault_id:
        return False, "VaultID cannot be empty"

    if not vault_id.startswith("AMOS://"):
        return False, "VaultID must start with 'AMOS://'"

    if not VAULTID_PATTERN.match(vault_id):
        return False, (
            "VaultID format invalid. Expected: AMOS://Component/Artifact/Version "
            f"(e.g., AMOS://MirrorDNA/Standard/v1.0). Got: {vault_id}"
        )

    # Check for proper version format if version is present
    if '/v' in vault_id:
        version_part = vault_id.split('/v')[-1]
        if not re.match(r'^\d+(?:\.\d+)*$', version_part):
            return False, (
                f"VaultID version must be numeric (v1.0, v2.1.3, etc.). Got: v{version_part}"
            )

    return True, None


def validate_glyphsig(glyphsig: str) -> Tuple[bool, Optional[str]]:
    """
    Validate GlyphSig format.

    Args:
        glyphsig: GlyphSig string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_glyphsig("⟡⟦STANDARD⟧ · ⟡⟦COMPLIANCE⟧")
        (True, None)
        >>> validate_glyphsig("INVALID")
        (False, "GlyphSig must contain at least one glyph marker")
    """
    if not glyphsig:
        return False, "GlyphSig cannot be empty"

    # Check if it contains glyph markers
    if '⟡⟦' not in glyphsig or '⟧' not in glyphsig:
        return False, "GlyphSig must contain at least one glyph marker ⟡⟦...⟧"

    if not GLYPHSIG_PATTERN.match(glyphsig):
        return False, (
            "GlyphSig format invalid. Expected: ⟡⟦KEYWORD⟧ · ⟡⟦KEYWORD⟧ · ... "
            "Keywords must be uppercase alphanumeric with underscores/hyphens. "
            f"Got: {glyphsig}"
        )

    # Extract all glyph components
    components = GLYPH_COMPONENT_PATTERN.findall(glyphsig)
    if not components:
        return False, "No valid glyph components found"

    # Check for duplicate glyphs (warning, not error)
    unique_components = set(components)
    if len(unique_components) < len(components):
        # This is a warning case, but we'll still return True
        # The caller can check for duplicates separately if needed
        pass

    return True, None


def validate_glyphsig_list(glyphsig: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate GlyphSig that may be a string or list of strings.

    Args:
        glyphsig: GlyphSig string or list of strings to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if isinstance(glyphsig, str):
        return validate_glyphsig(glyphsig)
    elif isinstance(glyphsig, list):
        if not glyphsig:
            return False, "GlyphSig list cannot be empty"

        for idx, glyph in enumerate(glyphsig):
            if not isinstance(glyph, str):
                return False, f"GlyphSig list item {idx} must be a string"

            is_valid, error = validate_glyphsig(glyph)
            if not is_valid:
                return False, f"GlyphSig list item {idx}: {error}"

        return True, None
    else:
        return False, f"GlyphSig must be string or list, got {type(glyphsig).__name__}"


def check_format_compliance(
    manifest: Dict[str, Any],
    policy: Dict[str, Any] = None,
    profile: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Check format compliance for VaultID and GlyphSig in manifest and related files.

    Args:
        manifest: Project manifest data
        policy: Reflection policy data (optional)
        profile: Continuity profile data (optional)

    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []

    # Validate manifest VaultID if present
    if 'vault_id' in manifest:
        vault_id = manifest['vault_id']
        is_valid, error = validate_vaultid(vault_id)
        if not is_valid:
            errors.append(f"Manifest vault_id: {error}")
    else:
        # VaultID is required for L3, recommended for L2
        compliance_level = manifest.get('mirrorDNA_compliance_level', '')
        if compliance_level == 'level_3_vault_backed_sovereign':
            errors.append("Manifest must include 'vault_id' for Level 3 compliance")
        elif compliance_level == 'level_2_continuity_aware':
            warnings.append("Manifest should include 'vault_id' for Level 2 compliance")

    # Validate profile VaultID if present
    if profile and 'vault_id' in profile:
        vault_id = profile['vault_id']
        is_valid, error = validate_vaultid(vault_id)
        if not is_valid:
            errors.append(f"Continuity profile vault_id: {error}")

    # Validate policy GlyphSig references if present
    if policy and 'glyph_signatures' in policy:
        glyph_config = policy['glyph_signatures']

        if 'registered_glyphs' in glyph_config:
            registered = glyph_config['registered_glyphs']
            if isinstance(registered, list):
                for idx, glyph_def in enumerate(registered):
                    if isinstance(glyph_def, dict) and 'glyph' in glyph_def:
                        glyph_str = glyph_def['glyph']
                        is_valid, error = validate_glyphsig(glyph_str)
                        if not is_valid:
                            errors.append(
                                f"Policy registered_glyphs[{idx}]: {error}"
                            )

    passed = len(errors) == 0
    return passed, errors, warnings


def extract_glyphs_from_text(text: str) -> List[str]:
    """
    Extract all glyph components from a text string.

    Args:
        text: Text to search for glyphs

    Returns:
        List of found glyph strings (e.g., ['⟡⟦STANDARD⟧', '⟡⟦MIRROR⟧'])
    """
    return GLYPH_COMPONENT_PATTERN.findall(text)


def validate_semantic_glyphs(glyphsig: str, context: str = None) -> List[str]:
    """
    Validate semantic consistency of glyphs (warnings only).

    This checks for common patterns and provides recommendations.

    Args:
        glyphsig: GlyphSig string to validate
        context: Optional context (e.g., "Master Citation", "Standard")

    Returns:
        List of warning messages
    """
    warnings = []

    # Extract glyph keywords
    glyphs = extract_glyphs_from_text(glyphsig)
    keywords = [g.replace('⟡⟦', '').replace('⟧', '') for g in glyphs]

    # Check for common patterns
    standard_glyphs = {
        'MASTER', 'STANDARD', 'CANONICAL', 'VERIFIED', 'CONTINUITY',
        'MIRROR', 'REFLECTION', 'VAULT', 'SEALED', 'LAW', 'GLYPHSIG',
        'TRI-WEAVE', 'ZDL', 'AMOS'
    }

    unknown_glyphs = [k for k in keywords if k not in standard_glyphs]
    if unknown_glyphs:
        warnings.append(
            f"Non-standard glyphs found: {', '.join(unknown_glyphs)}. "
            "Consider using registered glyphs from glossary."
        )

    # Check for SEALED without CANONICAL
    if 'SEALED' in keywords and 'CANONICAL' not in keywords:
        warnings.append(
            "⟡⟦SEALED⟧ typically appears with ⟡⟦CANONICAL⟧ for finalized documents"
        )

    return warnings
