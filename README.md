# 🧠 Personal RAG Notes App

> **Your intelligent second brain that grows smarter with every note you write.**

Transform your scattered thoughts into an AI-powered knowledge powerhouse! A beautiful, private, and incredibly smart note-taking system that helps you remember everything, discover hidden connections, and unlock insights you never knew existed.

[![GitHub stars](https://img.shields.io/github/stars/ratandeepbansal/pNotes?style=social)](https://github.com/ratandeepbansal/pNotes)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Why You'll Love This

- 🔒 **100% Private** - Your thoughts stay on your machine. No cloud, no tracking, no data mining.
- 🚀 **Blazingly Fast** - Find any note in milliseconds using semantic search
- 🤖 **Actually Intelligent** - Powered by OpenAI (optional) + local embeddings for true AI understanding
- 🎨 **Beautiful Interface** - Clean, modern UI with dark mode and interactive visualizations
- 📊 **Insightful Analytics** - Discover patterns in your thinking with knowledge graphs and heatmaps
- 📝 **Markdown Native** - Write in plain markdown, sync with Obsidian, export anywhere
- ✨ **Zero Setup Complexity** - Just clone, install, and start capturing ideas

## ✨ Stunning Features

### 🎯 Core Intelligence (Phase 1-3)
- ✅ **Semantic Search** - Ask in natural language, find exactly what you need
- ✅ **Smart Q&A** - Get AI-generated answers from your entire knowledge base
- ✅ **Auto-Tagging** - Let AI suggest perfect tags for your notes (OpenAI)
- ✅ **Topic Summaries** - Instant summaries on any topic across all your notes
- ✅ **Context Filters** - Search by tags, dates, and relevance scores

### 🎨 Beautiful UI (Phase 2, 5, 8)
- ✅ **8-Tab Dashboard** - Search, Q&A, Summarize, Analysis, Reflections, Editor, Knowledge Graph, Analytics
- ✅ **Built-in Markdown Editor** - Write notes directly in the app with live preview
- ✅ **Real-time Stats** - Track your knowledge base growth with beautiful metrics
- ✅ **Dark Mode UI** - Easy on the eyes, gorgeous on all screens
- ✅ **Interactive Graphs** - Visualize note connections with force-directed networks

### 🧠 Advanced Intelligence (Phase 7)
- ✅ **Smart Suggestions** - AI-powered note recommendations based on context
- ✅ **Daily Reflections** - Auto-generated insights about your thinking patterns
- ✅ **Weekly Summaries** - Track themes and productivity over time
- ✅ **Trending Topics** - See what you're focusing on most
- ✅ **Orphan Detection** - Find lonely notes that need connections

### 📊 Powerful Analytics (Phase 8)
- ✅ **Knowledge Graph Visualization** - See your notes as an interactive network
- ✅ **Centrality Analysis** - Discover your most important "hub" notes
- ✅ **Community Detection** - Find natural topic clusters in your knowledge
- ✅ **Activity Heatmaps** - 24/7 visualization of when you're most productive
- ✅ **Usage Charts** - Beautiful Plotly charts tracking notes, tags, and growth
- ✅ **Tag Analytics** - See your most-used tags and content distribution

### 🔄 Sync & Backup (Phase 4, 6)
- ✅ **Obsidian Integration** - Two-way sync with your Obsidian vault
- ✅ **Automated Backups** - Never lose a thought with one-click backups
- ✅ **Watch Mode** - Auto-sync changes in real-time
- ✅ **Data Portability** - All data in open formats (Markdown, SQLite, ChromaDB)

### 🤖 OpenAI Integration (Phase 6)
- ✅ **GPT-Powered Q&A** - Get smarter answers with GPT-4 integration
- ✅ **Intelligent Tagging** - AI suggests relevant tags automatically
- ✅ **Topic Suggestions** - Discover new areas to explore
- ✅ **Flexible Config** - Works great offline too with local embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git
- (Optional) OpenAI API key for enhanced AI features

### Installation

```bash
# 1. Clone this awesome project
git clone https://github.com/ratandeepbansal/pNotes.git
cd pNotes

# 2. Set up your environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install all the magic
pip install -r requirements.txt

# 4. Create your notes folder
mkdir -p notes

# 5. Add your first note
cat > notes/welcome.md << 'EOF'
---
title: Welcome to Your Second Brain
tags: getting-started, welcome
---

# Hello, Future Genius! 👋

This is your first note in what will become your most valuable digital asset.

Every thought, idea, and insight you capture here becomes searchable,
discoverable, and connected to everything else you know.

Welcome to your journey of knowledge!
EOF

# 6. Index your notes
python -m src.main index

# 7. Launch the app!
./run_app.sh
```

🎉 **That's it!** Visit http://localhost:8501 and prepare to be amazed!

## 📖 Experience The Magic

### 🔍 Lightning-Fast Search
Type naturally: "What were my thoughts on productivity last week?" - The AI understands context, time, and meaning.

### 💬 Intelligent Q&A
Ask: "Summarize everything I know about machine learning" - Get instant, sourced answers from your entire knowledge base.

### 🕸️ Knowledge Graph
Watch your thoughts come alive as a beautiful, interactive network. See connections you never noticed!

### 📊 Analytics Dashboard
Track your intellectual growth with:
- **Activity Heatmaps** - When are you most creative?
- **Tag Clouds** - What topics dominate your thinking?
- **Timeline Charts** - Visualize your knowledge growth over time

### ✏️ Built-in Editor
Write notes directly in the app with:
- Live markdown preview
- Frontmatter validation
- Auto-save functionality
- Template support

### 🎯 Smart Features That Just Work
- **Auto-suggestions** - Get note recommendations as you write
- **Daily reflections** - Morning summaries of yesterday's insights
- **Topic tracking** - See emerging themes in your thinking
- **Connection discovery** - Find related notes automatically

## 🎨 Screenshots & Demo

```
┌─────────────────────────────────────────────────────┐
│  🔍 Search    💬 Q&A    📝 Summarize    🧠 Analysis │
│  📊 Reflections    ✏️ Editor    🕸️ Graph    📈 Stats │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Search your knowledge...                            │
│  ┌──────────────────────────────────────────┐      │
│  │ "ideas about AI and creativity"          │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  📄 Creative AI Applications (95% match)            │
│     Tags: AI, creativity, innovation                │
│     "Exploring how AI augments human creativity..." │
│                                                      │
│  🎨 The Artist's Algorithm (87% match)              │
│     Tags: creativity, technology, art               │
│     "Can machines be creative? My thoughts on..."   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 📁 Project Architecture

```
personal_rag/
├── 📝 notes/                      # Your markdown notes live here
├── 💾 data/                       # Local databases (gitignored)
│   ├── metadata.db               # SQLite - note metadata
│   └── chroma/                   # ChromaDB - vector embeddings
├── 🧠 src/
│   ├── db/
│   │   ├── metadata.py           # Metadata operations
│   │   └── vectorstore.py        # Vector storage
│   ├── rag/
│   │   ├── embedder.py           # Embedding generation
│   │   ├── retriever.py          # Semantic search engine
│   │   ├── qa.py                 # Question answering
│   │   └── smart_rag.py          # OpenAI integration
│   ├── intelligence/
│   │   ├── note_suggester.py    # Smart recommendations
│   │   └── summary_generator.py  # Auto summaries
│   ├── visualization/
│   │   └── knowledge_graph.py    # Network graphs
│   ├── analytics/
│   │   └── usage.py              # Statistics & charts
│   ├── editor/
│   │   └── markdown_editor.py    # Built-in editor
│   └── utils/
│       ├── file_loader.py        # Markdown parsing
│       └── config.py             # Configuration
├── 🎨 app.py                     # Streamlit UI (8 tabs!)
├── 🚀 run_app.sh                 # One-click launcher
├── 🛠️ scripts/
│   ├── backup.py                 # Backup utility
│   ├── restore.py                # Restore utility
│   └── sync_obsidian.py          # Obsidian sync
└── 📦 requirements.txt            # All dependencies
```

## 🎯 Power User Guide

### Command Line Interface

```bash
# Index everything
python -m src.main index

# Semantic search
python -m src.main search "distributed systems concepts"

# Ask complex questions
python -m src.main ask "What are the main themes in my productivity notes?"

# Generate topic summaries
python -m src.main summarize "machine learning"

# View statistics
python -m src.main stats
```

### Advanced Search Filters

In the sidebar:
- **Tags** - Filter by single or multiple tags
- **Date Ranges** - Today, Last 7 days, Last 30 days, Custom
- **Top K** - Control number of results
- **Similarity Threshold** - Adjust result relevance

### Obsidian Integration

```bash
# One-time sync
python scripts/sync_obsidian.py /path/to/vault

# Real-time watch mode
python scripts/sync_obsidian.py /path/to/vault --watch

# Symlink mode (advanced)
python scripts/sync_obsidian.py /path/to/vault --mode symlink
```

### Backup Strategy

```bash
# Create timestamped backup
python scripts/backup.py create

# List all backups
python scripts/backup.py list

# Restore from backup
python scripts/restore.py backups/knowledge_base_backup_20250108_143022.tar.gz
```

### OpenAI Configuration

1. Get your API key: https://platform.openai.com/api-keys
2. Open the app → Settings (sidebar)
3. Enter your API key
4. Enable features:
   - ✅ Use OpenAI for Q&A
   - ✅ Auto-generate tags

**Pro Tip:** The app works great without OpenAI too! Local embeddings provide excellent semantic search.

## 🎨 Customization

Edit `src/utils/config.py`:

```python
# Paths
NOTES_DIR = Path("./notes")
BACKUP_DIR = Path("./backups")

# Search settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# OpenAI (optional)
OPENAI_MODEL = "gpt-4-turbo-preview"
```

## 🏆 What Makes This Special?

### 🔐 Privacy First
Unlike Notion, Roam, or Evernote - your data **never** leaves your machine. No surveillance, no data mining, no "improving our AI" with your private thoughts.

### 🧠 Genuinely Intelligent
This isn't just full-text search with a fancy UI. Semantic embeddings mean the AI actually *understands* what you're looking for.

### 📊 Beautifully Visual
Knowledge graphs, heatmaps, and analytics dashboards turn your notes into stunning visualizations that reveal patterns you'd never spot manually.

### ⚡ Actually Fast
ChromaDB vector search + SQLite metadata means sub-100ms search times, even with thousands of notes.

### 🎯 Zero Lock-In
Everything is markdown and open formats. Export anytime. Your notes outlive any app.

## 🐛 Troubleshooting

**Q: Notes not appearing?**
- Ensure files are in `notes/` folder with `.md` extension
- Click "🔄 Reindex All Notes" in sidebar
- Check note count in statistics

**Q: Search returns nothing?**
- Verify notes are indexed (check sidebar stats)
- Try broader search terms
- Remove filters temporarily
- Rebuild index: `python -m src.main index --force`

**Q: OpenAI errors?**
- Click "🗑️ Clear Stored API Key" in Settings
- Re-enter a valid API key (starts with `sk-`)
- Check API key permissions at platform.openai.com

**Q: Performance issues?**
- Reduce `TOP_K_RESULTS` in config
- Consider using smaller embedding model
- Ensure SSD for data directory

## 🚀 Roadmap

- [x] **Phase 1** - Core RAG System ✅
- [x] **Phase 2** - Streamlit UI ✅
- [x] **Phase 3** - Intelligence Layer ✅
- [x] **Phase 4** - Backup & Sync ✅
- [x] **Phase 5** - Markdown Editor ✅
- [x] **Phase 6** - OpenAI Integration ✅
- [x] **Phase 7** - Smart Suggestions ✅
- [x] **Phase 8** - Knowledge Graphs & Analytics ✅
- [ ] **Phase 9** - Local LLM Support (Ollama/LM Studio)
- [ ] **Phase 10** - Mobile App (PWA)
- [ ] **Phase 11** - Collaborative Features (Self-hosted)
- [ ] **Phase 12** - Plugin System

## 🤝 Contributing

Love this project? Here's how you can help:

1. ⭐ **Star this repo** - It motivates development!
2. 🐛 **Report bugs** - Open detailed issues
3. 💡 **Suggest features** - Share your ideas
4. 🔧 **Submit PRs** - Contributions welcome
5. 📢 **Spread the word** - Tweet, blog, share!

## 📜 License

MIT License - Use it, modify it, build on it, make it yours!

## 🙏 Built With Love Using

- [Streamlit](https://streamlit.io/) - Beautiful web UI
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [SentenceTransformers](https://www.sbert.net/) - Embeddings
- [OpenAI](https://openai.com/) - GPT-4 integration (optional)
- [SQLite](https://www.sqlite.org/) - Metadata storage
- [NetworkX](https://networkx.org/) - Graph algorithms
- [Plotly](https://plotly.com/) - Interactive charts
- [Pyvis](https://pyvis.readthedocs.io/) - Network visualization

## 💬 Community & Support

- 📝 **Issues** - Found a bug? Open an issue!
- 💡 **Discussions** - Share ideas and use cases
- 🌟 **Show & Tell** - Built something cool? Share it!
- 📧 **Contact** - Questions? Open an issue or discussion

## 🎉 Success Stories

*Be the first to share your experience! Open a discussion and tell us how Personal RAG Notes transformed your note-taking.*

---

<div align="center">

**🧠 Your thoughts deserve better than a plain text file.**

**Build your AI-powered second brain today!**

[⭐ Star this repo](https://github.com/ratandeepbansal/pNotes) • [🐛 Report Bug](https://github.com/ratandeepbansal/pNotes/issues) • [💡 Request Feature](https://github.com/ratandeepbansal/pNotes/issues)

Made with ❤️ and 🤖 by developers who believe in privacy, intelligence, and beautiful code.

</div>
