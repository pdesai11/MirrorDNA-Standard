# MirrorDNA Templates

Ready-to-use templates for MirrorDNA-compliant projects.

---

## 📄 Available Templates

### GitHub Actions Workflow

**File:** `github-actions-mirrordna.yml`

**Purpose:** Automated compliance validation in CI/CD

**Setup:**
```bash
# Copy to your project's workflows directory
cp templates/github-actions-mirrordna.yml .github/workflows/mirrordna-compliance.yml

# Customize as needed
# - Set COMPLIANCE_LEVEL (L1, L2, or L3)
# - Adjust Python version
# - Enable/disable specific steps
```

**Features:**
- ✅ Validates manifest, policy, and profile
- ✅ Generates JSON compliance report
- ✅ Uploads report as artifact
- ✅ Verifies checksums
- ✅ Comments on pull requests with results
- ✅ Creates GitHub job summary

**Requirements:**
- `mirrorDNA_manifest.yaml` in repo root
- `reflection_policy.yaml` in repo root
- `continuity_profile.yaml` (for L2+)
- MirrorDNA validators in `validators/` directory

---

## 🚀 Usage Examples

### Quick Start: Add CI/CD to Your Project

```bash
# 1. Ensure you have MirrorDNA files
ls mirrorDNA_manifest.yaml reflection_policy.yaml

# 2. Create workflows directory
mkdir -p .github/workflows

# 3. Copy template
cp path/to/MirrorDNA-Standard/templates/github-actions-mirrordna.yml \
   .github/workflows/mirrordna-compliance.yml

# 4. Commit and push
git add .github/workflows/mirrordna-compliance.yml
git commit -m "Add MirrorDNA compliance validation"
git push
```

The workflow will now run on every push and pull request.

---

## 📝 Customization

### Adjust Compliance Level

Edit the `env` section:
```yaml
env:
  COMPLIANCE_LEVEL: 'L3'  # Change to L1, L2, or L3
```

### Run on Specific Branches

Edit the `on` section:
```yaml
on:
  push:
    branches: [ main, staging ]  # Only these branches
```

### Add Scheduled Checks

Uncomment the schedule section at bottom of workflow.

---

## 🔧 Troubleshooting

**Issue:** Workflow fails with "manifest not found"

**Solution:** Ensure `mirrorDNA_manifest.yaml` exists in repo root

---

**Issue:** Validation passes locally but fails in CI

**Solution:** Check dependencies are installed (see `requirements.txt`)

---

**Issue:** PR comments not appearing

**Solution:** Ensure GitHub Actions has write permissions for issues/PRs

---

## 📚 More Templates Coming Soon

- ✨ GitLab CI/CD template
- ✨ Pre-commit configuration
- ✨ Docker build template
- ✨ Project scaffolding templates

---

⟡⟦TEMPLATES⟧ · ⟡⟦READY-TO-USE⟧ · v1.0.0
