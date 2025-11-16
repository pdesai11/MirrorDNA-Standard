#!/usr/bin/env python3
"""
MirrorDNA Watch Mode Validator

Monitors file system for changes and runs validation automatically.
Provides real-time feedback on compliance status.

Usage:
  # Watch current directory
  python tools/watch.py

  # Watch specific files
  python tools/watch.py --files mirrorDNA_manifest.yaml reflection_policy.yaml

  # Watch with custom interval
  python tools/watch.py --interval 2

  # Enable desktop notifications (macOS/Linux)
  python tools/watch.py --notify

  # Quiet mode (only show on changes)
  python tools/watch.py --quiet

Features:
  - Poll-based file watching (no external dependencies)
  - Auto-runs validation when files change
  - Debouncing to avoid repeated validations
  - Optional desktop notifications
  - Colorized terminal output
  - Configurable watch interval
"""

import argparse
import sys
import time
import subprocess
import os
from pathlib import Path
from typing import Dict, Set, Optional
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


class FileWatcher:
    """Watches files for changes using polling."""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.file_mtimes: Dict[Path, float] = {}
        self.last_validation = 0
        self.debounce_seconds = 0.5

    def add_file(self, filepath: Path):
        """Add a file to watch."""
        if filepath.exists():
            self.file_mtimes[filepath] = filepath.stat().st_mtime

    def check_changes(self) -> Set[Path]:
        """Check for file changes. Returns set of changed files."""
        changed_files = set()

        for filepath in list(self.file_mtimes.keys()):
            if not filepath.exists():
                # File was deleted
                changed_files.add(filepath)
                del self.file_mtimes[filepath]
                continue

            current_mtime = filepath.stat().st_mtime
            if current_mtime != self.file_mtimes[filepath]:
                # File was modified
                changed_files.add(filepath)
                self.file_mtimes[filepath] = current_mtime

        return changed_files

    def should_validate(self) -> bool:
        """Check if enough time has passed for debouncing."""
        now = time.time()
        if now - self.last_validation >= self.debounce_seconds:
            self.last_validation = now
            return True
        return False


class ValidationRunner:
    """Runs MirrorDNA validation."""

    def __init__(self, manifest: Path, policy: Optional[Path] = None,
                 profile: Optional[Path] = None, no_color: bool = False):
        self.manifest = manifest
        self.policy = policy
        self.profile = profile
        self.no_color = no_color
        self.last_result = None

    def run(self) -> bool:
        """Run validation. Returns True if passed."""
        try:
            cmd = ['python', '-m', 'validators.cli', '--manifest', str(self.manifest)]

            if self.policy and self.policy.exists():
                cmd.extend(['--policy', str(self.policy)])

            if self.profile and self.profile.exists():
                cmd.extend(['--profile', str(self.profile)])

            if self.no_color:
                cmd.append('--no-color')

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            self.last_result = {
                'passed': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'timestamp': datetime.now()
            }

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}⚠️  Validation timeout{Colors.RESET}")
            return False

        except Exception as e:
            print(f"{Colors.RED}⚠️  Validation error: {e}{Colors.RESET}")
            return False


class NotificationManager:
    """Handles desktop notifications."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.notifier = self._detect_notifier()

    def _detect_notifier(self) -> Optional[str]:
        """Detect available notification system."""
        if not self.enabled:
            return None

        # macOS
        if sys.platform == 'darwin':
            return 'osascript'

        # Linux with notify-send
        if sys.platform.startswith('linux'):
            try:
                subprocess.run(['which', 'notify-send'], capture_output=True, check=True)
                return 'notify-send'
            except subprocess.CalledProcessError:
                pass

        return None

    def notify(self, title: str, message: str, success: bool = True):
        """Send desktop notification."""
        if not self.notifier:
            return

        try:
            if self.notifier == 'osascript':
                # macOS notification
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', script], check=True)

            elif self.notifier == 'notify-send':
                # Linux notification
                icon = 'dialog-information' if success else 'dialog-error'
                subprocess.run(['notify-send', '-i', icon, title, message], check=True)

        except Exception as e:
            # Silently fail on notification errors
            pass


class WatchMode:
    """Main watch mode controller."""

    def __init__(self, files: list, interval: float = 1.0, quiet: bool = False,
                 notify: bool = False, no_color: bool = False):
        self.files = [Path(f) for f in files]
        self.interval = interval
        self.quiet = quiet
        self.no_color = no_color

        self.watcher = FileWatcher(interval=interval)
        self.notifications = NotificationManager(enabled=notify)

        # Determine validation files
        self.manifest = self._find_file('mirrorDNA_manifest.yaml')
        self.policy = self._find_file('reflection_policy.yaml')
        self.profile = self._find_file('continuity_profile.yaml')

        if not self.manifest:
            print(f"{Colors.RED}Error: mirrorDNA_manifest.yaml not found{Colors.RESET}")
            sys.exit(1)

        self.validator = ValidationRunner(
            self.manifest,
            self.policy,
            self.profile,
            no_color=no_color
        )

        # Add files to watch
        for filepath in [self.manifest, self.policy, self.profile]:
            if filepath and filepath.exists():
                self.watcher.add_file(filepath)

    def _find_file(self, filename: str) -> Optional[Path]:
        """Find file in current directory or specified files."""
        # Check specified files
        for filepath in self.files:
            if filepath.name == filename:
                return filepath

        # Check current directory
        filepath = Path(filename)
        if filepath.exists():
            return filepath

        return None

    def print_status(self, message: str, color: str = ''):
        """Print status message."""
        if self.no_color:
            print(message)
        else:
            print(f"{color}{message}{Colors.RESET}")

    def run(self):
        """Run watch mode."""
        self.print_status("\n" + "=" * 70, Colors.CYAN)
        self.print_status("MirrorDNA Watch Mode", Colors.CYAN + Colors.BOLD)
        self.print_status("=" * 70, Colors.CYAN)

        print(f"\nWatching files:")
        for filepath in [self.manifest, self.policy, self.profile]:
            if filepath:
                status = "✓" if filepath.exists() else "✗"
                self.print_status(f"  {status} {filepath}", Colors.GREEN if filepath.exists() else Colors.RED)

        print(f"\nInterval: {self.interval}s")
        print("Press Ctrl+C to stop\n")

        # Run initial validation
        self.print_status("Running initial validation...", Colors.BLUE)
        passed = self.validator.run()
        self._print_validation_result(passed, initial=True)

        # Watch loop
        try:
            iteration = 0
            while True:
                time.sleep(self.interval)
                iteration += 1

                # Check for changes
                changed_files = self.watcher.check_changes()

                if changed_files:
                    # Files changed
                    print()
                    self.print_status(f"[{datetime.now().strftime('%H:%M:%S')}] Files changed:", Colors.YELLOW)
                    for filepath in changed_files:
                        print(f"  - {filepath.name}")

                    # Wait for debounce
                    if self.watcher.should_validate():
                        self.print_status("\nRunning validation...", Colors.BLUE)
                        passed = self.validator.run()
                        self._print_validation_result(passed)

                elif not self.quiet and iteration % 10 == 0:
                    # Periodic status update (every 10 iterations)
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.print_status(f"[{timestamp}] Watching... (no changes)", Colors.DIM)

        except KeyboardInterrupt:
            print()
            self.print_status("\nWatch mode stopped", Colors.YELLOW)

    def _print_validation_result(self, passed: bool, initial: bool = False):
        """Print validation result."""
        result = self.validator.last_result

        if passed:
            self.print_status("✅ VALIDATION PASSED", Colors.GREEN + Colors.BOLD)
            if not initial:
                self.notifications.notify(
                    "MirrorDNA Validation",
                    "Compliance validation passed ✓",
                    success=True
                )
        else:
            self.print_status("❌ VALIDATION FAILED", Colors.RED + Colors.BOLD)
            if not initial:
                self.notifications.notify(
                    "MirrorDNA Validation",
                    "Compliance validation failed ✗",
                    success=False
                )

        # Print output
        if result['stdout']:
            print()
            print(result['stdout'])

        if result['stderr']:
            self.print_status("\nErrors:", Colors.RED)
            print(result['stderr'])

        print()


def main():
    parser = argparse.ArgumentParser(
        description='Watch MirrorDNA files and validate on changes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch current directory
  python tools/watch.py

  # Watch specific files
  python tools/watch.py --files mirrorDNA_manifest.yaml reflection_policy.yaml

  # Custom watch interval (seconds)
  python tools/watch.py --interval 2

  # Enable desktop notifications
  python tools/watch.py --notify

  # Quiet mode (only show changes)
  python tools/watch.py --quiet

  # No color output
  python tools/watch.py --no-color

Features:
  - Auto-detects manifest, policy, and profile files
  - Runs validation when files change
  - Debounces rapid changes (0.5s delay)
  - Optional desktop notifications (macOS/Linux)
  - Colorized output

Notifications:
  - macOS: Uses osascript (built-in)
  - Linux: Uses notify-send (install libnotify-bin)
        """
    )

    parser.add_argument(
        '--files',
        nargs='+',
        default=[],
        help='Specific files to watch'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Watch interval in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (only show changes)'
    )
    parser.add_argument(
        '--notify', '-n',
        action='store_true',
        help='Enable desktop notifications'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    args = parser.parse_args()

    # Run watch mode
    watch = WatchMode(
        files=args.files,
        interval=args.interval,
        quiet=args.quiet,
        notify=args.notify,
        no_color=args.no_color
    )

    watch.run()


if __name__ == '__main__':
    main()
