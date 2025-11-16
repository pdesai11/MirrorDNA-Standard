#!/usr/bin/env python3
"""
MirrorDNA Compliance Badge Generator

Generates SVG badges based on validation results.
Compatible with shields.io style for use in README files.

Usage:
  # Generate from validation report
  python tools/generate-badge.py --report compliance-report.json --output badge.svg

  # Auto-detect from manifest
  python tools/generate-badge.py --auto

  # Generate for specific level
  python tools/generate-badge.py --level L3 --status passed --output badge.svg

  # Custom text
  python tools/generate-badge.py --level L2 --status passed --label "Compliance" --output badge.svg
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple


# Badge color schemes
COLORS = {
    'L1': {
        'passed': '#4c1',  # Green
        'failed': '#e05d44',  # Red
        'warning': '#fe7d37',  # Orange
    },
    'L2': {
        'passed': '#007ec6',  # Blue
        'failed': '#e05d44',  # Red
        'warning': '#fe7d37',  # Orange
    },
    'L3': {
        'passed': '#dfb317',  # Gold
        'failed': '#e05d44',  # Red
        'warning': '#fe7d37',  # Orange
    },
    'non_compliant': {
        'passed': '#9f9f9f',  # Gray (shouldn't happen)
        'failed': '#e05d44',  # Red
        'warning': '#fe7d37',  # Orange
    }
}

# Level display names
LEVEL_NAMES = {
    'level_1_basic_reflection': 'L1',
    'level_2_continuity_aware': 'L2',
    'level_3_vault_backed_sovereign': 'L3',
    'non_compliant': 'Non-Compliant'
}


def generate_svg_badge(
    label: str,
    message: str,
    color: str,
    label_color: str = '#555'
) -> str:
    """
    Generate SVG badge content.

    Args:
        label: Left side text (e.g., "MirrorDNA")
        message: Right side text (e.g., "L2 Passed")
        color: Background color for message side
        label_color: Background color for label side

    Returns:
        SVG content as string
    """
    # Calculate text widths (approximate)
    label_width = len(label) * 6 + 10
    message_width = len(message) * 6 + 10
    total_width = label_width + message_width

    # Label center point
    label_center = label_width / 2

    # Message center point
    message_center = label_width + (message_width / 2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{total_width}" height="20" role="img" aria-label="{label}: {message}">
    <title>{label}: {message}</title>
    <linearGradient id="s" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="r">
        <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#r)">
        <rect width="{label_width}" height="20" fill="{label_color}"/>
        <rect x="{label_width}" width="{message_width}" height="20" fill="{color}"/>
        <rect width="{total_width}" height="20" fill="url(#s)"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
        <text aria-hidden="true" x="{label_center * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(label_width - 10) * 10}">{label}</text>
        <text x="{label_center * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(label_width - 10) * 10}">{label}</text>
        <text aria-hidden="true" x="{message_center * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(message_width - 10) * 10}">{message}</text>
        <text x="{message_center * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(message_width - 10) * 10}">{message}</text>
    </g>
</svg>'''

    return svg


def parse_compliance_report(report_path: Path) -> Tuple[str, str, str]:
    """
    Parse compliance report and extract badge info.

    Args:
        report_path: Path to JSON compliance report

    Returns:
        Tuple of (level, status, color)
    """
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
    except Exception as e:
        print(f"Error reading report: {e}", file=sys.stderr)
        return 'non_compliant', 'failed', COLORS['non_compliant']['failed']

    # Extract info
    passed = report.get('overall_passed', False)
    declared_level = report.get('declared_level', 'non_compliant')
    detected_level = report.get('detected_level', 'non_compliant')
    errors = report.get('total_errors', 0)
    warnings = report.get('total_warnings', 0)

    # Determine level to display (use detected, not declared)
    level_key = detected_level if detected_level != 'unknown' else declared_level
    level_display = LEVEL_NAMES.get(level_key, 'Unknown')

    # Determine status
    if passed:
        status = 'passed'
        status_text = 'Passed'
    elif warnings > 0 and errors == 0:
        status = 'warning'
        status_text = f'{warnings} Warnings'
    else:
        status = 'failed'
        status_text = f'{errors} Errors'

    # Get color
    if level_key in COLORS:
        color = COLORS[level_key][status]
    else:
        color = COLORS['non_compliant'][status]

    return level_display, status_text, color


def auto_detect_manifest() -> Tuple[str, str, str]:
    """
    Auto-detect compliance level from manifest.

    Returns:
        Tuple of (level, status, color)
    """
    manifest_path = Path('mirrorDNA_manifest.yaml')

    if not manifest_path.exists():
        return 'Unknown', 'No Manifest', COLORS['non_compliant']['failed']

    try:
        # Simple YAML parsing (without PyYAML dependency)
        content = manifest_path.read_text()
        level = 'non_compliant'

        for line in content.splitlines():
            if 'mirrorDNA_compliance_level:' in line:
                level_value = line.split(':', 1)[1].strip().strip('"\'')
                level = LEVEL_NAMES.get(level_value, 'Unknown')
                break

        # Can't determine pass/fail without validation
        return level, 'Declared', COLORS.get(level, {}).get('passed', '#9f9f9f')

    except Exception as e:
        print(f"Error reading manifest: {e}", file=sys.stderr)
        return 'Unknown', 'Error', COLORS['non_compliant']['failed']


def main():
    parser = argparse.ArgumentParser(
        description='Generate MirrorDNA compliance badges',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From validation report
  python tools/generate-badge.py --report compliance-report.json -o badge.svg

  # Auto-detect from manifest
  python tools/generate-badge.py --auto -o badge.svg

  # Manual specification
  python tools/generate-badge.py --level L3 --status passed -o badge.svg

  # Custom label
  python tools/generate-badge.py --report report.json --label "Compliance" -o badge.svg

Badge Colors:
  - L1 Passed: Green
  - L2 Passed: Blue
  - L3 Passed: Gold
  - Failed: Red
  - Warnings: Orange
        """
    )

    parser.add_argument(
        '--report',
        help='Path to JSON compliance report'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect from manifest (shows declared level only)'
    )
    parser.add_argument(
        '--level',
        choices=['L1', 'L2', 'L3', 'Unknown'],
        help='Compliance level (manual mode)'
    )
    parser.add_argument(
        '--status',
        choices=['passed', 'failed', 'warning'],
        help='Compliance status (manual mode)'
    )
    parser.add_argument(
        '--label',
        default='MirrorDNA',
        help='Badge label text (default: MirrorDNA)'
    )
    parser.add_argument(
        '-o', '--output',
        default='mirrordna-badge.svg',
        help='Output SVG file path (default: mirrordna-badge.svg)'
    )

    args = parser.parse_args()

    # Determine badge content
    if args.report:
        # Parse report
        level, status_text, color = parse_compliance_report(Path(args.report))
        message = f'{level} {status_text}'

    elif args.auto:
        # Auto-detect
        level, status_text, color = auto_detect_manifest()
        message = f'{level} {status_text}'

    elif args.level and args.status:
        # Manual mode
        level = args.level
        status = args.status

        # Get color
        if level in COLORS:
            color = COLORS[level][status]
        else:
            color = COLORS['non_compliant'][status]

        status_text = status.capitalize()
        message = f'{level} {status_text}'

    else:
        print("Error: Must specify --report, --auto, or both --level and --status", file=sys.stderr)
        parser.print_help()
        return 1

    # Generate badge
    svg_content = generate_svg_badge(
        label=args.label,
        message=message,
        color=color
    )

    # Write output
    output_path = Path(args.output)
    try:
        output_path.write_text(svg_content)
        print(f"✓ Badge generated: {output_path}")
        print(f"  Level: {level}")
        print(f"  Status: {status_text}")
        print(f"  Color: {color}")
        return 0
    except Exception as e:
        print(f"Error writing badge: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
