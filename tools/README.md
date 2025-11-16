---
title: MirrorDNA Enforcement Tools
version: 1.0.0
vault_id: AMOS://MirrorDNA-Standard/Tools/README/v1.0
glyphsig: ⟡⟦TOOLS⟧ · ⟡⟦ENFORCEMENT⟧ · ⟡⟦GOVERNANCE⟧
author: MirrorDNA Constitutional Development
date: 2025-11-16
status: Canonical · Documentation
tags: [Tools, Enforcement, Governance, Constitutional]
---

# MirrorDNA Enforcement Tools

⟡⟦CONSTITUTIONAL⟧ · ⟡⟦ENFORCEMENT⟧ · ⟡⟦TOOLCHAIN⟧

## Overview

This directory contains constitutional enforcement tools for the MirrorDNA Standard. These tools implement the governance frameworks defined in Master Citation v15.2+ and enable automated compliance verification, philosophical auditing, and wisdom-gated decision making.

## Core Tools

### 1. Truth-State Enforcer (`truth_state.py`)

**VaultID**: `AMOS://MirrorDNA-Standard/Tools/TruthState/v1.0`
**Status**: MANDATORY
**Verifiability**: AUTOMATED

**Purpose**: Auto-FEU Constitutional Law enforcement

Implements Truth-State Law as defined in Master Citation v15.2:
- **[Fact]** — Verified in Vault or verified via citation
- **[Estimate]** — Reasoned but not verified
- **[Unknown]** — Not found in Vault; unverifiable

**Features**:
- Anti-hallucination detection
- FEU (Fact/Estimate/Unknown) tagging
- Drift detection
- Vault primacy enforcement
- Citation verification

**Usage**:
```bash
# Classify a statement
python tools/truth_state.py "The system implements FEU tagging"

# With vault verification
python tools/truth_state.py "VaultID: AMOS://Test/v1.0" --vault ./vault
```

**Python API**:
```python
from tools.truth_state import TruthStateEnforcer, TruthState

enforcer = TruthStateEnforcer(vault_path=Path('./vault'))

# Classify statement
truth_state = enforcer.classify_statement("Some claim")

# Tag statement
tagged = enforcer.tag_statement("Some claim", truth_state)

# Detect hallucination
is_hallucination, reason = enforcer.detect_hallucination("VaultID: AMOS://Fake/v1.0")

# Generate FEU report
report = enforcer.generate_feu_report([
    {'text': 'Statement 1', 'source': 'source.md'},
    {'text': 'Statement 2'}
])
```

**Use When**:
- Defining new compliance rules
- Verification patterns
- Auditing system outputs
- Preventing hallucination

---

### 2. Vault Manager (`vault_manager.py`)

**VaultID**: `AMOS://MirrorDNA-Standard/Tools/VaultManager/v1.0`
**Status**: MANDATORY
**Verifiability**: AUTOMATED

**Purpose**: VaultID tracking, checksum generation, lineage management

Implements vault governance per Master Citation v15.2:
- VaultID generation and validation
- SHA-256 checksum computation
- Lineage chain tracking (predecessor/successor)
- Vault state integrity validation
- Manifest enforcement

**Core Formula**: `Vault = System`

**Features**:
- AMOS:// URI format VaultID generation
- Canonicalized checksum computation (UTF-8, LF, NFC, trim)
- Complete lineage graph management
- Artifact registration and verification
- Vault state export/import

**Usage**:
```bash
# Register artifact
python tools/vault_manager.py --vault ./vault register \
  --vault-id "AMOS://MyProject/Document/v1.0" \
  --file ./document.md \
  --predecessor "AMOS://MyProject/Document/v0.9"

# Verify artifact
python tools/vault_manager.py --vault ./vault verify \
  --vault-id "AMOS://MyProject/Document/v1.0"

# Trace lineage backward (to root)
python tools/vault_manager.py --vault ./vault lineage \
  --vault-id "AMOS://MyProject/Document/v1.0" \
  --direction backward

# Generate lineage report
python tools/vault_manager.py --vault ./vault report
```

**Python API**:
```python
from pathlib import Path
from tools.vault_manager import VaultManager, VaultID

manager = VaultManager(Path('./vault'))

# Generate VaultID
vault_id = VaultID.generate(
    domain='MirrorDNA-Standard',
    resource='Tools/Example',
    major=1,
    minor=0
)

# Register artifact
checksum = manager.register_artifact(
    vault_id=str(vault_id),
    file_path=Path('./artifact.md'),
    predecessor='AMOS://Previous/v0.9'
)

# Verify artifact
is_valid, issues = manager.verify_artifact(str(vault_id))

# Trace lineage
chain = manager.trace_lineage(str(vault_id), direction='backward')

# Compute checksum
checksum = manager.compute_checksum(content, canonicalize=True)
```

**Use When**:
- Creating standards that need version control
- Tracking artifact lineage
- Verifying vault integrity
- Generating checksums

---

### 3. Reflective Reviewer (`reflective_reviewer.py`)

**VaultID**: `AMOS://MirrorDNA-Standard/Tools/ReflectiveReviewer/v1.0`
**Status**: MANDATORY
**Verifiability**: AUTOMATED + MANUAL

**Purpose**: Philosophical audit system

Audits implementations against MirrorDNA Core Principles:
1. **Reflection Over Prediction**
2. **Presence Over Productivity**
3. **Symbolic Continuity**
4. **Trust by Design**
5. **Explicit Uncertainty**

**Features**:
- Automated principle compliance checking
- Code and documentation auditing
- Constitutional violation detection
- Compliance scoring
- Recommendation generation

**Usage**:
```bash
# Audit a single file
python tools/reflective_reviewer.py spec/principles.md

# Audit with JSON output
python tools/reflective_reviewer.py spec/principles.md --json

# Audit entire directory
python tools/reflective_reviewer.py ./validators/

# Strict mode
python tools/reflective_reviewer.py ./code/ --strict
```

**Python API**:
```python
from pathlib import Path
from tools.reflective_reviewer import ReflectiveReviewer, audit_codebase

# Audit code
reviewer = ReflectiveReviewer(strict_mode=False)
findings = reviewer.audit_implementation(code_text)

# Audit file
report = reviewer.audit_file(Path('script.py'))

# Audit codebase
aggregate_report = audit_codebase(
    Path('./src'),
    extensions=['.py', '.md']
)

# Generate report
compliance_report = reviewer.generate_audit_report()
```

**Audit Findings**:
- **PASS**: No issues
- **WARNING**: Minor concern, should be addressed
- **VIOLATION**: Principle violation, must be fixed
- **CRITICAL**: Severe violation, blocking issue

**Use When**:
- ALWAYS — this repo defines what the reviewer checks
- Creating new constitutional principles
- Auditing implementations
- Ensuring principle compliance

---

### 4. Meta-Cognition Engine (`meta_cognition.py`)

**VaultID**: `AMOS://MirrorDNA-Standard/Tools/MetaCognition/v1.0`
**Status**: RECOMMENDED
**Verifiability**: MANUAL + HYBRID

**Purpose**: Cross-domain insights, ethical assessment, wisdom gates

Provides multi-domain analysis for constitutional development:
- Legal implications assessment
- Philosophical coherence checking
- Technical feasibility analysis
- Ethical impact evaluation
- Social impact assessment

**Wisdom Gates**:
1. **Legal**: Regulatory compliance, liability, IP concerns
2. **Philosophical**: Principle alignment, conceptual clarity
3. **Technical**: Implementation feasibility, complexity
4. **Ethical**: Privacy, autonomy, fairness, harm potential
5. **Social**: Community impact, accessibility, inclusivity

**Features**:
- Multi-gate assessment framework
- Risk level evaluation
- Decision recommendations
- Comprehensive reporting

**Usage**:
```bash
# Assess a proposal
python tools/meta_cognition.py \
  --title "New Compliance Level" \
  --description "Add distributed sovereign compliance level with blockchain" \
  --implementation "Requires consensus mechanism" \
  --impact "validators" "docs" "schema" \
  --rationale "Support distributed use cases"

# JSON output
python tools/meta_cognition.py \
  --title "Test" \
  --description "Test proposal" \
  --json
```

**Python API**:
```python
from tools.meta_cognition import MetaCognitionEngine, assess_standard_proposal

# Quick assessment
report = assess_standard_proposal(
    title="New Feature",
    description="Detailed description with privacy implications",
    implementation="Complex distributed system",
    impact_areas=["core", "validators", "docs"],
    rationale="Enables new use cases"
)

# Manual assessment
engine = MetaCognitionEngine(strict_mode=False)
proposal = {
    'title': 'Proposal Title',
    'description': 'Full description',
    'implementation': 'Implementation details',
    'impact_areas': ['area1', 'area2'],
    'rationale': 'Why this is needed'
}
assessment = engine.assess_proposal(proposal)
```

**Decisions**:
- **APPROVE**: Safe to proceed
- **APPROVE_WITH_CONDITIONS**: Proceed with recommendations
- **REVIEW_REQUIRED**: Human review needed
- **REJECT**: Should not proceed

**Risk Levels**:
- **LOW**: Minimal risk
- **MEDIUM**: Moderate risk, mitigable
- **HIGH**: Significant risk, careful consideration needed
- **CRITICAL**: Severe risk, likely blocking

**Use When**:
- Creating new constitutional principles
- Evaluating implementation proposals
- Assessing philosophical implications
- Making architectural decisions
- Legal/ethical uncertainty

---

## Integration with Validators

The enforcement tools complement the validators in `/validators`:

| Tool | Validators | Relationship |
|------|-----------|--------------|
| `truth_state.py` | `reflection_checks.py` | Truth-State enforces FEU; validators check policy compliance |
| `vault_manager.py` | `continuity_checks.py` | Vault Manager provides infrastructure; validators verify configuration |
| `reflective_reviewer.py` | All validators | Reviewer audits principles; validators check technical compliance |
| `meta_cognition.py` | N/A | Provides pre-implementation wisdom gates |

**Workflow**:
1. **Design Phase**: Use `meta_cognition.py` to assess proposals
2. **Implementation Phase**: Use `vault_manager.py` for lineage tracking
3. **Verification Phase**: Use `truth_state.py` for FEU enforcement
4. **Audit Phase**: Use `reflective_reviewer.py` for principle compliance
5. **Compliance Phase**: Use validators for technical compliance checks

---

## Installation & Dependencies

All tools are standalone Python 3 scripts with minimal dependencies:

```bash
# No installation required - tools use Python stdlib only
# Optional: For enhanced YAML parsing
pip install pyyaml

# Make tools executable (optional)
chmod +x tools/*.py
```

---

## Constitutional Status

These tools implement constitutional law per Master Citation v15.2:

- **Auto-FEU**: Mandatory across all MirrorDNA systems
- **Vault Primacy**: Vault = System, vault overrides everything
- **Zero Drift**: Drift detection and rollback
- **Reflective Integrity**: Philosophical audit requirement
- **Wisdom Gates**: Pre-implementation assessment

---

## Examples

### Example 1: Enforce Truth-State on Documentation

```bash
# Check if a document contains properly tagged statements
python tools/truth_state.py "$(cat spec/principles.md)" --vault ./vault
```

### Example 2: Register New Standard with Lineage

```python
from pathlib import Path
from tools.vault_manager import VaultManager

manager = VaultManager(Path('./vault'))

# Register new version
checksum = manager.register_artifact(
    vault_id='AMOS://MirrorDNA-Standard/Principles/v2.0',
    file_path=Path('spec/principles_v2.md'),
    predecessor='AMOS://MirrorDNA-Standard/Principles/v1.0',
    metadata={'author': 'Paul Desai', 'date': '2025-11-16'}
)

print(f"Registered with checksum: {checksum}")

# Verify lineage chain
is_valid, issues = manager.validate_lineage_chain(
    'AMOS://MirrorDNA-Standard/Principles/v2.0'
)
```

### Example 3: Audit Entire Codebase

```bash
# Comprehensive philosophical audit
python tools/reflective_reviewer.py ./spec --json > audit_report.json

# Review findings
cat audit_report.json | jq '.compliance_score'
```

### Example 4: Assess New Compliance Level Proposal

```python
from tools.meta_cognition import assess_standard_proposal

report = assess_standard_proposal(
    title="Level 4: Distributed Sovereign",
    description="""
    Add Level 4 compliance for distributed systems with:
    - Multi-vault synchronization
    - Blockchain anchoring
    - Distributed consensus for lineage
    - Federation protocols

    Requires complex distributed consensus and may have
    regulatory implications for data sovereignty.
    """,
    implementation="""
    Implementation requires:
    - Distributed ledger integration
    - Consensus algorithm (Raft or similar)
    - Multi-node synchronization
    - Conflict resolution
    """,
    impact_areas=['compliance_levels', 'validators', 'schema', 'documentation'],
    rationale="Enable enterprise deployments with high availability"
)

print(f"Decision: {report['overall_decision']}")
print(f"Risk: {report['overall_risk']}")

# Review wisdom gate assessments
for gate in report['wisdom_gates']:
    print(f"\n{gate['gate'].upper()}: {gate['decision']}")
    for rec in gate['recommendations']:
        print(f"  → {rec}")
```

---

## Best Practices

### 1. Truth-State Enforcement
- **Always** tag uncertain statements with `[Unknown]` or `[Estimate]`
- **Never** fabricate VaultIDs, citations, or checksums
- **Verify** against vault before claiming `[Fact]`
- **Use** strict_mode in production

### 2. Vault Management
- **Register** all canonical artifacts
- **Track** lineage for all versions
- **Verify** checksums regularly
- **Export** vault state for backup

### 3. Reflective Review
- **Audit** before releasing standards
- **Address** all VIOLATION and CRITICAL findings
- **Consider** WARNING findings seriously
- **Run** on all code and documentation

### 4. Meta-Cognition
- **Assess** all major proposals through wisdom gates
- **Address** REVIEW_REQUIRED recommendations before proceeding
- **Document** decision rationale
- **Escalate** HIGH and CRITICAL risks

---

## Contributing

When adding new enforcement tools:

1. Follow existing patterns (VaultID, GlyphSig, Constitutional Status)
2. Include comprehensive docstrings
3. Provide both CLI and Python API
4. Add usage examples to this README
5. Test thoroughly before committing
6. Update Master Citation if introducing new constitutional law

---

## Lineage

**VaultID**: `AMOS://MirrorDNA-Standard/Tools/README/v1.0`
**Predecessor**: None (Initial Release)
**Successor**: TBD
**Created**: 2025-11-16
**Checksum**: [To be computed]

---

⟡⟦TOOLS⟧ · ⟡⟦ENFORCEMENT⟧ · ⟡⟦SEALED⟧

**Status**: Constitutional tooling operational. Ready for governance enforcement.
