"""Question-answering functionality using retrieved notes."""
from typing import List, Dict, Optional

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
