"""AI-powered summary generation for notes."""
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..db.metadata import MetadataDB
from ..utils.config import NOTES_DIR


class SummaryGenerator:
    """Generates intelligent summaries and reflections."""

    def __init__(self, metadata_db: Optional[MetadataDB] = None, smart_rag=None):
        """
        Initialize summary generator.

        Args:
            metadata_db: MetadataDB instance
            smart_rag: Optional SmartRAG instance for AI summaries
        """
        self.metadata_db = metadata_db or MetadataDB()
        self.smart_rag = smart_rag
        self.notes_dir = NOTES_DIR

    def generate_daily_reflection(self, date: Optional[datetime] = None, smart_rag=None) -> Dict:
        """
        Generate a daily reflection based on notes from a specific day.

        Args:
            date: Date to reflect on (defaults to today)
            smart_rag: Optional SmartRAG instance

        Returns:
            Dictionary with reflection and metadata
        """
        if date is None:
            date = datetime.now()

        # Use provided smart_rag or instance's smart_rag
        rag = smart_rag or self.smart_rag

        # Get start and end of day
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0).timestamp()
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59).timestamp()

        # Get notes from that day
        notes = self.metadata_db.search_by_date_range(
            start_timestamp=start_of_day,
            end_timestamp=end_of_day
        )

        if not notes:
            return {
                'reflection': f"No notes found for {date.strftime('%Y-%m-%d')}",
                'note_count': 0,
                'date': date.strftime('%Y-%m-%d'),
                'ai_powered': False
            }

        # Build context from notes
        notes_content = []
        for note in notes:
            notes_content.append({
                'title': note.get('title', 'Untitled'),
                'content': note.get('content', '')[:500],  # Limit content length
                'tags': note.get('tags', '')
            })

        context = "\n\n".join([
            f"**{n['title']}**\n{n['content']}\nTags: {n['tags']}"
            for n in notes_content
        ])

        # Generate AI reflection if SmartRAG available
        if rag:
            try:
                period = date.strftime('%Y-%m-%d')
                reflection = rag.generate_reflection(context, period=period)

                return {
                    'reflection': reflection,
                    'note_count': len(notes_content),
                    'date': period,
                    'ai_powered': True
                }
            except Exception as e:
                print(f"Error generating AI reflection: {e}")

        # Fallback: Simple summary
        tags = set()
        for note in notes_content:
            note_tags = note['tags']
            if note_tags:
                tag_list = note_tags.split(',') if isinstance(note_tags, str) else note_tags
                tags.update([tag.strip() for tag in tag_list if tag.strip()])

        fallback_reflection = f"""# Daily Summary - {date.strftime('%Y-%m-%d')}

**Notes Created:** {len(notes_content)}

**Topics Covered:** {', '.join(sorted(tags)) if tags else 'None'}

**Notes:**
"""
        for note in notes_content:
            fallback_reflection += f"\n- {note['title']}"

        return {
            'reflection': fallback_reflection,
            'note_count': len(notes_content),
            'date': date.strftime('%Y-%m-%d'),
            'ai_powered': False
        }

    def generate_weekly_summary(self, smart_rag=None) -> Dict:
        """
        Generate a weekly summary of notes.

        Args:
            smart_rag: Optional SmartRAG instance

        Returns:
            Dictionary with weekly summary
        """
        rag = smart_rag or self.smart_rag

        # Get last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        notes = self.metadata_db.search_by_date_range(
            start_timestamp=start_date.timestamp(),
            end_timestamp=end_date.timestamp()
        )

        if not notes:
            return {
                'summary': 'No notes found in the past week',
                'note_count': 0,
                'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'ai_powered': False
            }

        # Build context
        notes_content = []
        for note in notes[:20]:  # Limit to 20 notes
            notes_content.append({
                    'title': note.get('title', 'Untitled'),
                    'content': note.get('content', '')[:300],
                    'tags': note.get('tags', ''),
                    'date': datetime.fromtimestamp(note.get('modified_at', 0)).strftime('%Y-%m-%d')
                })

        context = "\n\n".join([
            f"[{n['date']}] **{n['title']}**\n{n['content']}"
            for n in notes_content
        ])

        # Generate AI summary if available
        if rag:
            try:
                summary = rag.generate_reflection(context, period='this week')

                return {
                    'summary': summary,
                    'note_count': len(note_ids),
                    'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    'ai_powered': True
                }
            except Exception as e:
                print(f"Error generating weekly summary: {e}")

        # Fallback summary
        tags = set()
        for note in notes_content:
            note_tags = note['tags']
            if note_tags:
                tag_list = note_tags.split(',') if isinstance(note_tags, str) else note_tags
                tags.update([tag.strip() for tag in tag_list if tag.strip()])

        fallback_summary = f"""# Weekly Summary
**Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
**Total Notes:** {len(note_ids)}
**Topics:** {', '.join(sorted(tags)) if tags else 'None'}

**Recent Notes:**
"""
        for note in notes_content[:10]:
            fallback_summary += f"\n- [{note['date']}] {note['title']}"

        return {
            'summary': fallback_summary,
            'note_count': len(note_ids),
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'ai_powered': False
        }

    def save_reflection_as_note(self, reflection_data: Dict) -> Path:
        """
        Save a generated reflection as a new note.

        Args:
            reflection_data: Reflection dictionary from generate_daily_reflection

        Returns:
            Path to saved note
        """
        import frontmatter

        title = f"Daily Reflection - {reflection_data['date']}"
        content = reflection_data['reflection']

        # Create frontmatter
        metadata = {
            'title': title,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'tags': ['reflection', 'auto-generated'],
            'note_count': reflection_data['note_count'],
            'ai_powered': reflection_data.get('ai_powered', False)
        }

        post = frontmatter.Post(content, **metadata)

        # Save file
        filename = f"reflection_{reflection_data['date']}.md"
        file_path = self.notes_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return file_path
