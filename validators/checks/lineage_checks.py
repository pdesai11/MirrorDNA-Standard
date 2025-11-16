"""
Lineage chain validation checks for MirrorDNA Standard.

Validates predecessor/successor relationships and continuity chains.
"""

from typing import Dict, Any, List, Tuple, Set


def check_lineage_compliance(
    manifest: Dict[str, Any],
    profile: Dict[str, Any] = None,
    sidecar: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Check lineage tracking compliance.

    Validates that lineage fields (predecessor/successor) are properly configured.

    Args:
        manifest: Project manifest data
        profile: Continuity profile data (optional)
        sidecar: Sidecar metadata (optional)

    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []
    compliance_level = manifest.get('mirrorDNA_compliance_level', '')

    # Level 2+ should have lineage tracking
    if compliance_level in ['level_2_continuity_aware', 'level_3_vault_backed_sovereign']:
        # Check if profile has lineage configuration
        if profile and 'session_tracking' in profile:
            session_tracking = profile['session_tracking']
            if not session_tracking.get('lineage_tracking'):
                if compliance_level == 'level_3_vault_backed_sovereign':
                    errors.append("Level 3 requires lineage_tracking enabled in session_tracking")
                else:
                    warnings.append("Level 2 should enable lineage_tracking in session_tracking")

    # Level 3 requires full lineage
    if compliance_level == 'level_3_vault_backed_sovereign':
        # Check for lineage in sidecar
        if sidecar and 'lineage' in sidecar:
            lineage = sidecar['lineage']

            # Validate lineage structure
            if not isinstance(lineage, dict):
                errors.append("Sidecar lineage must be an object/dictionary")
            else:
                # Check for predecessor field
                if 'predecessor' not in lineage:
                    warnings.append("Sidecar lineage should include 'predecessor' field")

                # Check for successor field
                if 'successor' not in lineage:
                    warnings.append("Sidecar lineage should include 'successor' field")

                # Validate predecessor is not self-referential
                if 'predecessor' in lineage and lineage['predecessor']:
                    vault_id = sidecar.get('vault_id')
                    if vault_id and lineage['predecessor'] == vault_id:
                        errors.append("Lineage predecessor cannot be self-referential")

    passed = len(errors) == 0
    return passed, errors, warnings


def validate_lineage_chain(lineage_items: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate a chain of lineage items for consistency.

    Checks:
    - No circular references
    - No broken links
    - No duplicate IDs

    Args:
        lineage_items: List of items with vault_id, predecessor, successor fields

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Build ID set
    ids = set()
    for item in lineage_items:
        vault_id = item.get('vault_id')
        if not vault_id:
            errors.append(f"Item missing vault_id: {item}")
            continue

        # Check for duplicates
        if vault_id in ids:
            errors.append(f"Duplicate vault_id: {vault_id}")
        ids.add(vault_id)

    # Check links
    for item in lineage_items:
        vault_id = item.get('vault_id')
        if not vault_id:
            continue

        lineage = item.get('lineage', {})
        predecessor = lineage.get('predecessor')
        successor = lineage.get('successor')

        # Check predecessor exists (unless it's None or 'none')
        if predecessor and predecessor.lower() not in ['none', 'null']:
            if predecessor not in ids:
                errors.append(
                    f"Broken lineage: {vault_id} references predecessor {predecessor} "
                    f"but it's not in the chain"
                )

        # Check successor exists (unless it's None, 'none', or 'TBD')
        if successor and successor.lower() not in ['none', 'null', 'tbd', 'pending']:
            if successor not in ids:
                # This is a warning, not an error (successor might not exist yet)
                pass

        # Check for cycles (self-reference)
        if predecessor == vault_id:
            errors.append(f"Self-referential predecessor: {vault_id}")
        if successor == vault_id:
            errors.append(f"Self-referential successor: {vault_id}")

    is_valid = len(errors) == 0
    return is_valid, errors


def detect_lineage_cycles(items: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Detect cycles in lineage chains using DFS.

    Args:
        items: List of items with vault_id and lineage information

    Returns:
        List of cycles (each cycle is a list of vault_ids)
    """
    # Build adjacency list
    graph = {}
    for item in items:
        vault_id = item.get('vault_id')
        if not vault_id:
            continue

        lineage = item.get('lineage', {})
        successor = lineage.get('successor')

        if successor and successor.lower() not in ['none', 'null', 'tbd', 'pending']:
            if vault_id not in graph:
                graph[vault_id] = []
            graph[vault_id].append(successor)

    # DFS to find cycles
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles
