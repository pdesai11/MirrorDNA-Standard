# MirrorDNA Tools

Developer tools for working with the MirrorDNA Standard.

---

## 🛠️ Available Tools

### 1. Markdown Checksum Auto-Updater

**File:** `update-md-checksums.py`

**Purpose:** Calculate and update SHA-256 checksums in markdown frontmatter

**Usage:**
```bash
# Update all spec files
python tools/update-md-checksums.py spec/*.md

# Verify checksums (CI mode)
python tools/update-md-checksums.py --verify spec/*.md

# Dry run
python tools/update-md-checksums.py --dry-run spec/*.md
```

**Features:**
- ✅ Follows MirrorDNA checksum specification (skips frontmatter)
- ✅ Batch processing
- ✅ Verify mode for CI/CD
- ✅ Dry run mode
- ✅ Handles "pending" checksums

**Exit Codes:**
- `0`: Success (all checksums valid/updated)
- `1`: Failure (mismatches found in verify mode, or errors)

---

### 2. Pre-commit Hook Installer

**File:** `install-hooks.sh`

**Purpose:** Install git hooks for automated compliance validation

**Usage:**
```bash
# Install hook
bash tools/install-hooks.sh --install

# Check status
bash tools/install-hooks.sh --status

# Update existing hook
bash tools/install-hooks.sh --update

# Uninstall
bash tools/install-hooks.sh --uninstall
```

**Hook Validates:**
- ✅ Manifest schema compliance
- ✅ Policy schema compliance
- ✅ Profile schema compliance (if present)
- ✅ VaultID and GlyphSig format
- ✅ Prevents commits if validation fails

**Bypass:** `git commit --no-verify` (not recommended)

---

### 3. Compliance Badge Generator

**File:** `generate-badge.py`

**Purpose:** Generate SVG badges for compliance status

**Usage:**
```bash
# From validation report
python tools/generate-badge.py --report compliance-report.json -o badge.svg

# Auto-detect from manifest
python tools/generate-badge.py --auto -o badge.svg

# Manual specification
python tools/generate-badge.py --level L3 --status passed -o badge.svg
```

**Badge Colors:**
- **L1 Passed:** Green (#4c1)
- **L2 Passed:** Blue (#007ec6)
- **L3 Passed:** Gold (#dfb317)
- **Failed:** Red (#e05d44)
- **Warnings:** Orange (#fe7d37)

**Use in README:**
```markdown
![MirrorDNA L3](./badge.svg)
```

---

### 4. Other Tools

#### Add Version Sidecars (`add_version_sidecars.sh`)

Adds version field to sidecar JSON files.

```bash
bash tools/add_version_sidecars.sh 1.0.0
```

#### Publish Blockchain Anchor (`publish_blockchain_anchor.sh`)

Publishes artifact checksums to blockchain for immutable lineage.

```bash
bash tools/publish_blockchain_anchor.sh
```

#### Checksum Tools (`checksums/`)

Directory containing bash-based checksum verification scripts.

- `verify_repo_checksums.sh` - Verify all repo checksums
- `checksum_verifier.sh` - Single file verification
- `checksum_updater.sh` - Update checksums

---

## 🚀 Quick Start Guide

### New Project Setup

```bash
# 1. Install pre-commit hook
bash tools/install-hooks.sh --install

# 2. Set up checksums for all markdown files
python tools/update-md-checksums.py spec/*.md

# 3. Generate compliance badge
python tools/generate-badge.py --auto -o badge.svg

# 4. Add badge to README
echo "![MirrorDNA](./badge.svg)" >> README.md
```

### CI/CD Integration

```bash
# 1. Copy GitHub Actions template
cp templates/github-actions-mirrordna.yml .github/workflows/mirrordna-compliance.yml

# 2. Commit and push
git add .github/workflows/
git commit -m "Add MirrorDNA CI/CD"
git push
```

### Regular Maintenance

```bash
# Verify all checksums
python tools/update-md-checksums.py --verify **/*.md

# Update checksums after edits
python tools/update-md-checksums.py spec/*.md

# Regenerate badge after validation
python tools/generate-badge.py --report report.json -o badge.svg
```

---

## 📋 Tool Comparison

| Tool | Purpose | Mode | Language |
|------|---------|------|----------|
| `update-md-checksums.py` | Checksum management | CLI | Python |
| `install-hooks.sh` | Git integration | Install/Config | Bash |
| `generate-badge.py` | Badge generation | CLI | Python |
| `generate_checksum.py` | JSON checksums | CLI (scripts/) | Python |
| Checksum tools | Bash verification | CLI | Bash |

---

## 🔧 Dependencies

### Python Tools
- Python 3.7+
- No external dependencies (uses stdlib only)
- Integrates with validators/ package

### Bash Tools
- Bash 4.0+
- Standard Unix tools (grep, awk, sed)
- Git (for hooks)

---

## 🐛 Troubleshooting

**Issue:** `update-md-checksums.py` says "No frontmatter found"

**Solution:** Ensure file starts with `---` and has closing `---`

---

**Issue:** Pre-commit hook not running

**Solution:** Check executable permissions: `chmod +x .git/hooks/pre-commit`

---

**Issue:** Badge generator fails with "No manifest"

**Solution:** Create `mirrorDNA_manifest.yaml` or use `--report` mode

---

**Issue:** Python tools can't find validators

**Solution:** Run from repository root, not from tools/ directory

---

## 📚 See Also

- [Validators Architecture](../validators/ARCHITECTURE.md) - Validator system documentation
- [Templates](../templates/README.md) - CI/CD and project templates
- [Examples](../examples/README.md) - Example configurations

---

⟡⟦TOOLS⟧ · ⟡⟦DEVELOPER-EXPERIENCE⟧ · v1.0.0

**Last Updated:** 2025-11-16
**Author:** AMOS Dev Twin
**Status:** Production Ready
