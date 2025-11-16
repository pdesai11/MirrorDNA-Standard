#!/usr/bin/env python3
"""
MirrorDNA Project Initialization Tool

Interactive scaffold for new MirrorDNA-compliant projects.
Creates manifest, policy, profile, and supporting files.

Usage:
  # Interactive mode (recommended)
  python tools/mirrordna-init.py

  # Non-interactive mode
  python tools/mirrordna-init.py --name "MyProject" --level L2 --non-interactive

  # Specify output directory
  python tools/mirrordna-init.py --output ./my-project

  # Dry run (show what would be created)
  python tools/mirrordna-init.py --dry-run
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import uuid


def prompt(message: str, default: str = None) -> str:
    """Prompt user for input with optional default."""
    if default:
        response = input(f"{message} [{default}]: ").strip()
        return response if response else default
    else:
        while True:
            response = input(f"{message}: ").strip()
            if response:
                return response
            print("  This field is required. Please enter a value.")


def confirm(message: str, default: bool = True) -> bool:
    """Ask yes/no question."""
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


def select_option(message: str, options: list, default: int = 0) -> str:
    """Select from list of options."""
    print(f"\n{message}")
    for i, option in enumerate(options, 1):
        marker = "*" if i == default + 1 else " "
        print(f"  {marker} {i}. {option}")

    while True:
        response = input(f"Select [1-{len(options)}] [{default + 1}]: ").strip()
        if not response:
            return options[default]
        try:
            idx = int(response) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"  Please enter a number between 1 and {len(options)}")


class ProjectInitializer:
    """Handles project initialization."""

    def __init__(self, interactive: bool = True, dry_run: bool = False):
        self.interactive = interactive
        self.dry_run = dry_run
        self.config = {}

    def gather_info(self, args):
        """Gather project information."""
        print("=" * 70)
        print("MirrorDNA Project Initialization")
        print("=" * 70)
        print()

        if self.interactive:
            print("Let's set up your MirrorDNA-compliant project.\n")

            # Project name
            self.config['name'] = prompt("Project name", args.name or "my-mirrordna-project")

            # Description
            self.config['description'] = prompt("Brief description", "A MirrorDNA-compliant project")

            # Compliance level
            level_options = [
                "L1 - Basic Reflection (cite-or-silence, basic tracking)",
                "L2 - Continuity Aware (session persistence, checksums)",
                "L3 - Vault-Backed Sovereign (full lineage, glyph signatures)"
            ]
            level_choice = select_option("Compliance level:", level_options, 1)
            self.config['level'] = level_choice.split()[0]  # Extract L1, L2, or L3

            # Layers
            print("\nWhich MirrorDNA layers will you use?")
            self.config['mirrorDNA_protocol'] = confirm("  MirrorDNA Protocol", True)
            self.config['lingOS'] = confirm("  LingOS (language operating system)", False)
            self.config['activeMirrorOS'] = confirm("  ActiveMirrorOS", False)
            self.config['trustByDesign'] = confirm("  Trust-by-Design", True)

            # Storage type for L2+
            if self.config['level'] in ['L2', 'L3']:
                storage_options = ["File system", "Vault (Obsidian)", "Database", "Custom"]
                storage_choice = select_option("State persistence storage:", storage_options, 0)
                self.config['storage_type'] = storage_choice.split()[0].lower()

            # Vault for L3
            if self.config['level'] == 'L3':
                self.config['use_vault'] = confirm("Use Obsidian vault template", True)

            # Additional features
            print("\nAdditional features:")
            self.config['create_gitignore'] = confirm("  Create .gitignore", True)
            self.config['create_readme'] = confirm("  Create README.md", True)
            self.config['install_hooks'] = confirm("  Install git pre-commit hook", True)
            self.config['setup_ci'] = confirm("  Set up GitHub Actions CI/CD", True)

        else:
            # Non-interactive mode
            self.config['name'] = args.name or "my-mirrordna-project"
            self.config['description'] = "A MirrorDNA-compliant project"
            self.config['level'] = args.level or "L1"
            self.config['mirrorDNA_protocol'] = True
            self.config['lingOS'] = False
            self.config['activeMirrorOS'] = False
            self.config['trustByDesign'] = True
            self.config['storage_type'] = 'file'
            self.config['use_vault'] = False
            self.config['create_gitignore'] = True
            self.config['create_readme'] = True
            self.config['install_hooks'] = False
            self.config['setup_ci'] = False

    def create_manifest(self) -> str:
        """Generate manifest content."""
        level_map = {
            'L1': 'level_1_basic_reflection',
            'L2': 'level_2_continuity_aware',
            'L3': 'level_3_vault_backed_sovereign'
        }

        manifest = f"""name: "{self.config['name']}"
version: "1.0.0"
description: "{self.config['description']}"
mirrorDNA_compliance_level: "{level_map[self.config['level']]}"

layers:
  mirrorDNA_protocol: {str(self.config['mirrorDNA_protocol']).lower()}
  lingOS: {str(self.config['lingOS']).lower()}
  activeMirrorOS: {str(self.config['activeMirrorOS']).lower()}
  trustByDesign: {str(self.config['trustByDesign']).lower()}

continuity_profile: "./continuity_profile.yaml"
reflection_policy: "./reflection_policy.yaml"
"""

        if self.config['level'] == 'L3':
            vault_id = f"AMOS://{self.config['name'].replace(' ', '')}/Vault/v1.0"
            manifest += f'\nvault_id: "{vault_id}"\n'

        manifest += f"""
maintainers:
  - name: "Your Name"
    email: "you@example.com"

created: "{datetime.now().strftime('%Y-%m-%d')}"
"""
        return manifest

    def create_reflection_policy(self) -> str:
        """Generate reflection policy content."""
        policy = f"""policy_version: "1.0.0"
reflection_mode: "constitutive"

uncertainty_handling:
  cite_or_silence: true
  unknown_marker: "[Unknown]"
  speculation_allowed: true
  speculation_marker: "[Speculation]"

anti_hallucination:
  grounding_required: true
  source_citation: true
  hallucination_detection: false
  correction_protocol: "manual"
"""

        if self.config['level'] in ['L2', 'L3']:
            policy += """
reflection_protocols:
  session_reflection: true
  continuity_checks: true
  state_validation: true
"""

        if self.config['level'] == 'L3':
            policy += """
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

interaction_safety:
  session_duration_warnings: true
  dependency_detection: true
  human_escalation: true
  rhythm_checks: true
  max_session_duration_minutes: 120
"""
        return policy

    def create_continuity_profile(self) -> str:
        """Generate continuity profile content (L2+)."""
        storage_map = {
            'file': 'file',
            'vault': 'vault',
            'database': 'database',
            'custom': 'custom'
        }

        storage = storage_map.get(self.config.get('storage_type', 'file'), 'file')
        mechanism = 'vault_backed' if self.config['level'] == 'L3' else 'session_storage'

        profile = f"""profile_version: "1.0.0"
continuity_mechanism: "{mechanism}"

state_persistence:
  enabled: true
  storage_type: "{storage}"
  storage_location: "./state"
  encryption: {str(self.config['level'] == 'L3').lower()}
  checksum_validation: true

session_tracking:
  enabled: true
  session_id_format: "uuid"
  lineage_tracking: true
"""

        if self.config['level'] == 'L3':
            vault_id = f"AMOS://{self.config['name'].replace(' ', '')}/Vault/v1.0"
            profile += f"""  vault_integration: true

vault_id: "{vault_id}"
sovereign_identity:
  enabled: true
  identity_binding: "vault_id"
  ownership: "user"
"""

        profile += """
recovery:
  enabled: true
  recovery_mechanism: "state_reload"
  backup_enabled: false
"""
        return profile

    def create_gitignore(self) -> str:
        """Generate .gitignore content."""
        return """# MirrorDNA State Files
state/
*.state.json
session_*.json

# Vault (if using Obsidian)
vault/.obsidian/workspace*
vault/.trash/

# Compliance Reports
compliance-report*.json
*.compliance.json

# Badges
*badge*.svg

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
*.egg-info/

# Virtual Environment
venv/
.venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""

    def create_readme(self) -> str:
        """Generate README.md content."""
        level_badges = {
            'L1': 'L1%20Basic-passed-brightgreen',
            'L2': 'L2%20Continuity-passed-blue',
            'L3': 'L3%20Sovereign-passed-yellow'
        }

        badge = level_badges.get(self.config['level'], 'L1%20Basic-passed-brightgreen')

        # Build compliance features list
        features = []
        features.append("- ✅ Cite-or-silence (Anti-Hallucination Protocol)")
        features.append("- ✅ Explicit uncertainty marking")
        if self.config['level'] in ['L2', 'L3']:
            features.append("- ✅ Session persistence and continuity")
            features.append("- ✅ Checksum validation")
        if self.config['level'] == 'L3':
            features.append("- ✅ Vault-backed storage")
            features.append("- ✅ Full lineage tracking")
            features.append("- ✅ Glyph signatures")

        features_text = '\n'.join(features)

        # Build validation command for setup
        setup_cmd = "python -m validators.cli --manifest mirrorDNA_manifest.yaml --policy reflection_policy.yaml"
        if self.config['level'] in ['L2', 'L3']:
            setup_cmd += " --profile continuity_profile.yaml"

        # Build validation command for usage section
        usage_cmd_parts = [
            "python -m validators.cli \\",
            "  --manifest mirrorDNA_manifest.yaml \\",
            "  --policy reflection_policy.yaml"
        ]
        if self.config['level'] in ['L2', 'L3']:
            usage_cmd_parts.append(" \\")
            usage_cmd_parts.append("  --profile continuity_profile.yaml")

        usage_cmd = '\n'.join(usage_cmd_parts)

        # Determine glyph for footer
        if self.config['level'] == 'L3':
            footer_glyph = 'SOVEREIGN'
        elif self.config['level'] == 'L2':
            footer_glyph = 'CONTINUITY'
        else:
            footer_glyph = 'REFLECTION'

        return f"""# {self.config['name']}

![MirrorDNA](https://img.shields.io/badge/MirrorDNA-{badge})

{self.config['description']}

## MirrorDNA Compliance

This project implements **MirrorDNA {self.config['level']}** compliance.

**Compliance Level:** {self.config['level']}
{features_text}

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Validate compliance
{setup_cmd}
```

## Usage

[Add your project-specific usage instructions here]

## MirrorDNA Validation

Validate compliance:

```bash
{usage_cmd}
```

## License

[Specify your license]

## Contributing

Please ensure all changes maintain MirrorDNA {self.config['level']} compliance.

---

⟡⟦{footer_glyph}⟧ · Generated by MirrorDNA Project Init Tool
"""

    def write_files(self, output_dir: Path):
        """Write all generated files."""
        files = {
            'mirrorDNA_manifest.yaml': self.create_manifest(),
            'reflection_policy.yaml': self.create_reflection_policy(),
        }

        if self.config['level'] in ['L2', 'L3']:
            files['continuity_profile.yaml'] = self.create_continuity_profile()

        if self.config.get('create_gitignore'):
            files['.gitignore'] = self.create_gitignore()

        if self.config.get('create_readme'):
            files['README.md'] = self.create_readme()

        # Create output directory
        if not self.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Creating files in: {output_dir}")
        print("=" * 70)

        for filename, content in files.items():
            filepath = output_dir / filename
            if self.dry_run:
                print(f"  Would create: {filename} ({len(content)} bytes)")
            else:
                filepath.write_text(content)
                print(f"  ✓ Created: {filename} ({len(content)} bytes)")

        # Create directories
        if self.config['level'] in ['L2', 'L3']:
            state_dir = output_dir / 'state'
            if self.dry_run:
                print(f"  Would create: state/ directory")
            else:
                state_dir.mkdir(exist_ok=True)
                (state_dir / '.gitkeep').write_text('')
                print(f"  ✓ Created: state/ directory")

        print("=" * 70)

        # Post-creation instructions
        print("\n✅ Project initialized successfully!")
        print(f"\nNext steps:")
        print(f"  1. cd {output_dir}")
        print(f"  2. Review and customize the generated files")

        if self.config.get('install_hooks'):
            print(f"  3. Install pre-commit hook: bash tools/install-hooks.sh --install")

        if self.config.get('setup_ci'):
            print(f"  4. Set up CI/CD:")
            print(f"     mkdir -p .github/workflows")
            print(f"     cp path/to/templates/github-actions-mirrordna.yml .github/workflows/")

        print(f"  5. Validate compliance:")
        cmd = f"     python -m validators.cli --manifest mirrorDNA_manifest.yaml --policy reflection_policy.yaml"
        if self.config['level'] in ['L2', 'L3']:
            cmd += " --profile continuity_profile.yaml"
        print(cmd)

        print(f"\n📚 Documentation:")
        print(f"  - MirrorDNA Standard: https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA-Standard")
        print(f"  - Migration Guide: spec/Compliance_Migration_Guide_v1.0.md")
        print(f"  - Validator Architecture: validators/ARCHITECTURE.md")


def main():
    parser = argparse.ArgumentParser(
        description='Initialize a new MirrorDNA-compliant project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python tools/mirrordna-init.py

  # Non-interactive mode
  python tools/mirrordna-init.py --name "MyProject" --level L2 --non-interactive

  # Specify output directory
  python tools/mirrordna-init.py --output ./my-new-project

  # Dry run
  python tools/mirrordna-init.py --dry-run

Compliance Levels:
  L1 - Basic Reflection: Cite-or-silence, basic tracking
  L2 - Continuity Aware: Session persistence, checksums
  L3 - Vault-Backed Sovereign: Full lineage, glyph signatures
        """
    )

    parser.add_argument(
        '--name',
        help='Project name'
    )
    parser.add_argument(
        '--level',
        choices=['L1', 'L2', 'L3'],
        help='Compliance level'
    )
    parser.add_argument(
        '--output',
        default='.',
        help='Output directory (default: current directory)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Non-interactive mode (use defaults)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without writing files'
    )

    args = parser.parse_args()

    # Initialize
    initializer = ProjectInitializer(
        interactive=not args.non_interactive,
        dry_run=args.dry_run
    )

    # Gather information
    initializer.gather_info(args)

    # Create files
    output_dir = Path(args.output)
    initializer.write_files(output_dir)

    return 0


if __name__ == '__main__':
    sys.exit(main())
