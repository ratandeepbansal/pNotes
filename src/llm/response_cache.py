"""Response caching system for cost optimization."""
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ResponseCache:
    """Persistent cache for LLM responses to reduce API costs."""

    def __init__(self, cache_dir: Path = Path("data/cache"), ttl_hours: int = 24):
        """
        Initialize response cache.

        Args:
            cache_dir: Directory for cache database
            ttl_hours: Time-to-live for cached responses in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "response_cache.db"
        self.ttl_hours = ttl_hours

        self._init_db()

    def _init_db(self):
        """Initialize cache database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (
                cache_key TEXT PRIMARY KEY,
                response TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                hit_count INTEGER DEFAULT 0
            )
        """)

        # Index for efficient cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at
            ON response_cache(expires_at)
        """)

        conn.commit()
        conn.close()

    def _generate_key(self, prompt: str, model: str, **kwargs) -> str:
        """
        Generate cache key from prompt and parameters.

        Args:
            prompt: User prompt
            model: Model name
            **kwargs: Additional parameters (temperature, etc.)

        Returns:
            SHA256 hash as cache key
        """
        # Create deterministic string from all inputs
        key_data = {
            "prompt": prompt,
            "model": model,
            **kwargs,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """
        Retrieve cached response if available and not expired.

        Args:
            prompt: User prompt
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Cached response or None if not found/expired
        """
        cache_key = self._generate_key(prompt, model, **kwargs)
        now = datetime.now().timestamp()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT response, expires_at
            FROM response_cache
            WHERE cache_key = ? AND expires_at > ?
        """,
            (cache_key, now),
        )

        result = cursor.fetchone()

        if result:
            response, expires_at = result

            # Increment hit counter
            cursor.execute(
                """
                UPDATE response_cache
                SET hit_count = hit_count + 1
                WHERE cache_key = ?
            """,
                (cache_key,),
            )
            conn.commit()
            conn.close()

            return response

        conn.close()
        return None

    def set(
        self,
        prompt: str,
        model: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Store response in cache.

        Args:
            prompt: User prompt
            model: Model name
            response: LLM response to cache
            metadata: Optional metadata (tokens, cost, etc.)
            **kwargs: Additional parameters
        """
        cache_key = self._generate_key(prompt, model, **kwargs)
        now = datetime.now().timestamp()
        expires_at = (datetime.now() + timedelta(hours=self.ttl_hours)).timestamp()

        metadata_json = json.dumps(metadata) if metadata else None

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO response_cache
            (cache_key, response, metadata, created_at, expires_at, hit_count)
            VALUES (?, ?, ?, ?, ?, COALESCE(
                (SELECT hit_count FROM response_cache WHERE cache_key = ?),
                0
            ))
        """,
            (cache_key, response, metadata_json, now, expires_at, cache_key),
        )

        conn.commit()
        conn.close()

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now().timestamp()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("DELETE FROM response_cache WHERE expires_at <= ?", (now,))
        deleted = cursor.rowcount

        conn.commit()
        conn.close()

        return deleted

    def clear_all(self) -> int:
        """
        Clear entire cache.

        Returns:
            Number of entries removed
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("DELETE FROM response_cache")
        deleted = cursor.rowcount

        conn.commit()
        conn.close()

        return deleted

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Total entries
        cursor.execute("SELECT COUNT(*) FROM response_cache")
        total_entries = cursor.fetchone()[0]

        # Total hits
        cursor.execute("SELECT SUM(hit_count) FROM response_cache")
        total_hits = cursor.fetchone()[0] or 0

        # Expired entries
        now = datetime.now().timestamp()
        cursor.execute(
            "SELECT COUNT(*) FROM response_cache WHERE expires_at <= ?", (now,)
        )
        expired_entries = cursor.fetchone()[0]

        conn.close()

        return {
            "total_entries": total_entries,
            "valid_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "total_hits": total_hits,
            "hit_rate": (
                round(total_hits / (total_entries + total_hits) * 100, 2)
                if (total_entries + total_hits) > 0
                else 0.0
            ),
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup expired entries."""
        self.cleanup_expired()
