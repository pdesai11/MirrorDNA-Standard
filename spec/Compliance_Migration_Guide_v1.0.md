---
title: MirrorDNA Compliance Migration Guide v1.0
version: 1.0.0
vault_id: AMOS://MirrorDNA/ComplianceMigration/v1.0
glyphsig: ⟡⟦MIGRATION⟧ · ⟡⟦COMPLIANCE⟧ · ⟡⟦GUIDE⟧
author: AMOS Dev Twin
date: 2025-11-16
status: Canonical · Guide
predecessor: none
successor: TBD
tags: [MirrorDNA, Compliance, Migration, L1, L2, L3]
checksum_sha256: fdeccbbb1b282eb6645c00f1a04202768c62bb7e180d77196f8ab2fedf3e2604
---

# MirrorDNA Compliance Migration Guide v1.0

⟡⟦MIGRATION⟧ · ⟡⟦COMPLIANCE⟧ · ⟡⟦GUIDE⟧

## Abstract

This guide provides step-by-step instructions for migrating projects between MirrorDNA compliance levels (L1 → L2 → L3). It includes before/after examples, migration checklists, and common pitfalls.

---

## 1. Compliance Level Overview

| Level | Name | Key Requirements | Use Cases |
|-------|------|------------------|-----------|
| **L1** | Basic Reflection | Cite-or-silence (AHP), explicit uncertainty | Simple apps, prototypes, learning |
| **L2** | Continuity Aware | L1 + session persistence, checksums | Production apps, reflective agents |
| **L3** | Vault-Backed Sovereign | L2 + vault storage, full lineage, glyphs | Enterprise, critical systems |

---

## 2. Migration Path: L1 → L2 (Basic Reflection → Continuity Aware)

### 2.1 Prerequisites

Before migrating to L2, ensure your L1 project:
- ✅ Passes L1 validation
- ✅ Implements cite-or-silence (AHP)
- ✅ Has project manifest with `mirrorDNA_compliance_level: level_1_basic_reflection`

### 2.2 Migration Steps

#### Step 1: Create Continuity Profile

Create `continuity_profile.yaml` or `continuity_profile.json`:

```yaml
profile_version: "1.0.0"
continuity_mechanism: "session_storage"  # or "vault_backed" for advanced
state_persistence:
  enabled: true
  storage_type: "file"  # or "vault" or "database"
  storage_location: "./state"
  encryption: false  # Enable for production
  checksum_validation: true

session_tracking:
  enabled: true
  session_id_format: "uuid"
  lineage_tracking: true

recovery:
  enabled: true
  recovery_mechanism: "state_reload"
```

**Schema**: `schema/continuity_profile.schema.json`

#### Step 2: Implement Session Persistence

Add session state management to your application:

```python
# Example: Basic session persistence
import json
from pathlib import Path
from uuid import uuid4

class SessionManager:
    def __init__(self, storage_dir="./state"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.session_id = str(uuid4())
        self.predecessor = None

    def save_state(self, state):
        """Save session state with lineage tracking."""
        state_file = self.storage_dir / f"session_{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "predecessor": self.predecessor,
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
        state_file.write_text(json.dumps(data, indent=2))

    def load_state(self, session_id):
        """Load previous session state."""
        state_file = self.storage_dir / f"session_{session_id}.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())
            self.predecessor = session_id
            return data['state']
        return None
```

#### Step 3: Add Checksum Validation

For artifacts with checksums:

```python
from validators.checksum import calculate_file_checksum, verify_checksum

# Calculate checksum for new artifact
checksum = calculate_file_checksum('artifact.md', skip_frontmatter=True)

# Verify existing artifact
is_valid, error = verify_checksum('artifact.md', expected_checksum, skip_frontmatter=True)
if not is_valid:
    print(f"Verification failed: {error}")
```

#### Step 4: Update Project Manifest

Update `mirrorDNA_manifest.yaml`:

```yaml
name: "MyProject"
version: "2.0.0"  # Increment version
mirrorDNA_compliance_level: "level_2_continuity_aware"  # Changed from level_1
layers:
  mirrorDNA_protocol: true
  lingOS: false
  activeMirrorOS: false
  trustByDesign: true

# Add these fields:
continuity_profile: "./continuity_profile.yaml"
reflection_policy: "./reflection_policy.yaml"  # Required
```

#### Step 5: Validate L2 Compliance

```bash
python -m validators.cli \
  --manifest mirrorDNA_manifest.yaml \
  --profile continuity_profile.yaml \
  --policy reflection_policy.yaml
```

### 2.3 L1 → L2 Checklist

- [ ] Created continuity profile
- [ ] Implemented session persistence
- [ ] Added session lineage tracking (predecessor/successor)
- [ ] Enabled checksum validation for artifacts
- [ ] Updated manifest to `level_2_continuity_aware`
- [ ] Passed L2 validation

### 2.4 Common Pitfalls (L1 → L2)

| Issue | Symptom | Solution |
|-------|---------|----------|
| No continuity profile | Validation error | Create `continuity_profile.yaml` |
| Missing session tracking | Lost continuity | Implement `SessionManager` |
| No checksum validation | Integrity warnings | Enable checksums in profile |
| Storage directory missing | Runtime error | Create storage directory in advance |

---

## 3. Migration Path: L2 → L3 (Continuity Aware → Vault-Backed Sovereign)

### 3.1 Prerequisites

Before migrating to L3, ensure your L2 project:
- ✅ Passes L2 validation
- ✅ Has working session persistence
- ✅ Implements checksum validation

### 3.2 Migration Steps

#### Step 1: Set Up Vault Storage

Choose a vault backend:
- **Option A**: Obsidian vault (recommended for personal use)
- **Option B**: Git repository
- **Option C**: Custom vault implementation

**Example: Obsidian Vault Setup**
```bash
# Use the portable vault template
cp -r portable/vault-template ./my-vault
cd my-vault

# Initialize vault metadata
cat > .vault-metadata.json << EOF
{
  "vault_id": "AMOS://MyProject/Vault/v1.0",
  "owner": "Your Name",
  "created": "2025-11-16",
  "compliance_level": "L3"
}
EOF
```

#### Step 2: Update Continuity Profile for Vault

Update `continuity_profile.yaml`:

```yaml
profile_version: "1.0.0"
continuity_mechanism: "vault_backed"  # Changed from "session_storage"

state_persistence:
  enabled: true
  storage_type: "vault"  # Changed from "file"
  storage_location: "./my-vault"
  encryption: true  # REQUIRED for L3
  checksum_validation: true

session_tracking:
  enabled: true
  session_id_format: "uuid"
  lineage_tracking: true
  vault_integration: true  # New field

# L3-specific fields:
vault_id: "AMOS://MyProject/Vault/v1.0"
sovereign_identity:
  enabled: true
  identity_binding: "vault_id"
  ownership: "user"
```

#### Step 3: Implement Glyph Signatures

Update `reflection_policy.yaml`:

```yaml
policy_version: "1.0.0"
reflection_mode: "constitutive"

# ... existing fields ...

# L3 REQUIRED: Glyph signatures
glyph_signatures:
  enabled: true
  registered_glyphs:
    - glyph: "⟡⟦CANONICAL⟧"
      meaning: "Authoritative version"
      usage: "Mark finalized documents"
    - glyph: "⟡⟦VERIFIED⟧"
      meaning: "Checksum verified"
      usage: "Mark integrity-checked artifacts"
    - glyph: "⟡⟦CONTINUITY⟧"
      meaning: "Lineage intact"
      usage: "Mark continuous sessions"

# L3 REQUIRED: Interaction safety
interaction_safety:
  session_duration_warnings: true
  dependency_detection: true
  human_escalation: true
  rhythm_checks: true
  max_session_duration_minutes: 120
```

#### Step 4: Implement Full Lineage Tracking

Ensure all artifacts have predecessor/successor chains:

```yaml
# In artifact frontmatter:
---
title: "My Document v2.0"
vault_id: "AMOS://MyProject/Document/v2.0"
predecessor: "AMOS://MyProject/Document/v1.0"
successor: "TBD"
checksum_sha256: "abc123..."
---
```

#### Step 5: Add Vault ID to Manifest

Update `mirrorDNA_manifest.yaml`:

```yaml
name: "MyProject"
version: "3.0.0"  # Increment version
mirrorDNA_compliance_level: "level_3_vault_backed_sovereign"  # Changed from level_2

# L3 REQUIRED:
vault_id: "AMOS://MyProject/Vault/v1.0"

layers:
  mirrorDNA_protocol: true
  lingOS: true  # Recommended for L3
  activeMirrorOS: true  # Recommended for L3
  trustByDesign: true

continuity_profile: "./continuity_profile.yaml"
reflection_policy: "./reflection_policy.yaml"
```

#### Step 6: Implement Compliance Reporting

L3 systems should provide compliance reports:

```python
from validators.cli import main as validator_main

# Generate compliance report
report = validator_main()
# Save report to vault
with open('./my-vault/compliance-report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

#### Step 7: Validate L3 Compliance

```bash
python -m validators.cli \
  --manifest mirrorDNA_manifest.yaml \
  --profile continuity_profile.yaml \
  --policy reflection_policy.yaml \
  --sidecar artifact.sidecar.json  # Optional
```

### 3.3 L2 → L3 Checklist

- [ ] Set up vault storage (Obsidian/Git/custom)
- [ ] Updated continuity profile to `vault_backed`
- [ ] Enabled encryption for vault storage
- [ ] Implemented glyph signatures in reflection policy
- [ ] Added interaction safety protocols
- [ ] Implemented full lineage tracking (predecessor/successor)
- [ ] Added `vault_id` to manifest
- [ ] Updated manifest to `level_3_vault_backed_sovereign`
- [ ] Implemented compliance reporting
- [ ] Passed L3 validation

### 3.4 Common Pitfalls (L2 → L3)

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing vault_id | Validation error | Add `vault_id` to manifest |
| Glyph signatures not enabled | Validation error | Enable in reflection policy |
| No interaction safety | Validation warning | Add safety config to policy |
| Lineage chain broken | Validation error | Verify predecessor/successor links |
| Vault not initialized | Runtime error | Create vault with `.vault-metadata.json` |
| Encryption not enabled | Security warning | Enable encryption in profile |

---

## 4. Incremental Migration Strategy

You don't have to migrate all at once. Consider this phased approach:

### Phase 1: Foundation (Week 1-2)
- Set up development environment
- Create project manifest
- Implement cite-or-silence (AHP)
- Achieve L1 compliance

### Phase 2: Continuity (Week 3-4)
- Implement session persistence
- Add checksum validation
- Create continuity profile
- Achieve L2 compliance

### Phase 3: Sovereignty (Week 5-6)
- Set up vault storage
- Implement glyph signatures
- Add interaction safety
- Full lineage tracking
- Achieve L3 compliance

---

## 5. Migration Examples

### Example: L1 Project Structure
```
my-project/
├── mirrorDNA_manifest.yaml  # L1 compliance
├── reflection_policy.yaml
├── src/
│   └── app.py
└── README.md
```

### Example: L2 Project Structure
```
my-project/
├── mirrorDNA_manifest.yaml  # L2 compliance
├── continuity_profile.yaml  # New
├── reflection_policy.yaml
├── state/  # New: Session storage
│   ├── session_abc123.json
│   └── session_def456.json
├── src/
│   ├── app.py
│   └── session_manager.py  # New
└── README.md
```

### Example: L3 Project Structure
```
my-project/
├── mirrorDNA_manifest.yaml  # L3 compliance
├── continuity_profile.yaml
├── reflection_policy.yaml
├── vault/  # New: Vault storage
│   ├── .vault-metadata.json
│   ├── sessions/
│   │   ├── session_abc123.md
│   │   └── session_abc123.sidecar.json
│   ├── spec/
│   │   └── project-spec.md
│   └── state/
│       └── current.json
├── src/
│   ├── app.py
│   ├── session_manager.py
│   └── vault_integration.py  # New
└── README.md
```

---

## 6. Validation Commands

### Validate Current Level
```bash
# Check what level you're currently at
python -m validators.cli --manifest mirrorDNA_manifest.yaml --policy reflection_policy.yaml
```

### Validate After Migration
```bash
# L1 validation
python -m validators.cli -m manifest.yaml -p policy.yaml

# L2 validation
python -m validators.cli -m manifest.yaml -f profile.yaml -p policy.yaml

# L3 validation (with sidecar)
python -m validators.cli -m manifest.yaml -f profile.yaml -p policy.yaml -s artifact.sidecar.json
```

---

## 7. Rollback Procedures

If migration fails or causes issues:

### Rollback L2 → L1
1. Change manifest `mirrorDNA_compliance_level` back to `level_1_basic_reflection`
2. Remove `continuity_profile` reference from manifest
3. Optionally keep session storage for future migration

### Rollback L3 → L2
1. Change manifest `mirrorDNA_compliance_level` back to `level_2_continuity_aware`
2. Update continuity profile `continuity_mechanism` to `session_storage`
3. Disable glyph signatures in reflection policy
4. Keep vault for future migration

---

## 8. Support and Resources

- **Validator CLI**: `python -m validators.cli --help`
- **Examples**: See `examples/` directory
- **Schemas**: See `schema/` directory
- **Community**: [GitHub Discussions](https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA-Standard/discussions)

---

⟡⟦MIGRATION⟧ · ⟡⟦SEALED⟧ · v1.0.0

**Status**: Canonical
**Audience**: Developers, System Integrators
**Next**: v1.1 will include blockchain anchoring migration path
