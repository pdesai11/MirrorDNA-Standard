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

### 4. Project Initialization Tool

**File:** `mirrordna-init.py`

**Purpose:** Interactive scaffold for new MirrorDNA-compliant projects

**Usage:**
```bash
# Interactive mode (recommended)
python tools/mirrordna-init.py

# Non-interactive mode
python tools/mirrordna-init.py --name "MyProject" --level L2 --non-interactive

# Specify output directory
python tools/mirrordna-init.py --output ./my-project

# Dry run
python tools/mirrordna-init.py --dry-run
```

**Features:**
- ✅ Interactive prompts for project configuration
- ✅ Generates manifest, policy, profile for L1/L2/L3
- ✅ Creates supporting files (.gitignore, README.md)
- ✅ Supports vault-backed L3 projects
- ✅ Dry run mode
- ✅ Non-interactive mode for automation

**Generated Files:**
- `mirrorDNA_manifest.yaml`
- `reflection_policy.yaml`
- `continuity_profile.yaml` (L2+)
- `.gitignore`, `README.md` (optional)
- `state/` directory (L2+)
- `vault/` directory (L3)

---

### 5. Interactive Migration Wizard

**File:** `migrate.py`

**Purpose:** Automate compliance level migrations (L1→L2→L3)

**Usage:**
```bash
# Interactive mode
python tools/migrate.py

# Migrate to L2
python tools/migrate.py --target L2

# Migrate to L3 with auto-confirm
python tools/migrate.py --target L3 --yes

# Dry run (preview changes)
python tools/migrate.py --target L2 --dry-run
```

**Features:**
- ✅ Guided step-by-step migration process
- ✅ Automatic backup before migration
- ✅ Rollback support on failure
- ✅ Validates at each step
- ✅ Supports L1→L2, L2→L3, and L1→L3 (two-step)
- ✅ Dry run mode

**Migration Paths:**
- **L1 → L2:** Adds session persistence, checksums, lineage tracking
- **L2 → L3:** Adds vault storage, glyph signatures, interaction safety
- **L1 → L3:** Performs L1→L2→L3 automatically

---

### 6. Lineage Visualizer

**File:** `visualize-lineage.py`

**Purpose:** Generate visual graphs of predecessor/successor lineage chains

**Usage:**
```bash
# Scan current directory
python tools/visualize-lineage.py

# Scan specific directory
python tools/visualize-lineage.py --scan ./state

# Generate SVG (requires graphviz)
python tools/visualize-lineage.py --format svg --output lineage.svg

# Generate interactive HTML
python tools/visualize-lineage.py --format html --output lineage.html

# From specific sidecar
python tools/visualize-lineage.py --sidecar file.sidecar.json
```

**Features:**
- ✅ Parses lineage from .sidecar.json files
- ✅ Builds directed graph of relationships
- ✅ Detects cycles and broken links
- ✅ Generates GraphViz DOT format
- ✅ Exports to SVG (requires graphviz) or HTML
- ✅ Interactive HTML with tooltips and metadata

**Output Formats:**
- **DOT:** GraphViz format (text)
- **SVG:** Scalable vector graphics (requires `graphviz` installed)
- **HTML:** Interactive visualization with clickable nodes

---

### 7. Watch Mode Validator

**File:** `watch.py`

**Purpose:** Real-time validation with file system monitoring

**Usage:**
```bash
# Watch current directory
python tools/watch.py

# Watch specific files
python tools/watch.py --files mirrorDNA_manifest.yaml reflection_policy.yaml

# Custom watch interval
python tools/watch.py --interval 2

# Enable desktop notifications
python tools/watch.py --notify

# Quiet mode (only show changes)
python tools/watch.py --quiet
```

**Features:**
- ✅ Poll-based file watching (no external dependencies)
- ✅ Auto-runs validation when files change
- ✅ Debouncing to avoid repeated validations
- ✅ Optional desktop notifications (macOS/Linux)
- ✅ Colorized terminal output
- ✅ Configurable watch interval

**Notifications:**
- macOS: Uses `osascript` (built-in)
- Linux: Uses `notify-send` (install `libnotify-bin`)

---

### 8. Checksum Sync Tool

**File:** `sync-checksums.py`

**Purpose:** Synchronize checksums between .md frontmatter and .sidecar.json files

**Usage:**
```bash
# Check for drift
python tools/sync-checksums.py --verify

# Sync from frontmatter to sidecar
python tools/sync-checksums.py --source frontmatter

# Sync from sidecar to frontmatter
python tools/sync-checksums.py --source sidecar

# Recalculate and sync both
python tools/sync-checksums.py --recalculate

# Specific files
python tools/sync-checksums.py --files spec/*.md --recalculate

# Dry run
python tools/sync-checksums.py --recalculate --dry-run
```

**Features:**
- ✅ Detects checksum drift between frontmatter and sidecar
- ✅ Bidirectional sync (frontmatter ↔ sidecar)
- ✅ Recalculates checksums from file content
- ✅ Batch operations on multiple files
- ✅ Dry-run mode
- ✅ Comprehensive reporting

**Operations:**
- **Verify:** Check for drift without modifying
- **Sync:** Copy checksum from source to target
- **Recalculate:** Calculate fresh checksum, update both

---

### 9. Other Tools

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

### Brand New Project Setup

```bash
# 1. Initialize MirrorDNA project
python tools/mirrordna-init.py

# 2. Install pre-commit hook
bash tools/install-hooks.sh --install

# 3. Generate compliance badge
python tools/generate-badge.py --auto -o badge.svg

# 4. Add badge to README
echo "![MirrorDNA](./badge.svg)" >> README.md
```

### Existing Project Setup

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
| `mirrordna-init.py` | Project initialization | Interactive/CLI | Python |
| `migrate.py` | Level migration | Interactive/CLI | Python |
| `visualize-lineage.py` | Lineage visualization | CLI | Python |
| `watch.py` | Real-time validation | Watch daemon | Python |
| `sync-checksums.py` | Checksum sync | CLI | Python |
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
