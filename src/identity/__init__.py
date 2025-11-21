"""MirrorDNA Identity Module.

This module provides the identity loading infrastructure for MirrorDNA.
It implements the two-layer identity model:

1. Master Standard (abstract, user-agnostic)
2. User Profile (user-specific overlay)

Usage:
    from identity.identity_loader import load_identity

    identity = load_identity()  # default Paul profile
    # or
    identity = load_identity("profile_other_user_v16.yaml")

    standard_text = identity.standard
    profile_data = identity.profile
"""

from .identity_loader import load_identity, load_profile, load_standard, MirrorIdentity

__all__ = ["load_identity", "load_profile", "load_standard", "MirrorIdentity"]
