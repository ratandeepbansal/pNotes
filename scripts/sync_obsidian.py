#!/usr/bin/env python3
"""Obsidian vault sync script for Personal RAG Notes App.

This script syncs markdown files from an Obsidian vault to the notes directory.
It can work in two modes:
1. Copy mode: Copies files from Obsidian vault to notes/
2. Symlink mode: Creates symlinks to Obsidian vault (requires reindexing when vault changes)
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def sync_vault(vault_path: Path, mode: str = "copy", pattern: str = "**/*.md"):
    """
    Sync Obsidian vault to notes directory.

    Args:
        vault_path: Path to Obsidian vault
        mode: 'copy' or 'symlink'
        pattern: Glob pattern for files to sync (default: **/*.md)
    """
    project_root = get_project_root()
    notes_dir = project_root / "notes"

    # Verify vault exists
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    if not vault_path.is_dir():
        print(f"Error: Vault path is not a directory: {vault_path}")
        sys.exit(1)

    print(f"Syncing Obsidian vault: {vault_path}")
    print(f"Mode: {mode}")
    print(f"Pattern: {pattern}\n")

    # Create notes directory if it doesn't exist
    notes_dir.mkdir(parents=True, exist_ok=True)

    if mode == "symlink":
        # Symlink mode: create a symlink to the vault
        vault_link = notes_dir / "obsidian_vault"

        if vault_link.exists():
            if vault_link.is_symlink():
                vault_link.unlink()
                print(f"  ✓ Removed existing symlink")
            else:
                print(f"  ⚠ Warning: {vault_link} exists and is not a symlink")
                print(f"    Please remove it manually and try again.")
                sys.exit(1)

        vault_link.symlink_to(vault_path.resolve())
        print(f"  ✓ Created symlink: {vault_link} -> {vault_path}")
        print(f"\n✓ Sync completed!")
        print(f"\nNote: You'll need to reindex notes when your Obsidian vault changes.")
        print(f"      Run: python -m src.main index")

    elif mode == "copy":
        # Copy mode: copy matching files
        markdown_files = list(vault_path.glob(pattern))

        if not markdown_files:
            print(f"  ⚠ No files matching pattern '{pattern}' found in vault")
            sys.exit(0)

        print(f"Found {len(markdown_files)} file(s) to sync\n")

        copied_count = 0
        skipped_count = 0

        for md_file in markdown_files:
            # Get relative path from vault
            rel_path = md_file.relative_to(vault_path)

            # Skip Obsidian config files
            if str(rel_path).startswith('.obsidian'):
                skipped_count += 1
                continue

            # Create target path
            target_file = notes_dir / rel_path

            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file (preserving timestamps)
            shutil.copy2(md_file, target_file)
            copied_count += 1

            print(f"  ✓ Copied: {rel_path}")

        print(f"\n✓ Sync completed!")
        print(f"  Copied: {copied_count} file(s)")
        print(f"  Skipped: {skipped_count} file(s)")
        print(f"\nNext steps:")
        print(f"  1. Reindex notes: python -m src.main index")
        print(f"  2. Or use the 'Reindex' button in the Streamlit app")

    else:
        print(f"Error: Unknown mode '{mode}'. Use 'copy' or 'symlink'.")
        sys.exit(1)


def watch_vault(vault_path: Path):
    """
    Watch Obsidian vault for changes and auto-sync.

    Args:
        vault_path: Path to Obsidian vault
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Error: watchdog module not installed.")
        print("Install it with: pip install watchdog")
        sys.exit(1)

    class VaultChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.md') and not '.obsidian' in event.src_path:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Detected change: {event.src_path}")
                print("  Syncing...")
                sync_vault(vault_path, mode="copy")

        def on_created(self, event):
            if event.src_path.endswith('.md') and not '.obsidian' in event.src_path:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] New file: {event.src_path}")
                print("  Syncing...")
                sync_vault(vault_path, mode="copy")

    event_handler = VaultChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(vault_path), recursive=True)

    print(f"👀 Watching Obsidian vault: {vault_path}")
    print("Press Ctrl+C to stop\n")

    observer.start()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\nStopped watching vault.")

    observer.join()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sync Obsidian vault with Personal RAG Notes App"
    )

    parser.add_argument(
        "vault_path",
        type=Path,
        help="Path to your Obsidian vault"
    )

    parser.add_argument(
        "--mode",
        choices=["copy", "symlink"],
        default="copy",
        help="Sync mode: 'copy' (default) or 'symlink'"
    )

    parser.add_argument(
        "--pattern",
        default="**/*.md",
        help="Glob pattern for files to sync (default: **/*.md)"
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch vault for changes and auto-sync (requires watchdog)"
    )

    args = parser.parse_args()

    try:
        if args.watch:
            # Initial sync
            sync_vault(args.vault_path, mode=args.mode, pattern=args.pattern)
            # Start watching
            watch_vault(args.vault_path)
        else:
            sync_vault(args.vault_path, mode=args.mode, pattern=args.pattern)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
