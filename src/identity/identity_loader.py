"""MirrorDNA Identity Loader.

Implements the two-layer identity model:
1. Master Standard v16 (abstract, user-agnostic constitutional spec)
2. User Profile (user-specific parameters overlay)

The identity loader ensures that:
- Standard is loaded first (constitutional foundation)
- Profile is loaded second (user customization)
- Both are combined into a MirrorIdentity object for agent use
"""

from pathlib import Path
import yaml

# Default paths relative to repository root
STANDARD_PATH = Path("spec/mirror/MirrorDNA_Master_Standard_v16.md")
PROFILES_DIR = Path("spec/mirror/profiles")


class MirrorIdentity:
    """Represents the combined Mirror identity (Standard + Profile).

    Attributes:
        standard: The full text of the Master Standard document.
        profile: Dictionary containing user-specific profile data.
    """

    def __init__(self, standard_text: str, profile_data: dict):
        self.standard = standard_text
        self.profile = profile_data

    def get_profile_summary(self) -> str:
        """Return a compact YAML-style summary of the profile for prompts."""
        lines = []
        lines.append(f"User: {self.profile.get('user_name', 'Unknown')}")
        lines.append(f"Role: {self.profile.get('role', 'Unknown')}")
        lines.append(f"Timezone: {self.profile.get('timezone', 'Unknown')}")
        lines.append(f"Cognitive Mode: {self.profile.get('cognitive_mode', 'Standard')}")

        if self.profile.get('core_projects'):
            lines.append(f"Core Projects: {', '.join(self.profile['core_projects'])}")

        if self.profile.get('overrides'):
            overrides = self.profile['overrides']
            lines.append("Overrides:")
            for key, value in overrides.items():
                lines.append(f"  - {key}: {value}")

        if self.profile.get('glyphs_enabled'):
            lines.append("Glyphs: Enabled")

        lines.append(f"Drift Tolerance: {self.profile.get('drift_tolerance', 0.0)}")

        return "\n".join(lines)

    def build_system_prompt(self, task_instructions: str = "") -> str:
        """Build a complete system prompt with Standard, Profile, and task instructions.

        Args:
            task_instructions: Optional task-specific instructions to append.

        Returns:
            A formatted system prompt string.
        """
        parts = [
            self.standard,
            "\n---\n",
            "# MirrorDNA Profile",
            self.get_profile_summary(),
        ]

        if task_instructions:
            parts.extend([
                "\n---\n",
                "# Task Instructions",
                task_instructions
            ])

        return "\n".join(parts)


def load_profile(profile_name: str = "profile_paul_v16.yaml") -> dict:
    """Load a user profile from the profiles directory.

    Args:
        profile_name: Name of the profile YAML file.

    Returns:
        Dictionary containing profile data.

    Raises:
        FileNotFoundError: If the profile file doesn't exist.
    """
    path = PROFILES_DIR / profile_name
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_standard() -> str:
    """Load the Master Standard document.

    Returns:
        Full text content of the Master Standard.

    Raises:
        FileNotFoundError: If the standard file doesn't exist.
    """
    if not STANDARD_PATH.exists():
        raise FileNotFoundError(f"Standard not found: {STANDARD_PATH}")
    with open(STANDARD_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_identity(profile_name: str = "profile_paul_v16.yaml") -> MirrorIdentity:
    """Load the complete Mirror identity (Standard + Profile).

    This is the main entry point for loading identity configuration.
    The loading order is:
    1. Master Standard (constitutional foundation)
    2. User Profile (customization overlay)

    Args:
        profile_name: Name of the profile YAML file to load.

    Returns:
        MirrorIdentity object containing both Standard and Profile.

    Raises:
        FileNotFoundError: If either Standard or Profile file is missing.

    Example:
        identity = load_identity()  # default Paul profile
        identity = load_identity("profile_other_user_v16.yaml")

        # Access components
        standard_text = identity.standard
        profile_data = identity.profile

        # Build system prompt
        system_prompt = identity.build_system_prompt("Complete this task...")
    """
    std = load_standard()
    prof = load_profile(profile_name)
    return MirrorIdentity(std, prof)
