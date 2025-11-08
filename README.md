# Personal RAG Notes App - Phase 1

A local, privacy-focused personal knowledge base that uses RAG (Retrieval-Augmented Generation) to search and answer questions from your Markdown notes.

## Features (Phase 1)

- Read Markdown files with YAML frontmatter support
- Extract metadata (title, tags) from notes
- Store metadata in SQLite
- Generate embeddings using SentenceTransformers
- Store embeddings in ChromaDB for semantic search
- Perform keyword and semantic search
- Answer questions based on your notes (retrieval-based)
- Fully local and offline - no API keys required

## Installation

1. Activate your virtual environment:
```bash
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Index Your Notes

First, index all your markdown notes:

```bash
python -m src.main index
```

This will:
- Scan all `.md` files in the `notes/` directory
- Extract metadata and content
- Generate embeddings
- Store everything in SQLite and ChromaDB

### 2. Search for Notes

Perform semantic search:

```bash
python -m src.main search "robotics vision"
```

Options:
- `-k, --top-k`: Number of results to return (default: 5)

### 3. Ask Questions

Ask questions about your notes:

```bash
python -m src.main ask "What have I written about AI?"
```

The system will retrieve relevant notes and provide an answer based on their content.

### 4. Summarize Topics

Get a summary of what your notes say about a topic:

```bash
python -m src.main summarize "machine learning"
```

### 5. View Statistics

Check your knowledge base stats:

```bash
python -m src.main stats
```

## Project Structure

```
personal_rag/
├── notes/                      # Your markdown notes
│   ├── robotics.md
│   ├── ai_thoughts.md
│   └── ideas.md
├── src/
│   ├── main.py                 # CLI entrypoint
│   ├── db/
│   │   ├── metadata.py         # SQLite operations
│   │   └── vectorstore.py      # ChromaDB operations
│   ├── rag/
│   │   ├── embedder.py         # Embedding generation
│   │   ├── retriever.py        # Semantic search
│   │   └── qa.py               # Question-answering
│   └── utils/
│       ├── file_loader.py      # Markdown file loading
│       └── config.py           # Configuration
├── data/                       # Generated (SQLite + ChromaDB)
├── requirements.txt
├── plan.md
└── README.md
```

## Note Format

Notes should be in Markdown format with optional YAML frontmatter:

```markdown
---
title: My Note Title
tags: tag1, tag2, tag3
---

# Content goes here

Your note content in Markdown format...
```

If no frontmatter is provided, the filename will be used as the title.

## What's Next?

This is Phase 1 of the project. Future phases will include:

- **Phase 2**: Streamlit UI for better interaction
- **Phase 3**: Local LLM integration for actual answer generation
- **Phase 4**: PyApp packaging for desktop distribution

## Technical Details

- **Embeddings**: Uses `all-MiniLM-L6-v2` for efficient, high-quality embeddings
- **Vector Store**: ChromaDB for persistent vector storage
- **Metadata**: SQLite for structured metadata
- **Search**: Hybrid semantic + keyword search

## License

MIT
