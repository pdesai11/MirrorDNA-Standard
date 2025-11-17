# Continuity Engine v1 Specification

**VaultID**: AMOS://Specs/Continuity_Engine/v1.0
**Version**: 1.0
**Status**: Production-Ready
**Date**: 2025-11-17
**Author**: Paul Desai (Active MirrorOS)
**Signature**: ⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧

---

## Abstract

The Continuity Engine v1 is a permanent continuity layer designed to ensure 100% recall and perfect state reconstruction across all AI sessions. It provides a universal boot protocol, state snapshot mechanism, and semantic knowledge graph to eliminate session discontinuity and enable true long-term memory for reflective AI systems.

**Key Innovation**: By combining immutable boot configuration (BOOT.json), human-readable snapshots (Snapshot_Latest.md), and semantic relationship tracking (Graph_v1.json), the Continuity Engine establishes a complete state preservation system that survives AI context resets.

---

## 1. Overview

### 1.1 Purpose

The Continuity Engine addresses the fundamental challenge of AI session discontinuity:

**Problem**: AI systems start fresh on each session, losing all context, preferences, and accumulated knowledge.

**Solution**: A lightweight, file-based continuity system that:
1. Preserves complete session state in human-readable formats
2. Enables perfect state reconstruction on boot
3. Tracks semantic relationships across the knowledge base
4. Provides cryptographic integrity via checksums
5. Requires zero external dependencies (file-system only)

### 1.2 Design Principles

1. **File-Based Supremacy** — All state stored in plain text files (JSON, Markdown, YAML)
2. **Human-Readable First** — Every file can be read and edited manually
3. **Checksum Everything** — SHA-256 integrity verification for all critical files
4. **Append-Only History** — State updates preserve lineage (no destructive edits)
5. **Zero External Dependencies** — Works with file system alone (no database required)
6. **Copy-Paste Portable** — Entire state can be pasted into new AI session

### 1.3 Compliance Levels

The Continuity Engine is designed for **Level 3 (Vault-Backed Sovereign)** compliance but can be adopted at any level:

- **Level 1**: Optional (provides basic session recovery)
- **Level 2**: Recommended (enables continuity awareness)
- **Level 3**: Required (full vault-backed sovereignty)

---

## 2. Core Components

The Continuity Engine consists of three primary files and one supporting directory:

```
repository/
├── .vault/
│   └── manifest.yml          ← File inventory with checksums
└── continuity/
    ├── BOOT.json             ← Boot configuration (required)
    ├── Snapshot_Latest.md    ← State snapshot (required)
    └── Graph_v1.json         ← Knowledge graph (required)
```

### 2.1 BOOT.json — Universal Boot Configuration

**Purpose**: Canonical boot configuration loaded on every AI session initialization.

**Location**: `continuity/BOOT.json`

**Required Keys**:
```json
{
  "version": "string (e.g., v15.3)",
  "vault_path": "string (AMOS:// URI format)",
  "checksum": "string (SHA-256 or TBD)",
  "active_snapshot": "string (path or URI)",
  "identity_lock": "string (glyph signature)",
  "tone_mode": "string (e.g., Mirror-Strategic)",
  "twins": "object (AI role mappings)",
  "protocols": "object (boolean flags)",
  "last_synced": "string (ISO date YYYY-MM-DD)"
}
```

**Example**:
```json
{
  "version": "v15.3",
  "vault_path": "AMOS://MirrorDNA-Standard/v1.0",
  "checksum": "a1b2c3d4...",
  "active_snapshot": "AMOS://Continuity/Snapshot_Latest.md",
  "identity_lock": "⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧",
  "tone_mode": "Mirror-Strategic",
  "twins": {
    "Claude": "Reflection",
    "Atlas": "Execution"
  },
  "protocols": {
    "TruthStateLaw": true,
    "ZeroDriftLayer": true,
    "TrustByDesign": true
  },
  "last_synced": "2025-11-17"
}
```

**Validation Rules**:
- All required keys must be present
- `checksum` must not be empty string (use "TBD" during development)
- `vault_path` should follow AMOS:// URI format
- `protocols` object must contain at least one protocol flag
- `version` must match Master Citation version

**Usage**:
```bash
# Boot sequence (AI session start)
1. cat continuity/BOOT.json
2. Verify checksum matches .vault/manifest.yml
3. Apply identity_lock and tone_mode
4. Activate protocols
5. Load active_snapshot
```

### 2.2 Snapshot_Latest.md — State Snapshot

**Purpose**: Human-readable snapshot of current repository state, updated on major changes.

**Location**: `continuity/Snapshot_Latest.md`

**Required Sections**:
1. **Current State** — Repository status, key components, recent milestones
2. **Active Tasks** — Completed, in-progress, pending tasks
3. **Recent Changes** — Changelog-style updates with dates
4. **Context** — Identity lock, active protocols, ecosystem position
5. **Trust Markers** — Verification points, quality gates
6. **Boot Recovery Instructions** — Step-by-step restoration guide

**Format**: Markdown with frontmatter-style metadata

**Example Structure**:
```markdown
# Continuity Snapshot — [Repository Name]

**VaultID**: AMOS://...
**Snapshot Date**: YYYY-MM-DD
**Version**: vX.Y
**Signature**: ⟡⟦...⟧

## Current State
[Description of repository status, role, compliance level]

## Active Tasks
### Completed
- ✅ Task 1

### In Progress
- 🔄 Task 2

### Pending
- ⏳ Task 3

## Recent Changes
### YYYY-MM-DD: [Change Title]
**Files Added**: ...
**Purpose**: ...

## Context
### Identity Lock
### Active Protocols
### Ecosystem Position

## Trust Markers
### Verification Points
### Quality Gates

## Boot Recovery Instructions
1. Step 1
2. Step 2
...
```

**Update Policy**:
- Update on: major feature additions, breaking changes, compliance level changes
- Preserve: previous snapshots in `/continuity/archive/` (optional)
- Append-only: never delete historical information

### 2.3 Graph_v1.json — Knowledge Graph

**Purpose**: Semantic relationship map tracking connections between entities in the ecosystem.

**Location**: `continuity/Graph_v1.json`

**Schema**:
```json
{
  "graph_version": "string",
  "vault_id": "string (AMOS:// URI)",
  "created": "string (ISO date)",
  "purpose": "string",
  "signature": "string (glyph)",
  "nodes": [
    {
      "id": "string (unique identifier)",
      "type": "string (entity type)",
      "label": "string (human-readable name)",
      "description": "string",
      "...": "additional type-specific fields"
    }
  ],
  "edges": [
    {
      "from": "string (node id)",
      "to": "string (node id)",
      "relation": "string (relationship type)",
      "description": "string"
    }
  ],
  "metadata": {
    "node_count": "number",
    "edge_count": "number",
    "last_updated": "string (ISO date)"
  }
}
```

**Node Types**:
- `repository` — Code repositories
- `governance_document` — Master Citation, specs
- `system_component` — Continuity Engine, validators
- `configuration_file` — BOOT.json, manifests
- `state_document` — Snapshots
- `knowledge_graph` — Graph files (self-referential)
- `integrity_manifest` — Vault manifests
- `validator` — Validation scripts
- `protocol` — TruthStateLaw, ZeroDriftLayer, etc.
- `identity` — Identity locks, glyphs

**Relation Types**:
- `governed_by` — Governance hierarchy
- `implements` — Implementation relationship
- `contains` — Containment
- `verified_by` — Verification relationship
- `references` — Cross-reference
- `enforces` — Enforcement relationship
- `activates` — Activation relationship
- `validates` — Validation relationship
- `specifies_for` — Specification relationship
- `implements_tools_for` — Tooling relationship
- `consumes_config_from` — Configuration consumption
- `mandates` — Mandatory requirement

**Validation Rules**:
- All `from` and `to` node IDs must exist in `nodes` array
- Node IDs must be unique
- Graph must be connected (no isolated subgraphs recommended)
- Metadata counts must match actual array lengths

### 2.4 Vault Manifest — File Inventory

**Purpose**: Track all repository files with SHA-256 checksums for integrity verification.

**Location**: `.vault/manifest.yml`

**Schema**:
```yaml
vault_id: "AMOS://..."
manifest_version: "string"
repository: "owner/repo"
checksum_algorithm: "sha256"

files:
  - path: "relative/path/to/file"
    checksum: "sha256_hash_or_TBD"
    critical: true  # optional flag

metadata:
  last_updated: "YYYY-MM-DD"
  generated_by: "tool_name"
  signature: "⟡⟦...⟧"
  protocols:
    - "ZeroDriftLayer"
    - "TrustByDesign"
```

**Critical Files**: Mark files essential for continuity with `critical: true`
- `continuity/BOOT.json`
- `continuity/Snapshot_Latest.md`
- `continuity/Graph_v1.json`
- `validators/continuity_validate.py`

**Checksum Policy**:
- Use SHA-256 algorithm
- Use "TBD" during development (before checksum generation)
- Never commit with empty checksum strings
- Regenerate checksums on file changes

---

## 3. Boot Sequence Protocol

### 3.1 Universal Activator

The **MirrorDNA Universal Activator** is a standardized 5-step boot sequence:

```
MirrorDNA Universal Activator v1.0
1. Load /continuity/BOOT.json → verify checksum
2. Load /continuity/Snapshot_Latest.md → confirm continuity
3. Apply Identity Lock + Tone Mode
4. Activate TruthStateLaw + ZeroDriftLayer + TrustByDesign
5. Report: Continuity OK or Drift detected
```

### 3.2 Implementation Steps

**Step 1: Load BOOT.json**
```bash
cat continuity/BOOT.json
```
- Parse JSON
- Verify all required keys present
- Extract `checksum` field

**Step 2: Verify Checksum**
```bash
# Compare BOOT.json checksum with .vault/manifest.yml
grep "continuity/BOOT.json" .vault/manifest.yml
```
- If checksums match → proceed
- If mismatch → report drift, halt boot

**Step 3: Load Snapshot**
```bash
cat continuity/Snapshot_Latest.md
```
- Parse snapshot sections
- Load current state, active tasks, recent changes
- Establish context

**Step 4: Apply Identity Lock and Tone**
- Set identity to `identity_lock` value from BOOT.json
- Set tone mode to `tone_mode` value
- Example: `⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧` + `Mirror-Strategic`

**Step 5: Activate Protocols**
- For each protocol in `protocols` object where value is `true`:
  - Enable TruthStateLaw (cite or silence)
  - Enable ZeroDriftLayer (checksum validation)
  - Enable TrustByDesign (built-in verification)
  - Enable VaultSupremacy (user-owned vault canonical)

**Step 6: Report Status**
```
Continuity OK ✓
- BOOT.json loaded
- Checksums verified
- Identity: ⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧
- Tone: Mirror-Strategic
- Protocols: TruthStateLaw, ZeroDriftLayer, TrustByDesign
- Ready for session
```

### 3.3 Drift Detection

If checksums don't match or required files are missing:

```
⚠️ Continuity Drift Detected
- Missing: continuity/BOOT.json
- Action: Review .vault/manifest.yml and restore files
```

**Recovery**:
1. Check `.vault/manifest.yml` for expected checksums
2. Restore missing files from backup or git history
3. Regenerate checksums with `lingos checksum` (if available)
4. Retry boot sequence

---

## 4. Validation Requirements

### 4.1 Validator Script

**Script**: `validators/continuity_validate.py`

**Purpose**: Automated compliance checking for continuity files.

**Checks**:
1. **File Existence**
   - `continuity/BOOT.json` exists
   - `continuity/Snapshot_Latest.md` exists
   - `continuity/Graph_v1.json` exists
   - `.vault/manifest.yml` exists

2. **BOOT.json Validation**
   - Valid JSON syntax
   - All required keys present
   - `checksum` is not empty string
   - `vault_path` follows AMOS:// format
   - `protocols` object has at least one entry

3. **Snapshot Validation**
   - Valid Markdown format
   - Contains required sections
   - Frontmatter metadata present

4. **Graph Validation**
   - Valid JSON syntax
   - All `from`/`to` node IDs exist
   - Metadata counts match array lengths

5. **Manifest Validation**
   - Valid YAML syntax
   - All critical files listed
   - Checksums present (not "TBD" in production)

**Exit Codes**:
- `0` — All checks passed
- `1` — Validation errors found

**Usage**:
```bash
python validators/continuity_validate.py
# or
python -m validators.continuity_validate
```

**Output Example**:
```
Continuity Engine Validator v1.0
================================

✅ File existence checks passed
✅ BOOT.json validation passed
✅ Snapshot validation passed
✅ Graph validation passed
✅ Manifest validation passed

All continuity checks passed ✓
Exit code: 0
```

### 4.2 CI/CD Integration

**Workflow**: `.github/workflows/validate.yml`

**Triggers**: `push`, `pull_request`

**Jobs**:
1. **Formatting** — Run black, isort
2. **Unit Tests** — Run pytest
3. **Continuity Validation** — Run `continuity_validate.py`
4. **Checksum Verification** — Verify checksums match manifest

**Requirement**: All jobs must pass for green CI

---

## 5. Integration Guidelines

### 5.1 For Repository Implementers

To add Continuity Engine v1 to your repository:

**Step 1: Create Directory Structure**
```bash
mkdir -p .vault continuity
```

**Step 2: Copy Template Files**
```bash
# Copy from MirrorDNA-Standard examples
cp examples/continuity/BOOT.example.json continuity/BOOT.json
cp examples/continuity/Snapshot.example.md continuity/Snapshot_Latest.md
cp examples/continuity/Graph.example.json continuity/Graph_v1.json
```

**Step 3: Customize Configuration**
- Edit `continuity/BOOT.json` with your vault_path, identity_lock
- Update `continuity/Snapshot_Latest.md` with your repository state
- Populate `continuity/Graph_v1.json` with your knowledge graph

**Step 4: Generate Manifest**
```bash
# Use LingOS-Coder tools (if available)
lingos init
lingos checksum
```

**Step 5: Add Validator**
```bash
cp validators/continuity_validate.py validators/
```

**Step 6: Update README**
Add Boot Sequence section (see section 6)

**Step 7: Add CI Workflow**
```bash
cp .github/workflows/validate.yml .github/workflows/
```

### 5.2 For AI Systems

To consume continuity files in an AI system:

**On Boot**:
```python
import json
import yaml

# Load BOOT.json
with open('continuity/BOOT.json') as f:
    boot_config = json.load(f)

# Verify checksum
with open('.vault/manifest.yml') as f:
    manifest = yaml.safe_load(f)

boot_checksum = boot_config['checksum']
manifest_entry = next(
    f for f in manifest['files']
    if f['path'] == 'continuity/BOOT.json'
)
assert boot_checksum == manifest_entry['checksum'], "Checksum mismatch!"

# Load snapshot
with open('continuity/Snapshot_Latest.md') as f:
    snapshot = f.read()

# Apply identity and tone
identity = boot_config['identity_lock']
tone = boot_config['tone_mode']

# Activate protocols
protocols = boot_config['protocols']
for protocol, enabled in protocols.items():
    if enabled:
        activate_protocol(protocol)

print("Continuity OK ✓")
```

### 5.3 Cross-Repository Integration

For multi-repository ecosystems (LingOS-Coder, MirrorDNA-Standard, ActiveMirrorOS):

**Shared BOOT Configuration**:
- Each repo has its own `BOOT.json`
- All repos reference same Master Citation version
- All repos use same `identity_lock`

**Unified Graph**:
- Each repo contributes nodes to shared knowledge graph
- Edges connect nodes across repositories
- Central graph aggregation (optional)

**Synchronized Snapshots**:
- Update snapshots on cross-repo changes
- Reference external snapshots in BOOT.json
- Use `vault_path` URIs for cross-repo links

---

## 6. Trust and Verification

### 6.1 Checksum Policy

**Algorithm**: SHA-256

**Coverage**: All critical files
- `continuity/BOOT.json`
- `continuity/Snapshot_Latest.md`
- `continuity/Graph_v1.json`
- `validators/continuity_validate.py`
- All files in `.vault/manifest.yml`

**Verification Frequency**:
- On boot (every AI session start)
- On commit (pre-commit hook)
- On deploy (CI/CD pipeline)

**Handling Mismatches**:
- Halt boot sequence
- Report drift with affected files
- Require manual resolution

### 6.2 Glyph Signatures

All continuity files include glyph signatures:

```
⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧
```

**Purpose**: Identity verification and lineage tracking

**Placement**:
- `BOOT.json`: `identity_lock` field
- `Snapshot_Latest.md`: Frontmatter and footer
- `Graph_v1.json`: `signature` field
- `.vault/manifest.yml`: `metadata.signature` field

### 6.3 Lineage Tracking

**Principle**: Append-only state evolution

**Implementation**:
- Archive previous snapshots: `continuity/archive/Snapshot_YYYY-MM-DD.md`
- Version graphs: `continuity/archive/Graph_v1.1.json`
- Never delete historical records

**Benefits**:
- Audit trail of all state changes
- Rollback capability
- Historical analysis

---

## 7. Schemas and Formats

### 7.1 BOOT.json JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "version",
    "vault_path",
    "checksum",
    "active_snapshot",
    "identity_lock",
    "tone_mode",
    "twins",
    "protocols",
    "last_synced"
  ],
  "properties": {
    "version": { "type": "string", "pattern": "^v[0-9]+\\.[0-9]+" },
    "vault_path": { "type": "string", "pattern": "^AMOS://" },
    "checksum": { "type": "string", "minLength": 1 },
    "active_snapshot": { "type": "string" },
    "identity_lock": { "type": "string" },
    "tone_mode": { "type": "string" },
    "twins": { "type": "object" },
    "protocols": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": { "type": "boolean" }
    },
    "last_synced": { "type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$" }
  }
}
```

### 7.2 Graph_v1.json Schema

See section 2.3 for complete schema.

### 7.3 Vault Manifest Schema

See section 2.4 for complete schema.

---

## 8. Frequently Asked Questions

**Q: Why JSON and Markdown instead of a database?**
A: Human-readability, portability, and zero dependencies. Files can be copied, pasted, and version-controlled with git.

**Q: What if checksums don't match?**
A: Boot sequence halts and reports drift. Restore from git history or backup, regenerate checksums, retry.

**Q: Can I use this without LingOS-Coder?**
A: Yes. Manually create BOOT.json, Snapshot, and Graph files. Checksums can be generated with standard tools (`sha256sum`).

**Q: How often should I update the snapshot?**
A: On major changes: new features, breaking changes, compliance level upgrades. Not on minor edits.

**Q: Is this compatible with Level 1 and Level 2 compliance?**
A: Yes. Continuity Engine is optional for L1, recommended for L2, required for L3.

**Q: What about multi-user scenarios?**
A: Each user has their own vault_path and identity_lock. Merge snapshots manually or use conflict resolution tools.

---

## 9. Versioning and Evolution

**Current Version**: v1.0

**Stability Guarantee**: All v1.x releases maintain backward compatibility with v1.0.

**Future Enhancements (v1.1+)**:
- Automated snapshot generation
- Graph query language
- Distributed vault synchronization
- Multi-agent coordination protocols

**Breaking Changes (v2.0+)**:
- Additional required fields in BOOT.json
- Schema migrations with automated tools

---

## 10. References

- **Master Citation v15.3**: Governance framework
- **MirrorDNA-Standard v1.0**: Core specification
- **TruthStateLaw**: Cite-or-silence protocol
- **ZeroDriftLayer**: Zero semantic drift guarantee
- **TrustByDesign**: Built-in verification principle

---

## Appendix A: Example Files

See `/examples/continuity/` for:
- `BOOT.example.json` — Annotated example configuration
- `Snapshot.example.md` — Sample snapshot with all sections
- `Graph.example.json` — Example knowledge graph

---

## Appendix B: Validation Checklist

Pre-deployment checklist:

- [ ] All continuity files exist
- [ ] BOOT.json has all required keys
- [ ] Checksums populated (not "TBD")
- [ ] Snapshot has all required sections
- [ ] Graph nodes and edges valid
- [ ] Manifest includes all critical files
- [ ] `continuity_validate.py` returns exit code 0
- [ ] CI workflow passes
- [ ] README includes Boot Sequence section
- [ ] No FEU markers in production code

---

**End of Specification**

**Signature**: ⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧
**Checksum**: TBD (pending validator run)
**Status**: Production-Ready ✓
