"""Streamlit UI for the Personal RAG Notes App with Phase 3 Intelligence Features."""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.qa import QASystem
from src.utils.config import TOP_K_RESULTS
from src.editor.markdown_editor import MarkdownEditor
from src.editor.file_manager import NoteManager
from src.editor.templates import TemplateManager
from src.llm.openai_client import SmartRAG


# Page configuration
st.set_page_config(
    page_title="Personal RAG Notes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = QASystem()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'qa_result' not in st.session_state:
        st.session_state.qa_result = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'all_tags' not in st.session_state:
        st.session_state.all_tags = []
    if 'editor' not in st.session_state:
        st.session_state.editor = MarkdownEditor()
    if 'note_manager' not in st.session_state:
        st.session_state.note_manager = NoteManager()
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = TemplateManager()
    if 'current_note' not in st.session_state:
        st.session_state.current_note = None

    # Initialize SmartRAG if API key is available
    if 'smart_rag' not in st.session_state:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                st.session_state.smart_rag = SmartRAG(
                    api_key=api_key,
                    retriever=st.session_state.qa_system.retriever
                )
                st.session_state.openai_available = True
            except Exception as e:
                st.session_state.smart_rag = None
                st.session_state.openai_available = False
        else:
            st.session_state.smart_rag = None
            st.session_state.openai_available = False

    # OpenAI feature toggles
    if 'use_openai_qa' not in st.session_state:
        st.session_state.use_openai_qa = False
    if 'use_auto_tagging' not in st.session_state:
        st.session_state.use_auto_tagging = False


def get_stats():
    """Get and cache statistics."""
    try:
        stats = st.session_state.qa_system.get_stats()
        st.session_state.stats = stats
        return stats
    except Exception as e:
        st.error(f"Error getting statistics: {e}")
        return {'total_notes': 0, 'notes_in_db': 0}


def get_all_tags():
    """Get all available tags."""
    try:
        tags = st.session_state.qa_system.retriever.get_all_tags()
        st.session_state.all_tags = tags
        return tags
    except Exception as e:
        st.error(f"Error getting tags: {e}")
        return []


def format_date_for_display(timestamp):
    """Format Unix timestamp for display."""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
    return "N/A"


def main():
    """Main Streamlit app."""
    initialize_session_state()

    # Header
    st.title("🧠 Personal RAG Notes")
    st.markdown("Your AI-powered personal knowledge base with intelligent search")

    # Sidebar
    with st.sidebar:
        st.header("📚 Knowledge Base")

        # Get stats
        stats = get_stats()

        # Display stats
        st.metric("Total Notes Indexed", stats.get('total_notes', 0))
        st.metric("Notes in Database", stats.get('notes_in_db', 0))

        st.divider()

        # Reindex button
        st.subheader("🔄 Index Management")
        if st.button("Reindex All Notes", type="primary", use_container_width=True):
            with st.spinner("Indexing notes... This may take a moment."):
                try:
                    count = st.session_state.qa_system.index_notes()
                    st.success(f"✓ Successfully indexed {count} notes!")
                    # Refresh stats and tags
                    get_stats()
                    get_all_tags()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error indexing notes: {e}")

        st.info("Click 'Reindex' to update the knowledge base with new or modified notes.")

        st.divider()

        # OpenAI API Key Configuration
        st.subheader("🤖 OpenAI Configuration")

        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('user_api_key', ''),
            placeholder="sk-...",
            help="Enter your OpenAI API key to enable AI features"
        )

        if api_key_input and api_key_input != st.session_state.get('user_api_key', ''):
            st.session_state.user_api_key = api_key_input
            # Reinitialize SmartRAG with new key
            try:
                st.session_state.smart_rag = SmartRAG(
                    api_key=api_key_input,
                    retriever=st.session_state.qa_system.retriever
                )
                st.session_state.openai_available = True
                st.success("✓ API Key Updated!")
            except Exception as e:
                st.session_state.smart_rag = None
                st.session_state.openai_available = False
                st.error(f"Error: {e}")

        # OpenAI Settings
        if st.session_state.openai_available:
            st.success("✓ OpenAI Connected")

            st.session_state.use_openai_qa = st.checkbox(
                "Use OpenAI for Q&A",
                value=st.session_state.use_openai_qa,
                help="Enable AI-powered question answering"
            )

            st.session_state.use_auto_tagging = st.checkbox(
                "Auto-generate tags",
                value=st.session_state.use_auto_tagging,
                help="Automatically suggest tags when creating notes"
            )

            # Cost tracking
            if st.session_state.smart_rag:
                cost_stats = st.session_state.smart_rag.get_cost_stats()
                st.caption(f"**API Usage:** {cost_stats['total_tokens']} tokens (${cost_stats['estimated_cost_usd']:.4f})")
        else:
            st.info("💡 Enter your OpenAI API key above to enable AI features")

        st.divider()

        # Settings
        st.subheader("⚙️ Settings")
        top_k = st.slider(
            "Number of results",
            min_value=1,
            max_value=10,
            value=TOP_K_RESULTS,
            help="How many notes to retrieve for each query"
        )

        st.divider()

        # Filters (Phase 3)
        st.subheader("🔍 Filters")

        # Tag filter
        all_tags = get_all_tags()
        if all_tags:
            selected_tags = st.multiselect(
                "Filter by tags",
                options=all_tags,
                help="Select one or more tags to filter results"
            )
        else:
            selected_tags = []
            st.info("No tags available. Add tags to your notes to use this filter.")

        # Date filter
        use_date_filter = st.checkbox("Filter by date range")

        if use_date_filter:
            date_preset = st.selectbox(
                "Date preset",
                ["Custom", "Today", "Last 7 days", "Last 30 days", "Last 90 days"]
            )

            if date_preset == "Custom":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start date", value=datetime.now() - timedelta(days=30))
                with col2:
                    end_date = st.date_input("End date", value=datetime.now())

                start_timestamp = time.mktime(start_date.timetuple())
                end_timestamp = time.mktime(end_date.timetuple()) + 86399  # End of day
            else:
                end_timestamp = time.time()
                if date_preset == "Today":
                    start_timestamp = time.time() - 86400
                elif date_preset == "Last 7 days":
                    start_timestamp = time.time() - (7 * 86400)
                elif date_preset == "Last 30 days":
                    start_timestamp = time.time() - (30 * 86400)
                else:  # Last 90 days
                    start_timestamp = time.time() - (90 * 86400)
        else:
            start_timestamp = None
            end_timestamp = None

    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Search",
        "💬 Ask Question",
        "📝 Summarize Topic",
        "🔗 Smart Analysis",
        "📊 Reflections",
        "✏️ Editor"
    ])

    # Tab 1: Semantic Search (Enhanced with filters)
    with tab1:
        st.header("Semantic Search")
        st.markdown("Search your notes using natural language with intelligent filtering")

        search_query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., 'machine learning algorithms' or 'personal growth ideas'",
            key="search_input"
        )

        # Display active filters
        if selected_tags or use_date_filter:
            st.caption("**Active filters:**")
            filter_info = []
            if selected_tags:
                filter_info.append(f"Tags: {', '.join(selected_tags)}")
            if use_date_filter:
                filter_info.append(f"Date: {format_date_for_display(start_timestamp)} to {format_date_for_display(end_timestamp)}")
            st.caption(" | ".join(filter_info))

        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.button("Search", type="primary", use_container_width=True)
        with col2:
            if search_button or search_query:
                if st.button("Clear Results", use_container_width=True):
                    st.session_state.search_results = None
                    st.rerun()

        if search_button and search_query:
            with st.spinner("Searching..."):
                try:
                    results = st.session_state.qa_system.retriever.search_semantic(
                        search_query,
                        top_k=top_k,
                        filter_tags=selected_tags if selected_tags else None,
                        start_date=start_timestamp if use_date_filter else None,
                        end_date=end_timestamp if use_date_filter else None
                    )
                    st.session_state.search_results = results
                except Exception as e:
                    st.error(f"Error during search: {e}")

        # Display search results
        if st.session_state.search_results is not None:
            results = st.session_state.search_results

            if not results:
                st.info("No results found. Try adjusting your query or filters.")
            else:
                st.success(f"Found {len(results)} relevant note(s)")

                for i, result in enumerate(results, 1):
                    with st.expander(
                        f"📄 {result.get('title', 'Untitled')} — Relevance: {result.get('relevance_score', 0):.3f}",
                        expanded=(i == 1)
                    ):
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**Path:** `{result.get('path', 'N/A')}`")
                        with col2:
                            tags = result.get('tags', '')
                            if tags:
                                st.markdown(f"**Tags:** {tags}")
                        with col3:
                            mod_time = result.get('modified_at')
                            if mod_time:
                                st.markdown(f"**Modified:** {format_date_for_display(mod_time)}")

                        st.divider()

                        # Content preview
                        content = result.get('content', 'No content available')
                        if len(content) > 500:
                            st.markdown(content[:500] + "...")
                            with st.expander("Show full content"):
                                st.markdown(content)
                        else:
                            st.markdown(content)

    # Tab 2: Question Answering
    with tab2:
        st.header("Ask a Question")
        st.markdown("Get answers based on your notes")

        question = st.text_area(
            "What would you like to know?",
            placeholder="e.g., 'What are my thoughts on deep learning?' or 'What have I learned about productivity?'",
            height=100,
            key="question_input"
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            ask_button = st.button("Ask", type="primary", use_container_width=True)
        with col2:
            if ask_button or (st.session_state.qa_result is not None):
                if st.button("Clear Answer", use_container_width=True):
                    st.session_state.qa_result = None
                    st.rerun()

        if ask_button and question:
            with st.spinner("Thinking..."):
                try:
                    # Use OpenAI if enabled and available
                    if st.session_state.use_openai_qa and st.session_state.smart_rag:
                        result = st.session_state.smart_rag.answer_question(
                            question,
                            top_k=top_k,
                            mode="hybrid"
                        )
                    else:
                        result = st.session_state.qa_system.answer_question(
                            question,
                            top_k=top_k
                        )
                    st.session_state.qa_result = result
                except Exception as e:
                    st.error(f"Error answering question: {e}")

        # Display answer
        if st.session_state.qa_result:
            result = st.session_state.qa_result

            # Answer section
            st.subheader("Answer")
            st.markdown(result['answer'])

            # Display metadata based on source
            col1, col2 = st.columns(2)
            with col1:
                # Confidence (traditional QA)
                if 'confidence' in result:
                    confidence = result.get('confidence', 0.0)
                    st.metric("Confidence", f"{confidence:.1%}")

            with col2:
                # Context used (OpenAI)
                if 'context_used' in result:
                    st.metric("Notes Retrieved", result['context_used'])
                # Enhanced query (OpenAI)
                if 'enhanced_query' in result:
                    st.caption(f"**Enhanced query:** {result['enhanced_query']}")

            # Sources
            sources = result.get('sources', [])
            if sources:
                st.divider()
                st.subheader(f"📚 Sources ({len(sources)} note(s))")

                for i, source in enumerate(sources, 1):
                    # Handle both old and new source formats
                    relevance = source.get('relevance_score') or source.get('score', 0)
                    with st.expander(
                        f"{i}. {source.get('title', 'Untitled')} — Relevance: {relevance:.3f}"
                    ):
                        if 'path' in source:
                            st.markdown(f"**Path:** `{source.get('path', 'N/A')}`")
                        tags = source.get('tags', '')
                        if tags:
                            st.markdown(f"**Tags:** {tags}")

    # Tab 3: Topic Summary
    with tab3:
        st.header("Summarize a Topic")
        st.markdown("Get an overview of what your notes say about a topic")

        topic = st.text_input(
            "Enter a topic:",
            placeholder="e.g., 'artificial intelligence' or 'life goals'",
            key="topic_input"
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            summarize_button = st.button("Summarize", type="primary", use_container_width=True)
        with col2:
            if summarize_button:
                if st.button("Clear Summary", use_container_width=True):
                    st.rerun()

        if summarize_button and topic:
            with st.spinner("Generating summary..."):
                try:
                    result = st.session_state.qa_system.summarize_topic(
                        topic,
                        top_k=top_k
                    )

                    # Display summary
                    st.subheader(f"Summary: {topic}")
                    st.markdown(result['summary'])

                    st.info(f"Based on {result['note_count']} note(s)")

                    # Show sources
                    if result.get('sources'):
                        with st.expander(f"View all {len(result['sources'])} source notes"):
                            for i, source in enumerate(result['sources'], 1):
                                st.markdown(
                                    f"{i}. **{source.get('title', 'Untitled')}** "
                                    f"(`{source.get('path', 'N/A')}`) — "
                                    f"Relevance: {source.get('relevance_score', 0):.3f}"
                                )
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

    # Tab 4: Smart Analysis (Phase 3 - Auto-summarize related notes)
    with tab4:
        st.header("🔗 Smart Analysis")
        st.markdown("Discover connections and themes across your notes")

        analysis_query = st.text_input(
            "Enter a topic to analyze:",
            placeholder="e.g., 'machine learning' or 'productivity'",
            key="analysis_input"
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            analyze_button = st.button("Analyze", type="primary", use_container_width=True)
        with col2:
            if analyze_button:
                if st.button("Clear Analysis", use_container_width=True):
                    st.rerun()

        if analyze_button and analysis_query:
            with st.spinner("Analyzing your notes..."):
                try:
                    result = st.session_state.qa_system.auto_summarize_related_notes(
                        analysis_query,
                        top_k=top_k
                    )

                    # Display analysis
                    st.markdown(result['summary'])

                    # Show connections as a network-like view
                    if result.get('connections'):
                        st.divider()
                        st.subheader("📊 Connection Strength")

                        # Group by strength
                        strong_connections = [c for c in result['connections'] if c['strength'] >= 3]
                        medium_connections = [c for c in result['connections'] if c['strength'] == 2]
                        weak_connections = [c for c in result['connections'] if c['strength'] == 1]

                        if strong_connections:
                            st.markdown(f"**Strong connections ({len(strong_connections)}):**")
                            for conn in strong_connections[:5]:
                                st.success(f"{conn['note1']} ↔ {conn['note2']}")

                        if medium_connections:
                            st.markdown(f"**Medium connections ({len(medium_connections)}):**")
                            for conn in medium_connections[:5]:
                                st.info(f"{conn['note1']} ↔ {conn['note2']}")

                except Exception as e:
                    st.error(f"Error analyzing notes: {e}")

    # Tab 5: Reflections (Phase 3 - Daily/Weekly reflections)
    with tab5:
        st.header("📊 Reflections")
        st.markdown("Review your knowledge journey")

        reflection_type = st.radio(
            "Reflection period:",
            ["Daily (Last 24 hours)", "Weekly (Last 7 days)", "Custom"],
            horizontal=True
        )

        if reflection_type == "Custom":
            custom_days = st.slider("Number of days to look back:", 1, 90, 7)
        else:
            custom_days = None

        if st.button("Generate Reflection", type="primary", use_container_width=True):
            with st.spinner("Generating reflection..."):
                try:
                    if reflection_type == "Daily (Last 24 hours)":
                        result = st.session_state.qa_system.generate_daily_reflection(days=1)
                    elif reflection_type == "Weekly (Last 7 days)":
                        result = st.session_state.qa_system.generate_weekly_reflection()
                    else:
                        result = st.session_state.qa_system.generate_daily_reflection(days=custom_days)

                    # Display reflection
                    st.markdown(result['summary'])

                    # Show insights as metrics
                    if result.get('themes'):
                        st.divider()
                        st.subheader("📈 Theme Distribution")

                        # Show top themes as metrics
                        theme_items = sorted(result['themes'].items(), key=lambda x: x[1], reverse=True)

                        cols = st.columns(min(len(theme_items), 4))
                        for i, (theme, count) in enumerate(theme_items[:4]):
                            with cols[i]:
                                st.metric(theme, f"{count} notes")

                except Exception as e:
                    st.error(f"Error generating reflection: {e}")

    # Tab 6: Editor (Phase 5)
    with tab6:
        st.header("✏️ Note Editor")
        st.markdown("Create and edit notes directly in the app")

        # Editor mode selection
        mode = st.radio(
            "Mode:",
            ["Create New Note", "Edit Existing Note", "Browse Notes"],
            horizontal=True
        )

        if mode == "Create New Note":
            col1, col2 = st.columns([2, 1])

            with col1:
                # Note title
                title = st.text_input("📝 Note Title", placeholder="Enter note title...")

                # Template selector
                templates = st.session_state.template_manager.list_templates()
                template = st.selectbox(
                    "Template",
                    templates,
                    index=0,
                    help="Choose a template to start with"
                )

                # Load template content
                template_content = st.session_state.template_manager.get_template(template)

                # Content editor
                content = st.text_area(
                    "Content",
                    value=template_content,
                    height=400,
                    help="Write your note in Markdown format"
                )

                # Preview toggle
                show_preview = st.checkbox("Show Live Preview")

                if show_preview:
                    st.divider()
                    st.subheader("Preview")
                    st.markdown(content)

            with col2:
                # Metadata panel
                st.subheader("Metadata")

                # Auto-tag button (if OpenAI enabled)
                if st.session_state.use_auto_tagging and st.session_state.smart_rag and content:
                    if st.button("🤖 Auto-Generate Tags", use_container_width=True):
                        with st.spinner("Generating tags..."):
                            try:
                                suggested_tags = st.session_state.smart_rag.auto_tag(content)
                                # Store in session state
                                st.session_state.suggested_tags = suggested_tags
                                st.success(f"✓ Generated {len(suggested_tags)} tags")
                            except Exception as e:
                                st.error(f"Error generating tags: {e}")

                # Tags input
                default_tags = ', '.join(st.session_state.get('suggested_tags', []))
                tags_input = st.text_input(
                    "Tags",
                    value=default_tags,
                    placeholder="comma, separated, tags",
                    help="Add tags separated by commas"
                )
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

                if tags:
                    st.caption("Tags: " + ", ".join(f"`{tag}`" for tag in tags))

                st.divider()

                # Save button
                if st.button("💾 Save Note", type="primary", use_container_width=True):
                    if not title:
                        st.error("Please enter a note title")
                    else:
                        try:
                            file_path = st.session_state.editor.save_note(
                                title=title,
                                content=content,
                                tags=tags,
                                template=template if template != 'blank' else None
                            )
                            st.success(f"✓ Note saved: {file_path.name}")

                            # Trigger reindex
                            if st.checkbox("Reindex now?", value=True):
                                with st.spinner("Reindexing..."):
                                    st.session_state.qa_system.index_notes()
                                st.success("✓ Knowledge base updated!")

                        except Exception as e:
                            st.error(f"Error saving note: {e}")

                # Note stats
                if content:
                    st.divider()
                    st.caption("📊 Stats")
                    word_count = len(content.split())
                    char_count = len(content)
                    st.caption(f"Words: {word_count}")
                    st.caption(f"Characters: {char_count}")

        elif mode == "Edit Existing Note":
            # List existing notes
            notes = st.session_state.note_manager.list_notes()

            if not notes:
                st.info("No notes found. Create your first note!")
            else:
                # Note selector
                note_options = {f"{note['filename']} ({note['modified'].strftime('%Y-%m-%d %H:%M')})": note['filename']
                               for note in notes}

                selected_display = st.selectbox(
                    "Select a note to edit:",
                    options=list(note_options.keys())
                )
                selected_file = note_options[selected_display]

                # Load note
                try:
                    note = st.session_state.editor.load_note(selected_file)

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Editable title
                        new_title = st.text_input("📝 Title", value=note['title'])

                        # Editable content
                        new_content = st.text_area(
                            "Content",
                            value=note['content'],
                            height=400
                        )

                        # Preview
                        if st.checkbox("Show Preview", key="edit_preview"):
                            st.divider()
                            st.subheader("Preview")
                            st.markdown(new_content)

                    with col2:
                        st.subheader("Metadata")

                        # Edit tags
                        current_tags = note.get('tags', [])
                        if isinstance(current_tags, str):
                            current_tags = [tag.strip() for tag in current_tags.split(',')]

                        tags_input = st.text_input(
                            "Tags",
                            value=", ".join(current_tags) if current_tags else "",
                            key="edit_tags"
                        )
                        new_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

                        st.divider()

                        # Update button
                        if st.button("💾 Update Note", type="primary", use_container_width=True):
                            try:
                                st.session_state.editor.update_note(
                                    filename=selected_file,
                                    title=new_title,
                                    content=new_content,
                                    tags=new_tags
                                )
                                st.success("✓ Note updated successfully!")

                                # Reindex option
                                if st.checkbox("Reindex now?", value=True, key="edit_reindex"):
                                    with st.spinner("Reindexing..."):
                                        st.session_state.qa_system.index_notes()
                                    st.success("✓ Knowledge base updated!")

                            except Exception as e:
                                st.error(f"Error updating note: {e}")

                        # Delete button
                        st.divider()
                        if st.button("🗑️ Delete Note", use_container_width=True):
                            if st.checkbox("Confirm deletion", key="confirm_delete"):
                                try:
                                    st.session_state.editor.delete_note(selected_file)
                                    st.success("✓ Note deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting note: {e}")

                except Exception as e:
                    st.error(f"Error loading note: {e}")

        else:  # Browse Notes
            st.subheader("📚 Note Library")

            # Search and filter
            col1, col2 = st.columns([3, 1])
            with col1:
                search_query = st.text_input("🔍 Search notes", placeholder="Search by title or content...")
            with col2:
                sort_by = st.selectbox("Sort by", ["modified", "created", "title", "size"])

            # Get notes
            notes = st.session_state.note_manager.list_notes(sort_by=sort_by, search_term=search_query)

            if not notes:
                st.info("No notes found matching your search.")
            else:
                st.caption(f"Showing {len(notes)} note(s)")

                # Display notes as cards
                for note in notes:
                    with st.expander(f"📄 {note['filename']} — {note['modified'].strftime('%Y-%m-%d %H:%M')}"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.caption(f"**Path:** `{note['path']}`")
                            st.caption(f"**Size:** {note['size']:,} bytes")
                            st.caption(f"**Created:** {note['created'].strftime('%Y-%m-%d %H:%M')}")

                        with col2:
                            if st.button("Edit", key=f"edit_{note['filename']}"):
                                st.session_state.current_note = note['filename']
                                st.rerun()

                # Note statistics
                st.divider()
                stats = st.session_state.note_manager.get_note_stats()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Notes", stats['total_notes'])
                with col2:
                    st.metric("Total Size", f"{stats['total_size_mb']:.2f} MB")
                with col3:
                    if stats['oldest_note']:
                        st.metric("Oldest Note", stats['oldest_note'].strftime('%Y-%m-%d'))

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🧠 Personal RAG Notes App — Phase 5: Editor Integration Active</p>
            <p style='font-size: 0.8em;'>Context-aware search • Smart analysis • Daily reflections • Built-in editor</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
