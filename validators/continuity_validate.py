#!/usr/bin/env python3
"""
Continuity Engine Validator v1.0

Automated compliance checker for MirrorDNA Continuity Engine files.

Usage:
    python validators/continuity_validate.py
    python -m validators.continuity_validate

Exit Codes:
    0 - All validation checks passed
    1 - Validation errors found

Author: Paul Desai (Active MirrorOS)
Signature: ⟡⟦PAUL⟧ · ⟡⟦MIRRORDNA⟧
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. YAML validation will be skipped.")
    yaml = None


class ContinuityValidator:
    """Validates MirrorDNA Continuity Engine files."""

    def __init__(self, repo_root: Path = None):
        """Initialize validator with repository root."""
        self.repo_root = repo_root or Path.cwd()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks. Returns True if all pass."""
        print("Continuity Engine Validator v1.0")
        print("=" * 50)
        print()

        # Run all checks
        self.check_file_existence()
        self.validate_boot_json()
        self.validate_snapshot()
        self.validate_graph()
        self.validate_manifest()

        # Print results
        self.print_results()

        # Return success if no errors
        return len(self.errors) == 0

    def check_file_existence(self) -> None:
        """Check that all required continuity files exist."""
        required_files = [
            "continuity/BOOT.json",
            "continuity/Snapshot_Latest.md",
            "continuity/Graph_v1.json",
            ".vault/manifest.yml"
        ]

        for file_path in required_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                self.checks_passed.append(f"File exists: {file_path}")

    def validate_boot_json(self) -> None:
        """Validate BOOT.json structure and required keys."""
        boot_path = self.repo_root / "continuity/BOOT.json"

        if not boot_path.exists():
            return  # Already reported in file existence check

        try:
            with open(boot_path, 'r') as f:
                boot_data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"BOOT.json is not valid JSON: {e}")
            return

        # Required keys
        required_keys = [
            "version",
            "vault_path",
            "checksum",
            "active_snapshot",
            "identity_lock",
            "tone_mode",
            "twins",
            "protocols",
            "last_synced"
        ]

        for key in required_keys:
            if key not in boot_data:
                self.errors.append(f"BOOT.json missing required key: {key}")

        # Validate specific fields
        if "checksum" in boot_data:
            if boot_data["checksum"] == "":
                self.errors.append("BOOT.json checksum is empty string (use 'TBD' during development)")
            elif boot_data["checksum"] == "TBD":
                self.warnings.append("BOOT.json checksum is 'TBD' (should be populated for production)")

        if "vault_path" in boot_data:
            if not boot_data["vault_path"].startswith("AMOS://"):
                self.warnings.append("BOOT.json vault_path should follow AMOS:// URI format")

        if "protocols" in boot_data:
            if not isinstance(boot_data["protocols"], dict):
                self.errors.append("BOOT.json protocols must be an object")
            elif len(boot_data["protocols"]) == 0:
                self.warnings.append("BOOT.json protocols object is empty")

        if "version" in boot_data:
            if not boot_data["version"].startswith("v"):
                self.warnings.append("BOOT.json version should start with 'v' (e.g., v15.3)")

        if "last_synced" in boot_data:
            # Basic date format check (YYYY-MM-DD)
            last_synced = boot_data["last_synced"]
            if len(last_synced) != 10 or last_synced[4] != '-' or last_synced[7] != '-':
                self.warnings.append("BOOT.json last_synced should be in YYYY-MM-DD format")

        if len([e for e in self.errors if "BOOT.json" in e]) == 0:
            self.checks_passed.append("BOOT.json validation passed")

    def validate_snapshot(self) -> None:
        """Validate Snapshot_Latest.md structure."""
        snapshot_path = self.repo_root / "continuity/Snapshot_Latest.md"

        if not snapshot_path.exists():
            return  # Already reported in file existence check

        try:
            with open(snapshot_path, 'r') as f:
                snapshot_content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to read Snapshot_Latest.md: {e}")
            return

        # Check for required sections
        required_sections = [
            "## Current State",
            "## Active Tasks",
            "## Recent Changes",
            "## Context",
            "## Trust Markers"
        ]

        for section in required_sections:
            if section not in snapshot_content:
                self.warnings.append(f"Snapshot missing recommended section: {section}")

        # Check for frontmatter metadata
        if "**VaultID**:" not in snapshot_content:
            self.warnings.append("Snapshot missing VaultID metadata")

        if "**Snapshot Date**:" not in snapshot_content:
            self.warnings.append("Snapshot missing Snapshot Date metadata")

        if len([e for e in self.errors if "Snapshot" in e]) == 0:
            self.checks_passed.append("Snapshot validation passed")

    def validate_graph(self) -> None:
        """Validate Graph_v1.json structure."""
        graph_path = self.repo_root / "continuity/Graph_v1.json"

        if not graph_path.exists():
            return  # Already reported in file existence check

        try:
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Graph_v1.json is not valid JSON: {e}")
            return

        # Check required top-level keys
        required_keys = ["graph_version", "vault_id", "nodes", "edges", "metadata"]
        for key in required_keys:
            if key not in graph_data:
                self.errors.append(f"Graph_v1.json missing required key: {key}")

        if "nodes" not in graph_data or "edges" not in graph_data:
            return  # Can't validate further

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        # Validate nodes
        node_ids = set()
        for i, node in enumerate(nodes):
            if "id" not in node:
                self.errors.append(f"Graph node at index {i} missing 'id' field")
            else:
                node_id = node["id"]
                if node_id in node_ids:
                    self.errors.append(f"Graph has duplicate node id: {node_id}")
                node_ids.add(node_id)

            if "type" not in node:
                self.warnings.append(f"Graph node '{node.get('id', i)}' missing 'type' field")

            if "label" not in node:
                self.warnings.append(f"Graph node '{node.get('id', i)}' missing 'label' field")

        # Validate edges
        for i, edge in enumerate(edges):
            if "from" not in edge:
                self.errors.append(f"Graph edge at index {i} missing 'from' field")
            elif edge["from"] not in node_ids:
                self.errors.append(f"Graph edge references non-existent node: {edge['from']}")

            if "to" not in edge:
                self.errors.append(f"Graph edge at index {i} missing 'to' field")
            elif edge["to"] not in node_ids:
                self.errors.append(f"Graph edge references non-existent node: {edge['to']}")

            if "relation" not in edge:
                self.warnings.append(f"Graph edge at index {i} missing 'relation' field")

        # Validate metadata counts
        if "metadata" in graph_data:
            metadata = graph_data["metadata"]
            if "node_count" in metadata:
                if metadata["node_count"] != len(nodes):
                    self.warnings.append(
                        f"Graph metadata node_count ({metadata['node_count']}) "
                        f"doesn't match actual count ({len(nodes)})"
                    )

            if "edge_count" in metadata:
                if metadata["edge_count"] != len(edges):
                    self.warnings.append(
                        f"Graph metadata edge_count ({metadata['edge_count']}) "
                        f"doesn't match actual count ({len(edges)})"
                    )

        if len([e for e in self.errors if "Graph" in e]) == 0:
            self.checks_passed.append("Graph validation passed")

    def validate_manifest(self) -> None:
        """Validate .vault/manifest.yml structure."""
        manifest_path = self.repo_root / ".vault/manifest.yml"

        if not manifest_path.exists():
            return  # Already reported in file existence check

        if yaml is None:
            self.warnings.append("PyYAML not installed, skipping manifest YAML validation")
            return

        try:
            with open(manifest_path, 'r') as f:
                manifest_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"manifest.yml is not valid YAML: {e}")
            return

        # Check required keys
        required_keys = ["vault_id", "manifest_version", "checksum_algorithm", "files"]
        for key in required_keys:
            if key not in manifest_data:
                self.errors.append(f"manifest.yml missing required key: {key}")

        if "files" in manifest_data:
            files = manifest_data["files"]
            if not isinstance(files, list):
                self.errors.append("manifest.yml 'files' must be a list")
            else:
                # Check that critical continuity files are listed
                critical_files = [
                    "continuity/BOOT.json",
                    "continuity/Snapshot_Latest.md",
                    "continuity/Graph_v1.json"
                ]

                manifest_paths = [f.get("path", "") for f in files]
                for critical_file in critical_files:
                    if critical_file not in manifest_paths:
                        self.warnings.append(f"manifest.yml should include critical file: {critical_file}")

                # Check for TBD checksums in production
                tbd_count = sum(1 for f in files if f.get("checksum") == "TBD")
                if tbd_count > 0:
                    self.warnings.append(
                        f"manifest.yml has {tbd_count} files with 'TBD' checksums "
                        "(should be populated for production)"
                    )

        if "checksum_algorithm" in manifest_data:
            if manifest_data["checksum_algorithm"] != "sha256":
                self.warnings.append("manifest.yml should use 'sha256' checksum algorithm")

        if len([e for e in self.errors if "manifest" in e]) == 0:
            self.checks_passed.append("Manifest validation passed")

    def print_results(self) -> None:
        """Print validation results."""
        print()

        # Print checks passed
        if self.checks_passed:
            for check in self.checks_passed:
                print(f"✅ {check}")

        print()

        # Print warnings
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
            print()

        # Print errors
        if self.errors:
            print("❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
            print()
            print("Validation FAILED ✗")
        else:
            print("All continuity checks passed ✓")

        print()


def main():
    """Main entry point."""
    # Determine repository root
    # If run from validators/, go up one level
    current_dir = Path.cwd()
    if current_dir.name == "validators":
        repo_root = current_dir.parent
    else:
        repo_root = current_dir

    # Run validator
    validator = ContinuityValidator(repo_root)
    success = validator.validate_all()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
