"""Smart note suggestion system."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..db.metadata import MetadataDB
from ..rag.retriever import Retriever


class NoteSuggester:
    """Suggests related notes and topics to explore."""

    def __init__(self, retriever: Optional[Retriever] = None, metadata_db: Optional[MetadataDB] = None):
        """
        Initialize note suggester.

        Args:
            retriever: Retriever instance for semantic search
            metadata_db: MetadataDB instance for metadata queries
        """
        self.retriever = retriever or Retriever()
        self.metadata_db = metadata_db or MetadataDB()

    def suggest_related_notes(
        self,
        note_id: str,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Dict]:
        """
        Suggest notes related to the current note.

        Args:
            note_id: ID of the current note
            top_k: Number of suggestions
            min_similarity: Minimum similarity threshold

        Returns:
            List of related note dictionaries
        """
        # Get the current note's content
        note_info = self.metadata_db.get_note_by_id(note_id)
        if not note_info:
            return []

        # Search for similar notes using content
        similar = self.retriever.search_semantic(
            query=note_info['content'][:500],  # Use first 500 chars as query
            top_k=top_k + 1  # +1 to exclude self
        )

        # Filter out the current note and low-similarity matches
        related = []
        for note in similar:
            note_result_id = note.get('id') or note.get('note_id')
            if note_result_id != note_id:
                score = note.get('score', 0) or note.get('relevance_score', 0)
                if score >= min_similarity:
                    related.append(note)

        return related[:top_k]

    def suggest_by_tags(self, note_id: str, top_k: int = 5) -> List[Dict]:
        """
        Suggest notes with similar tags.

        Args:
            note_id: ID of the current note
            top_k: Number of suggestions

        Returns:
            List of related notes by tags
        """
        note_info = self.metadata_db.get_note_by_id(note_id)
        if not note_info or not note_info.get('tags'):
            return []

        tags = note_info['tags'].split(',') if isinstance(note_info['tags'], str) else note_info.get('tags', [])
        tags = [tag.strip() for tag in tags if tag.strip()]

        if not tags:
            return []

        # Get notes with overlapping tags
        tag_matches = self.metadata_db.filter_notes(tags=tags)

        # Exclude current note
        tag_matches = [nid for nid in tag_matches if nid != note_id]

        # Get full note info
        suggestions = []
        for nid in tag_matches[:top_k]:
            note = self.metadata_db.get_note_by_id(nid)
            if note:
                suggestions.append(note)

        return suggestions

    def suggest_next_topics(
        self,
        days: int = 7,
        smart_rag=None
    ) -> Dict:
        """
        Suggest topics to explore next based on recent notes.

        Args:
            days: Number of days to look back
            smart_rag: Optional SmartRAG instance for AI suggestions

        Returns:
            Dictionary with suggestions and context
        """
        # Get recent notes
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        recent_notes = self.metadata_db.search_by_date_range(start_date=cutoff)

        if not recent_notes:
            return {
                'suggestions': [],
                'context': 'No recent notes found',
                'recent_count': 0
            }

        # Get note details
        notes_content = []
        for note_id in recent_notes[:10]:  # Limit to 10 most recent
            note = self.metadata_db.get_note_by_id(note_id)
            if note:
                notes_content.append({
                    'title': note.get('title', 'Untitled'),
                    'tags': note.get('tags', ''),
                    'content_preview': note.get('content', '')[:200]
                })

        # Build context string
        context = "\n\n".join([
            f"**{n['title']}**\nTags: {n['tags']}\n{n['content_preview']}"
            for n in notes_content
        ])

        # If SmartRAG available, use AI for suggestions
        if smart_rag:
            try:
                ai_suggestions = smart_rag.suggest_topics(context)
                return {
                    'suggestions': ai_suggestions,
                    'context': context,
                    'recent_count': len(notes_content),
                    'ai_powered': True
                }
            except Exception as e:
                print(f"Error getting AI suggestions: {e}")

        # Fallback: Extract common tags/themes
        all_tags = []
        for note in notes_content:
            tags = note['tags']
            if tags:
                tag_list = tags.split(',') if isinstance(tags, str) else tags
                all_tags.extend([tag.strip() for tag in tag_list])

        # Count tag frequency
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(5)

        suggestions = [
            f"Explore more about: {tag} (mentioned {count} times)"
            for tag, count in top_tags
        ]

        return {
            'suggestions': suggestions,
            'context': context,
            'recent_count': len(notes_content),
            'ai_powered': False
        }

    def find_orphan_notes(self) -> List[Dict]:
        """
        Find notes with no tags or links (orphans).

        Returns:
            List of orphan notes
        """
        all_notes = self.metadata_db.get_all_notes()
        orphans = []

        for note_id, note_data in all_notes:
            tags = note_data.get('tags', '')
            # Consider a note orphan if it has no tags
            if not tags or tags.strip() == '':
                orphans.append({
                    'id': note_id,
                    'title': note_data.get('title', 'Untitled'),
                    'path': note_data.get('path', '')
                })

        return orphans

    def get_trending_topics(self, days: int = 30, top_k: int = 10) -> List[Dict]:
        """
        Get trending topics based on recent note creation.

        Args:
            days: Number of days to analyze
            top_k: Number of top topics

        Returns:
            List of trending topics with counts
        """
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        recent_notes = self.metadata_db.search_by_date_range(start_date=cutoff)

        # Collect all tags
        tag_counts = {}
        for note_id in recent_notes:
            note = self.metadata_db.get_note_by_id(note_id)
            if note and note.get('tags'):
                tags = note['tags']
                tag_list = tags.split(',') if isinstance(tags, str) else tags
                for tag in tag_list:
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by count
        trending = [
            {'tag': tag, 'count': count}
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return trending[:top_k]
