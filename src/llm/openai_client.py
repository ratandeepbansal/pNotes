"""OpenAI integration for enhanced RAG capabilities."""
import os
from typing import List, Dict, Optional, Literal
from openai import OpenAI
from functools import lru_cache

from ..rag.retriever import Retriever
from .prompts import (
    SMART_RAG_PROMPT,
    AUTO_TAG_PROMPT,
    SMART_SUMMARY_PROMPT,
    QUERY_ENHANCEMENT_PROMPT,
    REFLECTION_PROMPT,
    NOTE_SUGGESTIONS_PROMPT
)


class SmartRAG:
    """Enhanced RAG system with OpenAI integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        retriever: Optional[Retriever] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize SmartRAG with OpenAI client.

        Args:
            api_key: OpenAI API key (reads from env if not provided)
            retriever: Retriever instance for semantic search
            model: OpenAI model to use
            temperature: Temperature for generation (0.0-2.0)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.retriever = retriever
        self.model = model
        self.temperature = temperature

        # Cost tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0

    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Make OpenAI API call with cost tracking.

        Args:
            messages: Chat messages
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens,
        )

        # Track usage
        usage = response.usage
        self.total_tokens_used += usage.total_tokens

        # Simple cost estimation (gpt-4o-mini pricing)
        input_cost = usage.prompt_tokens * 0.00015 / 1000
        output_cost = usage.completion_tokens * 0.0006 / 1000
        self.total_cost += input_cost + output_cost

        return response.choices[0].message.content

    def enhance_query(self, query: str) -> str:
        """
        Enhance a search query with synonyms and expansions.

        Args:
            query: Original search query

        Returns:
            Enhanced query string
        """
        messages = [
            {"role": "system", "content": "You are a query enhancement assistant."},
            {
                "role": "user",
                "content": QUERY_ENHANCEMENT_PROMPT.format(query=query),
            },
        ]

        return self._call_openai(messages, temperature=0.3, max_tokens=100).strip()

    def search_with_enhancement(
        self,
        query: str,
        top_k: int = 5,
        mode: Literal["local", "semantic", "hybrid"] = "hybrid",
    ) -> Dict:
        """
        Search with automatic query enhancement.

        Args:
            query: Search query
            top_k: Number of results
            mode: Search mode (local=keyword, semantic=embedding, hybrid=both)

        Returns:
            Dictionary with enhanced_query and results
        """
        if not self.retriever:
            raise ValueError("Retriever not initialized")

        # Enhance query
        enhanced_query = self.enhance_query(query)

        # Perform search based on mode
        if mode == "local":
            results = self.retriever.search_keyword(enhanced_query, top_k=top_k)
        elif mode == "semantic":
            results = self.retriever.search_semantic(enhanced_query, top_k=top_k)
        else:  # hybrid
            keyword_results = self.retriever.search_keyword(query, top_k=top_k)
            semantic_results = self.retriever.search_semantic(
                enhanced_query, top_k=top_k
            )

            # Combine and deduplicate
            seen = set()
            results = []
            for result in keyword_results + semantic_results:
                note_id = result.get("id") or result.get("note_id")
                if note_id and note_id not in seen:
                    seen.add(note_id)
                    results.append(result)

            results = results[:top_k]

        return {"enhanced_query": enhanced_query, "results": results}

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        mode: Literal["local", "semantic", "hybrid"] = "hybrid",
    ) -> Dict:
        """
        Answer a question using RAG with OpenAI.

        Args:
            question: User's question
            top_k: Number of context notes to retrieve
            mode: Search mode

        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Search for relevant notes
        search_results = self.search_with_enhancement(question, top_k, mode)
        results = search_results["results"]
        enhanced_query = search_results["enhanced_query"]

        if not results:
            return {
                "answer": "I couldn't find any relevant notes to answer this question.",
                "sources": [],
                "enhanced_query": enhanced_query,
            }

        # Build context from results
        context_parts = []
        sources = []

        for i, result in enumerate(results, 1):
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            score = result.get("score", 0)

            context_parts.append(f'[Note {i}: "{title}"]\n{content}\n')
            sources.append({"title": title, "score": score, "note_id": result.get("id")})

        context = "\n".join(context_parts)

        # Generate answer
        messages = [
            {"role": "system", "content": SMART_RAG_PROMPT},
            {
                "role": "user",
                "content": f"Context from notes:\n\n{context}\n\nQuestion: {question}",
            },
        ]

        answer = self._call_openai(messages, max_tokens=1000)

        return {
            "answer": answer,
            "sources": sources,
            "enhanced_query": enhanced_query,
            "context_used": len(results),
        }

    @lru_cache(maxsize=100)
    def auto_tag(self, content: str) -> List[str]:
        """
        Automatically generate tags for content.

        Args:
            content: Note content (first 500 chars used)

        Returns:
            List of suggested tags
        """
        # Limit content length for tagging
        content_sample = content[:500]

        messages = [
            {"role": "system", "content": "You are a note tagging assistant."},
            {"role": "user", "content": f"{AUTO_TAG_PROMPT}\n\nContent:\n{content_sample}"},
        ]

        response = self._call_openai(messages, temperature=0.3, max_tokens=50)

        # Parse comma-separated tags
        tags = [tag.strip() for tag in response.split(",")]
        return [tag for tag in tags if tag]

    def summarize_note(self, content: str, title: Optional[str] = None) -> str:
        """
        Create an intelligent summary of a note.

        Args:
            content: Note content
            title: Optional note title

        Returns:
            Markdown-formatted summary
        """
        title_prefix = f"Note: {title}\n\n" if title else ""

        messages = [
            {"role": "system", "content": "You are a note summarization assistant."},
            {
                "role": "user",
                "content": f"{SMART_SUMMARY_PROMPT}\n\n{title_prefix}Content:\n{content}",
            },
        ]

        return self._call_openai(messages, max_tokens=300)

    def generate_reflection(self, notes_context: str, period: str = "today") -> str:
        """
        Generate a reflection based on recent notes.

        Args:
            notes_context: Combined context from recent notes
            period: Time period (e.g., "today", "this week")

        Returns:
            Markdown-formatted reflection
        """
        messages = [
            {"role": "system", "content": "You are a personal reflection assistant."},
            {
                "role": "user",
                "content": REFLECTION_PROMPT.format(
                    period=period, context=notes_context
                ),
            },
        ]

        return self._call_openai(messages, max_tokens=800)

    def suggest_topics(self, notes_context: str) -> str:
        """
        Suggest topics to explore based on recent notes.

        Args:
            notes_context: Combined context from recent notes

        Returns:
            Formatted list of suggestions
        """
        messages = [
            {"role": "system", "content": "You are a knowledge exploration assistant."},
            {
                "role": "user",
                "content": NOTE_SUGGESTIONS_PROMPT.format(context=notes_context),
            },
        ]

        return self._call_openai(messages, max_tokens=400)

    def get_cost_stats(self) -> Dict:
        """
        Get usage and cost statistics.

        Returns:
            Dictionary with tokens used and estimated cost
        """
        return {
            "total_tokens": self.total_tokens_used,
            "estimated_cost_usd": round(self.total_cost, 4),
            "model": self.model,
        }

    def reset_cost_tracking(self):
        """Reset cost tracking counters."""
        self.total_tokens_used = 0
        self.total_cost = 0.0
