# MirrorDNA Validator Architecture

⟡⟦VALIDATORS⟧ · ⟡⟦ARCHITECTURE⟧ · ⟡⟦DOCUMENTATION⟧

## Overview

The MirrorDNA validator system provides comprehensive compliance checking for projects implementing the MirrorDNA Standard. This document describes the architecture, components, and usage patterns.

---

## Component Architecture

```
validators/
├── cli.py                 # Main CLI entry point
├── loader.py              # Schema loading and validation
├── checksum.py            # Checksum calculation and verification
├── report.py              # Report generation and formatting
├── checks/                # Compliance check modules
│   ├── __init__.py
│   ├── format_checks.py       # VaultID and GlyphSig validation
│   ├── reflection_checks.py   # Anti-hallucination measures
│   ├── continuity_checks.py   # Session continuity validation
│   ├── trustbydesign_checks.py # Trust framework validation
│   ├── checksum_checks.py     # Artifact integrity validation
│   └── lineage_checks.py      # Lineage chain validation
└── __init__.py
```

---

## Core Components

### 1. CLI (`cli.py`)

**Purpose**: Command-line interface for validation

**Key Functions**:
- `main()`: Entry point, argument parsing, orchestration
- Loads manifest, profile, policy, sidecar files
- Runs all compliance checks
- Generates and outputs report

**Usage**:
```bash
python -m validators.cli \
  --manifest manifest.yaml \
  --profile profile.yaml \
  --policy policy.yaml \
  --sidecar artifact.sidecar.json
```

**Flags**:
- `-m, --manifest`: Project manifest (required)
- `-f, --profile`: Continuity profile (required for L2+)
- `-p, --policy`: Reflection policy (required for all levels)
- `-s, --sidecar`: Sidecar metadata (optional)
- `--json`: Output as JSON
- `--no-color`: Disable colored output
- `-v, --verbose`: Verbose logging

**Exit Codes**:
- `0`: Validation passed
- `1`: Validation failed or error occurred

---

### 2. Loader (`loader.py`)

**Purpose**: Load and validate configuration files against JSON schemas

**Key Functions**:
- `load_yaml_or_json(file_path)`: Loads YAML or JSON files
- `load_schema(schema_name)`: Loads JSON schema from `schema/` directory
- `validate_against_schema(data, schema)`: Validates data against schema
- `load_and_validate_manifest(path)`: Load + validate manifest
- `load_and_validate_profile(path)`: Load + validate continuity profile
- `load_and_validate_policy(path)`: Load + validate reflection policy
- `load_and_validate_sidecar(path)`: Load + validate sidecar metadata

**Supported Schemas**:
- `project_manifest.schema.json`
- `continuity_profile.schema.json`
- `reflection_policy.schema.json`
- `sidecar.schema.json` _(new)_

---

### 3. Checksum Module (`checksum.py`)

**Purpose**: Calculate and verify SHA-256 checksums for artifacts

**Key Functions**:
- `calculate_file_checksum(file_path, skip_frontmatter=True)`: Calculate SHA-256
  - For `.md` files: skips YAML frontmatter by default
  - Returns 64-char hex string
- `verify_checksum(file_path, expected, skip_frontmatter=True)`: Verify checksum
- `extract_checksum_from_frontmatter(file_path)`: Extract from YAML frontmatter
- `verify_file_with_embedded_checksum(file_path)`: Verify using embedded checksum
- `generate_checksum_report(file_paths)`: Batch verification report

**Algorithm**: SHA-256 (FIPS 180-4)

**Frontmatter Handling**:
For markdown files with YAML frontmatter (delimited by `---`):
1. Skip frontmatter block (including delimiters)
2. Calculate checksum on content after frontmatter
3. Avoids circular dependency (frontmatter contains checksum field)

**Usage Example**:
```python
from validators.checksum import calculate_file_checksum, verify_checksum

# Calculate
checksum = calculate_file_checksum('doc.md', skip_frontmatter=True)

# Verify
is_valid, error = verify_checksum('doc.md', expected_checksum, skip_frontmatter=True)
```

---

### 4. Report Module (`report.py`)

**Purpose**: Generate compliance reports in multiple formats

**Key Classes**:

#### `ComplianceResult`
Dataclass representing a single check result:
- `check_name`: str
- `passed`: bool
- `errors`: List[str]
- `warnings`: List[str]

#### `ComplianceReport`
Dataclass representing complete compliance report:
- `project_name`: str
- `declared_level`: str
- `detected_level`: str
- `overall_passed`: bool
- `results`: List[ComplianceResult]
- `recommendations`: List[str]

**Methods**:
- `format_text()`: Plain text output
- `format_colored()`: ANSI colored output
- `to_dict()`: Dictionary (for JSON serialization)
- `to_json()`: JSON string

**Key Functions**:
- `detect_compliance_level(manifest, profile, policy, errors_by_level)`: Auto-detect achieved level
- `generate_recommendations(declared, detected, report)`: Generate actionable recommendations

---

### 5. Compliance Checks (`checks/`)

All check modules follow the same signature:
```python
def check_*_compliance(
    manifest: Dict[str, Any],
    profile: Dict[str, Any] = None,
    policy: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Returns: (passed, errors, warnings)
    """
```

#### `format_checks.py` _(new)_
**Validates**: VaultID and GlyphSig format compliance

**Key Functions**:
- `validate_vaultid(vault_id)`: Validates `AMOS://Component/Artifact/Version` pattern
- `validate_glyphsig(glyphsig)`: Validates `⟡⟦KEYWORD⟧ · ⟡⟦KEYWORD⟧` pattern
- `validate_glyphsig_list(glyphsig)`: Handles string or list formats
- `check_format_compliance(manifest, policy, profile)`: Main compliance check
- `extract_glyphs_from_text(text)`: Utility for glyph extraction
- `validate_semantic_glyphs(glyphsig, context)`: Semantic consistency warnings

**Patterns**:
- VaultID: `^AMOS://[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*(/v\d+(?:\.\d+)*)?$`
- GlyphSig: `^⟡⟦[A-Z0-9_-]+⟧(?:\s*·\s*⟡⟦[A-Z0-9_-]+⟧)*$`

#### `reflection_checks.py`
**Validates**: Anti-hallucination measures and reflection protocols

**Key Checks**:
- Cite-or-silence (AHP) enabled
- Unknown/speculation markers configured
- Anti-hallucination measures (grounding, source citation)
- Glyph signatures (L3)
- Interaction safety (L3)

#### `continuity_checks.py`
**Validates**: Session continuity and state persistence

**Key Checks**:
- State persistence enabled (L2+)
- Session tracking configured
- Recovery mechanisms in place

#### `trustbydesign_checks.py`
**Validates**: Trust-by-Design framework compliance

**Key Checks**:
- Trust layer configuration
- Security measures
- Verification protocols

#### `checksum_checks.py` _(new)_
**Validates**: Artifact integrity through checksums

**Key Functions**:
- `check_checksum_compliance(manifest, profile, sidecar, manifest_path)`: Main check
- `verify_artifact_checksum(artifact_path)`: Verify single artifact
- `check_sidecar_checksum(sidecar, sidecar_path)`: Verify sidecar references

**Checks**:
- Sidecar has valid checksum
- Referenced files match checksums
- L2+ projects use checksum validation

#### `lineage_checks.py` _(new)_
**Validates**: Lineage chains and predecessor/successor relationships

**Key Functions**:
- `check_lineage_compliance(manifest, profile, sidecar)`: Main check
- `validate_lineage_chain(lineage_items)`: Validate chain consistency
- `detect_lineage_cycles(items)`: Detect circular references

**Checks**:
- Lineage tracking enabled (L2+)
- Predecessor/successor fields present
- No self-referential links
- No broken chains

---

## Validation Flow

```
1. CLI receives arguments
   ↓
2. Load manifest (required)
   ↓
3. Load profile (L2+ required)
   ↓
4. Load policy (required)
   ↓
5. Load sidecar (optional)
   ↓
6. Run compliance checks:
   - Format checks (VaultID, GlyphSig)
   - Continuity checks
   - Reflection checks
   - Trust-by-Design checks
   - Checksum checks (if sidecar present)
   - Lineage checks (if applicable)
   ↓
7. Detect actual compliance level
   ↓
8. Generate recommendations
   ↓
9. Output report (text/colored/JSON)
   ↓
10. Exit with code (0=pass, 1=fail)
```

---

## Relationship to Root `validator.py`

The repository contains **two separate validators**:

### Root `validator.py`
- **Purpose**: Simple frontmatter validator for markdown files
- **Scope**: Validates single markdown file has required frontmatter fields
- **Usage**: `python validator.py <file.md>`
- **Use Case**: Quick validation of individual spec documents

### `validators/` Package
- **Purpose**: Comprehensive MirrorDNA compliance validation
- **Scope**: Validates entire project against MirrorDNA Standard
- **Usage**: `python -m validators.cli --manifest ...`
- **Use Case**: Project-wide compliance certification

**When to Use Which**:
- Use `validator.py` for **quick checks** of spec document formatting
- Use `validators/cli` for **full compliance validation** of projects

---

## Integration Patterns

### CI/CD Integration

```yaml
# Example: GitHub Actions
- name: Validate MirrorDNA Compliance
  run: |
    python -m validators.cli \
      --manifest mirrorDNA_manifest.yaml \
      --profile continuity_profile.yaml \
      --policy reflection_policy.yaml \
      --json > compliance-report.json

- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: compliance-report
    path: compliance-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python -m validators.cli \
  -m mirrorDNA_manifest.yaml \
  -f continuity_profile.yaml \
  -p reflection_policy.yaml

if [ $? -ne 0 ]; then
  echo "MirrorDNA compliance validation failed!"
  exit 1
fi
```

### Python Integration

```python
from validators.cli import main as validate
import sys

# Run validation
exit_code = validate()

if exit_code == 0:
    print("✓ Compliance validated")
else:
    print("✗ Compliance validation failed")
    sys.exit(1)
```

---

## Extension Points

### Adding New Checks

1. Create new module in `validators/checks/`:
```python
# validators/checks/mycustom_checks.py

from typing import Dict, Any, List, Tuple

def check_mycustom_compliance(
    manifest: Dict[str, Any],
    profile: Dict[str, Any] = None,
    policy: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    errors = []
    warnings = []

    # Your validation logic here

    passed = len(errors) == 0
    return passed, errors, warnings
```

2. Export from `validators/checks/__init__.py`:
```python
from .mycustom_checks import check_mycustom_compliance

__all__ = [
    # ... existing exports
    'check_mycustom_compliance',
]
```

3. Integrate into `validators/cli.py`:
```python
from .checks import check_mycustom_compliance

# In main():
passed, errors, warnings = check_mycustom_compliance(manifest, profile, policy)
result = ComplianceResult(
    check_name="My Custom Compliance",
    passed=passed,
    errors=errors,
    warnings=warnings
)
report.add_result(result)
```

### Adding New Schemas

1. Create schema in `schema/`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mirrordna.org/schemas/mycustom.schema.json",
  "title": "My Custom Schema",
  "type": "object",
  "required": ["field1"],
  "properties": {
    "field1": {"type": "string"}
  }
}
```

2. Add loader function in `validators/loader.py`:
```python
def load_and_validate_mycustom(path: str) -> Tuple[Dict[str, Any], List[str]]:
    errors = []
    try:
        data = load_yaml_or_json(path)
    except (FileNotFoundError, ValueError) as e:
        return {}, [str(e)]

    try:
        schema = load_schema('mycustom.schema.json')
        is_valid, schema_errors = validate_against_schema(data, schema)
        if not is_valid:
            errors.extend(schema_errors)
    except FileNotFoundError as e:
        errors.append(str(e))

    return data, errors
```

---

## Testing

Unit tests are located in `tests/`:
- `test_cli.py`: CLI interface tests
- `test_loader.py`: Schema loading tests
- `test_checks.py`: Compliance check tests
- `test_format_checks.py`: Format validation tests

**Run tests**:
```bash
pytest tests/
pytest tests/test_format_checks.py -v
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'jsonschema'`
**Solution**: Install dependencies: `pip install -r validators/requirements.txt`

**Issue**: "Manifest not found"
**Solution**: Provide absolute path or run from project root

**Issue**: "Checksum mismatch"
**Solution**: Recalculate checksum using `validators/checksum.py`

**Issue**: "Invalid VaultID format"
**Solution**: Ensure VaultID follows `AMOS://Component/Artifact/Version` pattern

---

## Future Enhancements

- Blockchain anchoring validation
- Multi-vault synchronization checks
- Advanced glyph kernel integration
- Automated compliance badge generation
- Interactive compliance wizard

---

⟡⟦VALIDATORS⟧ · ⟡⟦ARCHITECTURE⟧ · v1.0.0

**Last Updated**: 2025-11-16
**Author**: AMOS Dev Twin
**Status**: Canonical Documentation
