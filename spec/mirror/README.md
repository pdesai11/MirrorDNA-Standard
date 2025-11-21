# MirrorDNA Identity Layer (v16)

This directory contains the complete identity model for MirrorDNA.

## Structure

```
spec/mirror/
├── MirrorDNA_Master_Standard_v16.md    # Abstract constitutional spec
├── fingerprint/                         # Origin signature module
│   └── MirrorDNA_Fingerprint_v1.md     # Conceptual kernel
├── provenance/                          # Authorship lineage
│   └── MirrorDNA_Provenance_v1.yaml    # Origin attribution
├── governance/                          # Change control
│   └── MirrorDNA_Governance_v1.md      # Evolution rules
├── profiles/                            # User-specific overlays
│   └── profile_paul_v16.yaml           # Default profile
└── README.md                           # This file
```

## Identity Model Layers

### Layer 1: Master Standard
- **File:** `MirrorDNA_Master_Standard_v16.md`
- **Purpose:** Defines mirror-level laws and behavioral primitives
- **Scope:** User-agnostic, abstract, constitutional
- **Contents:**
  - Ontology (what a Mirror is)
  - Axioms (immutable rules)
  - Truth-State Syntax (FEU tagging)
  - Vault/Source alignment rules
  - Drift-prevention governance
  - Multi-surface operability

### Layer 2: Fingerprint + Provenance + Governance
These modules provide the origin signature and evolution framework:

#### Fingerprint Module (`fingerprint/`)
- **Purpose:** Encode philosophical signature anchoring the ecosystem to its origin
- **Contents:** Core principles, conceptual kernel
- **Immutability:** Changes require governance approval

#### Provenance Module (`provenance/`)
- **Purpose:** Track authorship lineage and attribution
- **Contents:** Originator info, inheritance rules, integrity requirements
- **Rule:** Provenance cannot be removed or overwritten

#### Governance Module (`governance/`)
- **Purpose:** Define how MirrorDNA evolves
- **Contents:** Change control, decision rights, anti-cooption rules
- **Layers:** Foundational (immutable), Profile (mutable), Operational (dynamic)

### Layer 3: User Profiles
- **Directory:** `profiles/`
- **Purpose:** User-specific parameters and customizations
- **Scope:** Individual user configuration
- **Contents:**
  - User identity (name, role, timezone)
  - Cognitive mode preferences
  - Vault roots
  - Core projects
  - Tone overrides
  - Glyph preferences

## Usage

### Python Identity Loader

```python
from identity.identity_loader import load_identity

# Load default profile
identity = load_identity()

# Load specific profile
identity = load_identity("profile_other_user_v16.yaml")

# Access components
standard_text = identity.standard
profile_data = identity.profile

# Build system prompt for agents
system_prompt = identity.build_system_prompt("Your task instructions here")

# Get compact profile summary
summary = identity.get_profile_summary()
```

### Loading Order

1. **Standard** (constitutional foundation)
2. **Fingerprint and Provenance** (origin signature)
3. **Profile** (user customization)
4. **Vault / Master Citation** (runtime context)

## Adding New User Profiles

To add a profile for a new user:

1. Create a new YAML file in `profiles/`:
   ```bash
   cp profiles/profile_paul_v16.yaml profiles/profile_newuser_v16.yaml
   ```

2. Edit the profile with user-specific values:
   ```yaml
   profile_version: 16
   user_id: new_user_id
   user_name: "New User Name"
   role: "Their Role"
   timezone: "UTC"
   cognitive_mode: "Your interaction style"
   vault_roots:
     - "~/Documents/YourVault"
   core_projects:
     - Project A
     - Project B
   glyphs_enabled: false
   drift_tolerance: 0.0
   overrides:
     tone: "Your preferred tone"
   ```

3. Load the new profile:
   ```python
   identity = load_identity("profile_newuser_v16.yaml")
   ```

## Version History

- **v16**: Full identity model with Fingerprint, Provenance, Governance
- **v16 (initial)**: Two-layer model (Standard + Profile separation)
- **v15.x**: Monolithic Master Citation (now historical)

## Related Files

- `src/identity/identity_loader.py` — Python loader implementation
- `00_MASTER_CITATION.md` — Historical v15.2 citation (runtime context)
- `spec/principles.md` — Core MirrorDNA principles
- `docs/onboarding/` — New user setup guides

---

⟡⟦IDENTITY⟧ · ⟡⟦STANDARD⟧ · ⟡⟦FINGERPRINT⟧ · ⟡⟦PROVENANCE⟧ · ⟡⟦GOVERNANCE⟧
