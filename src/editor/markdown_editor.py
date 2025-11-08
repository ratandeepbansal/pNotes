"""Markdown editor for creating and editing notes."""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import frontmatter

from ..utils.config import NOTES_DIR


class MarkdownEditor:
    """Handles note creation and editing with YAML frontmatter."""

    def __init__(self, notes_dir: Optional[Path] = None):
        """
        Initialize the markdown editor.

        Args:
            notes_dir: Directory to store notes (defaults to NOTES_DIR)
        """
        self.notes_dir = notes_dir or NOTES_DIR
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def generate_note_id(self, title: str) -> str:
        """
        Generate a unique note ID from title and timestamp.

        Args:
            title: Note title

        Returns:
            Unique note ID
        """
        timestamp = datetime.now().isoformat()
        combined = f"{title}_{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]

    def sanitize_filename(self, title: str) -> str:
        """
        Convert title to valid filename.

        Args:
            title: Note title

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        filename = title
        for char in invalid_chars:
            filename = filename.replace(char, '-')

        # Replace spaces with underscores
        filename = filename.replace(' ', '_')

        # Remove consecutive dashes/underscores
        while '--' in filename:
            filename = filename.replace('--', '-')
        while '__' in filename:
            filename = filename.replace('__', '_')

        # Trim and lowercase
        filename = filename.strip('-_').lower()

        # Limit length
        if len(filename) > 100:
            filename = filename[:100]

        return filename or 'untitled'

    def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        template: Optional[str] = None
    ) -> Dict:
        """
        Create a new note with YAML frontmatter.

        Args:
            title: Note title
            content: Note content (markdown)
            tags: List of tags
            template: Template name (if any)

        Returns:
            Dictionary with note information
        """
        tags = tags or []

        # Create frontmatter metadata
        metadata = {
            'title': title,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'tags': tags
        }

        if template:
            metadata['template'] = template

        # Create frontmatter post
        post = frontmatter.Post(content, **metadata)

        return {
            'metadata': metadata,
            'content': content,
            'frontmatter': frontmatter.dumps(post)
        }

    def save_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        filename: Optional[str] = None,
        template: Optional[str] = None
    ) -> Path:
        """
        Save note to file system.

        Args:
            title: Note title
            content: Note content
            tags: List of tags
            filename: Custom filename (optional, generated from title if not provided)
            template: Template used (optional)

        Returns:
            Path to saved note
        """
        # Generate filename if not provided
        if not filename:
            filename = self.sanitize_filename(title)

        # Ensure .md extension
        if not filename.endswith('.md'):
            filename = f"{filename}.md"

        # Create note with frontmatter
        note_data = self.create_note(title, content, tags, template)

        # Save to file
        file_path = self.notes_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(note_data['frontmatter'])

        return file_path

    def load_note(self, filename: str) -> Dict:
        """
        Load a note from file.

        Args:
            filename: Note filename

        Returns:
            Dictionary with note data
        """
        file_path = self.notes_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Note not found: {filename}")

        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        return {
            'title': post.get('title', filename.replace('.md', '')),
            'content': post.content,
            'tags': post.get('tags', []),
            'created': post.get('created'),
            'modified': post.get('modified'),
            'template': post.get('template'),
            'metadata': post.metadata
        }

    def update_note(
        self,
        filename: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Path:
        """
        Update an existing note.

        Args:
            filename: Existing note filename
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)

        Returns:
            Path to updated note
        """
        # Load existing note
        note = self.load_note(filename)

        # Update fields
        if title is not None:
            note['title'] = title
        if content is not None:
            note['content'] = content
        if tags is not None:
            note['tags'] = tags

        # Update modified time
        note['modified'] = datetime.now().isoformat()

        # Create updated frontmatter
        metadata = {
            'title': note['title'],
            'created': note['created'],
            'modified': note['modified'],
            'tags': note['tags']
        }

        if note.get('template'):
            metadata['template'] = note['template']

        post = frontmatter.Post(note['content'], **metadata)

        # Save
        file_path = self.notes_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return file_path

    def delete_note(self, filename: str) -> bool:
        """
        Delete a note.

        Args:
            filename: Note filename

        Returns:
            True if successful
        """
        file_path = self.notes_dir / filename

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def list_notes(self) -> List[Dict]:
        """
        List all notes in the notes directory.

        Returns:
            List of note summaries
        """
        notes = []

        for md_file in self.notes_dir.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                notes.append({
                    'filename': md_file.name,
                    'path': str(md_file.relative_to(self.notes_dir)),
                    'title': post.get('title', md_file.stem),
                    'tags': post.get('tags', []),
                    'created': post.get('created'),
                    'modified': post.get('modified'),
                    'preview': post.content[:200] if post.content else ''
                })
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
                continue

        # Sort by modified date (newest first)
        notes.sort(key=lambda x: x.get('modified', ''), reverse=True)

        return notes
