"""SQLite database operations for note metadata."""
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path

from ..utils.config import SQLITE_DB_PATH, ensure_directories


class MetadataDB:
    """Manages note metadata in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database connection."""
        if db_path is None:
            ensure_directories()
            db_path = SQLITE_DB_PATH

        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Create the database and tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                path TEXT NOT NULL,
                tags TEXT,
                created_at REAL,
                modified_at REAL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_note(self, note: Dict) -> bool:
        """Insert or update a note in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO notes (id, title, path, tags, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                note['id'],
                note['title'],
                note['path'],
                note['tags'],
                note.get('created_at'),
                note.get('modified_at')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting note: {e}")
            return False

    def insert_notes(self, notes: List[Dict]) -> int:
        """Insert multiple notes. Returns count of successfully inserted notes."""
        count = 0
        for note in notes:
            if self.insert_note(note):
                count += 1
        return count

    def get_note_by_id(self, note_id: str) -> Optional[Dict]:
        """Retrieve a note by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_all_notes(self) -> List[Dict]:
        """Retrieve all notes from the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY modified_at DESC")
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def search_by_tags(self, tags: str) -> List[Dict]:
        """Search notes by tags (comma-separated)."""
        cursor = self.conn.cursor()
        # Simple LIKE search for tags
        cursor.execute(
            "SELECT * FROM notes WHERE tags LIKE ? ORDER BY modified_at DESC",
            (f"%{tags}%",)
        )
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Search notes by keyword in title or tags."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM notes
            WHERE title LIKE ? OR tags LIKE ?
            ORDER BY modified_at DESC
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all notes from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM notes")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
