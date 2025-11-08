#!/usr/bin/env python3
"""Backup script for Personal RAG Notes App.

This script backs up:
- SQLite metadata database
- ChromaDB vector store
- Notes directory (optional)
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime
import tarfile


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def create_backup(backup_dir: Path, include_notes: bool = False):
    """
    Create a backup of the knowledge base.

    Args:
        backup_dir: Directory to store backups
        include_notes: Whether to include the notes directory
    """
    project_root = get_project_root()
    data_dir = project_root / "data"

    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"knowledge_base_backup_{timestamp}.tar.gz"

    print(f"Creating backup: {backup_file}")

    # Create tar.gz archive
    with tarfile.open(backup_file, "w:gz") as tar:
        # Backup data directory (metadata DB and ChromaDB)
        if data_dir.exists():
            print("  ✓ Backing up metadata database...")
            print("  ✓ Backing up vector store...")
            tar.add(data_dir, arcname="data")
        else:
            print("  ⚠ Data directory not found. Skipping.")

        # Optionally backup notes
        if include_notes:
            notes_dir = project_root / "notes"
            if notes_dir.exists():
                print("  ✓ Backing up notes...")
                tar.add(notes_dir, arcname="notes")
            else:
                print("  ⚠ Notes directory not found. Skipping.")

    file_size = backup_file.stat().st_size / (1024 * 1024)  # Convert to MB
    print(f"\n✓ Backup completed successfully!")
    print(f"  Location: {backup_file}")
    print(f"  Size: {file_size:.2f} MB")

    return backup_file


def list_backups(backup_dir: Path):
    """List all available backups."""
    if not backup_dir.exists():
        print(f"No backups found. Backup directory does not exist: {backup_dir}")
        return

    backups = sorted(backup_dir.glob("knowledge_base_backup_*.tar.gz"), reverse=True)

    if not backups:
        print(f"No backups found in: {backup_dir}")
        return

    print(f"\nAvailable backups in {backup_dir}:\n")
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / (1024 * 1024)  # MB
        timestamp_str = backup.stem.replace("knowledge_base_backup_", "")
        # Parse timestamp
        try:
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_date = timestamp_str

        print(f"{i}. {backup.name}")
        print(f"   Created: {formatted_date}")
        print(f"   Size: {size:.2f} MB\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Backup utility for Personal RAG Notes App"
    )

    parser.add_argument(
        "action",
        choices=["create", "list"],
        help="Action to perform: create a new backup or list existing backups"
    )

    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=get_project_root() / "backups",
        help="Directory to store backups (default: ./backups)"
    )

    parser.add_argument(
        "--include-notes",
        action="store_true",
        help="Include notes directory in backup (not recommended if notes are large)"
    )

    args = parser.parse_args()

    try:
        if args.action == "create":
            create_backup(args.backup_dir, include_notes=args.include_notes)
        elif args.action == "list":
            list_backups(args.backup_dir)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
