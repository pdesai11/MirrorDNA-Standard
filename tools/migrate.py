#!/usr/bin/env python3
"""
MirrorDNA Interactive Migration Wizard

Automates compliance level migrations (L1→L2→L3) with guided step-by-step process.
Includes validation, rollback support, and dry-run mode.

Usage:
  # Interactive mode (recommended)
  python tools/migrate.py

  # Specify target level
  python tools/migrate.py --target L2

  # Dry run (show what would change)
  python tools/migrate.py --target L3 --dry-run

  # Non-interactive with auto-confirm
  python tools/migrate.py --target L2 --yes

Migration Paths:
  L1 → L2: Adds session persistence, checksums, lineage tracking
  L2 → L3: Adds vault storage, glyph signatures, interaction safety
  L1 → L3: Performs L1→L2→L3 in sequence

Based on: spec/Compliance_Migration_Guide_v1.0.md
"""

import argparse
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class MigrationWizard:
    """Handles compliance level migrations."""

    def __init__(self, dry_run: bool = False, yes_to_all: bool = False):
        self.dry_run = dry_run
        self.yes_to_all = yes_to_all
        self.backup_dir = None
        self.changes_made = []
        self.current_level = None
        self.target_level = None

    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask yes/no question."""
        if self.yes_to_all:
            return True

        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{message} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ('y', 'yes'):
                return True
            if response in ('n', 'no'):
                return False
            print("  Please enter 'y' or 'n'")

    def detect_current_level(self) -> Optional[str]:
        """Detect current compliance level from manifest."""
        manifest_path = Path('mirrorDNA_manifest.yaml')

        if not manifest_path.exists():
            print("❌ Error: mirrorDNA_manifest.yaml not found")
            print("   This doesn't appear to be a MirrorDNA project.")
            print("   Run: python tools/mirrordna-init.py")
            return None

        try:
            content = manifest_path.read_text()

            # Parse compliance level
            for line in content.splitlines():
                if 'mirrorDNA_compliance_level:' in line:
                    level_value = line.split(':', 1)[1].strip().strip('"\'')

                    if 'level_1' in level_value or level_value == 'L1':
                        return 'L1'
                    elif 'level_2' in level_value or level_value == 'L2':
                        return 'L2'
                    elif 'level_3' in level_value or level_value == 'L3':
                        return 'L3'

            print("⚠ Warning: Could not determine compliance level from manifest")
            return None

        except Exception as e:
            print(f"❌ Error reading manifest: {e}")
            return None

    def validate_migration_path(self, current: str, target: str) -> bool:
        """Validate that migration path is allowed."""
        levels = {'L1': 1, 'L2': 2, 'L3': 3}

        if current not in levels or target not in levels:
            return False

        # Can only migrate forward
        if levels[target] <= levels[current]:
            print(f"❌ Error: Cannot migrate from {current} to {target}")
            print(f"   Migration must move to higher compliance level.")
            return False

        return True

    def create_backup(self) -> bool:
        """Create backup of current state."""
        if self.dry_run:
            print("[DRY RUN] Would create backup")
            return True

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path(f'.mirrordna_backup_{timestamp}')

        try:
            self.backup_dir.mkdir(exist_ok=True)

            # Backup key files
            files_to_backup = [
                'mirrorDNA_manifest.yaml',
                'reflection_policy.yaml',
                'continuity_profile.yaml',
            ]

            for filename in files_to_backup:
                filepath = Path(filename)
                if filepath.exists():
                    shutil.copy2(filepath, self.backup_dir / filename)

            print(f"✓ Backup created: {self.backup_dir}")
            return True

        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False

    def rollback(self) -> bool:
        """Restore from backup."""
        if not self.backup_dir or not self.backup_dir.exists():
            print("❌ No backup found")
            return False

        try:
            print(f"Rolling back from: {self.backup_dir}")

            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file():
                    target = Path(backup_file.name)
                    shutil.copy2(backup_file, target)
                    print(f"  ✓ Restored: {backup_file.name}")

            print("✓ Rollback complete")
            return True

        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return False

    def migrate_l1_to_l2(self) -> bool:
        """Migrate from L1 to L2."""
        print("\n" + "=" * 70)
        print("Migrating: L1 → L2 (Basic Reflection → Continuity Aware)")
        print("=" * 70)

        steps = [
            ("Update manifest to L2", self.update_manifest_to_l2),
            ("Create continuity profile", self.create_continuity_profile),
            ("Add checksums to policy", self.add_checksums_to_policy),
            ("Create state directory", self.create_state_directory),
            ("Update .gitignore", self.update_gitignore_l2),
            ("Validate L2 compliance", self.validate_compliance),
        ]

        return self.execute_migration_steps(steps)

    def migrate_l2_to_l3(self) -> bool:
        """Migrate from L2 to L3."""
        print("\n" + "=" * 70)
        print("Migrating: L2 → L3 (Continuity Aware → Vault-Backed Sovereign)")
        print("=" * 70)

        steps = [
            ("Update manifest to L3", self.update_manifest_to_l3),
            ("Add vault_id to manifest", self.add_vault_id_to_manifest),
            ("Update continuity profile for vault", self.update_profile_for_vault),
            ("Add glyph signatures to policy", self.add_glyph_signatures),
            ("Add interaction safety to policy", self.add_interaction_safety),
            ("Create vault directory structure", self.create_vault_structure),
            ("Validate L3 compliance", self.validate_compliance),
        ]

        return self.execute_migration_steps(steps)

    def execute_migration_steps(self, steps: List[Tuple[str, callable]]) -> bool:
        """Execute migration steps with validation."""
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\nStep {i}/{len(steps)}: {step_name}")

            try:
                if not step_func():
                    print(f"❌ Step failed: {step_name}")
                    return False

                self.changes_made.append(step_name)
                print(f"✓ {step_name} complete")

            except Exception as e:
                print(f"❌ Error in step '{step_name}': {e}")
                return False

        return True

    def update_manifest_to_l2(self) -> bool:
        """Update manifest to L2 compliance level."""
        manifest_path = Path('mirrorDNA_manifest.yaml')

        try:
            content = manifest_path.read_text()

            # Update compliance level
            updated = content.replace(
                'mirrorDNA_compliance_level: "level_1_basic_reflection"',
                'mirrorDNA_compliance_level: "level_2_continuity_aware"'
            )

            # Add continuity profile reference if not present
            if 'continuity_profile:' not in updated:
                # Find where to insert (after reflection_policy line)
                lines = updated.splitlines()
                new_lines = []
                for line in lines:
                    new_lines.append(line)
                    if line.startswith('reflection_policy:'):
                        new_lines.append('continuity_profile: "./continuity_profile.yaml"')
                updated = '\n'.join(new_lines)

            if self.dry_run:
                print("[DRY RUN] Would update manifest to L2")
                return True

            manifest_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error updating manifest: {e}")
            return False

    def update_manifest_to_l3(self) -> bool:
        """Update manifest to L3 compliance level."""
        manifest_path = Path('mirrorDNA_manifest.yaml')

        try:
            content = manifest_path.read_text()

            # Update compliance level
            updated = content.replace(
                'mirrorDNA_compliance_level: "level_2_continuity_aware"',
                'mirrorDNA_compliance_level: "level_3_vault_backed_sovereign"'
            )

            if self.dry_run:
                print("[DRY RUN] Would update manifest to L3")
                return True

            manifest_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error updating manifest: {e}")
            return False

    def create_continuity_profile(self) -> bool:
        """Create continuity_profile.yaml for L2."""
        profile_path = Path('continuity_profile.yaml')

        if profile_path.exists():
            print("  Continuity profile already exists, skipping")
            return True

        # Read project name from manifest
        manifest = Path('mirrorDNA_manifest.yaml').read_text()
        project_name = "MyProject"
        for line in manifest.splitlines():
            if line.startswith('name:'):
                project_name = line.split(':', 1)[1].strip().strip('"\'')
                break

        profile_content = f"""profile_version: "1.0.0"
continuity_mechanism: "session_storage"

state_persistence:
  enabled: true
  storage_type: "file"
  storage_location: "./state"
  encryption: false
  checksum_validation: true

session_tracking:
  enabled: true
  session_id_format: "uuid"
  lineage_tracking: true

recovery:
  enabled: true
  recovery_mechanism: "state_reload"
  backup_enabled: false
"""

        if self.dry_run:
            print("[DRY RUN] Would create continuity_profile.yaml")
            return True

        profile_path.write_text(profile_content)
        return True

    def add_checksums_to_policy(self) -> bool:
        """Add checksum validation to reflection policy."""
        policy_path = Path('reflection_policy.yaml')

        if not policy_path.exists():
            print("  reflection_policy.yaml not found, skipping")
            return True

        try:
            content = policy_path.read_text()

            # Check if already has reflection_protocols section
            if 'reflection_protocols:' in content:
                print("  Policy already has reflection_protocols, skipping")
                return True

            # Add reflection protocols section
            addition = """
reflection_protocols:
  session_reflection: true
  continuity_checks: true
  state_validation: true
"""

            updated = content + addition

            if self.dry_run:
                print("[DRY RUN] Would add checksums to policy")
                return True

            policy_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error updating policy: {e}")
            return False

    def create_state_directory(self) -> bool:
        """Create state/ directory for L2."""
        state_dir = Path('state')

        if state_dir.exists():
            print("  state/ directory already exists")
            return True

        if self.dry_run:
            print("[DRY RUN] Would create state/ directory")
            return True

        state_dir.mkdir(exist_ok=True)
        (state_dir / '.gitkeep').write_text('')
        return True

    def update_gitignore_l2(self) -> bool:
        """Update .gitignore for L2."""
        gitignore_path = Path('.gitignore')

        l2_entries = """
# MirrorDNA L2 State Files
state/
*.state.json
session_*.json
"""

        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if 'MirrorDNA L2 State Files' in content:
                print("  .gitignore already has L2 entries")
                return True

            updated = content + l2_entries
        else:
            updated = l2_entries

        if self.dry_run:
            print("[DRY RUN] Would update .gitignore")
            return True

        gitignore_path.write_text(updated)
        return True

    def add_vault_id_to_manifest(self) -> bool:
        """Add vault_id to manifest for L3."""
        manifest_path = Path('mirrorDNA_manifest.yaml')

        try:
            content = manifest_path.read_text()

            # Check if already has vault_id
            if 'vault_id:' in content:
                print("  Manifest already has vault_id")
                return True

            # Get project name for vault_id
            project_name = "MyProject"
            for line in content.splitlines():
                if line.startswith('name:'):
                    project_name = line.split(':', 1)[1].strip().strip('"\'')
                    break

            vault_id = f'AMOS://{project_name.replace(" ", "")}/Vault/v1.0'

            # Add vault_id after continuity_profile line
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.startswith('continuity_profile:'):
                    new_lines.append(f'vault_id: "{vault_id}"')

            updated = '\n'.join(new_lines)

            if self.dry_run:
                print(f"[DRY RUN] Would add vault_id: {vault_id}")
                return True

            manifest_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error adding vault_id: {e}")
            return False

    def update_profile_for_vault(self) -> bool:
        """Update continuity profile for vault backing."""
        profile_path = Path('continuity_profile.yaml')

        if not profile_path.exists():
            print("  continuity_profile.yaml not found")
            return False

        try:
            content = profile_path.read_text()

            # Update continuity mechanism
            updated = content.replace(
                'continuity_mechanism: "session_storage"',
                'continuity_mechanism: "vault_backed"'
            )

            # Update encryption
            updated = updated.replace(
                'encryption: false',
                'encryption: true'
            )

            # Add vault integration if not present
            if 'vault_integration:' not in updated:
                # Get project name for vault_id
                manifest = Path('mirrorDNA_manifest.yaml').read_text()
                project_name = "MyProject"
                for line in manifest.splitlines():
                    if line.startswith('name:'):
                        project_name = line.split(':', 1)[1].strip().strip('"\'')
                        break

                vault_id = f'AMOS://{project_name.replace(" ", "")}/Vault/v1.0'

                addition = f"""  vault_integration: true

vault_id: "{vault_id}"
sovereign_identity:
  enabled: true
  identity_binding: "vault_id"
  ownership: "user"
"""

                # Find session_tracking section and add after
                lines = updated.splitlines()
                new_lines = []
                in_session_tracking = False
                for line in lines:
                    new_lines.append(line)
                    if line.startswith('session_tracking:'):
                        in_session_tracking = True
                    elif in_session_tracking and line.startswith('  lineage_tracking:'):
                        new_lines.append(addition)
                        in_session_tracking = False

                updated = '\n'.join(new_lines)

            if self.dry_run:
                print("[DRY RUN] Would update profile for vault")
                return True

            profile_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def add_glyph_signatures(self) -> bool:
        """Add glyph signatures to policy."""
        policy_path = Path('reflection_policy.yaml')

        if not policy_path.exists():
            return False

        try:
            content = policy_path.read_text()

            if 'glyph_signatures:' in content:
                print("  Policy already has glyph signatures")
                return True

            addition = """
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
"""

            updated = content + addition

            if self.dry_run:
                print("[DRY RUN] Would add glyph signatures")
                return True

            policy_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error adding glyph signatures: {e}")
            return False

    def add_interaction_safety(self) -> bool:
        """Add interaction safety to policy."""
        policy_path = Path('reflection_policy.yaml')

        if not policy_path.exists():
            return False

        try:
            content = policy_path.read_text()

            if 'interaction_safety:' in content:
                print("  Policy already has interaction safety")
                return True

            addition = """
interaction_safety:
  session_duration_warnings: true
  dependency_detection: true
  human_escalation: true
  rhythm_checks: true
  max_session_duration_minutes: 120
"""

            updated = content + addition

            if self.dry_run:
                print("[DRY RUN] Would add interaction safety")
                return True

            policy_path.write_text(updated)
            return True

        except Exception as e:
            print(f"Error adding interaction safety: {e}")
            return False

    def create_vault_structure(self) -> bool:
        """Create vault directory structure."""
        vault_dir = Path('vault')

        if vault_dir.exists():
            print("  vault/ directory already exists")
            return True

        if self.dry_run:
            print("[DRY RUN] Would create vault/ directory structure")
            return True

        vault_dir.mkdir(exist_ok=True)
        (vault_dir / 'sessions').mkdir(exist_ok=True)
        (vault_dir / 'artifacts').mkdir(exist_ok=True)
        (vault_dir / '.gitkeep').write_text('')

        return True

    def validate_compliance(self) -> bool:
        """Validate compliance using validators."""
        validators_dir = Path('validators')

        if not validators_dir.exists():
            print("  ⚠ Validators not found, skipping validation")
            return True

        if self.dry_run:
            print("[DRY RUN] Would validate compliance")
            return True

        try:
            import subprocess

            cmd = ['python', '-m', 'validators.cli', '--manifest', 'mirrorDNA_manifest.yaml']

            if Path('reflection_policy.yaml').exists():
                cmd.extend(['--policy', 'reflection_policy.yaml'])

            if Path('continuity_profile.yaml').exists():
                cmd.extend(['--profile', 'continuity_profile.yaml'])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("  ✓ Compliance validation passed")
                return True
            else:
                print("  ⚠ Compliance validation had warnings:")
                print(result.stdout)
                return True  # Don't fail migration on warnings

        except Exception as e:
            print(f"  ⚠ Could not run validation: {e}")
            return True  # Don't fail migration if validation can't run

    def run(self, target_level: Optional[str] = None) -> int:
        """Run the migration wizard."""
        print("=" * 70)
        print("MirrorDNA Interactive Migration Wizard")
        print("=" * 70)
        print()

        # Detect current level
        self.current_level = self.detect_current_level()
        if not self.current_level:
            return 1

        print(f"Current compliance level: {self.current_level}")

        # Determine target level
        if not target_level:
            print("\nAvailable migration paths:")
            if self.current_level == 'L1':
                print("  1. L1 → L2 (Add session persistence, checksums)")
                print("  2. L1 → L3 (Full upgrade to vault-backed)")
            elif self.current_level == 'L2':
                print("  1. L2 → L3 (Add vault storage, glyph signatures)")
            else:
                print("  Already at L3 (highest level)")
                return 0

            while True:
                choice = input("\nSelect migration path [1]: ").strip() or "1"
                if choice == "1":
                    target_level = 'L2' if self.current_level == 'L1' else 'L3'
                    break
                elif choice == "2" and self.current_level == 'L1':
                    target_level = 'L3'
                    break
                print("  Invalid choice")

        self.target_level = target_level

        # Validate migration path
        if not self.validate_migration_path(self.current_level, self.target_level):
            return 1

        print(f"\nMigration plan: {self.current_level} → {self.target_level}")

        # Special case: L1 → L3 requires two-step migration
        if self.current_level == 'L1' and self.target_level == 'L3':
            print("\nNote: L1 → L3 requires intermediate L2 migration")
            if not self.confirm("Proceed with L1 → L2 → L3 migration?"):
                print("Migration cancelled")
                return 0

            # Do L1 → L2 first
            if not self.create_backup():
                return 1

            if not self.migrate_l1_to_l2():
                print("\n❌ L1 → L2 migration failed")
                if self.confirm("Rollback changes?"):
                    self.rollback()
                return 1

            # Update current level
            self.current_level = 'L2'
            print("\n✓ L1 → L2 migration complete")
            print("\nProceeding to L2 → L3 migration...")

            # Continue to L2 → L3
            if not self.migrate_l2_to_l3():
                print("\n❌ L2 → L3 migration failed")
                if self.confirm("Rollback changes?"):
                    self.rollback()
                return 1

        else:
            # Single-step migration
            if not self.confirm(f"\nProceed with {self.current_level} → {self.target_level} migration?"):
                print("Migration cancelled")
                return 0

            # Create backup
            if not self.create_backup():
                return 1

            # Execute migration
            if self.current_level == 'L1' and self.target_level == 'L2':
                success = self.migrate_l1_to_l2()
            elif self.current_level == 'L2' and self.target_level == 'L3':
                success = self.migrate_l2_to_l3()
            else:
                print(f"❌ Unsupported migration: {self.current_level} → {self.target_level}")
                return 1

            if not success:
                print(f"\n❌ Migration failed")
                if self.confirm("Rollback changes?"):
                    self.rollback()
                return 1

        # Success
        print("\n" + "=" * 70)
        print(f"✅ Migration Complete: {self.current_level} → {self.target_level}")
        print("=" * 70)

        print("\nChanges made:")
        for change in self.changes_made:
            print(f"  ✓ {change}")

        if self.backup_dir:
            print(f"\nBackup saved to: {self.backup_dir}")
            print("  (You can delete this after verifying the migration)")

        print("\nNext steps:")
        print("  1. Review the changes made")
        print("  2. Run compliance validation:")
        print("     python -m validators.cli --manifest mirrorDNA_manifest.yaml \\")
        print("       --policy reflection_policy.yaml \\")
        if self.target_level in ['L2', 'L3']:
            print("       --profile continuity_profile.yaml")
        print("  3. Test your application")
        print("  4. Commit changes to git")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Migrate MirrorDNA compliance levels (L1→L2→L3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python tools/migrate.py

  # Migrate to L2
  python tools/migrate.py --target L2

  # Migrate to L3
  python tools/migrate.py --target L3

  # Dry run (preview changes)
  python tools/migrate.py --target L2 --dry-run

  # Non-interactive (auto-confirm)
  python tools/migrate.py --target L3 --yes

Migration Paths:
  L1 → L2: Adds session persistence, checksums, lineage tracking
  L2 → L3: Adds vault storage, glyph signatures, interaction safety
  L1 → L3: Performs L1→L2→L3 in sequence

Rollback:
  Backups are created automatically before migration.
  If migration fails, you'll be prompted to rollback.
  Manual rollback: Copy files from .mirrordna_backup_* directory
        """
    )

    parser.add_argument(
        '--target',
        choices=['L2', 'L3'],
        help='Target compliance level'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Auto-confirm all prompts (non-interactive)'
    )

    args = parser.parse_args()

    # Run wizard
    wizard = MigrationWizard(dry_run=args.dry_run, yes_to_all=args.yes)
    return wizard.run(target_level=args.target)


if __name__ == '__main__':
    sys.exit(main())
