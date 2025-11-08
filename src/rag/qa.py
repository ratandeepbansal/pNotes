"""Question-answering functionality using retrieved notes."""
from typing import List, Dict, Optional
import time
from datetime import datetime, timedelta

from .retriever import Retriever
from ..utils.config import TOP_K_RESULTS


class QASystem:
    """Handles question-answering based on retrieved notes."""

    def __init__(self):
        """Initialize the QA system."""
        self.retriever = Retriever()

    def answer_question(self, question: str, top_k: int = TOP_K_RESULTS) -> Dict:
        """
        Answer a question using retrieved notes.

        For Phase 1, this provides a simple retrieval-based answer by returning
        the most relevant notes. In Phase 3, this can be enhanced with local LLM
        for actual answer generation.

        Args:
            question: The question to answer
            top_k: Number of relevant notes to retrieve

        Returns:
            Dictionary containing the answer and source notes
        """
        # Retrieve relevant notes
        results = self.retriever.search_semantic(question, top_k=top_k)

        if not results:
            return {
                'answer': "I couldn't find any relevant notes for your question.",
                'sources': [],
                'confidence': 0.0
            }

        # For Phase 1: Simple extraction-based answer
        # We'll return the most relevant note's content as the answer
        top_result = results[0]

        # Generate a simple summary from top results
        answer = self._generate_simple_answer(question, results)

        return {
            'answer': answer,
            'sources': results,
            'confidence': top_result.get('relevance_score', 0.0)
        }

    def _generate_simple_answer(self, question: str, results: List[Dict]) -> str:
        """
        Generate a simple answer from retrieved results.

        This is a basic implementation for Phase 1. Can be enhanced with
        local LLM in later phases.

        Args:
            question: The original question
            results: Retrieved note results

        Returns:
            A formatted answer string
        """
        if not results:
            return "No relevant information found."

        # For Phase 1, we provide a simple formatted response
        answer_parts = []

        answer_parts.append(f"Based on your notes, here's what I found:\n")

        # Include top 3 most relevant notes
        for i, result in enumerate(results[:3], 1):
            title = result.get('title', 'Untitled')
            content = result.get('content', '')
            score = result.get('relevance_score', 0.0)

            # Truncate content if too long
            if len(content) > 300:
                content = content[:300] + "..."

            answer_parts.append(f"\n{i}. **{title}** (relevance: {score:.2f})")
            answer_parts.append(f"   {content}\n")

        return "\n".join(answer_parts)

    def summarize_topic(self, topic: str, top_k: int = TOP_K_RESULTS) -> Dict:
        """
        Summarize what your notes say about a topic.

        Args:
            topic: The topic to summarize
            top_k: Number of relevant notes to include

        Returns:
            Dictionary containing the summary and source notes
        """
        # Retrieve relevant notes
        results = self.retriever.search_semantic(topic, top_k=top_k)

        if not results:
            return {
                'summary': f"No notes found about '{topic}'.",
                'sources': [],
                'note_count': 0
            }

        # Generate summary
        summary_parts = [f"Summary of notes about '{topic}':\n"]

        # Group by tags if available
        tagged_notes = {}
        for result in results:
            tags = result.get('tags', 'untagged')
            if tags not in tagged_notes:
                tagged_notes[tags] = []
            tagged_notes[tags].append(result)

        # Format summary
        for tags, notes in tagged_notes.items():
            summary_parts.append(f"\n**Tagged with: {tags}**")
            for note in notes:
                title = note.get('title', 'Untitled')
                score = note.get('relevance_score', 0.0)
                summary_parts.append(f"  - {title} (relevance: {score:.2f})")

        return {
            'summary': "\n".join(summary_parts),
            'sources': results,
            'note_count': len(results)
        }

    def get_related_notes(self, note_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find notes related to a given note.

        Args:
            note_id: ID of the source note
            top_k: Number of related notes to return

        Returns:
            List of related notes
        """
        # Get the content of the source note
        content = self.retriever.get_note_content(note_id)

        if not content:
            return []

        # Use the content as a query to find similar notes
        results = self.retriever.search_semantic(content, top_k=top_k + 1)

        # Filter out the source note itself
        related = [r for r in results if r['id'] != note_id]

        return related[:top_k]

    def auto_summarize_related_notes(self, query: str, top_k: int = 5) -> Dict:
        """
        Automatically find and summarize related notes on a topic.

        This analyzes the retrieved notes and generates a comprehensive summary
        showing connections between notes.

        Args:
            query: The topic or query to search for
            top_k: Number of notes to consider

        Returns:
            Dictionary with summary, connections, and themes
        """
        # Retrieve relevant notes
        results = self.retriever.search_semantic(query, top_k=top_k)

        if not results:
            return {
                'summary': f"No notes found related to '{query}'.",
                'connections': [],
                'themes': [],
                'note_count': 0
            }

        # Extract themes from tags
        themes = {}
        for result in results:
            tags = result.get('tags', '')
            if tags:
                tag_list = [t.strip() for t in tags.split(',')]
                for tag in tag_list:
                    if tag:
                        if tag not in themes:
                            themes[tag] = []
                        themes[tag].append(result['title'])

        # Find connections (notes with similar tags or high relevance)
        connections = []
        for i, note1 in enumerate(results):
            for note2 in results[i+1:]:
                # Check for shared tags
                tags1 = set([t.strip() for t in note1.get('tags', '').split(',') if t.strip()])
                tags2 = set([t.strip() for t in note2.get('tags', '').split(',') if t.strip()])
                shared_tags = tags1.intersection(tags2)

                if shared_tags:
                    connections.append({
                        'note1': note1['title'],
                        'note2': note2['title'],
                        'shared_tags': list(shared_tags),
                        'strength': len(shared_tags)
                    })

        # Generate comprehensive summary
        summary_parts = [f"## Analysis of '{query}'\n"]
        summary_parts.append(f"Found {len(results)} relevant note(s).\n")

        # Themes section
        if themes:
            summary_parts.append("\n### Key Themes:")
            for theme, notes in sorted(themes.items(), key=lambda x: len(x[1]), reverse=True):
                summary_parts.append(f"\n**{theme}** ({len(notes)} note{'s' if len(notes) != 1 else ''}):")
                for note_title in notes[:3]:  # Show top 3
                    summary_parts.append(f"  - {note_title}")

        # Top notes section
        summary_parts.append("\n### Most Relevant Notes:")
        for i, result in enumerate(results[:3], 1):
            title = result.get('title', 'Untitled')
            score = result.get('relevance_score', 0.0)
            summary_parts.append(f"\n{i}. **{title}** (relevance: {score:.2f})")

            # Add snippet
            content = result.get('content', '')
            if len(content) > 150:
                snippet = content[:150] + "..."
            else:
                snippet = content
            summary_parts.append(f"   {snippet}")

        # Connections section
        if connections:
            summary_parts.append(f"\n### Connections Found:")
            summary_parts.append(f"Discovered {len(connections)} connection(s) between notes:")
            for conn in connections[:5]:  # Show top 5
                summary_parts.append(
                    f"  - **{conn['note1']}** ↔ **{conn['note2']}** "
                    f"(shared: {', '.join(conn['shared_tags'])})"
                )

        return {
            'summary': '\n'.join(summary_parts),
            'connections': connections,
            'themes': themes,
            'note_count': len(results),
            'sources': results
        }

    def generate_daily_reflection(self, days: int = 1) -> Dict:
        """
        Generate a daily reflection summary of recent notes.

        Args:
            days: Number of days to look back (default: 1 for today)

        Returns:
            Dictionary with reflection summary and insights
        """
        # Calculate time range
        now = time.time()
        start_time = now - (days * 24 * 60 * 60)

        # Get notes from the time period
        recent_notes = self.retriever.metadata_db.search_by_date_range(
            start_timestamp=start_time,
            end_timestamp=now
        )

        if not recent_notes:
            period = "today" if days == 1 else f"the last {days} days"
            return {
                'summary': f"No notes were created or modified {period}.",
                'note_count': 0,
                'themes': {},
                'insights': []
            }

        # Analyze themes
        themes = {}
        for note in recent_notes:
            tags = note.get('tags', '')
            if tags:
                tag_list = [t.strip() for t in tags.split(',')]
                for tag in tag_list:
                    if tag:
                        if tag not in themes:
                            themes[tag] = 0
                        themes[tag] += 1

        # Generate insights
        insights = []

        # Insight: Most active theme
        if themes:
            top_theme = max(themes.items(), key=lambda x: x[1])
            insights.append(
                f"Your most active theme was **{top_theme[0]}** with {top_theme[1]} note(s)"
            )

        # Insight: Note count comparison
        period_str = "today" if days == 1 else f"the last {days} days"
        insights.append(
            f"You created or modified **{len(recent_notes)}** note(s) {period_str}"
        )

        # Insight: Diverse topics
        if len(themes) > 3:
            insights.append(
                f"You explored **{len(themes)}** different topics, showing diverse thinking"
            )

        # Build summary
        summary_parts = []

        if days == 1:
            summary_parts.append("# Daily Reflection\n")
        else:
            summary_parts.append(f"# Reflection for the Last {days} Days\n")

        summary_parts.append(f"**Period:** {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M')}\n")

        # Key insights
        summary_parts.append("## Key Insights")
        for insight in insights:
            summary_parts.append(f"- {insight}")

        # Themes breakdown
        if themes:
            summary_parts.append("\n## Themes Explored")
            for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- **{theme}**: {count} note(s)")

        # Recent notes
        summary_parts.append("\n## Recent Notes")
        for note in sorted(recent_notes, key=lambda x: x.get('modified_at', 0), reverse=True)[:10]:
            title = note.get('title', 'Untitled')
            mod_time = datetime.fromtimestamp(note.get('modified_at', 0))
            summary_parts.append(f"- **{title}** ({mod_time.strftime('%Y-%m-%d %H:%M')})")

        return {
            'summary': '\n'.join(summary_parts),
            'note_count': len(recent_notes),
            'themes': themes,
            'insights': insights,
            'notes': recent_notes
        }

    def generate_weekly_reflection(self) -> Dict:
        """Generate a weekly reflection (last 7 days)."""
        return self.generate_daily_reflection(days=7)

    def index_notes(self) -> int:
        """
        Index all notes in the notes directory.

        Returns:
            Number of notes indexed
        """
        return self.retriever.index_all_notes()

    def get_stats(self) -> Dict:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary containing statistics
        """
        return self.retriever.get_stats()

    def close(self):
        """Close database connections."""
        self.retriever.close()
