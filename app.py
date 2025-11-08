"""Streamlit UI for the Personal RAG Notes App with Phase 3 Intelligence Features."""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, timedelta
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.qa import QASystem
from src.utils.config import TOP_K_RESULTS


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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Search",
        "💬 Ask Question",
        "📝 Summarize Topic",
        "🔗 Smart Analysis",
        "📊 Reflections"
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

            # Confidence
            confidence = result.get('confidence', 0.0)
            st.metric("Confidence", f"{confidence:.1%}")

            # Sources
            sources = result.get('sources', [])
            if sources:
                st.divider()
                st.subheader(f"📚 Sources ({len(sources)} note(s))")

                for i, source in enumerate(sources, 1):
                    with st.expander(
                        f"{i}. {source.get('title', 'Untitled')} — Relevance: {source.get('relevance_score', 0):.3f}"
                    ):
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

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🧠 Personal RAG Notes App — Phase 3: Intelligence Layer Active</p>
            <p style='font-size: 0.8em;'>Context-aware search • Smart analysis • Daily reflections</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
