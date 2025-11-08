# 🚀 Personal RAG Notes App — Extension Plan (v2.0)

## 📋 Prerequisites
- ✅ Completed Phase 1-4 from `plan.md`
- ✅ Working SQLite + ChromaDB + Local Embeddings
- ✅ Basic Streamlit UI with search functionality

---

## 🎯 New Goals
1. **Built-in Markdown Editor** — Create, edit, and organize notes directly in the app
2. **OpenAI-Enhanced RAG** — Use GPT-4 for intelligent responses while keeping embeddings local
3. **Smart Note Templates** — AI-assisted note creation with context awareness

---

## 📂 Extended Project Structure

```
personal_rag/
│
├── notes/                     # Existing markdown storage
│
├── src/
│   ├── [existing files...]
│   │
│   ├── editor/               # NEW: Note editing module
│   │   ├── markdown_editor.py
│   │   ├── file_manager.py
│   │   ├── templates.py
│   │   └── __init__.py
│   │
│   ├── llm/                  # NEW: LLM integration
│   │   ├── openai_client.py
│   │   ├── prompts.py
│   │   ├── response_cache.py
│   │   └── __init__.py
│   │
│   └── intelligence/         # NEW: Smart features
│       ├── auto_tagger.py
│       ├── note_suggester.py
│       ├── summary_generator.py
│       └── __init__.py
│
├── .env                      # NEW: API keys storage
├── config.yaml               # NEW: App configuration
└── templates/                # NEW: Note templates
    ├── daily.md
    ├── meeting.md
    ├── idea.md
    └── research.md
```

---

## 🛠️ Phase 5 — Markdown Editor Integration

### **5.1 Core Editor Features**

```python
# src/editor/markdown_editor.py

import streamlit as st
from datetime import datetime
import frontmatter

class MarkdownEditor:
    def create_note(self, title, content, tags=[], template=None):
        """Create new note with YAML frontmatter"""
        note = {
            'title': title,
            'date': datetime.now().isoformat(),
            'tags': tags,
            'id': self.generate_note_id()
        }
        
        post = frontmatter.Post(content, **note)
        return post.dumps()
    
    def save_note(self, filename, content):
        """Save to notes folder and trigger re-indexing"""
        path = f"notes/{filename}.md"
        with open(path, 'w') as f:
            f.write(content)
        
        # Trigger incremental indexing
        self.index_single_note(path)
```

### **5.2 Streamlit UI Components**

```python
# Addition to app.py

def note_editor_page():
    st.header("📝 Create/Edit Note")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Live markdown editor
        title = st.text_input("Title")
        
        # Template selector
        template = st.selectbox("Template", 
            ["Blank", "Daily", "Meeting", "Research", "Idea"])
        
        content = st.text_area("Content", 
            height=400,
            value=load_template(template))
        
        # Live preview
        if st.checkbox("Show Preview"):
            st.markdown(content)
    
    with col2:
        # Metadata panel
        tags = st_tags.st_tags(label="Tags")
        
        # AI suggestions based on content
        if st.button("🤖 Auto-tag"):
            suggested_tags = auto_tag(content)
            st.write(suggested_tags)
        
        if st.button("💾 Save"):
            save_note(title, content, tags)
            st.success("Note saved!")
            trigger_reindex()
```

### **5.3 File Management**

```python
# src/editor/file_manager.py

class NoteManager:
    def list_notes(self, sort_by='modified'):
        """List all notes with metadata"""
        
    def search_by_title(self, query):
        """Quick title search"""
        
    def bulk_operations(self, note_ids, operation):
        """Archive, delete, export multiple notes"""
        
    def version_control(self, note_id):
        """Simple git-like versioning using SQLite"""
```

---

## 🤖 Phase 6 — OpenAI API Integration

### **6.1 Hybrid RAG Architecture**

```python
# src/llm/openai_client.py

from openai import OpenAI
import os
from functools import lru_cache

class SmartRAG:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.local_retriever = ChromaRetriever()
    
    def enhanced_search(self, query, mode='hybrid'):
        """
        Modes:
        - local: Use only ChromaDB (free, fast)
        - semantic: Use OpenAI embeddings
        - hybrid: Local retrieval + OpenAI generation
        """
        
        if mode == 'local':
            # Existing ChromaDB search
            return self.local_retriever.search(query)
        
        elif mode == 'semantic':
            # Generate OpenAI embedding for query
            query_embedding = self.get_openai_embedding(query)
            return self.local_retriever.search_by_vector(query_embedding)
        
        elif mode == 'hybrid':
            # Local retrieval + GPT synthesis
            local_results = self.local_retriever.search(query, top_k=5)
            context = self.format_context(local_results)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective
                messages=[
                    {"role": "system", "content": SMART_RAG_PROMPT},
                    {"role": "user", "content": f"Query: {query}\n\nContext:\n{context}"}
                ],
                temperature=0.3
            )
            
            return {
                'answer': response.choices[0].message.content,
                'sources': local_results,
                'tokens_used': response.usage.total_tokens
            }
    
    @lru_cache(maxsize=100)
    def get_openai_embedding(self, text):
        """Cache embeddings to reduce API calls"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",  # Cheaper than ada-002
            input=text
        )
        return response.data[0].embedding
```

### **6.2 Intelligent Prompts**

```python
# src/llm/prompts.py

SMART_RAG_PROMPT = """You are a personal knowledge assistant analyzing the user's notes.
Your task is to provide intelligent, synthesized answers based on their personal knowledge base.

Guidelines:
1. Reference specific notes when answering
2. Identify connections between different notes
3. Suggest related topics they might want to explore
4. If information is missing, indicate what additional notes would be helpful
5. Maintain the user's writing style and terminology

Always cite which notes you're drawing from."""

AUTO_TAG_PROMPT = """Extract 3-5 relevant tags from this note content.
Tags should be: lowercase, single concepts, reusable across notes.
Examples: 'robotics', 'machine-learning', 'project-idea', 'meeting-notes'"""

SMART_SUMMARY_PROMPT = """Create a concise summary that:
1. Captures key insights
2. Lists action items if present  
3. Notes questions that need answers
4. Identifies connections to other topics"""
```

### **6.3 Cost Optimization**

```python
# src/llm/response_cache.py

class ResponseCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}  # Or use Redis
        self.ttl = ttl_hours * 3600
    
    def get_or_generate(self, query, generator_func):
        """Cache OpenAI responses to reduce costs"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        if cache_key in self.cache:
            if not self.is_expired(cache_key):
                return self.cache[cache_key]
        
        response = generator_func(query)
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        return response
```

---

## 🧠 Phase 7 — Intelligence Features

### **7.1 Auto-Tagging System**

```python
# src/intelligence/auto_tagger.py

def auto_tag_note(content):
    """Use GPT to suggest tags"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": AUTO_TAG_PROMPT},
            {"role": "user", "content": content[:1000]}  # Limit tokens
        ],
        temperature=0.3,
        max_tokens=50
    )
    
    tags = response.choices[0].message.content.split(',')
    return [tag.strip() for tag in tags]
```

### **7.2 Smart Note Suggestions**

```python
# src/intelligence/note_suggester.py

def suggest_related_notes(current_note_id):
    """When editing a note, suggest related notes to link"""
    current_embedding = get_note_embedding(current_note_id)
    similar_notes = chroma.similarity_search(
        embedding=current_embedding,
        k=5,
        where={"id": {"$ne": current_note_id}}
    )
    return similar_notes

def suggest_next_note():
    """Based on recent notes, suggest what to write next"""
    recent_notes = get_recent_notes(days=7)
    context = summarize_notes(recent_notes)
    
    prompt = f"Based on these recent notes, suggest 3 topics to explore next:\n{context}"
    suggestions = generate_gpt_response(prompt)
    return suggestions
```

### **7.3 Daily Summaries**

```python
# src/intelligence/summary_generator.py

def generate_daily_reflection():
    """AI-powered daily summary of your notes"""
    today_notes = get_notes_by_date(date.today())
    
    summary_prompt = f"""
    Review these notes from today and create a reflection:
    - Key accomplishments
    - Open questions
    - Tomorrow's priorities
    
    Notes: {today_notes}
    """
    
    reflection = generate_gpt_response(summary_prompt)
    
    # Auto-save as a daily summary note
    save_note(f"daily-summary-{date.today()}", reflection)
```

---

## 🎨 Phase 8 — Enhanced UI/UX

### **8.1 Multi-Page Streamlit App**

```python
# app.py restructure

import streamlit as st
from streamlit_option_menu import option_menu

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        "Personal RAG",
        ["Search", "Editor", "Graph View", "Analytics", "Settings"],
        icons=['search', 'pencil', 'diagram-3', 'bar-chart', 'gear'],
        default_index=0
    )

if selected == "Search":
    search_page()
elif selected == "Editor":
    editor_page()
elif selected == "Graph View":
    knowledge_graph_page()
elif selected == "Analytics":
    analytics_page()
elif selected == "Settings":
    settings_page()
```

### **8.2 Knowledge Graph Visualization**

```python
# src/visualization/graph.py

def create_knowledge_graph():
    """Interactive graph of note connections"""
    G = nx.Graph()
    
    # Add notes as nodes
    for note in get_all_notes():
        G.add_node(note.id, title=note.title, tags=note.tags)
    
    # Add edges based on:
    # - Shared tags
    # - Internal links [[note]]
    # - Semantic similarity > 0.8
    
    # Visualize with Pyvis
    net = Network(height="750px", width="100%")
    net.from_nx(G)
    net.save_graph("knowledge_graph.html")
```

---

## ⚙️ Configuration & Settings

### **config.yaml**
```yaml
app:
  name: "Personal RAG Notes"
  version: "2.0"

editor:
  autosave_interval: 30  # seconds
  max_file_size: 10  # MB
  supported_formats: [".md", ".txt"]

openai:
  model: "gpt-4o-mini"
  embedding_model: "text-embedding-3-small"
  max_tokens: 1000
  temperature: 0.3
  cache_ttl: 24  # hours

rag:
  retrieval_mode: "hybrid"  # local|semantic|hybrid
  top_k: 5
  rerank: true
  
costs:
  monthly_limit: 10.00  # USD
  alert_threshold: 0.80  # Alert at 80% of limit
```

### **.env**
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional fallback
```

---

## 📊 Monitoring & Analytics

```python
# src/analytics/usage.py

def track_usage():
    """Monitor API costs and usage patterns"""
    return {
        'total_notes': count_notes(),
        'total_tokens_used': get_monthly_tokens(),
        'estimated_cost': calculate_cost(),
        'most_searched_topics': get_top_queries(),
        'orphan_notes': find_unlinked_notes()
    }
```

---

## 🚢 Deployment Updates

### **Updated PyApp Config**
```toml
[tool.pyapp]
name = "PersonalRAG"
version = "2.0.0"
dependencies = [
    "streamlit>=1.28",
    "openai>=1.0",
    "chromadb>=0.4",
    "streamlit-tags>=1.2",
    "streamlit-option-menu>=0.3"
]

[tool.pyapp.env]
OPENAI_API_KEY = "${OPENAI_API_KEY}"
```

---

## 📈 Performance Optimizations

1. **Streaming Responses**
   ```python
   # Stream GPT responses for better UX
   for chunk in openai.chat.completions.create(stream=True):
       yield chunk.choices[0].delta.content
   ```

2. **Background Indexing**
   ```python
   # Use threading for non-blocking indexing
   threading.Thread(target=index_note, args=(note_path,)).start()
   ```

3. **Batch API Calls**
   ```python
   # Process multiple queries together
   embeddings = openai.embeddings.create(
       model="text-embedding-3-small",
       input=batch_of_texts  # Up to 2048 inputs
   )
   ```

---

## ✅ Implementation Checklist

### **Week 1: Editor Foundation**
- [ ] Basic markdown editor in Streamlit
- [ ] Save/load functionality
- [ ] Template system
- [ ] File browser sidebar

### **Week 2: OpenAI Integration**
- [ ] API client setup
- [ ] Hybrid search implementation
- [ ] Response caching
- [ ] Cost tracking

### **Week 3: Intelligence Layer**
- [ ] Auto-tagging
- [ ] Related notes suggestions
- [ ] Smart summaries
- [ ] Query enhancement

### **Week 4: Polish & Package**
- [ ] Multi-page navigation
- [ ] Settings management
- [ ] Export functionality
- [ ] PyApp packaging v2.0

---

## 🎯 Success Metrics

- **Search Quality**: >90% relevant results in top-3
- **API Costs**: <$5/month for personal use
- **Response Time**: <2s for hybrid search
- **Editor UX**: Zero-friction note creation

---

## 🔮 Future Extensions (v3.0)

- **Voice Notes**: Whisper API transcription
- **Image Support**: GPT-4 Vision for diagrams
- **Multi-modal Search**: Search by sketch/image
- **Collaborative Mode**: Share specific notes via links
- **Mobile App**: React Native companion

---

💡 **Next Step**: Start with Phase 5.1 - get the basic editor working, then gradually add OpenAI features while monitoring costs.