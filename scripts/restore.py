#!/usr/bin/env python3
"""Restore script for Personal RAG Notes App.

This script restores a backup created by backup.py.
"""

import argparse
import shutil
import sys
from pathlib import Path
import tarfile


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def restore_backup(backup_file: Path, force: bool = False):
    """
    Restore a backup of the knowledge base.

    Args:
        backup_file: Path to the backup file
        force: Skip confirmation prompt
    """
    project_root = get_project_root()

    # Verify backup file exists
    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)

    # Check if data directory exists and warn user
    data_dir = project_root / "data"
    if data_dir.exists() and not force:
        print("⚠ WARNING: This will overwrite existing data!")
        print(f"   Current data directory: {data_dir}")
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("Restore cancelled.")
            sys.exit(0)

    # Backup current data if it exists
    if data_dir.exists():
        backup_current = project_root / "data.backup.old"
        if backup_current.exists():
            shutil.rmtree(backup_current)
        print(f"  ✓ Creating safety backup of current data to: {backup_current}")
        shutil.copytree(data_dir, backup_current)

    print(f"\nRestoring from: {backup_file}")

    # Extract backup
    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            # Get members to restore
            members = tar.getmembers()

            # Extract data directory
            data_members = [m for m in members if m.name.startswith("data/")]
            if data_members:
                print("  ✓ Restoring metadata database...")
                print("  ✓ Restoring vector store...")

                # Remove existing data directory
                if data_dir.exists():
                    shutil.rmtree(data_dir)

                # Extract data
                tar.extractall(path=project_root, members=data_members)

            # Extract notes directory if present
            notes_members = [m for m in members if m.name.startswith("notes/")]
            if notes_members:
                print("  ✓ Restoring notes...")
                notes_dir = project_root / "notes"

                # Confirm before overwriting notes
                if notes_dir.exists() and not force:
                    response = input("\n  Notes directory exists. Overwrite? (yes/no): ").strip().lower()
                    if response not in ["yes", "y"]:
                        print("  Skipping notes restore.")
                    else:
                        shutil.rmtree(notes_dir)
                        tar.extractall(path=project_root, members=notes_members)
                else:
                    tar.extractall(path=project_root, members=notes_members)

        print(f"\n✓ Restore completed successfully!")
        print(f"\nNext steps:")
        print(f"  1. Restart the Streamlit app if it's running")
        print(f"  2. Verify your data in the app")

    except Exception as e:
        print(f"\nError during restore: {e}", file=sys.stderr)
        print("\nAttempting to restore from safety backup...")

        # Restore from safety backup
        backup_current = project_root / "data.backup.old"
        if backup_current.exists():
            if data_dir.exists():
                shutil.rmtree(data_dir)
            shutil.copytree(backup_current, data_dir)
            print("✓ Original data restored from safety backup.")

        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Restore utility for Personal RAG Notes App"
    )

    parser.add_argument(
        "backup_file",
        type=Path,
        help="Path to the backup file to restore"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts (use with caution)"
    )

    args = parser.parse_args()

    try:
        restore_backup(args.backup_file, force=args.force)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
