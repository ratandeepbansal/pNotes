"""LLM integration module for enhanced RAG with OpenAI."""

from .openai_client import SmartRAG
from .prompts import SMART_RAG_PROMPT, AUTO_TAG_PROMPT, SMART_SUMMARY_PROMPT
from .response_cache import ResponseCache

__all__ = ['SmartRAG', 'SMART_RAG_PROMPT', 'AUTO_TAG_PROMPT', 'SMART_SUMMARY_PROMPT', 'ResponseCache']
