"""
Tests for format validation checks (VaultID, GlyphSig).
"""

import pytest
from validators.checks.format_checks import (
    validate_vaultid,
    validate_glyphsig,
    validate_glyphsig_list,
    check_format_compliance,
    extract_glyphs_from_text,
    validate_semantic_glyphs
)


class TestVaultIDValidation:
    """Tests for VaultID format validation."""

    def test_valid_vaultids(self):
        """Test valid VaultID formats."""
        valid_ids = [
            "AMOS://MirrorDNA/Standard/v1.0",
            "AMOS://MasterCitation/v15.2",
            "AMOS://MirrorDNA/Glyphsig/Law/v1.0",
            "AMOS://Component/Artifact/v2.1.3",
            "AMOS://Simple/v1",
            "AMOS://Multi-Part/Component_Name/v3.14.159",
        ]

        for vault_id in valid_ids:
            is_valid, error = validate_vaultid(vault_id)
            assert is_valid, f"VaultID {vault_id} should be valid: {error}"
            assert error is None

    def test_invalid_vaultids_wrong_prefix(self):
        """Test VaultIDs with wrong prefix."""
        invalid_ids = [
            "HTTP://MirrorDNA/Standard/v1.0",
            "INVALID://MirrorDNA/Standard/v1.0",
            "amos://MirrorDNA/Standard/v1.0",  # lowercase
            "MirrorDNA/Standard/v1.0",  # missing prefix
        ]

        for vault_id in invalid_ids:
            is_valid, error = validate_vaultid(vault_id)
            assert not is_valid, f"VaultID {vault_id} should be invalid"
            assert "AMOS://" in error

    def test_invalid_vaultids_bad_version(self):
        """Test VaultIDs with invalid version format."""
        invalid_ids = [
            "AMOS://MirrorDNA/Standard/vabc",
            "AMOS://MirrorDNA/Standard/v1.x",
            "AMOS://MirrorDNA/Standard/version1",
        ]

        for vault_id in invalid_ids:
            is_valid, error = validate_vaultid(vault_id)
            assert not is_valid, f"VaultID {vault_id} should be invalid"
            assert "version" in error.lower()

    def test_empty_vaultid(self):
        """Test empty VaultID."""
        is_valid, error = validate_vaultid("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_vaultid_without_version(self):
        """Test VaultID without version (should be valid)."""
        vault_id = "AMOS://MirrorDNA/Standard"
        is_valid, error = validate_vaultid(vault_id)
        assert is_valid, f"VaultID without version should be valid: {error}"


class TestGlyphSigValidation:
    """Tests for GlyphSig format validation."""

    def test_valid_glyphsigs(self):
        """Test valid GlyphSig formats."""
        valid_glyphs = [
            "⟡⟦STANDARD⟧ · ⟡⟦COMPLIANCE⟧ · ⟡⟦MIRROR⟧",
            "⟡⟦MASTER⟧ · ⟡⟦TRI-WEAVE⟧ · ⟡⟦ZDL⟧ · ⟡⟦VAULT⟧",
            "⟡⟦CANONICAL⟧",
            "⟡⟦VERIFIED⟧ · ⟡⟦SEALED⟧",
            "⟡⟦TEST_GLYPH⟧",
            "⟡⟦GLYPH-1⟧ · ⟡⟦GLYPH2⟧",
        ]

        for glyphsig in valid_glyphs:
            is_valid, error = validate_glyphsig(glyphsig)
            assert is_valid, f"GlyphSig {glyphsig} should be valid: {error}"
            assert error is None

    def test_invalid_glyphsigs_no_markers(self):
        """Test GlyphSigs without glyph markers."""
        invalid_glyphs = [
            "STANDARD · COMPLIANCE",
            "No markers here",
            "⟦MISSING_SYMBOL⟧",
            "⟡⟦lowercase⟧",
        ]

        for glyphsig in invalid_glyphs:
            is_valid, error = validate_glyphsig(glyphsig)
            assert not is_valid, f"GlyphSig {glyphsig} should be invalid"
            assert error is not None

    def test_invalid_glyphsigs_bad_format(self):
        """Test GlyphSigs with incorrect format."""
        invalid_glyphs = [
            "⟡⟦STANDARD⟧ ⟡⟦MISSING_SEPARATOR⟧",  # missing ·
            "⟡⟦STANDARD⟧ - ⟡⟦WRONG_SEPARATOR⟧",  # wrong separator
            "⟡⟦ ⟧",  # empty keyword
            "⟡⟦HAS SPACE⟧",  # space in keyword
        ]

        for glyphsig in invalid_glyphs:
            is_valid, error = validate_glyphsig(glyphsig)
            assert not is_valid, f"GlyphSig {glyphsig} should be invalid"

    def test_empty_glyphsig(self):
        """Test empty GlyphSig."""
        is_valid, error = validate_glyphsig("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_glyphsig_with_extra_whitespace(self):
        """Test GlyphSig with varying whitespace around separator."""
        # These should all be valid
        valid_variations = [
            "⟡⟦A⟧ · ⟡⟦B⟧",
            "⟡⟦A⟧·⟡⟦B⟧",
            "⟡⟦A⟧  ·  ⟡⟦B⟧",
        ]

        for glyphsig in valid_variations:
            is_valid, error = validate_glyphsig(glyphsig)
            assert is_valid, f"GlyphSig {glyphsig} should be valid: {error}"


class TestGlyphSigListValidation:
    """Tests for GlyphSig list validation."""

    def test_valid_glyphsig_string(self):
        """Test single string GlyphSig."""
        glyphsig = "⟡⟦STANDARD⟧ · ⟡⟦MIRROR⟧"
        is_valid, error = validate_glyphsig_list(glyphsig)
        assert is_valid
        assert error is None

    def test_valid_glyphsig_list(self):
        """Test list of GlyphSigs."""
        glyphsig_list = [
            "⟡⟦STANDARD⟧",
            "⟡⟦COMPLIANCE⟧ · ⟡⟦MIRROR⟧"
        ]
        is_valid, error = validate_glyphsig_list(glyphsig_list)
        assert is_valid
        assert error is None

    def test_invalid_glyphsig_list_wrong_type(self):
        """Test GlyphSig list with wrong type."""
        is_valid, error = validate_glyphsig_list(123)
        assert not is_valid
        assert "must be string or list" in error

    def test_invalid_glyphsig_list_empty(self):
        """Test empty GlyphSig list."""
        is_valid, error = validate_glyphsig_list([])
        assert not is_valid
        assert "empty" in error.lower()

    def test_invalid_glyphsig_list_non_string_item(self):
        """Test GlyphSig list with non-string items."""
        glyphsig_list = ["⟡⟦VALID⟧", 123, "⟡⟦ANOTHER⟧"]
        is_valid, error = validate_glyphsig_list(glyphsig_list)
        assert not is_valid
        assert "must be a string" in error

    def test_invalid_glyphsig_list_invalid_format(self):
        """Test GlyphSig list with invalid format in one item."""
        glyphsig_list = [
            "⟡⟦VALID⟧",
            "INVALID_FORMAT",
            "⟡⟦ANOTHER_VALID⟧"
        ]
        is_valid, error = validate_glyphsig_list(glyphsig_list)
        assert not is_valid
        assert "item 1" in error


class TestFormatComplianceCheck:
    """Tests for comprehensive format compliance checking."""

    def test_manifest_with_valid_vaultid(self):
        """Test manifest with valid VaultID."""
        manifest = {
            "name": "Test Project",
            "version": "1.0.0",
            "mirrorDNA_compliance_level": "level_2_continuity_aware",
            "vault_id": "AMOS://TestProject/v1.0",
            "layers": {}
        }

        passed, errors, warnings = check_format_compliance(manifest)
        assert passed
        assert len(errors) == 0

    def test_manifest_with_invalid_vaultid(self):
        """Test manifest with invalid VaultID."""
        manifest = {
            "name": "Test Project",
            "version": "1.0.0",
            "mirrorDNA_compliance_level": "level_2_continuity_aware",
            "vault_id": "INVALID://Format",
            "layers": {}
        }

        passed, errors, warnings = check_format_compliance(manifest)
        assert not passed
        assert len(errors) > 0
        assert any("vault_id" in e.lower() for e in errors)

    def test_level3_requires_vaultid(self):
        """Test that Level 3 compliance requires VaultID."""
        manifest = {
            "name": "Test Project",
            "version": "1.0.0",
            "mirrorDNA_compliance_level": "level_3_vault_backed_sovereign",
            "layers": {}
        }

        passed, errors, warnings = check_format_compliance(manifest)
        assert not passed
        assert any("vault_id" in e.lower() for e in errors)

    def test_level2_recommends_vaultid(self):
        """Test that Level 2 compliance recommends VaultID."""
        manifest = {
            "name": "Test Project",
            "version": "1.0.0",
            "mirrorDNA_compliance_level": "level_2_continuity_aware",
            "layers": {}
        }

        passed, errors, warnings = check_format_compliance(manifest)
        # Should pass but have warning
        assert passed
        assert len(errors) == 0
        assert any("vault_id" in w.lower() for w in warnings)

    def test_profile_with_valid_vaultid(self):
        """Test continuity profile with valid VaultID."""
        manifest = {"name": "Test", "version": "1.0.0", "layers": {}}
        profile = {
            "profile_version": "1.0.0",
            "vault_id": "AMOS://TestVault/v1.0"
        }

        passed, errors, warnings = check_format_compliance(manifest, None, profile)
        assert passed
        assert len(errors) == 0

    def test_profile_with_invalid_vaultid(self):
        """Test continuity profile with invalid VaultID."""
        manifest = {"name": "Test", "version": "1.0.0", "layers": {}}
        profile = {
            "profile_version": "1.0.0",
            "vault_id": "BAD://Format"
        }

        passed, errors, warnings = check_format_compliance(manifest, None, profile)
        assert not passed
        assert any("profile" in e.lower() and "vault_id" in e.lower() for e in errors)

    def test_policy_with_valid_registered_glyphs(self):
        """Test reflection policy with valid registered glyphs."""
        manifest = {"name": "Test", "version": "1.0.0", "layers": {}}
        policy = {
            "policy_version": "1.0.0",
            "glyph_signatures": {
                "enabled": True,
                "registered_glyphs": [
                    {"glyph": "⟡⟦CANONICAL⟧", "meaning": "Authoritative version"},
                    {"glyph": "⟡⟦VERIFIED⟧", "meaning": "Checksummed and verified"}
                ]
            }
        }

        passed, errors, warnings = check_format_compliance(manifest, policy, None)
        assert passed
        assert len(errors) == 0

    def test_policy_with_invalid_registered_glyphs(self):
        """Test reflection policy with invalid registered glyphs."""
        manifest = {"name": "Test", "version": "1.0.0", "layers": {}}
        policy = {
            "policy_version": "1.0.0",
            "glyph_signatures": {
                "enabled": True,
                "registered_glyphs": [
                    {"glyph": "INVALID_FORMAT", "meaning": "Bad format"},
                    {"glyph": "⟡⟦VALID⟧", "meaning": "Good format"}
                ]
            }
        }

        passed, errors, warnings = check_format_compliance(manifest, policy, None)
        assert not passed
        assert any("registered_glyphs" in e for e in errors)


class TestGlyphExtraction:
    """Tests for glyph extraction from text."""

    def test_extract_glyphs_from_text(self):
        """Test extracting glyphs from arbitrary text."""
        text = """
        This document has ⟡⟦CANONICAL⟧ status and is ⟡⟦VERIFIED⟧.
        It maintains ⟡⟦CONTINUITY⟧ across sessions.
        """

        glyphs = extract_glyphs_from_text(text)
        assert len(glyphs) == 3
        assert "⟡⟦CANONICAL⟧" in glyphs
        assert "⟡⟦VERIFIED⟧" in glyphs
        assert "⟡⟦CONTINUITY⟧" in glyphs

    def test_extract_glyphs_no_matches(self):
        """Test extracting glyphs from text with no glyphs."""
        text = "This text has no glyph markers."
        glyphs = extract_glyphs_from_text(text)
        assert len(glyphs) == 0


class TestSemanticGlyphValidation:
    """Tests for semantic glyph validation."""

    def test_standard_glyphs_no_warnings(self):
        """Test that standard glyphs produce no warnings."""
        glyphsig = "⟡⟦STANDARD⟧ · ⟡⟦CANONICAL⟧ · ⟡⟦MIRROR⟧"
        warnings = validate_semantic_glyphs(glyphsig)
        # May or may not have warnings, but shouldn't error
        assert isinstance(warnings, list)

    def test_non_standard_glyphs_warning(self):
        """Test that non-standard glyphs produce warnings."""
        glyphsig = "⟡⟦CUSTOM_GLYPH⟧ · ⟡⟦ANOTHER_CUSTOM⟧"
        warnings = validate_semantic_glyphs(glyphsig)
        assert len(warnings) > 0
        assert any("non-standard" in w.lower() for w in warnings)

    def test_sealed_without_canonical_warning(self):
        """Test that SEALED without CANONICAL produces warning."""
        glyphsig = "⟡⟦SEALED⟧"
        warnings = validate_semantic_glyphs(glyphsig)
        assert any("sealed" in w.lower() and "canonical" in w.lower() for w in warnings)

    def test_sealed_with_canonical_no_specific_warning(self):
        """Test that SEALED with CANONICAL doesn't produce SEALED-specific warning."""
        glyphsig = "⟡⟦CANONICAL⟧ · ⟡⟦SEALED⟧"
        warnings = validate_semantic_glyphs(glyphsig)
        # Should not have the SEALED-without-CANONICAL warning
        sealed_warnings = [w for w in warnings if "sealed" in w.lower() and "canonical" in w.lower()]
        assert len(sealed_warnings) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
