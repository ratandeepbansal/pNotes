"""Load and parse markdown files."""
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
import frontmatter

from .config import NOTES_DIR


def generate_file_id(file_path: str) -> str:
    """Generate a unique ID for a file based on its path."""
    return hashlib.md5(file_path.encode()).hexdigest()


def extract_metadata(file_path: Path) -> Dict:
    """
    Extract metadata from a markdown file.

    Supports YAML frontmatter for metadata like title and tags.
    If no frontmatter exists, uses the filename as title.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Extract metadata from frontmatter
        title = post.get('title', file_path.stem)
        tags = post.get('tags', '')

        # Handle tags - could be list or comma-separated string
        if isinstance(tags, list):
            tags = ', '.join(tags)
        elif not isinstance(tags, str):
            tags = str(tags)

        # Get the content without frontmatter
        content = post.content

        # Get file stats
        stats = file_path.stat()

        return {
            'id': generate_file_id(str(file_path)),
            'title': title,
            'path': str(file_path),
            'tags': tags,
            'content': content,
            'created_at': stats.st_ctime,
            'modified_at': stats.st_mtime
        }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def load_all_notes(notes_dir: Optional[Path] = None) -> List[Dict]:
    """
    Load all markdown files from the notes directory.

    Returns a list of dictionaries containing file metadata and content.
    """
    if notes_dir is None:
        notes_dir = NOTES_DIR

    notes = []

    # Recursively find all .md files
    for md_file in notes_dir.rglob('*.md'):
        metadata = extract_metadata(md_file)
        if metadata:
            notes.append(metadata)

    return notes


def get_note_by_id(note_id: str, notes_dir: Optional[Path] = None) -> Optional[Dict]:
    """Get a specific note by its ID."""
    notes = load_all_notes(notes_dir)
    for note in notes:
        if note['id'] == note_id:
            return note
    return None
