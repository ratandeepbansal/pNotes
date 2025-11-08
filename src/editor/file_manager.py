"""File management operations for notes."""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import shutil

from ..utils.config import NOTES_DIR


class NoteManager:
    """Manages note file operations and organization."""

    def __init__(self, notes_dir: Optional[Path] = None):
        """
        Initialize the note manager.

        Args:
            notes_dir: Directory containing notes
        """
        self.notes_dir = notes_dir or NOTES_DIR
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def list_notes(self, sort_by: str = 'modified', search_term: Optional[str] = None) -> List[Dict]:
        """
        List all notes with metadata.

        Args:
            sort_by: Sort field ('modified', 'created', 'title', 'size')
            search_term: Optional search term for filtering

        Returns:
            List of note information dictionaries
        """
        notes = []

        for md_file in self.notes_dir.rglob('*.md'):
            try:
                stat = md_file.stat()

                note_info = {
                    'filename': md_file.name,
                    'path': str(md_file.relative_to(self.notes_dir)),
                    'full_path': str(md_file),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                }

                # Filter by search term if provided
                if search_term:
                    search_lower = search_term.lower()
                    if search_lower not in md_file.name.lower():
                        # Also search in file content
                        try:
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                if search_lower not in content:
                                    continue
                        except:
                            continue

                notes.append(note_info)

            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                continue

        # Sort notes
        if sort_by == 'modified':
            notes.sort(key=lambda x: x['modified'], reverse=True)
        elif sort_by == 'created':
            notes.sort(key=lambda x: x['created'], reverse=True)
        elif sort_by == 'title':
            notes.sort(key=lambda x: x['filename'].lower())
        elif sort_by == 'size':
            notes.sort(key=lambda x: x['size'], reverse=True)

        return notes

    def search_by_title(self, query: str) -> List[Dict]:
        """
        Quick search notes by title.

        Args:
            query: Search query

        Returns:
            List of matching notes
        """
        return self.list_notes(search_term=query)

    def move_note(self, filename: str, new_path: str) -> Path:
        """
        Move a note to a different location.

        Args:
            filename: Current filename
            new_path: New path (relative to notes_dir)

        Returns:
            New file path
        """
        old_path = self.notes_dir / filename
        new_full_path = self.notes_dir / new_path

        # Create parent directories
        new_full_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        shutil.move(str(old_path), str(new_full_path))

        return new_full_path

    def copy_note(self, filename: str, new_filename: str) -> Path:
        """
        Create a copy of a note.

        Args:
            filename: Source filename
            new_filename: Destination filename

        Returns:
            Path to copied note
        """
        src = self.notes_dir / filename
        dst = self.notes_dir / new_filename

        shutil.copy2(str(src), str(dst))

        return dst

    def rename_note(self, old_filename: str, new_filename: str) -> Path:
        """
        Rename a note.

        Args:
            old_filename: Current filename
            new_filename: New filename

        Returns:
            New file path
        """
        old_path = self.notes_dir / old_filename
        new_path = self.notes_dir / new_filename

        old_path.rename(new_path)

        return new_path

    def bulk_operations(self, note_ids: List[str], operation: str, **kwargs) -> Dict:
        """
        Perform bulk operations on multiple notes.

        Args:
            note_ids: List of note filenames
            operation: Operation to perform ('archive', 'delete', 'tag', 'move')
            **kwargs: Additional arguments for the operation

        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': []
        }

        for filename in note_ids:
            try:
                if operation == 'delete':
                    file_path = self.notes_dir / filename
                    file_path.unlink()
                    results['success'].append(filename)

                elif operation == 'archive':
                    archive_dir = self.notes_dir / 'archive'
                    archive_dir.mkdir(exist_ok=True)
                    self.move_note(filename, f"archive/{filename}")
                    results['success'].append(filename)

                elif operation == 'move':
                    target_dir = kwargs.get('target_dir', '')
                    self.move_note(filename, f"{target_dir}/{filename}")
                    results['success'].append(filename)

            except Exception as e:
                results['failed'].append({
                    'filename': filename,
                    'error': str(e)
                })

        return results

    def get_note_stats(self) -> Dict:
        """
        Get statistics about the note collection.

        Returns:
            Dictionary with statistics
        """
        notes = self.list_notes()

        total_size = sum(note['size'] for note in notes)
        total_notes = len(notes)

        # Calculate age statistics
        if notes:
            oldest = min(note['created'] for note in notes)
            newest = max(note['created'] for note in notes)
        else:
            oldest = newest = None

        return {
            'total_notes': total_notes,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_note': oldest,
            'newest_note': newest,
            'avg_size_bytes': total_size / total_notes if total_notes > 0 else 0
        }

    def find_orphan_notes(self) -> List[str]:
        """
        Find notes that haven't been modified in a long time.

        Returns:
            List of potentially orphaned note filenames
        """
        from datetime import timedelta

        threshold = datetime.now() - timedelta(days=90)
        orphans = []

        for note in self.list_notes():
            if note['modified'] < threshold:
                orphans.append(note['filename'])

        return orphans

    def export_notes(self, output_dir: Path, format: str = 'md') -> Path:
        """
        Export all notes to a directory.

        Args:
            output_dir: Output directory
            format: Export format ('md', 'txt', 'html')

        Returns:
            Path to export directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for note in self.list_notes():
            src = Path(note['full_path'])

            if format == 'md':
                # Direct copy for markdown
                dst = output_dir / note['filename']
                shutil.copy2(src, dst)

            elif format == 'txt':
                # Convert to plain text (strip frontmatter)
                import frontmatter
                with open(src, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                dst = output_dir / note['filename'].replace('.md', '.txt')
                with open(dst, 'w', encoding='utf-8') as f:
                    f.write(post.content)

        return output_dir
