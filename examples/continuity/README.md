# Continuity Engine Examples

This directory contains example files for implementing the Continuity Engine v1 in your repository.

## Files

### BOOT.example.json
**Purpose**: Template for creating your `continuity/BOOT.json` boot configuration.

**Usage**:
```bash
cp examples/continuity/BOOT.example.json continuity/BOOT.json
# Edit continuity/BOOT.json with your values
```

**Required customizations**:
- `vault_path` → Your repository's AMOS:// URI
- `identity_lock` → Your glyph signature
- `checksum` → Generate with `sha256sum continuity/BOOT.json` or `lingos checksum`
- `last_synced` → Current date (YYYY-MM-DD)
- `repository.name` → Your repository name
- `repository.owner` → Your username

---

### Snapshot.example.md
**Purpose**: Template for creating your `continuity/Snapshot_Latest.md` state snapshot.

**Usage**:
```bash
cp examples/continuity/Snapshot.example.md continuity/Snapshot_Latest.md
# Edit continuity/Snapshot_Latest.md with your repository state
```

**Required customizations**:
- Replace all `[Your Repository Name]` with actual name
- Replace all `⟡⟦YOUR_NAME⟧ · ⟡⟦YOUR_PROJECT⟧` with your signature
- Fill in all sections with actual content
- Update `VaultID`, `Snapshot Date`, etc.

---

### Graph.example.json
**Purpose**: Template for creating your `continuity/Graph_v1.json` knowledge graph.

**Usage**:
```bash
cp examples/continuity/Graph.example.json continuity/Graph_v1.json
# Edit continuity/Graph_v1.json with your semantic graph
```

**Required customizations**:
- Add nodes for your components, dependencies, protocols
- Add edges connecting your nodes
- Update `vault_id` to your AMOS:// URI
- Update `signature` with your glyph
- Ensure all `from`/`to` references point to existing node IDs

---

## Quick Start

1. **Copy all templates**:
   ```bash
   mkdir -p continuity .vault
   cp examples/continuity/BOOT.example.json continuity/BOOT.json
   cp examples/continuity/Snapshot.example.md continuity/Snapshot_Latest.md
   cp examples/continuity/Graph.example.json continuity/Graph_v1.json
   ```

2. **Customize each file** (see "Required customizations" above)

3. **Create vault manifest**:
   ```bash
   # Manually or using LingOS-Coder tools
   touch .vault/manifest.yml
   # Populate with file list and checksums
   ```

4. **Validate**:
   ```bash
   python validators/continuity_validate.py
   ```

5. **Update README** with Boot Sequence section (see main README.md)

6. **Commit**:
   ```bash
   git add continuity/ .vault/
   git commit -m "feat(continuity): add Continuity Engine v1"
   ```

---

## Validation

After customization, run the validator:

```bash
python validators/continuity_validate.py
```

Expected output:
```
Continuity Engine Validator v1.0
==================================================

✅ File exists: continuity/BOOT.json
✅ File exists: continuity/Snapshot_Latest.md
✅ File exists: continuity/Graph_v1.json
✅ File exists: .vault/manifest.yml
✅ BOOT.json validation passed
✅ Snapshot validation passed
✅ Graph validation passed
✅ Manifest validation passed

All continuity checks passed ✓
```

---

## Integration

See full specification: [specs/Continuity_Engine_v1.md](../../specs/Continuity_Engine_v1.md)

For cross-repository integration (LingOS-Coder, ActiveMirrorOS), refer to section 5.3 of the spec.

---

## Support

- **Specification**: `/specs/Continuity_Engine_v1.md`
- **Validator**: `/validators/continuity_validate.py`
- **Main README**: `/README.md` (Boot Sequence section)

---

**Signature**: ⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧
**Version**: 1.0
**Status**: Ready for use
