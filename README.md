# 🧠 Personal RAG Notes App

Your AI-powered personal knowledge base that runs entirely offline. A private, intelligent note-taking and retrieval system built with Python, ChromaDB, and Streamlit.

## ✨ Features

### Core Functionality (Phase 1)
- ✅ **Markdown Note Support** - Store notes in plain markdown with YAML frontmatter
- ✅ **Semantic Search** - Find notes using natural language queries
- ✅ **Vector Embeddings** - Powered by SentenceTransformers (all-MiniLM-L6-v2)
- ✅ **Metadata Management** - SQLite database for fast metadata queries
- ✅ **Question Answering** - Ask questions and get answers from your notes
- ✅ **Topic Summarization** - Generate summaries on any topic from your notes

### Streamlit UI (Phase 2)
- ✅ **Web Interface** - Clean, modern UI built with Streamlit
- ✅ **Interactive Search** - Real-time search with expandable results
- ✅ **Statistics Dashboard** - Track your knowledge base metrics
- ✅ **One-Click Reindexing** - Update your knowledge base instantly

### Intelligence Layer (Phase 3)
- ✅ **Context-Aware Search** - Filter by tags and date ranges
- ✅ **Smart Analysis** - Discover connections and themes across notes
- ✅ **Daily Reflections** - Generate insights about your note-taking patterns
- ✅ **Connection Mapping** - Visualize relationships between notes

### Sync & Backup (Phase 4)
- ✅ **Backup & Restore** - Protect your knowledge base with automated backups
- ✅ **Obsidian Integration** - Sync with your Obsidian vault
- ✅ **Data Portability** - All data stored locally in open formats

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ratandeepbansal/pNotes.git
cd pNotes
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create your notes directory**
```bash
mkdir -p notes
```

5. **Add your first note**
Create a file `notes/example.md`:
```markdown
---
title: My First Note
tags: example, test
---

# Hello World

This is my first note in my personal knowledge base!
```

6. **Index your notes**
```bash
python -m src.main index
```

7. **Launch the app**
```bash
./run_app.sh
# Or manually: ./venv/bin/python3 -m streamlit run app.py
```

Visit http://localhost:8501 to access your knowledge base!

## 📖 Usage Guide

### Adding Notes

Notes are markdown files with optional YAML frontmatter:

```markdown
---
title: Understanding Machine Learning
tags: AI, machine-learning, tutorial
---

# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence...
```

**Supported metadata:**
- `title`: Note title (defaults to filename)
- `tags`: Comma-separated tags or YAML list

### Using the Web Interface

#### 🔍 Search Tab
- Enter natural language queries
- Apply tag and date filters in the sidebar
- View results with relevance scores
- Expand notes to read full content

#### 💬 Ask Question Tab
- Ask questions about your notes
- Get AI-generated answers with confidence scores
- View source notes used for the answer

#### 📝 Summarize Topic Tab
- Enter a topic to summarize
- Get organized summaries grouped by tags
- See all related notes

#### 🔗 Smart Analysis Tab
- Discover connections between notes
- View shared themes and tags
- Identify knowledge clusters

#### 📊 Reflections Tab
- Generate daily, weekly, or custom reflections
- Review your note-taking patterns
- Track themes and productivity

### Command Line Interface

The app also includes a CLI for power users:

```bash
# Index all notes
python -m src.main index

# Search notes
python -m src.main search "machine learning"

# Ask a question
python -m src.main ask "What are my thoughts on AI?"

# Summarize a topic
python -m src.main summarize "productivity"

# Show statistics
python -m src.main stats
```

## 🔧 Advanced Features

### Backup & Restore

**Create a backup:**
```bash
python scripts/backup.py create
```

**List available backups:**
```bash
python scripts/backup.py list
```

**Restore from backup:**
```bash
python scripts/restore.py backups/knowledge_base_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Obsidian Integration

**One-time sync:**
```bash
python scripts/sync_obsidian.py /path/to/your/obsidian/vault
```

**Watch for changes (requires watchdog):**
```bash
pip install watchdog
python scripts/sync_obsidian.py /path/to/your/obsidian/vault --watch
```

**Symlink mode (advanced):**
```bash
python scripts/sync_obsidian.py /path/to/your/obsidian/vault --mode symlink
```

### Filtering Search Results

Use the sidebar filters to refine your searches:

**Filter by tags:**
- Select one or more tags from the dropdown
- Only notes with matching tags will appear

**Filter by date:**
- Choose from presets (Today, Last 7 days, etc.)
- Or set a custom date range
- Only notes modified within the range will appear

## 📁 Project Structure

```
personal_rag/
├── notes/                    # Your markdown notes
├── data/                     # Local databases (not in git)
│   ├── metadata.db          # SQLite metadata
│   └── chroma/              # ChromaDB vector store
├── src/
│   ├── db/
│   │   ├── metadata.py      # SQLite operations
│   │   └── vectorstore.py   # ChromaDB management
│   ├── rag/
│   │   ├── embedder.py      # Embedding generation
│   │   ├── retriever.py     # Search & retrieval
│   │   └── qa.py            # Question answering
│   ├── utils/
│   │   ├── file_loader.py   # Markdown parsing
│   │   └── config.py        # Configuration
│   └── main.py              # CLI entrypoint
├── scripts/
│   ├── backup.py            # Backup utility
│   ├── restore.py           # Restore utility
│   └── sync_obsidian.py     # Obsidian sync
├── app.py                   # Streamlit UI
├── run_app.sh              # Launch script
└── requirements.txt         # Dependencies
```

## 🛠️ Configuration

Edit `src/utils/config.py` to customize:

```python
# Paths
NOTES_DIR = Path("./notes")
DATA_DIR = Path("./data")

# Search settings
TOP_K_RESULTS = 5  # Default number of results

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformer model
```

## 🔒 Privacy & Data

- **100% Offline**: No API keys required, no data sent to external services
- **Local Storage**: All data stored on your machine
- **Open Formats**: Notes in Markdown, metadata in SQLite
- **Portable**: Easy to backup and migrate

## 🐛 Troubleshooting

**SQLite threading errors in Streamlit:**
- Fixed in Phase 3 with `check_same_thread=False`
- If you encounter issues, restart the Streamlit app

**Notes not appearing:**
- Make sure notes are in the `notes/` directory
- Click "Reindex All Notes" in the sidebar
- Check that files have `.md` extension

**Search returns no results:**
- Verify notes are indexed (check stats in sidebar)
- Try different query terms
- Remove filters to broaden search

**Python module not found:**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Share your use cases and customizations

## 📝 License

MIT License - feel free to use, modify, and distribute as you see fit.

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web interface
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [SentenceTransformers](https://www.sbert.net/) - Embeddings
- [SQLite](https://www.sqlite.org/) - Metadata storage

## 🗺️ Roadmap

- [x] Phase 1: Core RAG System
- [x] Phase 2: Streamlit UI
- [x] Phase 3: Intelligence Layer
- [x] Phase 4: Backup & Sync
- [ ] Future: Local LLM integration (Ollama/LM Studio)
- [ ] Future: Knowledge graph visualization
- [ ] Future: Plugin system

## 📧 Contact

Questions or feedback? Open an issue or reach out!

---

**🧠 Build your own AI memory system - private, powerful, and entirely yours.**
