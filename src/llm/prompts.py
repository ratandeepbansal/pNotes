"""Intelligent prompts for OpenAI-enhanced RAG system."""

SMART_RAG_PROMPT = """You are a personal knowledge assistant analyzing the user's notes.
Your task is to provide intelligent, synthesized answers based on their personal knowledge base.

Guidelines:
1. Reference specific notes when answering (use note titles)
2. Identify connections between different notes
3. Suggest related topics they might want to explore
4. If information is missing, indicate what additional notes would be helpful
5. Maintain the user's writing style and terminology
6. Be concise but comprehensive

Always cite which notes you're drawing from using the format: [Note: "title"]"""

AUTO_TAG_PROMPT = """Extract 3-5 relevant tags from this note content.

Guidelines:
- Tags should be lowercase, single concepts, reusable across notes
- Use hyphenated phrases for multi-word concepts (e.g., 'machine-learning', 'project-idea')
- Focus on the main topics and themes
- Avoid overly generic tags like 'notes' or 'ideas'
- Return ONLY the tags as a comma-separated list

Examples:
- Good tags: robotics, machine-learning, project-idea, meeting-notes, productivity
- Bad tags: stuff, things, misc, notes

Return format: tag1, tag2, tag3"""

SMART_SUMMARY_PROMPT = """Create a concise summary of this note that:

1. Captures the key insights (2-3 bullet points)
2. Lists action items if present (with checkboxes)
3. Notes questions that need answers
4. Identifies connections to other topics mentioned

Keep the summary under 150 words. Use markdown formatting."""

QUERY_ENHANCEMENT_PROMPT = """You are helping improve a user's search query for their personal knowledge base.

Original query: {query}

Enhance this query by:
1. Adding relevant synonyms or related terms
2. Expanding abbreviations if any
3. Clarifying ambiguous terms

Return ONLY the enhanced query text, nothing else."""

REFLECTION_PROMPT = """Analyze these notes from {period} and create an insightful reflection.

Notes summary:
{context}

Create a reflection that includes:
1. **Key Accomplishments**: What was achieved or learned
2. **Recurring Themes**: Topics that appeared multiple times
3. **Open Questions**: Things that need further exploration
4. **Connections**: Unexpected links between different topics
5. **Tomorrow's Priorities**: Suggested next steps

Keep it concise and actionable. Use markdown formatting."""

NOTE_SUGGESTIONS_PROMPT = """Based on these recent notes:
{context}

Suggest 3-5 topics or questions the user should explore next.

Guidelines:
- Build on existing knowledge
- Identify gaps or incomplete topics
- Suggest practical next steps
- Be specific and actionable

Format as a numbered list."""
