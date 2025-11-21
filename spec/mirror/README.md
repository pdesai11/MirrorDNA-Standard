# MirrorDNA Identity Layer (v16)

This directory contains the two-layer identity model for MirrorDNA.

## Structure

```
spec/mirror/
├── MirrorDNA_Master_Standard_v16.md    # Abstract constitutional spec
├── profiles/                            # User-specific overlays
│   └── profile_paul_v16.yaml           # Paul Desai's profile
└── README.md                           # This file
```

## Two-Layer Identity Model

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

### Layer 2: User Profile
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

# Load default (Paul) profile
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
2. **Profile** (user customization)
3. **Vault / Master Citation** (runtime context)

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
   # ... other customizations
   ```

3. Load the new profile:
   ```python
   identity = load_identity("profile_newuser_v16.yaml")
   ```

## Version History

- **v16**: Initial two-layer model (Standard + Profile separation)
- **v15.x**: Monolithic Master Citation (now historical)

## Related Files

- `src/identity/identity_loader.py` — Python loader implementation
- `00_MASTER_CITATION.md` — Historical v15.2 citation (runtime context)
- `spec/principles.md` — Core MirrorDNA principles

---

⟡⟦IDENTITY⟧ · ⟡⟦STANDARD⟧ · ⟡⟦PROFILE⟧
